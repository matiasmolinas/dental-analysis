# Skills

Reusable capability documents (Claude Code skill format: frontmatter + procedural
body). The body of each trainable skill is a SkillOpt-style artifact — compact,
auditable, imperative discipline — so it can be evolved by the `skillopt-optimizer`
(reference: sibling `SkillOpt/` repo). See [`docs/PLAN.md` §3b](../docs/PLAN.md).

| Skill | Purpose | Trainable? |
|---|---|---|
| `oral-systemic-analysis.md` | Core: optimized input format + structured output + guardrails | Yes (J-lens + SkillOpt) |
| `record-normalization.md` | HISTORA integration: raw records -> schema, timeline, MISSING flags | Yes |
| `periodontal-staging.md` | 2017 AAP/EFP staging & grading framing | Yes |
| `cardiometabolic-framing.md` | Non-diagnostic CV/metabolic pathway framing | Yes |
| `oral-systemic-kb.md` | Retrievable mediator-mechanism knowledge base | Reference (context) |
| `traceability-audit.md` | Verify every claim cites input fields | Yes |
| `non-diagnostic-guardrail.md` | **PROTECTED INVARIANT** — never evolved; part of the gate | No |

## Evolution gate

The optimizer accepts a skill edit only if it strictly improves held-out Claude
accuracy AND does not lower the `non-diagnostic-guardrail` pass-rate. J-lens
mediator ranks are a cheap pre-filter for edits that change input representation.
