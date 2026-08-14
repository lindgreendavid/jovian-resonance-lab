#!/usr/bin/env python3
"""Fetch and normalize the frozen 2031-2040 v1 validation inputs."""

from __future__ import annotations

import datetime as dt
import itertools
from pathlib import Path
from typing import Any

from jovian_resonance_lab.analysis import write_json
from jovian_resonance_lab.angles import laplace_angle
from jovian_resonance_lab.horizons import (
    element_parameters,
    fetch_text,
    normalized_sha256,
    parse_elements,
    parse_vectors,
    reported_source,
    vector_parameters,
)

ROOT = Path(__file__).resolve().parents[1]
MOONS = {"Io": 501, "Europa": 502, "Ganymede": 503, "Callisto": 504}
START_JD = 2462867.5
END_JD = 2466519.5
EXPECTED_ROWS = 3653


def _element_chunks(target: int) -> tuple[list[Any], list[dict[str, Any]]]:
    rows: list[Any] = []
    queries: list[dict[str, Any]] = []
    for year in (2031, 2036):
        stop = year + 5
        parameters = element_parameters(target, f"{year}-01-01", f"{stop}-01-01", "1 d")
        text = fetch_text(parameters)
        source = reported_source(text)
        if not source.startswith("jup365"):
            raise RuntimeError(f"unexpected source {source!r}")
        chunk = parse_elements(text)
        if rows and chunk[0].jd == rows[-1].jd:
            chunk = chunk[1:]
        rows.extend(chunk)
        queries.append({"parameters": parameters, "reported_source": source, "rows": len(chunk)})
    return [row for row in rows if row.jd <= END_JD], queries


def main() -> None:
    retrieval = dt.datetime.now(dt.timezone.utc).isoformat()
    elements: dict[str, list[Any]] = {}
    query_log: dict[str, Any] = {}
    for name, target in list(MOONS.items())[:3]:
        elements[name], query_log[name] = _element_chunks(target)
    epochs = [row.jd for row in elements["Io"]]
    if (
        len(epochs) != EXPECTED_ROWS
        or epochs[0] != START_JD
        or epochs[-1] != END_JD
        or any(right - left != 1.0 for left, right in itertools.pairwise(epochs))
        or any([row.jd for row in elements[name]] != epochs for name in ("Europa", "Ganymede"))
    ):
        raise RuntimeError("validation epochs are incomplete or misaligned")

    reference = [
        {
            "jd_tdb": epoch,
            "lambda_io_degrees": elements["Io"][index].mean_longitude,
            "lambda_europa_degrees": elements["Europa"][index].mean_longitude,
            "lambda_ganymede_degrees": elements["Ganymede"][index].mean_longitude,
            "phi_l_degrees": laplace_angle(
                elements["Io"][index].mean_longitude,
                elements["Europa"][index].mean_longitude,
                elements["Ganymede"][index].mean_longitude,
            ),
        }
        for index, epoch in enumerate(epochs)
    ]

    initial: dict[str, Any] = {}
    initial_queries: dict[str, Any] = {}
    for name, target in MOONS.items():
        parameters = vector_parameters(target, START_JD)
        text = fetch_text(parameters)
        source = reported_source(text)
        if not source.startswith("jup365"):
            raise RuntimeError(f"unexpected source {source!r}")
        row = parse_vectors(text)[0]
        initial[name] = {"position_km": row.position, "velocity_km_day": row.velocity}
        initial_queries[name] = {"parameters": parameters, "reported_source": source}

    numeric_rows = [
        [
            row["jd_tdb"],
            row["lambda_io_degrees"],
            row["lambda_europa_degrees"],
            row["lambda_ganymede_degrees"],
            row["phi_l_degrees"],
        ]
        for row in reference
    ]
    write_json(ROOT / "data/jup365-reference-v1.0.json", reference)
    write_json(ROOT / "data/initial-states-v1.0.json", initial)
    write_json(
        ROOT / "data/provenance-v1.0.json",
        {
            "protocol_commit": "b280a9ce6a9d0e7309707b9315d7847739c6e956",
            "retrieved_utc": retrieval,
            "reference_frame": "Jupiter body equator and node of date",
            "initial_state_frame": "ICRF/J2000, Jupiter-centered",
            "reference_rows": len(reference),
            "normalized_reference_sha256": normalized_sha256(numeric_rows),
            "element_queries": query_log,
            "initial_state_queries": initial_queries,
        },
    )


if __name__ == "__main__":
    main()
