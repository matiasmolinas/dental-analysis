"""Metabolic axis as a PROCESS — the Bergman glucose–insulin minimal model (Stage-3, Phase B).

`mech_metabolic` reports the metabolic axis as a static linear shift `k·gain`. This module promotes the
staged substrate (Bergman 1979, E3.1) to the actual glucose–insulin dynamics, so inflammation acts where
the biology says — degrading insulin sensitivity S_I (IL-6 → IRS-1 serine phosphorylation;
Pritchard-Bell/Parker 2013) — and the metabolic burden emerges from a simulated meal response rather than
an asserted slope.

Extended minimal model (glucose G, remote insulin action X, plasma insulin I), with a decaying meal
appearance Ra(t) and a first-phase pancreatic response:

    dG/dt = −(p1 + X)·G + p1·Gb + Ra(t)
    dX/dt = −p2·X + p3_eff·(I − Ib),   p3_eff = p3 / (1 + β_si·gain)   ← inflammation degrades S_I
    dI/dt =  γ·max(0, G − Gb) − n·(I − Ib)

S_I = p3_eff/p2 falls with the shared inflammatory `gain`, so glucose disposal slows, the post-meal
excursion rises, mean glucose rises, and HbA1c (ADAG: A1c = (mean glucose + 46.7)/28.7) shifts up. The
reported shift is calibrated so the periodontal-therapy counterfactual (gain→0) reproduces the
meta-analytic ~0.35 pp HbA1c drop — the same anchor the linear model uses, now mechanistically grounded.

FLAGGED scaffold (β_si imposed, swept). NON-DIAGNOSTIC: structural-band input, parameter-level relative
outputs, never a patient value. Pure-python (mech_ode).
"""

from __future__ import annotations

import math
from typing import Any

from .mech_ode import integrate
from .mech_models import (
    default_params,
    il6_steady,
    inflammatory_gain,
    periodontal_source,
)

HBA1C_DROP_ANCHOR_PP = 0.35


def glucose_params(p: dict | None = None) -> dict:
    """Bergman-model constants (population-typical, dimensionless-time) merged onto the base params."""
    p = dict(p or default_params())
    p.setdefault("g_p1", 0.03)      # glucose effectiveness (insulin-independent disposal) /min
    p.setdefault("g_p2", 0.025)     # remote-insulin decay /min
    p.setdefault("g_p3", 1.3e-5)    # insulin action rate → S_I = p3/p2
    p.setdefault("g_Gb", 90.0)      # basal glucose mg/dL
    p.setdefault("g_Ib", 10.0)      # basal insulin µU/mL
    p.setdefault("g_gamma", 0.5)    # pancreatic first-phase secretion
    p.setdefault("g_n", 0.15)       # insulin clearance /min
    p.setdefault("g_meal_D", 250.0)  # meal glucose dose
    p.setdefault("g_meal_k", 0.05)  # meal appearance rate
    p.setdefault("beta_si", 0.15)   # inflammation → insulin-resistance coupling  [FLAGGED, swept]
    p.setdefault("g_horizon", 240.0)  # minutes simulated
    p.setdefault("k_hba1c_glu", 1.0)  # calibrated mapping scale (set by calibrate_glucose)
    return p


def _s_i(gain: float, p: dict) -> float:
    """Insulin sensitivity S_I = p3_eff/p2, degraded by inflammation: p3_eff = p3/(1+β_si·gain)."""
    p3_eff = p["g_p3"] / (1.0 + p["beta_si"] * max(0.0, gain))
    return p3_eff / p["g_p2"]


def glucose_rhs(t: float, y, p: dict) -> tuple:
    G, X, I = (max(0.0, v) for v in y)
    Ra = p["g_meal_D"] * p["g_meal_k"] * math.exp(-p["g_meal_k"] * t)     # decaying meal appearance
    p3_eff = p["g_p3"] / (1.0 + p["beta_si"] * p.get("_gain", 0.0))
    d_G = -(p["g_p1"] + X) * G + p["g_p1"] * p["g_Gb"] + Ra
    d_X = -p["g_p2"] * X + p3_eff * (I - p["g_Ib"])
    d_I = p["g_gamma"] * max(0.0, G - p["g_Gb"]) - p["g_n"] * (I - p["g_Ib"])
    return (d_G, d_X, d_I)


def glucose_response(gain: float, p: dict | None = None, dt: float = 1.0) -> dict[str, Any]:
    """Simulate the meal response at a given inflammatory gain; return the G/X/I trajectories, the mean
    glucose, and the incremental glucose AUC over basal — the data behind the glucose–insulin figure."""
    p = glucose_params(p)
    pp = dict(p, _gain=max(0.0, gain))
    ts, ys = integrate(glucose_rhs, (p["g_Gb"], 0.0, p["g_Ib"]), 0.0, p["g_horizon"], dt, pp)
    G = [y[0] for y in ys]
    mean_g = sum(G) / len(G)
    auc_inc = sum(max(0.0, g - p["g_Gb"]) for g in G) * dt
    return {"t": ts, "glucose": G, "insulin": [y[2] for y in ys], "remote_x": [y[1] for y in ys],
            "mean_glucose": round(mean_g, 3), "auc_incremental": round(auc_inc, 2),
            "s_i": _s_i(gain, p)}


def _hba1c_from_mean_glucose(mean_g: float) -> float:
    """ADAG estimated A1c from mean glucose (mg/dL): A1c(%) = (mean glucose + 46.7) / 28.7."""
    return (mean_g + 46.7) / 28.7


def calibrate_glucose(reference_features: dict | None = None, target_pp: float = HBA1C_DROP_ANCHOR_PP,
                      p: dict | None = None) -> dict[str, Any]:
    """Pin `k_hba1c_glu` so the reference case's therapy counterfactual (gain→0) reproduces the ~0.35 pp
    HbA1c drop. The raw ADAG shift is scaled linearly, so the factor is closed-form."""
    p = glucose_params(p)
    features = reference_features or {"bop_band": "high", "perio_stage": "stage III", "comorbidities": []}
    gain = inflammatory_gain(il6_steady(periodontal_source(features, p), p))
    raw = _hba1c_from_mean_glucose(glucose_response(gain, p)["mean_glucose"]) \
        - _hba1c_from_mean_glucose(glucose_response(0.0, p)["mean_glucose"])
    if raw <= 0:
        raise ValueError("reference case has no positive HbA1c shift — cannot calibrate")
    return {"k_hba1c_glu": round(target_pp / raw, 6), "raw_shift_pp": round(raw, 4),
            "reference_gain": round(gain, 4), "target_pp": target_pp}


def glucose_centerpiece(features: dict, p: dict | None = None) -> dict[str, Any]:
    """Chain oral severity → gain → degraded S_I → meal response → HbA1c shift (calibrated), with the
    β_si sweep (range) and the periodontal-therapy counterfactual."""
    p = glucose_params(p)
    if "k_hba1c_glu" not in (p if isinstance(p, dict) else {}) or p.get("k_hba1c_glu", 1.0) == 1.0:
        p["k_hba1c_glu"] = calibrate_glucose(p=p)["k_hba1c_glu"]
    gain = inflammatory_gain(il6_steady(periodontal_source(features, p), p))

    resp = glucose_response(gain, p)
    resp0 = glucose_response(0.0, p)
    raw_shift = _hba1c_from_mean_glucose(resp["mean_glucose"]) - _hba1c_from_mean_glucose(resp0["mean_glucose"])
    hba1c_shift = p["k_hba1c_glu"] * raw_shift

    sweep = []
    for b in (0.075, 0.15, 0.30):
        pp = dict(p, beta_si=b)
        r = glucose_response(gain, pp)
        s = pp["k_hba1c_glu"] * (_hba1c_from_mean_glucose(r["mean_glucose"])
                                 - _hba1c_from_mean_glucose(resp0["mean_glucose"]))
        sweep.append({"beta_si": b, "hba1c_shift_pp": round(s, 4)})
    rng = [round(min(s["hba1c_shift_pp"] for s in sweep), 4),
           round(max(s["hba1c_shift_pp"] for s in sweep), 4)]

    return {
        "features": features,
        "inflammatory_gain_pg_ml": round(gain, 4),
        "insulin_sensitivity_si": round(resp["s_i"], 8),
        "si_relative_drop": round(1.0 - resp["s_i"] / resp0["s_i"], 4),
        "mean_glucose_mg_dl": resp["mean_glucose"],
        "glucose_auc_incremental": resp["auc_incremental"],
        "hba1c_shift_pp": round(hba1c_shift, 4),
        "counterfactual_therapy": {"hba1c_drop_pp": round(hba1c_shift, 4),
                                   "note": "remove the oral source (gain→0): S_I recovers, HbA1c falls"},
        "beta_si_sweep": sweep,
        "hba1c_shift_range_over_beta": rng,
        "confidence": "scaffold",
        "flags": ["Bergman minimal model (E3.1); IL-6→IRS-1 S_I degradation; β_si FLAGGED, swept",
                  "HbA1c via ADAG mean-glucose mapping; calibrated to the ~0.35 pp therapy anchor",
                  "non-diagnostic; population/parameter-level, never a patient value"],
    }
