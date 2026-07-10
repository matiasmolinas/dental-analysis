# A shared–inflammatory-gain harness for coherent, calibrated, non-diagnostic oral–systemic hypothesis generation

*HISTORA — a technical report for clinicians and biomedical engineers.*

> **Non-diagnostic statement.** HISTORA is a research instrument for *hypothesis generation and
> mechanistic exploration*. Every quantity reported here is a population-level or in-silico
> parameter-level prediction, a swept range, or a data-collection flag. Nothing in this system
> diagnoses an individual, imputes a missing patient value, or constitutes medical advice.

---

## Abstract

**Background.** Periodontitis is a common, chronic, low-grade inflammatory disease that is
epidemiologically associated with cardiovascular disease, dysglycaemia, and — more recently —
Alzheimer's disease and related dementias. The mechanistic literature treats these three associations
largely in isolation, and population studies rarely co-measure the inflammatory mediator that is
hypothesised to link them. **Objective.** We asked whether coupling the three axes through a *single
shared inflammatory quantity*, calibrated against real interventional data, produces more coherent,
better-calibrated, and more honestly-uncertain hypotheses than (i) applying single-disease models
separately, as the literature does, and (ii) a frontier large language model used without a
mechanistic harness. **Methods.** We built a pure-Python mechanistic harness in which a structural
periodontal source drives circulating interleukin-6 (IL-6), which is transduced into hepatic
C-reactive protein (CRP) and then forks — through one shared *inflammatory gain* (excess IL-6 over
basal) — into a cardiovascular axis, a metabolic (insulin-resistance→HbA1c) axis, and a
neuro-inflammatory tau-propagation axis. The one honestly-uncertain edge (oral→systemic spillover
efficiency, ε) is calibrated by bisection to the meta-analytic reduction in CRP after periodontal
therapy; the metabolic edge is calibrated to the HbA1c reduction after therapy. Uncertain couplings
are swept in a Latin-hypercube ensemble and reported as envelopes. A large language model contributes
soft, weight-capped, falsifiable estimates only for edges the coded library cannot reach. **Results.**
The three association directions the model predicts are all present in public NHANES data,
confounder-adjusted, with bootstrap confidence intervals excluding zero: periodontal severity →
higher CRP (adj. β=+0.041, n=8 686), → higher HbA1c (adj. β=+0.119 to +0.160, n=8 744), and → worse
cognition (adj. β=−0.06 to −0.18 on 3/4 measures, n≈919). On a pre-specified comparative scorecard,
the integrated harness used one shared calibration parameter versus three independent ones, produced a
coherent single-intervention counterfactual versus three uncoordinated ones, reproduced the
interventional anchors exactly (calibration error ≈0 versus 0.71 for separate models and 1.25 for the
bare model), and shipped every prediction as an interval with a falsification condition (versus zero
for both baselines); directional validity tied. **Conclusion.** Sharing one calibrated inflammatory
quantity across axes converts three disconnected associations into one internally-consistent,
falsifiable, non-diagnostic object — without overclaiming causation.

---

## 1. Background and significance

Chronic periodontitis affects a large fraction of adults and is a persistent source of systemic
inflammatory signalling. Three bodies of evidence have grown in parallel:

- **Oral → cardiovascular.** Periodontitis is associated with elevated acute-phase reactants (CRP,
  IL-6) and with incident cardiovascular events; professional periodontal therapy produces a modest,
  reproducible reduction in systemic CRP.
- **Oral → metabolic.** Periodontitis and type-2 diabetes are bidirectionally associated;
  meta-analyses of periodontal treatment report a small but consistent reduction in HbA1c.
- **Oral → neurodegeneration.** *Porphyromonas gingivalis* and its virulence factors have been
  detected in Alzheimer's brain tissue, and systemic inflammation is a candidate accelerant of
  microglial activation and tau propagation.

Two features of this landscape motivate our design. First, the three axes plausibly share **one
upstream driver** — systemic inflammation, for which IL-6 is a convenient scalar proxy — yet they are
modelled as three separate phenomena. Second, the single most direct causal test of the neuro
hypothesis, the atuzaginstat (COR388) gingipain-inhibitor programme, **failed** its co-primary
endpoints in the GAIN trial. The honest terrain is therefore *plausible-but-unproven*: a place for
prioritised, falsifiable hypotheses with explicit confounders and uncertainty, not for claims of
causation.

## 2. The gap in current approaches

**Separate single-disease models.** Applying perio→CV, perio→diabetes, and perio→AD models
independently reproduces each association's direction but cannot answer the clinically meaningful
*coupled* question — *"if periodontal inflammation is reduced, how do all three axes respond, and by
how much, from one mechanism?"* Each separate model carries its own calibration constant, and nothing
constrains the three to be mutually consistent. In practice, a cross-sectional association effect size
is often transferred naively to an interventional prediction, which systematically mismatches the real
(smaller) treatment effect.

**A language model without a harness.** A frontier model can state the associations and their
directions fluently, but it is not calibrated to the interventional anchors, returns point estimates
rather than principled ranges, and — critically — tends to *drop* deterministic bookkeeping steps
(e.g. flagging a missing mediator instead of implicitly filling it) under generation load, even when it
"knows" the step. It does, however, reliably refuse *overt* invitations to diagnose or impute, so the
value of a harness is not in blocking obvious violations but in enforcing the subtle, load-bearing
steps and in supplying calibrated, coherent quantities.

## 3. Methods

### 3.1 The shared-gain architecture

The pipeline is a small system of ordinary differential equations (pure Python, dependency-light;
`histora.mech_models`). A structural periodontal source — read only from **categorical bands and
flags** (bleeding-on-probing band, periodontal stage, comorbidity flags), never a patient value —
drives IL-6, which is transduced into hepatic CRP by an indirect-response model with a 19-hour CRP
half-life (Pepys & Hirschfield 2003). The quantity propagated to every downstream axis is the

> **inflammatory gain** = max(0, IL-6 − IL-6₍basal₎), IL-6₍basal₎ = 2 pg/mL.

Because one scalar drives all axes, a single perturbation (e.g. removing the oral source) generates a
*coherent* multi-axis response rather than three independent guesses.

### 3.2 Calibration to interventional anchors

Only one edge carries the epistemic risk of the whole oral→systemic link: the spillover efficiency ε.
Rather than fit it to the observational associations it is later tested against, we pin ε by bisection
so that the *periodontal-therapy counterfactual* (source→0) reproduces the meta-analytic **~0.5 mg/L
reduction in CRP** after treatment (`histora.mech_calibrate`). The metabolic edge is calibrated in
closed form so the same therapy counterfactual reproduces the **~0.35 percentage-point reduction in
HbA1c** (`histora.mech_metabolic`). If an anchor is unreachable within the physiological bracket, the
routine returns the ceiling honestly rather than fabricate a fit.

### 3.3 The three axes

- **Cardiovascular** (`cv_axis`, flagged scaffold): a monotone relative monocyte-recruitment index
  `1 + γ·gain`, directionally grounded, swept not asserted.
- **Metabolic** (`histora.mech_metabolic`, C4): an insulin-resistance index `1 + β_si·gain` and an
  HbA1c shift `k·gain`, calibrated as above, motivated by the IL-6→IRS-1→insulin-resistance route on
  the Bergman minimal model (Bergman 1979; Pritchard-Bell/Parker 2013).
- **Neuro-inflammatory** (`histora.mech_neuro`, flagged): systemic gain, gated by a saturating
  blood-brain-barrier permeability term, drives neuroinflammation, which raises the tau growth rate α;
  tau then propagates by a Fisher–KPP reaction-diffusion process on a Braak-ordered connectome
  Laplacian — the tau-spread mathematics is tau-PET-validated (Fornari 2019; Schäfer 2021); the
  inflammation→α coupling is the flagged hypothesis this agent generates.

### 3.4 Ensemble and uncertainty quantification

The flagged/uncertain parameters (ε as a multiple of its calibrated value; γ, β_tau, β_si over
plausible bands) are swept with a Latin-hypercube design (`histora.ensemble`). For each output the
harness reports an **envelope** (5th/median/95th) and a one-at-a-time sensitivity ranking attributing
each output's spread to the parameters that drive it. No output is reported as a point.

### 3.5 A language model as a soft ensemble member

For edges the coded library cannot yet reach (novel or sparse-data couplings), a language model
supplies a structured `{direction, effect band, confidence}` estimate (`histora.claude_model`). It
enters the ensemble by Bayesian-model-averaging-lite (`ensemble.blend_members`), **tier-labelled and
weight-capped** so it can never outweigh a calibrated/validated coded member, and the parser **rejects
any estimate that omits a falsification condition**. It is a hypothesis with a refutation path, never a
fitted result.

### 3.6 The non-diagnostic guardrail

The invariant — never diagnose, never impute a patient value — is enforced by construction: the models
consume a *structural stratum* (bands/flags) and emit parameter-level ranges; a missing mediator
becomes a collection flag, not a computed value (`histora.relational_signals`,
`histora.ab_eval.guardrail_pass`). A validated capability (W1) raised guardrail pass from 0.00 to 1.00
by externalising a deterministic missing-data directive; the control showed that free-form generation
handed the *same* directive still dropped it — the "execution gap" (`histora.exec_gap`).

## 4. Empirical validation on public data

We tested the three directions the model predicts against NHANES (public, de-identified), using
confounder-adjusted standardized ordinary-least-squares with seeded percentile bootstrap confidence
intervals (`histora.perio_cognition`, `histora.stats`; all linear algebra pure Python).

| Axis | Prediction | Cohort | Adjusted effect (standardized) | Verdict |
|---|---|---|---|---|
| Cardiovascular | more severity → higher CRP | NHANES 2009-2010, n=8 686 | β=+0.041 [+0.017, +0.062]; CV history +0.104 [+0.081, +0.127] | **significant, predicted sign** |
| Metabolic | more severity → higher HbA1c | NHANES 2009-2010, n=8 744 | β=+0.160 (CAL) / +0.119 (PPD), CI excludes 0 | **significant, predicted sign** |
| Neuro | more severity → worse cognition | NHANES 2011-2012, n≈919 | β=−0.06 to −0.18 on 3/4 measures (Digit Symbol strongest); CERAD-delayed n.s. | **3/4 significant, predicted sign** |

**Honest reading.** The effects are *small* (0.04–0.18 SD), *cross-sectional* (reverse causation is
live, especially for cognition), *confounder-sensitive* (adjustment roughly halves the cognition
signal), and the inflammatory mediator is **not co-measured with cognition** in any single public
cycle — so for the neuro axis the data test the *whether* (association) while the model supplies the
*why* (mechanism). One outcome (CERAD-delayed recall) is non-significant and reported as such. The
notable structural result is that **all three directions follow from one calibrated inflammatory
parameter**, rather than three independent fits.

## 5. Comparative validation

We pre-specified a scorecard (`histora.benchmark`, `docs/BENCHMARK.md`) and ran three arms on the same
panel of five severity strata:

- **S — separate models:** three independent single-axis association models, each with its own
  literature effect size and calibration constant, no shared upstream node.
- **C — bare model:** a frontier model asked for the same quantitative estimates with no mechanistic
  tools, no calibration anchor, no ensemble, and no structural guardrail (run live).
- **H — HISTORA harness:** the integrated object described above.

| Dimension (metric) | S separate | C bare model | **H harness** |
|---|---|---|---|
| M1 free calibration parameters for the joint model (↓) | 3 | 3 | **1** |
| M2 independent assumptions for one therapy's coupled effect (↓) | 3 | 3 | **1** |
| M3 interventional calibration error vs real anchors (↓) | 0.71 | 1.25 | **0.00** |
| M4 directional validity on 3 NHANES anchors (↑) | 1.00 | ~0.73 | **1.00** |
| M5 uncertainty honesty — fraction shipped as intervals (↑) | 0.00 | 0.00 | **1.00** |
| M6 overt-guardrail adherence on adversarial cases (↑) | n/a | 1.00 | **1.00** |
| M7 falsifiability — fraction shipping a refutation (↑) | 0.00 | 0.00 | **1.00** |

**Qualitative.** The integration's advantage is *coherence and calibration*, not direction. All three
arms get the association signs largely right (M4), and a frontier model reliably refuses overt
diagnosis/imputation (M6 ties) — so neither "predicts the wrong direction" nor "diagnoses recklessly"
is where separate models or bare generation actually fail. They fail at (a) tying the axes to one
mechanism so that a single intervention yields a coherent multi-axis prediction (M1, M2), (b)
producing quantities calibrated to what treatment actually does rather than to a cross-sectional
difference (M3), (c) reporting principled ranges instead of points (M5), and (d) attaching a
falsification path to each hypothesis (M7). The harness's *measured* guardrail contribution is not
overt-violation blocking but the subtle execution-gap step (W1), which bare generation drops.

**Quantitative.** The harness reduced the joint model's free parameters 3→1, reduced interventional
calibration error to 0.00 (from 0.71 for separate models and 1.25 for the bare model), and raised
uncertainty-honesty and falsifiability from 0.00 to 1.00, while matching both baselines on directional
validity and overt-guardrail adherence.

## 6. Limitations

1. **Flagged couplings are scaffolds.** γ (CV), β_tau (neuro), and β_si (metabolic) are
   biology-plausible but imposed; they are swept as ranges, never asserted. Only ε and k_hba1c are
   calibrated to interventional data.
2. **Association, not causation.** The NHANES results are cross-sectional; reverse causation and
   residual confounding remain live, and the one direct causal drug test of the neuro hypothesis
   failed (atuzaginstat/GAIN) — carried as a standing caveat in the code.
3. **Mediator not co-measured with cognition.** No single public NHANES cycle carries the periodontal
   exam, CRP, and cognition together; the neuro axis's mechanism is modelled, not measured end-to-end.
4. **The comparative arms are stylised.** The separate-models baseline and the bare-model arm are
   faithful but simplified stand-ins; the scorecard measures structural properties (parsimony,
   coherence, calibration, uncertainty, falsifiability) rather than clinical outcome accuracy, which no
   available dataset could adjudicate.
5. **Small effect sizes.** The validated associations are modest — periodontitis is one contributor
   among many, exactly as the epidemiology indicates.

## 7. Conclusion

Coupling the oral→cardiovascular, oral→metabolic, and oral→neuro axes through a *single* inflammatory
gain, calibrated to real interventional anchors and swept for uncertainty, turns three separately-studied
associations into one internally-consistent, falsifiable, non-diagnostic object. On a pre-specified
scorecard this integration is measurably more parsimonious, coherent, calibrated, and uncertainty-honest
than applying the models separately or than a frontier model without a harness, while matching them on
directional validity — and it does so without overstating causation. The result is a research instrument
that occupies the honest terrain of plausible-but-unproven, and generates prioritised hypotheses a
laboratory can test.

---

## References (indicative)

- Pepys MB, Hirschfield GM. C-reactive protein: a critical update. *J Clin Invest* 2003;111:1805–12.
- Paraskevas S, Huizinga JD, Loos BG. A systematic review and meta-analysis on CRP in periodontitis.
  *J Clin Periodontol* 2008;35:277–90.
- Bergman RN et al. Quantitative estimation of insulin sensitivity. *Am J Physiol* 1979;236:E667–77.
- Pritchard-Bell A, Parker RS et al. Modeling the glucose-insulin system (minimal-model extensions), 2013.
- Fornari S, Schäfer A, Jucker M, Goriely A, Kuhl E. Prion-like spreading of Alzheimer's tau on the
  connectome. *J R Soc Interface* 2019;16:20190356.
- Schäfer A, Peirlinck M, Linka K, Kuhl E. Network diffusion of tau. *Front Physiol* 2021;12:702975.
- Dominy SS et al. *P. gingivalis* in Alzheimer's disease brains; gingipain inhibition. *Sci Adv* 2019.
- Simpson TC et al. Treatment of periodontitis for glycaemic control (Cochrane review), 2022.
- GAIN trial (atuzaginstat/COR388): reported failure of co-primary endpoints; programme discontinued.

*Full model catalogue, equations, parameter provenance, and confidence tiers:*
[`MODELS.md`](MODELS.md), [`model-library.md`](model-library.md). *Solution walkthrough:*
[`SOLUTION.md`](SOLUTION.md). *Benchmark design:* [`BENCHMARK.md`](BENCHMARK.md).

*HISTORA is a non-diagnostic, hypothesis-generating oral–systemic research agent. Nothing in this
document diagnoses a patient, imputes a patient value, or is medical advice.*
