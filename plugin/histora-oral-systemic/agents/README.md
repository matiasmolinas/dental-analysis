# Subagents

The HISTORA non-diagnostic relational agent, as Claude Code subagent definitions (frontmatter
`name` / `description` / `tools`). See [`PAPER.md`](../../../docs/PAPER.md) for how these fit
the whole solution.

## Runtime pipeline

| File | Role |
|---|---|
| `orchestrator.md` | Main agent: plans, routes, assembles the final non-diagnostic output |
| `record-normalizer.md` | Integrates fragmented dental + medical records into the schema (timeline, MISSING flags) |
| `periodontal-analyst.md` | 2017 AAP/EFP periodontal staging & grading; progression |
| `cardiometabolic-analyst.md` | Non-diagnostic cardiovascular / metabolic pathway framing |
| `oral-systemic-relational-reasoner.md` | **Core**: relates oral ↔ systemic data into relational axes + mediators |
| `guardrail-verifier.md` | Adversarial non-diagnostic guardrail + traceability gate |
| `hypothesis-generator.md` | Research hypotheses for follow-up |

Flow: **normalize → (periodontal ‖ cardiometabolic) → relate → hypotheses → verify → assemble.** The
verifier can block; nothing that fails the guardrail is emitted. The Python entrypoint that runs this
analysis on Claude is `src/run_agent.py` (see `histora.agent`).

## Skill ↔ subagent map

Each subagent applies one skill from [`../skills/`](../skills/): normalizer→`record-normalization`,
periodontal→`periodontal-staging`, cardiometabolic→`cardiometabolic-framing`,
relational→`oral-systemic-analysis` (+`oral-systemic-kb`),
verifier→`non-diagnostic-guardrail` + `traceability-audit`.

`non-diagnostic-guardrail` is a **protected invariant** — never edited.

## Modeling-extension subagent

| File | Role |
|---|---|
| `modeling-technique-selector.md` | For an oral-systemic edge the coded harness cannot yet reach: recommends the technique to code next and, while it is un-coded, produces a soft falsifiable estimate that enters the ensemble as a **weight-capped Claude member** (`histora.claude_model` → `ensemble.blend_members`). See docs/PAPER.md §3.5. |

This is the "Claude as a model member" role — a step toward a coded model, never a permanent
substitute; population/parameter level, non-diagnostic, and it must ship a falsification path.
