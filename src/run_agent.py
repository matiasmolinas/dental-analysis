"""Run the HISTORA relational agent on Claude — the non-diagnostic reasoning entrypoint.

Given an integrated oral + systemic record, this runs Claude to produce structured oral↔systemic
research hypotheses (relational axes + mechanisms + traceability + data-collection flags), then checks
the non-diagnostic guardrail. The input carries the deterministic missing-data directive (W1), so the
harness — not the model — guarantees the guardrail-critical collection flags.

Requires `anthropic` + `ANTHROPIC_API_KEY` (loaded from a repo-root `.env`).
Usage:  python src/run_agent.py [--model claude-opus-4-8]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.ab_eval import build_inputs, score
from histora.agent import load_dotenv, make_agent
from histora.record_formats import RECORD


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the HISTORA non-diagnostic relational agent")
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "agent_output.json"))
    args = ap.parse_args()

    load_dotenv()
    analyze = make_agent(args.model)

    record = RECORD                          # the built-in NHANES-2009-2010-grounded case
    record_text = build_inputs(record)["B"]  # converged input incl. the W1 missing-data directive
    output = analyze(record_text)
    scored = score(output, record)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({"output": output, "score": scored, "model": args.model}, f, indent=2)

    print(f"model={args.model} | guardrail_pass={scored['guardrail_pass']} "
          f"| axes={len(output.get('relational_axes', []))} "
          f"| missing_data_flagged={scored['missing_data_flagged']}")
    for ax in output.get("relational_axes", []):
        print(f"  [{ax.get('axis')}] {ax.get('hypothesized_mechanism', '')[:90]}")
    print("non_diagnostic_disclaimer:", output.get("non_diagnostic_disclaimer"))
    print("wrote:", args.out)


if __name__ == "__main__":
    main()
