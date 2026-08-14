#!/usr/bin/env python3
"""Run the four frozen model ablations and write the machine-readable report."""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Any

from jovian_resonance_lab.analysis import (
    compare_trace,
    describe_reference,
    expectation_results,
    load_json,
    relative_drift,
    write_json,
)
from jovian_resonance_lab.angles import unwrap_degrees
from jovian_resonance_lab.dynamics import Body, barycentric_bodies, integrate, state_energy

ROOT = Path(__file__).resolve().parents[1]
GM = {
    "Jupiter": 1.266865319003704e8,
    "Io": 5.959915466180539e3,
    "Europa": 3.202712099607295e3,
    "Ganymede": 9.887832752719638e3,
    "Callisto": 7.179283402579837e3,
}
PROTOCOL_COMMIT = "7d562ebaaf0be7073d3cfef206803472cbfce5e1"


def _bodies(names: list[str], states: dict[str, Any]) -> list[Body]:
    jupiter = Body("Jupiter", GM["Jupiter"], (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    moons = [
        Body(
            name,
            GM[name],
            tuple(states[name]["position_km"]),
            tuple(states[name]["velocity_km_day"]),
        )
        for name in names
    ]
    return barycentric_bodies(jupiter, moons)


def _run(
    names: list[str],
    states: dict[str, Any],
    days: int,
    step: float,
    *,
    include_j2: bool = False,
    independent: bool = False,
) -> tuple[list[float], dict[str, float]]:
    bodies = _bodies(names, states)
    gms = [body.gm for body in bodies]
    initial_positions = [value for body in bodies for value in body.position]
    initial_velocities = [value for body in bodies for value in body.velocity_km_day]
    initial_energy = state_energy(initial_positions, initial_velocities, gms)
    total_gm = sum(gms)

    def barycenter(values: list[float]) -> list[float]:
        return [
            sum(gm * values[3 * index + axis] for index, gm in enumerate(gms)) / total_gm
            for axis in range(3)
        ]

    initial_center = barycenter(initial_positions)
    initial_center_velocity = barycenter(initial_velocities)
    final: tuple[list[float], list[float]] | None = None

    def capture(day: int, positions: list[float], velocities: list[float]) -> None:
        nonlocal final
        if day == days:
            final = (positions.copy(), velocities.copy())

    samples = integrate(
        bodies,
        days,
        step,
        include_j2,
        capture,
        mode="independent" if independent else "interacting",
    )
    if final is None:
        raise RuntimeError("integration did not reach its final epoch")
    diagnostics: dict[str, float] = {}
    if not include_j2 and not independent:
        diagnostics["relative_point_mass_energy_drift"] = relative_drift(
            initial_energy, state_energy(final[0], final[1], gms)
        )
    final_center = barycenter(final[0])
    final_center_velocity = barycenter(final[1])
    diagnostics["barycenter_displacement_km"] = (
        sum((final_center[axis] - initial_center[axis]) ** 2 for axis in range(3)) ** 0.5
    )
    diagnostics["barycenter_velocity_drift_km_day"] = (
        sum((final_center_velocity[axis] - initial_center_velocity[axis]) ** 2 for axis in range(3))
        ** 0.5
    )
    return [sample.phi for sample in samples], diagnostics


def main() -> None:
    reference_rows = load_json(ROOT / "data/jup365-reference-v0.1.json")
    states = load_json(ROOT / "data/initial-states-v0.1.json")
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
            moons, states, days, 0.01, include_j2=include_j2, independent=independent
        )
        metrics[name] = compare_trace(reference, traces[name])
    sensitivity, _ = _run(specifications["G4J2"][0], states, days, 0.005, include_j2=True)
    sensitivity_metrics = compare_trace(traces["G4J2"], sensitivity)
    exploratory_quarter_step, _ = _run(
        specifications["G4J2"][0], states, days, 0.0025, include_j2=True
    )
    exploratory_eighth_step, _ = _run(
        specifications["G4J2"][0], states, days, 0.00125, include_j2=True
    )
    unwrapped_longitudes = {
        name: unwrap_degrees([row[field] for row in reference_rows])
        for name, field in {
            "Io": "lambda_io_degrees",
            "Europa": "lambda_europa_degrees",
            "Ganymede": "lambda_ganymede_degrees",
        }.items()
    }
    principal_daily_alias = {
        name: (values[-1] - values[0]) / days for name, values in unwrapped_longitudes.items()
    }
    raw_longitudes = {
        name: [row[field] for row in reference_rows]
        for name, field in {
            "Io": "lambda_io_degrees",
            "Europa": "lambda_europa_degrees",
            "Ganymede": "lambda_ganymede_degrees",
        }.items()
    }
    prograde_mean_motions = {
        name: sum((right - left) % 360.0 for left, right in itertools.pairwise(values)) / days
        for name, values in raw_longitudes.items()
    }
    report = {
        "schema_version": "0.1.0",
        "protocol_commit": PROTOCOL_COMMIT,
        "reference": describe_reference(reference),
        "reference_mean_motion_degrees_per_day": {
            "principal_daily_alias": principal_daily_alias,
            "prograde_resolved": {
                **prograde_mean_motions,
                "n_io_minus_2_n_europa": prograde_mean_motions["Io"]
                - 2 * prograde_mean_motions["Europa"],
                "n_europa_minus_2_n_ganymede": prograde_mean_motions["Europa"]
                - 2 * prograde_mean_motions["Ganymede"],
                "laplace_combination": prograde_mean_motions["Io"]
                - 3 * prograde_mean_motions["Europa"]
                + 2 * prograde_mean_motions["Ganymede"],
            },
        },
        "sample_count": len(reference),
        "models": metrics,
        "expectations": expectation_results(metrics),
        "numerical_diagnostics": diagnostics,
        "sensitivity_g4j2_half_step": sensitivity_metrics,
        "exploratory_convergence": {
            "prespecified_0.01_vs_0.005": sensitivity_metrics,
            "0.005_vs_0.0025": compare_trace(sensitivity, exploratory_quarter_step),
            "0.0025_vs_0.00125": compare_trace(exploratory_quarter_step, exploratory_eighth_step),
            "reference_metrics": {
                "0.005": compare_trace(reference, sensitivity),
                "0.0025": compare_trace(reference, exploratory_quarter_step),
                "0.00125": compare_trace(reference, exploratory_eighth_step),
            },
            "status": "exploratory post-confirmatory; does not replace the primary endpoint",
        },
        "endpoint_exclusion": {
            name: compare_trace(reference[:-1], trace[:-1]) for name, trace in traces.items()
        },
        "daily_traces": {"jd_tdb": [row["jd_tdb"] for row in reference_rows], **traces},
    }
    write_json(ROOT / "reports/v0.1-model-adequacy.json", report)


if __name__ == "__main__":
    main()
