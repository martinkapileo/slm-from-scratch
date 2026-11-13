---
name: ship-phase
description: SDLC stage 7 (Ship). Use when a spec's work is done and ready to merge — runs the release checklist, updates roadmap/spec/changelog, and opens a pull request for owner approval.
---

# Ship

Run each gate; stop and report if one fails.

1. **Tests:** `pytest -q` passes.
2. **Plugin in sync:** `python scripts/build_plugin.py --check` passes (run without `--check` to regenerate if skills/agents changed).
3. **Acceptance criteria:** every box in the spec is checked, each backed by a test or a row in `docs/experiments/log.md`. Unchecked boxes → not ready; say which.
4. **Review:** the `ml-reviewer` agent has reviewed the diff and its findings are fixed or explicitly deferred.
5. **Docs:** set the spec to `Status: Done`; update `docs/roadmap.md` status; add a dated entry to `CHANGELOG.md` (what changed, what was learned).
6. **Branch and PR:** work on a branch named `spec-NNN-slug`, never on `main`. Commit with a message referencing the spec id. Open a PR whose body lists the spec, acceptance criteria with evidence links, and the learning notes.
7. **Hand off:** the owner reviews and merges. Do not merge yourself.
