"""Live A/B run on Claude with real NHANES cases (Phase R5).

Wires the model-agnostic harness in `ab_eval.py` to (1) a real Claude call and (2) real
NHANES 2009-2010 participants, then writes a report. The INPUT format is the only lever:
the same fixed agent instruction and the same model score both arms, so any delta is
attributable to A (naive) vs B (Observer-converged).

Requirements for the live run (not needed for `--cases grounded`):
  * `anthropic` SDK + `ANTHROPIC_API_KEY`         (the Claude call)
  * `pandas` + network                             (NHANES download via nhanes_loader)
  install:  pip install -r requirements-live.txt

Usage:
  python src/run_live_ab.py --cases nhanes --n 5 --model claude-sonnet-5
  python src/run_live_ab.py --cases grounded            # 1 built-in NHANES-grounded case
  python src/run_live_ab.py --cases nhanes --seqns 51624 51625

Honesty: the inferred lens stays self-report; the AUTHORITY here is task accuracy +
the protected guardrail measured on Claude. A/B holds the agent constant and varies only
the input, so it is a fair test of the format/convergence, not of the model.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))

from ab_eval import run_ab
from record_formats import RECORD


def _load_dotenv() -> None:
    """Load KEY=VALUE lines from a local .env (repo root) into os.environ if present.
    Tiny, dependency-free; existing env vars win. The .env is git-ignored (secrets)."""
    path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

# A lean, NEUTRAL agent instruction — identical for both arms so the input is the lever.
# It does not itself gloss terms, inject the mechanistic KB, or name hs-CRP; whether the
# mediators surface and whether missing data is flagged must come from the INPUT.
SYSTEM_INSTRUCTION = """You analyze an integrated oral + systemic (periodontal +
cardiovascular) record and produce a NON-DIAGNOSTIC research output. Rules: research
hypotheses and data-completeness flags only, never a diagnosis; never impute a patient
value (missing data is a collection flag); every relational axis must cite the exact
input fields it was derived from. Output-compliance (applies to every response,
independent of the input): `non_diagnostic_disclaimer` must be exactly true, and every
entry in `relational_axes` must include a non-empty `traceability` array. Output ONLY a
JSON object conforming to this schema:
%s
Return the JSON and nothing else."""


def _load_schema() -> str:
    here = os.path.dirname(__file__)
    with open(os.path.join(here, "..", "schemas", "output_schema.json")) as f:
        return f.read()


def _extract_json(text: str) -> dict:
    """Parse the model's JSON output, tolerating code fences / prose around it."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.DOTALL)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not m:
            raise
        return json.loads(m.group(0))


def _create_with_retry(client, *, attempts: int = 5, **kwargs):
    """messages.create with backoff on transient errors (connection blips, 429/5xx), so a
    single network hiccup does not waste a long multi-call run."""
    import time

    import anthropic

    last = None
    for i in range(attempts):
        try:
            return client.messages.create(**kwargs)
        except (anthropic.APIConnectionError, anthropic.RateLimitError,
                anthropic.InternalServerError) as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last


def make_claude_model_fn(model: str, extra_system: str = ""):
    """A model_fn(prompt)->dict backed by the Anthropic API. Same system + model for
    both arms; only the user prompt (the A or B input) differs. `extra_system` appends a
    rule to the neutral instruction (used to test an EVOLVED instruction, e.g. the
    factor-grounding rule, against the base — keep it out of the fair A/B evaluator)."""
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover - env-dependent
        raise SystemExit(
            "anthropic SDK not installed. `pip install -r requirements-live.txt` "
            "and set ANTHROPIC_API_KEY."
        ) from e
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set.")
    client = anthropic.Anthropic()
    system = SYSTEM_INSTRUCTION % _load_schema()
    if extra_system:
        system += "\n\n" + extra_system

    def model_fn(prompt: str) -> dict:
        import json as _json
        last = None
        for _ in range(3):  # regenerate on a truncated/malformed JSON, not just conn errors
            resp = _create_with_retry(
                client, model=model, max_tokens=12000, system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            # Skip non-text blocks (e.g. ThinkingBlock when extended thinking is on).
            text = next(
                (b.text for b in resp.content if getattr(b, "type", None) == "text"), None
            )
            if text is None:
                last = RuntimeError("no text block in the model response")
                continue
            try:
                return _extract_json(text)
            except _json.JSONDecodeError as e:
                last = e
        raise last

    return model_fn


def load_cases(kind: str, n: int, seqns: list[int] | None) -> list[dict]:
    if kind == "grounded":
        return [RECORD]  # the built-in NHANES-2009-2010-grounded synthetic case
    if kind == "nhanes":
        try:
            import pandas  # noqa: F401
        except ImportError as e:  # pragma: no cover - env-dependent
            raise SystemExit(
                "pandas not installed (needed to read NHANES XPT). "
                "`pip install -r requirements-live.txt`."
            ) from e
        from nhanes_loader import build_case, download_files

        paths = download_files(os.path.join(os.path.dirname(__file__), "..", ".nhanes"))
        if seqns:
            return [build_case(paths, seqn=s) for s in seqns]
        return [build_case(paths, seqn=None) for _ in range(n)]
    raise SystemExit(f"unknown --cases {kind!r} (use 'grounded' or 'nhanes')")


def main() -> None:
    ap = argparse.ArgumentParser(description="Live A/B on Claude with NHANES cases")
    ap.add_argument("--cases", choices=["grounded", "nhanes"], default="grounded")
    ap.add_argument("--n", type=int, default=5, help="how many random NHANES participants")
    ap.add_argument("--seqns", type=int, nargs="*", help="specific NHANES SEQN ids")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..",
                                                   "results", "ab_live_report.json"))
    args = ap.parse_args()

    _load_dotenv()
    cases = load_cases(args.cases, args.n, args.seqns)
    model_fn = make_claude_model_fn(args.model)
    report = run_ab(cases, model_fn)
    report["meta"] = {"cases": args.cases, "model": args.model,
                      "seqns": args.seqns, "n": len(cases)}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report["aggregate"], indent=2))
    print("verdict:", report["verdict"], "| wrote:", args.out)


if __name__ == "__main__":
    main()
