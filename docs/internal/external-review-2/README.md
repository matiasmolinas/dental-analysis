# External review 2 — expert clinician-researchers

Two independent evaluations from clinician-researchers / dentists (in Spanish), assessing the HISTORA PDF
and demo. Both converge on one thesis: **present an instrument, not a study** — the hero is turning
fragmented clinical records into a *research-ready cohort* on demand, with the missing data flagged;
IL-6/CRP is just today's hypothesis loaded into it.

- [`review-A-narrative-and-strategy.md`](review-A-narrative-and-strategy.md) — "very few changes; change how
  it's *told*": start with the problem, hypothesis-as-protagonist, a visual research-integrity checklist,
  an Export/protocol button, and the strategic reframe to *cohort-building infrastructure*. Favorite line:
  *"Researchers don't need another chatbot. They need an AI that builds research-ready cohorts from
  fragmented clinical data."*
- [`review-B-cohort-demo.md`](review-B-cohort-demo.md) — the 10/10 demo choreography: a cohort **funnel** →
  per-patient **timeline** → **missing-data** detection → a **hypothesis, not a conclusion** → genetics as
  *plausibility*, Alzheimer as one exploratory sentence.

**What we implemented in response** (analyzed with Fable for feasibility, honesty-first): the narrative
reframe (see [`../../PITCH.md`](../../PITCH.md), [`../../DEMO-SCRIPT.md`](../../DEMO-SCRIPT.md)) and a **real**
cohort-builder over public NHANES — the funnel, the completeness/"what's missing" report, the integrity
checklist, and the preliminary-protocol export (`demo/run_cohort.py`, `histora.cohort`). We deliberately did
**not** fabricate a synthetic clinic (Review B's implied EHR): the demo is real data, and the honest
cross-sectional limitation is the punchline.
