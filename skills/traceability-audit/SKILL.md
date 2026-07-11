---
name: traceability-audit
description: Audit an oral-systemic analysis for traceability and evidence integrity - every relational axis and claim must cite the exact input fields it was derived from, with no unsupported or hallucinated relations. Used by the guardrail/verifier subagent. SkillOpt-trainable (but runs alongside the protected non-diagnostic guardrail).
---

# Traceability Audit Skill

Verify that every claim in a structured oral-systemic output is grounded in the
input record.

## Audit discipline

- For each `relational_axes[*]`, confirm `traceability` lists real fields that
  exist in the normalized record; reject axes citing absent or invented fields.
- Confirm `oral_evidence` and `systemic_evidence` items are actual values from the
  record, not paraphrases that drift from the data.
- Reject any relation asserted without both an oral and a systemic anchor (a
  cross-domain axis needs both sides present).
- Check that `hypothesized_mechanism` is a recognized association from
  `oral-systemic-kb`, not a novel causal invention.

## Confidence discipline

- Down-rate confidence when an axis leans on a `MISSING` mediating datum; the
  correct move is a `required_missing_data` flag, not a high-confidence claim.
- Flag over-claiming: language implying diagnosis, causation in an individual, or
  treatment benefit must be softened to association/hypothesis.

## Output discipline

- Return a per-claim verdict (supported / unsupported / over-claimed) with the
  offending field or phrase, so the orchestrator can revise before finalizing.
