"""Mechanistic-modeling toolkit — the numerical core.

Pure-Python primitives to *run* mechanistic models, not just describe them: integrate ODE
systems, find steady states, compute the Jacobian + stability (eigenvalues), local sensitivity,
and parameter sweeps. `jacobian()` is the classical dynamical-systems Jacobian ∂(dy_i/dt)/∂y_j of
a biological ODE, evaluated at a fixed point for stability (eigenvalue) analysis — variables are
IL-6, CRP, tau, etc. No hard scientific-stack dependency; numpy is used only as an optional
accelerator for eigenvalues of systems larger than 2x2 (the centerpiece models are <=2-D, so the
closed-form path needs nothing installed).

State y is a tuple/list of floats; a right-hand side is f(t, y, p) -> tuple of dy/dt, where
p is a params dict. Everything here is deterministic — the modeling layer is code the agent
calls as tools, so it is fully testable offline. See mech_models.py for the specific
oral-systemic models and docs/model-library.md for the science + citations.
"""

from __future__ import annotations

import cmath
import math
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


def _cubic_roots(a: float, b: float, c: float, d: float) -> list[complex]:
    """The three (possibly complex) roots of a·x³+b·x²+c·x+d — Cardano's method, pure-python. Used to
    get 3x3 eigenvalues (via the characteristic polynomial) with no scientific stack, so the Stage-3
    3-D mechanistic models (inflammation, atherosclerosis) get a stability verdict like the ≤2-D spine."""
    if abs(a) < 1e-14:                                  # degenerate → quadratic
        disc = cmath.sqrt(c * c - 4 * b * d)
        return [(-c + disc) / (2 * b), (-c - disc) / (2 * b)] if abs(b) > 1e-14 else [complex(-d / c)]
    b, c, d = b / a, c / a, d / a                       # monic x³+bx²+cx+d
    p = c - b * b / 3.0
    q = 2 * b ** 3 / 27.0 - b * c / 3.0 + d
    shift = -b / 3.0
    u = cmath.sqrt((q / 2) ** 2 + (p / 3) ** 3)
    A = (-q / 2 + u) ** (1 / 3)
    B = -(p / 3) / A if abs(A) > 1e-14 else 0.0
    w = complex(-0.5, math.sqrt(3) / 2)                 # primitive cube root of unity
    return [A + B + shift, A * w + B * w.conjugate() + shift, A * w.conjugate() + B * w + shift]


def eigenvalues(J: list[list[float]]) -> list[complex]:
    """Eigenvalues of a small matrix. Closed-form for 1x1/2x2/3x3 (no dependency, via the characteristic
    polynomial + a pure-python cubic solver); numpy for larger if available, else a clear error."""
    n = len(J)
    if n == 1:
        return [complex(J[0][0])]
    if n == 2:
        a, b = J[0]
        c, d = J[1]
        tr, det = a + d, a * d - b * c
        disc = cmath.sqrt(tr * tr - 4 * det)
        return [(tr + disc) / 2, (tr - disc) / 2]
    if n == 3:
        # char. poly of a 3x3: λ³ − tr·λ² + (Σ principal 2x2 minors)·λ − det = 0
        (a11, a12, a13), (a21, a22, a23), (a31, a32, a33) = J[0], J[1], J[2]
        tr = a11 + a22 + a33
        minors = (a11 * a22 - a12 * a21) + (a11 * a33 - a13 * a31) + (a22 * a33 - a23 * a32)
        det = (a11 * (a22 * a33 - a23 * a32) - a12 * (a21 * a33 - a23 * a31)
               + a13 * (a21 * a32 - a22 * a31))
        return _cubic_roots(1.0, -tr, minors, -det)
    try:
        import numpy as _np
        return [complex(v) for v in _np.linalg.eigvals(_np.array(J, dtype=float))]
    except ImportError as e:  # pragma: no cover - env-dependent
        raise ValueError("eigenvalues for n>3 need numpy; models here are <=3-D") from e


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
