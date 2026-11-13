# slm-from-scratch

A learning project: build a small GPT from scratch in PyTorch, then productionize it
the way an enterprise AI team would (tracking, evals, fine-tuning, serving, governance).
The owner is learning LLM fundamentals and preparing for AI solution architect roles,
so **explain the why** behind changes, not just the what.

## Layout
- `src/slm/` — library code: `config.py`, `data.py` (tokenizer, batching), `model.py` (GPT), `train.py`, `sample.py`
- `configs/*.toml` — every hyperparameter lives here, never hard-coded
- `src/slm/dashboard/api.py` — FastAPI read-only API over `runs/`; `frontend/` — React + TS dashboard (Vite)
- `scripts/` — one-off CLIs (data prep, plugin build)
- `tests/` — pytest; `tests/test_model.py` encodes core transformer properties
- `docs/sdlc.md` — **the workflow every change follows. Read it before starting work.**
- `docs/roadmap.md` — the five phases and their status
- `docs/specs/`, `docs/adr/`, `docs/experiments/` — specs, architecture decisions, experiment log
- `.claude/skills/`, `.claude/agents/` — the SDLC skills and reviewer agents (source of truth)
- `plugins/slm-sdlc/` — **generated** plugin; never edit by hand, run `python scripts/build_plugin.py`

## Commands
- Install: `pip install -e ".[dev]"`
- Test: `pytest -q`
- Prepare data: `python scripts/prepare_data.py --download shakespeare --out data/shakespeare_char`
- Train: `python -m slm.train --config configs/shakespeare_char.toml`
- Sample: `python -m slm.sample --run runs/shakespeare_char --prompt "ROMEO:"`
- Rebuild plugin after editing skills/agents: `python scripts/build_plugin.py`
- Dashboard (container): `docker compose up --build` → http://localhost:8000
- Dashboard (dev): `uvicorn slm.dashboard.api:app --reload --port 8000` and `cd frontend && npm install && npm run dev` → http://localhost:5173

## Rules
- Follow `docs/sdlc.md`: no feature code without a spec in `docs/specs/`; significant
  trade-offs get an ADR in `docs/adr/`.
- Test first for model/data code. Keep the causality and overfit-one-batch tests passing.
- Every training run that informs a decision is logged in `docs/experiments/log.md`
  with its config path, git commit and val loss. Never report a metric you did not measure.
- `data/` and `runs/` are gitignored; anything there must be reproducible from scripts + configs.
- Keep the from-scratch model readable: prefer explicit code with comments over clever code.
