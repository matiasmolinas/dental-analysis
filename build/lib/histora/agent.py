"""The Claude-powered relational analysis — HISTORA's non-diagnostic reasoning core.

Given an integrated oral + systemic record, Claude produces a structured, NON-DIAGNOSTIC research
output conforming to `schemas/output_schema.json`: relational axes (inflammatory / metabolic /
vascular / shared-behavioral / neuroinflammatory) with a hypothesized mechanism, full traceability to
the exact input fields, research hypotheses, and data-collection flags for absent mediators. This is
where Claude's reasoning does the work the deterministic harness cannot: relating fragmented dental +
medical data into candidate oral-systemic mechanisms.

Guardrails are structural (see `histora.scoring.guardrail_pass`): the disclaimer must be present, every
axis must cite its input fields, and every truly-missing mediating datum must be flagged for
collection (never imputed). Requires `anthropic` + `ANTHROPIC_API_KEY` (a local `.env` is loaded).
"""

from __future__ import annotations

import json
import os
import re
from typing import Callable

ModelFn = Callable[[str], dict]

# A lean, neutral instruction: the INPUT carries the record; the model must relate, not diagnose.
SYSTEM_INSTRUCTION = """You analyze an integrated oral + systemic (periodontal + cardiovascular +
neuro) record and produce a NON-DIAGNOSTIC research output. Rules: research hypotheses and
data-completeness flags only, never a diagnosis; never impute a patient value (missing data is a
collection flag); every relational axis must cite the exact input fields it was derived from.
Output-compliance (every response): `non_diagnostic_disclaimer` must be exactly true, and every entry
in `relational_axes` must include a non-empty `traceability` array. Output ONLY a JSON object
conforming to this schema:
%s
Return the JSON and nothing else."""


def load_dotenv() -> None:
    """Load KEY=VALUE lines from a repo-root .env into os.environ (existing vars win). The .env is
    git-ignored; this is a tiny dependency-free loader."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def _load_schema() -> str:
    here = os.path.dirname(__file__)
    with open(os.path.join(here, "..", "..", "schemas", "output_schema.json")) as f:
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
    """messages.create with backoff on transient errors (connection blips, 429/5xx)."""
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


def make_agent(model: str = "claude-opus-4-8") -> ModelFn:
    """Build `analyze(record_text) -> output dict` backed by Claude. The record text is the only
    lever; the same system + model produce a schema-shaped non-diagnostic output."""
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover - env-dependent
        raise SystemExit("anthropic SDK not installed: pip install anthropic; set ANTHROPIC_API_KEY.") from e
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set (add it to .env or the environment).")
    client = anthropic.Anthropic()
    system = SYSTEM_INSTRUCTION % _load_schema()

    def analyze(record_text: str) -> dict:
        last = None
        for _ in range(3):  # regenerate on truncated/malformed JSON, not just connection errors
            resp = _create_with_retry(client, model=model, max_tokens=12000, system=system,
                                      messages=[{"role": "user", "content": record_text}])
            text = next((b.text for b in resp.content if getattr(b, "type", None) == "text"), None)
            if text is None:
                last = RuntimeError("no text block in the model response")
                continue
            try:
                return _extract_json(text)
            except json.JSONDecodeError as e:
                last = e
        raise last

    return analyze
