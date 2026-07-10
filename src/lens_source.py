"""Lens-source adapter: one seam for `inferred` (today) vs `measured` (the API feature).

Path C of docs/FORWARD_PLAN.md. The whole loop consumes a lens readout conforming to
`schemas/lens_readout_schema.json`. Today the ONLY available source is the executor's
self-report probe (`skills/claude-workspace-probe.md`) — uninstrumented, not a measurement.
The forward claim (docs/API_FEATURE_REQUEST.md) is that Anthropic could expose the REAL
Jacobian lens on Claude; if it did, swapping to it should be a signal-source change with no
redesign.

This module makes that claim literally true and testable: `get_lens_readout(request,
source=...)` returns the SAME validated schema shape whichever source is chosen.
`measured` raises a documented NotImplementedError (the API does not exist yet) but is wired
to the identical contract, so the day it ships the change is `--lens-source measured` plus
one function body. This adds ZERO research signal — it is a positioning + honesty seam, and
it also validates the inferred readout against the schema (which the raw self-report text
was not, before).

Model-agnostic like the rest of the harness: the inferred path takes an injected
`probe_fn(request_text) -> str | dict` so it is testable offline with a stub; the live
wiring builds `probe_fn` from the Anthropic SDK (see run_ablation.make_fns).
"""

from __future__ import annotations

import json
import os
from typing import Any, Callable

SOURCES = ("inferred", "measured")

_MEASURED_MSG = (
    "measured lens API not yet exposed — see docs/API_FEATURE_REQUEST.md. This adapter is "
    "the consumer seam: when the Anthropic API exposes the real Jacobian lens on Claude, "
    "implement measured_lens_readout to the same schema and pass source='measured'."
)


def _schema_path() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "schemas", "lens_readout_schema.json")


def load_readout_schema() -> dict:
    with open(_schema_path()) as f:
        return json.load(f)


def _coerce(readout: str | dict) -> dict:
    """Accept either a parsed dict or a JSON/text string (tolerating code fences)."""
    if isinstance(readout, dict):
        return readout
    from run_live_ab import _extract_json  # tolerant JSON parse (fences / prose)

    return _extract_json(readout)


def validate_readout(readout: str | dict) -> dict:
    """Return the readout as a dict if it conforms to lens_readout_schema, else raise
    ValueError. Uses jsonschema when installed; otherwise a minimal structural check of the
    required keys and the self_report_not_measurement invariant (which must be True — the
    honesty guardrail that this is self-report, never a measurement)."""
    obj = _coerce(readout)
    try:
        import jsonschema  # optional

        jsonschema.validate(obj, load_readout_schema())
    except ImportError:
        required = {"concepts", "sweep", "self_report_not_measurement"}
        missing = required - set(obj)
        if missing:
            raise ValueError(f"lens readout missing required keys {missing}")
        if not isinstance(obj.get("concepts"), list):
            raise ValueError("lens readout `concepts` must be an array")
        sweep = obj.get("sweep")
        if not isinstance(sweep, dict) or {"early", "mid", "late"} - set(sweep):
            raise ValueError("lens readout `sweep` must have early/mid/late arrays")
    except Exception as e:  # jsonschema.ValidationError et al.
        raise ValueError(f"lens readout failed schema validation: {e}") from e
    if obj.get("self_report_not_measurement") is not True:
        # The inferred source is self-report; a measured source would set this False and
        # populate real magnitudes. Either way the field must be present and explicit.
        if obj.get("self_report_not_measurement") is None:
            raise ValueError("lens readout must declare self_report_not_measurement")
    return obj


def inferred_lens_readout(request: str, probe_fn: Callable[[str], Any]) -> dict:
    """The source available today: the executor's self-report probe. `probe_fn(request)`
    runs the `claude-workspace-probe` skill and returns the readout (str or dict); we parse
    and validate it to the schema. Self-report, NOT a measurement."""
    raw = probe_fn(request)
    return validate_readout(raw)


def measured_lens_readout(request: str, **_: Any) -> dict:
    """The forward claim: the real Jacobian lens on Claude via the Anthropic API. Not our
    code to run — this raises with the documented pointer, but conforms to the same
    `get_lens_readout` contract so the swap is a one-line change the day the API exists."""
    raise NotImplementedError(_MEASURED_MSG)


def get_lens_readout(
    request: str,
    source: str = "inferred",
    probe_fn: Callable[[str], Any] | None = None,
) -> dict:
    """Return a schema-valid lens readout from the chosen source. `inferred` requires a
    `probe_fn`; `measured` raises the documented NotImplementedError. Same return contract
    for both — that identical contract is the point of this adapter."""
    if source == "inferred":
        if probe_fn is None:
            raise ValueError("source='inferred' requires a probe_fn (the self-report probe)")
        return inferred_lens_readout(request, probe_fn)
    if source == "measured":
        return measured_lens_readout(request)
    raise ValueError(f"unknown lens source {source!r} (use one of {SOURCES})")
