"""Live three-arm ablation on Claude (Phase R6): A vs B_blind vs B_lens.

Isolates the inferred lens's causal contribution. B_blind and B_lens are produced by the
SAME converger model with the SAME instruction; the ONLY difference is that B_lens also
receives the inferred-lens readout + the Observer's deficiency map for the case. If
B_lens does not beat B_blind, the lens is not earning its keep and the win is blind prompt
engineering — an honest, valid result either way.

Requirements (as run_live_ab): anthropic + ANTHROPIC_API_KEY + pandas/network (for
--cases nhanes). Runs entirely on Claude.

Usage:
  python src/run_ablation.py --cases nhanes --n 4 --model claude-sonnet-5
  python src/run_ablation.py --cases grounded
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from ablation import run_ablation
from run_live_ab import (
    _extract_json,
    _load_dotenv,
    load_cases,
    make_claude_model_fn,
)

_HERE = os.path.dirname(__file__)


def _read(rel: str) -> str:
    with open(os.path.join(_HERE, "..", rel)) as f:
        return f.read()


# The converger's instruction is IDENTICAL for both blind and lens arms — it only ever
# sees extra (lens) information in the lens arm. It must not itself analyze; it produces
# the INPUT that a downstream agent will analyze.
CONVERGE_SYSTEM = """You prepare the INPUT that will be fed to a separate non-diagnostic
oral-systemic (periodontal + cardiovascular) research agent. Given the patient record,
produce the single most effective input text so that the downstream agent (a) surfaces
the true oral-systemic MEDIATING mechanisms (inflammation, C-reactive protein, cytokines,
atherosclerosis, endothelial dysfunction, bacteremia, oxidative stress, cardiovascular
risk) and (b) flags every mediating datum that is ABSENT from the record for collection,
never imputing a value. You may restructure, gloss terms, add mechanistic context, and
add explicit data-completeness flags. Output ONLY the input text to feed the agent — do
NOT produce the analysis yourself."""


def _text_block(resp) -> str:
    t = next((b.text for b in resp.content if getattr(b, "type", None) == "text"), None)
    if t is None:
        raise RuntimeError("no text block in the model response")
    return t


def make_fns(model: str):
    import anthropic

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set.")
    client = anthropic.Anthropic()
    schema = _read("schemas/output_schema.json")
    readout_system = (
        _read("skills/claude-workspace-probe.md")
        + "\n\nRespond ONLY with a JSON object per schemas/lens_readout_schema.json "
        "(concepts, sweep, required_variables_seen, cot_steps_traversed, "
        "self_report_not_measurement:true)."
    )
    observer_system = _read("prompts/observer.md")

    def call(system: str, user: str, max_tokens: int = 4000) -> str:
        resp = client.messages.create(
            model=model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}],
        )
        return _text_block(resp)

    def readout_fn(naive_input: str) -> str:
        return call(readout_system, naive_input)

    def observer_fn(naive_input: str, readout: str, spec: str) -> str:
        user = (f"Prompt package (naive input):\n{naive_input}\n\n"
                f"Inferred-lens readout:\n{readout}\n\nSpec:\n{spec}\n\n"
                "Return the deficiency map JSON per schemas/deficiency_map_schema.json.")
        return call(observer_system, user)

    def converge_fn(record: dict, diagnosis: dict | None) -> str:
        user = f"Patient record (JSON):\n{json.dumps(record, indent=2)}"
        if diagnosis is not None:
            user += (
                "\n\nDiagnostic signal from a workspace readout of a first pass on the "
                "naive input — which mediating concepts/variables were absent or weak, "
                "and the deficiency map. Address these SPECIFIC gaps in the input you "
                f"produce.\n\nInferred-lens readout:\n{diagnosis['readout']}\n\n"
                f"Deficiency map:\n{diagnosis['deficiency_map']}"
            )
        return call(CONVERGE_SYSTEM, user, max_tokens=3000)

    eval_fn = make_claude_model_fn(model)  # the neutral evaluator (input is the only lever)
    return readout_fn, observer_fn, converge_fn, eval_fn


def main() -> None:
    ap = argparse.ArgumentParser(description="Three-arm lens ablation on Claude")
    ap.add_argument("--cases", choices=["grounded", "nhanes"], default="grounded")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--seqns", type=int, nargs="*")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--out", default=os.path.join(_HERE, "..", "results", "ablation_report.json"))
    args = ap.parse_args()

    _load_dotenv()
    cases = load_cases(args.cases, args.n, args.seqns)
    readout_fn, observer_fn, converge_fn, eval_fn = make_fns(args.model)
    report = run_ablation(cases, readout_fn, observer_fn, converge_fn, eval_fn)
    report["meta"] = {"cases": args.cases, "model": args.model, "n": len(cases)}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report["aggregate"], indent=2))
    print("deltas:", json.dumps(report["deltas"]))
    print("verdict:", report["verdict"], "| wrote:", args.out)


if __name__ == "__main__":
    main()
