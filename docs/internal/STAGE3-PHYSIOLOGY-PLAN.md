# Stage-3 physiology plan — deepening the mechanism, proteins, signs & processes

> **Purpose.** A prior analysis (branch `claude/project-analysis-physiology-wkaw5r`) found that HISTORA's
> *spine* (periodontal source → IL-6 → hepatic CRP → three axes) is rigorously modelled and honestly
> tiered, but that almost everything **downstream of IL-6 is a linear phenomenological multiplier**, the
> **protein network is collapsed to one scalar**, and several **physiological relationships (resolution,
> bidirectionality, the amyloid arm) are named but not modelled**. This plan promotes the models the
> repo *already cited but never built* into working, tested, non-diagnostic code — and specifies the
> Claude Science figures that make each mechanism legible to a scientist.
>
> **Non-diagnostic invariant is untouched:** every new module consumes *structural bands/flags* and emits
> *parameter-level ranges*; a missing mediator is a collection flag, never an imputed patient value.

## The finding that shapes the plan

The library census (`docs/model-library.md`) already contains every model these upgrades need. The work
is **tier promotion**, not new science:

| Gap (from the analysis) | Model already in the library | Old tier | New tier |
|---|---|---|---|
| Proteins collapsed to one scalar; no resolution loop | Reynolds 2006 (E2.1) · Kumar 2004 (E2.2) · Kotas–Medzhitov 2015 (E3.4) | reference-only | **built** (`mech_inflammation`) |
| CV is a linear multiplier, not a process | Ougrinovskaia 2010 (E2.6) | flagged scaffold | **built ODE** (`mech_cv`) |
| Metabolic is a static shift, no glucose–insulin dynamics | Bergman 1979 (E3.1) · Pritchard-Bell/Parker 2013 | staged substrate | **built ODE** (`mech_glucose`) |
| Diabetes↔perio loop not closed; smoking mis-signed | Graves 2026 (E3.2) | flagged scaffold | **closed loop** (`mech_metabolic`) |
| Source too coarse; no microbiome / keystone | Pasqualini 2026 (E3.5) · Martin 2017 (E3.6) · Allee (E3.7) | staged substrate | **built** (`mech_microbiome`) |
| Neuro is tau-only; no amyloid, no APOE4/age | Hao & Friedman 2016 (E2.7) | flagged scaffold | **A/T cascade** (`mech_neuro`) |
| Missing-mediator flags too narrow; proteins ungrounded | KB mediators · UniProt/PDB connectors | — | **extended flags + connectors** |

## Phases (all shipped in one PR)

**A — Multi-cytokine inflammatory core** (`mech_inflammation.py`). A reduced Reynolds/Kumar ODE in
TNF-α, IL-6, IL-10 with an autocatalytic pro-inflammatory feedback damped by IL-10. Delivers the
distinction the single scalar cannot make: **acute/resolving vs chronic** (two basins of attraction).
Reports a bistability check, a resolution index (IL-10/IL-6) and a *chronic effective gain* that
enriches the source. Figure: nullcline phase portrait with the two basins.

**B — Mechanistic axes replace the linear multipliers.**
- `mech_cv.py`: the Ougrinovskaia oxLDL→macrophage→foam-cell plaque ODE with the foam-cell→recruitment
  positive feedback; reports a plaque-burden trajectory and its oral-attributable relative increase.
- `mech_glucose.py`: the Bergman minimal model (glucose G, remote insulin action X) with insulin
  sensitivity `S_I(gain)` degraded by inflammation (IL-6→IRS-1); fasting glucose → HbA1c (ADAG), the
  metabolic axis now dynamic and calibrated to the ~0.35 pp therapy drop.

**C — Bidirectionality & source realism.**
- Close the **diabetes↔periodontitis** loop: hyperglycaemia amplifies the periodontal source, the
  source raises the gain, the gain raises HbA1c — solved to a fixed point (`mech_metabolic`).
- Fix the **smoking–BOP** sign: smoking *suppresses* bleeding-on-probing, so BOP under-reads severity;
  model it as an explicit BOP-band up-correction, not an opaque risk multiplier (`relational_signals`,
  `mech_models`).
- `mech_microbiome.py`: a reduced generalized Lotka–Volterra (*P. gingivalis* keystone vs *S. gordonii*
  commensal) with an Allee/quorum persistence threshold; a dysbiosis index scales the source.

**D — Complete the neuro axis** (`mech_neuro.py`). Add amyloid **A** as a second variable
(Hao–Friedman reduced cascade: neuroinflammation → amyloid → tau-α), and **APOE4** + **age** as effect
modifiers of amyloid production and BBB permeability. Tau propagation on the Braak connectome is
retained; the neuro axis is now A/T, not tau-only.

**E — Plumbing, honesty & tests.** Extend `REQUIRED_MEDIATORS` (TNF-α, IL-1β, IL-10, LDL, p-tau);
register the new sub-models, swept parameters and outputs; a per-module test; an integrative
`run_physiology.py`; figures in `plot_pipeline.py`; and the tier-promotion edits to
`model-library.md` / `MODELS.md`.

## Claude Science — the figures that make it land for a scientist

One figure per mechanism, plus the integrative "one lever, many axes" panel that is the whole thesis.
Claude Science adds what static PNGs cannot: **native interactive/animated figures, connectors that pull
real UniProt/PDB/OpenGWAS/NHANES data so figures are grounded not decorative, and a reviewer agent that
audits each figure against the citation registry.**

| Mechanism | Most impactful figure | Claude Science resource |
|---|---|---|
| Inflammatory core (A) | Nullcline **phase portrait** with the resolution vs chronic basins; TNF/IL-6/IL-10 time courses | native figure + `dataviz` |
| Atherosclerosis (B) | oxLDL→foam-cell→**plaque** trajectory with the ensemble band | native animated figure |
| Metabolic (B) | Bergman glucose–insulin response + HbA1c **waterfall** after therapy | native figure |
| Neuro (D) | **Animated tau front** on the Braak connectome ± oral source; joint **A/T** trajectory | native network/animation |
| Diabetes↔perio (C) | **Causal-loop diagram** + fixed-point hysteresis | diagram + figure |
| Proteins (E) | **3-D structures of IL-6 / IL-6R / CRP** (and tocilizumab blockade) | **UniProt/PDB connector** |
| Genetic probe (built) | MR scatter (IVW/Egger) over **live OpenGWAS** | **OpenGWAS connector** |
| **Integrative** | **"One lever, N axes":** lower ε (= periodontal therapy) → CV, metabolic & neuro respond coherently on one timeline | native dashboard |
| Uncertainty (built) | Envelope forest + sensitivity tornado per axis | `plot_pipeline.py` |

**Built offline (`run_physiology.py --plot`):** the CV foam-cell trajectory, the Bergman glucose response,
the **two-basin inflammatory phase portrait**, the **Braak tau front** (flagged EXPLORATORY), the
**diabetes↔perio fixed-point cobweb**, the **protein signaling axis** (IL-6→IL-6Rα/gp130→CRP with UniProt/PDB
IDs + the tocilizumab blockade node — `histora.proteins`, the connector layer), and the **one-lever** panel —
the last with the *calibrated* CV/metabolic axes kept **visually separate** from the *EXPLORATORY* neuro
axis, and `axis_tier` carried in the JSON, so the neuro numbers can never be quoted as a calibrated result.
The remaining rows (native **animations** and live **3-D** protein structures) are the Claude-Science upgrade
of this same data — the `histora.proteins` registry is exactly what its UniProt/PDB connector consumes.

Workflow: the `histora-mechanistic-pipeline` skill runs the deterministic engine → connectors ground the
figures → the reviewer agent audits each figure against `CITATIONS.md` → every figure carries its tier
label (calibrated vs flagged) and its falsification condition, so nothing over-claims.

*Non-diagnostic throughout; population/parameter/instrument level only.*
