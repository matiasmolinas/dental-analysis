# The Models — the medical relationships HISTORA computes, their evidence, and the parameters it fits

> How the agent's mechanistic harness explains the oral–systemic relationships: the models, the
> bibliography that supports them, the agent's input, the parameters the harness calibrates / sweeps /
> validates against real data, and an honest account of which models are load-bearing vs. reference.
> Companion to [`SOLUTION.md`](SOLUTION.md) (the architecture) and [`model-library.md`](model-library.md)
> (the full ~30-model catalog with citations). **Non-diagnostic throughout.**

## 1. How the agent's input works

HISTORA separates two jobs cleanly, and this separation is what keeps it honest:

- **Claude reasons** over an integrated record to produce *relational hypotheses* — which oral↔systemic
  mediators plausibly link the data, with a mechanism and full traceability (`histora.agent`, schema
  `schemas/output_schema.json`).
- **The deterministic harness computes** the *mechanistic quantities* — the ODE/transport models that
  turn structural severity into predicted IL-6/CRP, CV, and neuro outcomes with honest uncertainty
  (`histora.mech_*`).

### 1a. The record → the agent's prompt
A normalized record (`histora.record_formats`) is turned into the agent's input by
`histora.ab_eval.build_inputs(record)["B"]`, which is the **converged input**: the glossed,
sectioned record **plus** two deterministic injections computed in code, not left to the model —

1. `histora.relational_signals.derived_signals` — structural signal bands (e.g. a BOP inflammatory-load
   band low/moderate/high) and the explicit missing-mediator list.
2. The **missing-data directive (W1)** — every mediating datum truly absent from the record is added to
   `required_missing_data` as a collection flag (field + why), never imputed.

This is the project's one clean, repeated engineering win: the harness *guarantees* the
guardrail-critical collection flags (`missing_data_flagged` 0.00 → 1.00), where a free-form model
handed the same content as prose did not (`histora.exec_gap` generalizes the mechanism).

### 1b. The record → the mechanistic models' inputs
The mechanistic models never read a patient's numeric values. They read a **structural case signature**
(`histora.relational_signals.case_signature`): perio stage, a BOP band, a comorbidity set, and which
mediators are flagged absent — **bands and flags only**. `histora.mech_models.structural_load` maps
that signature to a dimensionless inflammatory load:

```
structural_load = BOP_band{high:1.0, moderate:0.5, low:0.15} (+0.3 if stage III/IV)
                  × comorbidity amplifiers (diabetes ×1.4, smoking ×1.25)
```

So a patient's data selects a *stratum*; the models produce parameter-level, population-scale
predictions and ranges for that stratum — never a per-patient inference.

## 2. The implemented models — medical relationship, math, evidence, parameters

The harness implements one **calibratable pipeline** unified by a single shared quantity, the
**effective inflammatory gain** = excess circulating IL-6 over its healthy baseline. Every uncertain
coupling is flagged and swept as a range, never asserted. Full catalog + confidence tiers:
[`model-library.md`](model-library.md).

### 2.1 Periodontal inflammatory source → IL-6 (E2.3, E2.4)
- **Medical relationship.** Diseased periodontal tissue is a chronic low-grade source of
  pro-inflammatory cytokines and endotoxin (LPS) that spill into the circulation; circulating IL-6
  rises with periodontal severity and clears with a ~2 h half-life.
- **Math.** `dIL6/dt = base_prod + source − μ_IL6·IL6`, `μ_IL6 = ln2/2 h`; closed form
  `IL6_ss = (base_prod + source)/μ_IL6`, with `source = ε · structural_load` [pg·mL⁻¹·h⁻¹].
- **Evidence.** Human LPS/endotoxemia acute-phase kinetics (Relouw et al. 2024, *npj Syst Biol Appl*
  10:146); periodontitis host–microbe bone-loss ODE (Fujihara et al. 2023, *J Dent Res* 102(13)).
- **Parameters.** `base_prod` set so IL-6 rests at ~2 pg/mL with no source; **ε (spillover efficiency)
  is the one calibrated edge** (§3).

### 2.2 IL-6 → hepatic CRP turnover (E2.5) — the calibratable transducer
- **Medical relationship.** The liver integrates the IL-6 signal into C-reactive protein, the blood
  marker clinicians measure; CRP is a slow, near-linear low-pass filter of IL-6 (constant ~19 h
  half-life). CRP ≥3 mg/L flags high cardiovascular risk.
- **Math.** `dCRP/dt = k_syn·IL6/(EC50+IL6) − k_deg·CRP`, `k_deg = ln2/19 h ≈ 0.0365 h⁻¹`,
  `EC50 = 6 pg/mL`, `k_syn = crp_max·k_deg` (`crp_max = 10 mg/L`); closed form
  `CRP_ss = (k_syn/k_deg)·IL6/(EC50+IL6)`.
- **Evidence.** CRP kinetics (Pepys & Hirschfield 2003, *J Clin Invest* 111:1805); IL-6R-blockade
  (tocilizumab) TMDD PK-PD as regulatory-grade proof the IL-6→CRP link is turnover-kinetic.
- **The shared quantity:** `inflammatory_gain = max(0, IL6 − IL6_basal)`, `IL6_basal = 2 pg/mL`.

### 2.3 The cardiovascular axis (E2.6; E1.1 documented) — FLAGGED scaffold
- **Medical relationship.** Chronic IL-6/CRP excess raises monocyte recruitment into the artery wall,
  a pro-atherogenic drive; and it shifts the endothelial threshold at which low wall-shear-stress
  regions become dysfunctional.
- **Math (implemented).** `recruitment_multiplier = 1 + γ_cv · gain`, `γ_cv = 0.05` per pg/mL — a
  monotone relative atherogenic index, deliberately a hypothesis, not a fitted human model. The full
  wall-shear-stress / Windkessel apparatus is documented (E1.1, E1.5) but *not* fitted here (it needs
  patient-specific vascular geometry we do not have — see §4).
- **Evidence.** systemic-inflammation→atherosclerosis ODE (Ougrinovskaia et al. 2010, *Bull Math
  Biol*); WSS→endothelium (Malek/Alper/Izumo 1999, *JAMA* 282:2035). *Mendelian randomization: IL-6/
  IL-1β are causal, CRP a marker — the agent privileges IL-6 as the driver, CRP as the observable.*

### 2.4 The neuro axis (E2.7 → E2.8) — the oral→Alzheimer coupling, FLAGGED
- **Medical relationship.** Systemic inflammation, gated by blood-brain-barrier permeability, drives
  neuroinflammation (microglial activation) which may accelerate the **prion-like spread of tau** — the
  protein whose misfolded propagation tracks Alzheimer's progression.
- **Math (implemented).**
  - Neuroinflammation: `N = N_max · (bbb·gain)/(K_gain + bbb·gain)`, BBB permeability rising with
    inflammation (`bbb = 1 + bbb_gain·gain/(K_gain+gain)`), `K_gain = 4`, `bbb_gain = 0.5`.
  - Tau growth: `α_eff = α_tau·(1 + β_tau·N)`, `α_tau = 0.019 yr⁻¹` (Schäfer 2021, amyloid-positive),
    `β_tau` the flagged coupling (§3).
  - Spread: single-region logistic Fisher–KPP `c(t)=c0/(c0+(1−c0)e^{−α_eff t})` for burden/onset, and
    a **Braak-ordered connectome** `dc_i/dt = −κ Σ_j L_ij c_j + α_eff c_i(1−c_i)` (entorhinal →
    hippocampus → neocortex) for front propagation.
- **Evidence.** neuroinflammation-amyloid-tau cascade (Hao & Friedman 2016, *BMC Syst Biol* 10:108);
  Fisher–KPP tau spread on the connectome (Fornari et al. 2019, *J R Soc Interface* 16:20190356;
  Schäfer et al. 2021, *Front Physiol* 12:702975). **Honesty anchor:** the one direct causal test of
  the periodontitis→Alzheimer hypothesis (atuzaginstat/GAIN gingipain-inhibitor trial) **failed** — so
  this axis is a live hypothesis, never a result.

### 2.5 Counterfactual levers (E2.10)
- **Periodontal therapy** — remove the oral source (`source → 0`): predicted ΔCRP (the calibration
  anchor) and, on the neuro axis, a delay of the modeled tau-threshold crossing.
- **IL-6 blockade** — neutralize IL-6 signaling: CRP relaxes to its IL6-basal floor (the
  tocilizumab-style lever, E2.10).

## 3. What the agent / harness fits, sweeps, and validates

Three distinct epistemic operations — this is what makes the harness a *measurement*, not a demo:

| Operation | Parameter(s) | How | Against what data | Result |
|---|---|---|---|---|
| **Calibrate** | **ε** — oral→systemic spillover efficiency (the one honestly-uncertain edge of the whole chain) | `histora.mech_calibrate` bisects ε so the *periodontal-therapy counterfactual* reproduces the target ΔCRP | the real, meta-analytic **~0.5 mg/L ΔhsCRP-after-periodontal-therapy** anchor | ε ≈ 0.15; the chain now reproduces a real interventional effect |
| **Sweep (report a range, not a point)** | **β_tau** — the inflammation→tau-α coupling; the second epistemic-risk parameter | vary β_tau over a plausible band → a range of tau burden / onset | none available in-cycle (the coupling is unfitted) | tau-burden **range**, never a point claim |
| **Validate** | the model's *predicted direction* (worse cognition with more periodontal severity) | `histora.perio_cognition` — confounder-adjusted standardized OLS + bootstrap CIs | real **NHANES 2011-2012** (n=919; age/education/smoking/HbA1c adjusted) | **3/4 cognitive measures significant, negative** — Digit Symbol adj −0.181 [−0.226,−0.137], Animal Fluency −0.098, CERAD-immediate −0.057 (CERAD-delayed ns); the direction the model predicts |

**Additional checks the harness runs on itself:** every mechanistic run verifies the closed-form
steady state is the stable dynamical attractor (Jacobian eigenvalues); `histora.counterfactual` tests
that the analysis *reasons with* a flipped factor (not just names it); `histora.stats` puts a bootstrap
CI on every reported delta so nothing fires on sub-noise.

**The honest boundary of the parameters.** Only ε is calibrated to real interventional data. β_tau and
the CV/neuro coupling constants (γ_cv, β_tau, the BBB gates) are **imposed, biology-plausible
scaffolds swept as ranges** — the biology is real, the exact math is ours, and the agent reports
falsifiable ranges, privileging IL-6/IL-1β as causal and CRP as the observable.

## 4. Honest model census — what does real work vs. what is library decoration

We explored ~30 models; an adversarial review asked, for each, three questions: *(a) can it connect to
the shared inflammatory-gain parameter? (b) can it be validated or parameterized against data we
actually have (public NHANES / the literature), or is it stranded? (c) does it duplicate a kept model
or is its oral-systemic coupling too speculative to even be a useful hypothesis?* The honest answer:
**only ~8–9 of the 31 entries do real work; the rest is reference or discardable.**

- **KEEP-CORE (the spine — implemented, load-bearing):** E2.3 (human IL-6 source kernel), E2.4
  (periodontal source), E2.5 (IL-6→CRP transducer + the ε-calibration anchor), E2.8 (Fisher–KPP tau
  spread, tau-PET-validated), E2.10 (IL-6-blockade counterfactual), E4.5 (the failed-GAIN-trial honesty
  anchor), E4.6 (the validated NHANES perio↔cognition association).
- **KEEP-FLAGGED (real biology, imposed math, swept as a range — never asserted):** E2.6 (CV
  atherogenic index), E2.7 (neuroinflammation node), E4.2 (systemic→neuro bridge, realized by
  E2.7→E2.8), E3.2 (diabetes gain→insulin-sensitivity coupling).
- **DEMOTE (keep as a library citation, do NOT build):** E1.4, E1.5, E1.6 (GCF flow / Windkessel /
  bacteremia — subsumed by the `ε·structural_load` abstraction, and NHANES carries no PWV/CFU to fit
  them); E2.1, E2.2 (murine/dimensionless inflammation ODEs — their one insight, "IL-6 integral drives
  damage," is already why IL-6 is the shared scalar); E3.1 (Bergman — reference substrate for E3.2);
  E3.4, E3.5, E3.6, E3.7 (control/ecology framings — mostly unvalidatable on cross-sectional data).
- **DISCARD (no real application to *this* problem):**
  - **The entire fluid-mechanics track E1.1, E1.2, E1.3, E1.7** — WSS/CFD, glymphatic advection–
    diffusion, sleep-clearance, bacteremia→BBB. They need **patient-specific vascular geometry / PVS
    velocities / brain-transport parameters we cannot obtain from NHANES**; their oral-inflammation
    couplings are 2–3 speculative hops with no data path. They read as prestige scaffolding that makes
    the CV and glymphatic axes look deeper than the code is.
  - **E2.9** (size-resolved Smoluchowski tau) — duplicates E2.8 with machinery we can't fit (no
    size-resolved tau-PET) + an unreviewed 2026 preprint.
  - **E3.3, E3.8** (Guyton baroreflex BP; fold/tipping/chaos) — no data path on cross-sectional NHANES;
    the library itself admits tipping is "hard to distinguish from cross-sectional data."
  - **E4.1, E4.3, E4.4** (P. gingivalis brain-invasion SIR; oral–gut–brain axis; "network tau spread
    modulated by inflammation") — the first has no brain-Pg data and a failed causal test, the second is
    pure analogy with no model, the third is an explicit **duplicate label** for the kept E2.8 core.

**The load-bearing agent is the ~8 models that touch either the calibratable IL-6→CRP spine or a public
NHANES dataset.** The instinct to curate 30 models was the weakness; the honest harness is small.

### What to actually implement next (beyond the current centerpiece)
1. **A CV-axis empirical anchor — highest value.** NHANES **2009-2010 co-measures periodontal exam +
   CRP + CV history in the SAME participants** (unlike the neuro cycle, where the mediator is
   out-of-cycle). Run the *same* confounder-adjusted, bootstrapped perio→CRP and perio→CV-history
   association → converts the E2.6 CV scaffold from a bare `1+γ_cv·gain` hypothesis into a data-touching
   result, and closes the mediator gap the neuro axis honestly cannot. The cleanest available win.
2. **The E3.2 diabetes coupling as a third axis** — `gain → insulin-sensitivity` as a monotone
   set-point shift (not the decorative loop-gain instability), calibrated to the **~0.3–0.4 pp HbA1c
   drop after periodontal therapy** and cross-checked against **in-cycle NHANES 2009-2010 HbA1c**. The
   only other coupling with both a real interventional anchor and in-cycle data.
3. **E3.5 gLV on NHANES 16S — optional, flagged-only.** The one ecology model with a real public dataset
   (NHANES 2009–2012 oral-rinse 16S); deprioritized — cross-sectional gLV identifiability is weak.

## 5. Additional models to consider — disciplined depth, not more decoration

A deep-research pass surfaced ~37 established, citable, pure-python-codable models that fill real gaps.
**The discipline of §4 applies to these too:** a candidate earns a place only if it (a) couples to the
shared IL-6/CRP `gain`, (b) has a data path we can actually walk (public NHANES / MESA / ADNI / in-vitro
kinetics), and (c) is codable as ODE/PDE/network/FBA — **not** if it recreates the stranded
patient-geometry problem that sank the fluid-mechanics track. Below is the *curated shortlist* by axis;
the full catalog is a research appendix, most of it library reference.

**Highest priority (a real data path + a direct IL-6 coupling — build these first):**
- **C4 — IL-6 → IRS-1 → insulin resistance on the Bergman model** (Pritchard-Bell/Parker 2013). **IL-6
  *is* the gain parameter** modulating insulin sensitivity — the cleanest bridge from the existing
  metabolic substrate to the spine, with a real anchor (HbA1c drop after periodontal therapy) and
  in-cycle NHANES 2009-2010 HbA1c. *This is the concrete way to implement the §4 "diabetes coupling".*
  *(verify the exact IRS-1 inhibition form before coding.)*
- **C1 — adipose → plasma IL-6 kinetics** (Morettini 2017, *PLoS One* 12:e0181224). Supplies the
  **obesity/adipose confounder hook** (`Ra_IL6`) — important because adipose IL-6 confounds the
  perio→IL-6 attribution; feeds directly into the Pepys IL-6→CRP spine. **Strong.**
- **D7 — Th17/iTreg reciprocal switch** (Hong 2011, *PLOS Comput Biol* 7:e1002122). **IL-6 is an
  explicit model input** (raising gain biases toward Th17); a bistable RORγt/Foxp3 toggle, and its
  RANKL→osteoclast→bone-loss extension fuses with the E2.4 periodontal source. The single most direct
  IL-6 coupling of any candidate. **Strong.**

**CV-axis depth (codable, spine-coupling — implement after the CV empirical anchor of §4):**
- **A3 — reaction-diffusion inflammation-wave plaque** (El Khatib/Volpert 2007-2012). A bistable
  oxLDL→monocyte→cytokine travelling wave where **the cytokine field can *be* the shared gain state**;
  method-of-lines in pure python, no patient geometry. **Strong** — the CV model that avoids the CFD trap.
- **A2 → A6 endpoint chain** — foam-cell formation (Cobbold-Sherratt 2002) → coagulation cascade
  (Hockin-Mann 2002, importable as **BioModels BIOMD0000000335**) → thrombotic endpoint; **A8**
  constrained-mixture arterial remodeling (Humphrey-Rajagopal 2002) → the **carotid IMT** imaging
  endpoint (MESA/Framingham data). IL-6/CRP scales recruitment, MMP-driven collagen loss, TF initiation.

**Neuro-axis depth:**
- **B2 — microglial M1/M2 + cytokine ODE** (Vaughan 2018, *J Neuroinflammation* 15:345). Replaces the
  lumped saturating `N(gain)` with a real bistable neuroinflammation hub (add IL-6 to the M1 Hill term).
- **B5 / B6 — heterodimer prion + coupled amyloid-tau network** (Weickenmeier 2019; Thompson 2020). A
  richer alternative to the Fisher-KPP core (separate healthy/toxic pools; Aβ accelerates tau on the
  connectome), validated against **ADNI amyloid/tau-PET**; gain couples via growth/clearance rates.

**Upstream immune drivers + resolution (produce IL-6/IL-1β → feed the spine):**
- **D4 (NF-κB oscillator, Hoffmann 2002 / Nelson 2004)** and **D5 (NLRP3 inflammasome→IL-1β, Hamis
  2021)** — the transcriptional/inflammasome sources that *generate* the gain from periodontal LPS/DAMPs.
- **D1 — resolution-of-inflammation ODE** (Dunster 2014, **BioModels BIOMD0000000616**). A saddle-node
  bistability between a healthy and a chronic state — the mechanistic core of *why periodontitis becomes
  chronic*; the pro-inflammatory pool maps to the gain.

**Oral source + microbiome (the mouth end) + a multiscale spine option:**
- **E1-E5 — genome-scale / community / spatial metabolic models** (Mazumdar-Segrè 2009; SteadyCom
  Chan-Maranas 2017; MICOM Diener-Gibbons 2020, native python; biofilm reaction-diffusion Stewart 2016)
  — predict the LPS/SCFA/redox output of the subgingival biofilm that becomes the source term. Strong,
  but heavier (FBA-LP / PDE); flagged-exploratory.
- **E7 — Foteinou multiscale human-endotoxemia** (2010, *Physiol Genomics* 42:5). An off-the-shelf
  multiscale systemic spine (molecular→cellular→HPA/autonomic) whose pro-inflammatory state is a natural
  home for the shared gain; an alternative/expanded backbone to the current IL-6→CRP chain.
- **C5-C7 — HPA / cortisol / circadian cytokine models** (Malek 2015; Rao-Androulakis 2016) — a
  cortisol brake + **time-of-day confounder** on IL-6/CRP assays (relevant to the NHANES adjustment).

**Honesty flags carried from the research:** four citations need volume/page verification before formal
use (A7 Anand-Rajagopal, C4 Pritchard-Bell full manuscript, C6 Mavroudis, the *Cells* 2022 macrophage-
bistability ref); two items (D6 Boolean NLRP3 map, the co-occurrence-network layer of E6) are
**topology/inference scaffolds, not fittable dynamical models** — reference only. No ML-only model was
promoted.

**Reconciliation with §4:** these additions do **not** re-bloat the library — the rule is the same
(spine coupling + data path + codability). The three top-priority additions (C4, C1, D7) are exactly
the ones that give the metabolic axis a real IL-6 coupling and a data anchor; the CV chain (A3→A8) and
neuro depth (B2, B5/B6) are the *disciplined* replacements for the discarded CFD/glymphatic track —
same phenomena, but codable and data-touchable. Build order: **(1) the CV empirical anchor (§4) →
(2) C4 diabetes coupling → (3) A3 CV inflammation-wave → (4) B2 microglial hub**, each behind the
tier/guardrail discipline of §6.

## 6. Modeling techniques — how Claude ensembles richer models as code

The point of a *modeling harness* (rather than a fixed model) is that Claude — with skills, prompts,
and sub-agents — can pick a **technique** for a new oral-systemic edge, instantiate it as code in the
existing `mech_ode` idiom (`f(t, y, p) → dy/dt` + `integrate` / `steady_state` / `jacobian` /
`eigenvalues` / `local_sensitivity` / `sweep`), calibrate it against public data, and compose it into a
multiscale ensemble. The unifying rule: **the shared `gain` (excess IL-6) enters every sub-model as one
monotone knob on one rate constant**, so a single ε/`gain` sweep propagates coherently across all axes
and the ensemble reports *ranges*, never point claims.

### 6.1 The seven technique families

| Family | What it is | Oral-systemic use | `gain` couples via | Ensemble role |
|---|---|---|---|---|
| **Compartmental ODE** (PK/PBPK, SIR-like, indirect-response, mass-action) | well-mixed pools, mass balances `d[pool]/dt = in − out` | the spine itself: IL-6 → CRP turnover; add a bacteremia-transport compartment | native — `gain` is the inflammatory input to each new compartment | **the backbone** every other family perturbs or reads |
| **Linear systems / control theory** (state-space, transfer functions, feedback, Kalman) | linearize `ẋ=f(x,u)` at a fixed point → `A=∂f/∂x` (already `jacobian`), poles=eigenvalues, DC gain, loop gain | CRP as a low-pass filter of pulsatile bacteremia; homeostatic set-point drift; Kalman-fuse the model with sparse NHANES hs-CRP to estimate latent `gain` | loop-gain / set-point-shift knob; watch `Re λ_max → 0` | **diagnostic lens + estimator + fast surrogate** |
| **Nonlinear dynamics** (bistability, saddle-node/Hopf, reaction-diffusion, tipping) | qualitative regime change as a parameter moves; front speed `v=2√(Dα)`; early-warning signals | tau front (Fisher–KPP); chronic-inflammation bistability; dysbiosis fold; CV foam-cell switch | **bifurcation control parameter** (`α→α(1+β·gain)`, `μ=μ0+κ·gain`) → the *critical `gain` at which each system tips* | **regime classifier / tipping detector** |
| **Network / graph** (Laplacian diffusion, gLV, Boolean, flux-balance, multilayer) | state on nodes coupled by `L=D−A`; community stability from the interaction-matrix spectrum | tau on the ADNI connectome (regional tau-PET); gLV oral microbiome (replicon eigenvalue R→0 = dysbiosis) | modulate the reaction term OR the interaction matrix (`gain` raises antagonism → R→0) | **spatial/topological substrate** — makes hypotheses region/taxon-specific |
| **Stochastic / agent-based** (Gillespie CME, Langevin, branching, agent-based) | explicit discreteness/noise; establishment probability, not mean load | bacteremia seeding (1–300 CFU, transient → survive or clear?); rare tau-nucleation → deterministic front | modulates **propensities** (inflammation lowers clearance → higher establishment probability) | **rare-event / discreteness correction** — Monte-Carlo around the ODE mean field |
| **Analogy / cross-domain transfer** (the creative engine) | import a *validated* model from another field, preserving the mechanism, **with a falsification gate** | SIR→prion-like tau spread; predator-prey→immune-microbe; Darcy flow→glymphatic; queueing (Little's law)→production-vs-clearance; percolation→dysbiosis; polymerization→amyloid aggregation | each analogy exposes one knob (`R₀`, loop gain, utilization ρ, nucleation rate) that `gain` turns | **hypothesis generator + honesty gate** — ships the condition to *reject* a bad analogy |
| **Multiscale coupling & ensemble/UQ** (QSS reduction, operator splitting, surrogates; LHS, Sobol, BMA) | compose sub-models across timescales; quantify uncertainty across models | QSS-chain fast IL-6 → slow CRP → years-slow tau; LHS over (ε, β, γ); Sobol to find the dominant unknown; BMA over structural variants | ε/`gain` is the shared axis of every sweep | **the composer + uncertainty envelope** |

### 6.2 The analogy gate (the discipline that keeps transfer honest)

Cross-domain transfer is HISTORA's most powerful and most dangerous technique. Every imported model
must ship, with its variable map, **the mechanistic justification and the failure condition** the agent
checks before admitting it — e.g. *SIR→tau* is valid because templated conversion `S+I→2I` is
mathematically the epidemic transmission term (which is *why* Fisher–KPP works for tau), and it **fails
if** clearance ≫ conversion (no `R₀>1` threshold crossed) or there is co-occurrence without true
seeding. *Darcy→glymphatic* fails if the Péclet number is small (diffusion dominates, the "flow" story
is spurious). An analogy without a stated failure mode is rejected.

### 6.3 How Claude builds the ensemble as code (the recommended architecture)

Thin additions to the existing `histora` package, not a rewrite:

1. **A model registry** — one dict per sub-model: `{rhs, state_names, params, gain_coupling, axis,
   tier, citations}`, mirroring the `E-entry` metadata in `model-library.md`. `gain_coupling` is a
   single `p → p'` function that injects `gain` into exactly one rate constant — this is what makes any
   new sub-model plug into the shared parameter automatically. `tier` (anchor / flagged-scaffold /
   speculative) gates how its output is reported.
2. **A composition layer** — the three operators: **series** (QSS-inject via `steady_state`),
   **parallel fork** (one `gain` → CV + neuro), **feedback** (loop-gain via `jacobian` eigenvalue
   crossing), plus `operator_split` for reaction-diffusion PDE stages. Composition is just wiring RHS
   functions; the existing integrator runs the result.
3. **An ensemble / UQ driver** — pure-python `latin_hypercube`, Sobol (or `local_sensitivity` for
   screening), a `gillespie` for the stochastic layer, and `bma_average` weighting structural variants
   by fit to public data. Every run outputs an **envelope over the ε/`gain` sweep**, never a point.
4. **A modeling sub-agent + skill** — `modeling-technique-selector`: reads the target edge, picks a
   family (switch/threshold → nonlinear; topology → network; low-count → stochastic; new mechanism →
   analogy *running the gate*), instantiates it as a registry entry, calibrates against the public data
   the library names, and hands it to compose/ensemble. A `guardrail-verifier` pass enforces the
   non-diagnostic framing and the analogy failure-gates.

**The invariant that keeps it coherent and honest:** one shared `gain`, one monotone knob per
sub-model, every prediction a swept range with a UQ band and a tier label, every imported analogy
carrying its falsification condition. That is what turns seven modeling families into one multiscale
HISTORA agent rather than a bag of models.

*Technique references (landmark works):* Gillespie 1977 (stochastic simulation); Turing 1952 and
Fisher/KPP 1937 (reaction-diffusion); Kermack & McKendrick 1927 (SIR); Raj, Kuceyeski & Weiner 2012
(network diffusion); May 1972 (random-matrix community stability); Little 1961 (queueing); Sobol 2001 &
Saltelli 2008 and Marino et al. 2008 (global sensitivity / LHS in systems biology); Hoeting et al. 1999
(Bayesian model averaging); Åström & Murray, *Feedback Systems*; Strogatz, *Nonlinear Dynamics and Chaos*.
