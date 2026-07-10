"""Mechanistic-modeling toolkit — the numerical core (Harness 1, Phase 1).

Pure-Python primitives an agent uses to *run* mechanistic models, not just describe them:
integrate ODE systems, find steady states, compute Jacobians + stability (eigenvalues),
local sensitivity, and parameter sweeps.

TERMINOLOGY — this "Jacobian" is NOT the paper's "Jacobian lens". Here `jacobian()` is the
classical dynamical-systems Jacobian ∂(dy_i/dt)/∂y_j of a BIOLOGICAL ODE model, evaluated at a
fixed point for stability (eigenvalue) analysis — variables are IL-6, CRP, tau, etc. The
Anthropic "Jacobian lens" (the §0 investigation) is a linearization of the LLM's own
computation, ∂(readout)/∂(activations) — an interpretability instrument on the model's internal
workspace. Same word, different object: this one lives INSIDE the disease model the agent
builds; the lens lives inside the model doing the building. They meet only in Phase 2 (the fair
lens re-test), at two different levels, never as the same matrix. No hard scientific-stack dependency (matches the
project's pure-python, no-GPU harness ethos); numpy is used only as an optional accelerator
for eigenvalues of systems larger than 2x2 (our centerpiece models are <=2-D, so the
closed-form path needs nothing installed).

State y is a tuple/list of floats; a right-hand side is f(t, y, p) -> tuple of dy/dt, where
p is a params dict. Everything here is deterministic — the modeling layer is code the agent
calls as tools, so it is fully testable offline. See mech_models.py for the specific
oral-systemic models and docs/model-library.md for the science + citations.
"""

from __future__ import annotations

import cmath
from typing import Any, Callable

RHS = Callable[[float, tuple, dict], tuple]


def integrate(f: RHS, y0, t0: float, t1: float, dt: float, p: dict) -> tuple[list, list]:
    """Fixed-step RK4 integration of dy/dt = f(t, y, p) from t0 to t1. Returns (ts, ys)."""
    n = max(1, int(round((t1 - t0) / dt)))
    y = list(y0)
    ts, ys = [t0], [tuple(y)]
    t = t0
    for _ in range(n):
        k1 = f(t, y, p)
        k2 = f(t + dt / 2, [yi + dt / 2 * k1i for yi, k1i in zip(y, k1)], p)
        k3 = f(t + dt / 2, [yi + dt / 2 * k2i for yi, k2i in zip(y, k2)], p)
        k4 = f(t + dt, [yi + dt * k3i for yi, k3i in zip(y, k3)], p)
        y = [yi + dt / 6 * (a + 2 * b + 2 * c + d)
             for yi, a, b, c, d in zip(y, k1, k2, k3, k4)]
        t += dt
        ts.append(t)
        ys.append(tuple(y))
    return ts, ys


def steady_state(f: RHS, y0, p: dict, dt: float = 0.5, t_max: float = 5000.0,
                 tol: float = 1e-8) -> tuple:
    """Integrate to equilibrium: stop when the derivative norm falls below tol (relative to
    the state scale) or t_max is reached. Returns the steady-state y."""
    y = list(y0)
    t = 0.0
    steps = max(1, int(round(t_max / dt)))
    for _ in range(steps):
        dy = f(t, y, p)
        scale = 1.0 + max(abs(v) for v in y)
        if max(abs(d) for d in dy) / scale < tol:
            break
        # one RK4 step
        _, ys = integrate(f, y, t, t + dt, dt, p)
        y = list(ys[-1])
        t += dt
    return tuple(y)


def jacobian(f: RHS, y, p: dict, t: float = 0.0, eps: float = 1e-6) -> list[list[float]]:
    """Finite-difference Jacobian ∂f_i/∂y_j at state y (central differences)."""
    n = len(y)
    J = [[0.0] * n for _ in range(n)]
    for j in range(n):
        yp, ym = list(y), list(y)
        h = eps * (1.0 + abs(y[j]))
        yp[j] += h
        ym[j] -= h
        fp = f(t, yp, p)
        fm = f(t, ym, p)
        for i in range(n):
            J[i][j] = (fp[i] - fm[i]) / (2 * h)
    return J


def eigenvalues(J: list[list[float]]) -> list[complex]:
    """Eigenvalues of a small matrix. Closed-form for 1x1 and 2x2 (no dependency); numpy for
    larger if available, else a clear error. Our mechanistic models are <=2-D."""
    n = len(J)
    if n == 1:
        return [complex(J[0][0])]
    if n == 2:
        a, b = J[0]
        c, d = J[1]
        tr, det = a + d, a * d - b * c
        disc = cmath.sqrt(tr * tr - 4 * det)
        return [(tr + disc) / 2, (tr - disc) / 2]
    try:
        import numpy as _np
        return [complex(v) for v in _np.linalg.eigvals(_np.array(J, dtype=float))]
    except ImportError as e:  # pragma: no cover - env-dependent
        raise ValueError("eigenvalues for n>2 need numpy; models here are <=2-D") from e


def is_stable(J: list[list[float]]) -> bool:
    """A fixed point is (locally) stable iff every eigenvalue has negative real part."""
    return all(lam.real < 0 for lam in eigenvalues(J))


def stability_report(f: RHS, y_ss, p: dict) -> dict[str, Any]:
    """Jacobian + eigenvalues + stability verdict at a steady state — the sympy-style
    equilibrium analysis, done numerically."""
    J = jacobian(f, y_ss, p)
    eig = eigenvalues(J)
    return {
        "steady_state": list(y_ss),
        "jacobian": J,
        "eigenvalues": [[lam.real, lam.imag] for lam in eig],
        "stable": all(lam.real < 0 for lam in eig),
        "max_real_eig": max(lam.real for lam in eig),
    }


def local_sensitivity(output_fn: Callable[[dict], float], base_p: dict, keys: list[str],
                      frac: float = 0.1) -> dict[str, float]:
    """One-at-a-time local sensitivity: fractional change in the scalar output per fractional
    change in each parameter (a normalized elasticity, central difference). `output_fn(p)`
    returns the scalar of interest given a params dict."""
    base = output_fn(base_p)
    out = {}
    for k in keys:
        if not isinstance(base_p.get(k), (int, float)) or base_p[k] == 0:
            continue
        pp, pm = dict(base_p), dict(base_p)
        h = frac * base_p[k]
        pp[k] = base_p[k] + h
        pm[k] = base_p[k] - h
        d_out = (output_fn(pp) - output_fn(pm)) / (2 * h)
        # normalized elasticity: (dOut/Out)/(dP/P); falls back to raw slope if base==0
        out[k] = round(d_out * base_p[k] / base, 4) if base else round(d_out, 6)
    return out


def sweep(output_fn: Callable[[float], Any], values: list[float]) -> list[tuple]:
    """Evaluate output_fn across a list of parameter values → [(value, output), ...]. The
    parameter-range primitive behind 'sweep the epistemic-risk parameter, report a range'."""
    return [(v, output_fn(v)) for v in values]
