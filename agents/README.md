# Subagents

The HISTORA non-diagnostic relational agent, as Claude Code subagent definitions (frontmatter
`name` / `description` / `tools`). See [`../docs/SOLUTION.md`](../docs/SOLUTION.md) for how these fit
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
