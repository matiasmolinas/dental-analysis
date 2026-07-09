# EXPERIMENTAL — the Path A experiment (docs/FORWARD_PLAN.md); result TBD, not yet run
"""Live QA-monitor eval on Claude (Path A) — the experiment that can upgrade the verdict.

For each case: the executor (Opus) produces a clean output; inject_defects makes one labeled
corruption per applicable class + keeps the clean output as a control; the MONITOR (Opus,
off-plane read) and the BLIND baseline (Opus, generic "any problems?") both read every
(input, output); a Sonnet match-judge decides whether each read caught the planted defect.
Headline = monitor_recall − blind_recall on injected defects (bootstrap CI), at matched
control false-positive rate.

Roles: executor = Opus, monitor = Opus, blind = Opus (SAME model — fairness), judge = Sonnet.
Fable refuses the medical read, so no Fable here. Everything on Claude.

Usage:  python src/run_qa_eval.py [--cases planted|nhanes] [--n 3]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from inject_defects import inject_all
from qa_monitor import (
    BLIND_READ_SYSTEM,
    MATCH_JUDGE_SYSTEM,
    MATCH_JUDGE_TOOL,
    MONITOR_SYSTEM,
    MONITOR_TOOL,
    caught,
    detect,
    evaluate,
)
from record_formats import format_b_sections_glossed
from run_gate import PLANTED_CASE, _make_call
from run_live_ab import _load_dotenv, load_cases, make_claude_model_fn


def main() -> None:
    ap = argparse.ArgumentParser(description="Live QA-monitor injection eval (Path A)")
    ap.add_argument("--cases", choices=["planted", "nhanes"], default="planted")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--executor-model", default="claude-opus-4-8")
    ap.add_argument("--monitor-model", default="claude-opus-4-8")
    ap.add_argument("--blind-model", default="claude-opus-4-8")   # SAME as monitor for fairness
    ap.add_argument("--judge-model", default="claude-sonnet-5")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "qa_monitor_report.json"))
    args = ap.parse_args()

    _load_dotenv()
    import anthropic
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set.")
    anthropic.Anthropic()  # fail fast if the SDK/key is unusable

    cases = [PLANTED_CASE] if args.cases == "planted" else load_cases("nhanes", args.n, None)

    executor = make_claude_model_fn(args.executor_model)
    import anthropic as _a
    client = _a.Anthropic()
    monitor_fn = _make_call(client, args.monitor_model, MONITOR_SYSTEM, "monitor", MONITOR_TOOL)
    blind_fn = _make_call(client, args.blind_model, BLIND_READ_SYSTEM, "blind_review", MONITOR_TOOL)
    judge_fn = _make_call(client, args.judge_model, MATCH_JUDGE_SYSTEM, "match", MATCH_JUDGE_TOOL)

    injected, controls = [], []
    for rec in cases:
        case_input = format_b_sections_glossed(rec)
        clean = executor(case_input)
        controls.append({"input": case_input, "output": clean})
        for row in inject_all(clean, rec):
            injected.append({"input": case_input, "output": row["corrupted_output"],
                             "label": row["label"]})

    report = evaluate(
        injected, controls,
        monitor_detect=lambda i, o: detect(monitor_fn, i, o),
        blind_detect=lambda i, o: detect(blind_fn, i, o),
        judge_caught=lambda dets, label: caught(judge_fn, dets, label),
    )
    report["meta"] = {"cases": args.cases, "n_cases": len(cases),
                      "executor": args.executor_model, "monitor": args.monitor_model,
                      "blind": args.blind_model, "judge": args.judge_model}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"injected={report['n_injected']} controls={report['n_controls']}")
    print(f"monitor_recall={report['monitor_recall']:.2f}  blind_recall={report['blind_recall']:.2f}"
          f"  delta={report['recall_delta_mean']:+.2f}  CI90={report['ci_90_monitor_minus_blind']}")
    print(f"control FP: monitor={report['control_fp_rate']['monitor']:.2f}"
          f"  blind={report['control_fp_rate']['blind']:.2f}")
    print("by class:", json.dumps(report["by_defect_class"]))
    print("VERDICT:", report["verdict"], "| wrote:", args.out)


if __name__ == "__main__":
    main()
