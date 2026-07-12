"""Tests for the protein connector layer — the UniProt/PDB reference data behind the shared proxy.

Pure/offline. Locks in connector integrity: every mediator has a well-formed UniProt accession, the
signaling axis is the ordered IL-6 → IL-6Rα → gp130 → CRP chain, tocilizumab targets the IL-6Rα node, and
the registry is non-diagnostic reference data (never a patient value). These are the invariants the Claude
Science UniProt/PDB connector relies on.

Run:  python tests/test_proteins.py
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.proteins import by_mediator, protein_registry, registry_is_valid, signaling_axis

# the canonical UniProt accession pattern (same one UniProt documents)
UNIPROT = re.compile(r"^[A-NR-Z0-9][0-9][A-Z0-9]{3}[0-9]$|^[OPQ][0-9][A-Z0-9]{3}[0-9]$")


def test_registry_valid_and_core_mediators_present():
    assert registry_is_valid()
    names = {p["mediator"] for p in protein_registry()}
    for core in ("IL-6", "IL-6Rα", "gp130", "CRP", "TNF-α", "IL-10"):
        assert core in names
    # the spine's three canonical proteins carry the accessions the connector keys on
    assert by_mediator("IL-6")["accession"] == "P05231"
    assert by_mediator("CRP")["accession"] == "P02741"
    assert by_mediator("IL-6Rα")["accession"] == "P08887"


def test_every_accession_is_well_formed():
    for p in protein_registry():
        assert UNIPROT.match(p["accession"]), p["accession"]


def test_signaling_axis_is_the_ordered_chain_with_tocilizumab_on_il6r():
    ax = signaling_axis()
    assert [n["mediator"] for n in ax["nodes"]] == ["IL-6", "IL-6Rα", "gp130", "CRP"]
    assert ax["therapeutic"]["agent"] == "tocilizumab"
    assert ax["therapeutic"]["target_accession"] == by_mediator("IL-6Rα")["accession"]
    assert ax["non_diagnostic"] is True
    assert len(ax["edges"]) == len(ax["nodes"]) - 1


def test_registry_is_a_copy_not_the_live_reference():
    reg = protein_registry()
    reg[0]["accession"] = "TAMPERED"
    assert by_mediator("IL-6")["accession"] == "P05231"   # mutating the copy never touches the source


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
