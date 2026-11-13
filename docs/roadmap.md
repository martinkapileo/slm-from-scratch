# Roadmap

| Phase | Goal | Key skills learned | Status |
|-------|------|--------------------|--------|
| 1 | Tiny char-level GPT from scratch in PyTorch | Tokenization, attention, training loop, sampling | **In progress** |
| 2 | BPE tokenizer, Hugging Face reproduction, MLflow tracking, eval harness | Tokenizers, HF ecosystem, MLOps, evaluation | Planned |
| 3 | LoRA fine-tune of a small pretrained model; compare with Phase 1 | PEFT, transfer learning, cost/quality trade-offs | Planned |
| 4 | Docker + FastAPI/vLLM serving; RAG vs fine-tune comparison | Inference, latency/throughput, RAG architecture | Planned |
| 5 | Architecture doc: diagrams, cost model, governance, model card | Solution architecture, responsible AI | Planned |

## Open decisions
- **Target dataset/domain** for Phases 2–5 (Phase 1 uses Tiny Shakespeare as a known baseline).
- **Cloud** (AWS, Azure or GCP) for Phases 4–5: match target employers.
- **GPU access** (Colab, Kaggle or cloud) for Phase 3 onward.
