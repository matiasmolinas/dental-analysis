# HISTORA — Solution Description ("how it actually works")

> Companion to the VISION document. This is the mechanistic and empirical "how," written for **two
> readers at once**: a **physician**, who needs the clinical claims and their caveats stated plainly,
> and a **bioengineer**, who needs the models, data, equations, and statistics. Where a term belongs to
> one discipline, it is defined for the other.
>
> **Non-diagnostic, throughout.** HISTORA is an oral–systemic *research* agent. Every output is a
> population-level or in-silico parameter-level prediction, a swept range, or a data-collection flag —
> **never** a patient diagnosis and **never** an imputed patient value. Nothing here is medical advice.
>
> **Companions:** the condensed technical report is [`PAPER.md`](PAPER.md); the comparative validation
> against separate models and bare Claude is [`BENCHMARK.md`](BENCHMARK.md); the full model catalogue is
> [`MODELS.md`](MODELS.md).

---

## 1. Solution overview

HISTORA formalizes one defensible mechanistic chain from the mouth to two systemic axes
(cardiovascular and neurological), calibrates its single most uncertain link against real
interventional data, tests the association it predicts in a public population dataset, and wraps the
whole thing in a guardrail that refuses to diagnose or to invent missing values.

The pieces cohere because they share **one quantity**: the **effective inflammatory gain** — the
*excess* of circulating interleukin-6 (IL-6) above its healthy baseline, best understood as a **latent
systemic-inflammation proxy operationalized as excess IL-6** (CRP, IL-1β and TNF-α co-move with it), not
a claim that IL-6 is the sole mechanism. (For the physician: IL-6 is a pro-inflammatory cytokine, a
signaling protein; chronic periodontitis is a low-grade source of it. For the bioengineer: it is the
single scalar the entire pipeline propagates.) HISTORA is a **research agent, not a disease predictor**. The same excess-IL-6 quantity
drives the cardiovascular axis, the neuro axis, and the metabolic couplings — so varying one parameter
generates coherent, cross-axis, falsifiable hypotheses rather than a disconnected bag of models.

```
   DATA                MODEL LIBRARY            MECHANISTIC HARNESS              HYPOTHESES          VALIDATION            GUARDRAILS
   ────                ─────────────            ───────────────────              ──────────          ──────────            ──────────
  NHANES         ~30 cited, confidence-     periodontal source (E2.4)          CV axis:          NHANES 2011-2012     non-diagnostic
  (public,   ──► tiered mechanistic     ──►      │  structural bands only  ──►  atherogenic  ──►  perio ↔ cognition ──► invariant (W2)
  de-ident.)     models organized               ▼                               index               (n=919,             enforced at
                 around ONE pipeline        IL-6 (E2.3)                                             3/4 outcomes         write time
                 and ONE shared                  │                              NEURO axis:        SIGNIFICANT)         + traceability
                 parameter                       ▼   ← ε calibrated here         tau-spread α ↑                        + missing-data
                                            hepatic CRP (E2.5, t½≈19h)               │             (mediator not         directive (W1)
                                                 │                                   ▼             co-measured →         + exec-gap
                                        ┌────────┴────────┐                     Braak-ordered      "why"=model,          capability
                                        ▼                 ▼                     connectome         "whether"=data)
                                     CV axis          NEURO axis                propagation
                                        └──────── shared inflammatory gain ─────────┘
                                                (excess IL-6 over basal)
```

**The four load-bearing claims, and their epistemic status up front:**

| Claim | Status |
|---|---|
| The mechanistic pipeline is internally consistent, calibratable, and stable | **Validated capability** (deterministic, tested) |
| Higher periodontal severity tracks worse cognition in NHANES, adjusted | **Validated association** (real data, 3/4 outcomes significant) |
| Higher periodontal severity tracks higher CRP and higher HbA1c in NHANES, adjusted | **Validated associations** (2009-2010; CV and metabolic anchors significant) |
| The integrated harness beats separate models and bare Claude on a pre-specified scorecard | **Validated comparatively** (parsimony, calibration, uncertainty, falsifiability; direction ties — [`BENCHMARK.md`](BENCHMARK.md)) |
| Externalizing a known-but-dropped deterministic step improves guardrail reliability | **Validated capability** (W1, reproduced) |
| Oral inflammation *causes* faster tau spread via α | **Flagged hypothesis** — swept as a range, never asserted |

---

## 2. The mechanistic models

### 2.1 The centerpiece chain (`src/histora/mech_models.py`)

The pipeline is a small system of ordinary differential equations (ODEs — equations describing how
quantities change over time). It is **pure Python**, dependency-light, and every constant is anchored to
a cited literature range (see `docs/model-library.md`, entries `E2.x`). Below, each stage carries a
one-line **clinical meaning** for the physician and the **actual equation** for the bioengineer.

**Stage 0 — the structural source (E2.4).**
*Clinical meaning:* how much inflammatory drive the diseased gum tissue plausibly exports to the
bloodstream — read only from **structural categories**, never a patient's lab value.
The source is built from bands and flags: bleeding-on-probing (BOP) band, periodontal stage, and
comorbidity flags. `structural_load` maps `{high: 1.0, moderate: 0.5, low: 0.15}` for the BOP band,
adds `+0.3` for stage III/IV, and multiplies by comorbidity amplifiers (`diabetes ×1.4`, `smoking
×1.25`). Then:

```
source (IL-6 influx) = ε · structural_load        [pg·mL⁻¹·h⁻¹]
```

`ε` (epsilon) is the **oral→systemic spillover efficiency** — the one honestly-uncertain link, pinned by
calibration (§2.2).

**Stage 1 — IL-6 dynamics (E2.3).**
*Clinical meaning:* circulating IL-6 rises with the periodontal source and clears with a ~2 h half-life.

```
dIL6/dt = base_prod + source − μ_IL6 · IL6        μ_IL6 = ln2 / 2 h
IL6_ss  = (base_prod + source) / μ_IL6            (closed-form steady state)
```

Basal production is set so that with no source, IL-6 sits at its healthy baseline of ~2 pg/mL.

**Stage 2 — hepatic C-reactive protein turnover (E2.5) — the calibratable transducer.**
*Clinical meaning:* the liver integrates the IL-6 signal into CRP, the blood marker clinicians actually
measure; CRP is a slow, near-linear low-pass filter of IL-6 with a **19 h half-life** (Pepys &
Hirschfield 2003). (CRP = C-reactive protein, a standard inflammation blood test; ≥3 mg/L flags high
cardiovascular risk.)

```
dCRP/dt = k_syn · IL6/(EC50 + IL6) − k_deg · CRP
k_deg   = ln2 / 19 h ≈ 0.0365 h⁻¹      EC50 = 6 pg/mL      k_syn = crp_max · k_deg   (crp_max = 10 mg/L)
CRP_ss  = (k_syn/k_deg) · IL6/(EC50 + IL6)        (closed-form steady state)
```

**The shared quantity** feeding everything downstream:

```
inflammatory_gain = max(0, IL6 − IL6_basal)       IL6_basal = 2 pg/mL       [pg/mL]
```

**Stage 3a — the CV axis (E2.6, a FLAGGED scaffold).**
*Clinical meaning:* chronic IL-6 excess raises monocyte recruitment into the artery wall — a *relative*
atherogenic index, a hypothesis, not a fitted human model.

```
recruitment_multiplier = 1 + γ_cv · gain          γ_cv = 0.05 per pg/mL
```

The model library also contains the full fluid-mechanics apparatus for this axis — **wall shear stress**
(WSS, the frictional force blood exerts on the vessel lining; `τ_w = μ (∂u/∂n)|_wall`), the oscillatory
shear index `OSI = ½(1 − |∫τ_w| / ∫|τ_w|)`, atheroprotective above ~1.5 Pa and atherogenic below ~0.4
Pa (E1.1) — but the code's CV coupling is deliberately the simple monotone scaffold above, flagged as a
hypothesis. The WSS/Windkessel machinery is documented as available, not fitted here.

**Stage 3b — the NEURO axis (E2.8, a FLAGGED scaffold).**
*Clinical meaning:* inflammation may accelerate the prion-like spread of tau (a protein whose
misfolded spread tracks Alzheimer's progression) — the growth rate α rises with the gain.

```
α_eff = α_tau · (1 + β_neuro · gain)               α_tau = 0.019 yr⁻¹, β_neuro = 0.03 per pg/mL
```

**Counterfactuals** (`centerpiece`) are computed from the *same* steady state:
- **Periodontal therapy** → set `source → 0` → ΔCRP. This drop is the **calibration anchor** (§2.2).
- **IL-6 blockade** → CRP relaxes to its IL6-basal floor (the E2.10 tocilizumab-style lever).

Finally, `centerpiece` runs a **dynamics check**: it numerically integrates the ODEs and confirms the
closed-form steady state is the actual stable attractor via the **Jacobian** of the ODE system (the
matrix of partial derivatives of the vector field — the standard tool for testing whether a fixed
point is stable).

### 2.2 Calibrating ε — the one uncertain edge (`src/histora/mech_calibrate.py`)

Everything above is anchored to literature *except* ε, which carries the epistemic risk of the whole
periodontitis→systemic link. Rather than guess it, HISTORA **pins ε to a real interventional anchor**:
meta-analyses show professional periodontal treatment lowers systemic CRP by **~0.5 mg/L**.

The method: for a reference structural case (high BOP, stage III, no comorbidities), find the ε such
that the therapy counterfactual (`source → 0`) reproduces the target ΔCRP. Because CRP is monotone
increasing in ε, a **bracketed bisection** converges cleanly:

```
ΔCRP(ε) = CRP_ss(source = ε·load) − CRP_ss(source = 0)      →  bisect ε until ΔCRP(ε) = 0.5 mg/L
```

If the target is unreachable within the bracket, the routine returns the ceiling **honestly** with
`reached_target: False` rather than fabricate a fit. This is the step that turns the model from a demo
into a **falsifiable, data-anchored object**. Because the anchor itself has spread, ε is then *swept*
(0.5×–2× in `run_mechanistic.py`) to report a **range** of CRP predictions, not a point claim.

### 2.3 The neuro axis in full (`src/histora/mech_neuro.py`)

The neuro model reuses the *same* systemic gain and forks it into the brain. The chain: systemic IL-6
excess → (gated by blood–brain-barrier permeability) → neuroinflammation `N` → raised tau-spread α →
faster tau accumulation and earlier threshold crossing → Braak-ordered propagation across a connectome.

```
neuroinflammation:   bbb = 1 + bbb_gain · g/(K_gain + g);   x = bbb·g;   N = N_max · x/(K_gain + x)
                     bbb_gain = 0.5, K_gain = 4 pg/mL, N_max = 1.0        (saturating, super-linear then plateaus)

tau growth rate:     α_eff = α_tau · (1 + β_tau · N)          β_tau = 0.6   ← FLAGGED coupling, swept not asserted

single-region tau:   c(t) = c0 / (c0 + (1−c0) e^(−α t))       (logistic Fisher–KPP; c0 = tau_seed = 0.05)
threshold crossing:  t* = (1/α) · ln[ (θ/(1−θ)) · ((1−c0)/c0) ]        θ = 0.5

connectome spread:   dc_i/dt = −κ Σ_j L_ij c_j + α_eff c_i (1 − c_i)     (Fisher–KPP on a graph; L = path Laplacian)
                     Braak chain: entorhinal → hippocampus → neocortex,  κ_graph = 0.02 yr⁻¹ (illustrative)
```

*For the physician:* **Fisher–KPP** is the classic "reaction–diffusion" equation for a spreading front
(here, tau moving along brain networks); the **Braak stages** describe the stereotyped order in which
tau pathology appears (entorhinal cortex first, then hippocampus, then neocortex). The model reproduces
that order and asks: *does upstream oral inflammation move the front earlier?*

*For the bioengineer:* the tau-spread math (Fisher–KPP on the connectome Laplacian) is the **validated
anchor** (Fornari 2019, Schäfer 2021, tau-PET-fitted). The `β_tau` coupling from inflammation to α is
the **flagged hypothesis** — `neuro_centerpiece` sweeps `β_tau ∈ {0.3, 0.6, 1.0, 1.5}` and reports the
resulting **tau-burden range**, never a single number. Absolute onset years are explicitly labeled
illustrative (α_tau's literature CI is ±0.27 yr⁻¹); **the deliverable is the direction and the relative
counterfactual** (e.g., "periodontal therapy delays modeled onset by Δ years"), reported as a range.

### 2.4 Confidence table — anchors vs flagged scaffolds

| Component | Equation / anchor | Confidence | What it means |
|---|---|---|---|
| IL-6 → CRP turnover | `k_deg = ln2/19h`, indirect-response form | **Anchor** (Pepys 2003) | CRP kinetics are regulatory-grade |
| ε spillover efficiency | bisection to ~0.5 mg/L ΔCRP anchor | **Calibrated** (medium) | fit to interventional meta-analysis; swept |
| Tau spread (Fisher–KPP on connectome) | `dc_i/dt = −κLc + αc(1−c)` | **Anchor** (Fornari/Schäfer) | tau-PET-validated math |
| IL-6 dynamics / basal | `μ_IL6 = ln2/2h` | **Anchor** (Relouw 2024 human) | human-scaled acute-phase |
| CV coupling (recruitment index) | `1 + γ_cv·gain` | **Scaffold** (flagged) | directionally grounded, not fitted |
| inflammation → α (`β_neuro`, `β_tau`) | `α·(1+β·gain)` | **Scaffold** (flagged) | the hypothesis HISTORA generates |
| BBB gating of neuroinflammation | saturating `N(g)` | **Scaffold** (flagged) | biology real, math imposed |

The discipline is uniform: **anchors are built on; every flagged coupling is swept as a range of
falsifiable predictions, never a point claim.** Mendelian-randomization evidence favors IL-6/IL-1β as
*causal* nodes and CRP as a *marker* — so the axes are driven by IL-6, with CRP reported as the
observable readout.

---

## 3. The data and the empirical validation

### 3.1 The datasets (`src/histora/nhanes.py`)

HISTORA uses **NHANES** (the U.S. National Health and Nutrition Examination Survey — a large, public,
de-identified population dataset). Two cycles matter:

- **2009–2010 (`_F`):** the full-mouth periodontal exam coexists with **CRP**, HbA1c, lipids, blood
  pressure, and CV history — the cardiovascular anchor cycle. Files join on `SEQN` (respondent ID).
- **2011–2012 (`_G`):** the **cognitive-functioning module** (CERAD word-learning, Animal Fluency,
  Digit Symbol) coexists with the periodontal exam in the *same* participants — the oral↔neuro anchor.

**The honest cross-cycle caveat, stated openly in the code:** *no single public NHANES cycle carries
periodontal exam + CRP + cognition together.* Standard CRP was discontinued after 2009–2010; hs-CRP
returns only in 2015–2016 (`HSCRP_I`), but that cycle drops the full periodontal exam. Therefore the
**inflammation mediator that `mech_neuro` models is not co-measured with cognition.** The consequence,
stated plainly: **the model supplies the "why" (the mechanism); the data can only test the "whether"
(the association).** HISTORA does not paper over this gap — it names it.

### 3.2 The result (`src/histora/perio_cognition.py`)

**Question:** does higher periodontal severity (exposure = mean clinical attachment loss, CAL — the
distance the gum has detached from the tooth, a standard severity measure) track *lower* cognitive
scores, after adjusting for the dominant confounders (age, education, smoking, HbA1c)?

Run on NHANES 2011–2012: 9,756 participants merged; **n = 919** with complete periodontal + cognition +
confounder data (the cognition module is age 60+). Coefficients are **standardized** (in standard-
deviation units); a **negative** coefficient means *worse cognition with more periodontal severity* —
the direction the mechanistic model predicts.

| Cognitive outcome | Crude | **Adjusted** | 90% CI (adjusted) | Verdict |
|---|---|---|---|---|
| Digit Symbol (processing speed) | −0.324 | **−0.181** | [−0.226, −0.137] | **SIGNIFICANT** |
| Animal Fluency (executive function) | −0.172 | **−0.098** | [−0.157, −0.045] | **SIGNIFICANT** |
| CERAD immediate recall (memory) | −0.153 | **−0.057** | [−0.108, −0.007] | **SIGNIFICANT** |
| CERAD delayed recall (memory) | −0.126 | **−0.048** | [−0.100, +0.002] | ns (CI touches 0) |

**3 of 4 cognitive measures show a significant, confounder-adjusted negative association.** Processing
speed shows the strongest adjusted effect. This is the neuro axis's **empirical anchor**: the
association the mechanistic model predicts is *present* in real, public data.

**The honest reading (both audiences must take this away):**
- **It is real and adjusted** — survives age/education/smoking/HbA1c adjustment on 3/4 measures, with
  bootstrap CIs excluding 0.
- **Adjustment roughly halves the effect** (crude → adjusted): *much of the crude signal is confounding*
  (age above all). Effect sizes (−0.05 to −0.18 SD) are **small** — one contributor among many, exactly
  as the epidemiology suggests.
- **It is association, not causation.** Cross-sectional; reverse causation is live (early cognitive
  decline → worse oral self-care → periodontitis). The inflammation mediator is not in-cycle, so this is
  the "whether," not the "why."
- **CERAD-delayed is reported as non-significant** (CI [−0.100, +0.002], just touches 0) — *not* rounded
  into the win.

### 3.3 The statistics, explained plainly

Both the exposure and the outcomes are **z-scored** (standardized to mean 0, SD 1). An ordinary
least-squares (OLS) regression then fits `outcome ~ 1 + exposure + confounders`; the **exposure
coefficient** is a partial-correlation-like effect size in SD units. (With no confounders it equals the
Pearson correlation.) All linear algebra — Gaussian elimination with partial pivoting — is
**pure Python**, so the analysis is testable without numpy/scipy.

Significance uses a **seeded percentile bootstrap** (`_bootstrap_ci`): resample the participant rows
with replacement 2,000 times, refit each time, and take the 5th/95th percentiles of the coefficient as a
90% confidence interval. A result is "significant" only when that CI **excludes 0**. The seed makes it
reproducible; degenerate (collinear) resamples are skipped, not silently zeroed. This is the same
significance discipline the optimization apparatus uses (§4), applied to observational data.

---

## 4. Non-diagnostic guardrails and scientific honesty

### 4.1 The protected invariant (W2)

The invariant — **never diagnose, never impute a patient value** — is enforced structurally, not by
politeness. It is checked at **write time**: `lever_ledger.validate_lever` rejects any attempt to store a
numeric patient value, the one place a cross-patient leak could occur. It held across every experiment.

`src/histora/relational_signals.py` is the deterministic embodiment: it turns a record into **structural signal
bands** (e.g., a BOP inflammatory-load band of low/moderate/high) and an explicit **missing-mediator
list** — and its hard rules mirror the guardrail: *structural categorizations of present data only, and
no imputation — a missing datum becomes a collection flag, never a computed value.*

### 4.2 The apparatus — scoring, bootstrap CIs, counterfactual sensitivity

- `src/histora/ab_eval.py` — a **model-agnostic scorer**: mechanism recall (CV + neuro mediators),
  relational recall (a mediator counts only when used inside a *traced* axis, not merely named),
  missing-data flagging, traceability, and the guardrail. The **guardrail is a hard prerequisite**: an
  output that fails it is not deployable regardless of its accuracy.
- `src/histora/stats.py` — the significance discipline: seeded **bootstrap confidence intervals** (a
  claim never fires on a sub-noise delta) and a standardized OLS for confounder-adjusted analysis.
- `src/histora/counterfactual.py` — **counterfactual sensitivity**: flip one input factor and check the
  dependent axis moves in the mechanistically-correct direction while unrelated axes stay put — a
  behavioral test that the model *reasons with* a factor, not just names it.

### 4.3 W1 — the one clean win, and the execution-gap capability (`src/histora/exec_gap.py`)

The project's single clean, repeated win (**W1**): a **deterministic missing-data directive raised
guardrail pass 0.00 → 1.00** on real NHANES cases. The critical control: **free-form convergers handed
the *same* directive still fell back to 0.00.** They had the content in context and did not deploy it.

`src/histora/exec_gap.py` generalizes this into a repeatable capability. The insight is to split what
a model knows from what it reliably *does*:

- `K_know` = what the model can state if asked.
- `K_exec` = what it reliably deploys **in situ** under generation load.
- The payoff channel is the set difference **`K_know \ K_exec`** — steps the model *knows but drops*.
  A deterministic, enforced directive externalizes exactly this.

The module provides:
1. **A pre-A/B predictor** (`predict_pays`): classify a candidate directive by *(known? deterministic?
   dropped-in-situ?)*. The single strongest, cheapest signal is **"stated-on-demand-but-dropped-in-
   situ"** for a known + deterministic step → predict it **pays** (execution gap). A known + semantic
   step the model already applies → predict **null** (don't spend the A/B).
2. **A 3-arm A/B** (`run_directive_ab`): **base / enforced (deterministic) / prose-handoff (same
   directive as plain text)**. Bootstrap CIs on two contrasts both *measure* the effect and *classify
   why*: `execution_gap` (enforced beats both base and prose — externalization is load-bearing),
   `knowledge_gap` (content helped, externalization didn't), or `screened` (no effect). The prose arm is
   the W1 control that isolates externalization from content.

### 4.4 The honesty anchor — the failed atuzaginstat trial

The neuro hypothesis is kept honest by a real negative result. **Atuzaginstat (COR388)**, a gingipain
inhibitor targeting the *P. gingivalis*→Alzheimer's hypothesis, **failed both co-primary endpoints in
the GAIN trial, caused dose-dependent hepatotoxicity, hit an FDA hold, and the program was abandoned.**
`mech_neuro` carries this in its flags: *"atuzaginstat/GAIN trial failed → live hypothesis, not
causation."* The one direct causal test of the mechanism this agent models did **not** succeed — which
is precisely why HISTORA frames the inflammation→tau edge as a swept hypothesis, not a result.

---

## 5. How to run it

The mechanistic and validation centerpieces are **pure-Python** (the association runner needs `pandas`
+ network to fetch NHANES; the Claude agent needs `anthropic` + `ANTHROPIC_API_KEY`). Run from the
repository root.

```bash
# 1. The mechanistic centerpiece: calibrate ε, run the strata, sweep ε → a CRP range, write a report.
python src/run_mechanistic.py            # → results/mechanistic_report.json

# 2. The neuro axis: oral severity → gain → neuroinflammation → tau-α → burden/onset/connectome front,
#    with the periodontal-therapy counterfactual and the β_tau sweep (flagged coupling → a range).
python src/run_mech_neuro.py             # → results/mech_neuro_report.json

# 3. The empirical anchor: confounder-adjusted perio ↔ cognition association on real NHANES 2011-2012.
python src/run_perio_cognition.py --exposure perio_cal    # → results/perio_cognition_report.json

# 4. The Claude-powered relational agent: analyze a record → non-diagnostic oral-systemic hypotheses,
#    then check the guardrail. (Requires anthropic + ANTHROPIC_API_KEY in .env.)
python src/run_agent.py                  # → results/agent_output.json
```

Each runner reasserts the guardrail in its output ("non-diagnostic: structural bands only;
parameter-level predictions + ranges").

---

## 6. Validated vs hypothesis vs set-aside — the honest map

| Category | Component | Why it is here |
|---|---|---|
| **Validated capability** | The mechanistic pipeline (`mech_models`, `mech_calibrate`, `mech_neuro`) | Internally consistent, spillover calibrated to a real interventional anchor, ODE steady states verified stable |
| **Validated capability** | The apparatus (`ab_eval`, `stats`, `counterfactual`, bootstrap CIs) | Model-agnostic, significance-aware — a claim never fires on a sub-noise delta; pure-python, tested |
| **Validated capability** | The execution-gap mechanism (`exec_gap`) | Deterministic directive raised guardrail pass 0.00 → 1.00, reproduced; the prose control isolates enforcement from content |
| **Validated association** | Perio ↔ cognition (NHANES, `perio_cognition`) | 3/4 outcomes significant, confounder-adjusted, bootstrap CIs exclude 0 — real data, honestly caveated |
| **Hypothesis (flagged, swept)** | inflammation → tau-α causal coupling (`beta_tau`) | Biology plausible, math imposed; the direct causal test (atuzaginstat) failed — swept as a range, never asserted |

Everything in the codebase is one of the above: a validated capability, a validated association, or an
explicitly-flagged-and-swept hypothesis. Nothing that could not be verified or reproduced was kept.

---

*HISTORA is a non-diagnostic, hypothesis-generating oral–systemic research agent. Every quantity in this
document is a population-level or in-silico parameter, a swept range, or a data-collection flag. Nothing
here diagnoses a patient or imputes a patient value, and nothing here is medical advice.*
