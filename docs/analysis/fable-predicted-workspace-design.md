# Fable predicting Opus's workspace: circularity verdict and a falsifiable design

> Produced 2026-07-09 with the **Fable** model. Evaluates + designs the project lead's proposal to
> use Fable as an external predictor/simulator of Opus's J-space. Grounded in
> [`lens-non-redundancy-burden-of-proof.md`](lens-non-redundancy-burden-of-proof.md)
> (`I(feature;target|I,O)`, the three motivos, the corrected §5 program),
> [`measured-qwen-lens-contradiction-and-colab.md`](measured-qwen-lens-contradiction-and-colab.md)
> (Qwen rejected: transfer gap + single-token), [`skill-vs-mechanism-optimizer-reframe.md`](skill-vs-mechanism-optimizer-reframe.md)
> (mechanism bottleneck, actuator DOF), `skills/claude-workspace-probe.md`, `src/ab_eval.py`,
> `src/counterfactual.py`, and the J-lens paper. §2 is a genuine make-or-break gate the proposal can fail.

## 1. The epistemic ladder — where this sits

| # | Mode | Access to Opus's activations | Committed to Opus's output? | Transfer gap | Single-token | Status |
|---|---|---|---|---|---|---|
| 1 | Measured lens on Opus | Direct, causal | n/a | none | none | **Doesn't exist** — the ground truth we lack |
| 2 | Opus **self-report** (`claude-workspace-probe`) | **Privileged** (own activations) | **Yes** — can rationalize post-output | none | none | Exists; uncorroborated |
| 3 | Measured lens on **Qwen** | Direct on the *proxy* | No | **Large** | **Yes** | Rejected for optimization |
| 4 | **Fable predicting Opus's workspace** | **None** (external inference) | **No** (uncommitted) | none | none | **The proposal** |

Mode 4 vs Mode 2, honest: it **loses privileged access** (Fable can't see Opus's activations — one more
inferential step from ground truth than self-report; never a measurement) but **gains an uncommitted
perspective** (never produced Opus's output, so no post-hoc rationalization pressure). **Net-positive
*only* for GAP-DETECTION:** faithful reconstruction of what *was* in the workspace needs privileged access
(Mode 2 wins); finding what a competent workspace *should* have held and the output *didn't* surface needs
an **uncommitted normative "should"** — and the non-redundant content (considered-but-dropped,
silently-noticed, missing-variable) is exactly what Mode 2 is most pressured to under-report (admitting "I
should have considered X and didn't" argues against its own output). Fable pays no such tax. Still a
hypothesis, not a result — it depends on §2.

## 2. The circularity verdict — the make-or-break

**Trap:** if Fable predicts the workspace by *re-solving* the problem, its prediction is a function of
`{Input, problem}` → **zero new bits** vs a strong blind converger (which already hits 0.94 relational
recall re-deriving the mediators). A Fable-that-re-solves is a second B_blind in a workspace costume →
straight back to `lens_inconclusive`.

**The one thing that makes it non-circular:** Fable must predict the **delta** — the residual between
*what a competent solver would hold in mind* and *what Opus's output actually said* (non-verbalized /
considered-but-dropped / silently-noticed), **conditioned on Opus's output+trace**, explicitly NOT
re-deriving the answer. Forces: (a) Fable is *given* Opus's output+trace and models only what is *absent*
from them; (b) each predicted item carries `appears_in_output: yes/no`, only `no` items are candidate signal.

**The empirical gate (decides it, not a formality).** Let `P` = Fable's stable `no`-flagged items,
`O` = items in Opus's output, `C` = items a **blind converger** surfaces. Compute the non-redundant
surface **`P \ (O ∪ C)`**:
- **Empty** → `I(P;target|I,O) ≈ 0` by construction → **collapsed to circular. Stop, write the negative.**
- **Non-empty AND addressing those items moves counterfactual sensitivity** → non-redundant,
  behaviorally-load-bearing → escaped the trap. (`C` is the per-item "is this gap non-obvious?" oracle —
  the direct analog of burden-of-proof §5(a).)

**Honest prior:** Fable and the blind converger are both strong Claude-family solvers; on re-derivable
gaps both find it (→ empty), on genuinely non-obvious gaps both may miss it (→ empty). Fable's *only*
structural edge is the **framing** (uncommitted delta-model vs committed re-solver). Whether that yields
bits in `P \ (O ∪ C)` **cannot be assumed**. Verdict: **non-circular in principle, conditional on the gate;
build it to make the gate cheap and falsifiable; it may genuinely fail.**

## 3. Concrete design — the Fable workspace-predictor

Claude-only, no GPU (Opus executes, Fable predicts). **Distinct from the self-report probe:** that is
Opus introspecting itself (Mode 2, privileged); this is Fable modeling Opus (Mode 4, external). Same
target, opposite access — and where they *disagree* is itself a signal (self-report says salient; external
says should-have-been-but-output-shows-it-wasn't → candidate rationalization).

**(a) Prompt contract.** Inputs: `{objective (metrics + guardrail), record, executor input format,
executor OUTPUT, thinking-trace excerpt}` — output+trace **required** for the delta framing (without them
Fable is a solver). Instruction: "You model what Opus's workspace SHOULD have contained per the J-lens
precepts; you do NOT have activation access (inference, not measurement); do NOT re-solve; report only
content ABSENT from the output/trace." Output = predicted-J-space items on the paper's channels:

| channel | paper analog | captures |
|---|---|---|
| `silent-assessment` | `fake`/`fictional` on a staged scene | a judgment formed but not stated |
| `considered-but-dropped` | a dropped reasoning branch | a mediator/axis weighed and discarded |
| `intermediate-step` | intermediate reasoning | a sub-conclusion not surfaced verbatim |
| `error/anomaly-noticed` | `ERROR` on an unflagged bug | a record inconsistency a competent workspace catches |
| `missing-variable` | omission/injection detection | a mediating datum whose absence should register |

Each item: `channel`, `concept` (named directly — multi-token OK, dodging the single-token limit),
`salience`, and `appears_in_output: yes/no` (only `no` = candidate signal).

**(b) Variability protocol.** No privileged access → any single prediction is a draw from a belief
distribution. Sample `K≈5–7`, cluster synonyms, compute **stability = fraction of runs a concept appears
in** (confidence proxy). Report the distribution `{concept, channel, mean_salience, stability,
appears_in_output_rate}`; keep stability ≥0.6 AND `appears_in_output=no`. Low stability is a first-class
output (§5): where the simulation is uncertain, a real readout pays most.

**(c) Feed the joint optimizer as a privileged, DRIVING feature.** Stable `no`-flagged items become edit
drivers (missing-variable → collection flag; considered-but-dropped → ground the mediator; error-noticed →
record-consistency prompt) — the drop of the "never sole driver" rule that §5 says forbids the
non-redundant win, because the driver is *by construction* absent from the output. Gate is **behavioral,
downstream**: an edit is kept only if it raises `relational_recall`/`counterfactual sensitivity` on
held-out cases. Lens drives *proposal*; behavior authorizes *retention* (the "free actuator" §5(b)(ii) demands).

## 4. Validation and the honest label

**Test:** burden-of-proof §5 with the predictor as driving feature — **non-obvious-gap task** (planted
subtle omissions; confirm non-obviousness by running the blind converger first, `relational_recall` on the
planted item ≈ 0 — this is also `C`); metric `relational_recall` + counterfactual `sensitivity_rate` +
`mean_affected_delta`; `marginal(predictor) = (optimizer-full-with) − (optimizer-full-without)` at
**n≥30** with bootstrap CIs, separate evaluator. CI excludes 0 above → burden paid (first genuine
external non-redundant gap-driver); straddles/below on a non-obvious task with a free actuator → the
justified negative.

**Labeling (non-negotiable, stricter than the self-report probe):** (1) always "Fable's PREDICTION of
what Opus's workspace should contain," never "the workspace"; (2) never a measurement (stability is
belief-frequency, not a confidence readout); (3) every downstream claim gated on behavioral corroboration
(unretained predictions discarded, not reported); (4) never evidence about Opus's actual internals.

## 5. The "value of the real lens" deliverable

The simulation is a **lower bound on the real lens's value + a heat-map of where it concentrates:**
- **Where it helps** (`P \ (O ∪ C)` non-empty, edits move sensitivity), the **real measured lens on Opus
  helps strictly more and more reliably** (privileged causal access — reports what Opus *actually*
  represented, no inference gap / rationalization / sample variance). Every simulation win is a real-lens
  win with uncertainty removed → a *floor* achieved with zero activation access.
- **Where it is uncertain** (low stability, high `appears_in_output` variance, disagreement with the
  self-report probe) is **exactly where a real readout removes uncertainty → highest information value.**
  The variance map is a concrete pointer to the operations where a real J-lens API is decisive, not marginal.

Honest hackathon framing: *not "we measured the workspace" — "we built the consumer for a workspace
signal, showed where it moves behavior on Claude today with no GPU, and quantified where a real readout
would beat our inference."* A rigorous argument *for* the API feature precisely because it is careful about
what the simulation is not.

## 6. Recommendation: SCOPED-GO

Not full GO (non-circular only conditional on the §2 gate; honest prior is `P \ (O ∪ C)` may be empty —
both are strong Claude-family solvers). Not NO-GO (cheap, Claude-only; the *only* mode supplying an
uncommitted external gap-model; slots into the corrected §5 optimizer as the driving feature; doubles as
the value-of-the-real-lens argument regardless of the marginal's sign).

**Smallest first experiment (the gate, one case, decides scaling):**
1. One planted **non-obvious-gap** case (a subtle omission a blind converger provably misses).
2. Run the **blind converger** → `C`. Run **Opus executor** → output+trace, `O`.
3. Run the **Fable predictor**, K=5, delta framing, over {objective, record, Opus input, output, trace} → `P`.
4. Compute `P \ (O ∪ C)`. **Empty → circular, NO-GO on scaling, write the honest negative.** Non-empty →
   ground those items into the executor input, measure the change in `counterfactual sensitivity` on that case.
5. Only if step 4 is non-empty AND sensitivity moves → the n≥30 §4 validation.

One case, one afternoon, can come out either way — the mark of a test worth running.
