import math

import pytest

from jovian_resonance_lab.dynamics import (
    Body,
    acceleration,
    barycentric_bodies,
    integrate,
    state_energy,
    total_energy,
)


def _system() -> list[Body]:
    jupiter = Body("Jupiter", 1.0, (0, 0, 0), (0, 0, 0))
    moons = []
    mu = jupiter.gm
    for index, radius in enumerate((10000.0, 16000.0, 24000.0), start=1):
        speed = math.sqrt(mu / radius) * 0.99
        moons.append(Body(str(index), 1e-12, (radius, 0, 0), (0, speed, 0)))
    return barycentric_bodies(jupiter, moons)


def test_acceleration_modes_and_j2() -> None:
    positions = [0, 0, 0, 10, 0, 0, -20, 0, 0]
    gms = [100, 1, 2]
    interacting = acceleration(positions, gms, False)
    assert interacting[0] == pytest.approx(0.005)
    independent = acceleration(positions, gms, False, "independent")
    assert independent[:3] == [0, 0, 0]
    assert independent[3] < 0 < independent[6]
    with_j2 = acceleration(positions, gms, True)
    assert with_j2 != interacting
    with pytest.raises(ValueError, match="excludes"):
        acceleration(positions, gms, True, "independent")


def test_barycenter_and_energy_forms_match() -> None:
    bodies = _system()
    total_gm = sum(body.gm for body in bodies)
    for axis in range(3):
        center = sum(body.gm * body.position[axis] for body in bodies) / total_gm
        speed = sum(body.gm * body.velocity_km_day[axis] for body in bodies) / total_gm
        assert center == pytest.approx(0.0, abs=1e-10)
        assert speed == pytest.approx(0.0, abs=1e-10)
    positions = [value for body in bodies for value in body.position]
    velocities = [value for body in bodies for value in body.velocity_km_day]
    assert state_energy(positions, velocities, [body.gm for body in bodies]) == pytest.approx(
        total_energy(bodies)
    )


def test_short_integration_and_callback() -> None:
    calls: list[int] = []
    samples = integrate(_system(), 2, 0.01, False, lambda day, _p, _v: calls.append(day))
    assert [sample.day for sample in samples] == [0, 1, 2]
    assert calls == [1, 2]
    assert all(math.isfinite(sample.phi) for sample in samples)
    independent = integrate(_system(), 1, 0.01, False, mode="independent")
    assert len(independent) == 2


def test_invalid_integration_settings_fail() -> None:
    with pytest.raises(ValueError, match="divide"):
        integrate(_system(), 1, 0.3, False)
    with pytest.raises(ValueError, match="three moons"):
        integrate(_system()[:3], 1, 0.01, False)
