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
        return R, ref                          # legacy 2-tuple → run_cis_mr falls back to input order

    rep = run_cis_mr(config=CIS_CONFIG, token="fake", fetch_assoc=fake_assoc, fetch_ld=fake_ld)
    assert rep["correlated_ivw"]["estimate"] > 0            # positive causal slope recovered
    assert "naive_ivw_for_contrast" in rep and rep["caveats"]
    assert len(rep["instruments"]) == len(snps)


def test_run_cis_mr_realigns_R_to_ld_server_row_order():
    # Regression for the LD row-ordering bug: the OpenGWAS /ld/matrix server re-sorts SNPs by genomic
    # position (here we model it as reversed) and labels the rows via `snplist`. run_cis_mr must realign R
    # to those labels, NOT to the input order — reindexing by input order pairs the wrong rows and (with
    # near-collinear cis SNPs) injects a spurious cross-term that near-singularizes the GLS and collapses
    # the SE. With distinct pairwise LD and a non-exact by=slope*bx, the mis-ordered R yields a different
    # estimate/SE, so this test pins the correct realignment.
    snps = CIS_CONFIG["exposure"]["instruments"][:3]                       # s0, s1, s2
    exp_id, out_id = CIS_CONFIG["exposure"]["id"], CIS_CONFIG["outcome"]["id"]
    be = {s: 0.10 + 0.03 * k for k, s in enumerate(snps)}
    dev = {snps[0]: 0.0, snps[1]: 0.012, snps[2]: -0.009}                  # break exactness → est depends on R
    bo = {s: 0.15 * be[s] + dev[s] for s in snps}
    ld = {frozenset({snps[0], snps[1]}): 0.8,                              # distinct pairwise LD
          frozenset({snps[0], snps[2]}): 0.2,
          frozenset({snps[1], snps[2]}): 0.5}

    def Rmat(order):
        return [[1.0 if a == b else ld[frozenset({order[a], order[b]})]
                 for b in range(len(order))] for a in range(len(order))]

    def fake_assoc(rsids, ids, token):
        return [{"rsid": s, "id": sid, "ea": "A", "nea": "G",
                 "beta": be[s] if sid == exp_id else bo[s],
                 "se": 0.01 if sid == exp_id else 0.006}
                for s in snps for sid in ids]

    server_order = list(reversed(snps))                                   # server returns a REORDERED matrix
    def fake_ld(rsids, token, pop):
        return Rmat(server_order), {s: "A" for s in server_order}, list(server_order)

    rep = run_cis_mr(config=CIS_CONFIG, token="fake", fetch_assoc=fake_assoc, fetch_ld=fake_ld)

    # ground truth: instruments in harmonize (input) order, R aligned to THAT order
    insts = [Instrument(s, be[s], 0.01, bo[s], 0.006, ea="A") for s in snps]
    truth = correlated_ivw(insts, Rmat(snps))
    buggy = correlated_ivw(insts, Rmat(server_order))                     # what the input-order bug produced
    assert truth["se"] != buggy["se"]                                     # the scenario truly exercises the bug
    assert rep["correlated_ivw"]["estimate"] == truth["estimate"]         # realigned, not buggy
    assert rep["correlated_ivw"]["se"] == truth["se"]
    assert rep["n_instruments_ld"] == 3


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
