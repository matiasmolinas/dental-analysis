"""Tests for the execution-gap directive harness (W1 generalized) — pure python, no API.

Verifies the pre-A/B predictor classifies candidates correctly, the stated-but-dropped test plumbs
the flags, and the 3-arm A/B measures the effect and classifies the pattern (execution_gap vs
knowledge_gap vs screened) — all with stubs. The execution_gap case reproduces W1's signature:
enforced > prose > base.

Run:  python tests/test_exec_gap.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.exec_gap import predict_pays, run_directive_ab, stated_but_dropped


def test_predict_pays_classifies_all_cases():
    assert predict_pays(known=True, deterministic=True, dropped_in_situ=True) == "pays_execution_gap"
    assert predict_pays(known=False, deterministic=True, dropped_in_situ=False) == "pays_knowledge_gap"
    assert predict_pays(known=True, deterministic=False, dropped_in_situ=True) == "predict_null_semantic"
    assert predict_pays(known=True, deterministic=True, dropped_in_situ=False) == "predict_null_known_and_deployed"


def test_stated_but_dropped_flags():
    r = stated_but_dropped(
        task="case",
        state_fn=lambda: "flag every missing mediator",     # model CAN state it
        solve_fn=lambda t: {"required_missing_data": []},   # but omits it when solving
        states_check=lambda s: "missing" in s,
        deploys_check=lambda o: len(o.get("required_missing_data", [])) > 0,
    )
    assert r["known"] is True and r["deployed"] is False and r["dropped_in_situ"] is True


def _ab(base_fn, enforced_fn, prose_fn):
    recs = [{"id": i} for i in range(30)]
    return run_directive_ab(
        recs,
        base_build=lambda r: "base",
        enforced_build=lambda r: "enforced",
        prose_build=lambda r: "prose",
        eval_fn=lambda inp: {"arm": inp},
        score_fn=lambda out, rec: {"base": base_fn, "enforced": enforced_fn, "prose": prose_fn}[out["arm"]],
    )


def test_ab_execution_gap_pattern():
    # W1 signature: enforced (1.0) > prose (0.0) == base (0.0)
    rep = _ab(base_fn=0.0, enforced_fn=1.0, prose_fn=0.0)
    assert rep["helps"] is True
    assert rep["externalization_load_bearing"] is True
    assert rep["pattern"] == "execution_gap"
    assert rep["verdict"] == "adopt"


def test_ab_knowledge_gap_pattern():
    # content helped, externalization didn't: enforced ≈ prose > base
    rep = _ab(base_fn=0.0, enforced_fn=1.0, prose_fn=1.0)
    assert rep["helps"] is True
    assert rep["externalization_load_bearing"] is False
    assert rep["pattern"] == "knowledge_gap"


def test_ab_screened_pattern():
    # no effect: enforced ≈ base
    rep = _ab(base_fn=0.5, enforced_fn=0.5, prose_fn=0.5)
    assert rep["helps"] is False
    assert rep["pattern"] == "screened"
    assert rep["verdict"] == "reject"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
