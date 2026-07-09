# Mechanistic-Modeling Harness — Plan

> Produced 2026-07-09. A forward direction for HISTORA that reframes the settled §0 verdict
> (*"real, non-redundant signal; no demonstrated payoff as an optimizer"* — see
> [`RESEARCH_SUMMARY.md`](RESEARCH_SUMMARY.md)) rather than contradicting it. Companion artifact:
> [`model-library.md`](model-library.md) (populated by the deep-research pass).

## 0. The thesis (why this is the missing piece, not a pivot)

The honest null from the whole arc — no actuator turned the workspace signal into an outcome gain
— has a most-likely cause we never eliminated: **the NHANES oral–systemic task does not require
mechanistic reasoning.** Relating periodontitis to cardiovascular data over tabular records is
largely **re-derivable by statistical association**. If the task doesn't need the model to *build a
mechanism*, there is **no headroom** for reading its internal workspace to help reach — the lens
didn't fail, the task had no ceiling to raise.

This plan builds the task that *does* need thinking: an agent that **formulates and runs
mechanistic mathematical models** (ODEs, control loops, fluid transport, ecological dynamics) to
generate falsifiable, non-diagnostic hypotheses about oral–systemic disease — grounded first by a
**deep-research pass** over existing scientific models. Two consequences:

1. **A scientifically stronger product.** Findings move from "these variables co-occur" to "here is
   a candidate mechanism, encoded as equations, simulated, and checked against data — and here is
   what it predicts and where it breaks." That is hypothesis generation with a falsifiable backbone.
2. **The fair test the lens/monitor never got.** A mechanistic-reasoning task is one where a wrong
   internal model yields a *detectably* wrong output. That is exactly the regime where Path A (the
   QA monitor) and the ablation can finally ask — honestly — *does reading the workspace help when
   the task actually requires reasoning?* This **composes with** the existing apparatus; it does not
   replace it.

**Guardrail unchanged and load-bearing.** Everything stays **non-diagnostic**: the agent generates
research hypotheses and mechanistic models, never a patient diagnosis, never an imputed value. A
mechanistic model that does not fit real data must be reported as *not fitting* — the anti-Goodhart
and protected-guardrail invariants apply to models exactly as to prompts.

## 1. Architecture — two harness layers

### Harness 0 — Deep Research (the prerequisite)

A retrieval + curation layer that turns the open literature into a structured **model library**:
`mechanism → math formalism → variables → parameters + ranges → data sources → key papers →
confidence → caveats`. Without it, mechanistic modeling is invention; with it, it is *instantiating
models that already have scientific precedent*. Built on WebSearch/WebFetch + paper mining; output
is [`model-library.md`](model-library.md) (a living, cited artifact) plus a machine-readable index.

**Status:** deep-research pass launched (four tracks — fluid mechanics/glymphatic; inflammation &
neuroinflammation ODEs; control theory & ecological/Lotka-Volterra; periodontitis↔Alzheimer +
Gladstone alignment). Results assemble into the model library.

### Harness 1 — Mechanistic Modeling (the core)

Tools that let the model *formulate and run* models, not merely describe them:

| Tool | Capability | Library |
|---|---|---|
| symbolic math | derive equilibria, stability (Jacobian eigenvalues), bifurcations | `sympy` |
| numerical integration | simulate ODE/PDE dynamics over time | `scipy.integrate` |
| parameter fit + sensitivity | fit to data, local/global sensitivity, identifiability | `scipy.optimize`, `numpy` |
| (optional) transport/CFD-lite | 1-D advection–diffusion, Windkessel, reduced flow | `numpy`/`scipy` |

The loop: **propose mechanism → encode as equations → simulate → confront with data → report fit,
sensitivity, and where it fails.** The agent's *reasoning* — which mechanism, which formalism, which
parameters — is where its intelligence makes the difference, and where the workspace signal becomes
relevant.

## 2. Candidate first models (from the strong end of the library)

Chosen for real precedent (see the library for citations + honest confidence). The hackathon build
should take **one** end-to-end, not all.

- **Cytokine-mediated inflammatory feedback (ODE)** — periodontitis → systemic IL-6/CRP spillover →
  effects on *both* the vascular (endothelial) *and* neuro (neuroinflammation) axes. One model, two
  systemic edges. **Strong**; the recommended hackathon centerpiece.
- **Wall shear stress → endothelial dysfunction (fluid mechanics)** — the periodontitis→CV vascular
  edge; established CFD-in-cardiology. **Strong.**
- **Glymphatic Aβ clearance (fluid transport)** — the systemic-inflammation→Alzheimer edge; fluid
  mechanics of CSF clearing amyloid. **Strong**, and the natural bridge to the Gladstone axis.
- **Bergman minimal model + diabetes↔periodontitis feedback (control theory)** — bidirectional loop
  as a regulated system losing stability. **Medium–strong.**
- **Oral-microbiome dysbiosis (generalized Lotka-Volterra)** — keystone-pathogen (*P. gingivalis*)
  vs commensal dynamics. **Medium.**
- **Tau/Aβ prion-like spread (reaction–diffusion)** — speculative but Gladstone-aligned; flag as
  hypothesis, not result.

## 3. The Gladstone / Alzheimer axis

The hackathon is co-organized with **Gladstone Institutes**, a leader in neurodegeneration research.
Adding the **periodontitis ↔ Alzheimer's** edge (a) resonates directly with the co-organizer and (b)
extends the agent from *oral–CV* to *oral–CV–neuro* — the same relational apparatus, a second
systemic axis, and mechanistically rich (neuroinflammation ODEs, glymphatic fluid transport,
prion-like tau spread). Evidence anchor: *P. gingivalis*/gingipains in Alzheimer's brains (Dominy et
al. 2019) — with the **honest caveat** that the derived drug trial (atuzaginstat/COR388) did not
succeed, so this is a **live hypothesis, not settled causation** — precisely the terrain for a
non-diagnostic hypothesis-generating agent. (See the library's Gladstone-alignment section.)

## 4. Phases

| Phase | Deliverable | Model cost | Composes with |
|---|---|---|---|
| **0. Deep research** | `model-library.md` (cited, confidence-flagged) + index | low (web) | — |
| **1. Modeling harness** | sympy/scipy tools + one model instantiated, simulated, fit, sensitivity-analyzed | medium | new `src/` module + tools |
| **2. Fair lens/monitor re-test** | re-run Path A (monitor) + ablation on the mechanistic task, where reasoning defects are detectable | medium–high | `qa_monitor.py`, `ablation.py` |
| **3. Oral–neuro axis** | Alzheimer edge as a second domain, Gladstone-forward | medium | `bridge_concepts.py`, schemas |

## 5. Honest gut-check

- **Risk — elegant fiction.** A mechanistic model over re-derivable data can become storytelling.
  *Mitigation:* every model validated against real data; report non-fits; guardrail + anti-Goodhart
  apply to models.
- **Risk — scope explosion.** This is a large surface. *Mitigation:* one model end-to-end for the
  hackathon (the cytokine feedback ODE), the rest as library.
- **Risk — analogy worship.** Chaos/predator-prey framings are attractive but weakly evidenced here.
  *Mitigation:* the library's confidence flags gate what gets built; speculative models are labeled
  hypotheses, never results.
- **Opportunity — closes the lens loop.** Phase 2 is the first task with genuine mechanistic
  headroom, i.e. the fair test the §0 verdict flagged as still-owed.

## 6. What would make this a result (not just a demo)

A single mechanistic model, deep-research-grounded, instantiated and simulated by the agent, that
(a) fits a real public dataset on the axis it models, (b) makes a falsifiable prediction, and (c)
shows — via the monitor/ablation re-test — whether reading the workspace helps the agent build a
*correct* model versus a plausible-but-wrong one. That last clause is the honest bridge back to the
whole investigation: **give the model a task that needs thinking, then measure whether reading its
thinking helps.**
