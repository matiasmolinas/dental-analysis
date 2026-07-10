# EXPERIMENTAL / inconclusive result — see docs/RESEARCH_SUMMARY.md §0 and RETROSPECTIVE.md
"""Targeted actuator on a non-obvious-gap task (Phase R6, next-step #2) — Claude only.

The behavioral test (`run_gate_behavioral`) grounded ALL surfaced gaps as one checklist and it HURT
(dilution). The design (`fable-predicted-workspace-design.md` §5, `lens-non-redundancy-burden-of-proof.md`
§5) called for a FREE / TARGETED actuator instead: keep only the gaps a judge deems mechanistically
relevant to the present factors, injected as factor-anchored considerations — and measure whether
that *selective* grounding beats both the base input and the crude append-all.

Three arms per case, scored by counterfactual sensitivity + relational_recall (guardrail a hard gate):
  base      = the input as-is
  append_all = base + every surfaced gap (the crude actuator that hurt)
  targeted   = base + only the judge-selected, mechanistically-relevant gaps (the free actuator v1)

n is a CLI flag; n>=30 is the powered target (bounded here for cost). Uses the predictor to surface
gaps per case (Opus, which does not refuse), a selector judge, and the neutral evaluator.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from ab_eval import score
from ablation import _bootstrap_ci
from counterfactual import counterfactual_report
from record_formats import format_b_sections_glossed
from run_gate import PLANTED_CASE, PREDICTOR_TOOL, PREDICTOR_SYSTEM, _make_call
from run_live_ab import _load_dotenv, load_cases, make_claude_model_fn

SELECTOR_SYSTEM = """You select which review considerations to inject into a downstream oral-systemic
analysis. KEEP only items that are mechanistically tied to the SPECIFIC factors present in this case
(e.g. a drug-tissue interaction for a drug the patient is on, a confounder of a present finding, a
mediator directly linking the oral and systemic data). DROP peripheral/administrative items (generic
missing-data checklists, risk-score bookkeeping) that would dilute the core mediating reasoning.
Return, via the tool, keep_keys = the keys of the items to keep."""

SELECTOR_TOOL = {"type": "object", "properties": {"keep_keys": {"type": "array",
    "items": {"type": "string"}}}, "required": ["keep_keys"]}

# The lens-free CONTROL (the missing arm, per why-no-lens-payoff.md §5 Q4). A competent analyst
# brainstorms the mattering, output-absent considerations from (input, output) using ONLY its own
# expertise — NO predictor, NO workspace/lens self-report. The delta targeted − brainstorm_targeted
# isolates any lens-beyond-K_R marginal; if brainstorm matches targeted, the boundary condition wins
# (a competent reader recovered the gaps from output + prior with no lens).
BRAINSTORM_SYSTEM = """You are a careful oral-systemic (periodontal + cardiovascular) research analyst.
Non-diagnostic. You are given a case and a first-pass analysis OUTPUT. Using ONLY your own expertise —
you have NO access to the model's internal reasoning — brainstorm the MOST IMPORTANT considerations a
strong analysis should address that this output appears to have MISSED: key confounders, drug-tissue
interactions, mediators, or inconsistencies absent from the output. Be selective (top ~8). Do not
re-solve; only list the missed considerations.
Return, via the tool, items = [{key: short_snake_case_id, concept: short phrase}]."""

BRAINSTORM_TOOL = {"type": "object", "properties": {"items": {"type": "array", "items": {
    "type": "object", "properties": {"key": {"type": "string"}, "concept": {"type": "string"}},
    "required": ["key", "concept"]}}}, "required": ["items"]}


def _gaps_block(items, header):
    return ("\n\n" + header + "\n" + "\n".join("- " + i["concept"] for i in items)) if items else ""


def main() -> None:
    ap = argparse.ArgumentParser(description="Targeted actuator on a non-obvious-gap task")
    ap.add_argument("--cases", choices=["planted", "nhanes"], default="planted")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--model", default="claude-opus-4-8")           # executor / evaluator
    ap.add_argument("--predictor-model", default="claude-opus-4-8")  # surfaces gaps (no refusal)
    ap.add_argument("--brainstorm-model", default="claude-opus-4-8")  # lens-free K_R control
    ap.add_argument("--judge-model", default="claude-sonnet-5")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "targeted_report.json"))
    args = ap.parse_args()

    _load_dotenv()
    import anthropic
    client = anthropic.Anthropic()
    cases = [PLANTED_CASE] if args.cases == "planted" else load_cases("nhanes", args.n, None)

    eval_fn = make_claude_model_fn(args.model)
    predictor = _make_call(client, args.predictor_model, PREDICTOR_SYSTEM,
                           "predicted_workspace", PREDICTOR_TOOL)
    selector = _make_call(client, args.judge_model, SELECTOR_SYSTEM, "selection", SELECTOR_TOOL)
    brainstorm = _make_call(client, args.brainstorm_model, BRAINSTORM_SYSTEM,
                            "brainstorm", BRAINSTORM_TOOL)

    def _select(items):  # same selector filter for both lens and brainstorm arms (fair)
        keep = set(selector("CASE:\n" + base_in + "\n\nITEMS:\n"
                            + json.dumps([{"key": g["key"], "concept": g["concept"]} for g in items])
                            ).get("keep_keys", []))
        return [g for g in items if g["key"] in keep]

    per_case = []
    for i, rec in enumerate(cases):
        base_in = format_b_sections_glossed(rec)
        out = eval_fn(base_in)
        out_json = json.dumps(out, indent=2)
        # LENS arm: predictor surfaces gaps from the workspace self-report (delta framing)
        items = predictor("SOLVER INPUT:\n" + base_in
                          + "\n\nSOLVER OUTPUT (model absent content, do NOT re-solve):\n"
                          + out_json).get("items", [])
        gaps = [it for it in items if not it.get("appears_in_output")]
        targeted = _select(gaps)
        # BRAINSTORM control: a competent read of (input, output), NO lens
        bs_items = brainstorm("CASE:\n" + base_in + "\n\nFIRST-PASS OUTPUT:\n" + out_json).get("items", [])
        brainstorm_targeted = _select(bs_items)

        # each arm = the injected text suffix (empty for base); applied on top of format_b of
        # whatever record the counterfactual runner passes (flipped or not).
        suffixes = {
            "base": "",
            "append_all": _gaps_block(gaps, "Consider these:"),
            "targeted": _gaps_block(targeted, "Consider these factor-specific points:"),
            "brainstorm_targeted": _gaps_block(brainstorm_targeted,
                                               "Consider these factor-specific points:"),
        }
        row = {"case": i, "n_gaps": len(gaps), "n_targeted": len(targeted),
               "n_brainstorm_targeted": len(brainstorm_targeted)}
        for arm, suffix in suffixes.items():
            builder = (lambda s: (lambda r: format_b_sections_glossed(r) + s))(suffix)
            cf = counterfactual_report([rec], builder, eval_fn)
            sc = score(eval_fn(builder(rec)), rec)
            row[arm] = {"cf_mean_affected_delta": cf["mean_affected_delta"],
                        "cf_sensitivity_rate": cf["sensitivity_rate"],
                        "relational_recall": sc["relational_recall"],
                        "guardrail_pass": sc["guardrail_pass"]}
        per_case.append(row)

    def agg(arm, metric):
        xs = [c[arm][metric] for c in per_case]
        return round(sum(xs) / len(xs), 3) if xs else 0.0

    ARMS = ("base", "append_all", "targeted", "brainstorm_targeted")
    aggregate = {arm: {m: agg(arm, m) for m in ("cf_mean_affected_delta", "relational_recall")}
                 for arm in ARMS}

    # Significance-aware: bootstrap 90% CIs on PAIRED per-case deltas, so a point gain on few cases
    # cannot fire "useful" (matches ablation.py's discipline). Two contrasts:
    #  targeted − base            : does selective lens-guided injection help at all?
    #  targeted − brainstorm      : the LENS-BEYOND-K_R marginal — does the lens add anything over a
    #                               competent lens-free brainstorm of the same output? (the §5 Q4 test)
    METRICS = ("cf_mean_affected_delta", "relational_recall")
    ci = {m: _bootstrap_ci([c["targeted"][m] - c["base"][m] for c in per_case]) for m in METRICS}
    ci_vs_brainstorm = {m: _bootstrap_ci([c["targeted"][m] - c["brainstorm_targeted"][m]
                                          for c in per_case]) for m in METRICS}
    sig_gain = [m for m in METRICS if ci[m]["lo"] > 0]
    sig_loss = [m for m in METRICS if ci[m]["hi"] < 0]
    lens_beyond_kr = [m for m in METRICS if ci_vs_brainstorm[m]["lo"] > 0]
    report = {"meta": {"cases": args.cases, "n": len(cases), "model": args.model},
              "per_case": per_case, "aggregate": aggregate,
              "targeted_minus_base": {
                  m: round(aggregate["targeted"][m] - aggregate["base"][m], 3) for m in METRICS},
              "targeted_minus_brainstorm": {
                  m: round(aggregate["targeted"][m] - aggregate["brainstorm_targeted"][m], 3)
                  for m in METRICS},
              "ci_90_targeted_minus_base": ci,
              "ci_90_targeted_minus_brainstorm": ci_vs_brainstorm,
              "significant_gain_metrics": sig_gain,
              "significant_loss_metrics": sig_loss,
              "lens_beyond_kr_significant_metrics": lens_beyond_kr,
              # the honest headline for the §5 Q4 test: does the lens beat the lens-free brainstorm?
              "lens_beyond_kr_verdict": ("lens_adds_over_brainstorm" if lens_beyond_kr
                                         else "boundary_wins_brainstorm_matches_lens")}
    # Useful only if a delta's CI EXCLUDES 0 (a real effect) with no significant regression.
    # Point-positive-but-CI-straddles-0 is honestly inconclusive, not a win.
    if sig_gain and not sig_loss:
        report["verdict"] = "targeted_useful"
    elif sig_loss:
        report["verdict"] = "targeted_regresses"
    elif (report["targeted_minus_base"]["cf_mean_affected_delta"] > 0
          or report["targeted_minus_base"]["relational_recall"] > 0):
        report["verdict"] = "targeted_directional_inconclusive"  # point-positive, CI straddles 0
    else:
        report["verdict"] = "targeted_neutral_or_negative"

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    for arm in ARMS:
        a = aggregate[arm]
        print(f"{arm:19s} cf_delta={a['cf_mean_affected_delta']:+.2f}  rel_recall={a['relational_recall']:.2f}")
    print("targeted-base:", report["targeted_minus_base"], "| VERDICT:", report["verdict"])
    print("targeted-brainstorm (lens beyond K_R):", report["targeted_minus_brainstorm"])
    print("CI90 targeted-brainstorm:", json.dumps(report["ci_90_targeted_minus_brainstorm"]))
    print("LENS-BEYOND-K_R VERDICT:", report["lens_beyond_kr_verdict"], "| wrote:", args.out)


if __name__ == "__main__":
    main()
