# Changelog

## 2026-11-13: Phase 1 scaffold
- Character-level GPT from scratch (`src/slm/`), training loop with warmup + cosine LR, sampling.
- Tests for shapes, initial loss, causality, overfitting one batch, and an end-to-end training smoke test.
- Agentic SDLC: `docs/sdlc.md`, spec and ADR templates, SPEC-001, ADR-0001.
- Claude Code skills (`write-spec`, `write-adr`, `run-experiment`, `evaluate-model`, `ship-phase`),
  agents (`ml-reviewer`, `architecture-reviewer`), a Python check hook, and the `slm-sdlc` plugin.
