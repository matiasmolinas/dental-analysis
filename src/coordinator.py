# EXTERNAL / scaffold — not run in the Claude-only pipeline; speculative (see docs/RESEARCH_SUMMARY.md)
"""Learned coordinator scaffold (Phase R6 next-step #6) — Trinity/Conductor-style, offline.

The mechanism/burden-of-proof analyses concluded the bottleneck is a HAND-DESIGNED actuator, and that
the fix is a LEARNED map from the full problem state -> which surface to edit — trained with an
evolution strategy (sep-CMA-ES), NOT RL (the Trinity paper shows RL fails on this low-SNR,
weak-coupling, high-per-step-cost regime). The lens is ONE feature of the state, privileged because it
is non-redundant with the output.

This module is the SCAFFOLD: a tiny linear head (state-feature vector -> surface-choice logits) and a
minimal separable evolution strategy that trains it against a pluggable fitness function. Offline and
testable with a mock objective; the live fitness (a bounded rollout of an edit on Claude scored by
relational_recall + counterfactual sensitivity, guardrail as a hard gate) is future work — plug it in
as `fitness_fn`. This proves the architecture is real without the expensive live training loop.
"""

from __future__ import annotations

import random
from typing import Callable

SURFACES = ["work_prompt", "skill", "kb_context", "injected_variables", "subagent_def", "harness_code"]


def linear_head(params: list[float], features: list[float], n_out: int) -> list[float]:
    """logits = W @ features, W flattened row-major in `params` (n_out x n_feat). The head is tiny
    (~n_out*n_feat weights) — the Trinity insight: a small learned head over a rich state suffices."""
    n_feat = len(features)
    assert len(params) == n_out * n_feat, "params size mismatch"
    return [sum(params[o * n_feat + j] * features[j] for j in range(n_feat)) for o in range(n_out)]


def choose_surface(params: list[float], features: list[float]) -> str:
    logits = linear_head(params, features, len(SURFACES))
    return SURFACES[max(range(len(logits)), key=lambda i: logits[i])]


class SepES:
    """A minimal separable (diagonal-covariance) evolution strategy — the essence of sep-CMA-ES:
    per-dimension step sizes, (mu/mu, lambda) recombination. Suited to the low-SNR / weak-coupling
    regime where RL is ill-conditioned. Seeded for reproducibility."""

    def __init__(self, dim: int, popsize: int = 16, mu: int | None = None, sigma0: float = 0.5,
                 seed: int = 0):
        self.dim = dim
        self.lam = popsize
        self.mu = mu or max(1, popsize // 2)
        self.mean = [0.0] * dim
        self.sigma = [sigma0] * dim
        self.rng = random.Random(seed)

    def ask(self) -> list[list[float]]:
        self._pop = [[self.mean[d] + self.sigma[d] * self.rng.gauss(0, 1) for d in range(self.dim)]
                     for _ in range(self.lam)]
        return self._pop

    def tell(self, fitnesses: list[float]) -> None:
        # higher fitness = better; recombine the top mu, adapt sigma to their spread around the new mean
        order = sorted(range(self.lam), key=lambda i: fitnesses[i], reverse=True)[: self.mu]
        sel = [self._pop[i] for i in order]
        new_mean = [sum(x[d] for x in sel) / self.mu for d in range(self.dim)]
        for d in range(self.dim):
            std = (sum((x[d] - new_mean[d]) ** 2 for x in sel) / self.mu) ** 0.5
            # track the selected spread (diagonal step size), floored to keep some exploration
            self.sigma[d] = max(1e-4, 0.5 * self.sigma[d] + 0.5 * (std + 1e-6))
        self.mean = new_mean


def train(fitness_fn: Callable[[list[float]], float], dim: int, generations: int = 60,
          popsize: int = 16, seed: int = 0) -> tuple[list[float], float]:
    """Evolve head params to maximize fitness_fn. Returns (best_params, best_fitness)."""
    es = SepES(dim, popsize=popsize, seed=seed)
    best, best_f = list(es.mean), fitness_fn(es.mean)
    for _ in range(generations):
        pop = es.ask()
        fits = [fitness_fn(p) for p in pop]
        es.tell(fits)
        i = max(range(len(pop)), key=lambda k: fits[k])
        if fits[i] > best_f:
            best, best_f = list(pop[i]), fits[i]
    return best, best_f


def head_param_dim(n_features: int) -> int:
    return len(SURFACES) * n_features
