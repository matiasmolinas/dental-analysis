"""Tests for the live A/B runner plumbing (Phase R5) — no network, no API, no GPU.

Exercises everything in `run_live_ab.py` that does NOT require the Anthropic SDK, an API
key, or NHANES download: JSON extraction from messy model text, the neutral fixed system
instruction, grounded case loading, and graceful failure when credentials are absent.
The actual Claude call and NHANES download are covered by the live run itself.

Run:  python tests/test_run_live_ab.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import run_live_ab as live


def test_extract_json_plain():
    assert live._extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_code_fenced():
    assert live._extract_json('```json\n{"a": 1, "b": [2,3]}\n```') == {"a": 1, "b": [2, 3]}


def test_extract_json_with_prose_around():
    txt = 'Here is the output:\n{"non_diagnostic_disclaimer": true}\nHope it helps.'
    assert live._extract_json(txt) == {"non_diagnostic_disclaimer": True}


def test_system_instruction_is_neutral():
    # The fixed instruction must NOT itself gloss terms, inject the KB, or name hs-CRP,
    # or B's advantage would be baked into the agent rather than the input.
    s = live.SYSTEM_INSTRUCTION.lower()
    for leak in ("hs-crp", "hs_crp", "c-reactive", "atheroscler", "endothelial", "knowledge base"):
        assert leak not in s, f"agent instruction leaks '{leak}' — not a fair A/B lever"
    assert "non-diagnostic" in s and "cite" in s  # keeps the guardrail-relevant rules


def test_load_grounded_case_needs_no_deps():
    cases = live.load_cases("grounded", n=1, seqns=None)
    assert len(cases) == 1 and "periodontal" in cases[0]


def test_make_model_fn_fails_clearly_without_key(monkeypatch=None):
    os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        live.make_claude_model_fn("claude-sonnet-5")
    except SystemExit as e:
        assert "ANTHROPIC_API_KEY" in str(e) or "anthropic SDK" in str(e)
    else:  # pragma: no cover - only if SDK+key are both present
        pass


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
