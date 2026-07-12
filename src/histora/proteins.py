"""The protein layer of the shared inflammatory proxy — the UniProt/PDB connector data (Stage-3, phase E).

HISTORA's spine is one shared inflammatory proxy: periodontal inflammation drives **IL-6**, IL-6 signals
through the **IL-6Rα / gp130** receptor complex (JAK–STAT3) to the liver, and the liver secretes **CRP**.
The Stage-3 multi-cytokine core adds **TNF-α** (the autocatalytic driver) and **IL-10** (the resolution
brake). This module grounds those mediators in their molecular identity: the **UniProt accession** (the
stable connector key) and, where we can name one with confidence, a **representative PDB structure**.

Why this is a *connector*, not a claim: the accessions are reference facts, not model outputs. In Claude
Science the same registry drives the **UniProt/PDB connector** — it fetches the live entries and renders the
3-D structures (e.g. IL-6, the IL-6/IL-6Rα/gp130 hexamer, pentameric CRP, and the **tocilizumab** IL-6Rα
blockade that is the therapeutic analogue of removing the periodontal source). Here, offline, we ship the
registry + a static signaling-axis schematic; the live 3-D rendering is the platform upgrade.

Non-diagnostic: molecular/population-level reference data only — no patient value is produced or consumed.
PDB IDs are marked representative; a scientist (or the connector) resolves the authoritative structure.
"""

from __future__ import annotations

import re
from typing import Any, Optional

# accession (UniProt, human) is the stable connector key; pdb is a representative structure where we can
# name one with confidence, else None (the connector resolves the authoritative entry live).
_PROTEINS = [
    {"mediator": "IL-6", "gene": "IL6", "accession": "P05231", "pdb": "1ALU",
     "role": "the shared proxy — periodontal inflammation raises it; drives every systemic axis"},
    {"mediator": "IL-6Rα", "gene": "IL6R", "accession": "P08887", "pdb": None,
     "role": "IL-6 receptor α — the node tocilizumab blocks; the IL-6R MR instrument acts here"},
    {"mediator": "gp130", "gene": "IL6ST", "accession": "P40189", "pdb": None,
     "role": "signal transducer (IL6ST) — completes the hexameric signaling complex → JAK/STAT3"},
    {"mediator": "CRP", "gene": "CRP", "accession": "P02741", "pdb": "1GNH",
     "role": "hepatic acute-phase output; the calibration anchor (ΔhsCRP after periodontal therapy)"},
    {"mediator": "TNF-α", "gene": "TNF", "accession": "P01375", "pdb": "1TNF",
     "role": "Stage-3 core — the autocatalytic pro-inflammatory driver (bistability)"},
    {"mediator": "IL-10", "gene": "IL10", "accession": "P22301", "pdb": None,
     "role": "Stage-3 core — the anti-inflammatory resolution brake (acute vs chronic)"},
]

# the therapeutic node — an IL-6Rα-blocking mAb; the molecular analogue of removing the periodontal source.
_THERAPEUTIC = {"agent": "tocilizumab", "target_gene": "IL6R", "target_accession": "P08887",
                "drugbank": "DB06273", "action": "IL-6Rα blockade → attenuates IL-6 trans/classic signaling"}

_ACCESSION_RE = re.compile(r"^[A-NR-Z0-9][0-9][A-Z0-9]{3}[0-9]$|^[OPQ][0-9][A-Z0-9]{3}[0-9]$")


def protein_registry() -> list[dict[str, Any]]:
    """The mediator → molecular-identity registry (copied, so callers can't mutate the reference data)."""
    return [dict(p) for p in _PROTEINS]


def by_mediator(name: str) -> Optional[dict[str, Any]]:
    for p in _PROTEINS:
        if p["mediator"].lower() == name.lower():
            return dict(p)
    return None


def signaling_axis() -> dict[str, Any]:
    """The IL-6 → IL-6Rα/gp130 → hepatic CRP axis as an ordered node/edge graph for the schematic, with the
    tocilizumab blockade marked on the IL-6Rα node. Structural reference — not a patient-specific claim."""
    order = ["IL-6", "IL-6Rα", "gp130", "CRP"]
    nodes = [by_mediator(m) for m in order]
    return {
        "nodes": nodes,
        "edges": [("IL-6", "IL-6Rα", "binds"), ("IL-6Rα", "gp130", "recruits"),
                  ("gp130", "CRP", "JAK/STAT3 → hepatic acute phase")],
        "therapeutic": dict(_THERAPEUTIC),
        "lever": "removing the periodontal source lowers IL-6 — the same node tocilizumab blocks pharmacologically",
        "non_diagnostic": True,
    }


def registry_is_valid() -> bool:
    """Every mediator has a well-formed UniProt accession and a role — the connector's integrity check."""
    seen = set()
    for p in _PROTEINS:
        if not _ACCESSION_RE.match(p["accession"]):
            return False
        if not p["role"] or not p["mediator"]:
            return False
        seen.add(p["mediator"])
    return len(seen) == len(_PROTEINS)
