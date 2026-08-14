import math

import pytest

from jovian_resonance_lab.angles import (
    circular_difference,
    circular_mean,
    circular_rmse,
    laplace_angle,
    unwrap_degrees,
    wrap_degrees,
    wrap_positive,
)


def test_wrapping_and_laplace_angle() -> None:
    assert wrap_degrees(180.0) == -180.0
    assert wrap_degrees(-181.0) == 179.0
    assert wrap_positive(-1.0) == 359.0
    assert circular_difference(1.0, 359.0) == 2.0
    assert laplace_angle(10.0, 20.0, 30.0) == 10.0


def test_circular_statistics() -> None:
    assert circular_mean([359.0, 1.0]) == pytest.approx(0.0)
    assert circular_rmse([1.0, 359.0], [359.0, 1.0]) == 2.0
    assert unwrap_degrees([359.0, 1.0, 3.0]) == [359.0, 361.0, 363.0]


@pytest.mark.parametrize("function", [circular_mean, unwrap_degrees])
def test_empty_angle_statistics_fail(function: object) -> None:
    with pytest.raises(ValueError):
        function([])  # type: ignore[operator]


def test_undefined_mean_and_bad_rmse_fail() -> None:
    with pytest.raises(ValueError, match="undefined"):
        circular_mean([0.0, 180.0])
    with pytest.raises(ValueError):
        circular_rmse([], [])
    assert math.isfinite(circular_mean([90.0]))
