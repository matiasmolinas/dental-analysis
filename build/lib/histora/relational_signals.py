"""Deterministic, non-diagnostic oral-systemic relational signals.

The harness's deterministic layer. It turns a normalized record into **structural signal flags**, an
explicit **missing-mediator** collection list, and a **structural case signature** — computed in code
(not left to the model) so the guardrail-critical facts are guaranteed. `required_missing_data_entries`
is the project's one clean engineering win (W1): flagging every truly-absent mediating datum
deterministically, which a free-form model does not do reliably.

Hard rules (mirror the guardrail):
  * Non-diagnostic. Structural categorizations of *present* data, not diagnoses or risk scores.
  * No imputation. A missing datum becomes a collection flag, never a computed patient value.
  * Pure and dependency-light: loads without a GPU or a scientific stack.
"""

from __future__ import annotations

from typing import Any

# Required mediating data whose absence must surface as a collection flag. Keys are
# read from record["medical_cv"] / record["periodontal"]; None or missing => flagged.
REQUIRED_MEDIATORS = {
    "hs_crp": "systemic inflammatory burden marker (links periodontal inflammation to CV risk)",
    "il6": "pro-inflammatory cytokine mediator",
}


def _band(value: float, moderate: float, high: float) -> str:
    """Three-way structural band. Deterministic; not a clinical grade."""
    if value >= high:
        return "high"
    if value >= moderate:
        return "moderate"
    return "low"


def inflammatory_load(perio: dict) -> dict[str, Any] | None:
    """Structural inflammatory-burden band from bleeding-on-probing percentage.
    BOP% is an observed marker of gingival inflammation, not a diagnosis."""
    bop = perio.get("bop_pct")
    if bop is None:
        return None
    return {
        "signal": "bop_inflammatory_load",
        "band": _band(bop, moderate=10.0, high=30.0),
        "from": ["periodontal.bop_pct"],
        "value": bop,
    }


def metabolic_load(shared: dict) -> dict[str, Any] | None:
    """Structural metabolic-load band from HbA1c (present data only)."""
    hba1c = shared.get("hba1c")
    if hba1c is None:
        return None
    return {
        "signal": "metabolic_load",
        "band": _band(hba1c, moderate=5.7, high=6.5),
        "from": ["shared_risk.hba1c"],
        "value": hba1c,
    }


def perio_progression(perio: dict) -> dict[str, Any] | None:
    """Deterministic probing-depth delta over time, if a prior value is on record.
    A positive delta is worsening; reported as a structural change, not a prognosis."""
    now = perio.get("mean_ppd_mm")
    prior = perio.get("ppd_18m_ago_mm")
    if now is None or prior is None:
        return None
    delta = round(now - prior, 2)
    return {
        "signal": "ppd_progression_mm",
        "direction": "worsening" if delta > 0 else ("improving" if delta < 0 else "stable"),
        "delta_mm": delta,
        "from": ["periodontal.mean_ppd_mm", "periodontal.ppd_18m_ago_mm"],
    }


def missing_mediators(record: dict) -> list[dict[str, str]]:
    """Explicit collection flags for absent mediating data. Never imputes a value."""
    sources = {**record.get("medical_cv", {}), **record.get("periodontal", {})}
    flags = []
    for field, why in REQUIRED_MEDIATORS.items():
        if sources.get(field) is None:
            flags.append({"field": field, "why": why, "status": "MISSING"})
    return flags


# Absent mediators whose collection is guardrail-critical (they carry the
# periodontal-inflammation -> cardiovascular bridge, e.g. hs-CRP). Everything else
# missing is "important". Deterministic; not a clinical severity claim.
CRITICAL_MISSING = {"hs_crp"}


def required_missing_data_entries(record: dict) -> list[dict[str, str]]:
    """Schema-ready `required_missing_data` items for absent mediating data.

    Turns `missing_mediators(record)` into entries conforming to
    `schemas/output_schema.json`'s `required_missing_data` items —
    `{"field", "why", "impact"}` — so the HARNESS, not the model, guarantees the
    guardrail-critical collection flags. `impact` is "critical" for inflammatory
    markers that carry the oral->systemic bridge (hs-CRP), "important" otherwise.
    Never imputes a value: this is a collection flag, not a computed patient value.
    """
    entries = []
    for flag in missing_mediators(record):
        field = flag["field"]
        entries.append({
            "field": field,
            "why": flag["why"],
            "impact": "critical" if field in CRITICAL_MISSING else "important",
        })
    return entries


def case_signature(record: dict) -> dict:
    """A STRUCTURAL signature of a case — perio stage, a BOP band, a comorbidity set, and which
    mediating data are flagged absent. Bands/booleans/field-names only, NEVER a numeric patient value
    (guardrail). Used to derive the mechanistic models' structural inputs from a full record."""
    perio = record.get("periodontal", {})
    shared = record.get("shared_risk", {})
    med = record.get("medical_cv", {})
    bop = perio.get("bop_pct")
    stage = perio.get("diagnosis", "")
    comorbid = sorted(k for k, v in {
        "diabetes": shared.get("type2_diabetes"), "smoking": shared.get("smoking_active"),
        "hypertension": shared.get("hypertension")}.items() if v)
    absent = sorted(f for f in ("hs_crp", "il6") if med.get(f) is None and f not in perio)
    return {
        "perio_stage": stage.split(",")[0].strip() if stage else "unknown",
        "bop_band": ("high" if (bop or 0) >= 30 else "moderate" if (bop or 0) >= 10 else "low"),
        "comorbidities": comorbid,      # names only
        "absent_mediators": absent,     # field names only
    }


def derived_signals(record: dict) -> dict[str, Any]:
    """The injectable variable bundle: deterministic structural signals + the
    missing-mediator collection flags. This is the injectable variable bundle for the
    prompt package and then re-checks in the next readout."""
    perio = record.get("periodontal", {})
    shared = record.get("shared_risk", {})
    signals = [s for s in (inflammatory_load(perio), metabolic_load(shared),
                           perio_progression(perio)) if s is not None]
    return {
        "structural_signals": signals,
        "missing_mediators": missing_mediators(record),
        "non_diagnostic": True,
    }
