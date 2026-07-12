"""Tests for the neuro axis — neuroinflammation → tau spread (Phase 3) — pure python.

Verifies the coupling chain (systemic gain → neuroinflammation → tau-α), the closed-form tau
burden/onset, the Braak-ordered connectome front, the periodontal-therapy counterfactual, the
beta_tau sweep range, monotonicity in oral severity, and the non-diagnostic guardrail.

Run:  python tests/test_mech_neuro.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from histora.mech_neuro import (
    BRAAK_REGIONS,
    neuro_centerpiece,
    neuro_params,
    neuroinflammation,
    tau_alpha_effective,
    tau_burden_at,
    tau_front_arrival,
    tau_onset_time,
)

P = neuro_params()


def test_neuroinflammation_monotone_bounded_zero_at_zero():
    assert neuroinflammation(0.0, P) == 0.0
    assert neuroinflammation(1.0, P) < neuroinflammation(5.0, P)
    assert neuroinflammation(1e6, P) <= P["N_max"]


def test_alpha_effective_rises_with_inflammation():
    assert tau_alpha_effective(0.0, P) == P["alpha_tau"]
    assert tau_alpha_effective(0.5, P) > P["alpha_tau"]


def test_tau_burden_closed_form():
    c0 = P["tau_seed"]
    assert abs(tau_burden_at(0.03, 0.0, c0) - c0) < 1e-12          # c(0)=c0
    assert tau_burden_at(0.03, 100.0, c0) > tau_burden_at(0.03, 10.0, c0)   # grows in t
    assert tau_burden_at(0.05, 100.0, c0) > tau_burden_at(0.02, 100.0, c0)  # grows in α


def test_onset_time_decreases_with_alpha_and_none_if_unreachable():
    t_slow = tau_onset_time(0.02, 0.5, 0.05)
    t_fast = tau_onset_time(0.04, 0.5, 0.05)
    assert t_fast < t_slow
    assert tau_onset_time(0.0, 0.5, 0.05) is None      # no growth
    assert tau_onset_time(0.03, 0.5, 0.6) is None       # seed already past threshold


def test_connectome_front_respects_braak_order():
    arr = tau_front_arrival(0.025, P)
    times = [arr[r] for r in BRAAK_REGIONS]
    assert all(t is not None for t in times), arr
    # entorhinal <= hippocampus <= neocortex (front propagates along the chain)
    assert times[0] <= times[1] <= times[2]
    assert times[0] < times[2]


def test_neuro_centerpiece_monotone_in_oral_severity():
    low = neuro_centerpiece({"bop_band": "low", "comorbidities": []}, P)
    high = neuro_centerpiece({"bop_band": "high", "comorbidities": ["diabetes", "smoking"],
                              "perio_stage": "stage IV"}, P)
    assert high["neuroinflammation"] > low["neuroinflammation"]
    assert high["tau_alpha"]["relative_increase"] > low["tau_alpha"]["relative_increase"]
    assert high["tau_burden_horizon"]["relative_increase"] > low["tau_burden_horizon"]["relative_increase"]


def test_therapy_delays_onset_and_sweep_gives_range():
    r = neuro_centerpiece({"bop_band": "high", "comorbidities": []}, P)
    # therapy (remove oral source) delays tau threshold crossing by a positive amount
    assert r["tau_onset_years"]["therapy_delay_years"] > 0
    # sweeping the flagged coupling yields a genuine range (lo < hi)
    lo, hi = r["tau_burden_range_over_beta"]
    assert lo < hi
    assert len(r["beta_tau_sweep"]) == 4


def test_amyloid_arm_and_apoe4_age_modifiers():
    base = {"bop_band": "high", "perio_stage": "stage III"}
    plain = neuro_centerpiece(base, front=False)
    apoe4 = neuro_centerpiece({**base, "apoe4": True}, front=False)
    old = neuro_centerpiece({**base, "age_band": "old"}, front=False)
    both = neuro_centerpiece({**base, "apoe4": True, "age_band": "old"}, front=False)
    # the amyloid arm exists and rises with oral inflammation
    assert plain["amyloid_burden"]["with_oral_inflammation"] > 0
    # APOE4 and age each raise amyloid; together most of all (effect modifiers)
    a = lambda r: r["amyloid_burden"]["with_oral_inflammation"]
    assert a(apoe4) > a(plain) and a(old) > a(plain)
    assert a(both) > a(apoe4) and a(both) > a(old)
    # APOE4/age also raise tau-α (amyloid → tau-α edge)
    assert both["tau_alpha"]["relative_increase"] > plain["tau_alpha"]["relative_increase"]
    # modifiers are structural flags/bands, not patient values
    assert apoe4["modifiers"]["apoe4"] is True and old["modifiers"]["age_band"] == "old"


def test_flags_and_non_diagnostic():
    r = neuro_centerpiece({"bop_band": "high"}, P)
    assert r["confidence"] == "scaffold"
    assert any("atuzaginstat" in f for f in r["flags"])
    # numeric patient values in features are ignored by the structural source (guardrail)
    a = neuro_centerpiece({"bop_band": "high", "comorbidities": ["diabetes"]}, P)["neuroinflammation"]
    b = neuro_centerpiece({"bop_band": "high", "comorbidities": ["diabetes"],
                           "bop_pct": 47, "hba1c": 8.1}, P)["neuroinflammation"]
    assert a == b


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
