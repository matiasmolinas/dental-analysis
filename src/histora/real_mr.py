"""Real two-sample Mendelian randomization over public OpenGWAS summary statistics.

Turns the *illustrative* instrument panels of `histora.mendelian_randomization` into a **real** causal
probe: fetch genetic-association betas for a set of instrument SNPs across an exposure GWAS and an
outcome GWAS from the public **OpenGWAS** API, harmonize them to a common effect allele, and run the
same unit-tested estimator (IVW + MR-Egger + weighted-median). No individual-level data is ever touched
— only public, study-level summary statistics.

Access: OpenGWAS requires a free API token (a JWT from https://api.opengwas.io). This module reads it
from the `OPENGWAS_JWT` environment variable — **it never asks for, prints, or stores the token**. In
Claude Science, add it as a credential and the pipeline inherits it; Modal is optional and only needed
to *scale* to many exposure–outcome pairs (a single MR is laptop-light).

Non-diagnostic: MR estimates a population-level causal parameter for a genetic instrument — never an
individual genetic risk, never an imputed genotype. Study IDs are versioned; **verify them on OpenGWAS**
before quoting a result — the estimator is exact and tested, the study choice is yours.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Callable, Optional

from .mendelian_randomization import Instrument, run_mr

OPENGWAS_BASE = "https://api.opengwas.io/api"

# --- default probe configuration (VERIFY the OpenGWAS study IDs before quoting; they are versioned) ---
# Exposure: circulating CRP (the measurable readout of the shared IL-6 inflammatory proxy), instrumented
# by GWAS-significant cis/trans CRP SNPs. Outcomes: coronary disease, Alzheimer's, type-2 diabetes.
# Labels below were verified against live OpenGWAS `gwasinfo` metadata (2026-07); still re-verify, IDs
# are versioned. `caveat` surfaces a known metadata issue so it is reported, not hidden.
DEFAULT_CONFIG: dict[str, Any] = {
    "exposure": {"id": "ieu-b-35", "label": "CRP (Ligthart 2018, PMID 30388399) — inflammatory proxy",
                 "instruments": ["rs2794520", "rs1130864", "rs1205", "rs3091244",
                                 "rs1800947", "rs1417938", "rs3093077"]},
    "outcomes": [
        {"id": "ieu-a-7", "label": "coronary artery disease (CARDIoGRAMplusC4D, Nikpay 2015)"},
        {"id": "ieu-b-2", "label": "Alzheimer's disease (Kunkle 2019, IGAP-affiliated)"},
        {"id": "ebi-a-GCST006867", "label": "type-2 diabetes (Xue 2018)",
         "caveat": "OpenGWAS metadata reports an implausible ncontrol for this record — treat the "
                   "outcome SEs (and this pair's verdict) cautiously; consider an alternative T2D GWAS."},
    ],
    # ALTERNATIVE exposure — a cis-IL-6R probe (the tocilizumab-mimicking instrument): the IL6R-locus
    # effect on CRP. NOT auto-run by run_real_mr (swap it in as `exposure`). cis SNPs are in LD, so a
    # naive multi-instrument IVW violates the independence assumption — a rigorous run needs LD clumping
    # or a correlation-matrix method (e.g. GRAPPLE / correlated-IVW). Provided as a documented starting set.
    "il6r_cis": {"id": "ieu-b-35", "label": "IL-6R cis (IL6R locus → CRP)",
                 "instruments": ["rs2228145", "rs4129267", "rs7529229", "rs4845625", "rs4537545"],
                 "caveat": "cis instruments are correlated (LD) — run with LD-aware MR, not naive IVW; "
                           "this is why the single-SNP form cannot support the >=3-instrument checks."},
}


def _token() -> str:
    tok = os.environ.get("OPENGWAS_JWT", "").strip()
    if not tok:
        raise SystemExit("OPENGWAS_JWT not set. Get a free token at https://api.opengwas.io and export "
                         "OPENGWAS_JWT (or add it as a Claude Science credential). The token is read "
                         "from the environment and never stored by HISTORA.")
    return tok


def fetch_associations(rsids: list[str], study_ids: list[str], token: Optional[str] = None,
                       timeout: int = 30) -> list[dict]:
    """POST to OpenGWAS /associations for the given SNPs across the given studies. Returns the raw rows
    (each with rsid, ea, nea, beta, se, p, id). Public summary statistics only."""
    token = token or _token()
    body = json.dumps({"variant": rsids, "id": study_ids}).encode()
    req = urllib.request.Request(f"{OPENGWAS_BASE}/associations", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    # OpenGWAS returns either a list of rows or a {id: [rows]} map depending on version; normalize.
    if isinstance(data, dict):
        rows: list[dict] = []
        for v in data.values():
            rows.extend(v if isinstance(v, list) else [v])
        return rows
    return data


def harmonize(exposure_rows: list[dict], outcome_rows: list[dict]) -> list[Instrument]:
    """Align each SNP's outcome effect to the exposure effect allele (flip the outcome beta if the
    effect alleles are swapped); drop SNPs missing from either study or with incompatible alleles."""
    def key(r):
        return r.get("rsid") or r.get("variant") or r.get("name")
    exp = {key(r): r for r in exposure_rows}
    out = {key(r): r for r in outcome_rows}
    instruments = []
    for snp in exp:
        if snp not in out:
            continue
        e, o = exp[snp], out[snp]
        try:
            be, see = float(e["beta"]), float(e["se"])
            bo, seo = float(o["beta"]), float(o["se"])
        except (KeyError, TypeError, ValueError):
            continue
        ea_e, na_e = str(e.get("ea", "")).upper(), str(e.get("nea", "")).upper()
        ea_o, na_o = str(o.get("ea", "")).upper(), str(o.get("nea", "")).upper()
        if ea_e and ea_o:
            if {ea_e, na_e} != {ea_o, na_o}:
                continue                              # allele mismatch (multi-allelic / strand) → drop
            if ea_e != ea_o:
                bo = -bo                              # flip outcome to the exposure effect allele
        if be == 0 or see <= 0 or seo <= 0:
            continue
        instruments.append(Instrument(str(snp), be, see, bo, seo, ea=ea_e))
    return instruments


def run_real_mr(config: dict = DEFAULT_CONFIG, token: Optional[str] = None,
                fetch: Callable = fetch_associations) -> dict[str, Any]:
    """Run the real probe for each exposure→outcome pair. `fetch` is injectable for offline testing."""
    token = token or _token()
    exposure = config["exposure"]
    report: dict[str, Any] = {"exposure": exposure["label"], "source": "OpenGWAS (public summary stats)",
                              "outcomes": {}}
    for outcome in config["outcomes"]:
        rows = fetch(exposure["instruments"], [exposure["id"], outcome["id"]], token)
        exp_rows = [r for r in rows if r.get("id") == exposure["id"]]
        out_rows = [r for r in rows if r.get("id") == outcome["id"]]
        insts = harmonize(exp_rows, out_rows)
        entry: dict[str, Any] = {"outcome": outcome["label"], "exposure": exposure["label"],
                                 "n_instruments": len(insts),
                                 "exposure_id": exposure["id"], "outcome_id": outcome["id"],
                                 # per-SNP harmonized data, so a proper MR scatter can be drawn
                                 "instruments": [{"snp": i.snp, "beta_exposure": i.beta_exposure,
                                                  "se_exposure": i.se_exposure,
                                                  "beta_outcome": i.beta_outcome,
                                                  "se_outcome": i.se_outcome} for i in insts]}
        if outcome.get("caveat"):
            entry["caveat"] = outcome["caveat"]
        if len(insts) >= 3:
            entry.update(run_mr(insts))
        else:
            entry["note"] = "fewer than 3 harmonized instruments — MR sensitivity analyses need >=3"
        report["outcomes"][outcome["label"]] = entry
    report["guardrail"] = ("non-diagnostic: population-level causal parameters for genetic instruments; "
                           "never an individual genetic risk or an imputed genotype")
    report["caveat"] = "study IDs are versioned — verify on OpenGWAS before quoting"
    return report
