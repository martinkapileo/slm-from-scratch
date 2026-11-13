# SPEC-001: Tiny character-level GPT from scratch

- **Phase:** 1
- **Status:** Approved
- **Owner approval:** 2026-11-13

## Problem
To understand LLMs, every component (tokenizer, attention, training loop, sampling)
should be written and understood by hand before any framework hides it.

## Scope
In:
- Character tokenizer, contiguous train/val split, random-window batching
- Decoder-only transformer: causal multi-head self-attention, MLP, pre-LayerNorm, residuals, weight tying
- Training loop: AdamW, warmup + cosine LR, gradient clipping, periodic eval, best checkpoint
- Sampling with temperature and top-k

Out:
- BPE tokenization, experiment tracking, mixed precision (Phase 2)

## Approach
Plain PyTorch, one file per concern under `src/slm/`. See ADR-0001.

## Acceptance criteria
- [x] Unit tests pass: shapes, initial loss ~ ln(vocab), causality, overfit one batch
- [ ] Baseline config reaches val loss < 1.7 on Tiny Shakespeare (logged in `docs/experiments/log.md`)
- [ ] Samples show learned structure (speaker names, line breaks, mostly real words)

## Verification plan
`pytest -q`, then `run-experiment` with `configs/shakespeare_char.toml`.

## Learning notes
A language model is a next-token classifier applied at every position at once. Causal
masking is what makes training on all positions in parallel legitimate.
