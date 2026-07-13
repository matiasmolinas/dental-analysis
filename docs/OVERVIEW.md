# HISTORA — Project Overview

> **A non-diagnostic, agentic clinical-research navigator.** It turns fragmented clinical data into a research-ready
> cohort and states, honestly, **what the data cannot answer** — then grounds one falsifiable, calibrated,
> uncertainty-quantified hypothesis in genetics it runs live. Its first instantiated payload is the
> oral–systemic question of global interest: is periodontal inflammation *just a marker*, or a **modifiable,
> treatable, preventable contributing factor** to the shared inflammatory biology behind **heart disease and
> diabetes**? (The Alzheimer's axis stays strictly exploratory — the genetics are null and the direct causal
> trial failed.) One shared inflammatory proxy (excess IL-6 → CRP) links the axes; a calibrated,
> deterministic mechanistic engine turns a case into hypotheses — validated on public data *and* genetics.
> Built with Claude for Life Sciences, co-organized with **Gladstone Institutes**. Hypothesis-generation,
> never a diagnosis or a treatment claim — HISTORA never says treating the mouth prevents disease; it
> prepares the study that could test it.

This document is the guided tour: the **problem** and **objective**, the **technical solution**, the
**autonomous agentic workflow** we built and used to develop it, the **skill-evolution** capability we only
partially exploited, the **flagship case run live in Claude Science**, and the **future directions** we set
aside to focus on the hackathon.

*Front-facing companions: [`PITCH.md`](PITCH.md) (the thesis) · [`CASE-STUDY.md`](CASE-STUDY.md) (the
flagship session) · [`PAPER.md`](PAPER.md) (the technical report) · [`HOW-IT-WAS-BUILT.md`](HOW-IT-WAS-BUILT.md)
(the supervised autonomous build loop) · [`SELF-CORRECTION.md`](SELF-CORRECTION.md)
(the agent finding and fixing a bug in its own flagship number) · [`EVOLUTION.md`](EVOLUTION.md)
(self-improving skills) · [`CLAUDE-SCIENCE.md`](CLAUDE-SCIENCE.md) (run it in a real lab).*

---

## 1. The problem and the objective

### The problem
Gum disease, heart disease, diabetes, and Alzheimer's are studied in **separate silos** — different
specialties, different datasets, different models. Yet a growing body of evidence suggests they may share
one **upstream driver: chronic inflammation**, and specifically the cytokine **interleukin-6 (IL-6)**,
whose hepatic output **C-reactive protein (CRP)** is the clinical footprint. Periodontitis is a lifelong,
modifiable source of that inflammation.

Three things make this hard, and each is a design constraint for HISTORA:

1. **Fragmentation.** Oral and systemic data live apart and are never co-present on one timeline, so the
   cross-domain relationships can't even be *represented*, let alone reasoned about.
2. **Small, honest effect sizes.** Periodontitis is *one contributor among many*. Any tool that inflates
   the signal to look impressive is scientifically dishonest and self-defeating.
3. **The AI honesty gap.** A language model asked to reason over health data will happily hallucinate an
   uncited number, give a point where only a range is warranted, or drift toward an individual diagnosis.

### The objective
Build the **first *safe, transparent, mechanistic* research agent** for oral–systemic disease: an
instrument that turns fragmented structural data into **one falsifiable research line**, where the honesty
is not a disclaimer bolted on but a **structural property** — a *research-integrity gate* whose sharpest
clause is **non-diagnostic** (population/parameter-level out, ranges not points, a missing datum is a
collection flag never imputed, every claim traceable and falsifiable).

The target user is a **scientist working in Claude Science**, not a clinician and not a consumer. The win
is not accuracy — it is **mechanism + honesty**: coherence (one lever, three diseases), calibration (to
real treatment data), and intellectual honesty (uncertainty, falsification, and the reported nulls as
*features*).

![Architecture — Claude reasons; the deterministic engine computes; validation and explanation follow.](assets/architecture.png)

*Who does what: **Claude** decides what to run, how to report uncertainty, and when to route to
falsification; **the deterministic engine** decides the numbers. Claude never sources a headline number.*

### The capability that makes it click — a clinical-research navigator

Two expert clinician-reviewers converged on a sharpening: the researcher arrives with a *question*, not a
patient, and the bottleneck is **assembling a cohort from fragmented records** — weeks of chart review. So
the first thing HISTORA shows is that: it filters a corpus down to the eligible cohort, **flags what's
missing**, and states plainly what the data *cannot* answer — then exports a preliminary protocol.

> **"Researchers don't need another chatbot. They need an AI that builds research-ready cohorts from
> fragmented clinical data."** *IL-6/CRP is today's hypothesis — tomorrow it's another.*

![From fragmented records to a research-ready cohort — a real NHANES funnel + the research-integrity checklist + what the corpus can't answer.](assets/figures/fig_cohort_funnel.png)

*Real over public NHANES 2009-2010 (`demo/run_cohort.py`, nothing synthetic): **20,905 → periodontitis →
+diabetes → +hs-CRP → a cohort of 442.** The corpus is cross-sectional, so HISTORA says what it can't do —
no repeat CRP, no follow-up, no biologic-exposure timeline — as collection flags, never imputed. That honest
"cannot answer," on real data, is the differentiator. The mechanism (below) and the genetics enter **after**,
as the biological plausibility that makes the cohort worth building.*

---

## 2. The technical solution

### One shared proxy, three axes
The spine is a single calibrated parameter. A periodontal source raises **IL-6**; IL-6 → **CRP** is the one
uncertain edge, pinned (`ε`) to a *real interventional anchor* — the meta-analytic **ΔhsCRP after
periodontal therapy (~0.5 mg/L)**. From that shared inflammatory gain, three axes fork **coherently**: one
intervention moves all three together, not three independent guesses.

![One lever, many axes — the calibrated CV/metabolic axes kept visually separate from the EXPLORATORY neuro axis.](assets/figures/fig_stage3_one_lever.png)

*The integrative panel. The neuro axis is drawn **separately and marked EXPLORATORY** so its numbers can
never be quoted as a calibrated result — the honesty is in the figure, not just the caption.*

### Mechanistic depth (Stage-3)
Each axis is a real, tested, non-diagnostic model — not a linear multiplier:

| Axis | Model | What it shows |
|---|---|---|
| Inflammatory core | reduced Reynolds/Kumar TNF/IL-6/IL-10 ODE | **two basins** — acute/resolving vs chronic (bistability the single scalar can't express) |
| Cardiovascular | Ougrinovskaia foam-cell atherosclerosis ODE | plaque as a **process**, not an index |
| Metabolic | Bergman glucose–insulin minimal model | S_I degraded by inflammation → HbA1c, calibrated to the ~0.35 pp therapy anchor |
| Diabetes↔perio | closed feedback loop | a **fixed point** — hyperglycaemia amplifies the source, the source raises the gain |
| Neuro *(exploratory)* | Hao–Friedman amyloid + Braak tau front | the A/T cascade, **flagged**, APOE4/age as effect modifiers |

<p align="center">
  <img src="assets/figures/fig_stage3_inflammation_phase.png" width="46%" alt="Inflammatory phase portrait — two basins"/>
  <img src="assets/figures/fig_stage3_tau_front.png" width="46%" alt="Braak tau front — EXPLORATORY"/>
</p>
<p align="center">
  <img src="assets/figures/fig_stage3_perio_loop.png" width="40%" alt="Diabetes-periodontitis fixed-point cobweb"/>
  <img src="assets/figures/fig_stage3_cv_plaque.png" width="52%" alt="CV foam-cell plaque trajectory"/>
</p>

*Left→right: the two inflammatory basins; the tau front advancing on the Braak chain (marked EXPLORATORY —
read the shift, not the absolute years); the diabetes↔perio loop converging to a fixed point; the foam-cell
plaque process.*

### The protein layer — grounding the mechanism in molecules
The shared proxy is grounded in real molecular identity: **IL-6 → IL-6Rα / gp130 → CRP**, with
**tocilizumab** (an IL-6Rα-blocking antibody) marking the causal node. Every mediator carries its **UniProt
accession** — the stable key the Claude Science UniProt/PDB connector resolves into live 3-D structures.

![The IL-6 signaling axis with UniProt/PDB IDs and the tocilizumab blockade node.](assets/figures/fig_stage3_proteins.png)

### Validation — the "whether", independent of the calibration
- **NHANES** (public, de-identified): the three predicted directions are real and **survive design-adjusted
  (survey-weighted + FDR)** statistics.
- **Mendelian randomization** (public GWAS): **IL-6R → coronary disease is causal**; **circulating CRP →
  CAD is null** — the marker isn't causal, the *node* is; and **CRP/IL-6 → Alzheimer's is null**, which is
  why the neuro axis stays exploratory.

> **Calibration ≠ validation.** Calibration pins the one uncertain edge to an *interventional* anchor;
> validation is the independent NHANES signs and the genetic probe. We never present one as the other.

### The research-integrity gate (non-diagnostic by construction)
Every output is checked against a **protected invariant**: no diagnosis or individual claim; no imputed
patient value (missing → collection flag); evidence-grounded and schema-valid; population/parameter-level.
This gate is enforced as a hard binary check and — crucially — it sits **outside** the part of the system
Claude is allowed to self-edit (see §4).

### Delivery — two surfaces, one engine
A portable **Claude Code plugin** (the demo a judge runs anywhere) and its lab-grade home **Claude
Science**, where the same `skills/` become skills, the `histora` harness a reusable pipeline, the `agents/`
specialist agents, and UniProt/PDB/OpenGWAS/NHANES the connectors — the same components, ported directly.

---

## 3. The development workflow — an autonomous agentic system

The build itself is an artifact of this project. HISTORA was developed and operated by an **autonomous
agentic system** under human direction, exercising Claude at **every layer**:

- **Director (human).** A bioengineer + AI engineer sets the goals, validates, makes the judgment calls,
  and steers — approving risks, choosing anchors, and vetoing scope.
- **Builder + self-optimizer (Claude Code).** An autonomous agent that **proposes, rewrites its own
  skills, investigates, self-corrects, and consults** the director on genuinely open decisions. It authored
  the engine, the tests, the docs, and the SkillOpt loop, iterating through pull requests.
- **Operator (Claude Code → Claude-for-Chrome → Claude Science).** The same agent **deploys and operates**
  the project: it drives the Claude-for-Chrome plugin to run HISTORA inside Claude Science (a local web
  app), importing the skills, reinstalling the engine, running the pipeline, and driving the UniProt/PDB
  and OpenGWAS connectors.
- **Scientist-user (Claude, inside Claude Science).** Claude acts as a **qualified user** that evaluates
  the work, renders the figures and 3-D structures, and — through the **reviewer agent** — audits the
  outputs, *finds real flaws*, and prompts corrections.

```
        ┌─────────────┐   directs / validates / decides
Human ──┤  Director   ├───────────────────────────────────────────┐
        └─────────────┘                                            │
              ▲ consults on open decisions                         ▼
        ┌───────────────────────────┐   deploys & operates   ┌───────────────────┐
        │  Claude Code               │ ─────────────────────► │  Claude Science    │
        │  builder · self-optimizer  │  via Claude-for-Chrome │  operator ·        │
        │  (proposes, rewrites,      │ ◄───────────────────── │  scientist-user +  │
        │   investigates, corrects)  │   results / findings    │  reviewer agent   │
        └───────────────────────────┘                        └───────────────────┘
```

Every claim above is **evidence-linked, not narrated**: the SkillOpt archive (§4), the live Claude Science
run (§5), and the reviewer agent's real audit findings. This meta-role — Claude as builder, self-optimizer,
operator, *and* scientist-user — is the differentiator for a **builder track**; the science leads, and this
workflow is what reframes it as *"and Claude built and operates all of this, too."*

---

## 4. Skill evolution (SkillOpt) — a capability we only partially exploited

HISTORA can **improve its own reasoning skills**, safely. **SkillOpt** is a gated evolutionary loop: Claude
proposes an edit to one of its trainable `SKILL.md` files; the edit is **adopted only if** it *measurably*
improves a machine-checkable structural metric (bootstrap CI excludes 0) **AND** the non-diagnostic
guardrail still passes on **every** case (a hard binary gate). Every generation — adopted and rejected — is
appended to an **auditable archive** with parent→child lineage and the **guardrail hash**, identical in
parent and child: machine-checkable proof the safety invariant never moved.

**Why it's safe by construction:** the *genome* is only the prose of the trainable skills; the guardrail,
the citation registry, and the engine are **outside** it — evolution literally cannot reach them.

**What we ran (the honest portfolio):** live, with Claude as the mutation operator and a Claude agent as
the scored reasoner, across three real skills —

| Skill | Metric | Outcome | Pattern |
|---|---|---|---|
| `traceability-audit` | field-citation coverage | **adopted** 0.00 → 0.93 | knowledge_gap |
| `cardiometabolic-framing` | pathway-tag coverage | **adopted** 0.00 → 0.67 | **execution_gap** |
| `record-normalization` | MISSING-flag recall | **null** — parent already optimal | — |

Two skills improved *by different mechanisms*; one was **correctly left alone** because it was already at
ceiling. That the loop **doesn't manufacture a gain where none exists** is the anti-reward-hacking property
that makes the adopted gains credible.

**What we deliberately left out (hackathon time + safety discipline):** we did **not** run multi-generation
"optimize each skill to its maximum," and we did **not** build an ensemble co-optimization across all skills.
Both are trainable in principle — but "optimize to the maximum" is, by definition, the reward-hacking
behavior the whole design is built on *not* doing, and an ensemble-level metric would have to be
model-judged or hand-designed, breaking the "fitness is external/structural" safety layer. We froze the
portfolio at three: two adopted, one null. Extending this *safely* is a future direction (§6).

---

## 5. The documented case — run live in Claude Science

We ran the **flagship case** end-to-end inside Claude Science, on the current `main` engine, with the real
connectors. This is *"scripted like a demo, real like an experiment"* — the path is real; nothing is faked.
The screenshots below are the actual session.

![The human directs; Claude updates the engine to the latest main, rebuilds, and runs the case study.](assets/claude-science/01-workflow-directive.png)

*The workflow: a directive in, and Claude — as operator — updates the pinned engine and runs the pipeline.*

### The case and the research line (real engine output)
A structural stratum — **Stage III periodontitis · high BOP · type-2 diabetes · hs-CRP MISSING → collection
flag**. The engine forks the shared proxy to three axes as **90% ranges**:

| Output | Median | 90% band |
|---|---|---|
| CRP (mg/L) | 3.18 | [2.89, 3.45] |
| HbA1c shift (pp) | +0.49 | [0.27, 0.71] |
| tau-α rel. increase | +0.21 | [0.11, 0.40] · **EXPLORATORY** |

**The falsifiable research line it generates** (the safe anchor):
- **Lever = periodontal therapy** (non-pharmacological, the exact edge the engine is calibrated on) —
  predicted **ΔhsCRP 0.68 mg/L**.
- **Causal node = IL-6R.** cis-MR: **IL-6R → CAD causal** (LD-aware correlated-IVW β ≈ +0.553, SE 0.109);
  **circulating CRP → CAD null**. **Tocilizumab** (IL-6Rα blockade) is cited **only** as proof the node is druggable/causal —
  **never as a treatment.**
- **Hypothesis:** if the IL-6R node mediates the systemic effect, lowering the periodontal IL-6 source
  should move the markers in the direction the genetics implies — *a testable research line, not a therapy.*
- **Ships its own refutation** (therapy fails to lower hs-CRP → calibration wrong; no IL-6R coronary effect
  → node premise fails; marker moves opposite → mediation refuted) and **names its shakiest assumption**
  (population→stratum transfer, untested).

Claude Science **verified every honesty red-line programmatically** against `case_study.json` ✓.

![The engine ranges, the genetic node (IL-6R→CAD causal, CRP→AD null), and the falsifiable research line — beside the live IL-6R hexamer structure.](assets/claude-science/02-research-line.png)

*The science, live in Claude Science: the engine's 90% ranges, the MR node, and the falsifiable research
line, next to the IL-6/IL-6Rα/gp130 hexamer (1P9M) rendered in the interactive Mol\* viewer.*

### The molecular node — real 3-D structures via the UniProt/PDB connector
The connector resolved all six UniProt accessions and rendered real coordinates in the interactive Mol\*
viewer — including the **IL-6/IL-6Rα/gp130 hexameric signaling complex (PDB 1P9M, 5,322 atoms)**: the causal
node itself, in one structure, where the IL-6R cis-MR instrument acts and tocilizumab blocks.

<p align="center">
  <img src="assets/1alu_structure.jpeg" width="30%" alt="IL-6 (PDB 1ALU)"/>
  <img src="assets/1p9m_structure.jpeg" width="30%" alt="IL-6/IL-6Rα/gp130 hexamer (PDB 1P9M)"/>
  <img src="assets/1gnh_structure.jpeg" width="30%" alt="CRP (PDB 1GNH)"/>
</p>

> IL-6 (`1ALU`, four-helix bundle) → **IL-6/IL-6Rα/gp130 hexamer (`1P9M`)** → CRP (`1GNH`, pentamer) —
> the causal node in real coordinates. These render **interactively in Claude Science** (via the UniProt/PDB
> connector) as the live 3-D upgrade of the static schematic in §2; the structure images above are the same
> PDB entries. *Structure images: RCSB PDB (rcsb.org).*

### The scientist-user beat — the reviewer found a real (minor) error, and Claude self-corrected
The Claude Science **reviewer agent** audited the run and returned **one finding**: the closing prose stated
the hexamer's resolution as *"2.4 Å"*, but 1P9M is **3.65 Å** (2.4 Å belongs to `1N26`, a different,
non-hexameric IL-6Rα structure). The saved manifest already recorded the correct 3.65 Å — only the chat
prose slipped. **Claude read the finding and corrected itself** immediately. Nothing downstream was affected.

This is the honesty loop working in the open: a qualified reviewer catches a real slip, the agent fixes it,
and the record stays accurate — *shown, not dramatized.* (An earlier Stage-3 run had a similar honest
finding, since resolved.)

![The reviewer agent's finding and Claude's self-correction — "1P9M is 3.65 Å… only my closing prose misstated it" — with the hexamer structure and "All 2 findings fixed".](assets/claude-science/04-reviewer-finding-hexamer.png)

*The scientist-user beat, captured live: the reviewer flags the resolution slip, Claude self-corrects, and
the panel reads **"All 2 findings fixed."** The honesty is in the loop, not a caption.*

---

## 6. Future directions — what we set aside to focus on the hackathon

Everything below is deliberately **out of scope for the hackathon** but is a natural, honest extension:

- **Safe multi-generation SkillOpt + ensemble.** Extend the loop beyond one gated generation *without*
  losing the anti-reward-hacking discipline — e.g. loop-until-dry with per-skill external metrics and an
  ensemble metric that stays structural/held-out, never model-judged.
- **More axes and mechanisms.** The model library holds cited-but-unbuilt models (renal, hepatic, further
  microbiome/keystone dynamics) ready to promote to tested code under the same tier discipline.
- **Live connectors at lab scale.** Run the harness and the UniProt/PDB/OpenGWAS/NHANES connectors at scale
  in Claude Science (a natural fit for Anthropic's AI-for-Science program), with native animated figures.
- **Secondary research lines (honest, non-leading).** Behavioral / prophylactic interventions that alter
  oral physiology; the *P. gingivalis* / gingipain → tau microbiome line (kept out of the lead because it
  adds new science and lives on the exploratory neuro axis) — as additional falsifiable hypotheses, never
  efficacy claims.
- **Prospective validation design.** The tool's whole purpose is to *pose* a study; a natural next step is
  to specify the design (cohort, endpoints, refutation criteria) that would test the IL-6R-mediation
  hypothesis it generates — moving from MR-supported *direction* toward interventional evidence.
- **Behavioral trace diagnostics.** Analyzing the agent's own short- and long-term reasoning traces to find
  and correct systematic defects — an internal-quality research track we scoped but did not build.

---

*Non-diagnostic throughout · population / parameter / molecular / instrument level only · MR ≠ RCT ·
calibration ≠ validation · hypothesis-generation, never efficacy, prevention, or diagnosis. Not medical
advice — a research instrument.*
