"""The neuro axis — neuroinflammation → tau spread (Phase 3, model first).

The second mechanistic model, built on the Phase-1 centerpiece. It reuses the SAME systemic
inflammatory-gain quantity (periodontal source → IL-6, from mech_models) and forks it into the
brain: systemic IL-6 excess, gated by BBB permeability (E1.7/E4.2), drives neuroinflammation
(microglial activation, E2.7), which raises the tau-spread growth rate α (E2.8, Fisher–KPP), giving
faster tau accumulation and earlier threshold crossing. The novel edge HISTORA generates is exactly
this **oral inflammation → tau-α** modulation.

HONEST FLAGS (non-negotiable):
- The tau-spread math (Fisher–KPP on the connectome) is validated against tau-PET; the
  **inflammation→α coupling `beta_tau` is a FLAGGED hypothesis, not fitted** — swept, never asserted.
- The direct causal test of the P. gingivalis→AD hypothesis (atuzaginstat / GAIN trial) FAILED both
  endpoints; this is a live hypothesis, not causation. Non-diagnostic, hypothesis-generating only.
- α_tau has a very wide literature CI (≈0.019 ± 0.27 /yr, amyloid-positive; Schäfer 2021), so absolute
  onset times are illustrative — the deliverable is the DIRECTION and the RELATIVE counterfactual,
  reported as ranges.

Pure-python (mech_ode toolkit); the network sim uses RK4 (any n, no numpy).
"""

from __future__ import annotations

import math
from typing import Any

from .mech_ode import integrate
from .mech_models import (
    IL6_BASAL,
    default_params,
    il6_steady,
    inflammatory_gain,
    periodontal_source,
)

# Braak-order path: entorhinal → hippocampus → neocortex (a minimal connectome for propagation).
BRAAK_REGIONS = ["entorhinal", "hippocampus", "neocortex"]


def neuro_params(p: dict | None = None) -> dict:
    """Neuro constants merged onto the Phase-1 params (which carry ε, IL-6/CRP, etc.). Uses
    setdefault so a caller (e.g. the ensemble sweeping β_tau) can override any constant."""
    p = dict(p or default_params())
    p.setdefault("alpha_tau", 0.019)     # /yr baseline tau growth (Schäfer 2021, amyloid-positive)
    p.setdefault("N_max", 1.0)           # max neuroinflammation (normalized)
    p.setdefault("K_gain", 4.0)          # pg/mL systemic IL-6 excess for half-max neuroinflammation
    p.setdefault("bbb_gain", 0.5)        # BBB-permeability amplification of crossing (E1.7)
    p.setdefault("beta_tau", 0.6)        # inflammation→α coupling — FLAGGED unknown; sweep it
    # Literature κ≈1.30 µm/yr (Fornari 2019 / Schäfer 2021) is a CONTINUOUS spatial coefficient, not
    # a graph-diffusion rate; on the discrete 3-node Braak chain we use an illustrative coupling on
    # α's timescale so the front propagates over decades (large κ would equilibrate in <1 yr).
    p.setdefault("kappa_graph", 0.02)    # /yr, illustrative discrete-graph coupling
    p.setdefault("tau_seed", 0.05)       # initial entorhinal tau fraction
    p.setdefault("tau_threshold", 0.5)   # Braak-like crossing fraction
    p.setdefault("horizon_years", 20.0)
    # --- amyloid arm (Hao & Friedman 2016, E2.7): neuroinflammation → amyloid → tau-α (the A of ATN) ---
    p.setdefault("k_amyloid", 0.8)       # neuroinflammation → amyloid production  [FLAGGED]
    p.setdefault("d_amyloid", 1.0)       # amyloid clearance (glymphatic; lowered by APOE4/age)
    p.setdefault("beta_amyloid", 0.4)    # amyloid → tau-α coupling  [FLAGGED]
    # --- effect modifiers (structural flags/bands, not patient values) ---
    p.setdefault("apoe4_amyloid_mult", 1.6)   # APOE4 raises amyloid production (Huang/Gladstone)
    p.setdefault("apoe4_clear_mult", 0.75)    # APOE4 lowers amyloid clearance
    p.setdefault("apoe4_bbb_mult", 1.3)       # APOE4 raises BBB permeability
    # age band → (amyloid multiplier, baseline tau-α multiplier); age is the dominant AD driver
    p.setdefault("age_amyloid_mult", {"young": 0.6, "mid": 1.0, "old": 1.6})
    p.setdefault("age_alpha_mult", {"young": 0.7, "mid": 1.0, "old": 1.4})
    return p


def _modifiers(features: dict, p: dict) -> dict[str, float]:
    """Read the structural effect-modifier flags (APOE4 carrier, age band) — flags/bands only, never a
    patient value — and return the amyloid-production, amyloid-clearance, BBB and baseline-α multipliers."""
    apoe4 = bool(features.get("apoe4"))
    age_band = (features.get("age_band") or "mid").lower()
    a_mult = p["age_amyloid_mult"].get(age_band, 1.0)
    al_mult = p["age_alpha_mult"].get(age_band, 1.0)
    return {
        "apoe4": apoe4,
        "age_band": age_band,
        "amyloid_production_mult": (p["apoe4_amyloid_mult"] if apoe4 else 1.0) * a_mult,
        "amyloid_clearance_mult": p["apoe4_clear_mult"] if apoe4 else 1.0,
        "bbb_mult": p["apoe4_bbb_mult"] if apoe4 else 1.0,
        "alpha_baseline_mult": al_mult,
    }


def amyloid_burden(N: float, mods: dict, p: dict) -> float:
    """Steady amyloid burden from neuroinflammation N: A = k·N·(production mods)/(d·clearance mods).
    APOE4 and age raise production and lower clearance — the A of the ATN framework."""
    prod = p["k_amyloid"] * max(0.0, N) * mods["amyloid_production_mult"]
    clear = p["d_amyloid"] * mods["amyloid_clearance_mult"]
    return prod / clear if clear > 0 else 0.0


def tau_alpha_with_amyloid(N: float, A: float, mods: dict, p: dict) -> float:
    """Tau-spread growth rate driven by BOTH inflammation and amyloid, on an age-scaled baseline:
    α_eff = α·age·(1 + β_tau·N + β_amyloid·A). The neuro axis is now A/T, not tau-only. FLAGGED edges."""
    return (p["alpha_tau"] * mods["alpha_baseline_mult"]
            * (1.0 + p["beta_tau"] * max(0.0, N) + p["beta_amyloid"] * max(0.0, A)))


def neuroinflammation(systemic_gain: float, p: dict, bbb_mult: float = 1.0) -> float:
    """Systemic IL-6 excess → neuroinflammation, gated by BBB permeability. Saturating in [0, N_max);
    BBB permeability itself rises with inflammation (E1.7), so the map is mildly super-linear then
    saturates. `bbb_mult` lets an effect modifier (APOE4, age) further open the barrier."""
    g = max(0.0, systemic_gain)
    bbb = 1.0 + bbb_mult * p["bbb_gain"] * g / (p["K_gain"] + g)   # permeability rises with inflammation
    x = bbb * g
    return p["N_max"] * x / (p["K_gain"] + x)


def tau_alpha_effective(N: float, p: dict) -> float:
    """Inflammation raises the tau-spread growth rate: α_eff = α·(1 + beta_tau·N). FLAGGED edge."""
    return p["alpha_tau"] * (1.0 + p["beta_tau"] * N)


def tau_burden_at(alpha_eff: float, t: float, c0: float) -> float:
    """Single-region logistic Fisher–KPP: c(t) = c0/(c0 + (1−c0)e^{−α t})."""
    return c0 / (c0 + (1.0 - c0) * math.exp(-alpha_eff * t))


def tau_onset_time(alpha_eff: float, theta: float, c0: float) -> float | None:
    """Closed-form time for logistic tau to cross threshold θ. None if unreachable."""
    if alpha_eff <= 0 or not (0.0 < c0 < theta < 1.0):
        return None
    return (1.0 / alpha_eff) * math.log((theta / (1.0 - theta)) * ((1.0 - c0) / c0))


# ------------------------------------------------------------------- network propagation (E2.8)
def _path_laplacian(n: int, w: float = 1.0) -> list[list[float]]:
    """Weighted path-graph Laplacian for a length-n Braak chain."""
    L = [[0.0] * n for _ in range(n)]
    for i in range(n - 1):
        L[i][i] += w
        L[i + 1][i + 1] += w
        L[i][i + 1] -= w
        L[i + 1][i] -= w
    return L


def tau_network_rhs(t: float, y, p: dict) -> tuple:
    """Fisher–KPP on the connectome: dc_i/dt = −κ Σ_j L_ij c_j + α_eff c_i(1−c_i)."""
    L, k, a, n = p["_L"], p["kappa_graph"], p["_alpha_eff"], len(y)
    return tuple(-k * sum(L[i][j] * y[j] for j in range(n)) + a * y[i] * (1.0 - y[i])
                 for i in range(n))


def tau_front_arrival(alpha_eff: float, p: dict, t_max: float = 800.0, dt: float = 0.5) -> dict:
    """Simulate the Braak-chain front; return per-region time to cross the threshold (or None)."""
    n = len(BRAAK_REGIONS)
    pp = dict(p, _L=_path_laplacian(n), _alpha_eff=alpha_eff)
    y0 = [p["tau_seed"]] + [0.0] * (n - 1)
    ts, ys = integrate(tau_network_rhs, y0, 0.0, t_max, dt, pp)
    theta = p["tau_threshold"]
    arrival = {}
    for i, region in enumerate(BRAAK_REGIONS):
        t_cross = next((ts[k] for k in range(len(ts)) if ys[k][i] >= theta), None)
        arrival[region] = round(t_cross, 1) if t_cross is not None else None
    return arrival


# ------------------------------------------------------------------- the neuro centerpiece
def neuro_centerpiece(features: dict, p: dict | None = None, front: bool = True) -> dict[str, Any]:
    """Chain oral structural severity → systemic IL-6 gain → neuroinflammation → tau-α → tau burden
    and onset, with the periodontal-therapy counterfactual, a beta_tau sweep (the flagged coupling
    as a swept unknown → a RANGE), and the connectome front-arrival order. `front=False` skips the
    (expensive) Braak-chain front simulation — used by the ensemble, which needs only the scalars."""
    p = neuro_params(p)
    H, c0, theta = p["horizon_years"], p["tau_seed"], p["tau_threshold"]

    mods = _modifiers(features, p)
    il6 = il6_steady(periodontal_source(features, p), p)
    gain = inflammatory_gain(il6)
    N = neuroinflammation(gain, p, bbb_mult=mods["bbb_mult"])
    amyloid = amyloid_burden(N, mods, p)                       # the A of ATN (Hao & Friedman)
    amyloid_base = amyloid_burden(0.0, mods, p)                # no oral inflammation
    alpha_eff = tau_alpha_with_amyloid(N, amyloid, mods, p)    # tau-α driven by inflammation AND amyloid
    alpha_base = tau_alpha_with_amyloid(0.0, amyloid_base, mods, p)  # age-scaled baseline, no oral source

    burden = tau_burden_at(alpha_eff, H, c0)
    burden_base = tau_burden_at(alpha_base, H, c0)
    onset = tau_onset_time(alpha_eff, theta, c0)
    onset_base = tau_onset_time(alpha_base, theta, c0)

    # counterfactual: periodontal therapy removes the oral source → gain→0 → N→0 → α→α_base
    onset_delay = (onset_base - onset) if (onset and onset_base) else None

    # sweep the FLAGGED coupling beta_tau → a range of tau burden at the horizon
    sweep = []
    for b in (0.3, 0.6, 1.0, 1.5):
        ae = p["alpha_tau"] * (1.0 + b * N)
        sweep.append({"beta_tau": b, "alpha_eff": round(ae, 4),
                      "tau_burden_horizon": round(tau_burden_at(ae, H, c0), 4)})
    burden_range = [round(min(s["tau_burden_horizon"] for s in sweep), 4),
                    round(max(s["tau_burden_horizon"] for s in sweep), 4)]

    return {
        "features": features,
        "systemic_gain_pg_ml": round(gain, 4),
        "neuroinflammation": round(N, 4),
        "modifiers": {"apoe4": mods["apoe4"], "age_band": mods["age_band"],
                      "bbb_mult": round(mods["bbb_mult"], 3)},
        "amyloid_burden": {"with_oral_inflammation": round(amyloid, 4),
                           "baseline": round(amyloid_base, 4),
                           "relative_increase": round(amyloid / amyloid_base - 1.0, 4) if amyloid_base else round(amyloid, 4),
                           "note": "the A of ATN (Hao & Friedman E2.7); APOE4/age modify production & clearance"},
        "tau_alpha": {"baseline": round(alpha_base, 5), "effective": round(alpha_eff, 5),
                      "relative_increase": round(alpha_eff / alpha_base - 1.0, 4)},
        "tau_burden_horizon": {"years": H, "with_oral_inflammation": round(burden, 4),
                               "baseline": round(burden_base, 4),
                               "relative_increase": round(burden / burden_base - 1.0, 4)},
        "tau_onset_years": {"with_oral_inflammation": round(onset, 1) if onset else None,
                            "baseline": round(onset_base, 1) if onset_base else None,
                            "therapy_delay_years": round(onset_delay, 1) if onset_delay else None,
                            "note": "absolute years illustrative (α_tau CI ±0.27); read the delta"},
        "beta_tau_sweep": sweep,
        "tau_burden_range_over_beta": burden_range,
        "connectome_front_arrival_years": (tau_front_arrival(alpha_eff, p) if front else None),
        "confidence": "scaffold",
        "flags": ["inflammation→α and amyloid→α are FLAGGED hypotheses (not fitted)",
                  "amyloid arm (Hao & Friedman E2.7); APOE4/age are structural effect-modifier flags/bands",
                  "atuzaginstat/GAIN trial failed → live hypothesis, not causation",
                  "non-diagnostic; hypothesis generation only"],
    }
