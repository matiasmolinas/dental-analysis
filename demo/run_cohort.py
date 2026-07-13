"""HISTORA as a clinical-research navigator — build a research-ready cohort from a fragmented corpus.

The demo the expert reviewers asked for: a researcher arrives with a *question*; HISTORA filters the corpus
down a funnel to the eligible cohort, reports what's present and — honestly — what the data cannot answer,
and exports a preliminary protocol. **Everything shown here is REAL** (NHANES 2009-2010, the same public
corpus the paper validates on); nothing is synthetic. NHANES is cross-sectional, so the honest punchline is
that the *longitudinal* mediation question needs a longitudinal EHR this corpus does not contain — the
guardrail firing on real data.

Requires `pandas` + the NHANES 2009-2010 XPT files (a local `.nhanes/`). Non-diagnostic throughout.

    python demo/run_cohort.py            # → cohort_report.json
"""

from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.cohort import (build_funnel, cohort_completeness, integrity_checklist, preliminary_protocol)

NHANES_DIR = os.path.join(os.path.dirname(__file__), "..", ".nhanes")

QUESTION = ("Among patients with periodontitis and type-2 diabetes, does the periodontal–inflammatory "
            "(IL-6/CRP) axis track with systemic inflammation — and could periodontal therapy move it? "
            "(IL-6R blockade / tocilizumab enters only as biological plausibility, never as a treatment.)")


def _rule(t):
    return f"\n{'─' * 78}\n{t}\n{'─' * 78}"


def _load_records():
    paths = {os.path.basename(p).split(".")[0]: p for p in glob.glob(os.path.join(NHANES_DIR, "*.XPT"))}
    if not paths:
        return None
    from histora.nhanes import load_cv_table
    return load_cv_table(paths)


def main() -> None:
    records = None
    try:
        records = _load_records()
    except Exception as e:                                  # pragma: no cover - env-dependent
        print(f"(NHANES load failed: {e})")
    if not records:
        print("NHANES 2009-2010 data not found (need pandas + a local .nhanes/ with the XPT files).")
        print("This demo builds a REAL cohort funnel over that public corpus — no synthetic data.")
        return

    funnel = build_funnel(records)
    completeness = cohort_completeness(funnel["cohort"])
    protocol = preliminary_protocol(QUESTION, funnel, completeness)
    checklist = integrity_checklist(funnel, completeness)

    print(_rule("HISTORA · clinical-research navigator — from fragmented records to a research-ready cohort"))
    print("Researchers don't need another chatbot. They need an AI that builds research-ready cohorts")
    print("from fragmented clinical data. Everything below is REAL (NHANES 2009-2010) — nothing synthetic.")

    print(_rule("The question (the researcher arrives with a hypothesis, not a patient)"))
    print(f"  {QUESTION}")

    print(_rule("① Cohort funnel — real counts at each eligibility stage"))
    for s in funnel["funnel"]:
        print(f"  {s['n']:>6}   {s['stage']}")
    print(f"  → cohort ready: {funnel['cohort_n']} participants")
    print(f"  ({funnel['note']})")

    print(_rule("② Completeness — what's present, and what this corpus cannot answer"))
    for field, frac in completeness["field_present_fraction"].items():
        print(f"  present in {frac*100:5.1f}% of the cohort:  {field}")
    print("  MISSING from the corpus (cross-sectional → collection flags, never imputed):")
    for f in completeness["longitudinal_fields_absent_in_corpus"]:
        print(f"    ✗ {f}")
    print(f"\n  verdict: {completeness['verdict']}")

    print(_rule("③ HISTORA generates a hypothesis — not a conclusion"))
    print("  A cross-sectional cohort with sufficient data to study the periodontal→CRP edge was assembled;")
    print("  it is consistent with the IL-6R Mendelian-randomization evidence (plausibility, not proof),")
    print("  but is INSUFFICIENT to establish a causal or longitudinal effect. The neuro axis stays")
    print("  EXPLORATORY and is not part of this cohort's conclusions.")

    print(_rule("④ Research-integrity — what the cohort can and cannot support"))
    for c in checklist:
        print(f"  {'✓' if c['ok'] else '✗'} {c['label']}")

    print(_rule("⑤ Export — a preliminary protocol (prepares the study; is NOT the study)"))
    print(f"  {protocol['header']}")
    print(f"  inclusion: {'; '.join(protocol['inclusion_criteria'])}")
    print(f"  variables: {', '.join(protocol['primary_variables'])}")
    print("  limitations:")
    for lim in protocol["limitations"]:
        print(f"    · {lim}")

    report = {"question": QUESTION, "funnel": funnel["funnel"], "cohort_n": funnel["cohort_n"],
              "completeness": completeness, "integrity_checklist": checklist, "protocol": protocol}
    out = os.path.join(os.path.dirname(__file__), "cohort_report.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nwrote: {out}")

    if "--plot" in sys.argv:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills",
                                            "histora-mechanistic-pipeline"))
            import plot_pipeline as pp
            outdir = os.path.dirname(out)
            print("figure:", pp.plot_cohort(report, os.path.join(outdir, "fig_cohort_funnel.png")))
        except Exception as e:                             # pragma: no cover - plotting optional
            print(f"(plot skipped: {e})")
    print("\nNON-DIAGNOSTIC · population-level · hypothesis-generation only · MR ≠ RCT · calibration ≠ validation.")


if __name__ == "__main__":
    main()
