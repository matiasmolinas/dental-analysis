"""The model registry — the built sub-models, their tier, and how each couples to the shared gain.

The metadata layer that makes the harness an *ensemble* rather than one fixed model: each built
sub-model is registered with its axis, confidence tier, the parameter through which the shared
inflammatory `gain` enters it, and its citation (mirroring the `E-entry` catalog in
docs/model-library.md). `SWEPT_PARAMS` names the flagged/uncertain parameters the ensemble varies —
each with a plausible band around its nominal — so an ε/`gain` sweep propagates coherently and the
ensemble reports *ranges*, never points. Adding a new axis = adding one registry entry + its bounds.
"""

from __future__ import annotations

# name -> {axis, tier, kind, gain_param (the rate constant `gain` turns), citation}
#   kind = "coded"  — a pure-python ODE/PDE/network sub-model (validated/calibrated spine).
#          "claude" — a soft sub-model: a Claude subagent (with skills + the oral-systemic-kb) that
#                     returns a STRUCTURED estimate {value, band, confidence} for an edge that has no
#                     tractable equation, or a model-form weight when several coded forms are plausible.
#                     It enters the ensemble via BMA (`ensemble.blend_members`), tier-labeled and
#                     down-weighted vs the coded spine, gated by the non-diagnostic guardrail. It is a
#                     HYPOTHESIS with a falsification path, never a fitted result — used where the coded
#                     library cannot reach (novel edges, sparse-data couplings), NOT as a replacement.
SUBMODELS: dict[str, dict] = {
    "il6_crp_transducer": {"axis": "systemic", "tier": "core", "kind": "coded", "gain_param": None,
                           "citation": "Pepys & Hirschfield 2003 (E2.5)"},
    "cv_atherogenic_index": {"axis": "cardiovascular", "tier": "flagged", "kind": "coded",
                             "gain_param": "gamma_cv", "citation": "Ougrinovskaia 2010 (E2.6)"},
    "neuro_tau_spread": {"axis": "neuro", "tier": "flagged", "kind": "coded", "gain_param": "beta_tau",
                         "citation": "Fornari 2019 / Schäfer 2021 (E2.7→E2.8)"},
    "metabolic_insulin_resistance": {"axis": "metabolic", "tier": "flagged", "kind": "coded",
                                     "gain_param": "beta_si",
                                     "citation": "Bergman 1979 / Pritchard-Bell 2013 (E3.1/C4)"},
    # example slot for a Claude soft-model member of an un-coded edge (registered when instantiated):
    # "oral_gut_brain_estimate": {"axis":"neuro","tier":"claude","kind":"claude","gain_param":None,
    #                             "citation":"Claude reasoning over the oral-systemic KB + literature"},
}

# BMA weight ceiling for a Claude soft-model member relative to a coded spine member — a claude
# estimate never outweighs a calibrated/validated coded model.
CLAUDE_MEMBER_WEIGHT_CAP = 0.3

# The flagged/uncertain parameters the ensemble sweeps, each (lo, hi) around its nominal. ε is the
# calibrated spillover (swept within its anchor spread); gamma_cv and beta_tau are the imposed
# coupling constants (swept over plausible bands). These are exactly the "swept unknowns → ranges".
SWEPT_PARAMS: dict[str, tuple[float, float]] = {
    "epsilon": (0.5, 1.5),      # ×nominal (calibrated ε), reflecting the ΔCRP-anchor spread
    "gamma_cv": (0.025, 0.10),  # CV recruitment coupling per pg/mL (nominal 0.05)
    "beta_tau": (0.3, 1.5),     # inflammation→tau-α coupling (nominal 0.6)
    "beta_si": (0.075, 0.30),   # inflammation→insulin-resistance coupling (nominal 0.15)
}

# The ensemble's reported outputs (one envelope each over the sweep).
OUTPUTS = ("crp_mg_l", "cv_recruitment_multiplier", "tau_alpha_rel_increase",
           "tau_burden_rel_increase", "therapy_onset_delay_yr",
           "insulin_resistance_index", "hba1c_shift_pp")
