"""Deterministic helpers for the frozen Jovian model comparison."""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .angles import circular_difference, circular_mean, circular_rmse, unwrap_degrees


def compare_trace(reference: Sequence[float], model: Sequence[float]) -> dict[str, float]:
    """Calculate the prespecified circular error endpoints."""
    if len(reference) != len(model) or not reference:
        raise ValueError("reference and model must be non-empty and equally sized")
    residuals = [
        circular_difference(value, expected)
        for value, expected in zip(model, reference, strict=True)
    ]
    return {
        "circular_rmse_degrees": circular_rmse(model, reference),
        "maximum_absolute_residual_degrees": max(abs(value) for value in residuals),
    }


def describe_reference(values: Sequence[float]) -> dict[str, float]:
    """Calculate the frozen descriptive reference endpoints."""
    if not values:
        raise ValueError("reference must not be empty")
    unwrapped = unwrap_degrees(values)
    return {
        "circular_mean_degrees": circular_mean(values),
        "unwrapped_minimum_degrees": min(unwrapped),
        "unwrapped_maximum_degrees": max(unwrapped),
        "half_peak_to_peak_degrees": (max(unwrapped) - min(unwrapped)) / 2.0,
        "fraction_within_two_degrees_of_180": sum(
            abs(circular_difference(value, 180.0)) <= 2.0 for value in values
        )
        / len(values),
    }


def expectation_results(metrics: dict[str, dict[str, float]]) -> dict[str, bool]:
    """Evaluate only the three comparisons frozen in the protocol."""
    target = metrics["G4J2"]["circular_rmse_degrees"]
    return {
        f"G4J2_less_than_{name}": target < metrics[name]["circular_rmse_degrees"]
        for name in ("G4", "G3", "K2")
    }


def relative_drift(initial: float, final: float) -> float:
    if initial == 0.0 or not math.isfinite(initial) or not math.isfinite(final):
        raise ValueError("finite, non-zero energies are required")
    return (final - initial) / abs(initial)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
