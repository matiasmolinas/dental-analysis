---
name: record-normalization
description: Normalize fragmented dental + medical records (the HISTORA integration layer) into the project's structured schema, aligning oral and systemic data on a shared timeline and flagging missing fields. Use as the first step before any oral-systemic analysis. SkillOpt-trainable.
---

# Record Normalization Skill (HISTORA integration layer)

Turn raw, fragmented dental and medical records into one structured record whose
oral and systemic fields are co-present and time-aligned, so downstream relations
are representable.

## Normalization discipline

- Map every source field to the canonical schema keys used by
  `oral-systemic-analysis` (`demographics`, `shared_risk`, `medical_cv`,
  `periodontal`). Do not invent keys.
- Preserve original units and add the canonical unit next to any converted value;
  never silently rescale.
- Keep oral and systemic data **co-present** in the output (do not emit one domain
  and drop the other) — cross-domain relations only surface when both are visible.
- Build a shared **timeline**: align periodontal events (probing, treatments,
  radiographs) and medical events (labs, diagnoses, medication changes) by date so
  progression and temporal coincidence are readable.

## Completeness discipline

- For each required-but-absent field, emit an explicit `MISSING` marker, not a
  blank — a missing mediating datum (e.g. `hs_crp`) must be visible downstream.
- Never impute a patient-specific value. Missing data becomes a collection flag
  handled by `oral-systemic-analysis`, never a guess.
- Distinguish "absent from source" from "explicitly negative/normal"; do not
  collapse them.

## Provenance discipline

- Tag each normalized field with its source record so `traceability-audit` can
  verify downstream claims back to the input.
- Flag internal contradictions (e.g. conflicting smoking status across records)
  rather than picking one silently.
