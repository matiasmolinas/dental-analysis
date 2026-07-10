"""Calibrate the one honestly-uncertain edge: oral→systemic spillover efficiency ε (Phase 1).

The centerpiece has exactly one parameter that carries the epistemic risk of the periodontitis→
systemic edge: ε, the IL-6 spillover efficiency (docs/model-library.md E2.5). Everything else is
anchored to literature ranges. We pin ε by requiring the model to reproduce a real, interventional
anchor: **periodontal therapy lowers systemic CRP by ~0.5 mg/L** (meta-analytic ΔhsCRP after
professional periodontal treatment — Front Immunol 2025 dynamics; classic ~0.5 mg/L reductions).

Calibration = find ε such that the therapy counterfactual (remove the source, source→0) drops
steady-state CRP by the target ΔCRP for a reference structural case. CRP is monotone increasing in
ε, so a bracketed bisection converges. This is the step that turns the model from a demo into a
falsifiable, data-anchored object; ε is then reused across all cases (and can itself be swept to
report a RANGE of predictions, since the anchor has spread).
"""

from __future__ import annotations

from typing import Any

from mech_models import IL6_BASAL, crp_steady, default_params, il6_steady, structural_load


def _delta_crp_for_epsilon(eps: float, load: float, p: dict) -> float:
    """ΔCRP (mg/L) between the source-on steady state and the therapy (source→0) steady state."""
    p = dict(p, epsilon=eps)
    crp_on = crp_steady(il6_steady(eps * load, p), p)
    crp_off = crp_steady(il6_steady(0.0, p), p)
    return crp_on - crp_off


def calibrate_epsilon(reference_features: dict | None = None, target_delta_crp: float = 0.5,
                      p: dict | None = None, lo: float = 0.0, hi: float = 200.0,
                      tol: float = 1e-4, max_iter: int = 100) -> dict[str, Any]:
    """Bisect ε so the reference case's therapy ΔCRP matches target_delta_crp (mg/L). Returns the
    calibrated ε plus diagnostics. Reference defaults to a high-BOP, otherwise-unremarkable case —
    the population for which the ~0.5 mg/L anchor is reported."""
    p = dict(p or default_params())
    features = reference_features or {"bop_band": "high", "perio_stage": "stage III",
                                      "comorbidities": []}
    load = structural_load(features)
    if load <= 0:
        raise ValueError("reference case has zero structural load — cannot calibrate ε")

    d_hi = _delta_crp_for_epsilon(hi, load, p)
    if d_hi < target_delta_crp:
        # target not reachable in bracket → return the ceiling honestly, do not fabricate
        return {"epsilon": round(hi, 6), "reached_target": False, "achieved_delta_crp": round(d_hi, 4),
                "target_delta_crp": target_delta_crp, "reference_features": features,
                "note": "target ΔCRP exceeds model ceiling in bracket; ε capped"}

    a, b = lo, hi
    for _ in range(max_iter):
        mid = 0.5 * (a + b)
        d = _delta_crp_for_epsilon(mid, load, p)
        if abs(d - target_delta_crp) < tol:
            break
        if d < target_delta_crp:
            a = mid
        else:
            b = mid
    eps = 0.5 * (a + b)
    achieved = _delta_crp_for_epsilon(eps, load, p)
    return {
        "epsilon": round(eps, 6),
        "reached_target": True,
        "achieved_delta_crp": round(achieved, 4),
        "target_delta_crp": target_delta_crp,
        "reference_features": features,
        "reference_load": round(load, 4),
        "steady_state_crp_on": round(crp_steady(il6_steady(eps * load, dict(p, epsilon=eps)), p), 4),
        "il6_on": round(il6_steady(eps * load, dict(p, epsilon=eps)), 4),
        "note": ("ε fit to the ~0.5 mg/L ΔhsCRP-after-periodontal-therapy anchor "
                 "(meta-analytic); sweep ε for a range, the anchor has spread"),
    }


def calibrated_params(target_delta_crp: float = 0.5, p: dict | None = None,
                      reference_features: dict | None = None) -> dict:
    """A params dict with ε pinned to the anchor and a flag so downstream reports know it's fit."""
    p = dict(p or default_params())
    cal = calibrate_epsilon(reference_features, target_delta_crp, p)
    p["epsilon"] = cal["epsilon"]
    p["_epsilon_calibrated"] = cal["reached_target"]
    p["_calibration"] = cal
    return p
