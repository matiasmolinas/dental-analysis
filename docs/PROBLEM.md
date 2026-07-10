# HISTORA — The Problem

> A non-diagnostic research agent for the oral–systemic frontier.
> It turns *"these things co-occur"* into *"here is a candidate mechanism, simulated,
> checked against real data, with honest uncertainty."*
>
> **Non-diagnostic by construction:** HISTORA never diagnoses a patient, and never
> imputes a patient value. Every output is a population- or parameter-level *hypothesis*,
> not a clinical decision.

---

## 1. The vision in one paragraph

Gum disease is not just a dental problem. Periodontitis is a common, chronic, low-grade
*inflammatory* condition, and a growing body of evidence links it to disease elsewhere in
the body — cardiovascular disease, and, more recently, Alzheimer's and neurodegeneration —
plausibly through the inflammation it puts into the bloodstream. But that evidence lives in
two disconnected worlds: population statistics that say *"periodontitis patients get more
of X"*, and mechanistic biology that describes single pathways in isolation. **HISTORA is a
research agent that closes the gap.** It takes a patient's periodontal and systemic data,
surfaces oral–systemic risk *hypotheses*, and then does something most tools do not: it
**builds and runs mechanistic mathematical models** of the candidate pathways and validates
their predictions against public data. The result is a prioritized, honestly-caveated,
falsifiable research agenda — for physicians deciding where to look and for bioengineers and
neuroscientists deciding what to model and measure next. It is a hypothesis generator with a
simulator and a validation harness attached, and a hard guardrail that keeps it out of the
diagnosis business.

---

## 2. The clinical problem, and why it matters (for the physician)

### The oral–systemic link is real, and under-exploited at the point of care

Periodontitis — chronic inflammation and destruction of the tissues supporting the teeth —
affects a large fraction of adults. Clinically it is measured with structural findings:
**clinical attachment loss (CAL)**, probing pocket depth, **bleeding on probing (BOP)**, and
tooth count, summarized in staging systems (e.g. Stage I–IV). What makes it more than a local
problem is that inflamed periodontal tissue is a chronic source of inflammatory mediators and
bacterial products that reach the circulation. The best-supported systemic consequence runs
through **interleukin-6 (IL-6)**, a pro-inflammatory cytokine, and its downstream liver
product **C-reactive protein (CRP)** — the same acute-phase marker used clinically for
cardiovascular risk stratification.

Two systemic axes are of particular interest:

- **Cardiovascular.** Chronic systemic inflammation (elevated IL-6/CRP) is mechanistically
  tied to endothelial dysfunction and atherosclerosis. Periodontal inflammation is one
  plausible chronic contributor to that inflammatory burden.
- **Neurodegenerative (Alzheimer's).** This is the newer and more provocative axis.
  Epidemiology associates severe periodontitis with elevated dementia/cognitive-impairment
  risk, and there is a biologically plausible chain — periodontitis → systemic inflammation →
  **neuroinflammation** → accelerated **tau** pathology. This chain is a live *hypothesis*,
  not established fact (see §4 for the honest caveat, including a failed drug trial).

### What a non-diagnostic, hypothesis-generating tool offers a clinician

HISTORA is deliberately **not** a diagnostic aid and does not tell you what a given patient
"has" or "will get." What it offers instead:

- **Research direction.** It ranks which oral–systemic pathways are most worth investigating
  for a given patient profile, and says *why* — grounded in a simulated mechanism, not a bare
  correlation.
- **Prioritized, testable experiments.** Its outputs are framed as falsifiable predictions
  (e.g. *"if periodontal IL-6 were neutralized, predicted ΔCRP is …"*), suitable for designing
  a study, not for treating a patient.
- **A shared language for collaboration.** It gives a dentist, a cardiologist, a
  neuroscientist, and a bioengineer one common quantitative object to argue over — the
  inflammatory pathway, made explicit.

> **What it is not:** not a diagnosis, not a prognosis for an individual, not a treatment
> recommendation. If a reader wants a clinical decision, HISTORA is the wrong tool by design.

---

## 3. The scientific and engineering vision (for the bioengineer)

### Mechanism over correlation

The core methodological bet is that a *simulated mechanism, checked against data* is worth
far more than another association table. An association tells you two things move together; a
mechanistic model tells you *how*, predicts the *direction and relative size* of an
intervention's effect, and — crucially — **exposes its own assumptions as parameters you can
sweep and falsify.** HISTORA is built to produce the second kind of object.

### One shared parameter unifies three axes

The organizing idea is that a single quantity — the **effective inflammatory gain**, defined
concretely as **excess circulating IL-6 above basal** — links one periodontal inflammatory
source to multiple systemic axes. The *same* gain:

- degrades insulin sensitivity in the **metabolic** (diabetes ↔ periodontitis) loop,
- raises monocyte recruitment in the **cardiovascular** (endothelial / atherosclerosis) axis, and
- drives **neuroinflammation** and, through it, the tau-spread growth rate in the **neuro** axis.

Because it is one parameter, varying it propagates coherent, cross-axis predictions instead of
a bag of unrelated models. That is the intended use of the agent.

### The centerpiece pipeline

The implemented centerpiece (`src/mech_models.py`) wires one calibratable chain end to end:

```
 periodontal source ──► IL-6 ──► hepatic CRP (turnover) ──┬──► CV axis  (atherosclerosis coupling)
 (STRUCTURAL bands,     (E2.3)   (E2.5, t½ ≈ 19 h)         └──► NEURO axis (tau-spread α, E2.8)
  BOP / stage / comorbidity)
```

Mechanistic detail worth noting for a modeler:

- **Source term.** Built strictly from *structural bands and flags* — BOP band, perio stage,
  comorbidity flags (diabetes, smoking as inflammatory amplifiers) — mapped to a dimensionless
  local inflammatory load. **Never a numeric patient value.** This is where the non-diagnostic
  guardrail lives in the math itself.
- **IL-6 → CRP transducer.** CRP behaves as a near-linear low-pass integrator of IL-6, with a
  well-established plasma half-life (≈19 h, Pepys & Hirschfield 2003). Modeled as an
  indirect-response turnover ODE, `dCRP/dt = k_syn·IL6/(EC50+IL6) − k_deg·CRP`, whose closed-form
  steady state is verified numerically to be a stable attractor.
- **The one honestly-uncertain calibrated edge, ε.** The oral→systemic spillover efficiency ε
  is the single edge pinned by calibration — fit against the empirical **ΔCRP-after-periodontal-
  therapy anchor of ~0.5 mg/L** (the observed drop in CRP after periodontal treatment). This is
  what makes the centerpiece a *calibrated result* rather than a plausible-looking demo.
- **Counterfactual lever.** The same steady state supports an IL-6-neutralization counterfactual
  (an in-silico analogue of IL-6R blockade), yielding a predicted ΔCRP — the model's way of
  asking *"what if we removed the inflammatory driver?"*

### The neuro fork, and the jargon that goes with it

The neuro axis (`src/mech_neuro.py`) reuses the *same* inflammatory-gain quantity and forks it
into the brain: systemic IL-6 excess, gated by **blood-brain-barrier (BBB)** permeability,
drives neuroinflammation (microglial activation), which raises the growth rate of **tau**
propagation across the brain.

- **Fisher–KPP tau spread** (for the physician): tau is a protein that misfolds and spreads
  through the brain in a stereotyped, network-following pattern (the "Braak" progression:
  entorhinal cortex → hippocampus → neocortex). Fisher–KPP is a classic
  reaction–diffusion equation, `∂c/∂t = ∇·(D∇c) + α·c(1−c)`, that describes a *traveling front*:
  local growth (rate α) plus spread to connected regions. On the brain it is solved on the
  **connectome** (the brain's wiring graph) via its Laplacian. The tau-spread math itself is
  validated against tau-PET imaging.
- **CERAD, AFT, DSST** (for the bioengineer): these are the standardized cognitive tests used
  in the validation below. **CERAD** word-list learning measures memory (immediate and delayed
  recall); **Animal Fluency (AFT)** measures executive function; **Digit Symbol (DSST)** measures
  processing speed.

### Reusability beyond dentistry

Nothing about the apparatus is dental-specific. The pattern — *a bounded structural source → one
shared inflammatory-gain parameter → several coupled physiological axes → calibration against a
public dataset → a swept-range prediction with flagged unknowns* — is a template for any
oral-, gut-, or peripheral-inflammation-to-systemic-disease question. The modeling toolkit is
pure-python (a small ODE integrator, closed-form + RK4 network simulation, bootstrap-CI
statistics), so it runs anywhere and is reproducible from public data.

---

## 4. The Gladstone / Alzheimer's alignment (for the neurodegeneration researcher)

HISTORA's hackathon is co-organized with **Gladstone Institutes**, a leader in
neurodegeneration research. Gladstone's program centers on exactly the nodes this project
models: **tau** and network dysfunction, **APOE4** and human iPSC models,
**neuroinflammation and the blood-brain interface** (the "peripheral insult → BBB → microglia →
synapse/cognition" shape), and **microglial / innate-immune** biology in tauopathy.

### Why the oral→neuro axis is interesting to these labs

Most tau/microglia/BBB frameworks take the *insult* as given and study what happens
**downstream**. HISTORA's oral→neuro axis —

```
periodontitis → systemic inflammation → neuroinflammation → tau propagation
```

— supplies a **novel upstream perturbation** that can plug into those existing frameworks. The
concrete, modeled edge HISTORA generates is the coupling **inflammation → tau-spread growth rate
α** (`α_eff = α·(1 + β·N)`, where N is neuroinflammation). That gives a Gladstone-adjacent lab a
specific, parameterized hypothesis to test against their tau/microglia/BBB models and data,
rather than a vague "gum disease might matter."

### The honest causal caveat — stated up front, because it is a feature

This axis is a **live, biologically plausible hypothesis, not established causation**, and
HISTORA is built to say so loudly:

- The single most direct causal test of the periodontitis→Alzheimer's hypothesis —
  **atuzaginstat (COR388), a gingipain inhibitor, in the GAIN trial** — **failed both co-primary
  endpoints** (and raised safety concerns). A drug built on the *P. gingivalis*→AD story did not
  work. That is a high-confidence negative, and it is why the direction here is a hypothesis to
  probe, not a conclusion to assert.
- The inflammation→tau-α coupling (`beta_tau` in the code) is **flagged as a hypothesis and
  swept as a range**, never asserted as a fitted fact. Absolute tau-onset times are labeled
  *illustrative* (the literature CI on the tau growth rate is very wide); the deliverable is the
  **direction and the relative counterfactual**, reported as ranges.

This is the terrain HISTORA is designed to occupy: generate prioritized, testable, non-diagnostic
hypotheses on a real but unproven link, flag the confounders and the failures, and never
overclaim.

---

## 5. What makes it credible

Three things separate this from a plausible-sounding demo.

### (a) Real-data validation — the NHANES result

The neuro axis makes a specific, directional prediction: *more periodontal disease → worse
cognition*. That prediction was tested against real, public, de-identified data — **NHANES
2011–2012**, the cognition module (adults aged 60+), **n = 919** with complete periodontal,
cognitive, and confounder data. Using confounder-adjusted standardized regression (adjusting for
**age, education, smoking, and HbA1c**) with seeded bootstrap 90% confidence intervals:

| Cognitive outcome | Domain | Adjusted coefficient | 90% CI | Verdict |
|---|---|---|---|---|
| Digit Symbol (DSST) | processing speed | **−0.181** | [−0.226, −0.137] | **significant** |
| Animal Fluency (AFT) | executive function | **−0.098** | [−0.157, −0.045] | **significant** |
| CERAD immediate recall | memory | **−0.057** | [−0.108, −0.007] | **significant** |
| CERAD delayed recall | memory | −0.048 | [−0.100, +0.002] | ns (CI touches 0) |

**Three of four cognitive measures show a significant, confounder-adjusted negative
association** between periodontal severity (mean CAL) and cognition — the exact direction the
mechanistic model predicts. It is reproducible from public data with pure-python statistics.

### (b) Honest uncertainty, everywhere

- The NHANES finding is reported **honestly as an association, not proof of mechanism.**
  Adjustment roughly *halves* the crude effect (much of the raw signal is confounding, age above
  all); the effects are *small* (−0.05 to −0.18 SD), consistent with periodontitis being one
  contributor among many; the design is cross-sectional so **reverse causation is live** (early
  cognitive decline → worse oral self-care). Critically, the inflammatory mediator the model
  posits is **not co-measured** with cognition in this NHANES cycle, so the result establishes
  *whether* the predicted association exists, not *why*. The non-significant CERAD-delayed result
  is reported as-is, not rounded into the win.
- Every mechanistic coupling that is a hypothesis (the CV recruitment edge, the inflammation→tau-α
  edge) is **flagged as a scaffold and swept as a range**, not asserted. The strong, fitted
  pieces (CRP turnover kinetics, Fisher–KPP tau math) are used as anchors; the imposed couplings
  are labeled as such.
- The failed GAIN drug trial is included deliberately as the honest causal counterweight (§4).

### (c) The non-diagnostic guardrail — enforced, not just promised

The non-diagnostic invariant is not a disclaimer; it is enforced in code at *write time*. The
source term is built only from structural bands and flags, never a numeric patient value, and a
ledger-level validator rejects any attempt to write a numeric patient value. In the project's own
testing this guardrail was the single **clean, repeated engineering win**: a deterministic
missing-data-flagging directive moved reliability from **0.0 → 1.0** on real NHANES data (the
"W1" result), holding across every experiment. Reliability of the guardrail is demonstrated, not
assumed.

---


## Appendix — a shared glossary for a cross-disciplinary reader

| Term | Plain meaning |
|---|---|
| **CAL** (clinical attachment loss) | A structural measure of periodontal tissue destruction; the exposure variable here. |
| **BOP** (bleeding on probing) | A clinical sign of gum inflammation; feeds the model's structural source bands. |
| **IL-6** | Interleukin-6, a pro-inflammatory cytokine; the shared "inflammatory gain" driver. Mendelian-randomization evidence favors IL-6/IL-1β as *causal*, CRP as a *marker*. |
| **CRP / hs-CRP** | C-reactive protein, a liver-made acute-phase marker of inflammation; the model's observable readout and calibration target. |
| **tau** | A protein that misfolds and propagates through the brain along neural connections in Alzheimer's; the neuro-axis endpoint. |
| **BBB** | Blood-brain barrier; its inflammation-driven permeability gates the oral→neuro coupling. |
| **Fisher–KPP** | A reaction–diffusion equation for a growing, spreading front; used here for tau spread on the brain connectome. |
| **connectome** | The brain's network of connections; tau spread is simulated on it via its graph Laplacian. |
| **CERAD / AFT (Animal Fluency) / DSST (Digit Symbol)** | Standardized cognitive tests for memory / executive function / processing speed, respectively; the NHANES cognitive outcomes. |
| **NHANES** | The U.S. National Health and Nutrition Examination Survey; the public dataset carrying both periodontal exams and cognitive batteries. |
| **ε (spillover efficiency)** | The one calibrated model edge — how efficiently oral inflammation reaches the circulation; pinned to the ~0.5 mg/L ΔCRP-after-therapy anchor. |
| **non-diagnostic** | The project's hard constraint: outputs are population/parameter-level research hypotheses, never a patient diagnosis or an imputed patient value. |
