"""A/B evaluation harness (Phase R5) — Claude only.

Validates the approach by comparing two inputs for the SAME case:

  A (baseline)  = naive abbreviated format, no glossing / no KB
                  (`record_formats.format_a_abbrev_table`).
  B (converged) = the Observer-converged input: JSON + mechanistic KB + interpretability
                  constraints (`format_e_json_kb_constraints`) WITH the deterministic
                  structural signals + missing-mediator collection flags injected
                  (`relational_signals.derived_signals`).

The harness is **model-agnostic**: pass a `model_fn(prompt: str) -> dict` that returns
the agent's structured output (conforming to `schemas/output_schema.json`). Offline
tests use a deterministic stub; the live run wires a real Claude call. Everything runs on
Claude — no proxy, no GPU.

Scoring is **non-diagnostic and guardrail-aware**. B should not lose to A on
mechanism-recall or missing-data flagging, and BOTH outputs must pass the guardrail: an
edit that raises accuracy but breaks the guardrail is rejected (matches
`agents/skillopt-optimizer.md` — the gate is accuracy AND guardrail pass-rate).
"""

from __future__ import annotations

import json
from typing import Any, Callable

from bridge_concepts import BRIDGE_CONCEPTS, MEDIATOR_KEYS, NEURO_MEDIATOR_KEYS
from record_formats import RECORD, format_a_abbrev_table, format_e_json_kb_constraints
from relational_signals import derived_signals, missing_mediators

ModelFn = Callable[[str], dict]


# --------------------------------------------------------------------------- inputs
def build_inputs(record: dict) -> dict[str, str]:
    """The two candidate inputs for one case. B is A's converged counterpart."""
    a = format_a_abbrev_table(record)
    signals = derived_signals(record)
    missing = ", ".join(m["field"] for m in signals["missing_mediators"]) or "none"
    b = (
        format_e_json_kb_constraints(record)
        + "\n\nInjected structural signals (deterministic, non-diagnostic):\n"
        + json.dumps(signals, indent=2)
        + f"\n\nData-completeness directive: the fields under \"missing_mediators\" "
        f"({missing}) are ABSENT from this record. Add EVERY one of them to "
        f"required_missing_data (field + why it matters for the oral-systemic link); "
        f"never impute a value. This is a collection flag, not a patient value."
    )
    return {"A": a, "B": b}


# --------------------------------------------------------------------------- scoring
def _output_text(output: dict) -> str:
    """All free-text the model produced, lowercased, for concept-recall matching."""
    parts: list[str] = list(output.get("research_hypotheses", []))
    for axis in output.get("relational_axes", []):
        parts.append(axis.get("hypothesized_mechanism", ""))
        parts.extend(axis.get("oral_evidence", []))
        parts.extend(axis.get("systemic_evidence", []))
    return " \n ".join(parts).lower()


def mechanism_recall(output: dict) -> tuple[int, int]:
    """How many mediator concepts the output actually reasons with, by any surface
    form. Mediators (not shared factors) are the evidence of relational reasoning."""
    text = _output_text(output)
    hit = 0
    for key in MEDIATOR_KEYS:
        if any(surf.lower() in text for surf in BRIDGE_CONCEPTS[key]):
            hit += 1
    return hit, len(MEDIATOR_KEYS)


def _traced_mediator_recall(output: dict, keys: list[str]) -> tuple[int, int]:
    """How many of `keys` are named inside the `hypothesized_mechanism` of a traced axis — i.e.
    actually used in a traced oral↔systemic relation, not merely mentioned. Kills the
    'name-the-term' substring artifact that plain recall can reward."""
    axes = [a for a in output.get("relational_axes", []) if a.get("traceability")]
    mech_text = " \n ".join(a.get("hypothesized_mechanism", "") for a in axes).lower()
    hit = sum(1 for key in keys
              if any(surf.lower() in mech_text for surf in BRIDGE_CONCEPTS[key]))
    return hit, len(keys)


def relational_recall(output: dict) -> tuple[int, int]:
    """Stricter than mechanism_recall, over the CV/oral-systemic mediators (the primary metric)."""
    return _traced_mediator_recall(output, MEDIATOR_KEYS)


def neuro_relational_recall(output: dict) -> tuple[int, int]:
    """Relational recall over the NEURO-axis mediators (oral↔Alzheimer, Phase 3). Scored separately
    so CV-only cases are not penalized; a neuro-relevant case surfaces these in traced axes."""
    return _traced_mediator_recall(output, NEURO_MEDIATOR_KEYS)


def missing_data_flagged(output: dict, record: dict) -> tuple[int, int]:
    """Of the mediating data truly absent from the record, how many the output flags
    for collection (never imputed)."""
    truly_missing = {m["field"] for m in missing_mediators(record)}
    if not truly_missing:
        return 0, 0
    flagged = {f.get("field") for f in output.get("required_missing_data", [])}
    return len(truly_missing & flagged), len(truly_missing)


def traceability_ok(output: dict) -> bool:
    """Every relational axis must cite the input fields it was derived from."""
    axes = output.get("relational_axes", [])
    return bool(axes) and all(a.get("traceability") for a in axes)


def guardrail_pass(output: dict, record: dict) -> bool:
    """Protected invariant: non-diagnostic disclaimer present, full traceability, and
    every truly-missing mediating datum is acknowledged as a collection flag rather than
    silently used or imputed."""
    if output.get("non_diagnostic_disclaimer") is not True:
        return False
    if not traceability_ok(output):
        return False
    flagged, total = missing_data_flagged(output, record)
    return flagged == total  # all truly-missing fields acknowledged (none imputed)


def score(output: dict, record: dict) -> dict[str, Any]:
    mr_hit, mr_tot = mechanism_recall(output)
    rr_hit, rr_tot = relational_recall(output)
    md_hit, md_tot = missing_data_flagged(output, record)
    gp = guardrail_pass(output, record)
    return {
        "mechanism_recall": mr_hit / mr_tot if mr_tot else 0.0,
        "mechanism_recall_raw": [mr_hit, mr_tot],
        "relational_recall": rr_hit / rr_tot if rr_tot else 0.0,
        "relational_recall_raw": [rr_hit, rr_tot],
        "missing_data_flagged": md_hit / md_tot if md_tot else 1.0,
        "missing_data_raw": [md_hit, md_tot],
        "traceability_ok": traceability_ok(output),
        "guardrail_pass": gp,
    }


# ------------------------------------------------------------------------- A/B runner
def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def run_ab(records: list[dict], model_fn: ModelFn) -> dict[str, Any]:
    """Run both arms over every case and return per-case scores, aggregates, and the
    promotion verdict. `model_fn(prompt)` must return an output_schema.json-shaped dict."""
    per_case = []
    for i, rec in enumerate(records):
        inp = build_inputs(rec)
        sa = score(model_fn(inp["A"]), rec)
        sb = score(model_fn(inp["B"]), rec)
        per_case.append({"case": i, "A": sa, "B": sb})

    def agg(arm: str, metric: str) -> float:
        return _mean([c[arm][metric] for c in per_case])

    def rate(arm: str) -> float:
        return _mean([1.0 if c[arm]["guardrail_pass"] else 0.0 for c in per_case])

    aggregate = {
        "A": {"mechanism_recall": agg("A", "mechanism_recall"),
              "missing_data_flagged": agg("A", "missing_data_flagged"),
              "guardrail_pass_rate": rate("A")},
        "B": {"mechanism_recall": agg("B", "mechanism_recall"),
              "missing_data_flagged": agg("B", "missing_data_flagged"),
              "guardrail_pass_rate": rate("B")},
    }
    # Promotion gate. The guardrail is a HARD prerequisite: an arm that fails it is not
    # a deployable output, no matter its accuracy (health context). Among guardrail-
    # passing candidates, promote B when it is a Pareto improvement over A — no
    # regression on either accuracy sub-metric, and a strict gain on at least one axis
    # that matters (mechanism-recall, missing-data flagging, or guardrail pass-rate).
    a, b = aggregate["A"], aggregate["B"]
    no_regression = (
        b["mechanism_recall"] >= a["mechanism_recall"]
        and b["missing_data_flagged"] >= a["missing_data_flagged"]
    )
    strict_gain = (
        b["mechanism_recall"] > a["mechanism_recall"]
        or b["missing_data_flagged"] > a["missing_data_flagged"]
        or b["guardrail_pass_rate"] > a["guardrail_pass_rate"]
    )
    promote_b = b["guardrail_pass_rate"] == 1.0 and no_regression and strict_gain
    return {
        "n_cases": len(records),
        "per_case": per_case,
        "aggregate": aggregate,
        "verdict": "promote_B" if promote_b else "keep_A",
    }


def default_cases() -> list[dict]:
    """The grounded case(s) to A/B on. Replace / extend with real participants via
    `nhanes_loader.build_case(...)` for the live run."""
    return [RECORD]
