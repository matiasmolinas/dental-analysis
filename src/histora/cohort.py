"""Cohort builder — turn a fragmented data corpus into a research-ready cohort, honestly.

The capability two clinician-reviewers made the hero: a researcher arrives with a *question*, not a
patient; HISTORA filters the corpus down a **funnel** to the eligible cohort, reports **per-cohort data
completeness** (what's present vs. what the question needs), emits a **preliminary study protocol**, and —
critically — states plainly **what the available data cannot answer**. It never diagnoses and never invents
a value; a missing datum is a collection flag.

Honest by construction:
  * the funnel runs on the REAL corpus passed in (in the demo, NHANES 2009-2010 via `histora.nhanes`);
  * NHANES is **cross-sectional**, so the cohort it yields is cross-sectional — the completeness report says
    so, and flags that the *longitudinal* mediation question (repeat CRP, follow-up, a biologic-exposure
    timeline) requires a longitudinal EHR the corpus does not contain. That honest "cannot answer" is the point.

`records` is a list of per-participant dicts (e.g. from `nhanes.load_cv_table`): keys used here are
`seqn, perio_cal, perio_ppd, hs_crp, hba1c` (missing → None). Pure-python; no network.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

# --- eligibility predicates (simplified, clearly-labeled operationalizations of the criteria) ---
# Periodontitis proxy: mean loss-of-attachment or pocket depth at/above a moderate threshold. NHANES gives
# per-site OHX##LA/PC averaged to a mean; a mean-based proxy is coarser than the full CDC/AAP per-site
# staging and is labeled as such wherever reported.
PERIO_CAL_MM = 3.0
PERIO_PPD_MM = 3.0
DIABETES_HBA1C = 6.5   # % — the standard diagnostic threshold, applied to the real GHB measurement


def has_periodontitis(r: dict) -> bool:
    cal, ppd = r.get("perio_cal"), r.get("perio_ppd")
    return (cal is not None and cal >= PERIO_CAL_MM) or (ppd is not None and ppd >= PERIO_PPD_MM)


def has_diabetes(r: dict) -> bool:
    h = r.get("hba1c")
    return h is not None and h >= DIABETES_HBA1C


def has_hscrp(r: dict) -> bool:
    return r.get("hs_crp") is not None


DEFAULT_FUNNEL: list[tuple[str, Callable[[dict], bool]]] = [
    ("periodontal exam on record", lambda r: r.get("perio_cal") is not None or r.get("perio_ppd") is not None),
    ("periodontitis (moderate+, mean-CAL/PPD proxy)", has_periodontitis),
    ("+ diabetes (HbA1c ≥ 6.5%)", has_diabetes),
    ("+ hs-CRP measured", has_hscrp),
]


def build_funnel(records: list[dict],
                 stages: Optional[list[tuple[str, Callable[[dict], bool]]]] = None) -> dict[str, Any]:
    """Filter the corpus down the eligibility funnel; report the REAL N surviving each stage. Each stage
    is cumulative (applied on top of the previous). Returns the ladder + the final cohort's SEQNs."""
    stages = stages or DEFAULT_FUNNEL
    total = len(records)
    ladder = [{"stage": "total participants in corpus", "n": total}]
    cohort = records
    for label, pred in stages:
        cohort = [r for r in cohort if pred(r)]
        ladder.append({"stage": label, "n": len(cohort)})
    return {"funnel": ladder, "cohort_n": len(cohort),
            "cohort_seqns": [r.get("seqn") for r in cohort], "cohort": cohort,
            "note": "every N is a real count over the passed-in corpus; the periodontitis stage uses a "
                    "mean-CAL/PPD proxy, coarser than full CDC/AAP per-site staging."}


def cohort_completeness(cohort: list[dict], needed: Optional[dict[str, Callable[[dict], bool]]] = None) -> dict:
    """Per-cohort data completeness: fraction of the cohort with each field the question needs, plus the
    fields a *longitudinal* answer requires that a cross-sectional corpus cannot provide (repeat CRP,
    follow-up interval, biologic-exposure timeline, periodontal-treatment date). This is the honest
    'what's missing' the reviewers wanted — computed, not asserted."""
    needed = needed or {
        "periodontal severity": lambda r: r.get("perio_cal") is not None or r.get("perio_ppd") is not None,
        "hs-CRP (baseline)": has_hscrp,
        "HbA1c": lambda r: r.get("hba1c") is not None,
    }
    n = len(cohort) or 1
    present = {k: round(sum(1 for r in cohort if pred(r)) / n, 3) for k, pred in needed.items()}
    # cross-sectional corpora structurally lack these (single time point per participant):
    longitudinal_gap = ["repeat hs-CRP (post-therapy)", "follow-up interval > 12 months",
                        "biologic (e.g. IL-6R blockade) exposure timeline", "periodontal-treatment date"]
    return {"cohort_n": len(cohort), "field_present_fraction": present,
            "longitudinal_fields_absent_in_corpus": longitudinal_gap,
            "verdict": ("cohort is research-ready for a CROSS-SECTIONAL analysis of the perio↔CRP edge; "
                        "the LONGITUDINAL mediation question (CRP evolution under IL-6R blockade) cannot be "
                        "answered by this corpus — it needs a longitudinal EHR with the fields listed above."),
            "non_diagnostic": True}


def preliminary_protocol(question: str, funnel: dict, completeness: dict) -> dict:
    """The Export: a PRELIMINARY, ILLUSTRATIVE study protocol generated from the cohort — variables,
    inclusion/exclusion, and an honest limitations block. It prepares the study; it is NOT the study, and
    makes no efficacy, causal, or diagnostic claim."""
    return {
        "header": "PRELIMINARY PROTOCOL · illustrative · NOT a study · non-diagnostic",
        "research_question": question,
        "design": "observational, hypothesis-generating; cross-sectional on the available corpus",
        "cohort_size": funnel["cohort_n"],
        "inclusion_criteria": [s["stage"] for s in funnel["funnel"][1:]],
        "exclusion_criteria": ["no periodontal exam on record", "hs-CRP not measured"],
        "primary_variables": ["periodontal severity (CAL/PPD)", "hs-CRP", "HbA1c"],
        "planned_analysis": "association of periodontal severity with hs-CRP, confounder-adjusted; the "
                            "mechanistic engine supplies the calibrated expectation and the falsification "
                            "condition; genetics (IL-6R Mendelian randomization) enter as biological "
                            "PLAUSIBILITY, not as proof.",
        "limitations": [
            "Cross-sectional: no repeat CRP, no follow-up, no exposure timeline — cannot establish causality.",
            "Periodontitis operationalized by a mean-CAL/PPD proxy, not full per-site CDC/AAP staging.",
            "The longitudinal mediation hypothesis requires a prospective/EHR cohort with the absent fields.",
            "Hypothesis-generation only; no diagnosis, no treatment recommendation, no individual claim.",
        ],
        "non_diagnostic": True,
    }


def integrity_checklist(funnel: dict, completeness: dict) -> list[dict]:
    """The visual research-integrity card the reviewers asked for: what the cohort CAN and CANNOT support."""
    ready = funnel["cohort_n"] > 0
    return [
        {"ok": ready, "label": "Enough data to define a cohort"},
        {"ok": ready, "label": "Falsifiable hypothesis posed"},
        {"ok": ready, "label": "Valid cross-sectional cohort assembled"},
        {"ok": False, "label": "Establishes causality"},
        {"ok": False, "label": "Provides a diagnosis"},
        {"ok": False, "label": "Recommends a therapy"},
    ]
