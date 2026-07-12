"""Tests for the HISTORA mechanistic pipeline skill — pure/offline.

Verifies the runner computes the deterministic prediction block from a structural case (finding the
pinned engine via the local repo), that the guardrail holds, and that the plotting functions run when
matplotlib is available (skipped otherwise).

Run:  python tests/test_pipeline_skill.py
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(__file__)
SKILL = os.path.join(HERE, "..", "skills", "histora-mechanistic-pipeline")
sys.path.insert(0, os.path.abspath(SKILL))

import run_pipeline  # noqa: E402


def test_compute_returns_nondiagnostic_ranges():
    p = run_pipeline.compute(run_pipeline.DEFAULT_CASE)
    for key in ("structural_stratum", "systemic", "cardiovascular", "metabolic", "neuro",
                "counterfactuals", "ranges_over_uncertainty", "guardrail"):
        assert key in p, f"missing {key}"
    assert "non-diagnostic" in p["guardrail"].lower()
    # the stratum is bands/flags only (no raw patient value)
    assert p["structural_stratum"]["bop_band"] in ("low", "moderate", "high")


def test_ranges_are_genuine_intervals():
    p = run_pipeline.compute(run_pipeline.DEFAULT_CASE)
    env = p["ranges_over_uncertainty"]
    for out in ("crp_mg_l", "hba1c_shift_pp", "tau_alpha_rel_increase"):
        e = env[out]
        assert e["lo"] <= e["median"] <= e["hi"]
    # the flagged neuro coupling should be MORE uncertain (wider relative band) than calibrated CRP
    def relwidth(o):
        e = env[o]
        return (e["hi"] - e["lo"]) / e["median"] if e["median"] else 0.0
    assert relwidth("tau_alpha_rel_increase") > relwidth("crp_mg_l")


def test_plot_functions_when_matplotlib_present(tmpdir="/tmp"):
    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print("  (matplotlib absent — plot test skipped)")
        return
    import plot_pipeline
    p = run_pipeline.compute(run_pipeline.DEFAULT_CASE)
    out = os.path.join(tmpdir, "test_fig_envelopes.png")
    path = plot_pipeline.plot_envelopes(p, out)
    assert os.path.exists(path) and os.path.getsize(path) > 1000


def test_plot_mr_handles_both_report_shapes(tmpdir="/tmp"):
    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print("  (matplotlib absent — MR plot test skipped)")
        return
    import plot_pipeline
    # real_mr shape: nested under `outcomes`, with per-SNP instruments + egger pleiotropy flag
    real = {"exposure": "CRP", "outcomes": {"T2D": {
        "outcome": "T2D", "exposure": "CRP", "n_instruments": 3,
        "instruments": [{"snp": f"rs{k}", "beta_exposure": 0.1 + 0.05 * k, "se_exposure": 0.01,
                         "beta_outcome": -0.005 + 0.003 * k, "se_outcome": 0.007} for k in range(3)],
        "ivw": {"estimate": -0.01, "p_value": 0.6},
        "mr_egger": {"slope": -0.02, "intercept": 0.004, "pleiotropy_flagged": True}}}}
    illustrative = {"pairA": {"exposure": "IL6R", "outcome": "CAD",
                              "ivw": {"estimate": 0.105, "p_value": 0.001}}}
    assert len(plot_pipeline._mr_panels(real)) == 1
    assert len(plot_pipeline._mr_panels(illustrative)) == 1
    for name, rep in (("real", real), ("illustrative", illustrative)):
        path = plot_pipeline.plot_mr(rep, os.path.join(tmpdir, f"test_fig_mr_{name}.png"))
        assert os.path.exists(path) and os.path.getsize(path) > 1000


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
