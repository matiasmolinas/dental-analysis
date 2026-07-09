# Where This Generates Large Impact — a priori

> **The particular case for the method.** [`APPROACH.md`](APPROACH.md) describes *what*
> the inferred-lens Observer + Session Working-Consciousness architecture is. This
> document answers *when it is worth it* — which problem characteristics predict a
> large gain **before you build**, the mechanism behind each, the archetypes where the
> payoff is biggest, where it is not, and a rubric to score a candidate problem.

---

## 1. The question

Any architecture this involved must earn its complexity. A plain agent (prompt →
answer, maybe a retry) is the right default for most tasks. The approach pays off only
when the **failure mode is representational** — the system gets things wrong not for
lack of a bigger model but because *the input never made the right thing representable*,
and you cannot see that from the answer alone. The lens exposes exactly that failure
mode, so the impact is large precisely where that failure mode dominates.

---

## 2. A-priori predictors of high impact

Score a candidate problem against these. The more that hold, the larger the expected
gain.

| # | Predictor | Why it predicts impact |
|---|---|---|
| P1 | **Hidden mediators / bridging concepts** — the answer depends on links that appear in *no single input field* | This is the lens's home turf: it measures whether those links got represented. Grading the answer can't localize their absence. |
| P2 | **Fragmented / multi-source input** — data arrives siloed, in different shapes | The dominant failure is a format/normalization one the lens catches (variable never registered), and the harness seam fixes deterministically. |
| P3 | **Missing-variable sensitivity** — outcomes hinge on whether a specific datum is present/collected | The lens's "missing-data pull" signal directly targets this; the system flags collection needs instead of silently guessing. |
| P4 | **Deterministic sub-relations mixed into a reasoning task** — thresholds, ratios, deltas, categorizations the model tends to approximate | The prompt-vs-code boundary moves these into tested harness code and injects the exact value — a reliability jump code gives and prompting doesn't. |
| P5 | **Long / multi-turn / repeated sessions on the same problem family** | The Session Working-Consciousness compounds: lessons consolidate across turns, so later turns start from what earlier turns learned. |
| P6 | **High-stakes, guardrailed domain** — safety/compliance invariants that must hold | The protected gate + tiered evolution let the system self-improve *without* risking the invariant — impact you cannot get from unconstrained self-modification. |
| P7 | **Input format / context is the real lever** (not raw model capability) | If a stronger model alone would fix it, buy the model. If *how you present the data* is the lever, the Observer optimizes exactly that. |
| P8 | **You can name the target concepts / variables / steps** (a checkable spec) | The Observer needs a spec to score deficiencies against. A nameable spec = an actionable lens. |

**Rule of thumb:** ≥4 of P1–P8, with P1 or P2 among them, predicts a large gain.
P1+P2+P3 together is the sweet spot.

---

## 3. Mechanism → problem-class map

Each predictor is large because a specific mechanism of the approach bites:

- **Lens localizes representational failure (P1, P7).** You learn *which* mediator is
  absent under *which* format, not merely that the answer was wrong — so the fix is a
  targeted input edit, not blind prompt-fiddling.
- **Missing-data pull, not silent guess (P3).** A required-but-absent variable surfaces
  as a collection flag; the system never imputes it. In domains where a wrong guess is
  worse than a flagged gap, this is the whole game.
- **Deterministic offload (P4).** Moving a threshold/ratio/delta into tested code
  removes a class of stochastic errors entirely and makes the value auditable — then
  re-injects it so the lens can confirm it now registers.
- **Cross-turn consolidation (P5).** The working-consciousness ledger turns a sequence
  of independent turns into a learning curve; the marginal turn is cheaper and better.
- **Safe self-improvement (P6).** Tiered T0/T1 + a protected gate means the system can
  adapt live and promote durable wins without ever putting the invariant at risk.

---

## 4. High-impact archetypes

Concrete problem shapes where the payoff is largest:

- **Cross-domain relational analysis over siloed records** — link data across domains
  whose connection runs through unstated mediators (the dental oral-systemic case:
  perio ↔ cardiovascular via inflammation/CRP/endothelial). P1+P2+P3+P6.
- **Evidence-traceable research/analyst agents** — outputs must cite the exact input
  fields and flag what is missing; hallucinated bridges are unacceptable. P1+P3+P6+P8.
- **Data-integration pipelines with semantic gaps** — normalization plus "does the
  model actually *use* this field," where dropped/renamed fields silently degrade
  results. P2+P4+P7.
- **Iterative optimization / research loops** — the same problem family attacked over
  many sessions, where compounding session memory matters. P5+P7.
- **Regulated / clinical / financial reasoning** — a hard invariant plus a real need to
  improve; unconstrained self-modification is off the table. P6 + others.

---

## 5. Where impact is small (anti-patterns)

Be honest about these — using the approach here adds cost without return:

- **Single-hop factual or lookup tasks** — no hidden mediators; the answer *is* the
  signal. (Fails P1.)
- **Clean, single-source, well-specified input** — nothing for the format/normalization
  machinery to fix. (Fails P2/P3.)
- **Capability-bound tasks** — the model simply isn't strong enough; a better model, not
  a better input, is the lever. (Fails P7.)
- **One-shot, no-repeat tasks** — the Session Working-Consciousness never gets to
  compound. (Fails P5; the Observer can still help once, but the ledger's value is lost.)
- **No nameable spec** — if you cannot state the target concepts/variables/steps, the
  Observer has nothing to score deficiencies against. (Fails P8.)
- **Purely deterministic problems** — if there is no genuine reasoning, skip the agents
  and just write the harness code.

---

## 6. A-priori impact rubric

Score each predictor 0/1/2 (absent / partial / strong). Interpret the total (max 16):

- **11–16** — large impact expected; the approach is likely the right architecture.
- **6–10** — moderate; adopt selectively — often just the lens + harness seam, deferring
  the full online loop.
- **0–5** — low; a plain agent (+ retry, + RAG) is the better default.

Weight P1 and P2 double if you want a single tie-breaker: representational failure over
fragmented input is the core condition the method is built for.

---

## 7. Worked example — the dental oral-systemic instance

| Predictor | Score | Evidence |
|---|---|---|
| P1 hidden mediators | 2 | perio↔CV runs through inflammation, CRP, endothelial dysfunction, atherosclerosis, bacteremia — in no single field |
| P2 fragmented input | 2 | dental and medical records live in separate silos with different shapes (HISTORA's raison d'être) |
| P3 missing-variable sensitivity | 2 | hs-CRP is often absent; the whole inflammatory axis hinges on flagging it, never imputing it |
| P4 deterministic sub-relations | 2 | BOP-band, metabolic-load band, PPD progression delta — computed in `src/relational_signals.py`, tested, injected |
| P5 multi-turn sessions | 1 | research/optimization loop across formats and cases; ledger consolidates lessons |
| P6 guardrailed domain | 2 | non-diagnostic invariant is protected in every gate |
| P7 format is the lever | 2 | the C≥B≫A format hypothesis — presentation, not model size, moves the mediators |
| P8 nameable spec | 2 | the bridge concepts, required variables, and procedure steps are all enumerated |

**Total 15 / 16 → large impact expected.** This is why the dental oral-systemic problem
was chosen as the first instance: it lights up nearly every predictor, with the two
core conditions (P1, P2) at full strength.
