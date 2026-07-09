"""Deterministic, non-diagnostic oral-systemic relational signals.

The worked harness-evolution example (see skills/harness-evolution.md). When the
inferred lens shows the model keeps approximating a deterministic relation or dropping
a mediating datum, the Lens Observer moves the fix into code: this module turns a
normalized record into **structural signal flags** and an explicit **missing-mediator**
list, which are then injected back into the prompt as variables the lens re-checks.

Hard rules (mirrors the guardrail):
  * Non-diagnostic. These are structural categorizations of *present* data, not
    diagnoses and not risk scores about the patient.
  * No imputation. A missing datum becomes a collection flag, never a computed value.
  * Pure and dependency-light: loads without a GPU, like all of src/ (Claude only).
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


def derived_signals(record: dict) -> dict[str, Any]:
    """The injectable variable bundle: deterministic structural signals + the
    missing-mediator collection flags. This is what the Observer injects into the
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
