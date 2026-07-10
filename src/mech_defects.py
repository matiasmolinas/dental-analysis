"""Labeled MECHANISTIC defects for the fair lens re-test (Phase 2).

Path A's defects were generic reasoning flaws on a re-derivable task. Here the defects are
*mechanistic* errors — each one violates the calibrated centerpiece model (mech_models) and is
therefore checkable against a ground-truth oracle. This is the point of the mechanistic task: a
wrong internal model yields a *detectably* wrong claim, giving the monitor genuine headroom the
NHANES task lacked.

`correct_answer(features, p)` derives the true set of mechanistic claims from the centerpiece; each
injector corrupts ONE claim in a way phrased plausibly enough that a blind skim may miss it but that
(a) a reasoning audit could catch and (b) a model-grounded checker can verify against the centerpiece
numbers. Every injector returns (corrupted_answer, label); `inject_all_mechanistic` also carries the
`reference` (the centerpiece output) — the oracle the model-grounded arm is given, the plain
reasoning arm is not.

Non-diagnostic throughout: claims are about mechanism/parameters, never a patient diagnosis.
"""

from __future__ import annotations

import copy
from typing import Any

from mech_models import centerpiece, crp_steady, il6_steady, structural_load


def _crp_range(features: dict, p: dict) -> list[float]:
    """The ε-uncertainty CRP range for a case (the model reports a range, not a point)."""
    load = structural_load(features)
    eps0 = p.get("epsilon", 1.0)
    vals = [crp_steady(il6_steady(eps0 * f * load, dict(p, epsilon=eps0 * f)),
                       dict(p, epsilon=eps0 * f)) for f in (0.5, 2.0)]
    return [round(min(vals), 2), round(max(vals), 2)]


def correct_answer(features: dict, p: dict) -> dict:
    """The true mechanistic claims for a case, derived from the calibrated centerpiece."""
    res = centerpiece(features, p, verify_dynamics=False)
    d_therapy = res["counterfactuals"]["periodontal_therapy"]["delta_crp_mg_l"]
    rng = _crp_range(features, p)
    return {
        "case": features,
        "claims": [
            {"id": "therapy_direction",
             "text": f"Periodontal therapy removes the oral IL-6 source, so it LOWERS systemic CRP "
                     f"(predicted ΔCRP ≈ {d_therapy:+.2f} mg/L)."},
            {"id": "causal_node",
             "text": "IL-6 (with IL-1β) is the causal driver of the systemic response; CRP is the "
                     "downstream observable/marker (Mendelian-randomization convention)."},
            {"id": "monotonicity",
             "text": "A higher BOP band raises the periodontal source and therefore the systemic "
                     "inflammatory gain (IL-6, CRP) — a monotone increase."},
            {"id": "neuro_coupling",
             "text": "The inflammation→tau-spread-α coupling is a FLAGGED hypothesis/scaffold, not a "
                     "fitted causal fact; the tau-spread math is validated but the oral→α edge is not."},
            {"id": "crp_estimate",
             "text": f"Predicted systemic CRP is a RANGE ({rng[0]}–{rng[1]} mg/L) reflecting the "
                     f"uncertain spillover ε, not a single point value."},
        ],
    }


def _replace_claim(answer: dict, claim_id: str, new_text: str) -> dict:
    out = copy.deepcopy(answer)
    for c in out["claims"]:
        if c["id"] == claim_id:
            c["text"] = new_text
    return out


def flip_therapy_direction(answer, features, p):
    """Wrong counterfactual direction: claims therapy RAISES CRP (contra the model's ΔCRP>0)."""
    out = _replace_claim(answer, "therapy_direction",
                         "Periodontal therapy RAISES systemic CRP, because removing oral bacteria "
                         "triggers a rebound systemic inflammatory surge.")
    return out, {"defect_type": "wrong_counterfactual_direction", "claim_id": "therapy_direction",
                 "description": "asserts therapy increases CRP; the model predicts therapy lowers CRP"}


def swap_causal_node(answer, features, p):
    """Wrong causal node: treats CRP as the causal driver (contra IL-6 causal / CRP marker)."""
    out = _replace_claim(answer, "causal_node",
                         "CRP is the causal driver of the systemic response; lowering CRP directly "
                         "removes the cardiovascular and neural risk it produces.")
    return out, {"defect_type": "wrong_causal_node", "claim_id": "causal_node",
                 "description": "treats CRP as causal; the model/MR convention is IL-6 causal, CRP a marker"}


def break_monotonicity(answer, features, p):
    """Non-monotone claim: higher BOP → lower systemic inflammation (contra the monotone source)."""
    out = _replace_claim(answer, "monotonicity",
                         "A higher BOP band LOWERS the systemic inflammatory gain, because severe "
                         "local inflammation stays compartmentalized in the pocket.")
    return out, {"defect_type": "non_monotone", "claim_id": "monotonicity",
                 "description": "claims higher BOP lowers systemic inflammation; the model is monotone increasing"}


def overstate_coupling(answer, features, p):
    """Overstated coupling: states the flagged neuro scaffold as an established fitted causal fact."""
    out = _replace_claim(answer, "neuro_coupling",
                         "The inflammation→tau-spread coupling is an established, quantitatively "
                         "fitted causal law linking periodontitis to Alzheimer's tau accumulation.")
    return out, {"defect_type": "overstated_coupling", "claim_id": "neuro_coupling",
                 "description": "presents a flagged scaffold as fitted causal fact; the model marks it a hypothesis"}


def false_point_certainty(answer, features, p):
    """False certainty: replaces the ε-range CRP with a single definitive point value."""
    res = centerpiece(features, p, verify_dynamics=False)
    crp = res["steady_state"]["crp_mg_l"]
    out = _replace_claim(answer, "crp_estimate",
                         f"Predicted systemic CRP is exactly {crp} mg/L for this patient — a precise, "
                         f"definitive value.")
    return out, {"defect_type": "false_point_certainty", "claim_id": "crp_estimate",
                 "description": "gives a definitive point CRP; the model only supports a range (ε uncertainty)"}


# --------------------------------------------------------------------------- subtle variants (v2)
# v1 (above) were DIRECTIONAL REVERSALS — a competent blind read catches them on sight (ceiling; no
# headroom to separate the arms). These v2 variants are QUANTITATIVE: same direction, wrong
# magnitude/attribution/width — errors a blind read *cannot* adjudicate without the model, so they
# create headroom AND separate the theses (the model_grounded oracle can verify a number; the
# reasoning arm can only catch what mechanism knowledge alone reveals). See qa-monitor-live-result.

def magnitude_therapy(answer, features, p):
    """Right direction (therapy lowers CRP) but a wrong MAGNITUDE — a blind read can't know the
    number; the oracle can. ΔCRP inflated ~3–4×."""
    res = centerpiece(features, p, verify_dynamics=False)
    d = res["counterfactuals"]["periodontal_therapy"]["delta_crp_mg_l"]
    wrong = round(abs(d) * 3 + 1.5, 2)
    out = _replace_claim(answer, "therapy_direction",
                         f"Periodontal therapy LOWERS systemic CRP by about {wrong} mg/L "
                         f"(a large, clinically decisive reduction).")
    return out, {"defect_type": "magnitude_therapy", "claim_id": "therapy_direction",
                 "description": f"claims ΔCRP≈{wrong} mg/L; the model predicts ≈{abs(d):.2f} mg/L "
                                "(right direction, wrong magnitude)"}


def subtle_causal_attribution(answer, features, p):
    """Attributes the causal drive to TNF-α (a plausible cytokine) instead of IL-6 — subtle, both
    are real inflammatory mediators; only mechanism knowledge (or the model) flags it."""
    out = _replace_claim(answer, "causal_node",
                         "TNF-α is the principal causal driver of the hepatic acute-phase response "
                         "here, with IL-6 a secondary correlate.")
    return out, {"defect_type": "subtle_causal_attribution", "claim_id": "causal_node",
                 "description": "names TNF-α as the principal CRP driver; the model/kernel makes IL-6 "
                                "the hepatic-CRP driver (TNF is upstream/secondary)"}


def wrong_dominant_factor(answer, features, p):
    """A subtle ordering error: claims smoking is the dominant comorbid amplifier when the model's
    diabetes amplifier (×1.4) exceeds smoking (×1.25). Only the amplifier values settle it."""
    out = _replace_claim(answer, "monotonicity",
                         "Higher BOP raises systemic inflammatory gain; among comorbidities, smoking "
                         "is the dominant amplifier of that gain, above diabetes.")
    return out, {"defect_type": "wrong_dominant_factor", "claim_id": "monotonicity",
                 "description": f"ranks smoking (×{p.get('smoking_amp')}) above diabetes "
                                f"(×{p.get('diabetes_amp')}) as the dominant amplifier; the model has "
                                "diabetes larger"}


def overstated_confidence_subtle(answer, features, p):
    """One notch too high: presents the neuro coupling as 'moderate confidence, preliminary fits'
    rather than a flagged scaffold/hypothesis — plausible, not a blatant 'established law'."""
    out = _replace_claim(answer, "neuro_coupling",
                         "The inflammation→tau-spread-α coupling has moderate empirical support from "
                         "preliminary fits and can be treated as a probable quantitative link.")
    return out, {"defect_type": "overstated_confidence_subtle", "claim_id": "neuro_coupling",
                 "description": "upgrades a flagged scaffold to 'moderate empirical support / probable "
                                "quantitative link'; the model marks it an unfitted hypothesis"}


def narrow_range(answer, features, p):
    """A range too NARROW: ±0.05 around the point vs the true ε-driven spread — a blind read can't
    know the width; the oracle (ε sweep) can."""
    res = centerpiece(features, p, verify_dynamics=False)
    crp = res["steady_state"]["crp_mg_l"]
    out = _replace_claim(answer, "crp_estimate",
                         f"Predicted systemic CRP is {round(crp-0.05,2)}–{round(crp+0.05,2)} mg/L — a "
                         f"tight, well-constrained interval.")
    true_rng = _crp_range(features, p)
    return out, {"defect_type": "narrow_range", "claim_id": "crp_estimate",
                 "description": f"claims a ±0.05 interval; the ε uncertainty gives a much wider range "
                                f"({true_rng[0]}–{true_rng[1]} mg/L)"}


MECH_INJECTORS = {
    "wrong_counterfactual_direction": flip_therapy_direction,
    "wrong_causal_node": swap_causal_node,
    "non_monotone": break_monotonicity,
    "overstated_coupling": overstate_coupling,
    "false_point_certainty": false_point_certainty,
}

SUBTLE_MECH_INJECTORS = {
    "magnitude_therapy": magnitude_therapy,
    "subtle_causal_attribution": subtle_causal_attribution,
    "wrong_dominant_factor": wrong_dominant_factor,
    "overstated_confidence_subtle": overstated_confidence_subtle,
    "narrow_range": narrow_range,
}


def inject_all_mechanistic(features: dict, p: dict, mode: str = "blatant") -> dict[str, Any]:
    """The true answer + one corrupted variant per injector + the reference oracle (centerpiece
    numbers). `mode='blatant'` = v1 directional reversals; `mode='subtle'` = v2 quantitative errors
    a blind read cannot adjudicate without the model. Returns {reference, correct, injected}."""
    correct = correct_answer(features, p)
    reference = centerpiece(features, p, verify_dynamics=False)
    injectors = SUBTLE_MECH_INJECTORS if mode == "subtle" else MECH_INJECTORS
    injected = []
    for name, fn in injectors.items():
        corrupted, label = fn(correct, features, p)
        injected.append({"defect_type": name, "corrupted_answer": corrupted, "label": label})
    return {"reference": reference, "correct": correct, "injected": injected}
