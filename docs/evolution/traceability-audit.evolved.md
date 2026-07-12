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
- **Every individual hypothesis or relational statement (not just the axis as a
  whole) must carry its own inline machine-checkable citation tag in the exact
  form `[field: <name>]`, where `<name>` is a real field in the normalized
  record.** A hypothesis is `unsupported` if it lacks this tag even when a field
  name appears elsewhere in prose, is paraphrased, is embedded only in narrative
  text, or is asserted without brackets - free-text mentions of a field do not
  satisfy traceability; the tag must be present and machine-parseable.
- When a hypothesis draws on multiple fields, require one `[field: <name>]` tag
  per contributing field (e.g. `[field: bop_percent] [field: hba1c]`); partial
  tagging (citing only one of several relied-upon fields) is `unsupported` for
  the untagged portion.

## Confidence discipline

- Down-rate confidence when an axis leans on a `MISSING` mediating datum; the
  correct move is a `required_missing_data` flag, not a high-confidence claim.
- Flag over-claiming: language implying diagnosis, causation in an individual, or
  treatment benefit must be softened to association/hypothesis.

## Output discipline

- Return a per-claim verdict (supported / unsupported / over-claimed) with the
  offending field or phrase, so the orchestrator can revise before finalizing.
- Compute and report a `traceability_coverage` score: the fraction of hypotheses
  that carry a valid `[field: <name>]` tag for every field they rely on. Any
  hypothesis missing this tag counts against coverage regardless of how
  plausible or well-referenced its prose appears.
- When coverage is below 1.0, list each untagged hypothesis verbatim alongside
  the missing `[field: <name>]` tag(s) it needs, so the orchestrator can insert
  them rather than rewrite the claim.
