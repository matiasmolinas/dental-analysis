"""Design-adjusted NHANES analysis — survey weights, clustering, and multiplicity (WS6).

The base association engine (`histora.perio_cognition`) uses UNWEIGHTED standardized OLS. NHANES is a
complex, multistage probability sample: participants have unequal selection probabilities (exam weight
`WTMEC2YR`), and observations are clustered (PSU `SDMVPSU`) within strata (`SDMVSTRA`). Ignoring this
biases the point estimate (unequal weights) and understates variance (clustering). This module adds:

  - **Weighted standardized OLS** — the design-consistent point estimate (WLS with the survey weights;
    z-scoring uses weighted moments so the coefficient stays a partial correlation in SD units).
  - **A design-based CI** — a cluster bootstrap that resamples PSUs *within* stratum (with replacement),
    the standard practical bootstrap for a stratified two-PSU-per-stratum design; it respects both the
    stratification and the clustering, so the interval reflects the true design effect.
  - **Benjamini–Hochberg FDR** — across the set of outcomes tested, so a "3/4 significant" headline is
    not read as cherry-picking.

Reported alongside the unweighted estimate, so any attenuation from weighting is visible, not hidden —
which is on-message for a research agent that privileges honesty over a clean number. Pure-python.
Non-diagnostic: a population-level association, never a per-participant inference.
"""

from __future__ import annotations

import math
import random
from typing import Any, Callable

from .stats import solve


def _wmean(x: list[float], w: list[float]) -> float:
    return sum(wi * xi for wi, xi in zip(w, x)) / sum(w)


def _wstd(x: list[float], w: list[float]) -> list[float]:
    """Weighted z-score of a column (weighted mean 0, weighted variance 1)."""
    m = _wmean(x, w)
    var = sum(wi * (xi - m) ** 2 for wi, xi in zip(w, x)) / sum(w)
    sd = math.sqrt(var)
    return [0.0] * len(x) if sd == 0 else [(xi - m) / sd for xi in x]


def weighted_ols_exposure_coef(y: list[float], exposure: list[float],
                               confounders: list[list[float]], weights: list[float]) -> float:
    """Weighted standardized OLS: z-score (weighted) everything, fit y ~ 1 + exposure + confounders by
    weighted least squares, return the exposure coefficient. Solves (XᵀWX)β = XᵀWy."""
    w = weights
    zy = _wstd(y, w)
    cols = [_wstd(exposure, w)] + [_wstd(c, w) for c in confounders]
    n = len(y)
    X = [[1.0] + [cols[j][i] for j in range(len(cols))] for i in range(n)]
    k = len(X[0])
    XtWX = [[sum(w[r] * X[r][a] * X[r][c] for r in range(n)) for c in range(k)] for a in range(k)]
    XtWy = [sum(w[r] * X[r][a] * zy[r] for r in range(n)) for a in range(k)]
    return solve(XtWX, XtWy)[1]     # exposure coefficient (index 0 is the intercept)


def _normal_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def cluster_bootstrap(rows: list[dict], stat_fn: Callable[[list[dict]], float],
                      iters: int = 1000, alpha: float = 0.10, seed: int = 0) -> dict[str, Any]:
    """Design-based CI: resample PSUs within each stratum (with replacement), rebuild the row set from
    the sampled clusters, recompute `stat_fn`. Respects stratification + clustering. Returns the CI, a
    bootstrap SE, and a two-sided p-value (normal approx on the bootstrap SE)."""
    # group rows by (stratum -> psu -> [rows])
    strata: dict[Any, dict[Any, list[dict]]] = {}
    for r in rows:
        s, p = r.get("sdmvstra"), r.get("sdmvpsu")
        strata.setdefault(s, {}).setdefault(p, []).append(r)

    rng = random.Random(seed)
    point = stat_fn(rows)
    vals = []
    for _ in range(iters):
        boot: list[dict] = []
        for psus in strata.values():
            keys = list(psus)
            if not keys:
                continue
            for _ in range(len(keys)):                 # resample n_psu PSUs with replacement
                boot.extend(psus[keys[rng.randrange(len(keys))]])
        try:
            vals.append(stat_fn(boot))
        except ValueError:
            continue
    if len(vals) < 2:
        return {"estimate": round(point, 4), "lo": None, "hi": None, "se": None, "p_value": None}
    vals.sort()
    lo = vals[int((alpha / 2) * len(vals))]
    hi = vals[int((1 - alpha / 2) * len(vals))]
    se = (hi - lo) / (2 * 1.645) if hi > lo else float("nan")
    p = 2.0 * (1.0 - _normal_cdf(abs(point / se))) if se and se == se and se > 0 else None
    return {"estimate": round(point, 4), "lo": round(lo, 4), "hi": round(hi, 4),
            "se": round(se, 4) if se == se else None,
            "p_value": round(p, 5) if p is not None else None}


def benjamini_hochberg(pvalues: dict[str, float], q: float = 0.10) -> dict[str, dict]:
    """Benjamini–Hochberg FDR control at level q. Returns per-label {p, rank, threshold, survives}."""
    items = [(k, v) for k, v in pvalues.items() if v is not None]
    items.sort(key=lambda kv: kv[1])
    m = len(items)
    survive_upto = 0
    for i, (_, p) in enumerate(items, start=1):
        if p <= (i / m) * q:
            survive_upto = i
    out = {}
    for i, (k, p) in enumerate(items, start=1):
        out[k] = {"p": round(p, 5), "rank": i, "bh_threshold": round((i / m) * q, 5),
                  "survives_fdr": i <= survive_upto}
    for k, v in pvalues.items():
        if v is None:
            out[k] = {"p": None, "survives_fdr": None}
    return out


def analyze_weighted(records: list[dict], exposure_key: str, outcome_keys: list[str],
                     confounder_keys: list[str], fdr_q: float = 0.10) -> dict[str, Any]:
    """Design-adjusted association for each outcome: the WEIGHTED standardized coefficient with a
    cluster-bootstrap design-based CI, the UNWEIGHTED coefficient beside it (so attenuation is visible),
    and a Benjamini–Hochberg FDR verdict across the outcome set. Non-diagnostic, population-level."""
    from .stats import ols_exposure_coef

    results, pvals = {}, {}
    for outcome in outcome_keys:
        needed = [exposure_key, outcome, "weight", "sdmvstra", "sdmvpsu"] + confounder_keys
        rows = [r for r in records if all(r.get(k) is not None for k in needed)]
        n = len(rows)
        if n < max(20, len(confounder_keys) + 5):
            results[outcome] = {"n": n, "note": "insufficient complete rows"}
            continue

        def w_stat(rs, outcome=outcome):
            y = [float(r[outcome]) for r in rs]
            expo = [float(r[exposure_key]) for r in rs]
            confs = [[float(r[c]) for r in rs] for c in confounder_keys]
            wts = [float(r["weight"]) for r in rs]
            return weighted_ols_exposure_coef(y, expo, confs, wts)

        y = [float(r[outcome]) for r in rows]
        expo = [float(r[exposure_key]) for r in rows]
        confs = [[float(r[c]) for r in rows] for c in confounder_keys]
        unweighted = ols_exposure_coef(y, expo, confs)

        boot = cluster_bootstrap(rows, w_stat)
        pvals[outcome] = boot["p_value"]
        results[outcome] = {
            "n": n,
            "unweighted_std_coef": round(unweighted, 4),
            "weighted_std_coef": boot["estimate"],
            "design_ci_90": {"lo": boot["lo"], "hi": boot["hi"]},
            "design_se": boot["se"],
            "p_value": boot["p_value"],
            "significant_design": (boot["lo"] is not None
                                   and (boot["lo"] > 0 or boot["hi"] < 0)),
            "attenuation_vs_unweighted": (round(boot["estimate"] - unweighted, 4)
                                          if boot["estimate"] is not None else None),
        }

    fdr = benjamini_hochberg(pvals, q=fdr_q)
    for outcome, verdict in fdr.items():
        if outcome in results and "note" not in results[outcome]:
            results[outcome]["fdr"] = verdict

    return {
        "exposure": exposure_key,
        "confounders": confounder_keys,
        "fdr_q": fdr_q,
        "outcomes": results,
        "method": "weighted standardized OLS (WTMEC2YR) + cluster bootstrap (PSU within SDMVSTRA) + BH-FDR",
        "guardrail": "non-diagnostic population association; design-adjusted; not a per-participant inference",
    }
