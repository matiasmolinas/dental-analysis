# Session Working-Consciousness — example_case01

> Worked 3-turn example (committed, not a live session) showing the closed loop:
> readout → deficiency → T0 injection → verified outcome → consolidation. Pairs with
> `schemas/examples/readout_case01.json` (Turn 1). Non-diagnostic; no imputed values.
> See `skills/session-working-consciousness.md`.

**Case / goal:** Perio (stage III/B, BOP 62%) + HTN + T2DM, hs-CRP absent; surface the
oral-systemic relational axes non-diagnostically. Find the cheapest input lever that
makes the inflammatory mediators representable.
**Started:** 2026-07-08  ·  **Turn:** 3

## Task model
- Naive format A surfaces shared factors (diabetes/smoking) by copying, but the
  inflammatory mediators (CRP, endothelial, atherosclerosis) stay absent/faint.
- Two cheap levers move them: (1) inject `hs_crp=MISSING` explicitly, (2) attach the
  2-sentence mechanistic KB bridge. Making `axis_derivation` an explicit step fixes
  side-by-side listing.

## Consolidated beliefs
- [x] Flagging the missing mediating datum (`hs_crp=MISSING`) triggers the missing-data
  pull that a silent gap does not — evidence: Turn 1→2 (absent→mid), counterfactual flip.
- [x] The mechanistic KB snippet raises CRP + endothelial from absent to mid-stage —
  evidence: Turn 2→3 reread confirmed.
- [x] Naming `axis_derivation` as a required step converts side-by-side listing into a
  related axis — evidence: Turn 2→3 (skipped→covered).

## Pending hypotheses
- [ ] Does `bacteremia` need the oral-microbiome KB line specifically, or will the
  general inflammatory bridge surface it? (still absent at Turn 3)

## Active injections (T0 ephemeral — auto-revert at session end)
| Injection | Surface | Grounding | Verified? |
|---|---|---|---|
| `hs_crp=MISSING` field + note | injected_variables | Turn 1 missing_variable(hs_crp) | confirmed (Turn 2) |
| 2-sentence mechanistic KB bridge | kb_context | Turn 1 missing_mediator | confirmed (Turn 3) |
| axis_derivation as required step | subagent_def | Turn 1 uncovered_cot_step | confirmed (Turn 3) |

## Turn log
### Turn 1
- **Readout:** shared factors surfaced; inflammation faint/late/low; CRP, atherosclerosis,
  endothelial, bacteremia absent; hs_crp not present; axis_derivation skipped.
- **Deficiencies:** missing_mediator, missing_variable(hs_crp), uncovered_cot_step.
- **Edits applied:** inject `hs_crp=MISSING` (T0); attach KB bridge (T0); make
  axis_derivation explicit (T0). (See `schemas/examples/deficiency_map_case01.json`.)
- **Outcome:** injections staged for Turn 2; corroboration = counterfactual + reread.

### Turn 2
- **Readout:** with `hs_crp=MISSING` injected, missing-data pull now fires (CRP mid-stage,
  moderate); inflammation mid/moderate; endothelial + atherosclerosis still faint;
  bacteremia absent; pathway_grouping now covered, axis_derivation still shallow.
- **Deficiencies:** missing_mediator (endothelial/atherosclerosis/bacteremia),
  uncovered_cot_step (axis_derivation shallow).
- **Edits applied:** KB bridge already active; reinforce axis_derivation step (T0).
- **Outcome:** `hs_crp` injection **confirmed** (absent→mid). Counterfactual flip
  (hs_crp present↔MISSING) moved the inflammatory axis, unrelated axes stayed put.

### Turn 3
- **Readout:** CRP, inflammation, endothelial, atherosclerosis all mid/strong;
  cardiovascular_risk strong; bacteremia still absent; axis_derivation covered — oral
  and systemic findings now related into the inflammatory + vascular axes.
- **Deficiencies:** missing_mediator (bacteremia only) — minor.
- **Edits applied:** none new; open a pending hypothesis for the oral-microbiome KB line.
- **Outcome:** KB bridge + axis_derivation step **confirmed**. Three beliefs consolidated;
  one hypothesis (bacteremia) carried forward. Ready for the evaluator on this converged
  input; all injections remain T0 until a T1 promotion is proposed + human-approved.
