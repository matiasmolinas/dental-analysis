# Claude Science — live-run captures

Real UI screenshots of the HISTORA **flagship case study running live in Claude Science** (§5 of
[`../../OVERVIEW.md`](../../OVERVIEW.md)). These are the actual session — the
directive, the engine run, the connector-resolved 3-D structures, and the reviewer agent's audit.
*Everything shown is public.*

| File | What it shows |
|---|---|
| `01-workflow-directive.png` | the **workflow**: a directive in, and Claude — as operator — updating the pinned engine to the latest `main` and running the case study |
| `02-research-line.png` | the **science**: the engine's 90% ranges, the genetic node (IL-6R→CAD causal, CRP→AD null), and the falsifiable research line, beside the live IL-6/IL-6Rα/gp130 hexamer (`1P9M`) in the Mol\* viewer. *(This capture predates the LD-bug correction — the panel text shows the pre-correction cis-MR β≈+0.705, later retracted to +0.553; see [`../../SELF-CORRECTION.md`](../../SELF-CORRECTION.md). The demo video uses the structure panel only.)* |
| `04-reviewer-finding-hexamer.png` | the **scientist-user beat**: the reviewer agent's finding (`1P9M` is 3.65 Å, not 2.4 Å) and Claude's self-correction, with "All 2 findings fixed" |
| `05-per-participant-real.png` | the engine run across **4 real NHANES 2009-2010 participants** (SEQN-only, de-identified) — CRP and HbA1c-shift 90% ranges per participant, structural bands in, population-level ranges out; IL-6 flagged absent for all; BOP not collected this cycle → flagged. Non-diagnostic; ranges are **not** patient values. |
| `06-mr-replication-real.png` | the **IL-6R → CAD Mendelian-randomization replication** across THREE independent consortia via the `human-genetics` connector — our OpenGWAS/CARDIoGRAMplusC4D (naive + LD-aware cis-IVW) vs **FinnGen** (I9_CHD, I9_CORATHER; rs2228145 Asp358Ala) and **BioBank Japan** (cross-ancestry). All positive → the IL-6R→CAD causal **direction replicates** (single-SNP Wald vs multi-SNP magnitudes not directly comparable; the sign is what replicates). MR ≠ RCT, non-diagnostic. |
| `07-mr-headtohead-correlated-ivw.png` | the **LD-corrected like-for-like magnitude head-to-head**: the SAME construction (3 harmonized cis SNPs rs4537545/rs4845625/rs4129267, OpenGWAS CRP `ieu-b-35` exposure, EUR 1000G LD panel, GLS correlated-IVW estimator `histora.cis_mr`), swapping ONLY the outcome consortium — ours (CARDIoGRAMplusC4D) **+0.553 (SE 0.109)** vs FinnGen R12 **+0.421** (I9_CHD) / **+0.466** (I9_CORATHER). **Sign AND magnitude now agree** — the difference is non-significant (Δ p=0.35/0.54). Trying to close the residual gap with a native Finnish LD panel (blocked by an `ld-api.finngen.fi` 502 outage) instead **exposed a real LD row-ordering bug** in our estimator: the OpenGWAS `/ld/matrix` server returns SNPs in genomic-position order, and reindexing by request order injected a spurious `r≈1` cross-term that near-singularized the GLS and produced the earlier over-confident **+0.705 (SE 0.010)** — now retracted (shown greyed with an ✗) and **fixed in `histora.cis_mr` with a regression test**. MR ≠ RCT, population-level, non-diagnostic. |

*Non-diagnostic throughout; molecular / population-level only.*
