"""Tests for the canonical end-to-end demo (WS3) — pure/offline.

Verifies the brief has all five stages, that the engine ships ranges (not points), and that the
guardrail holds: the stratum is bands/flags only (no raw patient value), and the missing mediator is a
collection flag.

Run:  python tests/test_demo.py
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, os.path.join(HERE, "..", "demo"))

from run_demo import build_brief  # noqa: E402

CASE = json.load(open(os.path.join(HERE, "..", "demo", "case.json")))


def test_brief_has_all_stages():
    b = build_brief(CASE, live=False)
    for key in ("structural_stratum", "missing_data_flags", "relational_hypotheses",
                "engine", "validation", "falsification", "guardrail"):
        assert key in b, f"missing brief stage: {key}"
    assert len(b["relational_hypotheses"]) >= 3
    assert len(b["falsification"]) >= 2


def test_guardrail_stratum_is_bands_only():
    b = build_brief(CASE, live=False)
    s = b["structural_stratum"]
    assert s["bop_band"] in ("low", "moderate", "high")     # a band, not a number
    assert isinstance(s["comorbidities"], list)             # names only
    # the missing hs-CRP surfaced as a collection flag, never imputed
    fields = [f["field"] for f in b["missing_data_flags"]]
    assert "hs_crp" in fields
    assert "non-diagnostic" in b["guardrail"].lower()


def test_engine_reports_ranges_not_points():
    b = build_brief(CASE, live=False)
    env = b["engine"]["ranges_over_uncertainty"]
    for out in ("crp_mg_l", "hba1c_shift_pp", "tau_alpha_rel_increase"):
        e = env[out]
        assert e["lo"] <= e["median"] <= e["hi"]            # a genuine interval
        assert e["lo"] < e["hi"]                            # non-degenerate


def test_validation_is_separate_from_calibration():
    b = build_brief(CASE, live=False)
    assert "NOT the calibration" in b["validation"]["note"]
    assert len(b["validation"]["nhanes"]) == 4 and len(b["validation"]["mendelian_randomization"]) == 2


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
