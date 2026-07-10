"""Shared statistics — pure-python, no numpy/scipy dependency.

The project's significance discipline in one place: seeded bootstrap confidence intervals (the
apparatus never reports a point estimate without one) and a standardized OLS for confounder-adjusted
observational analysis. Pure-python so every test runs without a scientific stack.
"""

from __future__ import annotations

import random
from typing import Callable


def bootstrap_ci(deltas: list[float], iters: int = 2000, alpha: float = 0.10,
                 seed: int = 0) -> dict[str, float]:
    """Seeded (reproducible) bootstrap CI on the mean of paired per-item deltas. `lo>0` => a
    significant positive effect; `hi<0` => significant negative; straddling 0 => noise."""
    if not deltas:
        return {"mean": 0.0, "lo": 0.0, "hi": 0.0}
    rng = random.Random(seed)
    n = len(deltas)
    means = []
    for _ in range(iters):
        sample = [deltas[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int((alpha / 2) * iters)]
    hi = means[int((1 - alpha / 2) * iters)]
    return {"mean": round(sum(deltas) / n, 4), "lo": round(lo, 4), "hi": round(hi, 4)}


def bootstrap_ci_resample(stat_fn: Callable[[list[int]], float], n: int, iters: int = 2000,
                          alpha: float = 0.10, seed: int = 0) -> dict[str, float]:
    """Seeded percentile bootstrap CI on a statistic recomputed over a resample of row indices —
    used for observational effect sizes (e.g. an adjusted regression coefficient)."""
    rng = random.Random(seed)
    vals = []
    for _ in range(iters):
        idx = [rng.randrange(n) for _ in range(n)]
        try:
            vals.append(stat_fn(idx))
        except ValueError:
            continue  # degenerate (collinear) resample — skip
    if not vals:
        return {"mean": 0.0, "lo": 0.0, "hi": 0.0, "n_boot": 0}
    vals.sort()
    lo = vals[int((alpha / 2) * len(vals))]
    hi = vals[int((1 - alpha / 2) * len(vals))]
    point = stat_fn(list(range(n)))
    return {"mean": round(point, 4), "lo": round(lo, 4), "hi": round(hi, 4), "n_boot": len(vals)}


# --------------------------------------------------------------------------- standardized OLS
def standardize(col: list[float]) -> list[float]:
    n = len(col)
    m = sum(col) / n
    sd = (sum((x - m) ** 2 for x in col) / n) ** 0.5
    return [0.0] * n if sd == 0 else [(x - m) / sd for x in col]


def solve(A: list[list[float]], b: list[float]) -> list[float]:
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


def ols_exposure_coef(y: list[float], exposure: list[float],
                      confounders: list[list[float]]) -> float:
    """Standardized OLS: z-score everything, fit y ~ 1 + exposure + confounders, return the
    exposure coefficient (a partial slope in SD units; equals Pearson r with no confounders)."""
    zy = standardize(y)
    cols = [standardize(exposure)] + [standardize(c) for c in confounders]
    n = len(y)
    X = [[1.0] + [cols[j][i] for j in range(len(cols))] for i in range(n)]
    k = len(X[0])
    XtX = [[sum(X[r][a] * X[r][c] for r in range(n)) for c in range(k)] for a in range(k)]
    Xty = [sum(X[r][a] * zy[r] for r in range(n)) for a in range(k)]
    return solve(XtX, Xty)[1]  # exposure coefficient (index 0 is the intercept)
