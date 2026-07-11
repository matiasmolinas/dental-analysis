# Data, genomics/proteomics, and delivery — analysis

> Answers three questions for Stage 2: **(1) do we need an additional dataset?** **(2) do genetics /
> protein prediction / protein databases make sense to incorporate?** **(3) what is the best way to
> deliver the tool** (Claude Code plugin vs. an app vs. Claude Science)? Written under the same discipline
> the external review demanded: **only additions that strengthen the existing shared-proxy thesis earn
> in-scope status; everything else is roadmap or decoration.** Non-diagnostic throughout — genetics is
> used at the population/instrument level, never to assign risk to an individual.

## 0. The scope guardrail for this analysis

The review's #1 weakness was *scope too broad*. So the test for any new data/model is strict: **does it
make the ONE thesis (a single inflammatory proxy causes three systemic consequences) more credible?** If
yes → in-scope. If it adds a new modeling target (fold a protein, a new disease) → roadmap or decoration,
explicitly labeled. This keeps genomics from becoming the shiny distraction the review warned against.

## 1. Do we need an additional dataset?

**For the core hackathon thesis — no.** NHANES already validates the three predicted directions, and the
review asked us to *narrow*, not widen. But three targeted additions would strengthen credibility, ranked
by value ÷ feasibility:

| Addition | What it buys | Feasible in the hackathon? | Gladstone fit |
|---|---|---|---|
| **A. Mendelian randomization** (public GWAS summary stats: IL-6R/CRP instruments → CAD, T2D, AD, cognition) | Turns the project's **central assumption** — *inflammation is causal, IL-6 is the proxy* — into a **genetic causal probe**. This is the "external evidence" the review asked for (R6). | **Yes** — two-sample MR runs on public summary statistics (OpenGWAS / GWAS Catalog); inverse-variance-weighted MR is computable in pure Python from betas/SEs. No individual data, no heavy compute. | Genomic Immunology (inflammation genetics) + Data Science & Biotech |
| **B. APOE4 as an effect-modifier** of the existing neuro axis | The single most Gladstone-central genetic variable; stratifies (not replaces) the neuro module. | **Roadmap** — needs individual genotype+outcome data (ADNI/dbGaP application); public NHANES does not release genotypes. | Neurological Disease (Huang lab, APOE4) |
| **C. Protein/sequence databases** (UniProt, PDB, Ensembl, ClinVar) | Grounds the mechanism and the **citations** (IL-6, CRP, tau, *P. gingivalis* gingipains → canonical entries) — feeds WS5 citation accuracy. | **Yes** — read-only lookups; native Claude Science connectors. | Data Science & Biotech (proteomics) |

**The standout is A (Mendelian randomization).** It is honest, feasible offline, and it probes the exact
assumption the whole model rests on. Its likely result is itself on-message: MR evidence that **IL-6R
signaling is causal for cardiovascular disease is well established** (the IL-6R MR consortium, mimicking
tocilizumab), while **MR support for CRP/IL-6 → Alzheimer's is weak/null** — which *matches our existing
tiering* (CV/metabolic = data-anchored; neuro = exploratory) and would let us say, with genetics behind
it: *"the causal chain is genetically supported where we claim it strongly (CV) and genetically uncertain
where we flag it as exploratory (AD)."* That is a credibility win, not a risk.

## 2. Genomics / proteomics models — what earns in, what is decoration

| Model / method | Verdict | Why |
|---|---|---|
| **Mendelian randomization** (instrumental-variable causal inference) | **IN-SCOPE (do it)** | Strengthens the shared-proxy thesis with genetics; offline-feasible; honest about assumptions (pleiotropy). |
| **UniProt / PDB / Ensembl / ClinVar lookups** | **IN-SCOPE (grounding only)** | Mechanism + citation provenance; no new modeling. |
| **Protein-structure prediction** (AlphaFold / Boltz-2 / OpenFold3) | **DECORATION / roadmap** | HISTORA is a *systems-level* (ODE/network) model, not molecular. A folded IL-6/IL-6R interface or tau protofilament is an *illustrative visual*, not mechanism. Include only if Claude Science renders it for free; never as a core claim — that is the scope creep the review warned about. |
| **Genomic language models** (Evo 2) | **OUT** | Sequence-level generative genomics is orthogonal to a cytokine-kinetics/systems thesis. |
| **Polygenic risk scores; perio/AD GWAS** | **ROADMAP** | Needs individual genotypes; belongs to the longitudinal/genetics program (R12), not the hackathon. |

**One-line rule:** genetics enters only as a **causal probe of the existing proxy** (MR) or **evidence
grounding** (protein DBs). Protein folding and sequence models stay decoration/roadmap.

## 3. Gladstone alignment map (the "why Gladstone" narrative, with data)

HISTORA touches **four of Gladstone's five institutes** — a strong partnership story:

| Gladstone institute | HISTORA connection |
|---|---|
| **Neurological Disease** (Alzheimer's, tau; Huang/APOE4, Mucke/tau) | The neuro module (neuroinflammation → tau-α → Fisher–KPP), the novel *upstream* perturbation; APOE4 stratification path |
| **Cardiovascular Disease** | The CV axis (IL-6 → CRP → atherogenic index); MR shows IL-6R is causal for CAD |
| **Data Science & Biotechnology** (AI, computational biology, proteomics; Pollard) | The reproducible pure-Python harness + the oral-**microbiome** exposure side; the AI-reproducibility ethos |
| **Genomic Immunology** (inflammation, CRISPR; Marson) | The shared inflammatory proxy; the MR instruments (IL-6R/CRP) |

## 4. Claude Science — what it is, and the delivery recommendation

**What it is** (from the Jun 2026 launch): an AI workbench for scientists — a coordinating agent + 60+
skills/connectors for genomics, single-cell, proteomics, structural biology, cheminformatics; native
rendering of 3D protein structures and genome tracks; a **reviewer agent that checks citations and
calculations and self-corrects**; connectors to UniProt, PDB, Ensembl, Reactome, ClinVar, ChEMBL, GEO;
BioNeMo models (Evo 2, Boltz-2, OpenFold3); pipelines saved as **reusable skills**; runs on laptop / SSH
/ HPC; **auditable, reproducible artifacts** (figure + code + environment + message history).

**The key observation: HISTORA's architecture already mirrors Claude Science.** We have a coordinating
orchestrator, specialist subagents, skills, a **guardrail/reviewer agent**, and reproducible auditable
outputs (envelopes + full traceability). Claude Science is the natural production home — and its
**reviewer agent is literally our agentic-metrics story** (citation accuracy, untraceable-number
detection) built into the platform.

**Recommendation: dual delivery.**

1. **Claude Code plugin — keep it as the portable hackathon-demo surface.** No special account, runs
   anywhere, drives the WS3 live demo. This is what a judge can run.
2. **Claude Science packaging — the "where a real lab runs it" story.** Package HISTORA as Claude Science
   **skills + specialist agents**, save the `histora` harness as a **reusable pipeline/skill**, wire the
   **connectors** (UniProt/PDB for grounding; GWAS for the MR probe), and lean on the **reviewer agent**
   for citation/calculation checking. This directly satisfies the review's *polished interface* (R10) and
   *safe, transparent research acceleration* (F4), and it is the form that resonates with Gladstone +
   Anthropic.

Why not "an app that runs Claude Code"? A bespoke app re-implements what Claude Science already provides
(compute management, reviewer agent, connectors, reproducible artifacts) — effort better spent on the
science. The plugin covers portability; Claude Science covers the lab-grade surface.

**Time-sensitive opportunity:** the **AI for Science program** offers up to **$30,000 in credits** (+ up
to $2,000 Modal compute) for ~50 projects; **applications close July 15, 2026** (projects run Sep 1 – Dec
1, 2026). Given today's date this is imminent — HISTORA is a strong fit (biomedical, reproducible,
safety-forward) and worth a same-week decision.

**Caveat:** Claude Science is **beta** (macOS/Linux; Pro/Max/Team/Enterprise; Team/Enterprise need admin
enablement). So the hackathon cannot *require* it — hence the plugin stays the demo surface, and Claude
Science is the delivery/roadmap target.

## 5. How this folds into the Stage-2 plan (no scope creep)

- **WS5 (agentic metrics)** → add **UniProt/PDB** entries to the claim→source map; note that Claude
  Science's reviewer agent is the platform-native version of our citation-accuracy metric.
- **WS7 (sensitivity + external validation)** → upgrade R6 from a *named* path to a **doable** item:
  a two-sample **MR probe (IL-6R/CRP → CAD / T2D / AD)** on public summary stats, reported honestly
  (including where MR is null for AD — which supports our neuro-as-exploratory tiering).
- **WS8 (delivery + pitch)** → add **Claude Science packaging** as the delivery target, the **Gladstone
  four-institute alignment map**, and the **AI-for-Science grant** action.
- **Unchanged:** no new disease axis; MR strengthens the *existing* proxy; protein folding stays
  decoration/roadmap; the non-diagnostic guardrail extends to genetics (population/instrument level only,
  never individual genetic risk).

## 6. Risks

| Risk | Mitigation |
|---|---|
| Genomics becomes the shiny distraction the review warned about | Hard rule: only MR (causal probe of the proxy) + DB grounding are in-scope; everything else is labeled roadmap/decoration |
| MR assumptions (horizontal pleiotropy) overstated | Report MR with its caveats + sensitivity (MR-Egger/weighted-median); treat as *supporting evidence*, not proof |
| Claude Science beta dependency at demo time | Plugin remains the portable demo surface; Claude Science is delivery/roadmap |
| Individual genetic data access (APOE4/ADNI) assumed hackathon-fast | Keep it explicitly roadmap (dbGaP/ADNI applications are slow) |
| Non-diagnostic guardrail with genetics | Population/instrument level only; never an individual genetic risk or an imputed genotype |

---

*Companion: [`STAGE2-WORKPLAN.md`](STAGE2-WORKPLAN.md) (the executable plan), [`ROADMAP-STAGE2.md`](ROADMAP-STAGE2.md)
(strategy). Non-diagnostic throughout; genetics used at the population/instrument level only.*
