---
name: write-spec
description: SDLC stage 2 (Spec). Use before starting any new feature, phase step or non-trivial change in this repo — write a spec with measurable acceptance criteria in docs/specs/ and get owner approval before implementing.
---

# Write a spec

1. **Explore first.** Read `docs/roadmap.md`, existing specs in `docs/specs/`, and the code the change touches. Do not write code in this stage.
2. **Pick the id.** Next free `SPEC-NNN` number in `docs/specs/`. File name: `SPEC-NNN-short-slug.md`.
3. **Fill `docs/specs/_template.md`.** Rules:
   - Acceptance criteria must be measurable (a test name, a metric threshold with its config, a latency or cost number). Reject vague wording like "works well".
   - State what is **out** of scope.
   - If the approach involves a real trade-off, note "ADR needed" and use the `write-adr` skill.
   - Fill *Learning notes*: the owner is studying LLM fundamentals.
4. **Set status `Draft`** and show the owner a summary: problem, approach, acceptance criteria.
5. **Stop and wait for approval.** On approval set `Status: Approved` and the approval date. Only then move to implementation (test-first).
