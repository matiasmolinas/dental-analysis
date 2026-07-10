"""Claude as a soft model member — a live estimator for edges the coded library cannot reach.

The coded ODE/PDE spine (`mech_models`, `mech_neuro`, `mech_metabolic`) covers the edges that have a
tractable equation and a data anchor. Some couplings the harness cares about have neither yet — novel
oral-systemic links, sparse-data edges (e.g. an oral→gut→brain route). For those, Claude supplies a
STRUCTURED, reasoned estimate: a direction, a plausibility band, a confidence tier, a falsification
path, and the modeling technique it recommends coding next. That estimate enters the ensemble as one
member via `ensemble.blend_members`, tier-labeled `"claude"` and weight-capped by
`registry.CLAUDE_MEMBER_WEIGHT_CAP` so it can never outweigh a calibrated/validated coded member.

Design: the core is pure and unit-testable — `build_prompt`, `parse_estimate`, `to_member` take no
network. `estimate_edge(edge, model_fn=...)` injects the model function; it defaults to a Claude-backed
one built lazily (so importing this module never needs the SDK or a key). Tests pass a stub `model_fn`.

Guardrail: this estimates a POPULATION-level parameter edge for a STRUCTURAL stratum (bands/flags in,
a relative-effect band out) — never a patient value, never a diagnosis. The estimate is a HYPOTHESIS
with a falsification path, not a fitted result.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Optional

from .registry import CLAUDE_MEMBER_WEIGHT_CAP

ModelFn = Callable[[str], str]

CONFIDENCE_WEIGHT = {"low": 0.10, "medium": 0.20, "high": 0.30}

SYSTEM_INSTRUCTION = """You are a mechanistic-modeling estimator for a NON-DIAGNOSTIC oral-systemic
research harness. You are given ONE biological edge (a directed coupling between an oral/systemic
node and a downstream node) that the harness has NOT yet coded as an equation, plus the STRUCTURAL
stratum of a population (periodontal stage band, bleeding band, comorbidity set — never patient
values) and the value of the shared inflammatory `gain`. Produce a soft, honest estimate of the
edge's effect that a later coded model can be checked against.

Rules:
- Estimate a POPULATION-level relative effect for the stratum. Never a patient value, never a
  diagnosis, never impute a missing datum.
- Ground the estimate in known physiology/literature; where evidence is thin, say so and widen the
  band and lower the confidence rather than overclaiming.
- The estimate is a HYPOTHESIS: it MUST ship a concrete falsification path (what observation or
  dataset would refute the direction or the band).
- Recommend the single modeling technique best suited to CODE this edge next (one of:
  compartmental_ode, linear_transfer, nonlinear_saturating, reaction_diffusion, analogy_transfer).

Output ONLY a JSON object, nothing else:
{
  "edge": "<restate the edge>",
  "direction": "increase" | "decrease" | "negligible",
  "relative_effect_band": [<low>, <high>],   // multiplicative effect on the target vs baseline=1.0
  "point": <number>,                          // your single best multiplier within the band
  "confidence": "low" | "medium" | "high",
  "rationale": "<2-4 sentences grounded in physiology/literature>",
  "falsification": "<the observation/dataset that would refute this>",
  "recommended_technique": "compartmental_ode" | "linear_transfer" | "nonlinear_saturating" | "reaction_diffusion" | "analogy_transfer"
}"""


def build_prompt(edge: dict) -> str:
    """Render the edge + structural stratum into the user message. `edge` carries:
    `name` (id), `description` (the coupling), `stratum` (bands/flags, no values), `gain` (shared
    inflammatory gain, pg/mL over basal), optional `coded_neighbors` (nearby coded edges for anchoring)."""
    payload = {
        "edge_name": edge["name"],
        "edge_description": edge["description"],
        "structural_stratum": edge.get("stratum", {}),
        "shared_inflammatory_gain_pg_ml": round(float(edge.get("gain", 0.0)), 4),
        "coded_neighbors": edge.get("coded_neighbors", []),
    }
    return ("Estimate this un-coded edge for the given stratum.\n\n"
            + json.dumps(payload, indent=2))


def _extract_json(text: str) -> dict:
    import re
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


def parse_estimate(text: str) -> dict:
    """Parse + validate the model's JSON estimate. Coerces the band to [lo, hi], clamps confidence,
    and requires a non-empty falsification path (the guardrail: no hypothesis without a refutation)."""
    est = _extract_json(text)
    band = est.get("relative_effect_band") or [est.get("point", 1.0)] * 2
    lo, hi = float(min(band)), float(max(band))
    conf = str(est.get("confidence", "low")).lower()
    if conf not in CONFIDENCE_WEIGHT:
        conf = "low"
    direction = str(est.get("direction", "negligible")).lower()
    if direction not in ("increase", "decrease", "negligible"):
        direction = "negligible"
    point = float(est.get("point", (lo + hi) / 2))
    falsification = str(est.get("falsification", "")).strip()
    if not falsification:
        raise ValueError("estimate rejected: no falsification path (a hypothesis must ship its refutation)")
    return {
        "edge": est.get("edge", ""),
        "direction": direction,
        "band": [round(lo, 4), round(hi, 4)],
        "point": round(point, 4),
        "confidence": conf,
        "rationale": str(est.get("rationale", "")).strip(),
        "falsification": falsification,
        "recommended_technique": str(est.get("recommended_technique", "compartmental_ode")),
    }


def to_member(estimate: dict, source: str) -> dict:
    """Convert a parsed estimate into a `blend_members` member dict: value = the point multiplier,
    weight = confidence-scaled (capped at CLAUDE_MEMBER_WEIGHT_CAP), tier `claude`, provenance kept."""
    weight = min(CONFIDENCE_WEIGHT[estimate["confidence"]], CLAUDE_MEMBER_WEIGHT_CAP)
    return {
        "value": estimate["point"],
        "weight": weight,
        "source": source,
        "tier": "claude",
        "band": estimate["band"],
        "confidence": estimate["confidence"],
        "direction": estimate["direction"],
        "falsification": estimate["falsification"],
        "recommended_technique": estimate["recommended_technique"],
    }


def _default_model_fn(model: str = "claude-opus-4-8") -> ModelFn:
    """Lazily build a Claude-backed model function (imports the SDK only when actually called)."""
    from .agent import _create_with_retry, load_dotenv

    load_dotenv()

    def call(user_text: str) -> str:
        import os

        import anthropic
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("ANTHROPIC_API_KEY is not set (add it to .env or the environment).")
        client = anthropic.Anthropic()
        resp = _create_with_retry(client, model=model, max_tokens=1500,
                                  system=SYSTEM_INSTRUCTION,
                                  messages=[{"role": "user", "content": user_text}])
        return next((b.text for b in resp.content if getattr(b, "type", None) == "text"), "")

    return call


def estimate_edge(edge: dict, source: Optional[str] = None,
                  model_fn: Optional[ModelFn] = None) -> dict:
    """Estimate one un-coded edge with Claude and return a ready-to-blend member. Inject `model_fn`
    (a `str->str` callable) in tests to run offline; in production it defaults to the Claude backend.
    The returned member is tier `claude`, weight-capped, and carries its falsification path."""
    fn = model_fn or _default_model_fn()
    text = fn(build_prompt(edge))
    estimate = parse_estimate(text)
    return to_member(estimate, source or edge["name"])
