# EXPERIMENTAL — the memory-value experiment (docs/FORWARD_PLAN.md); result TBD, not yet run
"""Cross-session memory VALUE test — and the loop closure (memory-value path).

This is the FIRST caller of `lever_ledger.consolidate` and `lever_ledger.suggest_levers`, both
wired to nothing before now: `run_swc_session` only ever WROTE levers. It closes the loop the
Observer/SWC design implies — seed levers over solved cases, run the offline "sleep"
consolidation, then feed the consolidated belief back into the next session's INPUT — and
measures whether that WARM start beats a COLD start on held-out cases.

Pipeline:
  1. seed_ledger — over TRAINING cases, write a working lever per case (live: a compact
     SWC turn-1→turn-2 pass; offline: an injected stub lever_fn).
  2. consolidate(ledger, min_support) — the sleep pass: promote stable beliefs, drop noise.
  3. run_memory_value — for each HELD-OUT case: COLD = base input; WARM = base + the matched
     consolidated belief's learned consideration (the seam feeding memory into the next input);
     score both (ab_eval.score) + counterfactual_report; report WARM−COLD with a bootstrap CI.

Metric: WARM−COLD on guardrail_pass_rate, relational_recall, cf mean_affected_delta. CONFIRMS
if a CI excludes 0 (likeliest on guardrail/consistency reliability — in-session T0 can't fix
cross-case); REFUTES if WARM ≈ COLD (no transfer) or regresses (stale-lever dilution). The
likely null is honest and does NOT generalize to "memory is worthless".

Model-agnostic core (seed_ledger / run_memory_value take injected fns) so it is tested offline;
the live main wires Opus/Sonnet.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Callable

sys.path.insert(0, os.path.dirname(__file__))

from ab_eval import score
from ablation import _bootstrap_ci
from counterfactual import counterfactual_report
from lever_ledger import (
    _sig_key,
    case_signature,
    consolidate,
    suggest_levers,
    write_lever,
)


def seed_ledger(records: list[dict], ledger_path: str,
                lever_fn: Callable[[dict], dict | None]) -> int:
    """Write a working lever per training case. `lever_fn(record)->lever|None` returns a
    guardrail-valid lever (or None if the case yielded no improvement). Returns #written."""
    written = 0
    for rec in records:
        lever = lever_fn(rec)
        if lever is None:
            continue
        try:
            write_lever(ledger_path, lever)
            written += 1
        except ValueError:
            pass  # guardrail rejected (value leak / fail) — do not persist
    return written


def _belief_matches(belief_sig: dict, sig: dict) -> bool:
    """Same match rule as suggest_levers: exact signature OR comorbidity overlap."""
    exact = _sig_key(belief_sig) == _sig_key(sig)
    overlap = set(belief_sig.get("comorbidities", [])) & set(sig.get("comorbidities", []))
    return exact or bool(overlap)


def warm_suffix(beliefs: list[dict], sig: dict) -> str:
    """The seam: turn matched consolidated beliefs into a factor-specific input suffix. Injects
    the `mediator_moved` concepts the belief learned — memory feeding the next input. Empty when
    no belief matches (the honest COLD==WARM case)."""
    concepts = []
    for b in beliefs:
        if _belief_matches(b.get("case_signature", {}), sig):
            concepts.extend(c for c in b.get("mediator_moved", []) if c)
    seen, uniq = set(), []
    for c in concepts:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    if not uniq:
        return ""
    return ("\n\nConsider these factor-specific points learned from prior similar cases:\n"
            + "\n".join("- " + c for c in uniq))


def run_memory_value(
    held_out: list[dict],
    ledger_path: str,
    build_fn: Callable[[dict], str],
    eval_fn: Callable[[str], dict],
    min_support: int = 2,
) -> dict[str, Any]:
    """COLD vs WARM A/B on held-out cases. WARM = base input + the matched consolidated belief.
    Reports per-case scores + WARM−COLD bootstrap CIs + verdict."""
    beliefs = consolidate(ledger_path, min_support=min_support)  # the sleep pass (first caller)

    per_case = []
    for i, rec in enumerate(held_out):
        sig = case_signature(rec)
        suggested = suggest_levers(ledger_path, sig)  # first caller (surfaced for the record)
        suffix = warm_suffix(beliefs, sig)

        def warm_build(r: dict, s: str = suffix) -> str:
            return build_fn(r) + s

        cold_s = score(eval_fn(build_fn(rec)), rec)
        warm_s = score(eval_fn(warm_build(rec)), rec)
        cf_cold = counterfactual_report([rec], build_fn, eval_fn)
        cf_warm = counterfactual_report([rec], warm_build, eval_fn)
        per_case.append({
            "case": i,
            "warm_applied": bool(suffix),
            "n_suggested_levers": len(suggested),
            "cold": {"relational_recall": cold_s["relational_recall"],
                     "guardrail_pass": cold_s["guardrail_pass"],
                     "cf_mean_affected_delta": cf_cold["mean_affected_delta"]},
            "warm": {"relational_recall": warm_s["relational_recall"],
                     "guardrail_pass": warm_s["guardrail_pass"],
                     "cf_mean_affected_delta": cf_warm["mean_affected_delta"]},
        })

    def _delta(c, axis):
        if axis == "guardrail_pass":
            return int(c["warm"]["guardrail_pass"]) - int(c["cold"]["guardrail_pass"])
        return c["warm"][axis] - c["cold"][axis]

    AXES = ["guardrail_pass", "relational_recall", "cf_mean_affected_delta"]
    ci = {a: _bootstrap_ci([_delta(c, a) for c in per_case]) for a in AXES}
    sig_gain = [a for a in AXES if ci[a]["lo"] > 0]
    sig_loss = [a for a in AXES if ci[a]["hi"] < 0]
    if sig_gain and not sig_loss:
        verdict = "memory_adds_value"
    elif sig_loss:
        verdict = "memory_regresses"
    else:
        verdict = "memory_inconclusive"

    return {
        "n_held_out": len(held_out),
        "n_beliefs_consolidated": len(beliefs),
        "beliefs": beliefs,
        "per_case": per_case,
        "ci_90_warm_minus_cold": ci,
        "significant_gain_axes": sig_gain,
        "significant_loss_axes": sig_loss,
        "verdict": verdict,
    }


# --------------------------------------------------------------------------- live wiring

def _make_live_lever_fn(client, executor, reviewer, selector):
    """A compact SWC turn-1→turn-2 pass that returns a working lever for a training case
    (mirrors run_swc_session, distilled). Returns None if turn 2 did not improve."""
    from record_formats import format_b_sections_glossed

    def lever_fn(rec: dict) -> dict | None:
        t1_in = format_b_sections_glossed(rec)
        t1_out = executor(t1_in)
        s1 = score(t1_out, rec)
        cf1 = counterfactual_report([rec], format_b_sections_glossed, executor)
        items = [it for it in reviewer(
            "SOLVER INPUT:\n" + t1_in + "\n\nSOLVER OUTPUT (model absent content, do NOT re-solve):\n"
            + json.dumps(t1_out, indent=2)).get("items", []) if not it.get("appears_in_output")]
        keep = set(selector("CASE:\n" + t1_in + "\n\nITEMS:\n"
                            + json.dumps([{"key": g["key"], "concept": g["concept"]} for g in items])
                            ).get("keep_keys", []))
        targeted = [g for g in items if g["key"] in keep]
        if not targeted:
            return None
        suffix = ("\n\nConsider these factor-specific points:\n"
                  + "\n".join("- " + g["concept"] for g in targeted))
        t2_build = lambda r: format_b_sections_glossed(r) + suffix  # noqa: E731
        s2 = score(executor(t2_build(rec)), rec)
        cf2 = counterfactual_report([rec], t2_build, executor)
        improved = ((s2["relational_recall"] > s1["relational_recall"]
                     or cf2["mean_affected_delta"] > cf1["mean_affected_delta"])
                    and (s2["guardrail_pass"] or not s1["guardrail_pass"]))
        if not improved:
            return None
        return {"case_signature": case_signature(rec), "surface": "injected_variables",
                "lever": "inject targeted factor-specific review considerations",
                "mediator_moved": targeted[0]["concept"][:80],
                "corroboration": "repeated_turns", "confidence": 0.6, "guardrail_pass": True,
                "provenance": "memory_value seed (swc turn1->turn2)"}

    return lever_fn


def main() -> None:
    ap = argparse.ArgumentParser(description="Cross-session memory value test (COLD vs WARM)")
    ap.add_argument("--cases", choices=["planted", "nhanes"], default="nhanes")
    ap.add_argument("--n-train", type=int, default=4)
    ap.add_argument("--n-holdout", type=int, default=3)
    ap.add_argument("--min-support", type=int, default=2)
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--reviewer-model", default="claude-opus-4-8")
    ap.add_argument("--selector-model", default="claude-sonnet-5")
    ap.add_argument("--fresh-ledger", action="store_true",
                    help="seed a scratch ledger for this run instead of appending to the live one")
    ap.add_argument("--ledger", default=os.path.join(os.path.dirname(__file__), "..",
                                                     "results", "memory_value_ledger.jsonl"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "memory_value_report.json"))
    args = ap.parse_args()

    from record_formats import format_b_sections_glossed
    from run_gate import PLANTED_CASE, PREDICTOR_SYSTEM, PREDICTOR_TOOL, _make_call
    from run_targeted import SELECTOR_SYSTEM, SELECTOR_TOOL
    from run_live_ab import _load_dotenv, load_cases, make_claude_model_fn

    _load_dotenv()
    import anthropic
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set.")
    client = anthropic.Anthropic()

    if args.cases == "planted":
        train, held_out = [PLANTED_CASE], [PLANTED_CASE]
    else:
        cases = load_cases("nhanes", args.n_train + args.n_holdout, None)
        train, held_out = cases[:args.n_train], cases[args.n_train:]

    if args.fresh_ledger and os.path.exists(args.ledger):
        os.remove(args.ledger)

    executor = make_claude_model_fn(args.model)
    reviewer = _make_call(client, args.reviewer_model, PREDICTOR_SYSTEM, "predicted_workspace", PREDICTOR_TOOL)
    selector = _make_call(client, args.selector_model, SELECTOR_SYSTEM, "selection", SELECTOR_TOOL)
    lever_fn = _make_live_lever_fn(client, executor, reviewer, selector)

    n_written = seed_ledger(train, args.ledger, lever_fn)
    report = run_memory_value(held_out, args.ledger, format_b_sections_glossed, executor,
                              min_support=args.min_support)
    report["meta"] = {"cases": args.cases, "n_train": len(train), "n_seeded": n_written,
                      "min_support": args.min_support, "model": args.model, "ledger": args.ledger}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"seeded {n_written}/{len(train)} levers | consolidated {report['n_beliefs_consolidated']} beliefs")
    print("WARM-COLD CI90:", json.dumps(report["ci_90_warm_minus_cold"]))
    print("VERDICT:", report["verdict"], "| wrote:", args.out)


if __name__ == "__main__":
    main()
