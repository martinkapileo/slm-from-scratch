# Experiment log

One row per run that informs a decision. Written by the `run-experiment` skill.
Raw outputs live in `runs/<name>/` (gitignored); this table is the durable record.

| Date | Run | Config | Commit | Params | Iters | Train loss | Val loss | Notes |
|------|-----|--------|--------|--------|-------|-----------|----------|-------|
| 2026-11-13 | shakespeare_char | `configs/shakespeare_char.toml` | f401444 | 0.88M | 3000 | 1.497 | 1.689 | Baseline. Meets SPEC-001 target (<1.7) narrowly. 18.7 min on 4 CPU cores (shared with tests/builds). Train/val gap widened from 0.00 to 0.19: mild overfitting; val still falling at end, so longer training or more dropout may help. |
