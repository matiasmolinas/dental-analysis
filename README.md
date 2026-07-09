# dental-analysis — HISTORA Oral-Systemic Intelligence Agent

Interpretability-guided optimization of the input format, context, and knowledge
base for a **non-diagnostic** research agent that relates periodontal data
(probing, bleeding, bone loss, treatments, radiographs) to medical /
cardiovascular data (hypertension, diabetes, lipids, smoking, medications, CV
history) and surfaces oral-systemic risk profiles and research hypotheses.

## The problem we solve

Medical and dental records live in separate silos, and the periodontal <->
cardiovascular link runs through *hidden mediators* (inflammation, C-reactive
protein, atherosclerosis, endothelial dysfunction, bacteremia) that no single
record makes explicit. HISTORA supplies the missing data layer that integrates
oral and systemic records. The open question this project answers is:

> Given integrated oral + systemic data, **we do not know a priori the best way to
> present, formulate, and contextualize it** so that a model actually represents
> the true oral-systemic relationships — which values to complete, which input
> format to use, and which knowledge to inject.

We answer it with interpretability instead of guesswork, and turn the answer into
a self-improving, **non-diagnostic** research agent.

## How it works (the loop)

Full method in [`docs/APPROACH.md`](docs/APPROACH.md). A **second model instance — the
Lens Observer** (`agents/lens-observer.md`, Opus) reads the **inferred Jacobian lens**
of the primary model — the workspace self-report the primary emits while it processes
a prompt (`claude-workspace-probe` → `schemas/lens_readout_schema.json`) — and drives
the loop:

1. **Run** the task on the Executor with the inferred-lens readout active; emit the
   output **plus** the readout.
2. **Diagnose** — the Observer compares the readout to the spec (required mediators,
   variables, procedure steps) and returns a typed deficiency map
   (`schemas/deficiency_map_schema.json`): missing/incorrect variables, uncovered
   chain-of-thought steps, unrepresented mediators, under-specified framing.
3. **Evolve** — route each deficiency to the cheapest of five surfaces (work prompt,
   skill, KB context, sub-agent def + injected variables, **harness code**) as a
   bounded, readout-grounded edit. Values to complete become **collection flags, never
   imputed**.
4. **Consolidate + inject** — update the cumulative **Session Working-Consciousness**
   ledger and, from it, inject/modify the next prompt. Lessons compound across turns.
5. **Gate** — T0 edits are ephemeral (in-session); durable T1 edits are gated by
   Claude held-out accuracy + the protected non-diagnostic guardrail + tests + human
   approval. The final authority is task accuracy + guardrail, never the readout score.

**Claude only.** This project runs entirely on Claude — there is no proxy model, no GPU,
and no measured lens. We explore the Jacobian-lens paper *indirectly*, through the
self-report **skill**. Because the readout is self-report, the Observer corroborates
load-bearing claims with an API-observable behavioral test — **counterfactual
sensitivity** (flip one input factor; the dependent axis should move, unrelated axes
should not) — so the loop stays grounded on Claude alone.

**Epistemic status:** the inferred lens is self-report exercised as a readout channel —
directional, never a measurement and never clinical evidence; task accuracy on Claude
plus the protected guardrail are the authorities.

**Docs:** [`docs/APPROACH.md`](docs/APPROACH.md) (**the canonical, domain-general
description of the method** — inferred-lens Observer + Session Working-Consciousness),
[`docs/IMPACT.md`](docs/IMPACT.md) (where/when the approach generates large impact a
priori — predictors, archetypes, and a scoring rubric),
[`docs/REFORMULATION.md`](docs/REFORMULATION.md) (the delta from the earlier baseline +
the R0–R6 workplan), [`docs/PLAN.md`](docs/PLAN.md) (living workplan, status,
decisions), [`docs/HACKATHON_STRATEGY.md`](docs/HACKATHON_STRATEGY.md)
(Built with Claude: Life Sciences — tracks, named user, one-week plan, demo, judging),
[`docs/DATASETS.md`](docs/DATASETS.md) (NHANES 2009–2010 real anchor + Synthea
longitudinal; schema mapping and access).

## Exploring the Jacobian lens indirectly (and the API feature we're proposing)

We explore Anthropic's Jacobian-lens paper **indirectly, through the self-report
skill** — never an instrumented lens, never a proxy model, only Claude. The primary
emits a workspace self-report (`claude-workspace-probe` →
`schemas/lens_readout_schema.json`); the Lens Observer analyzes that readout of the
*primary* model, diagnoses deficiencies (missing/incorrect input variables, uncovered
chain-of-thought steps, unrepresented mediators), and drives bounded, gated evolution
of five surfaces — work prompts, skills, KB context, sub-agent definitions + injected
variables, and **harness code** — while curating the **Session Working-Consciousness**
ledger it injects prompts from. This is an honest limit: the inferred lens is
**self-report exercised as a readout channel — never a measurement and never clinical
evidence** (we corroborate load-bearing claims with counterfactual-sensitivity flips).

> **The feature we're proposing to Anthropic.** Exploring the paper this indirectly,
> the results — and we are frankly **speculating**, since we have no ground truth — look
> **very promising**: the Observer can localize *which* concept or variable a prompt
> failed to make representable, and act on it. That makes one API feature obviously
> desirable: **expose the real Jacobian lens on Claude through the Anthropic API.** If
> it existed, this exact architecture would swap the inferred signal for a **measured**
> one with **no change to the loop** — turning directional hypotheses into causal ground
> truth, enabling representation swaps, and letting the Observer optimize against the
> model's true internal workspace. That is where this would reach its real power; we
> raise it as a feature request precisely because the indirect results are encouraging.

## Layout

```
dental-analysis/
  src/
    bridge_concepts.py         # target mediators + shared concepts (the Observer spec)
    record_formats.py          # one NHANES-grounded record, five candidate formats (A–E)
    relational_signals.py      # deterministic, non-diagnostic structural signals (harness)
    nhanes_mapping.py          # schema field -> NHANES 2009-2010 file+variable codes
    nhanes_loader.py           # download XPT + build a grounded case
  schemas/
    output_schema.json         # non-diagnostic structured output contract
    lens_readout_schema.json   # inferred-lens readout the executor emits
    deficiency_map_schema.json # deficiency map + bounded edits the Observer returns
    examples/                  # worked readout -> deficiency-map example (schema-valid)
  prompts/
    observer.md                # Lens Observer system prompt (inferred-lens controller)
    evaluator.md               # Claude final-analysis prompt
  agents/                      # orchestrator + specialists + lens-observer + skillopt-optimizer
  skills/                      # reusable capability docs (SkillOpt-trainable; guardrail protected)
  tests/                       # harness tests (pure-python, no GPU)
  .session/                    # Session Working-Consciousness template + worked example
```

See [`agents/README.md`](agents/README.md) and [`skills/README.md`](skills/README.md)
for the full subagent + skill catalog and the skill↔subagent map.

## Reference repos (siblings, not part of this repo)

- `../jacobian-lens/` — Anthropic's Jacobian-lens reference implementation. We **do not
  run or import it** — this project explores the paper *indirectly* via the self-report
  skill on Claude. It is the instrument we would use directly if the lens were exposed
  on Claude through the API (see the API-feature section above).
- `../SkillOpt/` — Microsoft Research SkillOpt: skills as trainable parameters,
  the reference for the skill-evolution loop (the T1 promotion tier).
- `Doriandarko/skirano-skills` (GitHub, not cloned) — Pietro Schirano's `j-space-lens`
  self-report skill that inspired `skills/claude-workspace-probe.md`. Referenced with
  attribution, **not vendored** (its repo has no license); install its plugin
  separately if you want the original.

## Run

Everything runs on Claude — no GPU, no notebook. The agents and skills are Claude Code
artifacts; the `src/` harness is pure-python and loads without a GPU. Verify the
harness:

```bash
python3 tests/test_relational_signals.py     # deterministic signals (5/5)
```

The full loop is driven by the orchestrator (`agents/orchestrator.md`) and the Lens
Observer (`agents/lens-observer.md`); a worked, schema-valid turn is in
`schemas/examples/` and a 3-turn session ledger in `.session/example_case01.md`.

## Data

Cases are grounded in **NHANES 2009–2010** (public, de-identified — the cycle that
pairs the full-mouth periodontal exam with CRP), plus the **NHANES Oral Microbiome
2009–2012** mediator layer (SEQN-linked) and **Synthea** for longitudinal
progression and shareable demo records. Mapping in [`src/nhanes_mapping.py`](src/nhanes_mapping.py),
loader in [`src/nhanes_loader.py`](src/nhanes_loader.py), full detail in
[`docs/DATASETS.md`](docs/DATASETS.md).

## Guardrails

Non-diagnostic throughout. Missing mediating data becomes a **collection flag**,
never an imputed patient value. Every relational axis cites the input fields it
was derived from. NHANES-grounded / synthetic data only for methodology development.

## Note

`jacobian-lens/` (sibling folder) is the upstream paper reference and is left
unmodified; this project does not run or import it — it explores the paper indirectly,
on Claude, through the self-report skill.
