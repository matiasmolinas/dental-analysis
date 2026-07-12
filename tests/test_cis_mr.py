"""Tests for LD-aware cis-MR (correlated IVW) — pure/offline, injected fetches, no network.

Run:  python tests/test_cis_mr.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.cis_mr import CIS_CONFIG, align_ld_signs, correlated_ivw, run_cis_mr
from histora.mendelian_randomization import Instrument


def _insts(slope, n=4, ea="A"):
    return [Instrument(f"rs{k}", 0.10 + 0.03 * k, 0.01, slope * (0.10 + 0.03 * k), 0.006, ea=ea)
            for k in range(n)]


def test_correlated_ivw_recovers_slope_under_LD():
    # by = 0.12 * bx exactly → GLS recovers 0.12 for ANY valid correlation matrix R
    insts = _insts(0.12)
    n = len(insts)
    R = [[1.0 if a == b else 0.6 for b in range(n)] for a in range(n)]   # correlated (LD)
    res = correlated_ivw(insts, R)
    assert abs(res["estimate"] - 0.12) < 1e-3
    assert "correlated IVW" in res["method"]


def test_correlated_ivw_se_larger_than_independent():
    # positive LD should inflate the SE vs. the (wrong) independent assumption — the whole point
    insts = _insts(0.1)
    n = len(insts)
    R_ld = [[1.0 if a == b else 0.7 for b in range(n)] for a in range(n)]
    R_ind = [[1.0 if a == b else 0.0 for b in range(n)] for a in range(n)]
    assert correlated_ivw(insts, R_ld)["se"] > correlated_ivw(insts, R_ind)["se"]


def test_align_ld_signs_flips_on_allele_mismatch():
    insts = [Instrument("rsA", 0.1, 0.01, 0.01, 0.006, ea="A"),
             Instrument("rsB", 0.1, 0.01, 0.01, 0.006, ea="A")]
    R = [[1.0, 0.6], [0.6, 1.0]]
    # panel reference allele for rsB is G (!= its effect allele A) → flip rsB's row/col
    out = align_ld_signs(R, {"rsA": "A", "rsB": "G"}, insts)
    assert out[0][1] == -0.6 and out[1][0] == -0.6 and out[0][0] == 1.0
    # no mismatch → unchanged
    out2 = align_ld_signs(R, {"rsA": "A", "rsB": "A"}, insts)
    assert out2[0][1] == 0.6


def test_run_cis_mr_end_to_end_with_injected_fetches():
    snps = CIS_CONFIG["exposure"]["instruments"]
    exp_id, out_id = CIS_CONFIG["exposure"]["id"], CIS_CONFIG["outcome"]["id"]

    def fake_assoc(rsids, ids, token):
        rows = []
        for k, s in enumerate(rsids):
            be = 0.10 + 0.02 * k
            for sid in ids:
                rows.append({"rsid": s, "id": sid, "ea": "A", "nea": "G",
                             "beta": be if sid == exp_id else 0.15 * be,
                             "se": 0.01 if sid == exp_id else 0.006})
        return rows

    def fake_ld(rsids, token, pop):
        n = len(rsids)
        R = [[1.0 if a == b else 0.5 for b in range(n)] for a in range(n)]
        ref = {s: "A" for s in rsids}          # panel allele matches effect allele → no flips
        return R, ref

    rep = run_cis_mr(config=CIS_CONFIG, token="fake", fetch_assoc=fake_assoc, fetch_ld=fake_ld)
    assert rep["correlated_ivw"]["estimate"] > 0            # positive causal slope recovered
    assert "naive_ivw_for_contrast" in rep and rep["caveats"]
    assert len(rep["instruments"]) == len(snps)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
