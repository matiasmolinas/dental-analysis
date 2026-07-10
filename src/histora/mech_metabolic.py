"""The metabolic axis — inflammation → insulin resistance → HbA1c (Objective A3, the C4 coupling).

The third axis the shared inflammatory `gain` forks into. Mechanistic justification (Bergman minimal
model, E3.1): insulin sensitivity S_I is degraded by systemic inflammation — IL-6 inhibits IRS-1
signaling (Pritchard-Bell/Parker, C4), so `S_I(gain) = S_I0/(1 + β_si·gain)`. HISTORA uses the reduced,
population-level relative index (as for the CV axis): a monotone insulin-resistance index in `gain`,
and a predicted HbA1c shift attributable to the oral inflammatory source. Non-diagnostic, FLAGGED
scaffold — swept as a range, never asserted.

The one calibration: `k_hba1c` is pinned so the periodontal-therapy counterfactual (remove the oral
source → gain→0) reproduces the real **~0.35 pp HbA1c drop after periodontal therapy** (meta-analytic).
The data anchor is a perio→HbA1c association on in-cycle NHANES 2009-2010 (`run_perio_diabetes.py`).
"""

from __future__ import annotations

from typing import Any

from .mech_calibrate import calibrated_params
from .mech_models import (
    default_params,
    il6_steady,
    inflammatory_gain,
    periodontal_source,
)

# Meta-analytic anchor: periodontal therapy lowers HbA1c ~0.3–0.4 percentage points.
HBA1C_DROP_ANCHOR_PP = 0.35


def metabolic_params(p: dict | None = None) -> dict:
    """Metabolic constants merged onto the base params (setdefault so the ensemble can override)."""
    p = dict(p or default_params())
    p.setdefault("beta_si", 0.15)     # gain → insulin-resistance coupling (per pg/mL) — FLAGGED, swept
    p.setdefault("k_hba1c", 0.35)     # pp HbA1c per pg/mL gain — calibrated (see calibrate_hba1c)
    return p


def insulin_resistance_index(gain: float, p: dict) -> float:
    """Relative insulin-resistance index: 1 at no oral inflammation, rising with gain (S_I ∝ 1/IR)."""
    return 1.0 + p["beta_si"] * max(0.0, gain)


def hba1c_shift_pp(gain: float, p: dict) -> float:
    """Predicted HbA1c shift (percentage points) attributable to the oral inflammatory source."""
    return p["k_hba1c"] * max(0.0, gain)


def _gain_for(features: dict, p: dict) -> float:
    return inflammatory_gain(il6_steady(periodontal_source(features, p), p))


def calibrate_hba1c(reference_features: dict | None = None, target_pp: float = HBA1C_DROP_ANCHOR_PP,
                    p: dict | None = None) -> dict[str, Any]:
    """Pin `k_hba1c` so the reference case's periodontal-therapy counterfactual (gain→0) reproduces the
    ~0.35 pp HbA1c drop. Since the shift is linear in gain, k_hba1c = target_pp / gain_ref (closed form)."""
    p = metabolic_params(p or calibrated_params())
    features = reference_features or {"bop_band": "high", "perio_stage": "stage III", "comorbidities": []}
    gain = _gain_for(features, p)
    if gain <= 0:
        raise ValueError("reference case has zero inflammatory gain — cannot calibrate k_hba1c")
    k = target_pp / gain
    return {"k_hba1c": round(k, 6), "target_pp": target_pp, "reference_gain": round(gain, 4),
            "note": "HbA1c shift is linear in gain; therapy (gain→0) reproduces the ~0.35 pp anchor"}


def calibrated_metabolic_params(target_pp: float = HBA1C_DROP_ANCHOR_PP, p: dict | None = None) -> dict:
    p = metabolic_params(p or calibrated_params())
    p["k_hba1c"] = calibrate_hba1c(p=p, target_pp=target_pp)["k_hba1c"]
    return p


def metabolic_centerpiece(features: dict, p: dict | None = None) -> dict[str, Any]:
    """gain → insulin-resistance index + predicted HbA1c shift, with the periodontal-therapy
    counterfactual (removing the oral source drops HbA1c by the calibrated amount)."""
    p = calibrated_metabolic_params(p=p) if (p is None or "k_hba1c" not in p) else metabolic_params(p)
    gain = _gain_for(features, p)
    return {
        "features": features,
        "inflammatory_gain_pg_ml": round(gain, 4),
        "insulin_resistance_index": round(insulin_resistance_index(gain, p), 4),
        "hba1c_shift_pp": round(hba1c_shift_pp(gain, p), 4),
        "counterfactual_therapy": {
            "hba1c_drop_pp": round(hba1c_shift_pp(gain, p), 4),   # therapy (gain→0) removes this shift
            "note": "predicted HbA1c drop if the oral inflammatory source is removed"},
        "confidence": "scaffold",
        "flags": ["gain→insulin-resistance is a FLAGGED coupling (Bergman/C4 substrate), swept as a range",
                  "non-diagnostic; population/parameter-level, never a patient value"],
    }
