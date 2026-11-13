# ADR-0001: Build the first model in plain PyTorch, then adopt Hugging Face

- **Status:** Accepted
- **Date:** 2026-11-13
- **Related spec:** SPEC-001

## Context
The project has two goals: learn LLM fundamentals, and build a portfolio relevant to
enterprise AI architecture roles. Enterprises mostly use pretrained models through
Hugging Face and managed cloud services, but those layers hide the mechanics.

## Options considered
| Option | Pros | Cons |
|--------|------|------|
| Plain PyTorch from scratch | Every line understood; industry-standard framework | Reinvents existing code; slower to reach production features |
| Hugging Face `transformers` from day one | Enterprise-standard; fast | Mechanics hidden behind `from_pretrained` |
| JAX / Flax | Fast on TPUs | Smaller enterprise footprint; steeper curve |

## Decision
Phase 1 is plain PyTorch. Phase 2 reproduces the same model with Hugging Face so the
two can be compared line by line.

## Consequences
Phase 1 code favors readability over speed (for example, attention is written out
instead of using `scaled_dot_product_attention`). Revisit if training time blocks learning.
