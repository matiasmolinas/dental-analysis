# Stage 2 Roadmap — from a strong proposal to an outstanding submission

> A response to the external strategic review
> ([`external-review/…Hackathon_Review.md`](external-review/Mechanistic_Research_Agent_for_Oral-Systemic_Disease_Hackathon_Review.md)),
> which scored the project ~9/10 and asked us to **focus scope**, **make uncertainty and falsifiability
> the product**, and **reposition from disease *predictor* to scientific *research agent***. Stage 1
> (see [`ROADMAP.md`](ROADMAP.md)) built the engine; Stage 2 makes it *land* — one memorable demo, honest
> agentic-AI metrics, and statistical hardening.
>
> **Non-diagnostic remains the hard invariant.** Nothing here diagnoses or imputes a patient value.
>
> **➜ Executable version:** [`STAGE2-WORKPLAN.md`](STAGE2-WORKPLAN.md) — the task-level work plan with a
> full **coverage matrix** (every one of the 28 review points → a workstream), per-workstream checklists,
> acceptance criteria, the demo script, and the metric/statistics specs. Use that to *execute*; use this
> to understand *why*.
>
> *This plan was cross-checked with an independent review pass (a Fable-model agent). It converged on the
> same core finding — the gap to "outstanding" is ~70% framing/exhibition, ~30% code — and on the single
> substantive engineering item (NHANES survey weights). Its distinct contributions are folded in below.*

---

## 1. Honest triage of the review

The most important finding: **several review asks are already built — the risk is that we don't *show*
them.** We separate what needs *exhibiting* from what needs *building*.

| # | Review ask | Status | Stage-2 action |
|---|---|---|---|
| R1 | Reduce to ONE memorable end-to-end demo | **GAP** (engine exists, demo doesn't) | Build the narrated live demo (§3) — the centerpiece |
| R2 | Clear architecture diagram (Claude → tools → engine → validation → explanation) | **PARTIAL** (ASCII diagrams exist; no single polished visual) | One canonical diagram, reused in README/pitch/UI |
| R3 | Separate Claude's role from the math engine | **DONE** (agent = relational hypotheses; `histora.*` = deterministic math; `case_tools` is the boundary) | Make the split *visible* in the diagram + demo narration |
| R4 | Publish benchmark methodology + protocol | **PARTIAL** ([`BENCHMARK.md`](../BENCHMARK.md) has arms/metrics/honesty notes; the *formal* protocol — exact prompts, model version, seeds, how the live C arm's non-determinism is handled — is not yet pinned) | Formal reproduction protocol: verbatim prompts, model id, seed manifest, N-run variance for arm C |
| R5 | Calibration must NOT be presented as external validation | **PARTIAL** (docs say it, but the wording can still read as a "win") | Re-label everywhere: ε/k are *calibrated*; NHANES signs are the *validation* (§5) |
| R6 | Describe IL-6 as a latent/shared inflammatory **proxy**, not the unique mechanism | **PARTIAL** | Rename the shared variable to an *inflammatory proxy* in docs + code comments (§5) |
| R7 | Alzheimer's axis = exploratory research module | **PARTIAL** (flagged + GAIN caveat, but sits beside CV/metabolic as an equal) | Visually/structurally demote it to an "exploratory module" tier |
| R8 | Agentic-AI metrics (hallucination, citation accuracy, uncertainty calibration, consistency, falsifiability) | **GAP** (we have falsifiability + guardrail; not the rest) | Build `histora.agent_metrics` (§4) — high impact |
| R9 | Improve statistical treatment of NHANES | **GAP** (we use unweighted OLS; NHANES needs survey weights) | Add survey weights + sensitivity + multiplicity (§6) — credibility with scientists |
| R10 | External validation or sensitivity analyses | **PARTIAL** (LHS sensitivity in the ensemble; no second dataset) | Add a documented sensitivity suite now; name an external-cohort path (§7) |
| R11 | Polished visual interface | **PARTIAL** (one-page artifact + PDF exist; no interactive surface) | A single lightweight demo UI reusing the artifact design |
| R12 | "Why now? Why Anthropic + Gladstone?" | **GAP** | Two paragraphs, in README + pitch (§8) |
| R13 | Scientific roadmap: longitudinal, genetics, multimodal | **GAP** | A forward-looking section, honest about what today's data can't do (§7) |
| R14 | Position as research agent, not predictor | **PARTIAL** (true in substance; framing still leans "model") | The reframe threads through every doc + the demo (§2) |

**Takeaway:** ~half the review is *exhibition debt*, not *engineering debt*. Stage 2 spends most effort
on the three real gaps that move a judge: **the demo (R1)**, **agentic-AI metrics (R8)**, and
**statistical hardening (R9)** — plus cheap, high-leverage reframing (R5/R6/R7/R12/R14).

---

## 2. The reframe: a Scientific Research Agent, not a disease predictor

This is a positioning change, not a code change, and it should be visible in the first sentence of every
surface:

- **Claim we make:** *"HISTORA helps a researcher form and prioritize falsifiable oral–systemic
  hypotheses, with explicit mechanism and honest uncertainty."*
- **Claim we do NOT make:** *"HISTORA predicts whether a patient has / will get disease X."*
- **Consequence for metrics:** the headline is **coherence, calibration, uncertainty honesty,
  falsifiability, and citation integrity** — not accuracy/AUC. Our benchmark already measures the former;
  Stage 2 adds the agentic-AI half (§4). Predictive accuracy is deliberately *not* our leaderboard.

Every doc's opening line and the demo's first slide adopt this framing.

---

## 3. The centerpiece: one memorable end-to-end demo (R1)

**Thesis:** *one anonymized case goes in; a prioritized, mechanistically-explained, uncertainty-quantified,
falsifiable research brief comes out — and every number is traceable to either a calibrated equation or a
public-data association.* This is the whole product in ~3 minutes.

**The scope reframe (the punchline):** the review's #1 weakness is "scope too broad." The demo *inverts*
it. Three axes are not three models — they are **one shared inflammatory proxy that forks**. Narrated as
"the inflammatory-proxy walk," the breadth stops reading as dispersion and becomes the argument: *one
lever, three diseases, one engine.* We reduce the **narrative** to a single canonical path, not the
**capability** — deleting an axis would destroy the very thesis.

**The scripted flow (live, reproducible):**

1. **Input** — an integrated oral + systemic record (structural bands only; a missing mediator is shown
   as a *collection flag*, never filled). The UI shows the record and the guardrail badge.
2. **Claude (relational)** — narrates the candidate oral↔CV↔metabolic↔neuro couplings *as hypotheses*,
   each citing the exact input fields. Clearly labeled "Claude — reasoning," not "the model's answer."
3. **The engine (deterministic)** — `case_tools` runs the shared-proxy harness on the case's structural
   stratum: CRP / HbA1c / tau-α **as envelopes** (median + 90% band) with the sensitivity ranking, and
   the **counterfactual lever** ("periodontal therapy → predicted ΔCRP / ΔHbA1c"). Labeled "Engine — math."
4. **Validation** — side-by-side, the three **NHANES association signs** the engine predicts, with their
   bootstrap CIs — the *whether* — next to the engine's *why*. The calibration anchors are shown as
   **calibration**, explicitly not validation.
5. **Explanation + honesty** — the brief ends with: the ranked hypotheses, each with a **falsification
   condition**, the **agentic-AI metric card** (§4), and the standing caveats (GAIN trial; mediator not
   co-measured; small effects). One "print" button → the one-page PDF we already generate.

**Deliverable:** a `demo/` script + a thin UI (R11) that runs steps 1–5 on a fixed example with one
command, plus a recorded walkthrough. **Effort: M.** This single artifact answers R1, R2, R3, and R14 at
once.

---

## 4. Agentic-AI metrics — the biggest scoreable gap (R8)

A new module `histora.agent_metrics` + `run_agent_metrics.py`, extending the benchmark discipline
(pre-specified, seeded, reproducible). Each metric is defined so it can be *earned*, and we state plainly
which run offline vs. need live Claude.

| Metric | Definition | How measured | Runs |
|---|---|---|---|
| **Citation accuracy** | fraction of the agent's cited claims whose source exists in the model library / references and supports the claim | check each citation against `model-library.md` / `PAPER.md` reference keys; a claim with a dangling or mismatched cite fails | offline check of a live transcript |
| **Hallucination rate** | fraction of quantitative claims **not** traceable to (a) an engine output, (b) a cited source, or (c) a flagged hypothesis | parse the agent's output; every number must map to a harness field or a citation, else it's a hallucination | offline check of a live transcript |
| **Uncertainty calibration** | (a) *coverage:* do the ensemble's 90% bands contain the real interventional anchor (ΔCRP≈0.5, ΔHbA1c≈0.35) where one exists? (b) *honesty:* is ε flagged as the most-uncertain edge, consistent with the sensitivity ranking? | (a) empirical-coverage check of the envelopes; (b) reliability-style bucket of stated confidence vs. CI-excludes-0 | offline (uses stored anchors + NHANES) |
| **Consistency** | same case, N runs → how stable are the ranked hypotheses and the sign of each axis? | run the agent N times on a fixed case; report rank-stability and sign-flip rate | live Claude |
| **Falsifiability coverage** | fraction of hypothesis-level claims shipping a refutation condition | already in the benchmark (M7); surface it here too | offline |
| **Guardrail adherence** | non-diagnostic + no imputation + traceability | already enforced (`ab_eval.guardrail_pass`, W1) | offline / live probe |

**Why it moves the needle:** the review explicitly asks for these, and they are *exactly* the "safe,
transparent AI agent" story the judges want — and we can report them honestly because the engine gives
every number a home. **Effort: M.** Offline metrics ship first (deterministic); the live consistency run
is a small add.

> **Research-track extension (gated):** a *self-improving-harness* metric — the harness detects a
> recurring omission in its own traces and externalizes the fix, measured with the W1 guardrail metric
> and a prose-vs-enforcement control. See §11 (Behavioral Trace Diagnostics). It is upside, not a
> must-have, and runs only after the must-haves close.

---

## 5. Cheap, high-leverage honesty fixes (R5, R6, R7)

These are wording/structure changes with outsized credibility payoff:

- **R5 — calibration ≠ validation.** Audit every doc for phrasing that lets ε/k read as a "result."
  Standard line to adopt: *"ε and k are **calibrated** to interventional anchors (an input constraint);
  the **validation** is that the three association signs the engine predicts appear, confounder-adjusted,
  in NHANES."* Add a one-box "Calibration vs. Validation" callout to `PAPER.md` and the demo.
- **R6 — IL-6 as a latent inflammatory proxy.** Rename the shared variable in prose and code comments
  from "excess IL-6" to **"shared inflammatory proxy (operationalized as excess IL-6)."** IL-6 is the
  *measurable stand-in* for a latent systemic-inflammation factor (CRP, IL-1β, TNF-α co-move); Mendelian-
  randomization favoring IL-6/IL-1β as causal is the *justification for the proxy choice*, not a claim
  that IL-6 is the sole mechanism. One paragraph in `MODELS.md` + `SOLUTION.md`.
- **R7 — Alzheimer's as an exploratory module.** Introduce a tier label: CV + metabolic are
  *data-anchored axes*; **neuro is an "exploratory research module"** — same math rigor, but explicitly
  gated behind the GAIN-failure caveat and the mediator-not-co-measured gap, and visually set apart in the
  demo and README. This protects the whole project from being dismissed on the most speculative axis.

**Effort: S (all three).** Highest credibility-per-hour in the plan.

---

## 6. Statistical hardening of NHANES (R9)

The current analysis uses **unweighted** standardized OLS + bootstrap. NHANES has a **complex survey
design** (unequal selection probabilities, stratification, clustering); a scientist reviewer will expect:

1. **Survey weights** — use the exam weights (`WTMEC2YR`) with strata (`SDMVSTRA`) and PSU (`SDMVPSU`);
   report design-adjusted coefficients alongside the unweighted ones. If we implement a light Taylor-
   linearization/BRR in pure Python, keep it dependency-free; otherwise state the limitation explicitly.
2. **Multiplicity** — we test several outcomes; report which survive a Benjamini–Hochberg FDR control, so
   the 3/4-cognition result isn't read as cherry-picked.
3. **Sensitivity** — show the coefficient is stable across the exposure choice (CAL vs PPD, already
   partly done), across confounder sets, and across reasonable inclusion rules; a small table of "the
   result under 4 specifications."
4. **Effect-size honesty** — keep foregrounding that the effects are small and cross-sectional (already
   done well; don't lose it).

**Deliverable:** `histora.nhanes_survey` (weights/strata/PSU handling) + a sensitivity/multiplicity table
in `PAPER.md`. **Effort: M.** This is the single change that most raises scientific credibility.

---

## 7. Sensitivity now, external validation as a named path (R10, R13)

- **Now (in-repo):** a documented **global sensitivity** pass (we already have LHS + one-at-a-time
  elasticities in `ensemble.py`) promoted into `PAPER.md` as a figure/table, plus a Sobol-style total-
  order index if cheap. This satisfies "sensitivity analyses" honestly today.
- **Named external path (roadmap, not overclaimed):** the honest scientific extension —
  1. **Longitudinal cohorts** (e.g. ARIC, which has periodontal exams + incident CV/cognitive outcomes)
     to move from *association* to *temporal ordering* and to fit the flagged couplings (γ, β_tau, β_si).
  2. **Genetics** — APOE4 stratification on the neuro axis; Mendelian randomization (IL-6R variants) as a
     causal probe of the shared-proxy assumption.
  3. **Multimodal** — tau-PET (ADNI) to fit the connectome front directly; inflammatory panels to test the
     proxy's co-movement.

  State clearly: **none of this is claimed as done** — it is the falsification/validation program the
  agent is built to feed. **Effort: S (writing) for the roadmap; the cohort work is out of hackathon scope.**

---

## 8. "Why now / Why Anthropic + Gladstone" (R12)

Drop-in narrative for README + pitch:

> **Why now.** Three curves crossed. The oral–systemic inflammation literature has matured from
> association to candidate mechanism (IL-6/CRP kinetics, tau-spread models validated on tau-PET). Public
> data (NHANES) is rich enough to test directional predictions cheaply and reproducibly. And frontier
> models can now *orchestrate* a mechanistic pipeline — reason over evidence, call deterministic tools,
> and refuse to overstep — rather than act as opaque predictors. A safe, transparent research agent that
> stitches these together is newly possible.

> **Why Anthropic + Gladstone.** The project's spine is the pattern Anthropic cares about: an AI agent
> that is *useful because it is honest* — uncertainty, falsifiability, citation integrity, and a hard
> non-diagnostic guardrail as product features, not disclaimers. Its most exploratory axis is exactly
> Gladstone's terrain: neuroinflammation, the blood–brain interface, and tau propagation. HISTORA hands a
> Gladstone-adjacent lab a **novel upstream perturbation** (periodontal inflammation → tau-α) as a
> parameterized, falsifiable hypothesis to plug into existing tau/microglia/BBB models — with the
> intellectual honesty (including the failed GAIN trial) that a serious lab requires.

**Effort: S.**

---

## 9. Risks and traps — what NOT to do

- **Do not let calibration masquerade as validation** (R5). The single fastest way to lose a scientific
  judge. Police the wording relentlessly.
- **Do not present the Alzheimer's axis as a finding** (R7). It is an exploratory module behind a failed
  causal trial. Overclaiming here taints the credible CV/metabolic work.
- **Do not add a fourth axis or more models.** The review's #1 weakness is *scope*. Stage 2 adds **zero**
  new biological axes; it deepens and exhibits what exists.
- **Do not build a heavy UI.** One thin, honest demo surface reusing the existing artifact design — not a
  product. Effort spent on chrome is effort not spent on metrics/stats.
- **Do not report agentic metrics we can't reproduce.** Every metric ships with a seed/manifest and an
  offline check where possible; live-Claude metrics report their n and variance honestly (as the M6
  guardrail probe already does).
- **Do not let the research track (§11) become a Trojan horse for the removed lens/memory work, and do
  not persist patient-derived values into long-term memory.** The self-improvement layer must stay
  offline-reproducible over real traces, must be named honestly (behavioral, post-hoc — not "Jacobian
  lens"), and its consolidation step must persist only workflow patterns/templates — never a
  physiological magnitude — or it violates the non-diagnostic guardrail it is meant to strengthen.

---

## 10. Sequenced plan (impact ÷ effort first)

**Must-have for the pitch:**
1. **Reframe + honesty fixes** (§2, §5) — S — do first; unblocks everything's wording.
2. **Architecture diagram + Claude-vs-engine labor table** (R2, R3) — S — highest impact-per-hour; the first thing a judge looks at.
3. **The end-to-end demo, packaged** (§3, R1) — M — the memorable artifact; the scope reframe.
4. **Formal benchmark reproduction protocol** (R4) — M — turns the benchmark from a claim into a verifiable result.
5. **Agentic-AI metrics, offline** (§4) — M — the headline new evidence.
6. **NHANES statistical hardening** (§6) — M — scientific credibility (the one real engineering item).

**Strong nice-to-have:**
7. **Live consistency + hallucination metrics** (§4) — S — completes the agentic story with honest variance.
8. **Sensitivity figure promoted to the paper** (§7) — S.
9. **Why-now / Why-Anthropic-Gladstone + scientific roadmap** (§8, §7) — S — pitch polish.
10. **Thin demo UI** (§3/R11) — M — only after the must-haves.

**Research track (gated, zero budget until 1–6 close):**
- **Behavioral Trace Diagnostics** (§11) — the API-accessible analogue of the Jacobian-lens idea:
  self-improving-harness introspection over observable traces, with the W1-standard measured experiment
  and its control. A research-track sub-item of #5, reported honestly (including as a negative if the
  control ties). **Not** a must-have; never displaces the pitch.

**Definition of done for Stage 2:** a judge can watch one 3-minute demo that shows a case → Claude's
hypotheses → the engine's uncertainty-quantified mechanism → the NHANES validation → a falsifiable brief,
backed by a reproducible **agentic-AI metric card** and **design-adjusted NHANES statistics**, framed
throughout as a *safe scientific research agent*, not a predictor.

---

## 11. Research track (gated) — Behavioral Trace Diagnostics

> **Origin.** A hands-on experiment with the **Jacobian Lens** (J-Lens, Neuronpedia/Qwen) showed that
> reading a model's *internal workspace* alongside its output diagnoses **what a prompt is missing**
> better than reading the output alone — but does **not** catch execution errors (a bad multiplication);
> the winning loop is *lens (fix the input) + output verification*.
>
> **The hard constraint.** Claude's API does **not** expose the Jacobian lens, so this cannot be a
> production feature here. The question this track answers: *can we recover the diagnostic value from
> API-accessible **observable** signals instead — short-term session traces, long-term learned memory,
> per-session results, and the harness evolved during the session?*

**Why it is coherent (and why it is not a rerun of the removed lens work).** Stage-1 established the
boundary condition `I(L;Y|O,K_R)≈0`: the internal lens L was redundant with the observable output O plus
a competent reader's knowledge K_R. That result **argues for** this track — if the internal signal was
already recoverable from O+K_R, then the observable traces carry (almost) all of it. And traces have one
strict advantage over the internal lens: **they see the output**, so they can catch the execution errors
J-Lens missed. But the same result also carries the warning: the internal lens was cut for being
*insight without payoff*, and that risk **moves with us unchanged**. Recoverable ≠ actionable.

**Honest naming — do NOT call this "Jacobian lens."** It is a **different mechanism**: behavioral and
*post-hoc* (after the session), *correlational* (observation only, no STEER/ABLATE), over external
traces — not the causal, *during-computation* internal readout. The honest framing: *"inspired by the
J-Lens lesson (fixing the input beats fixing the token), implemented on observable traces because the
internal lens is inaccessible in production."* Overselling it as interpretability would cost credibility
across the whole project.

**Positioning: research-track, gated — not a new must-have.** The external review demanded *less* scope;
a self-improving-harness module is exactly the kind of shine to prune. It therefore has a **zero time
budget until the six must-haves are closed**, and it lives as a clearly-labelled **research-track
sub-item of must-have #5** (agentic-AI metrics) — because a measurable harness self-improvement *is* an
agentic metric. It never displaces the demo, the diagram, the protocol, or the survey weights.

**The one measurable experiment (held to the W1 standard — improvement, not insight).** W1 worked
because it *externalized a deterministic step the model knows but drops*, and **measured** it
(guardrail 0.00→1.00) with a **control** proving prose alone did not suffice. This track must repeat that
anatomy one level up (self-improvement instead of manual fix):

1. **Trace analyzed** — the deterministic S/C/H benchmark logs (they already exist; offline).
2. **Defect detected** — a recurring omission pattern (e.g. the execution-gap reappearing in a branch,
   or a branch that skips the non-diagnostic disclaimer / the survey-weights step). A consolidation pass
   (the llmunix `MemoryConsolidationAgent` pattern) extracts *"in context X, the harness drops step Y."*
3. **Harness change produced** — promote that pattern into an **externalized deterministic directive** in
   the sub-agent's long-term template (enforcement, not prose) — the session edits its own template.
4. **Metric that rises** — reuse a **validated** metric (the binary non-diagnostic guardrail, or an
   M1–M7 metric with a bootstrap CI). No new metric.
5. **Control (mandatory)** — give the template the same finding as descriptive **prose** vs. as an
   **externalized/enforced** directive. Only if externalization moves the metric is the W1 signature
   reproduced. **Kill criterion, pre-registered:** if prose ties externalization, or the delta needs
   Claude in the measurement loop (not offline-reproducible), it is insight-without-payoff again → it
   stays research-track and is reported as an honest negative (itself on-message for "research agent").

Offline: trace generation, consolidation, template edit, and the deterministic benchmark re-run
(old vs new template). Live-Claude (preview only, not the headline number): Claude *autonomously*
authoring the directive from the trace.

**Guardrail extension (a real, new trap).** Session traces over NHANES contain patient-like magnitudes
(CRP, the IL-6 proxy, ε). Consolidating to long-term memory must **never persist a physiological/patient-
derived value as a "learning"** — long-term memory may hold only **workflow patterns and agent templates**
(e.g. "apply survey weights in branch X"), never a derived individual magnitude. The structural
non-diagnostic guardrail must extend to the consolidation layer with a filter that refuses to persist any
physiological quantity. Skipping this would make the self-improvement module *violate* the very guardrail
that is the project's core differentiator. *(Reference implementation of the memory hierarchy:
`llmunix-marketplace/llmunix-plugin/system_files/SmartMemory.md` and `MemoryTraceManager.md`.)*

**Cross-checked with an independent Fable pass**, which converged on: coherent but risk-carrying;
rename away from "J-Lens"; research-track gated behind the must-haves; the W1-standard experiment with its
control and kill criterion; and the memory-consolidation guardrail extension above.

---

*This plan responds to the external review; it adds no new biological claims and preserves the
non-diagnostic invariant. Companion: [`ROADMAP.md`](ROADMAP.md) (Stage 1), [`PAPER.md`](../PAPER.md),
[`BENCHMARK.md`](../BENCHMARK.md).*
