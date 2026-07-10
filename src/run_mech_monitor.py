# EXPERIMENTAL — the Phase 2 fair lens re-test (docs/MECHANISTIC_HARNESS_PLAN.md); result TBD
"""Live fair-lens re-test on the mechanistic task (Phase 2) — Claude only.

For each structural case: derive the correct mechanistic answer + one labeled mechanistic defect per
class (mech_defects, checkable against the calibrated centerpiece) + keep the correct answer as a
clean control. Three reader arms — blind / reasoning_monitor / model_grounded — read every
(case, answer[, reference]); a Sonnet judge decides whether each read caught the planted defect.
Headline: reasoning_monitor − blind (lens thesis) and model_grounded − blind (harness thesis).

Roles: all three readers = Opus (fairness); judge = Sonnet. The model_grounded arm additionally
receives the centerpiece's numeric predictions as an oracle. Everything on Claude.

Usage:  python src/run_mech_monitor.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from mech_calibrate import calibrated_params
from mech_defects import inject_all_mechanistic
from mech_monitor import (
    MECH_BLIND_SYSTEM,
    MECH_GROUNDED_SYSTEM,
    MECH_MONITOR_SYSTEM,
    detect_mech,
    evaluate_mech,
)
from qa_monitor import MATCH_JUDGE_SYSTEM, MATCH_JUDGE_TOOL, MONITOR_TOOL, caught
from run_gate import _make_call
from run_live_ab import _load_dotenv


def _strata() -> list[dict]:
    base = {"perio_stage": "stage III"}
    return [
        {"bop_band": "low", "comorbidities": [], **base},
        {"bop_band": "moderate", "comorbidities": [], **base},
        {"bop_band": "high", "comorbidities": [], **base},
        {"bop_band": "high", "comorbidities": ["diabetes"], **base},
        {"bop_band": "high", "comorbidities": ["diabetes", "smoking"], "perio_stage": "stage IV"},
    ]


def _case_text(features: dict) -> str:
    return ("Structural periodontal case (non-diagnostic bands): "
            + json.dumps({k: features[k] for k in features}))


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 2 fair lens re-test (mechanistic, 3-arm)")
    ap.add_argument("--reader-model", default="claude-opus-4-8")
    ap.add_argument("--judge-model", default="claude-sonnet-5")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "mech_monitor_report.json"))
    args = ap.parse_args()

    _load_dotenv()
    import anthropic
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set.")
    client = anthropic.Anthropic()

    p = calibrated_params()  # calibrate ε once (offline)

    blind = _make_call(client, args.reader_model, MECH_BLIND_SYSTEM, "review", MONITOR_TOOL)
    monitor = _make_call(client, args.reader_model, MECH_MONITOR_SYSTEM, "audit", MONITOR_TOOL)
    grounded = _make_call(client, args.reader_model, MECH_GROUNDED_SYSTEM, "audit_grounded", MONITOR_TOOL)
    judge = _make_call(client, args.judge_model, MATCH_JUDGE_SYSTEM, "match", MATCH_JUDGE_TOOL)

    arms = {
        "blind": lambda ct, ans, ref: detect_mech(blind, ct, ans, None),
        "reasoning_monitor": lambda ct, ans, ref: detect_mech(monitor, ct, ans, None),
        "model_grounded": lambda ct, ans, ref: detect_mech(grounded, ct, ans, ref),
    }

    injected, controls = [], []
    for feat in _strata():
        bundle = inject_all_mechanistic(feat, p)
        ct = _case_text(feat)
        controls.append({"case_text": ct, "answer": bundle["correct"], "reference": bundle["reference"]})
        for row in bundle["injected"]:
            injected.append({"case_text": ct, "answer": row["corrupted_answer"],
                             "label": row["label"], "reference": bundle["reference"]})

    report = evaluate_mech(injected, controls, arms,
                           judge_caught=lambda dets, label: caught(judge, dets, label))
    report["meta"] = {"reader": args.reader_model, "judge": args.judge_model, "n_cases": 5}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"injected={report['n_injected']} controls={report['n_controls']}")
    print("recall:", json.dumps(report["recall"]))
    print("control FP:", json.dumps(report["control_fp_rate"]))
    print("Δ vs blind:", json.dumps(report["deltas_vs_blind"]))
    print("LENS thesis (reasoning_monitor):", report["lens_thesis_reasoning_monitor"])
    print("HARNESS thesis (model_grounded):", report["harness_thesis_model_grounded"])
    print("wrote:", args.out)


if __name__ == "__main__":
    main()
