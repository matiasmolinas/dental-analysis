# Stage-2 Work Plan (executable) — HISTORA for the Gladstone × Anthropic hackathon

> The **executable** companion to [`ROADMAP-STAGE2.md`](ROADMAP-STAGE2.md) (strategy). This document turns
> the external review ([`external-review/…Hackathon_Review.md`](external-review/Mechanistic_Research_Agent_for_Oral-Systemic_Disease_Hackathon_Review.md))
> into a task-level plan: a **coverage matrix** proving every review point is contemplated, then per-
> workstream **checklists, deliverables, acceptance criteria, effort, and dependencies**, the **demo
> script**, and the **metric / statistics specs**. Cross-checked with an independent Fable pass.
>
> **Invariant (never traded away):** non-diagnostic — structural bands in, population/parameter-level
> ranges out; a missing datum is a collection flag, never an imputed value; no patient value is ever
> produced or persisted.
>
> **Data, genomics & delivery** (whether we need more data, the genetics/protein angle, and Claude
> Science as the delivery surface) are analyzed in [`DATA-AND-DELIVERY.md`](DATA-AND-DELIVERY.md); its
> actionable conclusions are folded into WS5/WS7/WS8 below.

## How to use this document

- **Status:** ✅ done · ◑ partial (needs finishing) · ○ gap (new work) · ★ preserve/exhibit (already a
  strength — don't rebuild, make it visible).
- **Effort:** S (≤½ day) · M (½–2 days) · L (>2 days).
- **DoD** = Definition of Done: the verifiable condition that closes the task.
- Work the **Must-have** workstreams (WS1–WS6) first, in the §8 sequence. WS7–WS8 are strong nice-to-have.
  WS-R (research track) is **gated**: zero budget until WS1–WS6 close.

---

## 1. Coverage matrix — every review point → where it is handled

The review has 28 discrete points. Each maps to a workstream below. Nothing is orphaned.

### Executive summary
| # | Point | Status | Handled by |
|---|---|---|---|
| ES1 | Simplify / reduce scope | ○ | WS3 (one canonical demo makes breadth the *thesis*, not dispersion) |
| ES2 | Focus the demo on a complete end-to-end scientific workflow | ○ | WS3 |

### Strengths (preserve & exhibit — do not rebuild)
| # | Point | Status | Handled by |
|---|---|---|---|
| S1 | Shared inflammatory-variable hypothesis | ★ | WS2 diagram + WS3 demo make the "one lever → three diseases" explicit |
| S2 | Scientific transparency (anchored / calibrated / scaffold / hypothesis tiers) | ★ | WS1 keeps the tier labels; WS4 hardens the benchmark's transparency |
| S3 | NHANES reproducible public dataset | ★ | WS6 strengthens it (survey design); reproduce commands kept |
| S4 | Claude as orchestrator, not black-box predictor | ★ | WS2 labor table makes the Claude-vs-engine split explicit |
| S5 | Benchmark on coherence / uncertainty / explainability | ★ | WS4 publishes its protocol; WS5 adds the agentic half |

### Weaknesses
| # | Point | Status | Handled by |
|---|---|---|---|
| W1 | Scope too broad for a demo | ○ | WS3 (curate one path; **add zero axes**) |
| W2 | Clarify the IL-6 / CRP / inflammatory-variable flow | ◑ | WS1 (proxy reframe) + WS2 (the flow *is* the diagram) |
| W3 | Calibration must NOT read as external validation | ◑ | WS1 (calibration-vs-validation callout, policed everywhere) |
| W4 | Claude benchmark needs fully reproducible methodology | ◑ | WS4 (protocol: prompts, model id, seeds, C-arm variance) |
| W5 | Alzheimer's axis = exploratory research module | ◑ | WS1 (tier it below the data-anchored CV/metabolic axes) |

### Roadmap to 10/10
| # | Point | Status | Handled by |
|---|---|---|---|
| R1 | Single memorable end-to-end demo | ○ | WS3 |
| R2 | Architecture diagram | ◑ | WS2 |
| R3 | Demonstrate the complete workflow live | ◑ | WS3 (scripted live run + recorded fallback) |
| R4 | Separate Claude's responsibilities from the math engine | ◑ | WS2 (labor table) |
| R5 | Publish benchmark methodology + evaluation protocol | ◑ | WS4 |
| R6 | Validate with external evidence or sensitivity analyses | ◑ | WS7 (promote sensitivity now; name external cohorts) |
| R7 | Improve statistical treatment of NHANES | ○ | WS6 (survey weights + FDR + sensitivity) |
| R8 | Describe IL-6 as a latent/shared inflammatory proxy | ◑ | WS1 (rename in prose + code comments) |
| R9 | Agentic-AI metrics (hallucination, uncertainty calibration, citation accuracy, consistency, falsifiability) | ○ | WS5 |
| R10 | Polished visual interface | ◑ | WS8 (reuse the artifact design; thin demo UI) |
| R11 | Why now / Why Anthropic + Gladstone | ○ | WS8 (pitch assets) |
| R12 | Scientific roadmap (longitudinal, genetics, multimodal) | ○ | WS7 (named, honestly out-of-hackathon-scope) |

### Final recommendations
| # | Point | Status | Handled by |
|---|---|---|---|
| F1 | Present as a Scientific Research Agent, not a predictor | ◑ | WS1 (positioning line in every surface) |
| F2 | Emphasize mechanistic reasoning over predictive accuracy | ◑ | WS1 + WS4 (the leaderboard is coherence/calibration, not AUC) |
| F3 | Uncertainty & falsifiability as core product features | ◑ | WS3 demo ends on a falsifiable brief; WS5 metric card |
| F4 | Demonstrate safe, transparent research acceleration | ◑ | WS3 (the whole demo) + the non-diagnostic guardrail on screen |

**Orphans: none.** All 28 points route to WS1–WS8. (WS-R, the research track, is *our* addition beyond the
review.)

**Coverage confidence (independent Fable audit).** A separate Fable pass re-derived this matrix point by
point and found **no strict orphans**, flagging two spots of *weak* coverage to harden — both now folded
in:
- **Citation accuracy (R9)** presupposes an auditable **claim → source** map; if `PAPER.md`/`model-library.md`
  don't already carry it structurally, building it is a **prerequisite micro-task** of WS5 (added below).
- **Multimodal validation (R12)** lives only as future text; the pitch must state explicitly that it is
  *roadmap, not a deliverable* (§10), to avoid creating expectation.

---

## 2. Workstreams (task-level)

Every workstream: **covers** (review IDs) · **goal** · **tasks** (checklist) · **deliverables** ·
**DoD** · **effort** · **deps** · **files**.

### WS1 — Reframe + honesty pass  ·  *must-have*  ·  ◑ **mostly done** (README/MODELS/SOLUTION/plugin reframed + calibration≠validation callout; remaining: full grep sweep + PAPER abstract line)  ·  **effort S**
- **Covers:** F1, F2, F3, F4, W2, W3, R8, W5, S2(preserve).
- **Goal:** every surface opens as a *scientific research agent*, cleanly separates *calibration* from
  *validation*, and describes the shared variable as a *latent inflammatory proxy*.
- **Tasks:**
  - [ ] Adopt one canonical positioning line (research agent, not predictor) as the first sentence of
        `README.md`, `PAPER.md`, `SOLUTION.md`, the plugin README, and the demo's first screen.
  - [ ] Add a **"Calibration vs. Validation"** callout box to `PAPER.md` and the demo: *ε and k are
        **calibrated** to interventional anchors (an input constraint); the **validation** is that the
        three predicted association signs appear, confounder-adjusted, in NHANES.* Grep every doc for
        wording that lets ε/k read as a "result" and fix it.
  - [ ] Rename the shared variable in prose + code comments: **"shared inflammatory proxy (operationalized
        as excess IL-6)"**; add one paragraph in `MODELS.md`/`SOLUTION.md` justifying IL-6 as the
        measurable stand-in for a latent factor (CRP/IL-1β/TNF-α co-move; MR favors IL-6/IL-1β as causal).
  - [ ] Introduce a tier label: CV + metabolic = **data-anchored axes**; neuro = **exploratory research
        module** (gated behind the GAIN-failure + mediator-not-co-measured caveats), set apart visually.
  - [ ] Keep S2's existing tier labels (anchored/calibrated/scaffold/hypothesis) intact.
- **Deliverables:** edited docs; the callout box; the proxy paragraph.
- **DoD:** no doc presents calibration as validation; "research agent, not predictor" is the opening of
  every surface; the neuro axis is visibly an exploratory module; a reader sees "inflammatory proxy," not
  "IL-6 is the mechanism."
- **Deps:** none (do first — unblocks all wording). **Files:** `README.md`, `docs/PAPER.md`,
  `docs/SOLUTION.md`, `docs/MODELS.md`, plugin `README.md`.

### WS2 — Architecture diagram + Claude-vs-engine labor table  ·  *must-have*  ·  ✅ **DONE** (Mermaid diagram + labor table in README; reused in the artifact/demo when built)  ·  **effort S**
- **Covers:** R2, R4, S1, S4, W2.
- **Goal:** one canonical figure a judge reads in 10 seconds, plus an explicit division of labor.
- **Tasks:**
  - [ ] One diagram: **Claude (relational hypotheses) → tools/`case_tools` → mechanistic engine
        (`mech_*`) → validation (NHANES) → explanation (uncertainty + falsifiability)**, showing the
        shared proxy forking to CV/metabolic/neuro.
  - [ ] A two-column table: **Claude decides** *what to run, how to report uncertainty, when to route to
        falsification* · **the engine decides** *the numbers (calibrate, propagate, sweep)*. Include the
        weight-cap on any Claude soft-member.
  - [ ] Render it once (SVG/HTML, theme-aware, reuse the artifact palette) and embed it in `README.md`,
        `PAPER.md`, the one-page artifact, and the demo.
- **Deliverables:** the diagram asset + the labor table.
- **DoD:** the same single diagram appears in README, paper, artifact, and demo; the labor table states
  that Claude never sources a number.
- **Deps:** WS1 wording. **Files:** `docs/assets/architecture.*`, `README.md`, `docs/PAPER.md`, artifact.

### WS3 — The canonical end-to-end demo  ·  *must-have*  ·  **effort M**  ·  the centerpiece
- **Covers:** ES1, ES2, W1, R1, R3, F3, F4, S1(exhibit), S5(exhibit).
- **Goal:** one anonymized case → hypotheses → uncertainty-quantified mechanism → NHANES validation →
  falsifiable brief, in ~3 minutes, reproducible with one command. Breadth becomes the punchline.
- **Tasks:** (detailed script in §3)
  - [ ] Freeze one canonical synthetic case (structural bands only) in `demo/case.json`.
  - [ ] Wire the run: input → `agent` (relational, labeled "Claude") → `case_tools` (engine, envelopes +
        counterfactual) → the three NHANES signs (labeled "validation, not calibration") → the falsifiable
        brief + metric card + caveats.
  - [ ] One command (`python demo/run_demo.py` or the `/evaluate-case` flow on the fixed case) produces
        the full brief; a "print" button emits the one-page PDF we already generate.
  - [ ] Record a 3-minute walkthrough as a fallback if the live model arm misbehaves on stage.
  - [ ] On-screen guardrail moments: the missing mediator shown as a collection flag; the neuro block
        badged "exploratory module."
- **Deliverables:** `demo/` (case + runner + README), the recording.
- **DoD:** a first-time viewer runs one command and sees all five stages with uncertainty bands and a
  falsification condition; the calibration/validation split is visible; nothing diagnoses.
- **Deps:** WS1 (framing), WS2 (diagram on the first screen). **Files:** `demo/*`, reuses `histora.*`.

### WS4 — Benchmark reproducibility protocol  ·  *must-have*  ·  ✅ **DONE**
- **Covers:** W4, R5, S5(exhibit), F2.
- **Goal:** turn the benchmark from a claim into a verifiable result.
- **Tasks:**
  - [ ] Pin the protocol in `BENCHMARK.md`: exact model id, verbatim prompts for arms S/C/H, seed
        manifest, and the panel definition.
  - [ ] Handle arm C's non-determinism: run N times, report mean ± variance (as the M6 probe already
        does); document the N and the seed handling.
  - [ ] Give each metric M1–M7 an operational definition + a worked scoring example.
  - [ ] One-command reproduce: `python src/run_benchmark.py --live --seed …` writing a stamped report;
        note which numbers are deterministic (S/H) vs live (C).
- **Deliverables:** expanded `BENCHMARK.md` §Protocol; a seed manifest.
- **DoD:** a stranger can reproduce S/H exactly and C within reported variance from the doc alone.
- **Deps:** none. **Files:** `docs/BENCHMARK.md`, `src/run_benchmark.py`, `src/histora/benchmark.py`.

### WS5 — Agentic-AI metrics (offline)  ·  *must-have*  ·  ✅ **DONE** (offline; live consistency remains)
- **Covers:** R9, F3.
- **Goal:** a reproducible metric card: hallucination rate, citation accuracy, uncertainty calibration,
  consistency, falsifiability, guardrail — attributed across arms S/C/H. (Spec in §4.)
- **Tasks:**
  - [ ] **Prerequisite (Fable-flagged):** build an auditable **claim → source** map — a structured table
        mapping each numeric anchor (ΔCRP≈0.5, ΔHbA1c≈0.35, the NHANES coefficients, CRP t½=19h, α_tau…) to
        its reference key, including **UniProt/PDB** entries for the mechanism proteins (IL-6, CRP, tau,
        gingipains) — see [`DATA-AND-DELIVERY.md`](DATA-AND-DELIVERY.md) §1C. Citation accuracy cannot be
        scored without this source-of-truth; do it first.
  - [ ] `histora/agent_metrics.py` + `run_agent_metrics.py`.
  - [ ] **Citation accuracy** (offline): each cited claim resolves to a real reference key **in the map
        above** that supports it; check against `model-library.md`/`PAPER.md`.
  - [ ] **Hallucination rate** (offline check of a live transcript): every quantitative claim maps to an
        engine field, a citation, or a flagged hypothesis — else it's a hallucination.
  - [ ] **Uncertainty calibration** (offline): (a) coverage — do the 90% envelopes contain the real
        anchors (ΔCRP≈0.5, ΔHbA1c≈0.35)? (b) honesty — is ε flagged as the most-uncertain edge,
        consistent with the sensitivity ranking?
  - [ ] **Consistency** (live, small n): same case × N runs → rank-stability + axis-sign-flip rate, with
        variance reported.
  - [ ] Surface **falsifiability** (M7) and **guardrail** (M6/W1) in the same card.
- **Deliverables:** the module + a `results/agent_metrics.json` + a card in `PAPER.md`/the demo.
- **DoD:** every metric ships with a seed/manifest; offline metrics are deterministic; the live metric
  reports its n and variance; each is shown for S/C/H so the harness's contribution is attributable.
- **Deps:** WS4 (shares the benchmark harness) + the claim→source map (first task above, gates citation
  accuracy). **Files:** `src/histora/agent_metrics.py`, `src/run_agent_metrics.py`, `docs/PAPER.md`,
  `docs/CITATIONS.md` (the claim→source map).

### WS6 — NHANES statistical hardening  ·  *must-have*  ·  ✅ **DONE**
- **Covers:** R7, S3(strengthen), F2.
- **Goal:** design-adjusted statistics a survey statistician respects.
- **Tasks:**
  - [x] Survey design added to the NHANES loaders (`WTMEC2YR`, `SDMVSTRA`, `SDMVPSU`); design-adjusted
        coefficients reported **beside** the unweighted ones.
  - [x] Design-based variance via a **cluster bootstrap** (resample PSUs within stratum) — the standard
        practical bootstrap for the stratified two-PSU design; documented as the chosen method.
  - [x] **Multiplicity:** joint **Benjamini–Hochberg FDR** across all 7 outcomes.
  - [x] **Sensitivity:** CAL vs PPD exposure re-run in the same report.
  - [x] Honest attenuation reported: CRP/CV/HbA1c + processing-speed **survive**; two weaker cognition
        measures attenuate and drop under FDR (design-adjusted cognition = 2/4, not 3/4) — written into
        `PAPER.md` §4.2. `histora.nhanes_survey` + `run_nhanes_weighted.py`; 6 tests on synthetic truth.
- **Deliverables:** `histora/nhanes_survey.py`; a weighted-vs-unweighted + FDR + sensitivity table in
  `PAPER.md`.
- **DoD:** every NHANES coefficient is reported design-adjusted with an FDR verdict and a 4-spec
  sensitivity row; any attenuation is stated, not hidden.
- **Deps:** none (independent). **Files:** `src/histora/nhanes.py`, `src/histora/nhanes_survey.py`,
  `src/run_perio_*.py`, `docs/PAPER.md`. **Risk:** an effect may weaken under weighting — report it
  honestly (on-message for the reframe).

### WS7 — Sensitivity + external evidence (incl. Mendelian randomization)  ·  *nice-to-have (MR is high-value)*  ·  **effort S–M**
- **Covers:** R6, R12. **See** [`DATA-AND-DELIVERY.md`](DATA-AND-DELIVERY.md) §1–2.
- **Goal:** satisfy "sensitivity analyses" today; add a **genetic causal probe** of the shared proxy; name
  the longitudinal program honestly.
- **Tasks:**
  - [ ] Promote the existing LHS + one-at-a-time elasticities (`ensemble.py`) into a `PAPER.md` figure;
        add a Sobol total-order index if cheap.
  - [x] **Mendelian randomization probe — ✅ PROTOTYPED.** Pure-Python two-sample MR
        (`histora.mendelian_randomization`: IVW + MR-Egger + weighted-median + Cochran's Q; 6 tests on
        synthetic ground truth) with a runner (`src/run_mendelian_randomization.py`). Illustrative,
        literature-directional panels reproduce the established result: **IL-6R → coronary disease =
        causal** (IVW β=+0.105, p<0.001, no pleiotropy flag); **CRP/IL-6 → Alzheimer's = null** (p=0.91) —
        genetics that independently supports the CV/metabolic-anchored vs. neuro-exploratory tiering.
        *Remaining (funded scope):* swap the illustrative panels for live OpenGWAS/GWAS-Catalog extracts +
        MR-PRESSO/leave-one-out. Population/instrument level only — never an individual genetic risk.
  - [ ] Write the **scientific roadmap** (§10): longitudinal cohorts (e.g. ARIC) for temporal ordering +
        fitting γ/β_tau/β_si; genetics (APOE4 stratification — needs ADNI/dbGaP, roadmap); multimodal
        (tau-PET/ADNI; inflammatory panels). Label it clearly as *not done* — the program the agent feeds.
- **DoD:** a sensitivity figure is in the paper; the external roadmap is written and honestly out of
  hackathon scope. **Deps:** none. **Files:** `docs/PAPER.md`, `docs/ROADMAP.md`.

### WS8 — Delivery + polished interface + pitch assets  ·  *nice-to-have*  ·  **effort S/M**
- **Covers:** R10, R11. **See** [`DATA-AND-DELIVERY.md`](DATA-AND-DELIVERY.md) §3–4.
- **Goal:** decide the delivery surface, ship a thin honest demo, and write the framing narrative.
- **Tasks:**
  - [ ] **Delivery decision — dual:** keep the **Claude Code plugin** as the portable hackathon-demo
        surface; package HISTORA for **Claude Science** (skills + specialist agents + the `histora` harness
        saved as a reusable pipeline; connectors UniProt/PDB + GWAS; the platform reviewer agent as the
        native citation/calc check) as the lab-grade delivery/roadmap target. *Do not* build a bespoke app.
  - [ ] Add the **Gladstone four-institute alignment map** (Neuro/CV/Data-Science/Genomic-Immunology) to
        the pitch — HISTORA touches 4 of 5 institutes.
  - [ ] Evaluate the **AI-for-Science program** (up to $30k credits; applications close **Jul 15, 2026**)
        — time-sensitive decision this week.
  - [ ] Refine the one-page artifact/PDF; ensure the WS2 diagram and the metric card are on it.
  - [ ] Write **Why now / Why Anthropic + Gladstone** (draft in ROADMAP-STAGE2 §8) into README + a slide.
  - [ ] Optional thin demo UI (only after WS1–WS6) reusing the artifact palette — not a product.
- **DoD:** the delivery decision is documented; the artifact carries the diagram + metric card; the
  why-now/why-partners text + Gladstone map are in the README and pitch. **Deps:** WS2, WS5.
  **Files:** artifact HTML, `README.md`, plugin manifest.

### WS-R — Behavioral Trace Diagnostics  ·  *research track, gated*  ·  **effort M**
- **Covers:** beyond the review — the Jacobian-lens-via-observable-traces idea.
- **Full spec:** [`ROADMAP-STAGE2.md` §11](ROADMAP-STAGE2.md). **Gate:** zero budget until WS1–WS6 close.
- **One-line DoD:** the harness detects a recurring omission in its own benchmark traces, externalizes the
  fix into a sub-agent template, and a **W1-standard measured experiment** (guardrail/M-metric ↑, with a
  prose-vs-enforcement control and a pre-registered kill criterion) shows externalization — not prose —
  moves the number; consolidation persists **only workflow patterns/templates, never a patient value**.

---

## 3. The canonical demo — full script (WS3)

**Case (frozen):** stage III periodontitis, high BOP, diabetic — represented **only** as structural
bands/flags; hs-CRP and HbA1c marked MISSING (to show the collection-flag behavior).

| Step | On screen | Command / source | Narration | Guardrail moment |
|---|---|---|---|---|
| 0 | The WS2 architecture diagram | — | "One inflammatory proxy, three diseases, one engine." | "Research agent — never a diagnosis." |
| 1 | The record (bands only); MISSING labels | `demo/case.json` | "Structural stratum in — no patient numbers." | Missing hs-CRP → **collection flag**, not imputed. |
| 2 | Claude's relational hypotheses, each citing input fields | `histora.agent` | "Claude decides *what* to run and routes ε to calibration — it does not invent numbers." | Labeled "Claude — reasoning." |
| 3 | Engine: CRP / HbA1c / tau-α as **envelopes** + sensitivity + the therapy counterfactual | `case_tools` | "The engine calibrates ε to the real ΔCRP anchor, then propagates one proxy to three axes." | Output is a **band**, not a point. |
| 4 | The three NHANES signs with bootstrap CIs, in a panel labeled **"validation ≠ calibration"** | stored results | "Independent public-data validation of the predicted directions." | The mediator-not-co-measured caveat printed. |
| 5 | Ranked hypotheses, each with a **falsification condition**; the **agentic metric card**; caveats (GAIN, small effects) | WS5 card | "Here is the most fragile assumption and exactly what would refute it." | Neuro block badged "exploratory module." |
| 6 | "Print" → the one-page PDF | existing generator | — | — |

**Live-vs-recorded:** run live if the model arm is stable; keep the recording as the stage fallback.

---

## 4. Agentic-AI metrics spec (WS5)

| Metric | Definition | Method | Run | DoD |
|---|---|---|---|---|
| Citation accuracy | cited claims resolving to a real, supporting reference | match each cite to `model-library.md`/`PAPER.md` keys | offline | deterministic, ≥ threshold reported per arm |
| Hallucination rate | quantitative claims not traceable to engine / cite / flagged hypothesis | parse output; map each number to a source | offline (on a live transcript) | every number classified; rate reported per arm |
| Uncertainty calibration | (a) 90% envelopes cover the real anchors; (b) ε flagged as most-uncertain | coverage check + reliability bucket | offline | coverage % + honesty pass reported |
| Consistency | rank-stability + axis-sign-flip over N runs of one case | N live runs, report variance | live (small n) | n and variance stated |
| Falsifiability | fraction of hypothesis claims shipping a refutation (M7) | reuse benchmark | offline | surfaced in the card |
| Guardrail | non-diagnostic + no imputation + traceability (M6 / W1) | reuse `ab_eval` | offline / live probe | surfaced in the card |

**Rule:** report each metric for **S / C / H** so improvement is attributable to the *harness*, not the
model. Honesty note (carried from the benchmark): on *overt* adversarial cases a frontier model already
refuses — the harness's measured edge is the *subtle* execution-gap step, not overt blocking.

---

## 5. NHANES statistical hardening spec (WS6)

- **Design variables:** `WTMEC2YR` (exam weight), `SDMVSTRA` (strata), `SDMVPSU` (PSU). Weighted point
  estimates; design-based variance (Taylor/BRR if feasible, else bootstrap + stated caveat).
- **Report both** weighted and unweighted coefficients side by side.
- **Multiplicity:** BH-FDR across {CRP, CV-history, HbA1c, 4 cognition outcomes}; mark survivors.
- **Sensitivity:** each headline coefficient across CAL vs PPD × confounder set × inclusion rule (≥4 rows).
- **Honesty:** if weighting attenuates or flips a sign, report it — it is consistent with the "small,
  one-contributor-among-many" reading and with the research-agent framing.

---

## 6. Pitch assets (WS2/WS8)

- **Architecture diagram** — the WS2 asset, reused everywhere.
- **Calibration-vs-validation callout** — the WS1 box (reused on the demo's step 4).
- **Positioning line** — "HISTORA helps a researcher form and prioritize falsifiable oral–systemic
  hypotheses, with explicit mechanism and honest uncertainty — it does not predict or diagnose disease."
- **Why now / Why Anthropic + Gladstone** — drafted in [`ROADMAP-STAGE2.md` §8](ROADMAP-STAGE2.md);
  finalize into README + one slide.

---

## 7. Research track

See [`ROADMAP-STAGE2.md` §11](ROADMAP-STAGE2.md) (Behavioral Trace Diagnostics) — gated behind WS1–WS6.

---

## 8. Sequencing & milestones

Ordered by impact ÷ effort; each milestone is independently shippable.

1. **M0 — Framing locked (½ day):** WS1 + WS2. *Unblocks all wording and the demo's first screen.*
2. **M1 — The demo runs (1–2 days):** WS3 end-to-end on the frozen case + the recorded fallback.
3. **M2 — The benchmark is verifiable (1 day):** WS4 protocol pinned + one-command reproduce.
4. **M3 — The metric card exists (1–2 days):** WS5 offline metrics for S/C/H + the live consistency run.
5. **M4 — The stats are design-adjusted (1–2 days):** WS6 weights + FDR + sensitivity table.
6. **M5 — Pitch polish (½–1 day):** WS7 sensitivity figure + roadmap; WS8 why-now + artifact refresh.
7. **M6 — (gated) Research preview:** WS-R only if M0–M5 are closed; report honestly (incl. as a negative).

**Critical path to a strong pitch:** M0 → M1 → M2/M3/M4 (parallelizable) → M5.

---

## 9. Definition of Done (Stage 2) + risk register

**Stage-2 DoD:** a judge watches one 3-minute demo (case → Claude's hypotheses → the engine's
uncertainty-quantified mechanism → NHANES validation → falsifiable brief), backed by a **reproducible
agentic-AI metric card** and **design-adjusted NHANES statistics**, framed throughout as a **safe
scientific research agent**, with **calibration visibly separated from validation** and the **neuro axis
tiered as exploratory** — and every review point in §1 marked ✅.

**Risk register:**
| Risk | Mitigation |
|---|---|
| Calibration read as validation (W3) — the fastest way to lose a scientific judge | WS1 callout, policed by grep; separated on the demo's step 4 |
| Overclaiming the Alzheimer's axis (W5) | tier it exploratory; keep the GAIN caveat loud |
| Scope creep / a new axis (W1) | **add zero biological axes**; deepen & exhibit only |
| Survey weighting weakens a result (WS6) | report honestly; it is on-message, not a failure |
| Research track reintroduces removed lens/memory work, or persists patient values | WS-R gated + offline-reproducible + consolidation persists only patterns/templates (see §11) |
| Live model arm misbehaves on stage | the WS3 recorded fallback |
| Agentic metrics not reproducible | seeds/manifest; offline where possible; live reports n + variance |

---

## 10. Scientific roadmap (WS7 — future work, honestly out of hackathon scope)

- **Longitudinal cohorts** (e.g. ARIC: periodontal exams + incident CV/cognitive outcomes) → move from
  association to temporal ordering; fit the flagged couplings γ, β_tau, β_si.
- **Genetics** → APOE4 stratification on the neuro axis; Mendelian randomization (IL-6R variants) as a
  causal probe of the shared-proxy assumption.
- **Multimodal** → tau-PET (ADNI) to fit the connectome front directly; inflammatory panels to test the
  proxy's co-movement.

None claimed as done — this is the falsification/validation program the agent is built to feed.

---

*Companion strategy: [`ROADMAP-STAGE2.md`](ROADMAP-STAGE2.md). Stage 1: [`ROADMAP.md`](ROADMAP.md).
Evidence & models: [`PAPER.md`](PAPER.md), [`BENCHMARK.md`](BENCHMARK.md), [`MODELS.md`](MODELS.md).
Non-diagnostic throughout; no patient value is produced or persisted.*
