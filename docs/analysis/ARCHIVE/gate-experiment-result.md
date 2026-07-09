# Circularity-gate result (mode 4): CIRCULAR — but confounded, not a clean NO-GO

> 2026-07-09, live Claude. Result of the first gate experiment from
> [`fable-predicted-workspace-design.md`](fable-predicted-workspace-design.md) §6.
> Roles as run: executor = Opus, blind = Opus, predictor = **Opus (fallback)**, judge = Sonnet.
> Written directly (not via a Fable sub-agent: Fable refuses this medical-meta-analysis topic —
> see below). Grounded in `results/gate_report.json`.

## The run
Planted non-obvious gap: a hypertensive on **amlodipine** (a dihydropyridine CCB) with **gingival
overgrowth** — the finding may be **drug-induced** (a known CCB side effect), a confounder of the
periodontal reading. One planted case; blind converger → C, Opus executor → O, predictor ×K=5 → P;
gate = `P \ (O ∪ C)`.

## Result
`VERDICT: circular` — the non-redundant surface `P \ (O ∪ C)` was **empty**.

| quantity | value |
|---|---|
| blind C items | **24** (Opus blind was exhaustive) |
| planted gap surfaced by blind? | **False** (the plant WAS non-obvious to the blind — good) |
| stable P items (≥0.6, absent-from-output) | **2** (both about smoking) |
| non-redundant surface `P \ (O ∪ C)` | **0** |
| planted gap in the surface? | **False** |
| predictor models actually used | `[opus, opus, opus, opus, opus]` (Fable refused all 5 → fallback) |

## Why this is CONFOUNDED, not a clean "circular → NO-GO"

Two harness/setup flaws — not the concept — drove the empty surface. The raw signal for the
concept actually exists (an isolated single Opus prediction put the amlodipine confounder as its
**top item**, `appears_in_output=False`); the gate's aggregation and model setup are what failed.

**(1) Exact-key stability clustering fragmented the recurring items.** `aggregate_predictions`
counts stability by **exact `key` match**. But each run mints its own snake_case key for the same
concept (`amlodipine_gingival_overgrowth` vs `drug_induced_overgrowth` vs `ccb_gingival_hyperplasia`
…). A concept that recurred in, say, 4/5 runs under 4 different keys is counted as four items at
stability 0.2 each → **all filtered out below the 0.6 threshold**, never reaching the surface. The
design doc explicitly required "normalize surface forms, cluster synonyms" (a semantic step); the
implementation took the exact-key shortcut, which **systematically biases toward "circular."** The
amlodipine gap is the most likely casualty: strongly present in a single run, absent from the
aggregated stable set.

**(2) Fable refused → executor = blind = predictor = Opus, collapsing the model-diversity that WAS
the design.** The whole point of mode 4 was a **different, uncommitted** model predicting the
executor's workspace. Fable refused the topic (stop_reason=refusal) on all 5 runs, so the Opus
fallback ran — making the *predictor the same model as the blind and the executor*. Opus-as-blind
was extraordinarily thorough (24 considerations), so C nearly covers the space, and any gap the
predictor (also Opus) finds, the blind (also Opus) tends to find too. The design's escape hatch —
an outside perspective — was structurally removed by the refusal.

## What the run does and does not license
- **Does NOT license "the approach is circular."** The empty surface is explained by a clustering
  bug + the loss of model diversity, both fixable; it is not evidence that an uncommitted predictor
  adds nothing.
- **Does license two concrete lessons:** (a) the gate needs **semantic clustering** of predicted
  items across runs (a judge/embedding step), not exact-key; (b) mode 4 needs a **genuinely
  different predictor that does not refuse** — or, failing that, the honest admission that with
  Opus-predicts-Opus and an exhaustive Opus blind, the test is stacked toward circular and can't
  fairly answer the question.
- **One thing held up:** the plant was **non-obvious to the blind** (`planted_gap_surfaced_by_blind:
  False`) and the predictor *did* surface it in a single run — so the raw per-run signal is real; the
  failure is downstream (aggregation + model setup).

## Next (to make the gate trustworthy)
1. **Fix aggregation → semantic clustering.** Add a clustering pass (a judge call, or embeddings) that
   groups synonymous predicted items across the K runs before computing stability. Re-run; check
   whether the amlodipine confounder now survives to `P \ (O ∪ C)`.
2. **Restore model diversity for the predictor.** Options: a different non-refusing model as
   predictor; a reframed request that Fable will run (the benign "completeness review" rewrite ALSO
   refused, so this needs care); or accept Opus-predicts-Opus but pair it with a **leaner blind**
   (a single-pass converger, not an exhaustive 24-item dump) so C doesn't trivially cover everything.
3. Only after 1–2 does a `circular` verdict mean what it claims. This run is **inconclusive-confounded**.

## Note on Fable + medical topics
Fable (`claude-fable-5`) returned `stop_reason: refusal` for the predictor task on this medical
case, under both the paper-faithful "predict the workspace" prompt and a benign "analytical
completeness review" rewrite. The executor and blind roles (also medical, on Opus) did not refuse.
Per the project lead, the harness falls back to Opus when the primary predictor refuses; the
`meta.predictor_models_used` field records which model produced each run for transparency.
