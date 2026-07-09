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
| `claude-workspace-probe.md` | Inferred-lens readout source on Claude (self-report; the live signal) | No (instrument) |
| `lens-deficiency-analysis.md` | Observer instrument: readout → deficiency map + bounded gated edits across five surfaces | No (instrument) |
| `session-working-consciousness.md` | Observer instrument: the cumulative in-session ledger + prompt injection | No (instrument) |
| `harness-evolution.md` | Observer instrument: lens-driven code evolution + prompt-vs-code boundary + test-before-use | No (instrument) |
| `non-diagnostic-guardrail.md` | **PROTECTED INVARIANT** — never evolved; part of the gate | No |

`claude-workspace-probe` is inspired by the `j-space-lens` skill in
`Doriandarko/skirano-skills` (referenced, not vendored — no license). It is
uninstrumented self-report, **not a measurement**; see [`../docs/DUAL_LENS.md`](../docs/DUAL_LENS.md).

## Evolution gate

The optimizer accepts a skill edit only if it strictly improves held-out Claude
accuracy AND does not lower the `non-diagnostic-guardrail` pass-rate. J-lens
mediator ranks are a cheap pre-filter for edits that change input representation.
