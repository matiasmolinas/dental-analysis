"""Multi-cytokine inflammatory core — resolution vs chronicity (Stage-3, Phase A).

The spine (`mech_models`) collapses the whole inflammatory network into ONE scalar (excess IL-6). That
is deliberate and load-bearing for coherence, but it cannot distinguish an *acute, resolving* response
from a *chronic, unresolved* one — the very distinction that separates a transient perturbation from
tissue damage. This module restores that distinction with a small, identifiable protein network, then
hands a single bounded enrichment (a chronicity amplifier) back to the spine so the rest of the pipeline
is untouched and non-diagnostic.

Model (a reduced Reynolds-2006 / Kumar-2004 acute-inflammation ODE; E2.1/E2.2, in the control-system /
bistability framing of Kotas & Medzhitov 2015, E3.4), in NORMALIZED cytokine units (regime, not assay):

    dTNF/dt  = source + k_pos·H(TNF)·D(IL10) − mu_T·TNF   (pro-inflammatory, autocatalytic, IL-10-damped)
    dIL6/dt  = k_S·TNF/(K_T+TNF)             − mu_S·IL6    (IL-6 driven by TNF)
    dIL10/dt = k_A·IL6/(K_S+IL6)            − mu_A·IL10    (IL-10 resolution feedback, induced by IL-6)

with H(TNF)=TNF⁴/(K_h⁴+TNF⁴) the monocyte/macrophage positive feedback and D(IL10)=1/(1+IL10/K_i) the
anti-inflammatory brake. The autocatalysis + delayed IL-10 brake makes the system **bistable** over a
window of `source`: a low (resolving) fixed point and a high (chronic) fixed point coexist, so the same
oral load can leave inflammation resolved or locked-on depending on history — a genuine physiological
mechanism the single scalar cannot express. Severe structural load (high BOP + advanced stage, or any
high case with a comorbidity) tips the basal state into the chronic basin; mild/moderate load resolves.

NON-DIAGNOSTIC: `source` is built from STRUCTURAL bands (via `mech_models.structural_load`); outputs are
population/parameter-level regime descriptors and a bounded amplifier, never a patient value. Pure-python.
"""

from __future__ import annotations

import math
from typing import Any

from .mech_ode import integrate, jacobian, is_stable
from .mech_models import default_params, structural_load

# Basal (healthy) initial condition in the model's normalized units — a low pro-inflammatory state.
_BASAL_IC = (1.0, 1.0, 1.0)
_CHRONIC_IC = (30.0, 30.0, 1.0)     # high TNF/IL-6, low brake — probes the chronic basin
CHRONIC_AMP_MAX = 0.4               # max fractional boost to the structural source when fully chronic


def inflammation_params(p: dict | None = None) -> dict:
    """Reduced-network constants merged onto the base params (setdefault so the ensemble can override).

    Tuned so that with no oral source the only attractor reached from basal is the LOW/resolving fixed
    point; a bistable window opens for small–moderate source (resolution and chronic states coexist);
    and a sufficiently large source tips the basal state into the HIGH/chronic basin — the qualitative
    behaviour Reynolds/Kumar and Kotas–Medzhitov describe.
    """
    p = dict(p or default_params())
    p.setdefault("infl_source_scale", 1.0)   # maps structural load → TNF source (tipping load ≈ 1.25)
    p.setdefault("hill_n", 4)                # sharpness of the TNF positive feedback
    p.setdefault("k_pos", 16.0)              # TNF autocatalytic gain (monocyte recruitment)
    p.setdefault("K_h", 5.0)                 # half-max of the TNF positive feedback
    p.setdefault("mu_T", 0.8)                # TNF clearance
    p.setdefault("k_S", 2.0)                 # TNF → IL-6 drive
    p.setdefault("K_T", 2.0)                 # half-max of the TNF→IL-6 map
    p.setdefault("mu_S", 0.6)                # IL-6 clearance (slower than TNF)
    p.setdefault("k_A", 1.5)                 # IL-6 → IL-10 induction (the resolution feedback)
    p.setdefault("K_S", 3.0)                 # half-max of the IL-6→IL-10 map
    p.setdefault("mu_A", 0.8)                # IL-10 clearance
    p.setdefault("K_i", 4.0)                 # IL-10 inhibition constant on TNF autocatalysis
    return p


def inflammation_rhs(t: float, y, p: dict) -> tuple:
    """y = (TNF, IL6, IL10). `source` (structural load → TNF drive) is carried in p['_infl_source']."""
    tnf, il6, il10 = (max(0.0, v) for v in y)
    source = p.get("_infl_source", 0.0)
    n = p["hill_n"]
    H = tnf ** n / (p["K_h"] ** n + tnf ** n)            # autocatalytic recruitment (positive feedback)
    D = 1.0 / (1.0 + il10 / p["K_i"])                    # IL-10 anti-inflammatory brake
    d_tnf = source + p["k_pos"] * H * D - p["mu_T"] * tnf
    d_il6 = p["k_S"] * tnf / (p["K_T"] + tnf) - p["mu_S"] * il6
    d_il10 = p["k_A"] * il6 / (p["K_S"] + il6) - p["mu_A"] * il10
    return (d_tnf, d_il6, d_il10)


def _source_from_load(load: float, p: dict) -> float:
    return p["infl_source_scale"] * max(0.0, load)


def _settle(ic, source: float, p: dict, t_max: float = 400.0, dt: float = 0.05) -> tuple:
    """Integrate to the attractor reached from initial condition `ic` under a given source."""
    pp = dict(p, _infl_source=source)
    _, ys = integrate(inflammation_rhs, list(ic), 0.0, t_max, dt, pp)
    return ys[-1]


def _stable(fp, source: float, p: dict) -> bool:
    return is_stable(jacobian(inflammation_rhs, fp, dict(p, _infl_source=source)))


def bistability_report(load: float, p: dict | None = None) -> dict[str, Any]:
    """Probe the regime at a structural load: settle from a LOW and a HIGH initial condition. If they
    converge to distinct stable fixed points the system is **bistable** (resolution and chronic states
    coexist); otherwise it is monostable. Returns both fixed points and the verdict."""
    p = inflammation_params(p)
    source = _source_from_load(load, p)
    lo_fp = _settle(_BASAL_IC, source, p)
    hi_fp = _settle(_CHRONIC_IC, source, p)
    sep = math.dist(lo_fp[:2], hi_fp[:2])
    return {
        "load": round(load, 4),
        "source": round(source, 4),
        "low_fixed_point": {"tnf": round(lo_fp[0], 3), "il6": round(lo_fp[1], 3), "il10": round(lo_fp[2], 3)},
        "high_fixed_point": {"tnf": round(hi_fp[0], 3), "il6": round(hi_fp[1], 3), "il10": round(hi_fp[2], 3)},
        "bistable": bool(sep > 1.0),
        "low_stable": _stable(lo_fp, source, p),
        "high_stable": _stable(hi_fp, source, p),
        "separation": round(sep, 3),
        "_low_il6": lo_fp[1], "_high_il6": hi_fp[1],
    }


def resolution_index(state: dict) -> float:
    """IL-10 / IL-6 at a state: high ⇒ the anti-inflammatory brake dominates (resolving); low ⇒
    pro-inflammatory signalling is unopposed (chronic). A dimensionless regime descriptor."""
    return round(state["il10"] / (state["il6"] + 1e-6), 4)


def _basin_refs(p: dict) -> tuple[float, float]:
    """Absolute IL-6 references for the two basins, measured at a FIXED bistable probe source (so both
    basins exist regardless of the case's own load). Used to grade chronicity on one stable scale."""
    probe = 0.6                          # a source inside the bistable window (both basins exist)
    lo = _settle(_BASAL_IC, probe, p)[1]
    hi = _settle(_CHRONIC_IC, probe, p)[1]
    return lo, hi


def chronicity(load: float, p: dict | None = None) -> float:
    """Where the basal state settles relative to the resolving vs chronic basins, in [0, 1]: 0 = fully
    resolved, 1 = fully locked into the chronic basin. The chronicity the single scalar cannot see.
    Graded against FIXED basin references so it is well-defined even when the case's own load is in the
    monostable-chronic regime (both ICs converge, so the case-local gap would be degenerate)."""
    p = inflammation_params(p)
    reached = _settle(_BASAL_IC, _source_from_load(load, p), p)[1]
    lo, hi = _basin_refs(p)
    if hi - lo < 1e-6:
        return 0.0
    return round(min(1.0, max(0.0, (reached - lo) / (hi - lo))), 4)


def chronic_amplifier(features: dict, p: dict | None = None) -> float:
    """A bounded multiplier (1 … 1+CHRONIC_AMP_MAX) the spine applies to its structural source: an
    unresolved (chronic-basin) case sustains a higher *effective* inflammatory load than its acute
    reading suggests. Derived from the network dynamics, not asserted. Resolving cases → ≈1.0."""
    p = inflammation_params(p)
    return round(1.0 + CHRONIC_AMP_MAX * chronicity(structural_load(features), p), 4)


def inflammation_centerpiece(features: dict, p: dict | None = None) -> dict[str, Any]:
    """Structural severity → the multi-cytokine regime: the state reached from basal, whether the system
    is bistable at this load, the resolution index, the chronicity, and the bounded chronic amplifier the
    spine can consume. Counterfactual: therapy (load→0) — does inflammation fall back to the resolving
    basin?"""
    p = inflammation_params(p)
    load = structural_load(features)
    rep = bistability_report(load, p)
    reached_fp = _settle(_BASAL_IC, rep["source"], p)
    reached = {"tnf": round(reached_fp[0], 3), "il6": round(reached_fp[1], 3), "il10": round(reached_fp[2], 3)}
    chron = chronicity(load, p)
    therapy_fp = _settle(_BASAL_IC, 0.0, p)
    res_idx = resolution_index(reached)
    return {
        "features": features,
        "structural_load": round(load, 4),
        "reached_state": reached,
        "resolution_index": res_idx,
        "chronicity": chron,
        "chronic_amplifier": round(1.0 + CHRONIC_AMP_MAX * chron, 4),
        "bistable_at_this_load": rep["bistable"],
        "regime": "chronic" if chron >= 0.5 else "resolving",
        "counterfactual_therapy": {
            "reached_il6": round(therapy_fp[1], 3),
            "resolves": bool(chronicity(0.0, p) < 0.5),
            "note": "remove the oral source (load→0): does inflammation return to the resolving basin?"},
        "confidence": "scaffold",
        "flags": ["reduced Reynolds/Kumar network (E2.1/E2.2); bistability per Kotas–Medzhitov (E3.4)",
                  "TNF/IL-6/IL-10 are NORMALIZED units — read the REGIME, not an absolute assay value",
                  "non-diagnostic; population/parameter-level, never a patient value"],
    }
