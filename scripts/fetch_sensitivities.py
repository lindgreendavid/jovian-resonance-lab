#!/usr/bin/env python3
"""Fetch and evaluate the two frozen reference-only sensitivity analyses."""

from __future__ import annotations

import datetime as dt
import itertools
from pathlib import Path
from typing import Any

from jovian_resonance_lab.analysis import write_json
from jovian_resonance_lab.angles import circular_difference, laplace_angle, unwrap_degrees
from jovian_resonance_lab.horizons import (
    element_parameters,
    fetch_text,
    parse_elements,
    reported_source,
)

ROOT = Path(__file__).resolve().parents[1]
MOONS = {"Io": 501, "Europa": 502, "Ganymede": 503}


def _frame(plane: str) -> tuple[list[dict[str, float]], dict[str, Any]]:
    series: dict[str, Any] = {}
    queries: dict[str, Any] = {}
    for name, target in MOONS.items():
        parameters = element_parameters(target, "2011-01-01", "2011-01-31", "12 h", plane)
        text = fetch_text(parameters)
        source = reported_source(text)
        if not source.startswith("jup365"):
            raise RuntimeError(f"unexpected source {source!r}")
        series[name] = parse_elements(text)
        queries[name] = {"parameters": parameters, "reported_source": source}
    epochs = [row.jd for row in series["Io"]]
    if any([row.jd for row in series[name]] != epochs for name in ("Europa", "Ganymede")):
        raise RuntimeError("sensitivity epochs are misaligned")
    rows = [
        {
            "jd_tdb": epoch,
            "phi_l_degrees": laplace_angle(
                series["Io"][index].mean_longitude,
                series["Europa"][index].mean_longitude,
                series["Ganymede"][index].mean_longitude,
            ),
        }
        for index, epoch in enumerate(epochs)
    ]
    return rows, queries


def main() -> None:
    body, body_queries = _frame("B")
    icrf, icrf_queries = _frame("F")
    if [row["jd_tdb"] for row in body] != [row["jd_tdb"] for row in icrf]:
        raise RuntimeError("frame sensitivity epochs are misaligned")
    body_phi = [row["phi_l_degrees"] for row in body]
    icrf_phi = [row["phi_l_degrees"] for row in icrf]
    body_unwrapped = unwrap_degrees(body_phi)
    frame_residuals = [
        circular_difference(left, right) for left, right in zip(body_phi, icrf_phi, strict=True)
    ]
    write_json(
        ROOT / "reports/v0.1-reference-sensitivities.json",
        {
            "schema_version": "0.1.0",
            "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "sample_count": len(body),
            "twelve_hour_body_equator_trace": body,
            "twelve_hour_unwrapped_range_degrees": max(body_unwrapped) - min(body_unwrapped),
            "maximum_twelve_hour_increment_degrees": max(
                abs(right - left) for left, right in itertools.pairwise(body_unwrapped)
            ),
            "circulation_detected": max(body_unwrapped) - min(body_unwrapped) >= 360.0,
            "frame_sensitivity": {
                "maximum_absolute_difference_degrees": max(abs(value) for value in frame_residuals),
                "root_mean_square_difference_degrees": (
                    sum(value * value for value in frame_residuals) / len(frame_residuals)
                )
                ** 0.5,
            },
            "queries": {"body_equator_of_date": body_queries, "icrf_j2000": icrf_queries},
        },
    )


if __name__ == "__main__":
    main()
