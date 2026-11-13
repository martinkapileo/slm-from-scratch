# slm-from-scratch

Build a small language model from scratch to learn LLM fundamentals, then productionize
it the way an enterprise AI team would: experiment tracking, evaluation, fine-tuning,
serving, and an architecture and governance write-up.

Development follows an **agentic SDLC** (explore → spec → design → implement → verify →
review → ship), encoded as Claude Code skills, agents and hooks. See [`docs/sdlc.md`](docs/sdlc.md).

## Quickstart

```bash
pip install -e ".[dev]"
pytest -q
python scripts/prepare_data.py --download shakespeare --out data/shakespeare_char
python -m slm.train --config configs/shakespeare_char.toml
python -m slm.sample --run runs/shakespeare_char --prompt "ROMEO:"
```

## Roadmap

| Phase | Focus |
|-------|-------|
| 1 | Character-level GPT from scratch in PyTorch |
| 2 | BPE tokenizer, Hugging Face reproduction, MLflow, eval harness |
| 3 | LoRA fine-tuning of a pretrained small model |
| 4 | Docker + FastAPI/vLLM serving; RAG vs fine-tuning |
| 5 | Architecture doc: cost model, governance, model card |

Details and status: [`docs/roadmap.md`](docs/roadmap.md).

## Repository map

```
src/slm/            model, data, training and sampling code
configs/            TOML hyperparameter configs (one per experiment)
scripts/            data prep and plugin build
tests/              unit tests encoding transformer properties
docs/               SDLC guide, roadmap, specs, ADRs, experiment log
.claude/            Claude Code skills, agents, hooks, settings (source of truth)
plugins/slm-sdlc/   the same workflow packaged as an installable plugin (generated)
.claude-plugin/     marketplace manifest
```

## Use the SDLC plugin in another repo

```
/plugin marketplace add mkapileo12/slm-from-scratch
/plugin install slm-sdlc@slm-from-scratch
```
