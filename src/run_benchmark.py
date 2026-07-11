"""Run the comparative validation — the integrated HISTORA harness (H) vs. separate single-axis models
(S) vs. bare Claude (C) — and write the scorecard.

The deterministic arms (S, H) always run and are fully reproducible. The bare-Claude arm (C) and the
M6 guardrail probe run only with `--live` (needs `anthropic` + `ANTHROPIC_API_KEY`); without it the
report carries S vs H, which already establishes the "beats separate models" claim quantitatively.

Usage:
  python src/run_benchmark.py                # S vs H (offline, deterministic)
  python src/run_benchmark.py --live         # + bare Claude arm + guardrail probe (needs API key)
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from histora.benchmark import guardrail_adversarial, run_benchmark


def _live_model_fn():
    """A no-tools, no-guardrail Claude call: `(system, user) -> text`. The bare-Claude arm."""
    from histora.agent import _create_with_retry, load_dotenv
    load_dotenv()
    import anthropic
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY not set (add to .env) — run without --live for S vs H.")
    client = anthropic.Anthropic()

    def call(system: str, user: str) -> str:
        resp = _create_with_retry(client, model="claude-opus-4-8", max_tokens=1200,
                                  system=system, messages=[{"role": "user", "content": user}])
        return next((b.text for b in resp.content if getattr(b, "type", None) == "text"), "")

    return call


def _fmt(x) -> str:
    return f"{x:.3f}" if isinstance(x, float) else str(x)


def main() -> None:
    ap = argparse.ArgumentParser(description="HISTORA comparative validation (S vs C vs H)")
    ap.add_argument("--live", action="store_true", help="add the bare-Claude arm + guardrail probe")
    ap.add_argument("--repeats", type=int, default=1,
                    help="repeat the live bare-Claude arm N times and report mean±sd (handles its "
                         "non-determinism; S/H are deterministic)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "results",
                                                  "benchmark_report.json"))
    args = ap.parse_args()

    model_fn = _live_model_fn() if args.live else None
    report = run_benchmark(model_fn=model_fn)
    if args.live:
        report["guardrail_probe"] = guardrail_adversarial(model_fn)
        if args.repeats > 1:
            # arm C is non-deterministic; repeat and summarize the varying metrics (M3, M4).
            runs = [run_benchmark(model_fn=model_fn)["aggregate"]["bare_claude"]
                    for _ in range(args.repeats)]
            def _ms(key):
                xs = [r[key] for r in runs]
                m = sum(xs) / len(xs)
                sd = (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5
                return {"mean": round(m, 4), "sd": round(sd, 4), "n": len(xs)}
            report["bare_claude_variance"] = {k: _ms(k) for k in
                                              ("M3_calibration_error", "M4_directional_validity")}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    metrics = [("M1_free_params_joint", "M1 free params ↓"),
               ("M2_intervention_assumptions", "M2 interv. assumptions ↓"),
               ("M3_calibration_error", "M3 calibration err ↓"),
               ("M4_directional_validity", "M4 direction ↑"),
               ("M5_uncertainty_honesty", "M5 uncertainty ↑"),
               ("M7_falsifiability", "M7 falsifiability ↑")]
    arms = list(report["aggregate"].keys())

    print("HISTORA comparative validation — aggregate over the severity panel\n")
    print(f"  {'metric':26s} " + " ".join(f"{a:>18s}" for a in arms))
    for key, label in metrics:
        row = " ".join(f"{_fmt(report['aggregate'][a][key]):>18s}" for a in arms)
        print(f"  {label:26s} {row}")
    if "guardrail_probe" in report:
        gp = report["guardrail_probe"]
        print(f"\n  M6 guardrail (adversarial, n={gp['n_adversarial']}): "
              f"bare_claude={gp['bare_claude_guardrail_pass']:.2f}  harness={gp['harness_guardrail_pass']:.2f}")
    if "bare_claude_variance" in report:
        v = report["bare_claude_variance"]
        print(f"  bare_claude over {v['M3_calibration_error']['n']} runs: "
              f"M3={v['M3_calibration_error']['mean']}±{v['M3_calibration_error']['sd']}  "
              f"M4={v['M4_directional_validity']['mean']}±{v['M4_directional_validity']['sd']}")
    print("\nNON-DIAGNOSTIC: all arms operate on structural strata; no patient value is produced.")
    print("wrote:", args.out)


if __name__ == "__main__":
    main()
