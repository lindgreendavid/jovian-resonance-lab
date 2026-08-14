#!/usr/bin/env python3
"""Run the frozen v1 temporal replication and numerical-convergence gates."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from run_models import _run

from jovian_resonance_lab.analysis import (
    compare_trace,
    describe_reference,
    expectation_results,
    load_json,
    write_json,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_COMMIT = "b280a9ce6a9d0e7309707b9315d7847739c6e956"
COMMON_STEP = 0.0025
FINE_STEP = 0.00125
COARSE_STEP = 0.005


def _annual_metrics(reference: list[float], model: list[float]) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    cursor = 0
    final_stop = 0
    for year in range(2031, 2041):
        days = 366 if year % 4 == 0 else 365
        stop = cursor + days
        final_stop = stop
        result[str(year)] = compare_trace(reference[cursor:stop], model[cursor:stop])
        cursor += days
    if final_stop != len(reference):
        raise RuntimeError("annual validation slices do not cover the registry")
    return result


def main() -> None:
    reference_rows: list[dict[str, Any]] = load_json(ROOT / "data/jup365-reference-v1.0.json")
    states = load_json(ROOT / "data/initial-states-v1.0.json")
    reference = [row["phi_l_degrees"] for row in reference_rows]
    days = len(reference) - 1
    specifications = {
        "K2": (["Io", "Europa", "Ganymede"], False, True),
        "G3": (["Io", "Europa", "Ganymede"], False, False),
        "G4": (["Io", "Europa", "Ganymede", "Callisto"], False, False),
        "G4J2": (["Io", "Europa", "Ganymede", "Callisto"], True, False),
    }
    traces: dict[str, list[float]] = {}
    metrics: dict[str, dict[str, float]] = {}
    diagnostics: dict[str, dict[str, float]] = {}
    for name, (moons, include_j2, independent) in specifications.items():
        traces[name], diagnostics[name] = _run(
            moons,
            states,
            days,
            COMMON_STEP,
            include_j2=include_j2,
            independent=independent,
        )
        metrics[name] = compare_trace(reference, traces[name])

    moons = specifications["G4J2"][0]
    coarse, _ = _run(moons, states, days, COARSE_STEP, include_j2=True)
    fine, fine_diagnostics = _run(moons, states, days, FINE_STEP, include_j2=True)
    coarse_medium = compare_trace(coarse, traces["G4J2"])
    medium_fine = compare_trace(traces["G4J2"], fine)
    coarse_reference = compare_trace(reference, coarse)
    estimated_order = math.log2(
        coarse_medium["circular_rmse_degrees"] / medium_fine["circular_rmse_degrees"]
    )
    ordering = expectation_results(metrics)
    convergence = {
        "medium_fine_rmse_at_most_0.75_degrees": (medium_fine["circular_rmse_degrees"] <= 0.75),
        "estimated_order_between_1.5_and_2.5": 1.5 <= estimated_order <= 2.5,
    }
    fine_reference = compare_trace(reference, fine)
    adequacy = {
        "fine_reference_rmse_at_most_1_degree": fine_reference["circular_rmse_degrees"] <= 1.0
    }
    all_gates = all(ordering.values()) and all(convergence.values()) and all(adequacy.values())

    write_json(
        ROOT / "reports/v1.0-validation.json",
        {
            "schema_version": "1.0.0",
            "product_version": "1.0.0",
            "protocol_commit": PROTOCOL_COMMIT,
            "interval": {
                "start_tdb": "2031-01-01 00:00",
                "end_tdb": "2040-12-31 00:00",
                "sample_count": len(reference),
                "initialization": "JUP365 state at validation start",
            },
            "reference": describe_reference(reference),
            "common_step_days": COMMON_STEP,
            "common_step_models": metrics,
            "common_step_diagnostics": diagnostics,
            "ordering_gates": ordering,
            "convergence": {
                "coarse_step_days": COARSE_STEP,
                "medium_step_days": COMMON_STEP,
                "fine_step_days": FINE_STEP,
                "coarse_vs_medium": coarse_medium,
                "medium_vs_fine": medium_fine,
                "estimated_order": estimated_order,
                "gates": convergence,
            },
            "coarse_g4j2_reference": coarse_reference,
            "fine_g4j2_reference": fine_reference,
            "fine_g4j2_diagnostics": fine_diagnostics,
            "reference_adequacy_gate": adequacy,
            "all_confirmatory_gates_pass": all_gates,
            "annual_fine_g4j2_reference": _annual_metrics(reference, fine),
            "endpoint_exclusion": {
                name: compare_trace(reference[:-1], trace[:-1]) for name, trace in traces.items()
            },
            "daily_traces": {
                "jd_tdb": [row["jd_tdb"] for row in reference_rows],
                "reference": reference,
                **traces,
                "G4J2_coarse": coarse,
                "G4J2_fine": fine,
            },
        },
    )


if __name__ == "__main__":
    main()
