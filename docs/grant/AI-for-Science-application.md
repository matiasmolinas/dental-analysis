# AI for Science — application draft (HISTORA)

> **Time-sensitive.** Anthropic's *AI for Science* program funds ~50 projects with up to **$30,000 in
> Claude credits** (+ up to $2,000 Modal compute); **applications close July 15, 2026**; awards by
> July 31; projects run **Sep 1 – Dec 1, 2026**. This is a ready-to-adapt draft — trim to the official
> form's fields. Apply at claude.com/science.

## One-line pitch
**HISTORA** is a *non-diagnostic* scientific research agent that turns fragmented oral–systemic evidence
into **falsifiable, mechanistically-explained, uncertainty-quantified hypotheses** — one shared
inflammatory proxy linking periodontitis to cardiovascular, metabolic, and neurodegenerative disease,
calibrated to real interventional data, validated on public NHANES, and now genetically probed by
Mendelian randomization.

## Why this project (fit to the program)
- **Biomedical + reproducible + safety-forward.** Pure-Python engine over public data; every number
  traces to a calibrated equation, a public-data association, a genetic instrument, or a flagged
  hypothesis. A hard, structural **non-diagnostic guardrail**.
- **Claude as a scientific orchestrator, not a black-box predictor.** Claude selects models, reports
  uncertainty, routes to falsification, and contributes weight-capped soft estimates only where the
  coded library runs out — never sources a headline number.
- **Uncertainty and falsifiability as product features.** Predictions ship as ensemble envelopes with a
  refutation condition; a benchmark measures coherence, calibration, and falsifiability rather than
  accuracy.

## What we've built (evidence, not promises)
- **Mechanistic engine:** one shared inflammatory proxy (excess IL-6) → CRP → three coupled axes;
  the oral→systemic spillover ε **calibrated** to the ~0.5 mg/L ΔCRP-after-therapy anchor; couplings
  swept as ranges (Latin-hypercube ensemble + sensitivity).
- **Empirical validation on NHANES** (confounder-adjusted, bootstrap CIs): periodontal severity →
  higher CRP (+0.041), higher HbA1c (+0.12–0.16), worse cognition (−0.06 to −0.18, 3/4 measures) — all
  from **one** calibrated parameter.
- **Comparative benchmark** (S separate models / C bare Claude / H harness): the integration is more
  parsimonious (1 vs 3 params), calibrated (error 0.00 vs 0.71/1.25), and uncertainty-honest (ranges +
  falsifiability 1.00 vs 0.00); direction ties.
- **Genetic causal probe (Mendelian randomization):** IL-6R signaling → coronary disease shows **causal
  support**; CRP/IL-6 → Alzheimer's is **null** — genetics that independently supports our own tiering
  (CV/metabolic anchored; neuro exploratory). Pure-Python IVW + MR-Egger + weighted-median, on public
  GWAS summary statistics.

## What the credits would fund (Sep–Dec 2026)
1. **Scale the genetic causal layer** — replace the illustrative MR panels with live OpenGWAS/GWAS-Catalog
   extractions across IL-6R/CRP → CAD, T2D, AD, stroke, and cognition; add MR-PRESSO/leave-one-out.
2. **Statistical hardening at cohort scale** — NHANES survey-design estimation (weights/strata/PSU) and
   FDR across all axes; an external-cohort replication (ARIC-style longitudinal, application-gated).
3. **Claude Science packaging** — HISTORA as Claude Science skills + specialist agents + a reusable
   harness pipeline, using UniProt/PDB/GWAS connectors and the platform reviewer agent (which mirrors our
   citation/guardrail metrics); compute on Modal for the genomics pulls.
4. **The agentic-AI metric card** — reproducible hallucination rate, citation accuracy, uncertainty
   calibration (band coverage), and consistency, reported across arms.

## Why Anthropic + Gladstone
HISTORA sits exactly at the intersection: an AI agent whose value is that it is *honest* — uncertainty,
falsifiability, citation integrity, and a non-diagnostic guardrail as features, not disclaimers — and its
most exploratory axis is Gladstone's terrain (neuroinflammation, the blood–brain interface, tau). It
touches **four of Gladstone's five institutes** (Neurological Disease, Cardiovascular, Data Science &
Biotechnology, Genomic Immunology), and hands a lab a *novel upstream perturbation* (periodontal
inflammation → tau) as a parameterized, falsifiable hypothesis — with the intellectual honesty (including
the failed GAIN trial) a serious lab requires.

## Team & scope discipline
Solo/small-team, pure-Python, public-data. We deliberately **do not** add disease axes or claim causation
we haven't earned; the work is depth and honesty, not breadth.

## Safety statement
Non-diagnostic by construction: structural bands in, population/parameter-level ranges out; a missing
datum is a collection flag, never imputed; no patient value — and no individual genotype — is ever
produced or persisted. Genetics is used at the population/instrument level only.

## Links (fill in)
- Repo: <github.com/matiasmolinas/dental-analysis>
- Technical report: `docs/PAPER.md` · Benchmark: `docs/BENCHMARK.md` · Data/delivery analysis:
  `docs/DATA-AND-DELIVERY.md` · Stage-2 plan: `docs/STAGE2-WORKPLAN.md`

---

## Checklist before submitting (by Jul 15, 2026)
- [ ] Confirm eligibility/plan (Pro/Max/Team/Enterprise; academic/nonprofit Team discount if applicable).
- [ ] Trim this draft to the official form's fields and word limits.
- [ ] Fill the repo link and any required figures (reuse the one-page artifact + the architecture diagram).
- [ ] State compute needs (Modal) for the live OpenGWAS pulls and any genomics.
- [ ] Submit at claude.com/science and note the confirmation.

*Non-diagnostic throughout; population/parameter/instrument level only.*
