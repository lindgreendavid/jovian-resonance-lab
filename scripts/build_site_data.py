#!/usr/bin/env python3
"""Create the small, deterministic data projection used by the static site."""

from pathlib import Path

from jovian_resonance_lab.analysis import load_json, write_json

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    report = load_json(ROOT / "reports/v0.1-model-adequacy.json")
    sensitivities = load_json(ROOT / "reports/v0.1-reference-sensitivities.json")
    reference = load_json(ROOT / "data/jup365-reference-v0.1.json")
    stride = 30
    write_json(
        ROOT / "site/data/results-v0.1.json",
        {
            "reference": report["reference"],
            "models": report["models"],
            "expectations": report["expectations"],
            "convergence": report["exploratory_convergence"],
            "frame_sensitivity": sensitivities["frame_sensitivity"],
            "twelve_hour": {
                "range_degrees": sensitivities["twelve_hour_unwrapped_range_degrees"],
                "maximum_increment_degrees": sensitivities["maximum_twelve_hour_increment_degrees"],
                "circulation_detected": sensitivities["circulation_detected"],
            },
            "chart": {
                "jd_tdb": report["daily_traces"]["jd_tdb"][::stride],
                "reference": [row["phi_l_degrees"] for row in reference][::stride],
                **{
                    name: report["daily_traces"][name][::stride]
                    for name in ("K2", "G3", "G4", "G4J2")
                },
            },
        },
    )


if __name__ == "__main__":
    main()
