"""Tests for the Phase 2 fair lens re-test (mechanistic defects + 3-arm eval) — no API.

Verifies the mechanistic injectors corrupt the right claim with a checkable label, the correct
answer is derived from the centerpiece, and evaluate_mech computes per-arm recall, deltas vs blind
with CIs, control FP, and the two separated verdicts — all with stubs.

Run:  python tests/test_mech_monitor.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mech_calibrate import calibrated_params
from mech_defects import (
    correct_answer,
    inject_all_mechanistic,
    flip_therapy_direction,
    swap_causal_node,
    break_monotonicity,
    overstate_coupling,
    false_point_certainty,
    magnitude_therapy,
    subtle_causal_attribution,
    wrong_dominant_factor,
    narrow_range,
)
from mech_monitor import evaluate_mech

P = calibrated_params()
FEAT = {"bop_band": "high", "perio_stage": "stage III", "comorbidities": []}


def _claim(answer, cid):
    return next(c["text"] for c in answer["claims"] if c["id"] == cid)


def test_correct_answer_has_five_claims_from_model():
    ans = correct_answer(FEAT, P)
    ids = {c["id"] for c in ans["claims"]}
    assert ids == {"therapy_direction", "causal_node", "monotonicity", "neuro_coupling", "crp_estimate"}
    # therapy claim reflects the model's ΔCRP>0 (therapy lowers CRP)
    assert "LOWERS" in _claim(ans, "therapy_direction")


def test_each_injector_corrupts_its_claim():
    ans = correct_answer(FEAT, P)
    out, lab = flip_therapy_direction(ans, FEAT, P)
    assert "RAISES" in _claim(out, "therapy_direction") and lab["defect_type"] == "wrong_counterfactual_direction"
    out, lab = swap_causal_node(ans, FEAT, P)
    assert "CRP is the causal" in _claim(out, "causal_node") and lab["defect_type"] == "wrong_causal_node"
    out, lab = break_monotonicity(ans, FEAT, P)
    assert "LOWERS" in _claim(out, "monotonicity") and lab["defect_type"] == "non_monotone"
    out, lab = overstate_coupling(ans, FEAT, P)
    assert "fitted causal law" in _claim(out, "neuro_coupling") and lab["defect_type"] == "overstated_coupling"
    out, lab = false_point_certainty(ans, FEAT, P)
    assert "exactly" in _claim(out, "crp_estimate") and lab["defect_type"] == "false_point_certainty"


def test_inject_all_bundle_shape():
    b = inject_all_mechanistic(FEAT, P)
    assert set(b) == {"reference", "correct", "injected"}
    assert len(b["injected"]) == 5
    assert "steady_state" in b["reference"]  # the oracle for the grounded arm


def test_subtle_injectors_are_same_direction_wrong_quantity():
    ans = correct_answer(FEAT, P)
    # therapy: same direction (LOWERS) but a wrong magnitude number
    out, lab = magnitude_therapy(ans, FEAT, P)
    assert "LOWERS" in _claim(out, "therapy_direction") and lab["defect_type"] == "magnitude_therapy"
    # causal: names TNF-α (plausible), not a blatant CRP-as-cause
    out, lab = subtle_causal_attribution(ans, FEAT, P)
    assert "TNF" in _claim(out, "causal_node") and lab["defect_type"] == "subtle_causal_attribution"
    # dominant factor: smoking above diabetes (contra the amplifier values)
    out, lab = wrong_dominant_factor(ans, FEAT, P)
    assert "smoking" in _claim(out, "monotonicity").lower() and lab["defect_type"] == "wrong_dominant_factor"
    # range: too narrow
    out, lab = narrow_range(ans, FEAT, P)
    assert "tight" in _claim(out, "crp_estimate") and lab["defect_type"] == "narrow_range"


def test_subtle_mode_uses_subtle_set():
    b = inject_all_mechanistic(FEAT, P, mode="subtle")
    types = {r["defect_type"] for r in b["injected"]}
    assert types == {"magnitude_therapy", "subtle_causal_attribution", "wrong_dominant_factor",
                     "overstated_confidence_subtle", "narrow_range"}


def test_evaluate_mech_separates_theses():
    # 5 defect classes over 2 cases = 10 injected; 2 controls.
    injected, controls = [], []
    for case in ("A", "B"):
        for dt in ("wrong_counterfactual_direction", "wrong_causal_node", "non_monotone",
                   "overstated_coupling", "false_point_certainty"):
            injected.append({"case_text": case, "answer": {"corrupt": dt},
                             "label": {"defect_type": dt}, "reference": {"ref": True}})
        controls.append({"case_text": case, "answer": {"clean": True}, "reference": {"ref": True}})

    # blind catches nothing; reasoning_monitor catches half; model_grounded catches all — no FPs.
    HARD = {"wrong_counterfactual_direction", "non_monotone"}
    arms = {
        "blind": lambda ct, ans, ref: [],
        "reasoning_monitor": lambda ct, ans, ref: (
            [{"key": "m"}] if ans.get("corrupt") in HARD else []),
        "model_grounded": lambda ct, ans, ref: ([{"key": "m"}] if ans.get("corrupt") else []),
    }
    rep = evaluate_mech(injected, controls, arms,
                        judge_caught=lambda dets, label: len(dets) > 0)
    assert rep["recall"]["blind"] == 0.0
    assert rep["recall"]["model_grounded"] == 1.0
    assert 0.0 < rep["recall"]["reasoning_monitor"] < 1.0
    assert rep["control_fp_rate"]["model_grounded"] == 0.0
    assert rep["harness_thesis_model_grounded"] == "adds_value"      # CI excludes 0
    # reasoning_monitor beats blind here too (all-or-half is a clean gap)
    assert rep["deltas_vs_blind"]["model_grounded"]["mean"] == 1.0


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
