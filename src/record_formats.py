"""One synthetic combined medical + periodontal record, rendered in three
candidate input formats.

The three formats isolate the levers we optimize:
  A  abbreviated table, dental-first, no glossing of clinical terms
  B  named sections + glossed terms, medical-first
  C  narrative prose with an explicit mechanistic knowledge-base bridge

Hypothesis: C >= B >> A in the workspace rank of the mediator concepts.

This is SYNTHETIC data for methodology development. The task is non-diagnostic:
outputs are research hypotheses and data-completeness flags, never diagnoses.
"""

from __future__ import annotations

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
        "mean_ppd_mm": 5.2,
        "ppd_18m_ago_mm": 4.1,
        "cal_mm": 4.8,
        "bop_pct": 62,
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


FORMATS = {
    "A_abbrev_table": format_a_abbrev_table,
    "B_sections_glossed": format_b_sections_glossed,
    "C_narrative_mechanism": format_c_narrative_mechanism,
}

# Key patient values used by the capacity probe (single-token-friendly surfaces).
DATA_ITEMS = ["58", "20", "8.1", "155", "38", "210", "140", "62", "5.2", "4.8"]
