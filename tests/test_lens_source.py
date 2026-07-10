"""Tests for the lens-source adapter (Path C) — no API, no GPU.

Verifies the identical return contract across sources: `inferred` runs a stub probe and
validates to schemas/lens_readout_schema.json; `measured` raises the documented
NotImplementedError; both share the same schema shape.

Run:  python tests/test_lens_source.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lens_source import (
    get_lens_readout,
    inferred_lens_readout,
    measured_lens_readout,
    validate_readout,
)


def _valid_readout() -> dict:
    return {
        "concepts": [
            {"concept": "periodontitis", "channel": "intermediate_step", "stage": "early",
             "salience": "strong", "confidence": "high"}
        ],
        "sweep": {"early": ["periodontitis"], "mid": ["diabetes"], "late": ["inflammation"]},
        "self_report_not_measurement": True,
    }


def test_inferred_validates_and_returns_dict():
    readout = get_lens_readout("naive input", source="inferred",
                               probe_fn=lambda _req: _valid_readout())
    assert readout["self_report_not_measurement"] is True
    assert readout["concepts"][0]["concept"] == "periodontitis"


def test_inferred_accepts_json_string_from_probe():
    # the live probe returns text; the adapter must parse+validate it (tolerating fences)
    as_text = "```json\n" + json.dumps(_valid_readout()) + "\n```"
    readout = inferred_lens_readout("naive input", probe_fn=lambda _req: as_text)
    assert readout["sweep"]["early"] == ["periodontitis"]


def test_inferred_rejects_malformed_readout():
    bad = {"concepts": []}  # missing sweep + self_report_not_measurement
    try:
        inferred_lens_readout("x", probe_fn=lambda _req: bad)
    except ValueError:
        return
    raise AssertionError("expected ValueError on malformed readout")


def test_measured_raises_documented_not_implemented():
    try:
        measured_lens_readout("naive input")
    except NotImplementedError as e:
        assert "API_FEATURE_REQUEST.md" in str(e)
        return
    raise AssertionError("measured source must raise NotImplementedError until the API ships")


def test_get_lens_readout_measured_same_entrypoint():
    try:
        get_lens_readout("x", source="measured")
    except NotImplementedError:
        return
    raise AssertionError("get_lens_readout(source='measured') must raise NotImplementedError")


def test_inferred_requires_probe_fn():
    try:
        get_lens_readout("x", source="inferred")
    except ValueError:
        return
    raise AssertionError("inferred source without a probe_fn must raise ValueError")


def test_unknown_source_rejected():
    try:
        get_lens_readout("x", source="bogus")
    except ValueError:
        return
    raise AssertionError("unknown source must raise ValueError")


def test_validate_readout_accepts_canonical_example():
    here = os.path.join(os.path.dirname(__file__), "..", "schemas", "examples", "readout_case01.json")
    with open(here) as f:
        example = json.load(f)
    assert validate_readout(example)["self_report_not_measurement"] is True


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
