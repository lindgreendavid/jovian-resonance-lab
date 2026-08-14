"""Circular-angle helpers used by the reference and model pipelines."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence


def wrap_degrees(angle: float) -> float:
    """Wrap an angle to [-180, 180)."""
    return (angle + 180.0) % 360.0 - 180.0


def wrap_positive(angle: float) -> float:
    """Wrap an angle to [0, 360)."""
    wrapped = angle % 360.0
    return 0.0 if math.isclose(wrapped, 360.0, abs_tol=1e-12) else wrapped


def circular_difference(observed: float, reference: float) -> float:
    """Return the signed shortest observed-minus-reference difference."""
    return wrap_degrees(observed - reference)


def circular_mean(values: Iterable[float]) -> float:
    """Return the circular mean in [0, 360)."""
    items = list(values)
    if not items:
        raise ValueError("at least one angle is required")
    sin_sum = sum(math.sin(math.radians(value)) for value in items)
    cos_sum = sum(math.cos(math.radians(value)) for value in items)
    if math.isclose(sin_sum, 0.0, abs_tol=1e-15) and math.isclose(cos_sum, 0.0, abs_tol=1e-15):
        raise ValueError("circular mean is undefined")
    return wrap_positive(math.degrees(math.atan2(sin_sum, cos_sum)))


def circular_rmse(observed: Sequence[float], reference: Sequence[float]) -> float:
    """Return circular root-mean-square error in degrees."""
    if len(observed) != len(reference) or not observed:
        raise ValueError("angle sequences must be non-empty and equally sized")
    squared = [circular_difference(a, b) ** 2 for a, b in zip(observed, reference, strict=True)]
    return math.sqrt(sum(squared) / len(squared))


def unwrap_degrees(values: Sequence[float]) -> list[float]:
    """Unwrap a non-empty angular sequence while preserving its first value."""
    if not values:
        raise ValueError("at least one angle is required")
    result = [values[0]]
    for value in values[1:]:
        result.append(result[-1] + circular_difference(value, result[-1]))
    return result


def laplace_angle(io: float, europa: float, ganymede: float) -> float:
    """Return the Io-Europa-Ganymede Laplace angle in [0, 360)."""
    return wrap_positive(io - 3.0 * europa + 2.0 * ganymede)
