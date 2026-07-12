# CITATIONS — the claim → source registry (WS5)

> The auditable source-of-truth behind **citation accuracy**: every numeric anchor and mechanism entity
> HISTORA reports resolves to a citable source here. This document mirrors the machine-readable registry
> `histora.citations.CLAIMS`, which `histora.agent_metrics` scores against (does the cited key exist? does
> the stated value match?). Keep the two in sync — the module is the source of truth; this table is its
> human-readable view.
>
> Non-diagnostic: these are population/parameter-level constants and public associations, never a patient value.

| Claim id | Value | Grounds | Reference | Doc |
|---|---|---|---|---|
| `delta_crp_anchor` | 0.5 mg/L | CRP reduction after periodontal therapy | Front Immunol 2025 dynamics (meta-analytic ΔhsCRP) | MODELS.md |
| `delta_hba1c_anchor` | 0.35 pp | HbA1c reduction after periodontal therapy | Simpson/Cochrane 2022; Teshome 2017 | MODELS.md |
| `crp_half_life` | 19.0 h | CRP plasma half-life | Pepys & Hirschfield 2003, J Clin Invest 111:1805 | MODELS.md |
| `il6_half_life` | 2.0 h | IL-6 clearance half-life | human acute-phase IL-6 kinetics | MODELS.md |
| `alpha_tau` | 0.019 1/yr | baseline tau growth rate (amyloid-positive) | Schäfer et al. 2021, Front Physiol 12:702975 | MODELS.md |
| `nhanes_perio_crp` | 0.041 std beta | perio→CRP adjusted association | NHANES 2009-2010 (this work) | PAPER.md |
| `nhanes_perio_hba1c` | 0.16 std beta | perio→HbA1c adjusted association | NHANES 2009-2010 (this work) | PAPER.md |
| `nhanes_perio_dsst` | -0.18 std beta | perio→processing-speed adjusted association | NHANES 2011-2012 (this work) | PAPER.md |
| `il6r_cad_mr` | 0.105 IVW beta (naïve, literature direction) | IL-6R signaling causal for coronary disease — established direction (naïve IVW; the LD-aware cis run over live OpenGWAS gives correlated-IVW β≈0.705, the valid estimate when instruments are in LD) | IL6R MR Consortium, Lancet 2012 (direction) | PAPER.md |
| `crp_ad_mr_null` | 0.0 IVW beta | CRP/IL-6 → Alzheimer's genetically null | CRP–AD MR nulls (direction) | PAPER.md |
| `gain_trial_failed` | — | the direct causal test of perio→AD failed | atuzaginstat/COR388 GAIN trial (failed) | MODELS.md |
| `protein_il6` | — | Interleukin-6 | UniProt P05231 | DATA-AND-DELIVERY.md |
| `protein_crp` | — | C-reactive protein | UniProt P02741; PDB 1B09 | DATA-AND-DELIVERY.md |
| `protein_tau` | — | Microtubule-associated protein tau | UniProt P10636 (MAPT); PDB 6QJH | DATA-AND-DELIVERY.md |
| `protein_gingipain` | — | gingipain virulence factor | UniProt P28784 (RgpB, P. gingivalis) | DATA-AND-DELIVERY.md |

**How it is used.** `histora.citations.supports(claim_id, value)` returns True iff the id exists and (if a
value is asserted) it matches within tolerance. `histora.agent_metrics.citation_accuracy` scores an agent's
cited claims against this; a dangling key or a value mismatch is a citation failure. See
[`BENCHMARK.md`](BENCHMARK.md) (protocol) and [`internal/STAGE2-WORKPLAN.md`](internal/STAGE2-WORKPLAN.md) WS5.

**Note — the two IL-6R→CAD figures are not a contradiction.** `il6r_cad_mr` = **0.105** is the established
*literature direction* (naïve IVW). Our **LD-aware cis run over live OpenGWAS** gives **correlated-IVW
β≈0.705** — the valid estimate when the instruments are in LD (naïve IVW understates it with a ~7× wider
SE). See [`CLAUDE-SCIENCE.md`](CLAUDE-SCIENCE.md).

*Protein entities cite UniProt/PDB (the Claude Science connectors); replace/extend as the mechanism grows.*
