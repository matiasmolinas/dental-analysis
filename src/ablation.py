"""Three-arm ablation to isolate the inferred lens's causal contribution (Phase R6).

The live A/B (ab_eval.py) compares naive input (A) vs a hand-converged input (B). It
shows a converged input wins, but it does NOT isolate whether the *inferred lens* did any
work — B is just a good author's convergence. This ablation closes that gap:

  A        = naive input (format_a_abbrev_table).
  B_blind  = a capable model converges the input using ONLY its general expertise —
             no lens readout, no deficiency map (blind prompt engineering).
  B_lens   = the executor runs on the naive input with the workspace-probe -> an inferred
             lens readout; the Observer diagnoses deficiencies; the SAME capable converger
             then converges the input FROM that diagnosis.

The ONLY difference between B_blind and B_lens is the lens/deficiency information, so any
gap between them is attributable to the lens. The lens "earns its keep" iff
B_lens > B_blind on the guardrail-critical axis (or recall) beyond noise. All three inputs
are scored by the SAME neutral evaluator + the ab_eval metrics.

Model-agnostic: `run_ablation(records, readout_fn, observer_fn, converge_fn, eval_fn)` so
it is testable offline with stubs; the live wiring builds the four fns from the Anthropic
SDK (see run_ablation.py). Self-report is not ground truth — this measures whether the
lens signal *changes what gets converged*, judged by task accuracy + the guardrail.
"""

from __future__ import annotations

import random
from typing import Any, Callable

from bridge_concepts import BRIDGE_CONCEPTS, MEDIATOR_KEYS
from ab_eval import score
from record_formats import format_a_abbrev_table
from relational_signals import missing_mediators


def _bootstrap_ci(deltas: list[float], iters: int = 2000, alpha: float = 0.10,
                  seed: int = 0) -> dict[str, float]:
    """Seeded (reproducible) bootstrap CI on the mean of per-case deltas. lo>0 => a
    significant positive effect; hi<0 => significant negative; straddling 0 => noise."""
    if not deltas:
        return {"mean": 0.0, "lo": 0.0, "hi": 0.0}
    rng = random.Random(seed)
    n = len(deltas)
    means = []
    for _ in range(iters):
        sample = [deltas[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int((alpha / 2) * iters)]
    hi = means[int((1 - alpha / 2) * iters)]
    return {"mean": round(sum(deltas) / n, 4), "lo": round(lo, 4), "hi": round(hi, 4)}


def spec_text(record: dict) -> str:
    """The required-mediators / required-missing spec the Observer scores against."""
    mediators = ", ".join(MEDIATOR_KEYS)
    missing = ", ".join(m["field"] for m in missing_mediators(record)) or "none"
    return (
        f"Target mediators that should be represented: {mediators}. "
        f"Mediating data absent from this record (must be flagged for collection, never "
        f"imputed): {missing}. Procedure steps expected: staging, pathway grouping, "
        f"axis derivation."
    )


def run_ablation(
    records: list[dict],
    readout_fn: Callable[[str], str],
    observer_fn: Callable[[str, str, str], str],
    converge_fn: Callable[[dict, dict | None], str],
    eval_fn: Callable[[str], dict],
) -> dict[str, Any]:
    """Run the three arms over every case and report per-case scores + aggregates + the
    lens-value verdict.

    readout_fn(naive_input) -> inferred-lens readout (text/JSON)
    observer_fn(naive_input, readout, spec) -> deficiency map (text/JSON)
    converge_fn(record, diagnosis|None) -> converged input string
        diagnosis is {"readout":..., "deficiency_map":...} for B_lens, None for B_blind
    eval_fn(input) -> output_schema.json-shaped dict (the neutral evaluator)
    """
    per_case = []
    for i, rec in enumerate(records):
        a_in = format_a_abbrev_table(rec)
        readout = readout_fn(a_in)
        defmap = observer_fn(a_in, readout, spec_text(rec))
        blind_in = converge_fn(rec, None)
        lens_in = converge_fn(rec, {"readout": readout, "deficiency_map": defmap})
        per_case.append({
            "case": i,
            "A": score(eval_fn(a_in), rec),
            "B_blind": score(eval_fn(blind_in), rec),
            "B_lens": score(eval_fn(lens_in), rec),
        })

    def _mean(xs):
        return sum(xs) / len(xs) if xs else 0.0

    # Comparable axes per arm (guardrail + booleans mapped to 0/1 rates).
    AXES = ["mechanism_recall", "relational_recall", "missing_data_flagged",
            "guardrail_pass_rate"]

    def _val(cell, axis):
        if axis == "guardrail_pass_rate":
            return 1.0 if cell["guardrail_pass"] else 0.0
        return cell[axis]

    def arm_agg(arm):
        return {a: _mean([_val(c[arm], a) for c in per_case]) for a in AXES}

    aggregate = {arm: arm_agg(arm) for arm in ("A", "B_blind", "B_lens")}

    # Paired per-case deltas (B_lens - B_blind) with a bootstrap 90% CI, so the verdict
    # is significance-aware and cannot fire on sub-noise point differences (the v1 flaw).
    ci = {}
    for a in AXES:
        deltas = [_val(c["B_lens"], a) - _val(c["B_blind"], a) for c in per_case]
        ci[a] = _bootstrap_ci(deltas)

    # The lens earns its keep only where a delta's CI excludes 0 (a real effect), and
    # nowhere significantly regresses.
    sig_gain = [a for a in AXES if ci[a]["lo"] > 0]
    sig_loss = [a for a in AXES if ci[a]["hi"] < 0]
    if sig_gain and not sig_loss:
        verdict = "lens_adds_value"
    elif sig_gain and sig_loss:
        verdict = "lens_mixed"
    else:
        verdict = "lens_inconclusive"  # no axis's CI excludes 0 at this n

    return {
        "n_cases": len(records),
        "per_case": per_case,
        "aggregate": aggregate,
        "deltas": {
            "B_lens_minus_B_blind": {a: round(aggregate["B_lens"][a] - aggregate["B_blind"][a], 4)
                                     for a in AXES},
            "B_blind_minus_A": {a: round(aggregate["B_blind"][a] - aggregate["A"][a], 4)
                                for a in AXES},
        },
        "ci_90_B_lens_minus_B_blind": ci,
        "significant_gain_axes": sig_gain,
        "significant_loss_axes": sig_loss,
        "verdict": verdict,
    }
