"""Run the neuro axis end to end (Phase 3, model first) — offline, no API, no GPU.

Chains oral structural severity → systemic IL-6 gain (Phase-1 centerpiece, ε-calibrated) →
neuroinflammation → tau-spread α → tau burden / onset / connectome front, with the periodontal-
therapy counterfactual and a beta_tau sweep (the flagged coupling as a swept range). Deterministic
modeling — the tool an agent would call.

NON-DIAGNOSTIC: structural bands only; parameter-level predictions and ranges; the inflammation→α
edge is a FLAGGED hypothesis (atuzaginstat/GAIN trial failed) — not causation, not diagnosis.

Usage:  python src/run_mech_neuro.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.relational_signals import case_signature
from histora.mech_calibrate import calibrated_params
from histora.mech_neuro import neuro_centerpiece, neuro_params
from histora.record_formats import RECORD


def _features_from_record(record: dict) -> dict:
    sig = case_signature(record)
    return {"bop_band": sig["bop_band"], "perio_stage": sig["perio_stage"],
            "comorbidities": sig["comorbidities"]}


def _strata() -> list[dict]:
    base = {"perio_stage": "stage III"}
    return [
        {"label": "low BOP", **base, "bop_band": "low", "comorbidities": []},
        {"label": "high BOP", **base, "bop_band": "high", "comorbidities": []},
        {"label": "high BOP + diabetes", **base, "bop_band": "high", "comorbidities": ["diabetes"]},
        {"label": "high BOP + diabetes + smoking", "perio_stage": "stage IV", "bop_band": "high",
         "comorbidities": ["diabetes", "smoking"]},
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the neuro axis (oral→neuro chain, offline)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "mech_neuro_report.json"))
    args = ap.parse_args()

    p = neuro_params(calibrated_params())  # ε calibrated (Phase 1) + neuro constants
    grounded = {"label": "built-in NHANES-grounded case", **_features_from_record(RECORD)}
    cases = [grounded] + _strata()

    results = []
    for feat in cases:
        label = feat.pop("label")
        results.append({"label": label, **neuro_centerpiece(feat, p)})

    report = {
        "params": {k: p[k] for k in ("alpha_tau", "beta_tau", "kappa_graph", "K_gain", "bbb_gain",
                                     "N_max", "tau_seed", "tau_threshold", "horizon_years")},
        "cases": results,
        "guardrail": "non-diagnostic: structural bands only; ranges + directional predictions",
        "flags": results[0]["flags"],
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    for r in results:
        ta = r["tau_alpha"]["relative_increase"] * 100
        tb = r["tau_burden_horizon"]["relative_increase"] * 100
        delay = r["tau_onset_years"]["therapy_delay_years"]
        arr = r["connectome_front_arrival_years"]
        print(f"  {r['label']:34s} gain={r['systemic_gain_pg_ml']:5.2f}  N={r['neuroinflammation']:.3f}"
              f"  tauα+{ta:4.1f}%  burden+{tb:4.1f}%  therapyΔonset={delay}yr"
              f"  Braak={[arr[x] for x in ('entorhinal','hippocampus','neocortex')]}")
    hi = results[2]
    print(f"\nβ_tau sweep (flagged coupling) high-BOP+diabetes → tau-burden range: "
          f"{hi['tau_burden_range_over_beta']}")
    print("flags:", "; ".join(report["flags"]))
    print("wrote:", args.out)


if __name__ == "__main__":
    main()
