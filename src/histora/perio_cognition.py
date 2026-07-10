"""Periodontitis ↔ cognition association engine (Phase 3, Track 2) — pure python, no deps.

The empirical anchor for the neuro axis: does higher periodontal severity track with LOWER cognitive
scores across NHANES 2011-2012 participants, adjusting for the dominant confounders (age, education,
smoking, HbA1c)? This is a **population-level ASSOCIATION**, non-diagnostic and hypothesis-generating
— NOT a per-participant diagnosis and NOT a measured causal chain (the inflammation mediator that
mech_neuro models is not in-cycle with cognition; see histora.nhanes caveats). The mechanistic model
proposes the WHY; this measures WHETHER the association the model predicts is present in real data.

Standardized OLS (z-scored variables → the exposure coefficient is a partial correlation-like effect
size in SD units) with a seeded bootstrap CI — the project's significance discipline (`histora.stats`),
here for observational data. Pure-python so it is testable without numpy/scipy; the NHANES loader
(pandas) feeds it plain floats.
"""

from __future__ import annotations

from typing import Any

from .stats import bootstrap_ci_resample, ols_exposure_coef


# --------------------------------------------------------------------------- the analysis
def analyze(records: list[dict], exposure_key: str, outcome_keys: list[str],
            confounder_keys: list[str]) -> dict[str, Any]:
    """For each cognitive outcome: crude and confounder-adjusted standardized association with the
    periodontal exposure, plus a bootstrap 90% CI on the adjusted effect. Uses only rows with all
    needed fields present. A NEGATIVE coefficient = worse cognition with higher periodontal severity
    (the direction the mechanistic model predicts). Non-diagnostic, population-level."""
    results = {}
    for outcome in outcome_keys:
        needed = [exposure_key, outcome] + confounder_keys
        rows = [r for r in records if all(r.get(k) is not None for k in needed)]
        n = len(rows)
        if n < max(10, len(confounder_keys) + 3):
            results[outcome] = {"n": n, "note": "insufficient complete rows"}
            continue
        expo = [float(r[exposure_key]) for r in rows]
        y = [float(r[outcome]) for r in rows]
        confs = [[float(r[c]) for r in rows] for c in confounder_keys]

        crude = ols_exposure_coef(y, expo, [])
        adjusted = ols_exposure_coef(y, expo, confs)

        def stat(idx, y=y, expo=expo, confs=confs):
            return ols_exposure_coef([y[i] for i in idx], [expo[i] for i in idx],
                                     [[c[i] for i in idx] for c in confs])

        ci = bootstrap_ci_resample(stat, n)
        results[outcome] = {
            "n": n,
            "crude_std_coef": round(crude, 4),
            "adjusted_std_coef": round(adjusted, 4),
            "ci_90_adjusted": {"lo": ci["lo"], "hi": ci["hi"]},
            "significant": ci["lo"] > 0 or ci["hi"] < 0,
            "direction": ("worse_cognition_with_more_perio" if adjusted < 0
                          else "better_cognition_with_more_perio" if adjusted > 0 else "none"),
        }
    return {
        "exposure": exposure_key,
        "confounders": confounder_keys,
        "outcomes": results,
        "guardrail": "non-diagnostic population association; not a per-participant inference",
    }
