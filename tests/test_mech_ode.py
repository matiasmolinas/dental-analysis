"""Tests for the mechanistic ODE toolkit (Phase 1) — pure python, no deps.

Verifies RK4 integration, steady-state finding, the finite-difference Jacobian, closed-form
eigenvalues (1x1/2x2) + stability, sensitivity, and sweep against analytically-known systems.

Run:  python tests/test_mech_ode.py
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.mech_ode import (
    eigenvalues,
    integrate,
    is_stable,
    jacobian,
    local_sensitivity,
    steady_state,
    stability_report,
    sweep,
)


def test_integrate_exponential_decay():
    # dy/dt = -k y, y(0)=1 -> y(t)=e^{-kt}
    f = lambda t, y, p: (-p["k"] * y[0],)
    ts, ys = integrate(f, (1.0,), 0.0, 1.0, 0.001, {"k": 2.0})
    assert abs(ys[-1][0] - math.exp(-2.0)) < 1e-5


def test_steady_state_of_turnover():
    # dy/dt = a - b y -> y* = a/b
    f = lambda t, y, p: (p["a"] - p["b"] * y[0],)
    y_ss = steady_state(f, (0.0,), {"a": 3.0, "b": 0.5})
    assert abs(y_ss[0] - 6.0) < 1e-3


def test_jacobian_linear_system():
    # f = (a*x + b*y, c*x + d*y) -> J = [[a,b],[c,d]] everywhere
    p = {"a": -1.0, "b": 2.0, "c": 0.5, "d": -3.0}
    f = lambda t, y, q: (q["a"] * y[0] + q["b"] * y[1], q["c"] * y[0] + q["d"] * y[1])
    J = jacobian(f, (1.0, 1.0), p)
    assert abs(J[0][0] - (-1.0)) < 1e-4 and abs(J[0][1] - 2.0) < 1e-4
    assert abs(J[1][0] - 0.5) < 1e-4 and abs(J[1][1] - (-3.0)) < 1e-4


def test_eigenvalues_1x1_and_2x2():
    assert abs(eigenvalues([[-0.5]])[0].real + 0.5) < 1e-12
    # [[0,1],[-1,0]] -> eigenvalues ±i
    eig = eigenvalues([[0.0, 1.0], [-1.0, 0.0]])
    assert all(abs(l.real) < 1e-9 for l in eig)
    assert abs(abs(eig[0].imag) - 1.0) < 1e-9


def test_eigenvalues_3x3_diagonal_and_stability():
    # diagonal 3x3 → eigenvalues are the diagonal entries (Stage-3: pure-python cubic solver)
    eig = sorted(l.real for l in eigenvalues([[-1.0, 0.0, 0.0], [0.0, -2.0, 0.0], [0.0, 0.0, -3.0]]))
    assert all(abs(a - b) < 1e-6 for a, b in zip(eig, [-3.0, -2.0, -1.0]))
    # a 3x3 with a known positive eigenvalue is unstable
    assert is_stable([[-1.0, 0.0, 0.0], [0.0, -2.0, 0.0], [0.0, 0.0, -3.0]]) is True
    assert is_stable([[2.0, 0.0, 0.0], [0.0, -2.0, 0.0], [0.0, 0.0, -3.0]]) is False


def test_eigenvalues_3x3_upper_triangular():
    # eigenvalues of a triangular matrix are its diagonal, even with off-diagonal coupling
    eig = sorted(l.real for l in eigenvalues([[-1.0, 5.0, 2.0], [0.0, -4.0, 3.0], [0.0, 0.0, -7.0]]))
    assert all(abs(a - b) < 1e-5 for a, b in zip(eig, [-7.0, -4.0, -1.0]))


def test_is_stable():
    assert is_stable([[-1.0, 0.0], [0.0, -2.0]]) is True
    assert is_stable([[1.0, 0.0], [0.0, -2.0]]) is False


def test_stability_report_stable_node():
    # dy/dt = a - b y is stable (eigenvalue -b)
    f = lambda t, y, p: (p["a"] - p["b"] * y[0],)
    p = {"a": 3.0, "b": 0.5}
    y_ss = steady_state(f, (0.0,), p)
    rep = stability_report(f, y_ss, p)
    assert rep["stable"] is True and rep["max_real_eig"] < 0


def test_local_sensitivity_sign():
    # output = a/b ; sensitivity to a is +1 (elasticity), to b is -1
    out_fn = lambda p: p["a"] / p["b"]
    s = local_sensitivity(out_fn, {"a": 3.0, "b": 0.5}, ["a", "b"])
    # a-elasticity exact (+1, linear); b-elasticity ~-1 with O(h^2) finite-diff error on 1/b
    assert abs(s["a"] - 1.0) < 1e-3 and abs(s["b"] + 1.0) < 3e-2


def test_sweep():
    res = sweep(lambda x: x * x, [1.0, 2.0, 3.0])
    assert res == [(1.0, 1.0), (2.0, 4.0), (3.0, 9.0)]


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
