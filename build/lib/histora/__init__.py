"""HISTORA — a non-diagnostic oral-systemic research agent.

Relates periodontal disease to cardiovascular and Alzheimer's/neurodegeneration via mechanistic
models and an empirical-validation layer. See docs/PROBLEM.md and docs/SOLUTION.md.

Package layout (aligned to the solution):

  Domain
    record_formats     — the record schema + input formats
    bridge_concepts    — the target mediators (CV + neuro) the analysis must represent
    relational_signals — deterministic non-diagnostic signals + the W1 missing-data directive
                         + the structural case signature

  Reasoning (Claude)
    agent              — the Claude-powered non-diagnostic relational analysis

  Mechanistic harness (pure-python)
    mech_ode           — ODE tools (integrate, steady state, stability, sensitivity, sweep)
    mech_models        — the centerpiece: periodontal source -> IL-6 -> CRP -> CV & neuro axes
    mech_calibrate     — calibrate the spillover to the real dHsCRP-after-therapy anchor
    mech_neuro         — the neuro axis: neuroinflammation -> tau spread (Fisher-KPP, Braak chain)

  Evaluation & validation
    ab_eval            — scoring (recalls, missing-data, guardrail) + the A/B runner
    counterfactual     — counterfactual-sensitivity (reasoning, not vocabulary)
    stats              — bootstrap CIs + standardized OLS (pure-python)
    perio_cognition    — the periodontitis<->cognition association engine (NHANES 2011-2012)
    nhanes             — NHANES mapping + loaders (2009-2010 CV, 2011-2012 cognition)

  Optimization
    exec_gap           — the execution-gap capability (W1 generalized): externalize a known-but-
                         dropped deterministic step; predictor + 3-arm A/B

Everything except `agent` (needs anthropic) and the `nhanes` loaders (need pandas + network) is
pure-python and runs with no scientific stack. Non-diagnostic throughout.
"""
