# Worked example — R1 dry-run of the inferred-lens Observer contract

One case exercised end-to-end through the Phase R1 contract (see
[`../../docs/REFORMULATION.md`](../../docs/REFORMULATION.md)). Both files are strictly
schema-valid (`additionalProperties: false`); the case description lives here, not in
the JSON.

**Case 01 — mediators absent under a naive format.** Fragmented record: periodontitis
(deep PPD, high BOP, bone loss) + hypertension + type-2 diabetes, with the **hs-CRP
field absent** from the input, fed in naive format A (abbreviated table, no glossing).

| File | Schema | What it shows |
|---|---|---|
| `readout_case01.json` | `../lens_readout_schema.json` | The executor's inferred-lens readout: shared factors (diabetes/smoking) surface, but the inflammatory mediators are faint/absent, hs-CRP never registered, and axis derivation was skipped. |
| `deficiency_map_case01.json` | `../deficiency_map_schema.json` | The Lens Observer's response: three readout-grounded deficiencies → three bounded T0 edits (inject `hs_crp=MISSING`, attach the mechanistic KB snippet, make axis derivation explicit) → an SWC update with consolidated beliefs, pending hypotheses, and a prompt injection for the next turn. |

Every proposed edit cites its readout evidence (anti-Goodhart), sets
`guardrail_safe: true`, and is tier T0 (ephemeral, in-session). This is the intended
turn-level behavior of `agents/lens-observer.md` driven by
`prompts/observer.md` + `skills/lens-deficiency-analysis.md`.

Validate:

```bash
# strict validation (additionalProperties:false honored)
python3 -m venv .venv && . .venv/bin/activate && pip install jsonschema
python3 - <<'PY'
import json, jsonschema
for s,i in [("../lens_readout_schema.json","readout_case01.json"),
            ("../deficiency_map_schema.json","deficiency_map_case01.json")]:
    jsonschema.validate(json.load(open(i)), json.load(open(s)))
    print("OK", i)
PY
```
