import math

import pytest

from jovian_resonance_lab.orbits import (
    cross,
    dot,
    fixed_jupiter_basis,
    norm,
    rotate_to_basis,
    scale,
    state_to_elements,
    subtract,
)


def test_vector_helpers_and_basis() -> None:
    assert dot((1, 2, 3), (4, 5, 6)) == 32
    assert cross((1, 0, 0), (0, 1, 0)) == (0, 0, 1)
    assert norm((3, 4, 0)) == 5
    assert scale((1, 2, 3), 2) == (2, 4, 6)
    assert subtract((3, 2, 1), (1, 1, 1)) == (2, 1, 0)
    basis = fixed_jupiter_basis()
    assert all(norm(axis) == pytest.approx(1.0) for axis in basis)
    assert rotate_to_basis(basis[0], basis) == pytest.approx((1.0, 0.0, 0.0))


def test_known_elliptic_state() -> None:
    mu = 1.0
    eccentricity = 0.1
    radius_periapsis = 1.0 - eccentricity
    speed_periapsis = math.sqrt(mu * (1 + eccentricity) / radius_periapsis)
    elements = state_to_elements((radius_periapsis, 0, 0), (0, speed_periapsis, 0), mu)
    assert elements.semimajor_axis == pytest.approx(1.0)
    assert elements.eccentricity == pytest.approx(eccentricity)
    assert elements.mean_longitude == pytest.approx(0.0)


@pytest.mark.parametrize(
    ("position", "velocity", "mu", "message"),
    [
        ((0, 0, 0), (0, 1, 0), 1, "positive"),
        ((1, 0, 0), (1, 0, 0), 1, "radial"),
        ((1, 0, 0), (0, 1, 0), 1, "non-circular"),
    ],
)
def test_invalid_states_fail(
    position: tuple[int, int, int], velocity: tuple[int, int, int], mu: int, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        state_to_elements(position, velocity, mu)
