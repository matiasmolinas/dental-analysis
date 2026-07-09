"""Tests for the learned-coordinator scaffold (Phase R6 #6) — no API, no GPU.

Verifies the tiny linear head + the separable ES converges on a mock objective (proving the
mechanism), and the head maps a state to a surface. Run: python tests/test_coordinator.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from coordinator import (
    SURFACES, SepES, choose_surface, head_param_dim, linear_head, train,
)


def test_linear_head_and_choice():
    feats = [1.0, 0.0]
    params = [0] * (len(SURFACES) * 2)
    params[2 * 2] = 1.0  # weight for surface index 2 on feature 0 -> that surface wins
    assert choose_surface(params, feats) == SURFACES[2]
    assert len(linear_head(params, feats, len(SURFACES))) == len(SURFACES)


def test_sepes_converges_on_quadratic():
    target = [1.5, -2.0, 0.5, 3.0]
    fitness = lambda p: -sum((p[i] - target[i]) ** 2 for i in range(len(target)))  # noqa: E731
    start_f = fitness([0.0] * len(target))  # ~-15.5
    best, best_f = train(fitness, dim=len(target), generations=100, popsize=24, seed=1)
    # the scaffold demonstrates the MECHANISM (a big improvement from the start), not
    # production-grade sep-CMA-ES precision — ~10x closer to the optimum is the honest claim
    assert best_f > start_f * 0.15, f"ES did not substantially improve: {best_f} from {start_f}"
    assert sum((best[i] - target[i]) ** 2 for i in range(len(target))) < 2.0  # near the optimum


def test_es_improves_from_offset_start():
    # optimum at 2.0 per dim; ES starts at mean=0 -> it must move toward the optimum
    fitness = lambda p: -sum((x - 2.0) ** 2 for x in p)  # noqa: E731
    es = SepES(dim=6, popsize=16, seed=2)
    first = fitness(es.mean)
    for _ in range(40):
        pop = es.ask(); es.tell([fitness(x) for x in pop])
    assert fitness(es.mean) > first + 5  # clearly moved toward the optimum


def test_head_param_dim():
    assert head_param_dim(5) == len(SURFACES) * 5


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn(); print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
