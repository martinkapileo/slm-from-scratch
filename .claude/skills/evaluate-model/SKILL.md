---
name: evaluate-model
description: SDLC stage 5 (Verify). Use to compare two or more trained runs, or to check a model against a spec's acceptance criteria — produces a side-by-side table of metrics and samples with a recommendation.
---

# Evaluate and compare models

1. **List the runs** to compare and the criteria (from the spec, or ask the owner).
2. **Gather metrics** from each `runs/<name>/metrics.jsonl` and `config.json`. Missing a run? Use `run-experiment` first; never estimate a metric.
3. **Use the right metric.** Val loss is comparable only between runs with the **same tokenizer and dataset**. Across tokenizers, compare bits-per-character or a task metric. Say so if runs aren't comparable.
4. **Sample with fixed seeds and prompts** for each run (`python -m slm.sample --run ... --seed 0 --prompt ...`), so differences come from the model, not randomness.
5. **Report a table**: run, params, val loss, train/val gap, training time, plus short samples. For anything enterprise-facing, add cost and latency columns.
6. **Recommend** one run and explain why in terms of the acceptance criteria. Check off the spec criteria that are met, linking the log rows.
