"""Two-sample Mendelian randomization — a genetic causal probe of the shared inflammatory proxy.

HISTORA's whole thesis rests on one assumption: that systemic inflammation (operationalized as the
IL-6 / CRP proxy) is *causal* for the downstream axes, not merely correlated. Observational NHANES can
only test the association's *direction*; Mendelian randomization (MR) tests the *causal* claim using
germline genetic variants as instruments — genotype is randomized at conception, so a variant that
raises lifelong IL-6 signaling and also raises disease risk is causal evidence, not confounding.

This module is a pure-Python two-sample MR engine (no numpy/scipy):
  - **IVW** (inverse-variance-weighted) — the primary estimate (fixed-effect through the origin).
  - **MR-Egger** — slope robust to *directional* pleiotropy, and an intercept whose deviation from 0 is
    a test *for* pleiotropy (the key MR sensitivity check).
  - **Weighted median** — consistent if ≥50% of instrument weight is valid; a second robustness lens.
  - **Cochran's Q** — instrument heterogeneity (a pleiotropy smell test).

Input is per-instrument summary statistics: (beta_exposure, se_exposure, beta_outcome, se_outcome) —
exactly what public GWAS repositories (OpenGWAS, GWAS Catalog) expose, so no individual-level data is
ever needed or touched. **Non-diagnostic:** MR estimates a *population-level causal parameter* for an
*instrument*; it never assigns genetic risk to an individual and never imputes a genotype.

The expected, honest pattern for our proxy (reproducing the established MR literature): IL-6R signaling
is causal for coronary disease (IL6R MR Consortium, *Lancet* 2012), while CRP/IL-6 → Alzheimer's is
weak/null — which *supports* HISTORA's own tiering (CV/metabolic = data-anchored; neuro = exploratory).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any


@dataclass
class Instrument:
    """One genetic instrument (SNP) aligned to the exposure-increasing allele. `ea` is that effect
    allele (optional; needed by the LD-aware cis-MR to sign-align the LD matrix)."""
    snp: str
    beta_exposure: float
    se_exposure: float
    beta_outcome: float
    se_outcome: float
    ea: str = ""


def _normal_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _two_sided_p(estimate: float, se: float) -> float:
    if se <= 0:
        return float("nan")
    z = abs(estimate / se)
    return 2.0 * (1.0 - _normal_cdf(z))


def _ci90(estimate: float, se: float) -> dict[str, float]:
    # 90% CI (z = 1.645), matching the bootstrap-CI discipline used elsewhere in the repo.
    h = 1.645 * se
    return {"lo": round(estimate - h, 4), "hi": round(estimate + h, 4)}


def ivw(instruments: list[Instrument]) -> dict[str, Any]:
    """Inverse-variance-weighted MR: weighted regression of outcome-beta on exposure-beta through the
    origin, weights = 1/se_outcome^2. The primary causal estimate."""
    num = sum(i.beta_exposure * i.beta_outcome / i.se_outcome**2 for i in instruments)
    den = sum(i.beta_exposure**2 / i.se_outcome**2 for i in instruments)
    if den == 0:
        raise ValueError("degenerate instruments (zero denominator)")
    beta = num / den
    se = math.sqrt(1.0 / den)
    # Cochran's Q heterogeneity over the per-SNP ratio estimates.
    q = sum((i.beta_exposure**2 / i.se_outcome**2) * (i.beta_outcome / i.beta_exposure - beta) ** 2
            for i in instruments)
    df = len(instruments) - 1
    return {"estimate": round(beta, 4), "se": round(se, 4), "ci_90": _ci90(beta, se),
            "p_value": round(_two_sided_p(beta, se), 5),
            "cochran_q": round(q, 3), "q_df": df,
            "q_p_value": round(1.0 - _chi2_cdf(q, df), 4) if df > 0 else None,
            "n_instruments": len(instruments)}


def mr_egger(instruments: list[Instrument]) -> dict[str, Any]:
    """MR-Egger: weighted linear regression WITH an intercept (weights = 1/se_outcome^2). The slope is
    the pleiotropy-robust causal estimate; the intercept ≠ 0 is a directional-pleiotropy test."""
    w = [1.0 / i.se_outcome**2 for i in instruments]
    x = [i.beta_exposure for i in instruments]
    y = [i.beta_outcome for i in instruments]
    n = len(instruments)
    Sw = sum(w)
    Swx = sum(w[k] * x[k] for k in range(n))
    Swy = sum(w[k] * y[k] for k in range(n))
    Swxx = sum(w[k] * x[k] ** 2 for k in range(n))
    Swxy = sum(w[k] * x[k] * y[k] for k in range(n))
    d = Sw * Swxx - Swx**2
    if d == 0:
        raise ValueError("degenerate design (collinear instruments)")
    slope = (Sw * Swxy - Swx * Swy) / d
    intercept = (Swxx * Swy - Swx * Swxy) / d
    # residual-scaled standard errors (the standard MR-Egger multiplicative random-effects scale)
    resid = [y[k] - intercept - slope * x[k] for k in range(n)]
    dof = n - 2
    sigma2 = sum(w[k] * resid[k] ** 2 for k in range(n)) / dof if dof > 0 else float("nan")
    se_slope = math.sqrt(sigma2 * Sw / d) if dof > 0 else float("nan")
    se_int = math.sqrt(sigma2 * Swxx / d) if dof > 0 else float("nan")
    return {
        "slope": round(slope, 4), "slope_se": round(se_slope, 4), "slope_ci_90": _ci90(slope, se_slope),
        "slope_p_value": round(_two_sided_p(slope, se_slope), 5),
        "intercept": round(intercept, 5), "intercept_se": round(se_int, 5),
        "intercept_p_value": round(_two_sided_p(intercept, se_int), 5),
        "pleiotropy_flagged": _two_sided_p(intercept, se_int) < 0.10,
        "n_instruments": n,
    }


def weighted_median(instruments: list[Instrument], n_boot: int = 1000, seed: int = 0) -> dict[str, Any]:
    """Weighted-median MR: consistent if ≥50% of the instrument *weight* comes from valid instruments.
    CI by seeded parametric bootstrap over the summary statistics."""
    def _wmed(betas: list[float], weights: list[float]) -> float:
        order = sorted(range(len(betas)), key=lambda k: betas[k])
        total = sum(weights)
        cum = 0.0
        for k in order:
            cum += weights[k]
            if cum >= 0.5 * total:
                return betas[k]
        return betas[order[-1]]

    ratios = [i.beta_outcome / i.beta_exposure for i in instruments]
    weights = [i.beta_exposure**2 / i.se_outcome**2 for i in instruments]
    point = _wmed(ratios, weights)

    rng = random.Random(seed)
    boots = []
    for _ in range(n_boot):
        rs, ws = [], []
        for i in instruments:
            be = rng.gauss(i.beta_exposure, i.se_exposure)
            bo = rng.gauss(i.beta_outcome, i.se_outcome)
            if be == 0:
                be = i.beta_exposure or 1e-9
            rs.append(bo / be)
            ws.append(be**2 / i.se_outcome**2)
        boots.append(_wmed(rs, ws))
    boots.sort()
    lo = boots[int(0.05 * n_boot)]
    hi = boots[min(n_boot - 1, int(0.95 * n_boot))]
    se = (hi - lo) / (2 * 1.645) if hi > lo else float("nan")
    return {"estimate": round(point, 4), "se": round(se, 4),
            "ci_90": {"lo": round(lo, 4), "hi": round(hi, 4)},
            "p_value": round(_two_sided_p(point, se), 5) if se == se and se > 0 else None,
            "n_instruments": len(instruments)}


def _chi2_cdf(x: float, k: int) -> float:
    """Regularized lower incomplete gamma P(k/2, x/2) — chi-square CDF, for Cochran's Q p-value."""
    if x <= 0 or k <= 0:
        return 0.0
    a = k / 2.0
    xh = x / 2.0
    # series expansion for the regularized lower incomplete gamma (adequate for our small df/x)
    term = 1.0 / a
    total = term
    for n in range(1, 200):
        term *= xh / (a + n)
        total += term
        if term < 1e-12 * total:
            break
    return total * math.exp(-xh + a * math.log(xh) - math.lgamma(a))


def run_mr(instruments: list[Instrument]) -> dict[str, Any]:
    """Full MR: IVW (primary) + MR-Egger (pleiotropy) + weighted median (robustness). Returns a
    verdict that requires the primary estimate to be significant AND not pleiotropy-confounded."""
    if len(instruments) < 3:
        raise ValueError("MR needs ≥3 instruments for the sensitivity analyses")
    p = ivw(instruments)
    e = mr_egger(instruments)
    m = weighted_median(instruments)
    causal = (p["p_value"] < 0.05 and not e["pleiotropy_flagged"]
              and (p["estimate"] > 0) == (m["estimate"] > 0))
    return {
        "ivw": p, "mr_egger": e, "weighted_median": m,
        "direction": "risk-increasing" if p["estimate"] > 0 else "protective",
        "causal_support": causal,
        "verdict": ("causal support (IVW significant, no pleiotropy flag, robust across methods)"
                    if causal else
                    "weak/null or pleiotropy-flagged — no clean causal support"),
        "guardrail": "non-diagnostic: population-level causal parameter for an instrument; "
                     "never an individual genetic risk or an imputed genotype",
    }
