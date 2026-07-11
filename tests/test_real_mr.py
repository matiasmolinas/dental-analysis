"""Tests for the real (OpenGWAS) Mendelian-randomization pipeline — pure/offline (mock fetch, no network).

Verifies harmonization (effect-allele alignment + flipping), that an injected fetch feeds the tested
estimator, and that a missing token fails cleanly. No network, no real token.

Run:  python tests/test_real_mr.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.real_mr import DEFAULT_CONFIG, harmonize, run_real_mr


def test_harmonize_aligns_and_flips_effect_allele():
    # SNP1: alleles match → keep; SNP2: effect allele swapped → outcome beta must flip sign;
    # SNP3: allele mismatch → dropped; SNP4: missing from outcome → dropped.
    exposure = [
        {"rsid": "rs1", "ea": "A", "nea": "G", "beta": 0.10, "se": 0.01},
        {"rsid": "rs2", "ea": "T", "nea": "C", "beta": 0.20, "se": 0.02},
        {"rsid": "rs3", "ea": "A", "nea": "G", "beta": 0.15, "se": 0.02},
        {"rsid": "rs4", "ea": "A", "nea": "G", "beta": 0.15, "se": 0.02},
    ]
    outcome = [
        {"rsid": "rs1", "ea": "A", "nea": "G", "beta": 0.010, "se": 0.005},
        {"rsid": "rs2", "ea": "C", "nea": "T", "beta": 0.030, "se": 0.006},   # swapped → flip to -0.030
        {"rsid": "rs3", "ea": "A", "nea": "T", "beta": 0.020, "se": 0.006},   # mismatch → drop
    ]
    insts = harmonize(exposure, outcome)
    by = {i.snp: i for i in insts}
    assert set(by) == {"rs1", "rs2"}                      # rs3 (mismatch) + rs4 (missing) dropped
    assert by["rs1"].beta_outcome == 0.010
    assert abs(by["rs2"].beta_outcome - (-0.030)) < 1e-9  # flipped


def test_run_real_mr_with_injected_fetch():
    # a fake OpenGWAS: exposure betas ~0.1..0.2, outcome = 0.1*exposure (a real positive causal slope)
    snps = DEFAULT_CONFIG["exposure"]["instruments"]
    exp_id = DEFAULT_CONFIG["exposure"]["id"]

    def fake_fetch(rsids, ids, token):
        rows = []
        for k, snp in enumerate(rsids):
            be = 0.10 + 0.02 * k
            for sid in ids:
                beta = be if sid == exp_id else 0.10 * be
                rows.append({"rsid": snp, "id": sid, "ea": "A", "nea": "G",
                             "beta": beta, "se": 0.01 if sid == exp_id else 0.006})
        return rows

    rep = run_real_mr(config=DEFAULT_CONFIG, token="fake", fetch=fake_fetch)
    assert rep["source"].startswith("OpenGWAS")
    first = next(iter(rep["outcomes"].values()))
    assert first["n_instruments"] == len(snps)
    assert first["ivw"]["estimate"] > 0 and first["ivw"]["p_value"] < 0.05   # recovers the causal slope


def test_missing_token_fails_cleanly():
    saved = os.environ.pop("OPENGWAS_JWT", None)
    try:
        raised = False
        try:
            run_real_mr()                                 # no token, no injected fetch
        except SystemExit:
            raised = True
        assert raised
    finally:
        if saved is not None:
            os.environ["OPENGWAS_JWT"] = saved


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
