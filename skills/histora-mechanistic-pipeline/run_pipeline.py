"""HISTORA mechanistic pipeline — the deterministic engine as a runnable pipeline-skill entrypoint.

This is the "numbers, not just framing" half of HISTORA. Given a STRUCTURAL oral-systemic case (bands
and flags only), it runs the **pinned** `histora` harness — periodontal source → IL-6 → CRP calibrated
to the interventional anchor, forked to the CV / metabolic / neuro axes, with the ensemble uncertainty
envelopes and the counterfactual levers — and writes `predictions.json`. Optionally runs the genetic
Mendelian-randomization probe and the comparative benchmark.

Determinism is the point: the math comes from versioned, unit-tested code, not from a model regenerating
it. The engine is imported if installed, else from the local repo, else pip-installed at a pinned ref —
so the same case always yields the same ranges. Non-diagnostic by construction: structural bands in,
population/parameter-level ranges out; a missing datum is a collection flag, never imputed.

Usage:
  python run_pipeline.py --case case.json           # → predictions.json
  python run_pipeline.py --mr                        # → mr_report.json (genetic causal probe)
  python run_pipeline.py --benchmark                 # → benchmark_report.json (S vs H)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

REPO = "https://github.com/matiasmolinas/dental-analysis"

# A frozen, structural demo case (bands/flags only) — the canonical "inflammatory-proxy walk".
DEFAULT_CASE = {
    "provenance": {"source": "synthetic demo case — STRUCTURAL ONLY"},
    "periodontal": {"bop_pct": 45, "diagnosis": "Stage III, Grade B periodontitis", "mean_ppd_mm": 5.2},
    "shared_risk": {"type2_diabetes": True, "smoking_active": False, "hba1c": None},
    "medical_cv": {"hs_crp": None},
}


def _ensure_histora() -> None:
    """Make the pinned `histora` package importable: installed → local repo `src/` → pip-install."""
    try:
        import histora  # noqa: F401
        return
    except ImportError:
        pass
    here = os.path.dirname(os.path.abspath(__file__))
    for up in range(2, 6):                                   # search a few levels up for the repo src/
        cand = os.path.join(here, *([".."] * up), "src")
        if os.path.isdir(os.path.join(cand, "histora")):
            sys.path.insert(0, os.path.abspath(cand))
            try:
                import histora  # noqa: F401
                return
            except ImportError:
                sys.path.pop(0)
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", f"git+{REPO}@main"], check=True)
    import histora  # noqa: F401


def compute(case: dict) -> dict:
    """Run the mechanistic harness on a structural case; return the non-diagnostic prediction block."""
    _ensure_histora()
    from histora.case_tools import case_mechanistic_predictions
    return case_mechanistic_predictions(case)


def run_mr() -> dict:
    _ensure_histora()
    from histora.mendelian_randomization import Instrument, run_mr as _run
    # the illustrative, literature-directional panels (see histora docs); estimator is exact + tested
    import importlib
    mod = importlib.import_module("run_mendelian_randomization") if _on_path("run_mendelian_randomization") else None
    if mod is not None:
        report = {}
        for key, panel in mod.PANELS.items():
            report[key] = {"exposure": panel["exposure"], "outcome": panel["outcome"],
                           **_run([Instrument(*row) for row in panel["instruments"]])}
        return report
    return {"note": "run src/run_mendelian_randomization.py from the repo for the panels"}


def run_real_mr() -> dict:
    """Real MR over public OpenGWAS summary statistics (needs OPENGWAS_JWT in the environment)."""
    _ensure_histora()
    from histora.real_mr import run_real_mr as _real
    return _real()


def run_benchmark() -> dict:
    _ensure_histora()
    from histora.benchmark import run_benchmark as _bench
    return _bench()


def _on_path(mod: str) -> bool:
    import importlib.util
    # add repo src runners dir if present
    here = os.path.dirname(os.path.abspath(__file__))
    for up in range(2, 6):
        cand = os.path.join(here, *([".."] * up), "src")
        if os.path.isdir(cand) and cand not in sys.path:
            sys.path.insert(0, os.path.abspath(cand))
    return importlib.util.find_spec(mod) is not None


def main() -> None:
    ap = argparse.ArgumentParser(description="HISTORA mechanistic pipeline")
    ap.add_argument("--case", default=None, help="path to a structural case JSON (default: demo case)")
    ap.add_argument("--mr", action="store_true", help="run the Mendelian-randomization probe")
    ap.add_argument("--real", action="store_true",
                    help="with --mr: use REAL OpenGWAS summary stats (needs OPENGWAS_JWT) instead of "
                         "the illustrative panels")
    ap.add_argument("--benchmark", action="store_true", help="run the S-vs-H benchmark")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.mr:
        out = args.out or "mr_report.json"
        json.dump(run_real_mr() if args.real else run_mr(), open(out, "w"), indent=2)
    elif args.benchmark:
        out = args.out or "benchmark_report.json"
        json.dump(run_benchmark(), open(out, "w"), indent=2)
    else:
        case = json.load(open(args.case)) if args.case else DEFAULT_CASE
        out = args.out or "predictions.json"
        json.dump(compute(case), open(out, "w"), indent=2)
    print("NON-DIAGNOSTIC: structural bands in, parameter-level ranges out. wrote:", out)


if __name__ == "__main__":
    main()
