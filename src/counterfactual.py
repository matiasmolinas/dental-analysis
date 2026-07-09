"""Counterfactual-sensitivity runner (Phase R6 v2) — tests REASONING, not vocabulary.

The substring recall metric can be gamed by an input that merely *names* mediators. This
runner tests whether an input format makes the model actually *use* a factor: flip one
input factor (present ↔ absent) and check that the dependent relational axis moves in the
mechanistically-correct direction while unrelated axes stay put. A format whose output is
*insensitive* to flipping a factor it should depend on is a bad format — the same signal
the workspace lens gives, measured behaviorally at the output (API-observable, Claude only).

This is the honest corroboration a self-report lens needs, and the fair way to ask whether
a lens-guided input reasons better (not just names more): a more counterfactually-sensitive
format is genuinely using its inputs.

Model-agnostic: pass `build_input_fn(record) -> str` and `eval_fn(input) -> dict`.
"""

from __future__ import annotations

import copy
from typing import Any, Callable

# factor in the record  ->  (relational axis it should drive, how to remove it)
FACTORS: dict[str, str] = {
    "type2_diabetes": "metabolic",
    "smoking_active": "shared_behavioral",
    "hypertension": "vascular",
}

_CONF = {"absent": 0, "low": 1, "medium": 2, "high": 3}


def flip(record: dict, factor: str) -> dict:
    """Return a copy of `record` with `factor` removed (set to a non-present value).
    Removes co-indicators so the factor is genuinely absent, never imputes anything."""
    r = copy.deepcopy(record)
    shared, med = r.get("shared_risk", {}), r.get("medical_cv", {})
    if factor == "type2_diabetes":
        shared["type2_diabetes"] = False
        shared.pop("hba1c", None)
    elif factor == "smoking_active":
        shared["smoking_active"] = False
        shared["smoking_pack_years"] = 0
    elif factor == "hypertension":
        shared["hypertension"] = False
        shared.pop("blood_pressure", None)
    else:
        raise ValueError(f"unknown factor {factor!r}")
    return r


def axis_conf(output: dict, axis: str) -> int:
    """Confidence of a relational axis in the output (0 if absent)."""
    best = 0
    for a in output.get("relational_axes", []):
        if a.get("axis") == axis:
            best = max(best, _CONF.get(a.get("confidence", "absent"), 0))
    return best


def sensitivity(
    record: dict,
    factor: str,
    build_input_fn: Callable[[dict], str],
    eval_fn: Callable[[str], dict],
) -> dict[str, Any]:
    """Flip one factor; does its target axis weaken while unrelated axes stay put?"""
    target = FACTORS[factor]
    out_present = eval_fn(build_input_fn(record))
    out_absent = eval_fn(build_input_fn(flip(record, factor)))

    affected_delta = axis_conf(out_present, target) - axis_conf(out_absent, target)
    unrelated = [a for a in FACTORS.values() if a != target]
    unrelated_moves = [abs(axis_conf(out_present, ax) - axis_conf(out_absent, ax))
                       for ax in unrelated]
    max_unrelated = max(unrelated_moves) if unrelated_moves else 0
    # Sensitive = the affected axis dropped when the factor was removed, and unrelated
    # axes moved less than the affected one (coherent, targeted response).
    sensitive = affected_delta > 0 and affected_delta > max_unrelated
    return {
        "factor": factor,
        "target_axis": target,
        "affected_delta": affected_delta,
        "max_unrelated_delta": max_unrelated,
        "sensitive": sensitive,
    }


def counterfactual_report(
    records: list[dict],
    build_input_fn: Callable[[dict], str],
    eval_fn: Callable[[str], dict],
    factors: list[str] | None = None,
) -> dict[str, Any]:
    """Aggregate counterfactual sensitivity for one input-building strategy."""
    factors = factors or list(FACTORS)
    rows = []
    for i, rec in enumerate(records):
        for f in factors:
            rows.append({"case": i, **sensitivity(rec, f, build_input_fn, eval_fn)})
    n = len(rows)
    sens_rate = sum(r["sensitive"] for r in rows) / n if n else 0.0
    mean_affected = sum(r["affected_delta"] for r in rows) / n if n else 0.0
    return {
        "n_flips": n,
        "sensitivity_rate": sens_rate,
        "mean_affected_delta": mean_affected,
        "rows": rows,
    }
