# Agentic SDLC for this repo

This repo follows the agentic development loop Anthropic recommends for Claude Code
(**explore → plan → implement → verify → commit**), extended with the gates an ML
team needs: written specs, architecture decision records, logged experiments and
review by specialized agents.

Each stage has a tool in `.claude/` that does the work, so the process is enforced
by the repo rather than by memory.

| # | Stage | Question it answers | Tooling | Output |
|---|-------|--------------------|---------|--------|
| 1 | Explore | What exists today? | Built-in `Explore` agent, `CLAUDE.md` | Shared understanding, no code |
| 2 | Spec | What are we building and how do we know it works? | `write-spec` skill, plan mode | `docs/specs/<id>.md` with acceptance criteria |
| 3 | Design | Which option, and why? | `write-adr` skill, `architecture-reviewer` agent | `docs/adr/NNNN-*.md` |
| 4 | Implement | Build it, test-first | `tests/`, Python check hook | Code + tests |
| 5 | Verify | Does it meet the acceptance criteria? | `pytest`, `run-experiment` and `evaluate-model` skills | Passing tests, rows in `docs/experiments/log.md` |
| 6 | Review | What did we miss? | `ml-reviewer` agent, `/code-review` | Fixed findings |
| 7 | Ship | Is it merged and documented? | `ship-phase` skill, GitHub Actions CI | PR, updated roadmap and changelog |

## Rules of the loop

- **Small loops.** One spec covers about one PR. A phase in `docs/roadmap.md` is several loops.
- **Specs before code.** Acceptance criteria must be measurable, such as "val loss < 1.6 on
  shakespeare_char" or "p95 latency < 200 ms", never "works well".
- **ADRs for real decisions.** Write one when a choice has alternatives an interviewer
  could ask about, such as MLflow vs W&B or RAG vs fine-tuning. Skip trivial choices.
- **Evidence over claims.** A metric goes into a spec, ADR or PR only after it has a
  row in the experiment log.
- **Human gates.** The owner approves the spec (stage 2) and the PR (stage 7). Claude
  can run stages 3–6 autonomously in between.

## Where things live

```
.claude/
  settings.json          permissions + hook wiring
  hooks/check_python.py  stage 4: compile/lint every edited .py file
  skills/                stages 2, 3, 5, 7
  agents/                stages 3 and 6
plugins/slm-sdlc/        the same skills/agents/hook packaged as a plugin (generated)
.claude-plugin/          marketplace manifest so the plugin can be installed from GitHub
```

The `.claude/` copy is what Claude Code loads in this repo, both locally and in cloud
sessions. The plugin copy lets you install the same workflow into other repos:

```
/plugin marketplace add mkapileo12/slm-from-scratch
/plugin install slm-sdlc@slm-from-scratch
```
