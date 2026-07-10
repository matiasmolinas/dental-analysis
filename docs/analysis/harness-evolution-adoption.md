# Harness evolution — llmunix / skillos adoption analysis

> Fable analysis, 2026-07-10 (code read in full: the installed `llmunix-plugin` DreamEngine/
> MemoryAnalysis/SystemAgent, the older `../llmunix-marketplace`, `../skillos/skillos.py`, and the
> `skillos-systemcontrol-plugin` agents). Decision record for how to evolve the dental-analysis
> harness. Verdict: **adopt IDEAS, not frameworks — and measure our own consolidation first.**

## What each thing actually is (grounded in the code)

- **llmunix (DreamEngine / MemoryAnalysis / SystemAgent) — 100% prompt markdown. Zero code, zero
  tests, zero validation.** DreamEngine tells an LLM to run SWS→REM→Consolidation over
  `traces/*.md`: score `0.4·conf + 0.4·outcome + 0.2·recency`, merge successes on **50% keyword
  overlap**, `confidence += 0.05` capped 0.95, deprecate when `failures > 2·successes`, prune >7 days
  — all **uncalibrated folklore constants executed by an LLM** (non-deterministic; "idempotency" is
  declared, not achieved). MemoryAnalysis instructs the model to persist **complete prompts and
  responses verbatim**. SystemAgent mandates **≥3 agents + ≥3 dream cycles per goal** (a 5–10× cost
  multiplier by fiat). Well-written scaffold; nothing measured, nothing testable.
- **skillos (`skillos.py`, 867 lines) — not "Claude Code as a library."** A rich-REPL + threading
  scheduler whose entire integration surface is `subprocess.run(["claude","-p","--output-format",
  "text","--continue", prompt], timeout=300)`. No Agent SDK, no structured/JSON output, no transcript
  capture, racy `--continue` under concurrency, stderr discarded, quickstart uses
  `--dangerously-skip-permissions`.
- **skillos-systemcontrol-plugin** — the most useful *ideas*, as ~40 lines of rubric text:
  a **7-type failure taxonomy** (PerformanceScorecard) and an **anti-overfitting gate** +
  minimal-surface edit ranking + propose-don't-apply (EvolutionControl).

## Fit test — additive or re-skin?

| Need | dental-analysis has | llmunix/skillos offers | Verdict |
|---|---|---|---|
| Trace capture | deterministic scored outcomes + guardrailed writes (`validate_lever`) | LLM self-graded logs, full prompt/response persisted, **no write-time validation** | **Regression** (self-graded confidence + PHI risk) |
| Consolidation | `lever_ledger.consolidate()` — 20 deterministic lines, `min_support≥2` or strong corroboration | DreamEngine — same op, nondeterministic, keyword-overlap, folklore constants | **Re-skin.** Additive *concepts*: negative constraints; belief deprecation (~30 lines) |
| Value measurement | `run_memory_value.py` COLD/WARM + bootstrap CI — **built, never run** | **nothing** — neither framework measures whether consolidation helps | dental-analysis strictly ahead |
| Evolve prompts/defs | gap | failure taxonomy + anti-overfitting gate + minimal-surface ranking | **Additive — as rubric text only** |
| Loop orchestration | `run_memory_value.main()` + anthropic SDK, structured outputs | skillos subprocess REPL/scheduler | **Duplicate, worse** |

Ground truth: `.knowledge/lever_ledger.jsonl` is **0 bytes** (reset after the guardrail fix),
`results/memory_value_report.json` is **absent** — confirming "built but never measured."

## Per-option verdicts

- **Option 1 — llmunix as plugin: CUT.** Re-skins `consolidate()` nondeterministically; its trace
  capture **violates the non-diagnostic guardrail by design** (persists full transcripts, no
  validation — reopening the hole just patched at token scale, now at transcript scale); SystemAgent
  multiplies cost; trace format unreadable by our machinery. Salvage the *ideas* only.
- **Option 2 — skillos as Python executor: CUT.** The executor already exists (`run_memory_value.py`
  + anthropic SDK, structured + CIs). skillos replaces it with unstructured text over a racy
  subprocess. For the one real case (drive Claude Code as actor over the *dev harness*), `claude -p
  --output-format json` / the Agent SDK dominates skillos.py on every axis.
- **Option 3 — combination: CUT.** Compounds two unpaid costs, no synergy.

**Adopt-partial shopping list (~80 lines, zero deps):** negative-constraint levers + belief
deprecation (DreamEngine ideas), 7-type failure tags (PerformanceScorecard), anti-overfitting gate +
minimal-surface ranking (EvolutionControl) — **all writes still through `validate_lever`.**

## The prerequisite — run our own measurement FIRST (the decision gate)

The boundary condition (§6 of [`why-no-lens-payoff.md`](why-no-lens-payoff.md)) already names
trace-consolidation as the only live slice, and it is **the one thing the project built and never
measured.** Both frameworks are automation of exactly that unmeasured step. Therefore:

1. **A null on `run_memory_value` is a null on DreamEngine, transitively and for free** — a
   keyword-overlap LLM dream pass over self-graded traces is a strictly noisier estimator of the same
   WARM−COLD quantity than our deterministic, targeted, guardrailed consolidation.
2. **The decisive experiment is cheap** (~30–60 Opus/Sonnet calls, defaults).
3. **The project's own prior is `memory_inconclusive`** — adopting a heavyweight framework ahead of a
   result you predict null is premature by definition.

**Execution caveat (from the code):** the ledger is empty and `_make_live_lever_fn` writes ≤1 lever
per training case, so with `n_train=4` you may get **0 groups reaching `min_support=2`** unless two
cases share a `case_signature`. Check `n_beliefs_consolidated > 0` in the report before trusting the
verdict; a run where `beliefs == []` is a **no-op, not a null**. Raise `--n-train` (or lean on the
comorbidity-overlap match in `_belief_matches`, or `--min-support 1`) until ≥1 belief exists.

## Risks of adoption

- **Non-diagnostic guardrail (dominant).** llmunix persists complete prompts/responses with **no
  write-time validation** → patient-record inputs land in permanent traces + strategy files. Any
  adoption routing case data through llmunix capture is disqualified on this alone.
- **Reproducibility.** LLM-executed consolidation yields different strategy files on identical inputs
  → it can only be noise inside a CI-based COLD/WARM A/B.
- **Over-engineering.** L1–L4 hierarchies, recency decay, 7-day pruning, parallel "unihemispheric
  dreams" are sized for a high-volume agent OS; the dental corpus is ~a handful of cases and a ledger
  holding **zero** levers. Sleep phases over ~7 cases is ceremony, not method.
- **Dependency weight.** Plugin/version drift, Claude Code runtime coupling, `--dangerously-skip-
  permissions` quickstart, SystemAgent's per-goal token multiplier.

## Recommended sequence (cheapest-decisive-first)

1. **Run `src/run_memory_value.py --cases nhanes --fresh-ledger`**, sized so
   `n_beliefs_consolidated ≥ 1` (bump `--n-train`). One afternoon. **This is the entire decision gate.**
2. **If `memory_inconclusive` / `memory_regresses`:** consolidation thesis unpaid → **adopt nothing**
   (options 1/2/3 all CUT); record it; keep the anti-overfitting-gate rubric in a drawer.
3. **If `memory_adds_value`:** extend `lever_ledger.py` by hand — negative constraints, belief
   deprecation, failure tags — every write through `validate_lever`. ~80 lines, zero new deps. Still
   no plugin.
4. **Only if** evolution later targets the *dev harness itself* (no patient data) with Claude Code as
   actor: a thin `claude -p --output-format json` / Agent SDK driver — not skillos.py, not SystemAgent.

**Bottom line:** both siblings are prompt-architecture around a loop this project already implemented
better — deterministic, guardrailed, and with a value-measurement harness neither framework possesses.
The one embarrassing fact is that the measurement was never run. **Measure first; adopt ideas, not
frameworks, and only if the measurement pays.**
