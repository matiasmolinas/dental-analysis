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

from typing import Any, Callable

from bridge_concepts import BRIDGE_CONCEPTS, MEDIATOR_KEYS
from ab_eval import score
from record_formats import format_a_abbrev_table
from relational_signals import missing_mediators


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

    # Three comparable axes per arm (guardrail as a 0/1 pass-rate).
    AXES = ["mechanism_recall", "missing_data_flagged", "guardrail_pass_rate"]

    def arm_agg(arm):
        return {
            "mechanism_recall": _mean([c[arm]["mechanism_recall"] for c in per_case]),
            "missing_data_flagged": _mean([c[arm]["missing_data_flagged"] for c in per_case]),
            "guardrail_pass_rate": _mean([1.0 if c[arm]["guardrail_pass"] else 0.0
                                          for c in per_case]),
        }

    aggregate = {arm: arm_agg(arm) for arm in ("A", "B_blind", "B_lens")}

    # Does the lens add value OVER blind convergence? Strict gain on some axis, no regression.
    bl, bb = aggregate["B_lens"], aggregate["B_blind"]
    no_regression = all(bl[a] >= bb[a] for a in AXES)
    strict_gain = any(bl[a] > bb[a] for a in AXES)
    if strict_gain and no_regression:
        verdict = "lens_adds_value"
    elif strict_gain:  # better on one axis, worse on another
        verdict = "lens_mixed"
    else:
        verdict = "lens_neutral"  # blind convergence is as good -> lens not earning its keep

    return {
        "n_cases": len(records),
        "per_case": per_case,
        "aggregate": aggregate,
        "deltas": {
            "B_lens_minus_B_blind": {a: round(bl[a] - bb[a], 4) for a in AXES},
            "B_blind_minus_A": {a: round(bb[a] - aggregate["A"][a], 4) for a in AXES},
        },
        "verdict": verdict,
    }
