"""Stage-3 physiology — run every deepened mechanism end to end (offline, no API, no GPU).

Ties the Stage-3 modules into ONE report for a structural case, foregrounding the thesis: a single
upstream lever (the periodontal source / the shared inflammatory gain) drives EVERY axis coherently.

    inflammatory core (acute vs chronic)  ── mech_inflammation
    microbiome / keystone dysbiosis       ── mech_microbiome  → source realism
    CV atherosclerosis (foam-cell ODE)    ── mech_cv
    metabolic glucose–insulin (Bergman)   ── mech_glucose
    diabetes↔periodontitis closed loop    ── mech_metabolic.coupled_perio_metabolic
    neuro amyloid + tau (A/T), APOE4/age  ── mech_neuro

The "one lever" section shows all axes at the case's source vs after periodontal therapy (source→0),
so a reader sees the coherent multi-axis response from a single intervention. Emits JSON; pass --plot
to also render the Stage-3 figures (needs matplotlib).

NON-DIAGNOSTIC: structural bands/flags in, parameter-level ranges out — never a patient value.

Usage:  python src/run_physiology.py [--case case.json] [--plot] [--outdir .]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.mech_calibrate import calibrated_params
from histora.mech_cv import cv_plaque_centerpiece, plaque_trajectory
from histora.mech_glucose import glucose_centerpiece, glucose_response
from histora.mech_inflammation import inflammation_centerpiece, phase_trajectories
from histora.mech_metabolic import coupled_perio_metabolic, perio_metabolic_cobweb
from histora.mech_microbiome import microbiome_centerpiece
from histora.mech_models import il6_steady, inflammatory_gain, periodontal_source
from histora.mech_neuro import neuro_centerpiece, tau_front_pair
from histora.proteins import protein_registry, signaling_axis
from histora.relational_signals import case_signature

DEFAULT_CASE = {"bop_band": "high", "perio_stage": "stage III", "comorbidities": ["diabetes"],
                "apoe4": True, "age_band": "old"}


def _features(case: dict) -> dict:
    """Accept either a structural feature dict (bands/flags) or a full record (→ case signature)."""
    if "periodontal" in case or "shared_risk" in case:
        sig = case_signature(case)
        feats = {"bop_band": sig["bop_band"], "perio_stage": sig["perio_stage"],
                 "comorbidities": sig["comorbidities"]}
        for k in ("apoe4", "age_band"):
            if k in case:
                feats[k] = case[k]
        return feats
    return case


def one_lever_summary(features: dict, p: dict) -> dict:
    """The thesis in one block: every axis at the case's gain vs after therapy (source→0)."""
    gain = inflammatory_gain(il6_steady(periodontal_source(features, p), p))
    cv = cv_plaque_centerpiece(features, p)
    glu = glucose_centerpiece(features, dict(p))
    neu = neuro_centerpiece(features, p, front=False)
    return {
        "shared_inflammatory_gain_pg_ml": round(gain, 4),
        "lever": "remove the periodontal source (periodontal therapy) → gain → 0",
        "coherent_multi_axis_response_to_therapy": {
            "cardiovascular_plaque_rel_reduction": cv["counterfactual_therapy"]["plaque_rel_reduction"],
            "metabolic_hba1c_drop_pp": glu["counterfactual_therapy"]["hba1c_drop_pp"],
            "neuro_tau_onset_delay_years": neu["tau_onset_years"]["therapy_delay_years"],
            "neuro_amyloid_rel_reduction": neu["amyloid_burden"]["relative_increase"],
        },
        "axis_tier": {
            "cardiovascular": "mechanistic scaffold (Ougrinovskaia E2.6); foam-cell couplings FLAGGED & swept",
            "metabolic": "calibrated to the ~0.35 pp periodontal-therapy HbA1c anchor (Bergman E3.1)",
            "neuro": ("EXPLORATORY — genetics do NOT support the AD link causally (CRP→AD MR null; the "
                      "atuzaginstat/GAIN trial failed); inflammation→α and amyloid→α are FLAGGED hypotheses. "
                      "Absolute years are illustrative — read the delta, never the magnitude."),
        },
        "note": ("one intervention, one shared parameter → three axes respond together (not three guesses). "
                 "The neuro axis is EXPLORATORY and must not be read as a calibrated result — see axis_tier."),
    }


def physiology_report(case: dict) -> dict:
    p = calibrated_params()
    features = _features(case)
    return {
        "features": features,
        "inflammatory_core": inflammation_centerpiece(features, p),
        "microbiome_source": microbiome_centerpiece(features, p),
        "cardiovascular_plaque": cv_plaque_centerpiece(features, p),
        "metabolic_glucose": glucose_centerpiece(features, dict(p)),
        "diabetes_perio_loop": coupled_perio_metabolic(features, p),
        "neuro_amyloid_tau": neuro_centerpiece(features, p, front=True),
        "protein_layer": {"registry": protein_registry(), "signaling_axis": signaling_axis(),
                          "note": "UniProt/PDB connector data — reference IDs; live 3-D via Claude Science"},
        "one_lever_many_axes": one_lever_summary(features, p),
        "guardrail": "non-diagnostic: structural bands/flags in, parameter-level ranges out",
    }


def _trajectories(case: dict) -> dict:
    """The time-series arrays behind the Stage-3 figures (for --plot)."""
    p = calibrated_params()
    features = _features(case)
    gain = inflammatory_gain(il6_steady(periodontal_source(features, p), p))
    return {
        "plaque": plaque_trajectory(gain, p),
        "plaque_baseline": plaque_trajectory(0.0, p),
        "glucose": glucose_response(gain, p),
        "glucose_baseline": glucose_response(0.0, p),
        "inflammation_phase": phase_trajectories(p),
        "tau_front": tau_front_pair(features, p),
        "perio_cobweb": perio_metabolic_cobweb(features, p),
        "proteins": signaling_axis(),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Stage-3 physiology — all deepened mechanisms")
    ap.add_argument("--case", default=None, help="JSON file: structural features or a full record")
    ap.add_argument("--plot", action="store_true", help="render Stage-3 figures (needs matplotlib)")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()

    case = json.load(open(args.case)) if args.case else DEFAULT_CASE
    report = physiology_report(case)
    out_json = os.path.join(args.outdir, "physiology_report.json")
    with open(out_json, "w") as fh:
        json.dump(report, fh, indent=2)
    print(json.dumps(report["one_lever_many_axes"], indent=2))
    print(f"\nfull report → {out_json}")

    if args.plot:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                            "skills", "histora-mechanistic-pipeline"))
            import plot_pipeline as pp
            made = pp.plot_stage3(report, _trajectories(case), args.outdir)
            print("figures:", ", ".join(made))
        except Exception as e:  # pragma: no cover - plotting is optional
            print(f"(plotting skipped: {e})")


if __name__ == "__main__":
    main()
