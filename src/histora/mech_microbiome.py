"""Periodontal source realism — a reduced oral-microbiome model (Stage-3, Phase C).

The spine reads the periodontal source from structural bands and collapses all microbial detail into
`ε·load`. This module promotes the staged microbiome substrate (generalized Lotka–Volterra, Pasqualini
2026 E3.5; two-species biofilm, Martin 2017 E3.6; Allee/quorum keystone threshold E3.7) to a small
model that produces a **dysbiosis index** — how far the community has shifted from a commensal-dominated
to a pathogen-dominated state — which then scales the source magnitude. It names the keystone pathogen
(*Porphyromonas gingivalis*) the abstraction otherwise hides.

Two-species competitive Lotka–Volterra with an Allee/quorum term for the keystone:

    dP/dt = r_P·adv·P·(1 − (P + α_CP·C)/K_P)·(P/A − 1)   P = P. gingivalis (Allee: needs a quorum ≥ A)
    dC/dt = r_C·C·(1 − (C + α_PC·P)/K_C)                  C = S. gordonii (commensal)

The `(P/A − 1)` Allee factor encodes keystone dysbiosis onset: below the quorum threshold A the pathogen
declines (health resists); above it, P. gingivalis expands and suppresses the commensal (Hajishengallis
keystone-pathogen hypothesis). Structural risk (BOP band, stage, comorbidities) sets the pathogen seed,
a growth advantage, and a dysbiotic niche (a larger K_P), so severity graduates the community from
commensal, through partial dysbiosis, to pathogen-dominated past the threshold.

FLAGGED / exploratory (identifiability weak per the library). NON-DIAGNOSTIC: structural input, a
population-level dysbiosis index out, never a patient value or a microbial diagnosis. Pure-python.
"""

from __future__ import annotations

from typing import Any

from .mech_ode import integrate
from .mech_models import default_params, structural_load

DYSBIOSIS_SOURCE_MAX = 0.5             # max fractional boost to the source at full dysbiosis


def microbiome_params(p: dict | None = None) -> dict:
    """Reduced-gLV constants merged onto the base params (setdefault → ensemble can override)."""
    p = dict(p or default_params())
    p.setdefault("mb_r_P", 0.8)       # P. gingivalis growth rate
    p.setdefault("mb_r_C", 1.0)       # S. gordonii (commensal) growth rate
    p.setdefault("mb_K_C", 1.0)       # commensal carrying capacity
    p.setdefault("mb_alpha_CP", 0.4)  # commensal→pathogen competition
    p.setdefault("mb_alpha_PC", 1.1)  # pathogen→commensal suppression (keystone: strong)
    p.setdefault("mb_allee_A", 0.10)  # Allee/quorum threshold for P. gingivalis persistence
    p.setdefault("mb_horizon", 80.0)
    return p


def _seed_niche_advantage(load: float, p: dict) -> tuple[float, float, float]:
    """Structural load → (pathogen seed, growth advantage, pathogen carrying capacity K_P). Severe cases
    seed more P. gingivalis above the Allee quorum, give it a competitive edge, and open a dysbiotic
    niche (larger K_P) — so the pathogen fraction grows continuously with severity past the threshold."""
    seed = 0.05 + 0.20 * min(1.0, load)
    advantage = 1.0 + 0.6 * min(1.5, load)
    k_P = 0.6 + 0.5 * min(1.5, load)
    return seed, advantage, k_P


def microbiome_rhs(t: float, y, p: dict) -> tuple:
    """y = (P. gingivalis, S. gordonii). Growth advantage / niche K_P carried in p['_adv']/p['_K_P']."""
    P, C = (max(0.0, v) for v in y)
    adv, k_P = p.get("_adv", 1.0), p.get("_K_P", 1.0)
    allee = (P / p["mb_allee_A"] - 1.0)              # <0 below quorum (pathogen declines), >0 above
    d_P = p["mb_r_P"] * adv * P * (1.0 - (P + p["mb_alpha_CP"] * C) / k_P) * allee
    d_C = p["mb_r_C"] * C * (1.0 - (C + p["mb_alpha_PC"] * P) / p["mb_K_C"])
    return (d_P, d_C)


def dysbiosis_index(features: dict, p: dict | None = None) -> dict[str, Any]:
    """Settle the community for a structural case and report the dysbiosis index = P/(P+C): 0 = fully
    commensal (health), 1 = pathogen-dominated (keystone dysbiosis). Crosses over as severe load pushes
    P. gingivalis past its Allee quorum."""
    p = microbiome_params(p)
    load = structural_load(features)
    seed, adv, k_P = _seed_niche_advantage(load, p)
    pp = dict(p, _adv=adv, _K_P=k_P)
    _, ys = integrate(microbiome_rhs, (seed, 0.9), 0.0, p["mb_horizon"], 0.1, pp)
    P, C = ys[-1]
    idx = P / (P + C) if (P + C) > 1e-9 else 0.0
    return {
        "load": round(load, 4),
        "p_gingivalis": round(P, 4),
        "s_gordonii": round(C, 4),
        "dysbiosis_index": round(idx, 4),
        "crossed_allee_quorum": bool(P > p["mb_allee_A"]),
        "keystone_pathogen": "Porphyromonas gingivalis",
    }


def source_dysbiosis_multiplier(features: dict, p: dict | None = None) -> float:
    """A bounded multiplier (1 … 1+DYSBIOSIS_SOURCE_MAX) the spine can apply to the structural source: a
    dysbiotic, pathogen-dominated pocket sustains a stronger inflammatory source than the band implies."""
    idx = dysbiosis_index(features, p)["dysbiosis_index"]
    return round(1.0 + DYSBIOSIS_SOURCE_MAX * idx, 4)


def microbiome_centerpiece(features: dict, p: dict | None = None) -> dict[str, Any]:
    """Structural severity → community composition → dysbiosis index + source multiplier, with the
    health counterfactual (a commensal-seeded, low-load community stays commensal)."""
    p = microbiome_params(p)
    dys = dysbiosis_index(features, p)
    return {
        "features": features,
        **dys,
        "source_multiplier": round(1.0 + DYSBIOSIS_SOURCE_MAX * dys["dysbiosis_index"], 4),
        "confidence": "exploratory",
        "flags": ["reduced gLV + Allee keystone (E3.5/E3.6/E3.7); identifiability weak — exploratory",
                  "names P. gingivalis as the keystone the ε-abstraction hides; direction, not a count",
                  "non-diagnostic; population-level composition, never a patient microbial diagnosis"],
    }
