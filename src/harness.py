"""J-lens diagnostic harness for the oral-systemic input-format optimization loop.

Reads out, for each candidate input format, the minimum vocabulary rank of every
target bridge concept within the model's workspace band. A low rank means the
concept is represented internally and is available for verbal report; a high or
absent rank means the format fails to make that relation representable.

Requires a GPU (run in Colab). Depends on the `jlens` package from the
jacobian-lens repo: `pip install -e jacobian-lens`.
"""

from __future__ import annotations

import math
from typing import Any

from bridge_concepts import BRIDGE_CONCEPTS, MEDIATOR_KEYS
from record_formats import DATA_ITEMS


def single_token_id(tokenizer: Any, surface: str) -> int | None:
    """Return the token id if `surface` (with or without a leading space) encodes
    to exactly one token, else None. Multi-token surfaces are not directly
    measurable by the lens (it reads one vocabulary token per direction)."""
    for candidate in (" " + surface, surface):
        ids = tokenizer.encode(candidate, add_special_tokens=False)
        if len(ids) == 1:
            return ids[0]
    return None


def workspace_band(model: Any, lens: Any, lo: float = 0.33, hi: float = 0.66) -> list[int]:
    """Fitted layers whose depth fraction lies in the mid-network workspace band.
    Calibrate [lo, hi] once per model with `sweep_layers`."""
    return [l for l in lens.source_layers if lo <= l / model.n_layers <= hi]


def concept_ranks(
    model: Any,
    lens: Any,
    tokenizer: Any,
    prompt: str,
    band: list[int],
    tail_tokens: int = 40,
) -> dict[str, dict]:
    """Minimum lens rank of each bridge concept over the workspace band and the
    last `tail_tokens` positions (the question / answer span)."""
    lens_logits, _, input_ids = lens.apply(model, prompt, layers=band, positions=None)
    seq = input_ids.shape[-1]
    tail = list(range(max(0, seq - tail_tokens), seq))
    out: dict[str, dict] = {}
    for name, surfaces in BRIDGE_CONCEPTS.items():
        best, best_surface = math.inf, None
        for s in surfaces:
            tid = single_token_id(tokenizer, s)
            if tid is None:
                continue
            for l in band:
                sub = lens_logits[l][tail]  # [n_tail, vocab]
                ranks = (sub > sub[:, tid : tid + 1]).sum(dim=1)  # rank per position
                r = int(ranks.min())
                if r < best:
                    best, best_surface = r, s
        out[name] = {
            "min_rank": best,
            "surface": best_surface,
            "hit_at_1": best == 0,
            "hit_at_10": best < 10,
        }
    return out


def capacity(
    model: Any,
    lens: Any,
    tokenizer: Any,
    prompt: str,
    band: list[int],
    k: int = 25,
    tail_tokens: int = 60,
) -> tuple[int, int]:
    """How many key patient data items remain reachable (band-min rank < k)."""
    lens_logits, _, ids = lens.apply(model, prompt, layers=band, positions=None)
    seq = ids.shape[-1]
    tail = list(range(max(0, seq - tail_tokens), seq))
    reachable = 0
    measured = 0
    for item in DATA_ITEMS:
        tid = single_token_id(tokenizer, item)
        if tid is None:
            continue
        measured += 1
        best = min(
            int((lens_logits[l][tail] > lens_logits[l][tail][:, tid : tid + 1]).sum(1).min())
            for l in band
        )
        reachable += best < k
    return reachable, measured


def sweep_layers(
    model: Any,
    lens: Any,
    tokenizer: Any,
    prompt: str,
    surface: str,
    tail_tokens: int = 40,
) -> dict[int, int]:
    """Min rank of one surface at every fitted layer, to calibrate the band."""
    tid = single_token_id(tokenizer, surface)
    if tid is None:
        raise ValueError(f"{surface!r} is not a single token for this model")
    lens_logits, _, ids = lens.apply(model, prompt, layers=lens.source_layers, positions=None)
    seq = ids.shape[-1]
    tail = list(range(max(0, seq - tail_tokens), seq))
    return {
        l: int((lens_logits[l][tail] > lens_logits[l][tail][:, tid : tid + 1]).sum(1).min())
        for l in lens.source_layers
    }


def summarize(name: str, ranks: dict[str, dict]) -> str:
    """One-line summary line plus mediator ranks for a format."""
    hits = sum(v["hit_at_10"] for v in ranks.values())
    mediator_ranks = sorted(ranks[c]["min_rank"] for c in MEDIATOR_KEYS)
    return f"{name}: hit@10={hits}/{len(ranks)}  mediator_ranks={mediator_ranks}"
