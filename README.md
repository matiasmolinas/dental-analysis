# dental-analysis — HISTORA Oral-Systemic Intelligence Agent

> **What this is (honest, post-investigation).** An **apparatus and a rigorous negative.**
> We built a Claude-only system to ask whether reading a model's internal *workspace* helps
> optimize its inputs — an inferred-lens Observer loop, five-surface evolution, a
> session-consciousness ledger, a guardrail-protected gate — and a tested experimental
> apparatus (A/B with bootstrap CIs, an ablation, a counterfactual-sensitivity test), run
> live on real NHANES cases. The finding: the workspace signal is genuinely **non-redundant
> with the output**, but **no actuator we built turns it into an outcome gain over a strong
> blind baseline** on this task. The one clean, repeated win — reliable missing-data flagging
> (0.00→1.00, 6/6) — is a **deterministic directive, not the lens.** Canonical conclusions:
> [`docs/RESEARCH_SUMMARY.md`](docs/RESEARCH_SUMMARY.md) and [`docs/RETROSPECTIVE.md`](docs/RETROSPECTIVE.md).

A **non-diagnostic** research agent that relates periodontal data (probing, bleeding, bone
loss, treatments, radiographs) to medical / cardiovascular data (hypertension, diabetes,
lipids, smoking, medications, CV history) and surfaces oral-systemic risk profiles and
research hypotheses — used as the domain instance for the methodology above.

## What works (the validated pieces)

- **Deterministic missing-data flagging → guardrail reliability.** `missing_data_flagged`
  and `guardrail_pass` go **0.00 → 1.00 (6/6)** on real NHANES cases — the single clean,
  repeated win. It comes from a **hardcoded data-completeness directive**
  (`src/relational_signals.py`, `src/ab_eval.py`), *not* the lens: free-form convergers handed
  the same directive fell back to 0.00.
- **The protected non-diagnostic invariant.** Never evolved; part of every gate; enforced at
  *write time* where it could leak cross-patient (`src/lever_ledger.py` rejects any numeric
  patient value). Held across every experiment.
- **The honest experimental apparatus** — `src/ab_eval.py`, `src/ablation.py` (bootstrap CIs),
  `src/counterfactual.py`. Domain-general, 44 tests green; it is what produced a rigorous
  `lens_inconclusive` instead of a false positive.

## What was tried and is inconclusive

The **Observer-lens loop** (below) ran as software, but its lens-driven contribution over
*blind* convergence was **not demonstrated** (`lens_inconclusive`; the whole gain was blind
prompt engineering). The Session Working-Consciousness ran live once (n=1); cross-session
memory and targeted injection show a small, single-case signal without demonstrated payoff.
Details + the one number for each: [`docs/RESEARCH_SUMMARY.md`](docs/RESEARCH_SUMMARY.md) §2,
[`docs/RETROSPECTIVE.md`](docs/RETROSPECTIVE.md).

**The loop (tested, inconclusive).** A second model instance — the **Lens Observer**
(`agents/lens-observer.md`) — reads the primary's **inferred Jacobian-lens** self-report
(`claude-workspace-probe` → `schemas/lens_readout_schema.json`), diagnoses deficiencies
(`schemas/deficiency_map_schema.json`), and drives bounded, gated edits across five surfaces
(work prompt, skill, KB, sub-agent def + injected variables, **harness code**), curating a
Session Working-Consciousness ledger. Claude only — no proxy, no GPU, no measured lens; the
inferred lens is **self-report, never a measurement or clinical evidence**, corroborated by
counterfactual-sensitivity flips. The final authority is task accuracy + the protected
guardrail, never the readout score. Full method: [`docs/APPROACH.md`](docs/APPROACH.md).

## The measured-lens API feature (the forward claim)

The evidence-motivated ask — and the one route that removes the access layer everything is
bottlenecked on: **expose the real Jacobian lens on Claude through the Anthropic API.** This
repo is the **consumer built and waiting for it** — swapping the inferred signal for a
measured one is a signal-source change with no redesign (`schemas/lens_readout_schema.json`
is the contract). This is a *forward claim*, not a finding. See
[`docs/API_FEATURE_REQUEST.md`](docs/API_FEATURE_REQUEST.md).

**Docs:** [`docs/RESEARCH_SUMMARY.md`](docs/RESEARCH_SUMMARY.md) (**canonical** — the whole
arc, every hypothesis answered + next steps), [`docs/RETROSPECTIVE.md`](docs/RETROSPECTIVE.md)
(what worked / was inconclusive / failed), [`docs/APPROACH.md`](docs/APPROACH.md) (the method,
domain-general), [`docs/API_FEATURE_REQUEST.md`](docs/API_FEATURE_REQUEST.md) (the ask),
[`docs/AB_PROTOCOL.md`](docs/AB_PROTOCOL.md) (the apparatus),
[`docs/DATASETS.md`](docs/DATASETS.md) (NHANES + Synthea). Historical / hypothesis-status:
[`docs/REFORMULATION.md`](docs/REFORMULATION.md), [`docs/PLAN.md`](docs/PLAN.md),
[`docs/IMPACT.md`](docs/IMPACT.md), [`docs/HACKATHON_STRATEGY.md`](docs/HACKATHON_STRATEGY.md).
The full research trail is archived under
[`docs/analysis/ARCHIVE/`](docs/analysis/ARCHIVE/README.md).

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
