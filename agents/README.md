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

## Reformulated loop, dual-lens & offline (dev-time / in-loop)

| File | Role |
|---|---|
| `lens-observer.md` | **Secondary instance (Opus).** Analyzes the primary's inferred-lens readout, diagnoses deficiencies, curates the Session Working-Consciousness, drives bounded gated evolution of five surfaces + injects prompts |
| `claude-workspace-probe.md` | The inferred-lens readout source ON CLAUDE (real target, no GPU); surfaces mediators per format. Not a measurement |
| `jlens-diagnostic.md` | Measured Jacobian-lens harness on the Qwen proxy — the documented *validation/unlock* path (offline correlation), not a live dependency |
| `skillopt-optimizer.md` | **T1 promotion tier.** Evolves the five surfaces (prompts/skills/KB/sub-agent defs+variables/harness code) via bounded rollout->reflect->edit->gate |

The reformulated loop (inferred-lens Observer + Session Working-Consciousness) is in
[`../docs/REFORMULATION.md`](../docs/REFORMULATION.md); the two-instrument dual-lens
methodology and correlation experiment in [`../docs/DUAL_LENS.md`](../docs/DUAL_LENS.md).

## Skill ↔ subagent map

Each runtime subagent applies one skill from [`../skills/`](../skills/):
normalizer→`record-normalization`, periodontal→`periodontal-staging`,
cardiometabolic→`cardiometabolic-framing`, relational→`oral-systemic-analysis`
(+`oral-systemic-kb`), verifier→`non-diagnostic-guardrail`+`traceability-audit`.

`non-diagnostic-guardrail` is a **protected invariant**: the optimizer never edits it.
