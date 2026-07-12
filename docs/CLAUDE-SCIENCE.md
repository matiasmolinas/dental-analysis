# Running HISTORA in Claude Science

> HISTORA runs two ways, one engine: a **portable Claude Code plugin** (the demo a judge runs anywhere)
> and, its lab-grade home, **[Claude Science](https://www.anthropic.com/news/claude-science-ai-workbench)**
> — where the *same* skills + the deterministic pipeline drop in, native figures render, connectors reach
> real data, and a reviewer agent checks the output. This page is the quickstart + what we've **proven
> live**. The full "integrated vs. Claude Science" analysis is in
> [`internal/CLAUDE-SCIENCE-ANALYSIS.md`](internal/CLAUDE-SCIENCE-ANALYSIS.md).

## How HISTORA maps onto Claude Science

Claude Science's native extension model is **skills + connectors** (plus specialist agents and a reviewer
agent) — no "plugin" slot, but our components port directly, with **no rewrite**:

| HISTORA (this repo) | Claude Science |
|---|---|
| `skills/*/SKILL.md` (staging, guardrail, oral-systemic analysis, KB, traceability, …) | **skills** |
| `skills/histora-mechanistic-pipeline/` (the deterministic engine + figures) | a **reusable pipeline skill** |
| `agents/` (orchestrator, analysts, guardrail-verifier) | **specialist agents** |
| OpenGWAS (MR), UniProt/PDB (mechanism), NHANES | **connectors** |
| our citation/hallucination/guardrail metrics | the platform **reviewer agent** |

## Quickstart

1. **Import the skills** — Customize → Skills → *Add skill* → **Import from GitHub** →
   `matiasmolinas/dental-analysis` → Preview → Import. (Reads the plugin-marketplace layout; imports all
   the skills, including the deterministic pipeline.)
2. **Add credentials** you want (Settings → Credentials): a free **OpenGWAS** token as a custom credential
   named `OPENGWAS_JWT` (for real Mendelian randomization); **Modal** is optional (only to scale).
3. **Run a session.** Give it a structural case and it activates the reasoning skills; or ask it to run
   the pipeline:
   - `run_pipeline.py --case case.json` → mechanistic ranges + counterfactuals
   - `run_pipeline.py --mr --real --plot` → real MR over OpenGWAS + the scatter
   - `run_pipeline.py --cis --plot` → the LD-aware IL-6R cis probe + the scatter
   - `run_pipeline.py --benchmark` → the S-vs-H comparative scorecard

## Proven live (in a running Claude Science instance)

- **Reasoning skills** — a structural case (stage III periodontitis, hs-CRP MISSING) auto-loaded 6 skills
  and produced a faithful **non-diagnostic** oral-systemic analysis: field-level traceability, the CV axis
  down-rated because the mediator is missing, a **collection-flags block (nothing imputed)**, the full
  disclaimer — and the **reviewer agent passed** ("no issues found"). The guardrail held in the platform's
  own flow.
- **Real MR over OpenGWAS** — verified the study IDs against live `gwasinfo`, then: circulating **CRP → CAD
  null**, **CRP → Alzheimer's nominal +** (partial robustness), **CRP → T2D null + pleiotropy-flagged** —
  honestly *different* from the illustrative panels (CRP is a marker, not the causal node).
- **LD-aware IL-6R cis-MR** — correlated IVW (GLS with the OpenGWAS LD matrix): **IL-6R → coronary disease
  correlated-IVW β = +0.553 (SE 0.109)** — the honest LD-aware estimate; naïve IVW ignores the SNP
  correlation and under-states the variance, so the correlated estimate is the valid one. This is the
  **causal node** the CRP-marker result is null for. Both runs together tell the honest,
  literature-consistent story. *(The estimate corrects an earlier +0.705/SE 0.010 figure that was an LD
  row-ordering bug in `histora.cis_mr` — the OpenGWAS `/ld/matrix` server returns SNPs in genomic-position
  order, and reindexing by request order near-singularized the GLS; fixed, with a regression test.)*

## Delivery decision (in one line)

**Dual, not either/or.** The portable plugin/CLI is the stage-safe spine (offline, deterministic, no
account); Claude Science is the lab-grade home where it *lives* (visuals, connectors, compute, review).
The deterministic engine stays **pinned code** so reproducibility and the non-diagnostic guardrail survive.
See [`internal/CLAUDE-SCIENCE-ANALYSIS.md`](internal/CLAUDE-SCIENCE-ANALYSIS.md) for the full comparison and
[`internal/DATA-AND-DELIVERY.md`](internal/DATA-AND-DELIVERY.md) for the data/genomics rationale.

*Non-diagnostic throughout; population/parameter/instrument level only. Credentials (OpenGWAS token, Modal)
are added by the user in Claude Science — HISTORA never enters or stores them.*
