# SPEC-002: Containerized results dashboard

- **Phase:** 1 (supporting tooling; the FastAPI service also seeds Phase 4 serving)
- **Status:** Approved
- **Owner approval:** 2026-11-13 (requested directly: React frontend, runs in a container)

## Problem
Training results live in `runs/*/metrics.jsonl` and are only visible in terminal output.
Comparing runs and checking samples needs a visual view, including while training runs.

## Scope
In:
- FastAPI read-only API over `runs/`: list runs, metrics, config, generate text from a checkpoint
- React + TypeScript (Vite) single-page dashboard: run list, stat tiles, live loss curves with the SPEC-001 target line, config table, generation panel
- Multi-stage Dockerfile (Node build → slim Python runtime, CPU PyTorch, non-root, healthcheck) and docker-compose with `runs/` and `data/` mounted read-only

Out:
- Authentication, multi-user deployment, launching training from the UI (Phase 4)

## Approach
`src/slm/dashboard/api.py` serves `/api/*` and, when `SLM_STATIC_DIR` is set, the built React app at `/`.
The frontend polls every 5 s so live runs update. Runs now save `tokenizer.json` so a run directory is self-contained.

## Acceptance criteria
- [x] API tests pass, including path-traversal rejection and out-of-vocabulary prompt rejection (`tests/test_dashboard_api.py`)
- [x] `npm run build` succeeds with strict TypeScript
- [x] Dashboard shows a live training run and generates text in a browser (verified with Playwright screenshot)
- [ ] `docker compose up --build` serves the dashboard on :8000 (not verifiable in the cloud session: CPU PyTorch host blocked; verify locally)

## Verification plan
`pytest -q`; `cd frontend && npm run build`; run uvicorn and exercise the UI; `docker compose up --build` locally.

## Learning notes
Separating the API from the UI is the standard serving pattern: the same `/api/runs/{name}/sample`
endpoint is the seed of the Phase 4 inference service, where latency and throughput start to matter.
