# Skills

Reusable capability documents (Claude Code skill format: frontmatter + procedural body) for the
HISTORA non-diagnostic relational agent. See [`SOLUTION.md`](../../../docs/SOLUTION.md).

| Skill | Purpose |
|---|---|
| `oral-systemic-analysis.md` | Core: optimized input format + structured non-diagnostic output + guardrails |
| `record-normalization.md` | Raw dental + medical records → schema, timeline, MISSING flags |
| `periodontal-staging.md` | 2017 AAP/EFP periodontal staging & grading framing |
| `cardiometabolic-framing.md` | Non-diagnostic cardiovascular / metabolic pathway framing |
| `oral-systemic-kb.md` | Retrievable mediator-mechanism knowledge base (CV + neuro) |
| `traceability-audit.md` | Verify every claim cites the input fields it was derived from |
| `non-diagnostic-guardrail.md` | **PROTECTED INVARIANT** — part of every gate; never edited |

## The guardrail

The `non-diagnostic-guardrail` is enforced at every gate: research hypotheses and data-completeness
flags only, never a diagnosis; missing data is a collection flag, never an imputed patient value; every
relational axis cites its input fields. The deterministic layer that guarantees the guardrail-critical
missing-data flags lives in `histora.relational_signals` (the W1 win).
