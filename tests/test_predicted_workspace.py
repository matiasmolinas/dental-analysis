"""Tests for the circularity-gate set-logic (Phase R6, mode 4) — no API, no GPU.

Verifies the K-sample aggregation (stability + appears-in-output filtering) and the
P \\ (O ∪ C) non-redundant surface with a stub judge.

Run:  python tests/test_predicted_workspace.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from predicted_workspace import aggregate_predictions, cluster_predictions, non_redundant_surface


def _run(*keys, out=False):
    return {"items": [{"key": k, "concept": k, "appears_in_output": out} for k in keys]}


def test_aggregate_keeps_stable_and_absent():
    runs = [
        _run("amlodipine_ccb", "crp"),
        _run("amlodipine_ccb", "crp"),
        _run("amlodipine_ccb"),
        _run("amlodipine_ccb", "noise1"),
        _run("amlodipine_ccb", "crp"),
    ]  # amlodipine in 5/5 (1.0), crp in 3/5 (0.6), noise1 in 1/5 (0.2)
    agg = aggregate_predictions(runs, k=5, stability_min=0.6)
    keys = {i["key"] for i in agg}
    assert "amlodipine_ccb" in keys and "crp" in keys and "noise1" not in keys


def test_aggregate_drops_items_that_appear_in_output():
    runs = [_run("x", out=True) for _ in range(5)]  # stable but appears_in_output -> not signal
    assert aggregate_predictions(runs, k=5) == []


def test_cluster_predictions_counts_stability_per_concept():
    # same concept worded differently across 4/5 runs -> exact-key would fragment it; the
    # semantic cluster spans 4 runs -> stability 0.8 -> kept.
    runs = [
        {"items": [{"key": "amlodipine_go", "channel": "error-noticed",
                    "concept": "amlodipine gingival overgrowth", "appears_in_output": False}]},
        {"items": [{"key": "ccb_hyperplasia", "channel": "error-noticed",
                    "concept": "CCB-induced gingival hyperplasia", "appears_in_output": False}]},
        {"items": [{"key": "drug_overgrowth", "channel": "error-noticed",
                    "concept": "drug-induced overgrowth from amlodipine", "appears_in_output": False}]},
        {"items": [{"key": "amlo_gum", "channel": "error-noticed",
                    "concept": "amlodipine gum enlargement", "appears_in_output": False}]},
        {"items": [{"key": "noise", "channel": "silent-assessment",
                    "concept": "unrelated point", "appears_in_output": False}]},
    ]
    # stub cluster_fn: indices 0-3 are one cluster, 4 is its own
    def cluster_fn(_listing):
        return {"clusters": [
            {"concept": "amlodipine gingival overgrowth", "channel": "error-noticed",
             "member_indices": [0, 1, 2, 3]},
            {"concept": "unrelated point", "channel": "silent-assessment", "member_indices": [4]}]}
    kept = cluster_predictions(runs, k=5, cluster_fn=cluster_fn, stability_min=0.6)
    keys = {i["concept"] for i in kept}
    assert "amlodipine gingival overgrowth" in keys          # spans 4/5 runs -> 0.8, kept
    assert "unrelated point" not in keys                     # 1/5 -> 0.2, dropped


def test_non_redundant_surface_splits_on_judge():
    p_items = [{"key": "amlodipine_ccb", "concept": "amlodipine gingival overgrowth"},
               {"key": "crp", "concept": "hs-CRP missing"}]
    # judge says crp is covered by O/C, amlodipine is not
    def judge(_prompt):
        return {"verdicts": [{"key": "amlodipine_ccb", "covered": False, "why": "novel"},
                             {"key": "crp", "covered": True, "why": "already flagged"}]}
    res = non_redundant_surface(p_items, {"required_missing_data": [{"field": "hs_crp"}]},
                                [{"key": "crp", "concept": "crp"}], judge)
    assert res["circular"] is False and res["n_surface"] == 1
    assert res["surface"][0]["key"] == "amlodipine_ccb"


def test_empty_predictions_is_circular():
    res = non_redundant_surface([], {}, [], lambda p: {"verdicts": []})
    assert res["circular"] is True


def test_all_covered_is_circular():
    p = [{"key": "a", "concept": "a"}]
    judge = lambda _p: {"verdicts": [{"key": "a", "covered": True, "why": "in O"}]}
    res = non_redundant_surface(p, {}, [], judge)
    assert res["circular"] is True and res["n_surface"] == 0


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
