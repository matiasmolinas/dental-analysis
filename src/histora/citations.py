"""The claim → source registry — the auditable source-of-truth for citation accuracy (WS5).

Every numeric anchor and mechanism entity HISTORA reports must resolve to a citable source. This module
is that registry, machine-readable so `histora.agent_metrics` can *score* an agent's citations against
it (does the cited key exist? does the stated value match?). It is mirrored, human-readable, in
`docs/CITATIONS.md`.

Non-diagnostic: these are population/parameter-level constants and public associations, never a patient
value.
"""

from __future__ import annotations

from typing import Any, Optional

# id -> {value (or None for entities), unit, ref (citation key), supports (what it grounds), doc}
CLAIMS: dict[str, dict[str, Any]] = {
    # ---- interventional calibration anchors ----
    "delta_crp_anchor": {"value": 0.5, "unit": "mg/L", "ref": "Front Immunol 2025 dynamics (meta-analytic ΔhsCRP)",
                         "supports": "CRP reduction after periodontal therapy", "doc": "MODELS.md"},
    "delta_hba1c_anchor": {"value": 0.35, "unit": "pp", "ref": "Simpson/Cochrane 2022; Teshome 2017",
                           "supports": "HbA1c reduction after periodontal therapy", "doc": "MODELS.md"},
    # ---- mechanism kinetics ----
    "crp_half_life": {"value": 19.0, "unit": "h", "ref": "Pepys & Hirschfield 2003, J Clin Invest 111:1805",
                      "supports": "CRP plasma half-life", "doc": "MODELS.md"},
    "il6_half_life": {"value": 2.0, "unit": "h", "ref": "human acute-phase IL-6 kinetics",
                      "supports": "IL-6 clearance half-life", "doc": "MODELS.md"},
    "alpha_tau": {"value": 0.019, "unit": "1/yr", "ref": "Schäfer et al. 2021, Front Physiol 12:702975",
                  "supports": "baseline tau growth rate (amyloid-positive)", "doc": "MODELS.md"},
    # ---- validated public associations (this work, on NHANES) ----
    "nhanes_perio_crp": {"value": 0.041, "unit": "std beta", "ref": "NHANES 2009-2010 (this work)",
                         "supports": "perio→CRP adjusted association", "doc": "PAPER.md"},
    "nhanes_perio_hba1c": {"value": 0.16, "unit": "std beta", "ref": "NHANES 2009-2010 (this work)",
                           "supports": "perio→HbA1c adjusted association", "doc": "PAPER.md"},
    "nhanes_perio_dsst": {"value": -0.18, "unit": "std beta", "ref": "NHANES 2011-2012 (this work)",
                          "supports": "perio→processing-speed adjusted association", "doc": "PAPER.md"},
    # ---- genetic causal probe (direction from the literature) ----
    "il6r_cad_mr": {"value": 0.105, "unit": "IVW beta (naïve, literature direction)",
                    "ref": "IL6R MR Consortium, Lancet 2012 (direction)",
                    "supports": "IL-6R signaling causal for coronary disease — established direction "
                                "(naïve IVW; the LD-aware cis run over live OpenGWAS gives correlated-IVW "
                                "β≈0.705, the valid estimate when instruments are in LD)", "doc": "PAPER.md"},
    "crp_ad_mr_null": {"value": 0.0, "unit": "IVW beta", "ref": "CRP–AD MR nulls (direction)",
                       "supports": "CRP/IL-6 → Alzheimer's genetically null", "doc": "PAPER.md"},
    # ---- honesty anchor ----
    "gain_trial_failed": {"value": None, "unit": None, "ref": "atuzaginstat/COR388 GAIN trial (failed)",
                          "supports": "the direct causal test of perio→AD failed", "doc": "MODELS.md"},
    # ---- mechanism proteins (entity grounding; UniProt/PDB) ----
    "protein_il6": {"value": None, "unit": None, "ref": "UniProt P05231",
                    "supports": "Interleukin-6", "doc": "DATA-AND-DELIVERY.md"},
    "protein_crp": {"value": None, "unit": None, "ref": "UniProt P02741; PDB 1B09",
                    "supports": "C-reactive protein", "doc": "DATA-AND-DELIVERY.md"},
    "protein_tau": {"value": None, "unit": None, "ref": "UniProt P10636 (MAPT); PDB 6QJH",
                    "supports": "Microtubule-associated protein tau", "doc": "DATA-AND-DELIVERY.md"},
    "protein_gingipain": {"value": None, "unit": None, "ref": "UniProt P28784 (RgpB, P. gingivalis)",
                          "supports": "gingipain virulence factor", "doc": "DATA-AND-DELIVERY.md"},
}


def resolve(claim_id: str) -> Optional[dict]:
    """Return the registry entry for a claim id, or None if it does not exist (a dangling citation)."""
    return CLAIMS.get(claim_id)


def supports(claim_id: str, value: Optional[float] = None, rel_tol: float = 0.15) -> bool:
    """True iff `claim_id` is in the registry AND (no value asserted, or the asserted value matches the
    registry value within `rel_tol`). A dangling key or a value mismatch → False (a citation failure)."""
    entry = CLAIMS.get(claim_id)
    if entry is None:
        return False
    if value is None or entry["value"] is None:
        return True
    ref = entry["value"]
    if ref == 0:
        return abs(value) <= 0.02
    return abs(value - ref) <= rel_tol * abs(ref)
