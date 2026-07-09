# SWC live session (#4) + targeted actuator (#2): first live run of the session-consciousness loop

> 2026-07-09, live Claude (Opus executor/reviewer, Sonnet selector). Results of next-steps **#4**
> (`results/swc_session.json`) and **#2** (`results/targeted_report.json`). Closes the "implement all
> six next-steps" task; retires the "the SWC never ran live" caveat from
> [`RESEARCH_SUMMARY.md`](../../RESEARCH_SUMMARY.md) §2 (H5). Written directly (Fable refuses this topic).

## #4 — the Session Working-Consciousness ran end-to-end, live, for the first time

A 2-turn session on the planted case: turn-1 output → a reviewer named the absent, factor-relevant
gaps → a selector kept the targeted subset → turn-2 re-ran with them injected → measured the delta →
persisted the working lever to the **cross-session ledger** (`.knowledge/lever_ledger.jsonl`).

| | turn 1 | turn 2 | Δ |
|---|---|---|---|
| relational_recall | 0.50 | **0.625** | **+0.125** |
| counterfactual mean_affected_delta | 0.00 | 0.00 | 0.00 |
| `improved` | | | **True** |
| ledger write | | | `inject targeted factor-specific review considerations` (corroboration `repeated_turns`), **guardrail-validated** |

**What this demonstrates (mechanistic, not a value claim):**
- The **whole SWC loop works live** — a turn-1 deficiency measurably improved turn-2 (relational_recall
  +0.125), the loop is not just `.session/example_case01.md` any more.
- The **SWC ↔ cross-session memory wiring works** — the working lever was written to the ledger through
  the write-time guardrail (it is structural — a case signature + a lever + corroboration, **no patient
  values** — which is exactly what `lever_ledger.validate_lever` enforces). A future session's
  `suggest_levers` would surface it.

## #2 — targeted vs append-all vs base (the "free actuator" test)

Same planted case, three arms (`run_targeted.py`):

| arm | counterfactual Δ | relational_recall |
|---|---|---|
| base | +0.33 | 0.50 |
| append_all (crude actuator) | 0.00 | 0.50 |
| **targeted** (judge-selected, factor-relevant) | 0.00 | **0.62** |

**Selectivity helps recall:** the targeted actuator lifts relational_recall (0.62) over both base and
the crude append-all (0.50) — the append-all-dilution effect from
[`gate-behavioral-and-opus-result.md`](gate-behavioral-and-opus-result.md) is *partly* undone by
selecting only the mechanistically-relevant gaps. **But grounding still regresses the counterfactual
axis** (+0.33 → 0.00), and this is **n=1**.

## Honest reading

Both #2 and #4 point the same way and must be read the same way:
- **Consistent small positive on relational_recall (+0.12–0.125)** from *targeted* (not crude)
  injection, appearing in two independent runs (#2 and #4's turn-2). That is the least-weak positive
  signal in the whole arc for the actuator side.
- **No movement (or regression) on counterfactual sensitivity** — the *reasoning-grounding* axis did not
  improve; grounding did not make the output more factor-responsive.
- **n = 1**, single case, single day. These are **mechanistic demonstrations** — the loop runs, the
  memory persists, targeted beats crude on recall — **not** evidence of robust value. The verdict-changing
  runs remain the powered **n ≥ 30** targeted-actuator experiment on a non-obvious-gap task, and the
  **measured** lens (`RESEARCH_SUMMARY.md` §6).

## Net for the six-step implementation
All six next-steps are built (`RESEARCH_SUMMARY.md` §4b). The two that ran live (#2, #4) give a
**consistent, small, single-case positive on relational_recall from targeted injection** and **no
counterfactual gain** — directional, honest, and squarely inside the "real signal, payoff still
unproven at power" position the whole investigation converged on.
