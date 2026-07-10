# A/B Validation Protocol (Phase R5) — Claude only

> Validates the approach: does the Observer-converged input actually beat the naive
> input on Claude? This is the fitness signal and the promotion gate (see
> [`REFORMULATION.md`](analysis/ARCHIVE/REFORMULATION.md) §R5, [`../agents/skillopt-optimizer.md`](../agents/skillopt-optimizer.md)).
> Harness: [`../src/ab_eval.py`](../src/ab_eval.py); tests: `tests/test_ab_eval.py`.

## The two arms (same case, same model)

- **A — baseline:** naive abbreviated format, no glossing / no KB
  (`format_a_abbrev_table`).
- **B — converged:** JSON + mechanistic KB + interpretability constraints
  (`format_e_json_kb_constraints`) **with the deterministic structural signals +
  missing-mediator collection flags injected** (`relational_signals.derived_signals`) —
  i.e. the input the Lens Observer converges to.

`ab_eval.build_inputs(record)` returns both. The only difference is the input; the model
and the case are identical, so any score delta is attributable to the input.

## Metrics (non-diagnostic, guardrail-aware)

**Primary honest metrics.** After the live Sonnet-5 v2 runs, the primary signals are
`relational_recall` and **counterfactual sensitivity** — they resist the name-echo
artifact that plain substring recall rewards (v2 finding: counterfactual n=4 showed the
outputs were *not* factor-grounded, and mediator "recall" was largely name-echo, not
reasoning). Plain `mechanism_recall` is **secondary**: it overstates reasoning because it
credits a mediator merely mentioned anywhere in the text.

| Metric | Role | What it measures |
|---|---|---|
| **relational_recall** | **primary** | fraction of mediator concepts named *inside the `hypothesized_mechanism` of an axis that has traceability* — i.e. actually used in a traced oral↔systemic relation, not merely mentioned. Kills the name-echo substring artifact |
| **counterfactual sensitivity** | **primary** | flip one driving factor and check the dependent axis moves in the mechanistically-correct direction while unrelated axes stay put (see `../src/counterfactual.py`, `APPROACH.md` §8) — behavioral proof the output is factor-grounded |
| **mechanism_recall** | secondary | fraction of mediator concepts the output reasons with *by any surface form*; overstates relational reasoning (name-echo), so read it under `relational_recall` |
| **missing_data_flagged** | guardrail | fraction of truly-absent mediating data (e.g. hs-CRP) the output flags for **collection**, never imputed |
| **traceability_ok** | guardrail | every relational axis cites the input fields it came from |
| **guardrail_pass** | invariant | non-diagnostic disclaimer present, full traceability, every truly-missing datum acknowledged (none silently used or imputed) |

## The gate (matches the T1 promotion rule)

Promote B (`verdict: promote_B`) only when, aggregated over cases:
- B's `guardrail_pass_rate` is **1.0** and **≥** A's, **and**
- B's `mechanism_recall` is a **strict** improvement over A, **and**
- B's `missing_data_flagged` is **≥** A's.

An accuracy gain that lowers the guardrail pass-rate is rejected — always.

## Running it

The harness is model-agnostic: `run_ab(records, model_fn)` where
`model_fn(prompt: str) -> dict` returns an output conforming to
`schemas/output_schema.json`.

```python
import sys; sys.path.insert(0, "src")
from ab_eval import run_ab, default_cases

def claude_model_fn(prompt: str) -> dict:
    # Run the orchestrator (agents/orchestrator.md) / evaluator (prompts/evaluator.md)
    # on `prompt` with the guardrail active; return the parsed structured JSON output.
    ...

report = run_ab(default_cases(), claude_model_fn)   # -> aggregate + verdict
```

- **Offline check (now):** `python3 tests/test_ab_eval.py` runs the full scoring +
  verdict logic against a deterministic stub (naive-A vs converged-B canned outputs).
  6/6 pass; the report shows A `mechanism_recall 0.0 / guardrail 0.0` vs B `1.0 / 1.0` →
  `promote_B`. This proves the harness discriminates; it is **not** a model result.
- **Live run:** [`../src/run_live_ab.py`](../src/run_live_ab.py) wires it end to end —
  a real Claude call (Anthropic SDK, neutral fixed system prompt so the input is the
  only lever) over real NHANES 2009–2010 participants (`nhanes_loader.build_case`):

  ```bash
  pip install -r requirements-live.txt        # anthropic + pandas
  export ANTHROPIC_API_KEY=...
  python src/run_live_ab.py --cases nhanes --n 5 --model claude-sonnet-5
  # or a no-network smoke test on the grounded case:
  python src/run_live_ab.py --cases grounded
  ```

  It writes `results/ab_live_report.json` (git-ignored). Paste the aggregate + verdict
  into `REFORMULATION.md` §R5 Progress Log.

## Honesty

The stub result demonstrates the *harness*, not the *method*. Only the live run on
Claude with real cases is evidence for the approach; the inferred lens remains
self-report (corroborated by counterfactual sensitivity — see `APPROACH.md` §8), and
Claude task accuracy + the guardrail are the authorities.
