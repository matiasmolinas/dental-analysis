"""LD-aware cis-Mendelian randomization — the IL-6R probe done correctly.

The strong causal test in the shared-proxy story is **IL-6R signalling → coronary disease** (the
tocilizumab-mimicking instrument). But a cis probe uses several SNPs at *one locus* (the IL6R gene),
which are in **linkage disequilibrium** — correlated. Standard IVW assumes *independent* instruments, so
running it naively on cis SNPs is wrong (it under-states the variance and can bias the point estimate).

This module does it properly with **correlated IVW** (Burgess et al. 2016): a generalized-least-squares
estimate that uses the SNP–SNP LD correlation matrix R. The outcome-beta covariance is
Σ = diag(se) · R · diag(se); the estimate is β = (bxᵀ Σ⁻¹ by)/(bxᵀ Σ⁻¹ bx) with SE = 1/√(bxᵀ Σ⁻¹ bx).
Pure-python (uses `histora.stats.solve` for the GLS systems).

Two subtleties handled: (1) the LD matrix from a reference panel is defined relative to specific alleles,
so its signs are **aligned to the same effect alleles** used to harmonize the betas; (2) a tiny ridge
keeps Σ invertible when instruments are nearly collinear.

Access: the LD matrix is fetched from the OpenGWAS `/ld/matrix` endpoint (reference panel, e.g. EUR),
which needs the `OPENGWAS_JWT` token — read from the environment, never stored. Non-diagnostic:
population/instrument-level causal parameter, never an individual genetic risk.

Honest limits: correlated IVW is the standard first-line cis method, not the last word — it assumes the
LD matrix is accurate and the instruments valid; a fully rigorous cis-MR may add PCA/conditional analysis
and instrument-strength (F-stat) checks. Those are flagged, not silently omitted.
"""

from __future__ import annotations

import json
import math
import os
import urllib.request
from typing import Any, Callable, Optional

from .mendelian_randomization import Instrument, _ci90, _two_sided_p
from .real_mr import OPENGWAS_BASE, fetch_associations, harmonize
from .stats import solve

# cis probe: IL6R-locus SNPs' effect on CRP (exposure) → coronary artery disease (outcome).
CIS_CONFIG: dict[str, Any] = {
    "exposure": {"id": "ieu-b-35", "label": "IL-6R cis (IL6R locus → CRP)",
                 "instruments": ["rs2228145", "rs4129267", "rs7529229", "rs4845625", "rs4537545"]},
    "outcome": {"id": "ieu-a-7", "label": "coronary artery disease (CARDIoGRAMplusC4D)"},
    "pop": "EUR",
}


def correlated_ivw(instruments: list[Instrument], R: list[list[float]],
                   ridge: float = 1e-6) -> dict[str, Any]:
    """Correlated (LD-aware) IVW via GLS. `R` is the SNP–SNP LD correlation matrix, aligned to the
    instruments' effect alleles and in the SAME order as `instruments`."""
    n = len(instruments)
    if n < 2:
        raise ValueError("correlated IVW needs >=2 instruments")
    bx = [i.beta_exposure for i in instruments]
    by = [i.beta_outcome for i in instruments]
    se = [i.se_outcome for i in instruments]
    Sigma = [[R[a][b] * se[a] * se[b] + (ridge if a == b else 0.0) for b in range(n)] for a in range(n)]
    x = solve(Sigma, by[:])          # Σ x = by  → x = Σ⁻¹ by
    w = solve(Sigma, bx[:])          # Σ w = bx  → w = Σ⁻¹ bx
    num = sum(bx[k] * x[k] for k in range(n))
    den = sum(bx[k] * w[k] for k in range(n))
    if den <= 0:
        raise ValueError("non-positive information (LD matrix not positive-definite?)")
    beta = num / den
    se_beta = math.sqrt(1.0 / den)
    return {"estimate": round(beta, 4), "se": round(se_beta, 4), "ci_90": _ci90(beta, se_beta),
            "p_value": round(_two_sided_p(beta, se_beta), 5), "n_instruments": n,
            "method": "correlated IVW (GLS with LD matrix)"}


def fetch_ld_matrix(rsids: list[str], token: Optional[str] = None, pop: str = "EUR",
                    timeout: int = 30) -> tuple[list[list[float]], dict[str, str]]:
    """Fetch the LD correlation matrix for `rsids` from OpenGWAS `/ld/matrix`. Returns (R, ref_allele)
    where ref_allele[snp] is the allele the panel's correlations are signed to (from the row labels,
    typically 'rsid_A1_A2'). VERIFY the endpoint's response shape against your OpenGWAS version."""
    token = token or os.environ.get("OPENGWAS_JWT", "").strip()
    if not token:
        raise SystemExit("OPENGWAS_JWT not set — needed for the LD matrix (never stored by HISTORA).")
    body = json.dumps({"rsid": rsids, "pop": pop}).encode()
    req = urllib.request.Request(f"{OPENGWAS_BASE}/ld/matrix", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    matrix = data.get("matrix") if isinstance(data, dict) else data
    labels = (data.get("snplist") or data.get("snps") or []) if isinstance(data, dict) else []
    ref = {}
    for lab in labels:
        parts = str(lab).split("_")
        if len(parts) >= 2:
            ref[parts[0]] = parts[1].upper()      # first allele = the sign reference for that SNP
    return [[float(v) for v in row] for row in matrix], ref


def align_ld_signs(R: list[list[float]], ref_allele: dict[str, str],
                   instruments: list[Instrument]) -> list[list[float]]:
    """Flip the LD signs so R is defined relative to each instrument's EFFECT allele. If the panel's
    reference allele for a SNP differs from the harmonized effect allele, negate that SNP's row+column."""
    n = len(instruments)
    flip = []
    for i in instruments:
        ra = ref_allele.get(i.snp, "")
        flip.append(-1.0 if (ra and i.ea and ra != i.ea.upper()) else 1.0)
    return [[R[a][b] * flip[a] * flip[b] for b in range(n)] for a in range(n)]


def run_cis_mr(config: dict = CIS_CONFIG, token: Optional[str] = None,
               fetch_assoc: Callable = fetch_associations,
               fetch_ld: Callable = fetch_ld_matrix) -> dict[str, Any]:
    """The LD-aware IL-6R cis probe: fetch associations, harmonize, fetch + sign-align the LD matrix,
    and run correlated IVW. Also reports the (wrong) naive IVW for contrast, to show LD matters."""
    token = token or os.environ.get("OPENGWAS_JWT", "").strip()
    exp, out = config["exposure"], config["outcome"]
    rows = fetch_assoc(exp["instruments"], [exp["id"], out["id"]], token)
    exp_rows = [r for r in rows if r.get("id") == exp["id"]]
    out_rows = [r for r in rows if r.get("id") == out["id"]]
    insts = harmonize(exp_rows, out_rows)

    report: dict[str, Any] = {"exposure": exp["label"], "outcome": out["label"],
                              "n_instruments": len(insts), "source": "OpenGWAS (public summary + LD)",
                              "instruments": [{"snp": i.snp, "beta_exposure": i.beta_exposure,
                                               "se_exposure": i.se_exposure, "beta_outcome": i.beta_outcome,
                                               "se_outcome": i.se_outcome} for i in insts]}
    if len(insts) < 2:
        report["note"] = "fewer than 2 harmonized cis instruments — cannot run correlated IVW"
        return report

    from .mendelian_randomization import ivw as naive_ivw
    R_raw, ref = fetch_ld(exp["instruments"], token, config.get("pop", "EUR"))
    # order R to the harmonized instrument order
    idx = {s: k for k, s in enumerate(exp["instruments"])}
    order = [idx[i.snp] for i in insts if i.snp in idx]
    R = [[R_raw[a][b] for b in order] for a in order]
    R = align_ld_signs(R, ref, insts)

    report["correlated_ivw"] = correlated_ivw(insts, R)     # primary (LD-aware)
    report["naive_ivw_for_contrast"] = naive_ivw(insts)     # wrong on cis data — shown to prove LD matters
    report["caveats"] = [
        "cis instruments are correlated (LD) — correlated IVW is primary; naive IVW is shown only to "
        "illustrate the difference and must NOT be quoted.",
        "assumes the OpenGWAS LD reference panel matches the GWAS ancestry; verify the population.",
        "first-line method: consider PCA/conditional cis-MR and per-SNP F-statistics for a definitive run.",
    ]
    report["guardrail"] = ("non-diagnostic: a population-level causal parameter for the IL-6R instrument; "
                           "never an individual genetic risk or an imputed genotype")
    return report
