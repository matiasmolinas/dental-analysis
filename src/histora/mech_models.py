"""Oral-systemic mechanistic models — the centerpiece (Harness 1, Phase 1).

Instantiates the clean, calibratable pipeline from docs/model-library.md §1/§7:

    periodontal source ──► IL-6 ──► hepatic CRP (turnover) ──┬──► CV axis (atherosclerosis coupling)
    (structural, E2.4)     (E2.3)   (E2.5, t½≈19h)           └──► NEURO axis (tau-spread α, E2.8)

driven by ONE shared quantity — the excess IL-6 "inflammatory gain" — and calibrated through the
one honestly-uncertain edge, the oral→systemic spillover efficiency ε (mech_calibrate.py fits ε to
the ΔCRP-after-periodontal-therapy anchor). CV/neuro couplings are the flagged scaffolds: monotone,
directionally-grounded, swept not asserted. Mendelian-randomization favors IL-6/IL-1β as causal and
CRP as observable, so the axes are driven by IL-6, with CRP reported as the measurable readout.

NON-DIAGNOSTIC: the source term is built from STRUCTURAL bands (BOP band, perio stage, comorbidity
flags) — never a numeric patient value — and every output is a population/parameter-level prediction
or a swept range, never a diagnosis. Parameter values are phenomenological, anchored to literature
ranges (cited inline); they set dynamical regimes, and ε is what calibration pins.
"""

from __future__ import annotations

import math
from typing import Any

from .mech_ode import steady_state, stability_report

# --------------------------------------------------------------------------- anchors (cited)
LN2 = math.log(2)
# CRP plasma half-life ≈ 19 h, constant in health & disease (Pepys & Hirschfield 2003, JCI 111:1805)
K_DEG_CRP = LN2 / 19.0          # /h  (E2.5)
# IL-6 half-life ~2 h (short); sets the IL-6 clearance rate
MU_IL6 = LN2 / 2.0              # /h  (E2.3)
# hs-CRP: basal ~1 mg/L; ≥3 mg/L = high CV risk (Pepys 2003; clinical hs-CRP strata)
CRP_BASAL = 1.0                 # mg/L
CRP_CV_RISK = 3.0              # mg/L
# IL-6 basal ~2 pg/mL (circulating, healthy)
IL6_BASAL = 2.0                # pg/mL


def default_params() -> dict:
    """Phenomenological params anchored to library ranges. ε is nominal until calibrated."""
    p = {
        # IL-6 → CRP turnover (E2.5): dCRP/dt = k_syn·IL6/(EC50+IL6) − k_deg·CRP
        "k_deg_crp": K_DEG_CRP,
        "EC50_il6": 6.0,               # pg/mL, half-max hepatic CRP drive
        # k_syn set so saturating CRP_max = k_syn/k_deg ≈ 10 mg/L (upper hs-CRP)
        "crp_max": 10.0,               # mg/L
        # IL-6 dynamics (E2.3): dIL6/dt = base_prod + source − mu_il6·IL6
        "mu_il6": MU_IL6,
        # basal production set so IL6_ss(source=0) = IL6_BASAL
        "base_prod_il6": IL6_BASAL * MU_IL6,   # pg/mL/h
        # oral→systemic spillover efficiency (THE calibrated edge, E2.5 ε); nominal
        "epsilon": 1.0,                # (pg/mL/h) per unit structural load
        # comorbidity amplifier of the inflammatory gain (E3.2 AGE-RAGE): diabetes genuinely
        # worsens periodontal inflammation, so it multiplies the load.
        "diabetes_amp": 1.4,
        # smoking SUPPRESSES bleeding-on-probing, so BOP UNDER-READS true severity in smokers
        # (a measurement bias, not a risk multiplier). Model it as an additive band-suppression
        # correction that restores the under-counted load — the physiologically correct sign.
        "smoking_bop_correction": 0.25,
        # CV coupling scaffold (E2.6): recruitment multiplier = 1 + gamma_cv·gain  [FLAGGED]
        "gamma_cv": 0.05,              # per pg/mL excess IL-6
        # NEURO coupling scaffold (E2.8): tau-spread α → α·(1 + beta_neuro·gain)  [FLAGGED]
        "beta_neuro": 0.03,            # per pg/mL excess IL-6
        "alpha_tau": 0.019,            # /yr baseline tau growth (Schäfer 2021, amyloid-pos)
    }
    p["k_syn_crp"] = p["crp_max"] * p["k_deg_crp"]      # mg/L/h
    return p


# --------------------------------------------------------------------------- structural source (E2.4)
_BOP_LOAD = {"high": 1.0, "moderate": 0.5, "low": 0.15}


def structural_load(features: dict) -> float:
    """Map STRUCTURAL periodontal features → a dimensionless local inflammatory load. Bands and
    flags only (non-diagnostic); comorbidities amplify the gain (E3.2). No patient values."""
    p = default_params()
    load = _BOP_LOAD.get(features.get("bop_band", "low"), 0.15)
    stage = (features.get("perio_stage", "") or "").lower()
    if "stage iv" in stage or "stage iii" in stage:
        load += 0.3
    comorb = set(features.get("comorbidities", []))
    if "smoking" in comorb:
        # BOP-suppression correction FIRST (the observed band under-reads before any amplifier acts).
        load += p["smoking_bop_correction"]
    if "diabetes" in comorb:
        load *= p["diabetes_amp"]
    return load


def periodontal_source(features: dict, p: dict) -> float:
    """Oral→systemic IL-6 source term = ε · structural_load (pg/mL/h). ε is the calibrated edge."""
    return p["epsilon"] * structural_load(features)


# --------------------------------------------------------------------------- IL-6 → CRP (E2.3/E2.5)
def il6_crp_rhs(t: float, y, p: dict) -> tuple:
    """y = (IL6 [pg/mL], CRP [mg/L]). source is carried in p['_source']."""
    il6, crp = y
    source = p.get("_source", 0.0)
    d_il6 = p["base_prod_il6"] + source - p["mu_il6"] * il6
    d_crp = p["k_syn_crp"] * il6 / (p["EC50_il6"] + il6) - p["k_deg_crp"] * crp
    return (d_il6, d_crp)


def il6_steady(source: float, p: dict) -> float:
    """Closed-form IL-6 steady state: (base_prod + source)/mu_il6."""
    return (p["base_prod_il6"] + source) / p["mu_il6"]


def crp_steady(il6: float, p: dict) -> float:
    """Closed-form CRP steady state: (k_syn/k_deg)·IL6/(EC50+IL6)."""
    return (p["k_syn_crp"] / p["k_deg_crp"]) * il6 / (p["EC50_il6"] + il6)


def inflammatory_gain(il6: float) -> float:
    """The shared quantity feeding every downstream axis: excess IL-6 over basal (pg/mL)."""
    return max(0.0, il6 - IL6_BASAL)


# --------------------------------------------------------------------------- axis couplings (scaffolds)
def cv_axis(il6: float, p: dict) -> dict:
    """CV coupling (E2.6, FLAGGED scaffold): chronic IL-6 raises monocyte recruitment → a relative
    atherogenic index. Monotone in the shared gain; a hypothesis, not a fitted human model."""
    gain = inflammatory_gain(il6)
    return {"recruitment_multiplier": round(1.0 + p["gamma_cv"] * gain, 4),
            "confidence": "scaffold", "basis": "E2.6 systemic-inflammation→atherosclerosis ODE"}


def neuro_axis(il6: float, p: dict) -> dict:
    """NEURO coupling (E2.8, FLAGGED scaffold): inflammation raises tau-spread growth α→α(1+β·gain).
    The tau-spread math is validated (Fisher–KPP on the connectome); the inflammation→α edge is
    the hypothesis this agent generates, not fitted here."""
    gain = inflammatory_gain(il6)
    alpha_eff = p["alpha_tau"] * (1.0 + p["beta_neuro"] * gain)
    return {"tau_alpha_baseline": p["alpha_tau"], "tau_alpha_effective": round(alpha_eff, 5),
            "relative_increase": round(alpha_eff / p["alpha_tau"] - 1.0, 4),
            "confidence": "scaffold", "basis": "E2.8 Fisher–KPP tau spread; inflammation→α edge"}


# --------------------------------------------------------------------------- the centerpiece
def centerpiece(features: dict, p: dict | None = None, verify_dynamics: bool = True) -> dict[str, Any]:
    """Wire the pipeline end to end for a structural case, plus the counterfactual IL-6-neutralization
    lever (E2.10). Returns the steady IL-6/CRP, both axis readouts, the shared gain, the therapy and
    IL-6-blockade counterfactuals, and (optionally) a numerical stability check of the ODE core."""
    p = dict(p or default_params())
    source = periodontal_source(features, p)

    il6_ss = il6_steady(source, p)
    crp_ss = crp_steady(il6_ss, p)

    # counterfactuals from the SAME state:
    #  therapy  = remove the periodontal source (source→0)  [ΔCRP is the calibration anchor]
    #  il6_block= neutralize IL-6 signaling → CRP relaxes to its IL6_BASAL floor (E2.10 lever)
    il6_therapy = il6_steady(0.0, p)
    crp_therapy = crp_steady(il6_therapy, p)
    crp_block = crp_steady(IL6_BASAL, p)

    out = {
        "features": features,
        "source_il6_pg_ml_h": round(source, 4),
        "steady_state": {"il6_pg_ml": round(il6_ss, 4), "crp_mg_l": round(crp_ss, 4),
                         "crp_above_cv_risk_threshold": crp_ss >= CRP_CV_RISK},
        "inflammatory_gain_pg_ml": round(inflammatory_gain(il6_ss), 4),
        "cv_axis": cv_axis(il6_ss, p),
        "neuro_axis": neuro_axis(il6_ss, p),
        "counterfactuals": {
            "periodontal_therapy": {"crp_mg_l": round(crp_therapy, 4),
                                    "delta_crp_mg_l": round(crp_ss - crp_therapy, 4),
                                    "note": "source→0; ΔCRP is the calibration anchor (~0.5 mg/L)"},
            "il6_blockade": {"crp_mg_l": round(crp_block, 4),
                             "delta_crp_mg_l": round(crp_ss - crp_block, 4),
                             "note": "E2.10 lever: neutralize IL-6 signaling"},
        },
        "epsilon_calibrated": p.get("_epsilon_calibrated", False),
    }
    if verify_dynamics:
        # confirm the closed-form steady state is the dynamical attractor and it is stable
        p_dyn = dict(p, _source=source)
        y_ss = steady_state(il6_crp_rhs, (IL6_BASAL, CRP_BASAL), p_dyn)
        rep = stability_report(il6_crp_rhs, y_ss, p_dyn)
        out["dynamics_check"] = {
            "integrated_steady_state": [round(v, 4) for v in y_ss],
            "matches_closed_form": (abs(y_ss[0] - il6_ss) < 1e-2 and abs(y_ss[1] - crp_ss) < 1e-2),
            "stable": rep["stable"], "max_real_eig": round(rep["max_real_eig"], 5),
        }
    return out
