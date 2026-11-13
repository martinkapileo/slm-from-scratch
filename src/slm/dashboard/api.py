"""Dashboard API: read-only access to training runs, plus text generation.

Run locally:
    uvicorn slm.dashboard.api:app --reload --port 8000

Environment:
    SLM_RUNS_DIR    directory holding run folders (default: runs)
    SLM_STATIC_DIR  built React app to serve at / (default: unset = API only)
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from slm.sample import LoadedRun, generate_text, load_run

RUNS_DIR = Path(os.environ.get("SLM_RUNS_DIR", "runs")).resolve()

app = FastAPI(title="slm dashboard", version="0.1.0")


def _run_dir(name: str) -> Path:
    """Resolve a run name to a directory, refusing anything outside RUNS_DIR."""
    path = (RUNS_DIR / name).resolve()
    if path.parent != RUNS_DIR or not (path / "metrics.jsonl").exists():
        raise HTTPException(404, f"run not found: {name}")
    return path


def _read_metrics(run_dir: Path) -> list[dict]:
    rows = []
    for line in (run_dir / "metrics.jsonl").read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass  # a line being written by a live training run
    return rows


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "runs_dir": str(RUNS_DIR)}


@app.get("/api/runs")
def list_runs() -> list[dict]:
    if not RUNS_DIR.exists():
        return []
    out = []
    for d in sorted(p for p in RUNS_DIR.iterdir() if (p / "metrics.jsonl").exists()):
        rows = _read_metrics(d)
        last = rows[-1] if rows else {}
        out.append({
            "name": d.name,
            "evals": len(rows),
            "last_iter": last.get("iter"),
            "last_train": last.get("train"),
            "last_val": last.get("val"),
            "best_val": min((r["val"] for r in rows), default=None),
            "elapsed_s": last.get("elapsed_s"),
            "params": last.get("params"),
            "has_checkpoint": (d / "ckpt.pt").exists(),
            "updated": (d / "metrics.jsonl").stat().st_mtime,
        })
    return out


@app.get("/api/runs/{name}/metrics")
def run_metrics(name: str) -> list[dict]:
    return _read_metrics(_run_dir(name))


@app.get("/api/runs/{name}/config")
def run_config(name: str) -> dict:
    path = _run_dir(name) / "config.json"
    if not path.exists():
        raise HTTPException(404, "config.json missing")
    return json.loads(path.read_text())


class SampleRequest(BaseModel):
    prompt: str = Field("\n", max_length=500)
    tokens: int = Field(300, ge=1, le=2000)
    temperature: float = Field(0.8, gt=0, le=2.0)
    top_k: int | None = Field(None, ge=1)
    seed: int = 0


@lru_cache(maxsize=4)
def _cached_run(path: str, mtime: float) -> LoadedRun:
    # mtime is part of the cache key, so a newer checkpoint is reloaded.
    return load_run(path)


@app.post("/api/runs/{name}/sample")
def run_sample(name: str, req: SampleRequest) -> dict:
    d = _run_dir(name)
    ckpt = d / "ckpt.pt"
    if not ckpt.exists():
        raise HTTPException(404, "no checkpoint yet")
    run = _cached_run(str(d), ckpt.stat().st_mtime)
    try:
        text = generate_text(run, req.prompt, req.tokens, req.temperature, req.top_k, req.seed)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    return {"text": text, "checkpoint_iter": run.iter}


static_dir = os.environ.get("SLM_STATIC_DIR")
if static_dir and Path(static_dir).is_dir():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="ui")
