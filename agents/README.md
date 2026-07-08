# Subagents

Subagent definitions for the HISTORA Oral-Systemic Intelligence Agent, in Claude
Code agent format (frontmatter `name` / `description` / `tools`). See
[`docs/PLAN.md` §3b](../docs/PLAN.md) for the architecture rationale.

## Runtime pipeline

| File | Role |
|---|---|
| `orchestrator.md` | Main agent: plans, routes, assembles the final output |
| `record-normalizer.md` | Integrates fragmented dental+medical records (HISTORA core) -> schema |
| `periodontal-analyst.md` | 2017 AAP/EFP staging & grading, progression |
| `cardiometabolic-analyst.md` | Non-diagnostic CV/metabolic pathway framing |
| `oral-systemic-relational-reasoner.md` | **Core**: relational axes & mediators (J-lens target) |
| `guardrail-verifier.md` | Adversarial guardrail + traceability gate |
| `hypothesis-generator.md` | Research hypotheses for follow-up |

Flow: normalize -> (periodontal ‖ cardiometabolic) -> relate -> hypotheses ->
verify -> assemble. The verifier can block; nothing failing the guardrail is emitted.

## Offline (dev-time) — not runtime subagents

| File | Role |
|---|---|
| `jlens-diagnostic.md` | Runs the Jacobian-lens harness on the Qwen proxy; proposes format/KB edits |
| `skillopt-optimizer.md` | Evolves trainable skills via bounded rollout->reflect->edit->gate |

## Skill ↔ subagent map

Each runtime subagent applies one skill from [`../skills/`](../skills/):
normalizer→`record-normalization`, periodontal→`periodontal-staging`,
cardiometabolic→`cardiometabolic-framing`, relational→`oral-systemic-analysis`
(+`oral-systemic-kb`), verifier→`non-diagnostic-guardrail`+`traceability-audit`.

`non-diagnostic-guardrail` is a **protected invariant**: the optimizer never edits it.
