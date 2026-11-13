---
name: write-adr
description: SDLC stage 3 (Design). Use when a choice has real alternatives worth defending (framework, tracking tool, tokenizer, serving stack, RAG vs fine-tune, cloud service) — record it as an Architecture Decision Record in docs/adr/.
---

# Write an Architecture Decision Record

1. **Check it is ADR-worthy.** Would an interviewer for an AI architect role ask "why this and not X?" If not, skip the ADR and note the choice in the spec.
2. **Number it.** Next free `NNNN` in `docs/adr/`; file `NNNN-kebab-title.md`, from `docs/adr/_template.md`.
3. **Options table.** At least two real options. Weigh them on the axes enterprises care about: cost, operational burden, vendor lock-in, security/compliance, team skills, and quality. Cite measurements from `docs/experiments/log.md` where they exist; label anything else as an estimate.
4. **Decision and consequences.** One-sentence decision. Consequences must include what would make us revisit it.
5. **Review.** Ask the `architecture-reviewer` agent to challenge the ADR, address its findings, then set `Status: Accepted`.
6. **Supersede, don't edit.** To change an accepted decision, write a new ADR and mark the old one `Superseded by ADR-XXXX`.
