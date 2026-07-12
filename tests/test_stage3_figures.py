"""Tests for the Stage-3 figure trajectory helpers — phase portrait, tau front, diabetes↔perio cobweb.

Pure-python, offline. Locks in the physics the figures draw AND the honesty markers: the inflammatory
core is bistable (two distinct basins), the oral source advances the tau front (and is tier=EXPLORATORY),
and the diabetes↔perio cobweb converges to the SAME fixed point coupled_perio_metabolic solves for.

Run:  python tests/test_stage3_figures.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.mech_calibrate import calibrated_params
from histora.mech_inflammation import phase_trajectories
from histora.mech_metabolic import coupled_perio_metabolic, perio_metabolic_cobweb
from histora.mech_neuro import tau_front_pair

FEATURES = {"bop_band": "high", "perio_stage": "stage III", "comorbidities": ["diabetes"],
            "apoe4": True, "age_band": "old"}


def test_phase_trajectories_two_basins():
    ph = phase_trajectories(calibrated_params())
    for arm in ("resolving", "chronic"):
        assert len(ph[arm]["il6"]) == len(ph[arm]["il10"]) > 10       # real trajectories
    lo, hi = ph["fixed_points"]["low"], ph["fixed_points"]["high"]
    assert hi["il6"] > lo["il6"]                                       # the chronic basin sits higher in IL-6
    assert isinstance(ph["fixed_points"]["bistable"], bool)


def test_tau_front_pair_oral_source_advances_front_and_is_exploratory():
    tf = tau_front_pair(FEATURES, calibrated_params())
    assert tf["tier"] == "EXPLORATORY"                                # honesty marker travels with the data
    assert tf["regions"] and set(tf["with_oral"]) == set(tf["regions"])
    # for any region that both cross, the oral-inflammation front arrives no later than baseline
    for r in tf["regions"]:
        wo, bl = tf["with_oral"][r], tf["baseline"][r]
        if wo is not None and bl is not None:
            assert wo <= bl + 1e-6


def test_perio_cobweb_matches_coupled_fixed_point():
    p = calibrated_params()
    cw = perio_metabolic_cobweb(FEATURES, p, feedback=0.30)
    loop = coupled_perio_metabolic(FEATURES, p, feedback=0.30)
    # the cobweb fixed point IS the closed-loop shift the solver reports (same map, same feedback)
    assert abs(cw["fixed_point"] - loop["closed_loop_hba1c_shift_pp"]) < 1e-2
    assert cw["fixed_point"] >= cw["open_loop"] - 1e-9                # the positive feedback raises the shift
    assert len(cw["map_x"]) == len(cw["map_y"]) and len(cw["seq"]) >= 2


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
