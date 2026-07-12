---
name: cardiometabolic-framing
description: Frame cardiovascular and metabolic risk factors (lipids, HbA1c/diabetes, blood pressure, smoking, medications, family history) in a non-diagnostic, research-oriented way, highlighting the factors that mediate or share pathways with periodontal disease. Not a risk calculator or diagnosis. SkillOpt-trainable.
---

# Cardiometabolic Framing Skill (non-diagnostic)

Frame the systemic cardiovascular/metabolic picture so oral-systemic relations are
representable. This is a **research framing**, not a diagnosis or a validated risk
score.

## Framing discipline

- Group systemic data by pathway so the relational reasoner can link it to oral
  findings:
  - **Inflammatory/vascular:** hs-CRP, other inflammatory markers, prior CV events,
    family history of early MI.
  - **Metabolic:** HbA1c / diabetes status, lipid panel (LDL/HDL/triglycerides), BMI.
  - **Behavioral (shared):** smoking (pack-years, current/former), which is a risk
    factor common to both periodontitis and cardiovascular disease.
- Name the **mediating markers** explicitly (inflammation, C-reactive protein,
  atherosclerosis, endothelial dysfunction) when the data supports the pathway —
  these are the oral-systemic bridges.
- Note medications that modify a pathway (statins, antihypertensives,
  anticoagulants, metformin) and their direction of effect at a framing level.

## Machine-checkable pathway tagging (required)

- **Every** factor line — present, elevated, normal, or missing — must end with a
  literal, machine-checkable tag in exactly this form:
  `[pathway: <inflammatory|vascular|metabolic|behavioral>]`.
  Use `inflammatory` and `vascular` as distinct tags when the datum is clearly one
  or the other (e.g. hs-CRP → `inflammatory`; prior MI, BP → `vascular`); use
  whichever single tag best fits if a datum plausibly spans two categories, and
  do not invent a fifth category.
- Section headers (e.g. "**Metabolic pathway:**") and narrative/summary text are
  not factor lines and do not need the tag, but every bullet that states an input
  field's value, status, or missing-status must carry it.
- Format for each factor line:
  `- **<Factor name>:** <value or MISSING> (input: `field_name = value`); <brief
  pathway rationale>. [pathway: <tag>]`
- Example:
  - `- **hs-CRP:** MISSING — required for inflammatory-axis assessment (input:
    `hs_crp` not provided). [pathway: inflammatory]`
  - `- **LDL:** 165 mg/dL (input: `ldl = 165`); lipid component of metabolic
    pathway. [pathway: metabolic]`
  - `- **Smoking:** current, 20 pack-years (input: `smoking = "current, 20py"`);
    shared behavioral risk factor. [pathway: behavioral]`
  - `- **Prior MI:** documented (input: `prior_mi = "yes"`); marks prior
    atherosclerotic vascular event. [pathway: vascular]`

## Non-diagnostic discipline

- Do not compute or imply a validated CV risk percentage or diagnosis.
- Do not recommend treatment or medication changes.
- If a pathway-defining datum is missing (e.g. no hs-CRP for the inflammatory
  axis), flag it for collection with its pathway tag; never impute the value.

## Output discipline

- Report the pathway groupings, the mediating markers present vs. missing, and the
  input fields each framing was derived from.
- Confirm before finalizing that every factor line (present or missing) carries a
  `[pathway: ...]` tag; a line without one is incomplete and must be corrected.
