#!/usr/bin/env python3
"""Create the small, deterministic data projection used by the static site."""

from pathlib import Path

from jovian_resonance_lab.analysis import load_json, write_json

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    report = load_json(ROOT / "reports/v0.1-model-adequacy.json")
    validation = load_json(ROOT / "reports/v1.0-validation.json")
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
    validation_stride = 10
    write_json(
        ROOT / "site/data/results-v1.0.json",
        {
            "product_version": validation["product_version"],
            "interval": validation["interval"],
            "reference": validation["reference"],
            "models": validation["common_step_models"],
            "ordering_gates": validation["ordering_gates"],
            "convergence": validation["convergence"],
            "coarse_reference": validation["coarse_g4j2_reference"],
            "fine_reference": validation["fine_g4j2_reference"],
            "reference_adequacy_gate": validation["reference_adequacy_gate"],
            "all_confirmatory_gates_pass": validation["all_confirmatory_gates_pass"],
            "annual_fine_reference": validation["annual_fine_g4j2_reference"],
            "chart": {
                key: values[::validation_stride]
                for key, values in validation["daily_traces"].items()
            },
            "historical_v0_1": {
                "interval": "2001-01-01 through 2030-12-31 TDB",
                "sample_count": report["sample_count"],
                "nominal_models": report["models"],
                "status": "unchanged frozen v0.1 analysis",
            },
        },
    )


if __name__ == "__main__":
    main()
