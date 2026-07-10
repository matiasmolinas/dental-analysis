"""Periodontitis ↔ cognition association engine (Phase 3, Track 2) — pure python, no deps.

The empirical anchor for the neuro axis: does higher periodontal severity track with LOWER cognitive
scores across NHANES 2011-2012 participants, adjusting for the dominant confounders (age, education,
smoking, HbA1c)? This is a **population-level ASSOCIATION**, non-diagnostic and hypothesis-generating
— NOT a per-participant diagnosis and NOT a measured causal chain (the inflammation mediator that
mech_neuro models is not in-cycle with cognition; see nhanes_mapping caveats). The mechanistic model
proposes the WHY; this measures WHETHER the association the model predicts is present in real data.

Standardized OLS (z-scored variables → the exposure coefficient is a partial correlation-like effect
size in SD units) with a seeded bootstrap CI — the project's significance discipline (ablation.py),
here for observational data. Pure-python linear algebra so it is testable without numpy/scipy; the
NHANES loader (pandas) feeds it plain floats.
"""

from __future__ import annotations

import random
from typing import Any, Callable


# --------------------------------------------------------------------------- pure-python linear algebra
def _standardize(col: list[float]) -> list[float]:
    n = len(col)
    m = sum(col) / n
    var = sum((x - m) ** 2 for x in col) / n
    sd = var ** 0.5
    return [0.0] * n if sd == 0 else [(x - m) / sd for x in col]


def _solve(A: list[list[float]], b: list[float]) -> list[float]:
    """Solve A x = b by Gaussian elimination with partial pivoting (A square)."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-12:
            raise ValueError("singular design matrix (collinear predictors?)")
        M[col], M[piv] = M[piv], M[col]
        pivval = M[col][col]
        for r in range(n):
            if r != col:
                factor = M[r][col] / pivval
                M[r] = [M[r][k] - factor * M[col][k] for k in range(n + 1)]
    return [M[i][n] / M[i][i] for i in range(n)]


def _ols_exposure_coef(y: list[float], exposure: list[float],
                       confounders: list[list[float]]) -> float:
    """Standardized OLS: z-score everything, fit y ~ 1 + exposure + confounders, return the
    exposure coefficient (a partial slope in SD units; equals Pearson r when confounders is empty)."""
    zy = _standardize(y)
    cols = [_standardize(exposure)] + [_standardize(c) for c in confounders]
    n = len(y)
    X = [[1.0] + [cols[j][i] for j in range(len(cols))] for i in range(n)]  # design, intercept first
    k = len(X[0])
    XtX = [[sum(X[r][a] * X[r][c] for r in range(n)) for c in range(k)] for a in range(k)]
    Xty = [sum(X[r][a] * zy[r] for r in range(n)) for a in range(k)]
    beta = _solve(XtX, Xty)
    return beta[1]  # exposure coefficient (index 0 is the intercept)


# --------------------------------------------------------------------------- bootstrap CI
def _bootstrap_ci(stat_fn: Callable[[list[int]], float], n: int, iters: int = 2000,
                  alpha: float = 0.10, seed: int = 0) -> dict[str, float]:
    """Seeded percentile bootstrap CI on a statistic computed over a resample of row indices."""
    rng = random.Random(seed)
    vals = []
    for _ in range(iters):
        idx = [rng.randrange(n) for _ in range(n)]
        try:
            vals.append(stat_fn(idx))
        except ValueError:
            continue  # a degenerate resample (collinear) — skip
    if not vals:
        return {"mean": 0.0, "lo": 0.0, "hi": 0.0, "n_boot": 0}
    vals.sort()
    lo = vals[int((alpha / 2) * len(vals))]
    hi = vals[int((1 - alpha / 2) * len(vals))]
    point = stat_fn(list(range(n)))
    return {"mean": round(point, 4), "lo": round(lo, 4), "hi": round(hi, 4), "n_boot": len(vals)}


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

        crude = _ols_exposure_coef(y, expo, [])
        adjusted = _ols_exposure_coef(y, expo, confs)

        def stat(idx, y=y, expo=expo, confs=confs):
            return _ols_exposure_coef([y[i] for i in idx], [expo[i] for i in idx],
                                      [[c[i] for i in idx] for c in confs])

        ci = _bootstrap_ci(stat, n)
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
