"""One synthetic combined medical + periodontal record, rendered in three
candidate input formats.

The formats isolate the levers we optimize (A–E below):
  A  abbreviated table, dental-first, no glossing of clinical terms
  B  named sections + glossed terms, medical-first
  C  narrative prose with an explicit mechanistic knowledge-base bridge
  D  structured JSON, no narrative, no KB
  E  JSON + KB + interpretability constraints

Hypothesis: E >= C >= B >> A in whether the mediator concepts surface in the primary's
inferred-lens readout (self-report on Claude, not a measurement).

Data grounding: values are chosen to be consistent with real NHANES 2009-2010
distributions (the cycle that pairs the full-mouth periodontal exam with CRP);
see docs/DATASETS.md and histora/nhanes.py. `nhanes.build_case` can
replace this hand-written case with a real grounded participant row. The
longitudinal field `ppd_18m_ago_mm` has NO NHANES source (NHANES is
cross-sectional) — it is Synthea-style progression, flagged below.

This is a NHANES-grounded SYNTHETIC case for methodology development. The task is
non-diagnostic: outputs are research hypotheses and data-completeness flags, never
diagnoses.
"""

from __future__ import annotations

import json

# Provenance: schema field -> data source. Real fields trace to NHANES 2009-2010
# variables (see histora.nhanes.SCHEMA_TO_NHANES); progression is synthetic.
PROVENANCE = {
    "cross_sectional_fields": "NHANES 2009-2010 (grounded values; see histora.nhanes)",
    "ppd_18m_ago_mm": "Synthea-style longitudinal progression (no NHANES source)",
}

RECORD = {
    "demographics": {"age": 58, "sex": "M", "bmi": 29.4},
    "shared_risk": {
        "smoking_pack_years": 20,
        "smoking_active": True,
        "type2_diabetes": True,
        "hba1c": 8.1,
        "hypertension": True,
        "blood_pressure": "140/90",
    },
    "medical_cv": {
        "ldl": 155,
        "hdl": 38,
        "triglycerides": 210,
        "hs_crp": None,  # deliberately missing -> should trigger a completeness flag
        "prior_cv_event": False,
        "family_history_mi": True,
        "medications": ["enalapril", "metformin"],
        "on_statin": False,
    },
    "periodontal": {
        "mean_ppd_mm": 5.2,          # OHXPER_F per-site probing depth (mean)
        "ppd_18m_ago_mm": 4.1,       # SYNTHETIC progression — no NHANES source (Synthea)
        "cal_mm": 4.8,               # OHXPER_F per-site attachment loss (mean)
        "bop_pct": 62,               # OHXPER_F bleeding-on-probing sites
        "radiographic_bone_loss": "moderate-to-severe, generalized",
        "diagnosis": "periodontitis stage III grade B",
        "regular_maintenance": False,
    },
}

TARGET_ANSWER_HINT = "elevated oral-systemic risk driven by the inflammatory axis"


def format_a_abbrev_table(r: dict) -> str:
    """Abbreviated, dental-first, no term glossing."""
    return (
        "PERIO: PPD 5.2(^4.1) CAL 4.8 BOP 62% BoneLoss mod-sev; dx perio III/B\n"
        "MED: HbA1c 8.1 LDL 155 HDL 38 TG 210 HTN 140/90 smoker 20py CRP ?\n"
        "Q: oral-systemic risk?"
    )


def format_b_sections_glossed(r: dict) -> str:
    """Named sections + glossed terms, medical-first."""
    return (
        "## SHARED RISK FACTORS\n"
        "smoking: 20 pack-years (active) | type 2 diabetes: yes, HbA1c 8.1% | "
        "hypertension 140/90\n"
        "## CARDIOVASCULAR PROFILE\n"
        "LDL 155, HDL 38, TG 210 | hs-CRP: MISSING | family history of MI: yes | "
        "statin: no\n"
        "## PERIODONTAL PROFILE (longitudinal)\n"
        "mean PPD 5.2 mm (up from 4.1 mm 18 months ago) | CAL 4.8 mm | "
        "BOP 62% (bleeding on probing = marker of gingival inflammation) | "
        "bone loss moderate-to-severe | periodontitis stage III grade B\n"
        "## QUESTION\nWhat is the oral-systemic risk profile and which relational axes apply?"
    )


def format_c_narrative_mechanism(r: dict) -> str:
    """Narrative prose with an explicit mechanistic KB bridge."""
    return (
        "Context: periodontitis can raise systemic inflammatory burden, which is "
        "associated with cardiovascular risk through markers such as C-reactive protein.\n"
        "A 58-year-old man, smoker (20 pack-years), type 2 diabetic with HbA1c 8.1%, "
        "hypertensive, LDL 155 / HDL 38, with periodontitis stage III grade B, BOP 62%, "
        "and progressive moderate-to-severe bone loss. No CRP on record and not on a statin.\n"
        "What oral-systemic risk profile and relational axes does this suggest?"
    )


def format_d_structured_json(r: dict) -> str:
    """Structured JSON record (schema-shaped), no narrative and no KB."""
    return (
        "Analyze this integrated oral-systemic record (non-diagnostic).\n"
        "Record (JSON):\n" + json.dumps(r, indent=2) + "\n\n"
        "Question: oral-systemic risk profile and relational axes?"
    )


def format_e_json_kb_constraints(r: dict) -> str:
    """JSON + mechanistic KB + interpretability constraints (reason through mediators)."""
    kb = (
        "Knowledge base: periodontitis raises systemic inflammatory burden "
        "(C-reactive protein, IL-6), linked to cardiovascular risk via endothelial "
        "dysfunction and atherosclerosis; the oral microbiome mediates bacteremia and "
        "inflammation (AHA statement; HOMD)."
    )
    constraints = (
        "Constraints: reason explicitly through the mediating concepts (inflammation, "
        "C-reactive protein, atherosclerosis, endothelial dysfunction, bacteremia); "
        "flag any missing mediating datum as data to collect; never impute a patient "
        "value; non-diagnostic (association/hypothesis only)."
    )
    return (
        kb + "\n\nRecord (JSON):\n" + json.dumps(r, indent=2) + "\n\n" + constraints +
        "\n\nQuestion: oral-systemic risk profile and relational axes?"
    )


FORMATS = {
    "A_abbrev_table": format_a_abbrev_table,
    "B_sections_glossed": format_b_sections_glossed,
    "C_narrative_mechanism": format_c_narrative_mechanism,
    "D_structured_json": format_d_structured_json,
    "E_json_kb_constraints": format_e_json_kb_constraints,
}
