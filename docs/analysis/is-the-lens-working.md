# Is the Jacobian-Lens Strategy Working? An Honest Read of the Live A/B

> Produced 2026-07-09 with the **Fable** model. Scope: Claude Sonnet-5, live A/B of
> 2026-07-09. Inferred lens = self-report only; no measured lens, no proxy. Numbers from
> `results/ab_live_report.json` (n=3), `results/ab_live_improved.json` (n=6), and the
> grounded n=1 run in [`../REFORMULATION.md`](../REFORMULATION.md) §R5.

## 1. Is it working? — the honest verdict

| Claim | Rating | Basis |
|---|---|---|
| **(a) Converged INPUT (B) improves outcomes vs naive (A)** | **Supported (small-n)** | B ≥ A on every metric in all three runs; strict wins on missing-data + guardrail, and on recall in 2 of 3. |
| **(b) The gain is on the guardrail-critical axis (missing-data flagging / non-imputation)** | **Supported, but partly by construction** | missing_data_flagged 0.00→1.00, guardrail_pass 0.00→1.00 — but B is *told* which fields are missing. |
| **(c) The inferred *lens itself* is doing causal work** | **Not-yet / unfalsifiable here** | The live A/B does not contain the lens in the loop at all. |

**Blunt statement on (c).** The live experiment compares **naive input (A)** against a
**converged input (B)** = JSON + mechanistic KB + injected deterministic signals + a
data-completeness directive. All four are things a competent domain author would write
**without ever reading a lens readout**. The Observer, the readout schema, the deficiency
maps, and the Session Working-Consciousness are design-stage artifacts and worked
examples (`schemas/examples/`, `.session/example_case01.md`); **none executed during the
A/B.** So the data licenses only: *"a well-structured, KB-glossed, flag-injected input
beats a naive abbreviated table on Claude"* — a **prompt-engineering** result, not
evidence the lens localized anything. The comparison that would credit the lens
(**lens-guided vs blind convergence**) is absent.

**Second caveat on (b).** A's guardrail pass-rate is **0.00 structurally**: `guardrail_pass`
requires flagging all truly-missing mediators, but A's naive format never names those
fields, so it can't. B is handed a directive saying *"add EVERY one of them to
required_missing_data."* The missing-data axis is therefore near-**tautological** — B is
instructed to do exactly what the metric scores. The genuinely empirical content is not
"B flags missing data" but the *reliability* finding in §2.

## 2. What the numbers actually show

**Recall is not where the value is.** Sonnet-5 recovers mediators even from naive A:
recall **0.58 → 0.65 → 0.75** for A. B gives **0.75 → 0.79 → 0.77** (delta +0.00 / +0.21
/ +0.12). Positive but modest, and B's KB spoon-feeds the mediator vocabulary, so the
lift is not cleanly attributable. Mechanism-recall is **not** the story.

**The value is reliable guardrail compliance / non-imputation:** missing_data_flagged
**0.00 → 1.00**, guardrail_pass **0.00 → 1.00 (6/6)**. In a health context where a silent
guess is worse than a flagged gap, "never flags → always flags" is the meaningful delta.

**The n=3 → n=6 story is the most honest result.** At n=3 the verdict was **keep_A**: B
guardrail 0.33 (1/3), missing-flag 0.67. The per-case JSON shows why — two cases had
`traceability_ok: false` and one didn't flag the missing field, i.e. **the executor was
explicitly told to copy the injected flags and still didn't, 2 of 3 times.** A real
found weakness: instruction-following isn't free even when explicit. A bounded input
directive + a fair output-compliance clause lifted B to **1.00 (6/6)** → **promote_B**.

**Caveats riding alongside:** tiny n (1/3/6), random participants, no CIs, no
temperature-variance; single model, single day; and the fix that flipped the verdict was
found by reading the **output metric**, not a lens readout — even the one empirical
improvement was not lens-driven.

## 3. The experiment gap that must be closed to credit the lens

Run a **three-arm ablation on the same cases**:
- **A** — naive input.
- **B_blind** — a strong author / capable model converges the input **without any lens
  readout**. Best-effort blind prompt engineering.
- **B_lens** — the Observer reads the inferred-lens readout, produces a deficiency map,
  and converges the input *from that diagnosis*.

The lens earns its keep **only if B_lens > B_blind** beyond noise. If B_lens ≈ B_blind,
the lens is decorative and the win is prompt engineering. **This is the single most
important missing experiment.**

Two corroborating runs to add:
- **Counterfactual-sensitivity — specified but never executed.** "counterfactual"
  appears in 19 docs but in **zero runnable code**. Implement the flip (toggle a mediator
  present↔MISSING; verify the dependent axis moves, unrelated axes don't). It converts a
  promised safeguard into a real one. *(T0, high value.)*
- **Measured-lens comparison** — only if Anthropic ever exposes the real lens via API;
  speculative until then, label as such.

## 4. Next steps across all surfaces + the SWC

Recall already high → deprioritize; missing-data reliability is the demonstrated lever;
lens isolation is unproven.
- **Work prompts** *(T0)* — make the data-completeness directive a reusable, testable
  fragment; run it inside **B_blind vs B_lens** to learn whether the *lens* or merely the
  *directive* produced the 0.33→1.00 lift.
- **Skills** *(T1)* — promote the output-compliance clause into a skill only behind the
  T1 gate at larger n; do not promote off n=6.
- **KB context** *(T0)* — KB-ablation (B with vs without KB); if it isn't moving
  mediators, trim it.
- **Sub-agent defs + injected variables** *(T1)* — validate each injected signal changes
  an output axis (counterfactual flip per signal) before committing new variables.
- **Harness code** *(T0 build / T1 promote)* — implement the counterfactual-sensitivity
  runner in `src/` with tests; currently the biggest gap between docs and code, and the
  cleanest S4 demo (lens → code → injected variable → re-check).
- **Session Working-Consciousness** *(T1)* — has never run live (only the example). Its
  thesis (cross-turn consolidation) is untested. Next: a real multi-turn session where a
  turn-1 deficiency measurably improves turn 2, logged in the live ledger.

**Priority:** (1) **B_lens vs B_blind ablation** — without it the central claim is
unsupported; (2) **larger-n A/B (n≥30)**; (3) **execute counterfactual sensitivity**.
Lifting recall is **not** a priority.

## 5. Bottom line for a hackathon judge

On Claude today, the live A/B genuinely demonstrates one thing: an **Observer-converged
input reliably beats a naive one on the guardrail-critical axis** — missing-data flagging
and non-imputation go 0.00 → 1.00 (6/6), flipping the verdict to promote_B, while
mechanism-recall (0.65→0.77) shows the frontier model already recovers most mediators
unaided, so recall is not the lever. The most credible finding is the **n=3→n=6 story**:
a real reliability weakness was caught and fixed with a bounded directive — honest
engineering, small-n. What remains **speculative** is the load-bearing claim: this A/B
compares naive-vs-converged input, **not lens-guided-vs-blind convergence**, so it does
**not** isolate any causal contribution from the inferred lens — a careful author would
produce arm B unaided, and the guardrail win is partly baked in because B is *told* which
fields to flag. The lens's isolated value and the measured-lens "unlock" are both
**unproven**; credit the prompt-engineering result, and reserve judgment on the
Jacobian-lens thesis until the B_lens/B_blind ablation and the (still-unimplemented)
counterfactual-sensitivity check are actually run.
