"""The ensemble / uncertainty-quantification driver — predictions as ranges, not points.

This is what makes "adjust the ensemble" a real operation: it takes the calibrated centerpiece +
neuro axis, sweeps the flagged/uncertain parameters (`registry.SWEPT_PARAMS`) with a Latin-hypercube
design, and reports for each output an **envelope** (median + 90% band) over the sweep, plus a
**sensitivity ranking** attributing each output's spread to the parameters that drive it. The shared
ε/`gain` is the common axis of every sweep, so the ranges are coherent across the CV and neuro axes.

Pure-python (uses `histora.stats`); no numpy/scipy required. Non-diagnostic: the outputs are
parameter-level ranges for a structural stratum, never a patient value.
"""

from __future__ import annotations

import random
from typing import Any, Callable

from .mech_calibrate import calibrated_params
from .mech_metabolic import calibrated_metabolic_params, hba1c_shift_pp, insulin_resistance_index
from .mech_models import centerpiece
from .mech_neuro import neuro_centerpiece, neuro_params
from .registry import CLAUDE_MEMBER_WEIGHT_CAP, OUTPUTS, SWEPT_PARAMS


def latin_hypercube(bounds: dict[str, tuple[float, float]], n: int, seed: int = 0) -> list[dict]:
    """Latin-hypercube sample of `n` points over the named `bounds` — far better space coverage than
    a grid at the same cost (the right sampler for 'sweep the epistemic-risk parameters')."""
    rng = random.Random(seed)
    keys = list(bounds)
    cuts = {k: [(i + rng.random()) / n for i in range(n)] for k in keys}
    for k in keys:
        rng.shuffle(cuts[k])
    return [{k: bounds[k][0] + cuts[k][i] * (bounds[k][1] - bounds[k][0]) for k in keys}
            for i in range(n)]


def predict_case(features: dict, p: dict) -> dict[str, float]:
    """Run the full chain (source → IL-6 → CRP → CV & neuro) for a structural stratum and given
    params; return the ensemble's scalar outputs."""
    cp = centerpiece(features, p, verify_dynamics=False)
    nc = neuro_centerpiece(features, p, front=False)   # skip the expensive Braak-chain sim
    gain = cp["inflammatory_gain_pg_ml"]
    return {
        "crp_mg_l": cp["steady_state"]["crp_mg_l"],
        "cv_recruitment_multiplier": cp["cv_axis"]["recruitment_multiplier"],
        "tau_alpha_rel_increase": nc["tau_alpha"]["relative_increase"],
        "tau_burden_rel_increase": nc["tau_burden_horizon"]["relative_increase"],
        "amyloid_rel_increase": nc["amyloid_burden"]["relative_increase"],
        "therapy_onset_delay_yr": nc["tau_onset_years"]["therapy_delay_years"] or 0.0,
        "insulin_resistance_index": insulin_resistance_index(gain, p),
        "hba1c_shift_pp": hba1c_shift_pp(gain, p),
    }


def _summary(vals: list[float]) -> dict[str, float]:
    s = sorted(vals)
    n = len(s)
    return {"lo": round(s[int(0.05 * n)], 4), "median": round(s[n // 2], 4),
            "hi": round(s[min(n - 1, int(0.95 * n))], 4), "mean": round(sum(s) / n, 4)}


def _base_params(target_delta_crp: float = 0.5) -> dict:
    """Calibrated ε + neuro + metabolic constants; the nominal center the sweep bands scale around."""
    return calibrated_metabolic_params(p=neuro_params(calibrated_params(target_delta_crp=target_delta_crp)))


def _resolve_bounds(base: dict) -> dict[str, tuple[float, float]]:
    """SWEPT_PARAMS gives ε as ×nominal (calibrated) and the others as absolute bands."""
    b = dict(SWEPT_PARAMS)
    lo, hi = b["epsilon"]
    b["epsilon"] = (lo * base["epsilon"], hi * base["epsilon"])
    return b


def ensemble_report(features: dict, n: int = 200, seed: int = 0) -> dict[str, Any]:
    """Sweep the flagged/uncertain parameters (Latin hypercube, n samples) and return, for each
    output, an envelope (5th/median/95th/mean) over the sweep — the honest 'range, not a point'. The
    nominal prediction (all params at their calibrated/nominal value) is included for reference."""
    base = _base_params()
    bounds = _resolve_bounds(base)
    samples = latin_hypercube(bounds, n, seed)

    collected: dict[str, list[float]] = {o: [] for o in OUTPUTS}
    for s in samples:
        pred = predict_case(features, dict(base, **s))
        for o in OUTPUTS:
            collected[o].append(pred[o])

    return {
        "features": features,
        "n_samples": n,
        "swept_params": {k: [round(v[0], 4), round(v[1], 4)] for k, v in bounds.items()},
        "nominal": {o: round(v, 4) for o, v in predict_case(features, base).items()},
        "envelope": {o: _summary(v) for o, v in collected.items()},
        "sensitivity": sensitivity_ranking(features, base),
        "guardrail": "non-diagnostic: parameter-level ranges for a structural stratum, not a patient value",
    }


def blend_members(members: list[dict]) -> dict[str, Any]:
    """Bayesian-model-averaging-lite: combine several estimates of ONE output edge into a single
    value + provenance. Each member = {value, weight, source, tier}; a `kind:"claude"` soft-model
    member (a Claude subagent's structured estimate for an un-coded edge) is capped by
    `CLAUDE_MEMBER_WEIGHT_CAP` so it never outweighs a calibrated/validated coded member. Returns the
    weight-averaged value, the min/max member spread (the structural-uncertainty band), and the
    per-source contribution — so a Claude-contributed estimate is always visible and tier-labeled,
    never silently blended into a false precision.

    This is how "Claude as a model" plugs into the ensemble: for edges the coded ODE/PDE library
    cannot reach (novel oral-systemic couplings, sparse-data links), a Claude sub-model supplies a
    reasoned {direction, band, confidence}; coded and Claude members are averaged here, and the
    guardrail + falsification discipline is enforced upstream (the member must ship its check)."""
    if not members:
        return {"value": None, "band": [None, None], "sources": []}
    ws = []
    for m in members:
        w = float(m.get("weight", 1.0))
        if m.get("tier") == "claude":
            w = min(w, CLAUDE_MEMBER_WEIGHT_CAP)
        ws.append(w)
    total = sum(ws) or 1.0
    value = sum(w * float(m["value"]) for w, m in zip(ws, members)) / total
    vals = [float(m["value"]) for m in members]
    return {
        "value": round(value, 4),
        "band": [round(min(vals), 4), round(max(vals), 4)],
        "sources": [{"source": m.get("source", "?"), "tier": m.get("tier", "coded"),
                     "value": round(float(m["value"]), 4), "weight": round(w / total, 3)}
                    for w, m in zip(ws, members)],
    }


def sensitivity_ranking(features: dict, base: dict) -> dict[str, dict[str, float]]:
    """One-at-a-time normalized sensitivity: fractional change in each output per fractional change in
    each swept parameter (a screening elasticity — which unknown dominates each prediction)."""
    out: dict[str, dict[str, float]] = {o: {} for o in OUTPUTS}
    base_pred = predict_case(features, base)
    for k in SWEPT_PARAMS:
        v0 = base[k]
        if not v0:
            continue
        hi = predict_case(features, dict(base, **{k: v0 * 1.1}))
        lo = predict_case(features, dict(base, **{k: v0 * 0.9}))
        for o in OUTPUTS:
            d = (hi[o] - lo[o]) / (0.2 * v0)                 # dOutput/dParam
            elasticity = d * v0 / base_pred[o] if base_pred[o] else 0.0
            out[o][k] = round(elasticity, 3)
    return out
