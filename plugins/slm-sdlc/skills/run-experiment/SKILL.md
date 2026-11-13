---
name: run-experiment
description: SDLC stage 5 (Verify). Use to train or re-train a model in this repo — runs a config end to end (data prep, training, sampling) and records the result in docs/experiments/log.md so metrics are reproducible evidence.
---

# Run an experiment

1. **Define the hypothesis** in one sentence ("doubling n_layer lowers val loss below 1.6"). Tie it to a spec's acceptance criterion if one exists.
2. **Config, not code.** Copy the closest file in `configs/` to a new name and change only the variables under test. Set a unique `out_dir` under `runs/`.
3. **Make sure tests pass** (`pytest -q`). Don't train on broken code.
4. **Prepare data** if `data_dir` is missing: `python scripts/prepare_data.py ...` (see `CLAUDE.md`).
5. **Train**: `python -m slm.train --config <config>`. Runs over ~10 minutes go in the background. On CPU, estimate time from the first eval before committing to a long run.
6. **Read the results** from `runs/<name>/metrics.jsonl`. Check for overfitting: a train loss far below val loss means memorization.
7. **Sample**: `python -m slm.sample --run runs/<name>` and quote a short excerpt.
8. **Log it.** Append a row to `docs/experiments/log.md`: date, run name, config path, `git rev-parse --short HEAD` (add `-dirty` if uncommitted changes), params, iters, final train loss, best val loss, one-line note. Use only numbers the run printed.
9. **Report** hypothesis → result → what you'd try next. Explain any surprise in plain terms.
