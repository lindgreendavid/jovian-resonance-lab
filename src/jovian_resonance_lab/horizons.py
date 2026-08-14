"""Minimal, auditable client and parser for fixed JPL Horizons queries."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
import urllib.parse
import urllib.request
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

API_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
SOURCE_PATTERN = re.compile(r"\{source:\s*([^}]+)\}", re.IGNORECASE)


@dataclass(frozen=True)
class ElementRow:
    jd: float
    eccentricity: float
    inclination: float
    ascending_node: float
    argument_of_periapsis: float
    mean_anomaly: float
    semimajor_axis: float

    @property
    def mean_longitude(self) -> float:
        return (self.ascending_node + self.argument_of_periapsis + self.mean_anomaly) % 360.0


@dataclass(frozen=True)
class VectorRow:
    jd: float
    position: tuple[float, float, float]
    velocity: tuple[float, float, float]


def build_url(parameters: dict[str, str]) -> str:
    """Build a stable Horizons URL with quoted batch values supplied by the caller."""
    return f"{API_URL}?{urllib.parse.urlencode(parameters)}"


def fetch_text(parameters: dict[str, str], timeout: float = 120.0) -> str:
    """Fetch one Horizons response using an explicit user agent."""
    request = urllib.request.Request(
        build_url(parameters), headers={"User-Agent": "jovian-resonance-lab/0.1"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        value: str = response.read().decode("utf-8")
        return value


def reported_source(text: str) -> str:
    """Return the unique ephemeris source reported in a response."""
    sources: set[str] = {match.strip().lower() for match in SOURCE_PATTERN.findall(text)}
    if len(sources) != 1:
        raise ValueError(f"expected one reported source, found {sorted(sources)}")
    return sources.pop()


def _rows(text: str) -> list[list[str]]:
    try:
        body = text.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    except IndexError as exc:
        raise ValueError("Horizons response has no ephemeris block") from exc
    rows = []
    for row in csv.reader(line for line in body.splitlines() if line.strip()):
        cells = [cell.strip() for cell in row]
        if cells and cells[-1] == "":
            cells.pop()
        rows.append(cells)
    if not rows:
        raise ValueError("Horizons ephemeris block is empty")
    return rows


def parse_elements(text: str) -> list[ElementRow]:
    """Parse CSV element rows emitted by the frozen query shape."""
    parsed = []
    for row in _rows(text):
        if len(row) != 14:
            raise ValueError(f"expected 14 element columns, found {len(row)}")
        parsed.append(
            ElementRow(
                jd=float(row[0]),
                eccentricity=float(row[2]),
                inclination=float(row[4]),
                ascending_node=float(row[5]),
                argument_of_periapsis=float(row[6]),
                mean_anomaly=float(row[9]),
                semimajor_axis=float(row[11]),
            )
        )
    _require_strict_epochs(item.jd for item in parsed)
    return parsed


def parse_vectors(text: str) -> list[VectorRow]:
    """Parse CSV position/velocity rows emitted by VEC_TABLE=2."""
    parsed = []
    for row in _rows(text):
        if len(row) != 8:
            raise ValueError(f"expected 8 vector columns, found {len(row)}")
        parsed.append(
            VectorRow(
                jd=float(row[0]),
                position=(float(row[2]), float(row[3]), float(row[4])),
                velocity=(float(row[5]), float(row[6]), float(row[7])),
            )
        )
    _require_strict_epochs(item.jd for item in parsed)
    return parsed


def _require_strict_epochs(values: Iterable[float]) -> None:
    items = list(values)
    if any(b <= a for a, b in itertools.pairwise(items)):
        raise ValueError("epochs must be strictly increasing")


def normalized_sha256(rows: Sequence[Sequence[float]]) -> str:
    """Hash numeric rows independently of response formatting and retrieval headers."""
    normalized = [[format(value, ".17g") for value in row] for row in rows]
    payload = json.dumps(normalized, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(payload).hexdigest()


def element_parameters(
    target: int, start: str, stop: str, step: str, plane: str = "B"
) -> dict[str, str]:
    """Return the complete frozen element-query parameter mapping."""
    return {
        "format": "text",
        "COMMAND": f"'{target}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'ELEMENTS'",
        "CENTER": "'500@599'",
        "START_TIME": f"'{start}'",
        "STOP_TIME": f"'{stop}'",
        "STEP_SIZE": f"'{step}'",
        "TIME_TYPE": "'TDB'",
        "REF_PLANE": f"'{plane}'",
        "CSV_FORMAT": "'YES'",
        "OUT_UNITS": "'KM-D'",
    }


def vector_parameters(target: int, jd: float) -> dict[str, str]:
    """Return the complete frozen initial-state query mapping."""
    return {
        "format": "text",
        "COMMAND": f"'{target}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'VECTORS'",
        "CENTER": "'500@599'",
        "TLIST": f"'{jd:.1f}'",
        "TLIST_TYPE": "'JD'",
        "TIME_TYPE": "'TDB'",
        "REF_PLANE": "'F'",
        "CSV_FORMAT": "'YES'",
        "OUT_UNITS": "'KM-D'",
        "VEC_TABLE": "'2'",
    }


def vector_series_parameters(target: int, start: str, stop: str, step: str) -> dict[str, str]:
    """Return the complete frozen vector-series query mapping for the site animation."""
    values = vector_parameters(target, 0.0)
    del values["TLIST"]
    del values["TLIST_TYPE"]
    values.update(
        {
            "START_TIME": f"'{start}'",
            "STOP_TIME": f"'{stop}'",
            "STEP_SIZE": f"'{step}'",
        }
    )
    return values
