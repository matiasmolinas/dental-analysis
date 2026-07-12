"""Cardiovascular axis as a PROCESS — early-atherosclerosis ODE (Stage-3, Phase B).

The spine's `cv_axis` is a one-line monotone index (`1 + γ·gain`) — directionally right, but not a
process. This module promotes the flagged CV scaffold (Ougrinovskaia et al. 2010, E2.6) to a small
dynamical model of the foam-cell positive-feedback loop that actually drives plaque growth:

    dL/dt = σ·(1 + γ_cv·gain) − k_up·M·L − d_L·L        oxLDL: entry rises with systemic inflammation
    dM/dt = r·(1 + γ_cv·gain) + β_f·F − k_up·M·L − d_M·M monocyte→macrophage recruitment (+foam feedback)
    dF/dt = k_up·M·L − d_F·F                            foam cells: macrophages laden with oxLDL

The engine of atherogenesis is the **F→M positive feedback** (foam cells release chemokines → recruit
more monocytes → more foam cells; Ougrinovskaia's bifurcation). Systemic inflammation (the shared IL-6
`gain` from `mech_models`) enters exactly where the biology says — raising oxLDL entry and monocyte
recruitment — so the SAME lever that drives CRP/neuro/metabolic drives plaque here. The reported plaque
burden is the foam-cell load at a fixed horizon; the deliverable is its RELATIVE increase attributable
to the oral inflammatory source (with the periodontal-therapy counterfactual, gain→0).

FLAGGED scaffold: the couplings are biology-plausible but imposed; swept as a range, never asserted.
NON-DIAGNOSTIC: structural-band input, parameter-level relative outputs, never a patient value. MR frames
it honestly (CRP marker, IL-6/IL-1 causal). Pure-python (mech_ode).
"""

from __future__ import annotations

from typing import Any

from .mech_ode import integrate, steady_state
from .mech_models import (
    default_params,
    il6_steady,
    inflammatory_gain,
    periodontal_source,
)


def cv_params(p: dict | None = None) -> dict:
    """Atherosclerosis-ODE constants merged onto the base params (setdefault → ensemble can override)."""
    p = dict(p or default_params())
    p.setdefault("cv_sigma", 1.0)        # baseline oxLDL entry
    p.setdefault("cv_gamma", 0.05)       # inflammation → (oxLDL entry, recruitment) coupling  [FLAGGED]
    p.setdefault("cv_recruit", 0.5)      # baseline monocyte→macrophage recruitment
    p.setdefault("cv_k_up", 0.20)        # oxLDL uptake by macrophages → foam cells
    p.setdefault("cv_beta_f", 0.15)      # foam-cell → recruitment POSITIVE FEEDBACK (the engine)
    p.setdefault("cv_d_L", 0.30)         # oxLDL clearance
    p.setdefault("cv_d_M", 0.25)         # macrophage egress/death
    p.setdefault("cv_d_F", 0.02)         # foam-cell turnover (slow → plaque accumulates)
    p.setdefault("cv_horizon", 60.0)     # arbitrary-unit horizon for the reported plaque burden
    return p


def atherosclerosis_rhs(t: float, y, p: dict) -> tuple:
    """y = (oxLDL L, macrophages M, foam cells F). Shared inflammatory gain carried in p['_gain']."""
    L, M, F = (max(0.0, v) for v in y)
    infl = 1.0 + p["cv_gamma"] * p.get("_gain", 0.0)
    uptake = p["cv_k_up"] * M * L
    d_L = p["cv_sigma"] * infl - uptake - p["cv_d_L"] * L
    d_M = p["cv_recruit"] * infl + p["cv_beta_f"] * F - uptake - p["cv_d_M"] * M
    d_F = uptake - p["cv_d_F"] * F
    return (d_L, d_M, d_F)


def _plaque_at_horizon(gain: float, p: dict) -> float:
    """Integrate the atherosclerosis ODE to the horizon and return the foam-cell (plaque) burden."""
    pp = dict(p, _gain=gain)
    ts, ys = integrate(atherosclerosis_rhs, (1.0, 1.0, 0.0), 0.0, p["cv_horizon"], 0.1, pp)
    return ys[-1][2]


def plaque_trajectory(gain: float, p: dict | None = None, dt: float = 0.5) -> dict[str, list]:
    """The oxLDL / macrophage / foam-cell time courses — the data behind the plaque-growth figure."""
    p = cv_params(p)
    pp = dict(p, _gain=gain)
    ts, ys = integrate(atherosclerosis_rhs, (1.0, 1.0, 0.0), 0.0, p["cv_horizon"], dt, pp)
    return {"t": ts, "oxldl": [y[0] for y in ys], "macrophage": [y[1] for y in ys],
            "foam": [y[2] for y in ys]}


def cv_plaque_centerpiece(features: dict, p: dict | None = None) -> dict[str, Any]:
    """Chain oral structural severity → systemic IL-6 gain → the atherosclerosis ODE → a plaque burden
    at the horizon, its relative increase over the no-oral-inflammation baseline, and the
    periodontal-therapy counterfactual (gain→0). A γ_cv sweep gives the honest RANGE."""
    p = cv_params(p)
    gain = inflammatory_gain(il6_steady(periodontal_source(features, p), p))

    plaque = _plaque_at_horizon(gain, p)
    plaque_base = _plaque_at_horizon(0.0, p)                 # no oral inflammation (therapy limit)
    rel = plaque / plaque_base - 1.0 if plaque_base else 0.0

    sweep = []
    for g_cv in (0.025, 0.05, 0.10):
        pp = dict(p, cv_gamma=g_cv)
        sweep.append({"gamma_cv": g_cv,
                      "plaque_rel_increase": round(_plaque_at_horizon(gain, pp) / plaque_base - 1.0, 4)})
    rng = [round(min(s["plaque_rel_increase"] for s in sweep), 4),
           round(max(s["plaque_rel_increase"] for s in sweep), 4)]

    return {
        "features": features,
        "inflammatory_gain_pg_ml": round(gain, 4),
        "plaque_burden_horizon": {"years": p["cv_horizon"], "with_oral_inflammation": round(plaque, 4),
                                  "baseline": round(plaque_base, 4), "relative_increase": round(rel, 4)},
        "counterfactual_therapy": {"plaque_rel_reduction": round(rel, 4),
                                   "note": "remove the oral source (gain→0): plaque relaxes to baseline"},
        "gamma_cv_sweep": sweep,
        "plaque_rel_increase_range_over_gamma": rng,
        "confidence": "scaffold",
        "flags": ["Ougrinovskaia 2010 foam-cell positive feedback (E2.6); couplings FLAGGED, swept",
                  "MR: CRP is a marker, IL-6/IL-1 causal — read the direction, not a risk score",
                  "non-diagnostic; population/parameter-level, never a patient value"],
    }
