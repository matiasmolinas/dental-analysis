# Research-Methodology Retrospective — dental-analysis (HISTORA / inferred-lens arc)

> Produced 2026-07-09 (Fable model). Meta-analysis of the research *strategy*, not clinical content.
> Every claim is cited to a doc + metric. The settled verdict ([`RESEARCH_SUMMARY.md`](RESEARCH_SUMMARY.md)
> §0): *"real, non-redundant signal; no demonstrated payoff."* This retrospective categorizes which
> components earned their place and drove the repo restructure (see the ARCHIVE index at
> [`analysis/ARCHIVE/README.md`](analysis/ARCHIVE/README.md)).

## Part 1 — Categorization

### WORKING (clear, substantial — the deterministic engineering, NOT the lens)

- **W1. The deterministic missing-data directive → guardrail reliability.** `missing_data_flagged
  0.00 → 1.00`, `guardrail_pass 0.00 → 1.00 (6/6)` on real NHANES. The single clean, repeated win —
  and it came from the hardcoded data-completeness directive in `ab_eval.build_inputs`, **not** the
  lens (free-form convergers handed the *same* directive fell back to 0.00). Source:
  `src/relational_signals.py` (`required_missing_data_entries()`), `src/ab_eval.py`.
- **W2. The guardrail-protected non-diagnostic invariant.** Never evolved, part of every gate, and
  enforced at *write time* where it could have leaked cross-patient: `lever_ledger.validate_lever`
  rejects any numeric patient value. Held across every experiment. A real safety property.
- **W3. The honest experimental apparatus as reusable tooling.** The bootstrap-CI ablation
  (`src/ablation.py`), the model-agnostic A/B scorer + promotion gate (`src/ab_eval.py`), the
  counterfactual-sensitivity runner (`src/counterfactual.py`). This is what produced
  `lens_inconclusive` instead of a false positive (the significance-aware rule prevents
  `lens_adds_value` firing on sub-noise deltas). 35 tests green. Domain-general; outlives the dental
  instance.

**The lens is NOT in this list.** Across self-report, Qwen-proxy, and Fable/Opus-prediction, no form
of the workspace signal was shown to improve outcomes over a strong blind baseline through any
actuator built here.

### UNCLEAR (tried; inconclusive — documented as "tried, no demonstrated payoff at power")

| Component | The one number | Documented as |
|---|---|---|
| Inferred lens as optimization signal | B_lens−B_blind relational **+0.104, 90% CI [−0.042,+0.229]**; `lens_inconclusive`, n=6 | non-redundant in principle but CI straddles 0 — failed to *reject* H₀, not evidence of no value; the gain was blind convergence |
| Observer loop's lens-driven value | B_lens ≈ B_blind (+0.02–0.10, CIs through 0) | loop works as software; lens-driven contribution unproven (~70% mechanism / 30% skill, the 30% gated to ~0) |
| SWC (session working-consciousness) | live once: turn1→turn2 relational_recall **0.50 → 0.625 (+0.125)**, n=1 | one mechanistic demo; not a value claim (n=1) |
| Cross-session memory (lever_ledger) | built + 4 tests + one guardrail-validated live write | persistence + write-time guardrail demonstrated (W2); cross-session transfer *value* untested |
| Targeted (selective) injection | relational_recall **0.62 targeted vs 0.50 base/append_all** (twice); counterfactual +0.33→0.00; n=1 | least-weak actuator-side positive; directional only |
| Factor-grounding instruction | counterfactual mean_affected_delta **−0.25 → +0.33** once; `sensitivity_rate` stayed 0.00 | one directional win, found via the *output* metric, bypassing the lens; not selective; n=4 |

### FAILED (clearly did not work)

- **F1. Append-all checklist grounding — actively hurt.** counterfactual `mean_affected_delta`
  **+0.33 → −0.33 (Δ −0.67)**, relational_recall **0.625 → 0.500**. The crude actuator dilutes the
  core reasoning. Non-redundant did not become useful.
- **F2. Isolating a *specific* planted gap — intermittent.** The amlodipine plant never cleared the
  0.6 stability bar across 5 runs, for *either* Sonnet or Opus predictors. The gate cannot be trusted
  to catch a particular gap.
- **F3. (Historical/retracted) v1 circularity + v1 `lens_adds_value`.** Both harness artifacts
  (exact-key clustering + Fable refusal collapsing diversity; a sub-0.1 delta with no significance
  test). Retained in the trail as the honest record of what was walked back.

### SPECULATIVE / EXTERNAL (not ours to run — not presented as results)

- **Measured-lens API feature** — Anthropic's to expose; documented consumer seam only
  ([`API_FEATURE_REQUEST.md`](API_FEATURE_REQUEST.md)). The strongest *forward* claim, not a finding.
- **Learned coordinator (Trinity/Conductor, sep-CMA-ES)** — `src/coordinator.py` converges on a
  *mock* objective; live fitness never run.
- **Qwen measured-lens probe** — `probes/qwen_correlation_probe.py`, GPU/jlens-gated, never run; and
  the single-token lens is *blinder* than self-report on multi-token mediators.

## Part 2 — Restructure (executed on this branch)

**Restated thesis.** This project built and ran an **honest, tested apparatus** for asking whether
reading a model's internal workspace helps optimize its inputs. The apparatus produced a **rigorous
negative-with-nuance**: the workspace signal is genuinely **non-redundant with the output** (it
surfaces content off the output plane, including a meta-critique of the output's own reasoning the
output cannot self-report), but **no actuator we built converts it into an outcome gain over a strong
blind baseline** on this largely re-derivable task. The one clean, repeated win — reliable
missing-data flagging (0.00→1.00) — belongs to a **deterministic directive**, not the lens. So the
project is: a validated apparatus + a demonstrated non-redundant signal without demonstrated payoff +
a concrete, evidence-motivated **API-feature ask** for which this repo is the consumer built and waiting.

**README headline:** *"An honest apparatus and a rigorous negative: the workspace signal is
non-redundant but not yet useful through inferred access — here is the tooling, the evidence, and the
measured-lens feature that would settle it."*

**Dispositions applied:** REWRITE README + APPROACH §8 + HACKATHON pitch (lead with W1–W3, demote the
loop to tested-inconclusive); KEEP RESEARCH_SUMMARY / API_FEATURE_REQUEST / AB_PROTOCOL / DATASETS;
DEMOTE REFORMULATION + PLAN + IMPACT to historical/hypothesis status with closure banners; ARCHIVE all
11 analyses under `docs/analysis/ARCHIVE/`; LABEL the experimental/scaffold `src` runners with a
one-line header and keep the core apparatus/harness modules unlabeled. No code deleted.
