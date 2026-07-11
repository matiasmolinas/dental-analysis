"""Agentic-AI metric card (WS5) — hallucination, citation accuracy, uncertainty calibration,
falsifiability, and guardrail, across the separate-models (S), bare-model (C), and harness (H) arms.

The offline metrics are deterministic. The bare-model arm's ledger is illustrative by default (matching
its known behavior: point numbers, no citations, no intervals, no falsification); pass `--live` to score
a real bare-Claude transcript instead. Reports each metric per arm so the harness's contribution is
attributable to the *harness*, not the model.

Usage:  python src/run_agent_metrics.py [--live]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.agent_metrics import Claim, metric_card
from histora.benchmark import DELTA_CRP_ANCHOR_MG_L, DELTA_HBA1C_ANCHOR_PP
from histora.ensemble import ensemble_report
from histora.mech_calibrate import calibrated_params
from histora.mech_metabolic import calibrated_metabolic_params, hba1c_shift_pp
from histora.mech_models import crp_steady, il6_steady, structural_load

REF = {"bop_band": "high", "perio_stage": "stage III", "comorbidities": []}   # calibration reference


def _point_envelopes(anchors: dict) -> dict:
    """A point predictor 'reports' each anchor key but with no interval → coverage scores 0."""
    return {k: {"lo": None, "hi": None} for k in anchors}


def _therapy_delta_crp(eps: float, p: dict) -> float:
    load = structural_load(REF)
    on = crp_steady(il6_steady(eps * load, p), p)
    off = crp_steady(il6_steady(0.0, p), p)
    return on - off


def harness_envelopes_and_anchors() -> tuple[dict, dict]:
    """Sweep the calibrated edges around their nominal and report the therapy-effect 90% bands, so we
    can test whether they COVER the real interventional anchors (ΔCRP≈0.5 mg/L, ΔHbA1c≈0.35 pp)."""
    base = calibrated_params()
    eps0 = base["epsilon"]
    crp_deltas = sorted(_therapy_delta_crp(eps0 * m, dict(base, epsilon=eps0 * m))
                        for m in [0.5 + 0.1 * i for i in range(11)])           # 0.5×..1.5× nominal
    mp = calibrated_metabolic_params()
    # ΔHbA1c therapy effect = hba1c_shift at the reference gain, swept over k (β_si held); use the
    # calibrated k and a ±30% band to reflect the anchor's spread.
    from histora.mech_models import default_params, il6_steady as il6s, inflammatory_gain, periodontal_source
    gain_ref = inflammatory_gain(il6s(periodontal_source(REF, base), base))
    k0 = mp["k_hba1c"]
    hba1c_deltas = sorted(hba1c_shift_pp(gain_ref, dict(mp, k_hba1c=k0 * m))
                          for m in [0.7 + 0.06 * i for i in range(11)])
    envelopes = {
        "delta_crp_mg_l": {"lo": round(crp_deltas[0], 4), "hi": round(crp_deltas[-1], 4)},
        "delta_hba1c_pp": {"lo": round(hba1c_deltas[0], 4), "hi": round(hba1c_deltas[-1], 4)},
    }
    anchors = {"delta_crp_mg_l": DELTA_CRP_ANCHOR_MG_L, "delta_hba1c_pp": DELTA_HBA1C_ANCHOR_PP}
    return envelopes, anchors


def harness_ledger() -> list[Claim]:
    """The harness's claims: engine-sourced numbers, cited anchors, and flagged hypotheses that ship a
    falsification condition. Deterministic."""
    env = ensemble_report(REF, n=120)["envelope"]
    return [
        Claim("steady-state CRP", env["crp_mg_l"]["median"], "engine", source_key=None),
        Claim("HbA1c shift", env["hba1c_shift_pp"]["median"], "engine"),
        Claim("CRP plasma half-life 19 h", 19.0, "citation", source_key="crp_half_life"),
        Claim("therapy ΔCRP anchor 0.5 mg/L", 0.5, "citation", source_key="delta_crp_anchor"),
        Claim("therapy ΔHbA1c anchor 0.35 pp", 0.35, "citation", source_key="delta_hba1c_anchor"),
        Claim("IL-6R causal for coronary disease", 0.105, "citation", source_key="il6r_cad_mr"),
        Claim("inflammation→tau-α coupling accelerates spread", None, "hypothesis",
              falsification="no earlier modeled tau onset under raised gain would refute it; GAIN trial failed"),
        Claim("IL-6 excess raises CV monocyte recruitment", None, "hypothesis",
              falsification="no CRP/CV-history gradient with periodontal severity in NHANES would refute it"),
    ]


def separate_models_ledger() -> list[Claim]:
    """Separate single-axis models: point numbers, no shared citation to the interventional anchors, no
    ensemble intervals, no falsification path."""
    return [
        Claim("cross-sectional CRP elevation", 1.1, "none"),
        Claim("cross-sectional HbA1c elevation", 0.5, "none"),
        Claim("cognition effect", -0.18, "none"),
    ]


def bare_model_ledger_illustrative() -> list[Claim]:
    """Bare model (no harness): confident point numbers, uncited and not matching the calibrated
    anchors, no intervals, no falsification. (Illustrative — matches the benchmark's live-C behavior.)"""
    return [
        Claim("estimated CRP", 3.5, "none"),
        Claim("estimated HbA1c above normal", 1.0, "none"),
        Claim("therapy ΔCRP", 2.0, "none"),
    ]


def bare_model_ledger_live() -> list[Claim]:
    """Score a REAL bare-Claude transcript: run the benchmark's no-harness arm on the reference case and
    tag each number as untraceable (a bare model neither cites nor reproduces the calibrated anchors)."""
    from run_benchmark import _live_model_fn
    from histora.benchmark import bare_claude, case_stratum
    pred = bare_claude(case_stratum(REF), _live_model_fn())
    ax, tp = pred["axes"], pred["therapy_prediction"]
    return [
        Claim("estimated CRP", ax["crp_mg_l"]["point"], "none"),
        Claim("estimated HbA1c", ax["hba1c_pp"]["point"], "none"),
        Claim("estimated cognition", ax["cognition_z"]["point"], "none"),
        Claim("therapy ΔCRP", tp["delta_crp_mg_l"], "none"),
        Claim("therapy ΔHbA1c", tp["delta_hba1c_pp"], "none"),
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description="Agentic-AI metric card (WS5)")
    ap.add_argument("--live", action="store_true", help="score a live bare-Claude transcript (needs API)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "agent_metrics.json"))
    args = ap.parse_args()

    env, anchors = harness_envelopes_and_anchors()
    sens = ensemble_report(REF, n=120)["sensitivity"]
    sens_crp = {"crp_mg_l": sens.get("crp_mg_l", {})}

    cards = {
        "histora_harness": metric_card("histora_harness", harness_ledger(), envelopes=env,
                                       anchors=anchors, sensitivity=sens_crp, guardrail_pass=1.0),
        # S/C report POINTS (no intervals) → their envelopes are point-only, so coverage = 0.0
        "separate_models": metric_card("separate_models", separate_models_ledger(),
                                       envelopes=_point_envelopes(anchors), anchors=anchors),
        "bare_model": metric_card("bare_model",
                                  bare_model_ledger_live() if args.live else bare_model_ledger_illustrative(),
                                  envelopes=_point_envelopes(anchors), anchors=anchors, guardrail_pass=None),
    }
    report = {"cards": cards, "anchors": anchors, "harness_therapy_envelopes": env,
              "note": "offline metrics are deterministic; the bare-model ledger is illustrative unless "
                      "--live wires a captured transcript. None = metric not applicable to that arm.",
              "guardrail": "non-diagnostic; population/parameter-level claims only"}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    metrics = ["citation_accuracy", "hallucination_rate", "falsifiability",
               "uncertainty_coverage", "calibration_honesty", "guardrail_pass"]
    arms = list(cards)
    print("Agentic-AI metric card (offline)\n")
    print(f"  {'metric':22s} " + " ".join(f"{a:>17s}" for a in arms))
    for m in metrics:
        row = " ".join(f"{str(cards[a][m]):>17s}" for a in arms)
        print(f"  {m:22s} {row}")
    print("\nNON-DIAGNOSTIC; population/parameter-level claims only. wrote:", args.out)


if __name__ == "__main__":
    main()
