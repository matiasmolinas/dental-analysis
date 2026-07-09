# Is the null result the SKILL or the MECHANISM? A diagnosis, and the optimizer reframe

> Produced 2026-07-09 with the **Fable** model. Scope: live Claude Sonnet-5. Grounded in
> `src/ablation.py`, `src/counterfactual.py`, `src/run_ablation.py`, `src/ab_eval.py`, the
> observer/probe prompts, and the result files (`results/ablation_v2.json` n=6,
> `results/counterfactual_report.json` n=4, `results/counterfactual_evolved.json` n=4).
> Inferred lens = self-report only, Claude grading Claude. No cheerleading. References:
> Anthropic "A global workspace in language models" (J-lens, Jul 2026); Sakana AI
> **TRINITY** and **Conductor** (ICLR 2026).

## 0. The numbers this rests on

**Three-arm ablation** (`ablation_v2.json`, n=6 NHANES, 8 mediators):

| arm | mechanism_recall | relational_recall | guardrail_pass_rate |
|---|---|---|---|
| A (naive) | 0.625 | 0.542 | 0.00 |
| B_blind (converge, no lens) | 0.938 | 0.833 | 0.00 |
| B_lens (converge, lens+defmap) | 0.958 | 0.938 | 0.00 |

- **A → B_blind** (blind convergence): mechanism **+0.313**, relational **+0.292**.
- **B_blind → B_lens** (the lens's *marginal* contribution): mechanism **+0.021** (90% CI
  [-0.042, +0.083]); relational **+0.104** (90% CI [-0.042, +0.229]). Both CIs straddle 0
  → **`lens_inconclusive`**.

**Counterfactual sensitivity** (12 flips each): A_naive 0.00; B_converged 0.00
(mean_affected_delta −0.25/−0.33); **B_evolved +0.33** (factor-grounding instruction on the
executor's `extra_system`, `run_counterfactual.py:31`) — the one intervention that flipped
the sign, found by reading the **output** metric, bypassing the lens pipeline entirely.

---

## 1. Diagnosis: (a) skill vs (b) mechanism

**Verdict: mostly (b), the mechanism. ~70% mechanism / ~30% skill — and the 30% is
currently *gated* by the mechanism, so its realized independent contribution is ~0.**

**Why the skill (a) is NOT the binding constraint.** (i) Self-report *dodges* the measured
lens's headline limit — the J-lens "can only identify single-token concepts," but our
mediators are multi-token ("endothelial dysfunction," "C-reactive protein"); verbal report
names them, the instrument can't. On the exact concepts this task needs, self-report is
arguably *richer* than the tool it approximates. (ii) The paper validates the channel
(self-report is causally coupled to reasoning). If (a) bound, B_lens would move the number
erratically; instead B_lens ≈ B_blind almost exactly (+0.021) — the signature of a signal
the mechanism does nothing with, not of a noisy signal.

**Why the mechanism (b) binds.** (i) The blind converger already recovers the lens's
information: B_blind reaches 0.94 relational recall re-deriving "hs-CRP absent, endothelial
faint, axis-derivation skipped" from the record — the readout is **redundant with the
converger's competence** (the Trinity/Conductor finding: a strong model matches the
hand-designed scaffold). (ii) A *fixed-prompt* `converge_fn` caps the lens's payoff at
"how much the output changes when the readout is present vs absent" ≈ 0 — **the mechanism
bounds the lens's marginal value near zero regardless of signal quality**; even a *measured*
lens through this same text-in-text-out converger would likely show the same redundancy.
(iii) The only win (+0.33) was a mechanism-level intervention (shape the executor's
reasoning directly) found via the output metric, **outside** `readout_fn→observer_fn→
converge_fn`.

**The 30% left on (a):** we have not tested a *good* use of the lens; the localization
("axis-derivation skipped") is the kind of thing an output grade doesn't give. But that
residual is unproven and unreachable through the current actuator. **The null is a
mechanism failure wearing a signal costume: a good detector wired to an actuator a blind
model renders unnecessary.**

---

## 2. Why the mechanism is the bigger lever — through Trinity / Conductor

| Our component | What it is | Trinity/Conductor analog |
|---|---|---|
| `readout_fn` | executor self-report → ranked concepts | verbalized projection of internal state — **lossy vs a hidden-state representation** |
| `observer_fn` | fixed-prompt deficiency map | **hand-designed routing** (a human wrote the deficiency→surface table) |
| `converge_fn` | fixed-prompt input rewriter | **hand-designed scaffold** — the exact thing a strong model matches blind |
| state→edit map | authored English in three `.md` files | **learned** (sep-CMA-ES / GRPO) |

Two structural mismatches: **(1) signal form** — Trinity's tiny head consumes the SLM's
**penultimate-token hidden state** (a rich vector, linearly separable by task); we consume
the model's *English caption* of its state (lossy, single-token-biased). We kept the
caption, threw away the representation. **(2) the map is fixed, not learned** — Trinity
learns state→route with sep-CMA-ES (and shows RL/REINFORCE *fails* here: low-SNR terminal
binary rewards, weak parameter coupling); Conductor learns state→workflow with GRPO. Both
papers' headline: **learned coordination beats hand-designed routing/scaffolds** — and
B_blind is the empirical proof a strong model already matches our scaffold.

---

## 3. The full optimization state (the reframe, made concrete)

The workspace readout is **one input parameter among many** to an optimizer that emits
gap-detection *as a byproduct of choosing the best edit*. The lens is row 11 of 11.

| # | State parameter | Gap signal it carries | How the optimizer consumes it |
|---|---|---|---|
| 1 | **Objective** (metric defs) | is the target right? (recall was name-echo) | reward/gate spec; flag objective drift |
| 2 | **Problem framing** (`spec_text`) | under-specification | reference to score other features against |
| 3 | **Inputs (record)** | missing fields, ambiguous encodings | raw substrate |
| 4 | **Data completeness/quality/selection** (`missing_mediators`) | which mediating data truly absent — **deterministic, high-value** | drives the missing-data flag (the axis that works) |
| 5 | **Injected params** (`derived_signals`) | did a computed signal move an output axis? | per-signal counterfactual flip; prune dead signals |
| 6 | **Skill contents** | a reasoning step never made explicit | candidate edit surface |
| 7 | **Sub-agent defs** | a role/step assigned to no one | candidate edit surface |
| 8 | **Prompt instructions** | the best lever found (factor-grounding) | candidate edit surface + **seed policy** |
| 9 | **Thinking trace** (currently discarded) | which steps traversed vs skipped — behavioral CoT coverage | parse for step-coverage (richer than the self-report caption) |
| 10 | **Output + behavioral grade** | relational_recall, sensitivity, guardrail | **primary reward** — the current observer never sees it |
| 11 | **Lens readout** | a *localizer*: which concept/step was faint/absent | **one feature**, corroborated by row 10, never the sole driver |

The architecture's miss: rows **9 and 10** are strictly richer gap signals than row 11, yet
the observer consumes *only* row 11.

---

## 4. Concrete architecture for THIS project

**v1 — Conductor-lite, hand-prompted, feasible now (~free).** One "Optimizer" instance
(Opus) replacing `readout→observer→converge` with a single holistic call:
- **Input:** structured state `{objective, spec, record, missing_mediators, injected_signals,
  current skill/agent/prompt text, executor thinking-trace excerpt, executor OUTPUT, output
  scores (relational_recall + counterfactual delta), lens_readout}` — rows 4/9/10 are the
  new material; the lens is one field.
- **Output:** `{gap_detection, proposed_edits:[{surface, change, rationale, corroboration}],
  predicted_metric_move}` (same `deficiency_map_schema.json` shape) — rationale must cite the
  **output grade + counterfactual delta**, not just the readout (kills the anti-Goodhart hole).
- **Why it beats today's observer even hand-prompted:** it *sees the behavioral metric and
  the trace*, so it proposes the factor-grounding edit for the reason it works (sensitivity
  was 0), instead of chasing a faint mediator the readout named. Cost: one call/case, no training.

**v2 — learned optimizer (expensive).** Trinity-style: encode the state with a small SLM,
read its **hidden state** (and, if the API exposes it, the *measured* lens as an activation
feature), train a ~10K-param head with **sep-CMA-ES** to emit {surface, edit template} over
turns — the low-SNR terminal reward here is exactly the regime where the paper shows
**CMA-ES works and RL fails**, so do *not* reach for GRPO first. Conductor-style (if reward
densified): a 7B optimizer GRPO-trained to output the edit workflow, reward = held-out
`relational_recall` + `sensitivity_rate`, **guardrail pass-rate a hard constraint** (edit
that lowers it scores −∞). Optimize the honest pair, never `mechanism_recall` (name-echo).

**Seed: factor-grounding = crude counterfactual-reflection training.** The paper's result —
training the model on *what it would say if asked to reflect* reshaped its reasoning — is
exactly what our factor-grounding instruction did (sign-flip −0.25→+0.33). So v1 gets it as
a worked high-value example; v2's initial policy is "inject factor-grounding reflection
instructions," and the counterfactual-sensitivity reward *is* a scalable, automatable form
of the counterfactual-reflection objective — the most defensible bridge from our one real
result to the literature.

---

## 5. The experiment that settles (a) vs (b)

Five arms, same held-out cases (**n ≥ 30** real NHANES, bootstrap CIs in `ablation.py`),
one neutral evaluator:

| arm | optimizer sees | isolates |
|---|---|---|
| 0. blind | nothing (record only) | competence floor |
| 1. observer (current) | `readout→observer→converge` | today's hand-designed mechanism |
| 2. optimizer-lens-only | v1, state = lens readout only | can the lens carry it alone? |
| 3. optimizer-full-minus-lens | v1, full state EXCEPT the lens | mechanism value *without* lens |
| 4. optimizer-full | v1, full state INCLUDING lens | full system |

**Metric:** `relational_recall` AND counterfactual `sensitivity_rate` / `mean_affected_delta`
(recall alone discredited); guardrail pass-rate a hard gate.

- **Lens marginal value = (4) − (3).** ≈0 with CI through 0 → **(a) adds nothing even inside
  a good optimizer**; a measured lens unlikely to change it through this class of use.
- **Mechanism value = (3) − (1).** Full-state optimizer *without* the lens beating today's
  observer → **(b) was the binding constraint** (richer state + better actuator = the lever).
- **(2) vs (3)** = how much power is lens vs everything-else (the "one feature" test).
- **(4) vs (0)** = the honest end-to-end "did any of this beat blind."

**Predicted (for falsification):** (3) ≈ (4) > (1) ≥ (0) — the lens is a near-zero-marginal
feature, the full-state optimizer beats both the observer and blind. If instead (4) ≫ (3),
the lens carries real marginal information — the first genuine evidence for it as an
*improver*, worth running because it can come out either way.

---

## 6. Bottom line

The inferred lens didn't fail because self-report is too weak (it dodges the single-token
limit; the paper validates the channel). It failed because we **wired a detector to a
hand-designed actuator a blind strong model already renders redundant** — the exact
hand-designed-routing regime Trinity/Conductor beat with *learned* coordination over a
*representation*. The whole gain is A→B_blind (+0.29–0.31); the lens's marginal is
+0.02–0.10 with CIs through 0; the one thing that moved reasoning (+0.33) bypassed the lens
pipeline and was found in the *output*. ~70/30 mechanism/skill, the 30% gated to ~0. The
reframe is right: feed the **full eleven-parameter state** — thinking trace and output grade
included, lens as one feature — to a holistic optimizer; ship hand-prompted Conductor-lite
v1 now, learn the map (sep-CMA-ES, not RL) in v2, seed both with factor-grounding.
