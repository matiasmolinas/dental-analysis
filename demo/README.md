# The canonical demo — one case, end to end

The whole product in one command: a structural case goes in; a **falsifiable, uncertainty-quantified,
non-diagnostic research brief** comes out — Claude's relational hypotheses, the engine's mechanism as
*ranges*, the independent NHANES + genetic validation, and an agentic-metric card, every number traceable.

```bash
python demo/run_demo.py            # offline, deterministic (no API key) — the stage-safe path
python demo/run_demo.py --live     # real Claude relational analysis (needs ANTHROPIC_API_KEY)
```

**The five steps:**

1. **Input** — a structural stratum (bands only); a missing mediator (hs-CRP) shows as a **collection
   flag**, never imputed.
2. **Claude — reasoning** — non-diagnostic oral↔systemic hypotheses, each citing input fields (a
   deterministic stand-in offline; the real agent with `--live`).
3. **Engine** — the shared inflammatory proxy → CRP / HbA1c / tau-α as **90% envelopes** + the
   periodontal-therapy counterfactual + the dominant uncertainty per output.
4. **Validation** — the three NHANES association signs (design-adjusted) + the Mendelian-randomization
   probe, in a panel labeled **"validation ≠ calibration."**
5. **Falsifiable brief** — the refutation conditions + the agentic-metric card (citation accuracy,
   hallucination rate, uncertainty coverage, falsifiability, guardrail).

**The message:** breadth is the point — *one inflammatory proxy, three diseases, one engine* — and the
agent is honest by construction (ranges, falsification, a hard non-diagnostic guardrail). The fixed case
(`case.json`) is synthetic and structural; **nothing here diagnoses or imputes a patient value.**

`brief.json` is written next to this README (git-ignored). Record a screen capture of the run as the
stage fallback.
