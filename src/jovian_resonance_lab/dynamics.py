"""Small, independently implemented leapfrog model for the frozen ablations."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal

from .angles import laplace_angle
from .orbits import Vector, dot, fixed_jupiter_basis, rotate_to_basis, state_to_elements

SECONDS_PER_DAY = 86400.0
JUPITER_RADIUS_KM = 71492.0
JUPITER_J2 = 0.0146965735
JUPITER_POLE = fixed_jupiter_basis()[2]


@dataclass(frozen=True)
class Body:
    name: str
    gm_km3_s2: float
    position: Vector
    velocity_km_day: Vector

    @property
    def gm(self) -> float:
        return self.gm_km3_s2 * SECONDS_PER_DAY**2


@dataclass(frozen=True)
class IntegrationSample:
    day: int
    phi: float


def _point_mass_acceleration(positions: list[float], gms: Sequence[float]) -> list[float]:
    count = len(gms)
    acceleration = [0.0] * (3 * count)
    for i in range(count):
        ix = 3 * i
        for j in range(count):
            if i == j:
                continue
            jx = 3 * j
            dx = positions[jx] - positions[ix]
            dy = positions[jx + 1] - positions[ix + 1]
            dz = positions[jx + 2] - positions[ix + 2]
            distance2 = dx * dx + dy * dy + dz * dz
            inverse_distance3 = 1.0 / (distance2 * math.sqrt(distance2))
            factor = gms[j] * inverse_distance3
            acceleration[ix] += factor * dx
            acceleration[ix + 1] += factor * dy
            acceleration[ix + 2] += factor * dz
    return acceleration


def _independent_acceleration(positions: list[float], gms: Sequence[float]) -> list[float]:
    """Accelerate each moon around a fixed Jupiter for the frozen K2 ablation."""
    acceleration = [0.0] * len(positions)
    for moon in range(1, len(gms)):
        offset = 3 * moon
        dx = positions[offset] - positions[0]
        dy = positions[offset + 1] - positions[1]
        dz = positions[offset + 2] - positions[2]
        distance2 = dx * dx + dy * dy + dz * dz
        inverse_distance3 = 1.0 / (distance2 * math.sqrt(distance2))
        factor = -(gms[0] + gms[moon]) * inverse_distance3
        acceleration[offset] = factor * dx
        acceleration[offset + 1] = factor * dy
        acceleration[offset + 2] = factor * dz
    return acceleration


def _add_j2(acceleration: list[float], positions: list[float], gms: Sequence[float]) -> None:
    jupiter_gm = gms[0]
    pole_x, pole_y, pole_z = JUPITER_POLE
    for moon in range(1, len(gms)):
        offset = 3 * moon
        rx = positions[offset] - positions[0]
        ry = positions[offset + 1] - positions[1]
        rz = positions[offset + 2] - positions[2]
        radius2 = rx * rx + ry * ry + rz * rz
        radius = math.sqrt(radius2)
        axial = rx * pole_x + ry * pole_y + rz * pole_z
        q = axial * axial / radius2
        factor = 1.5 * JUPITER_J2 * jupiter_gm * JUPITER_RADIUS_KM**2 / radius**5
        ax = factor * (rx * (5.0 * q - 1.0) - 2.0 * axial * pole_x)
        ay = factor * (ry * (5.0 * q - 1.0) - 2.0 * axial * pole_y)
        az = factor * (rz * (5.0 * q - 1.0) - 2.0 * axial * pole_z)
        acceleration[offset] += ax
        acceleration[offset + 1] += ay
        acceleration[offset + 2] += az
        reaction = gms[moon] / jupiter_gm
        acceleration[0] -= reaction * ax
        acceleration[1] -= reaction * ay
        acceleration[2] -= reaction * az


def acceleration(
    positions: list[float],
    gms: Sequence[float],
    include_j2: bool,
    mode: Literal["interacting", "independent"] = "interacting",
) -> list[float]:
    """Return point-mass accelerations with an optional fixed-axis J2 term."""
    if mode == "independent":
        if include_j2:
            raise ValueError("K2 independent mode excludes J2")
        return _independent_acceleration(positions, gms)
    values = _point_mass_acceleration(positions, gms)
    if include_j2:
        _add_j2(values, positions, gms)
    return values


def barycentric_bodies(jupiter: Body, moons: Sequence[Body]) -> list[Body]:
    """Shift Jupiter-centered input states into the system barycenter frame."""
    total_gm = jupiter.gm + sum(moon.gm for moon in moons)
    jupiter_position: Vector = (
        -sum(moon.gm * moon.position[0] for moon in moons) / total_gm,
        -sum(moon.gm * moon.position[1] for moon in moons) / total_gm,
        -sum(moon.gm * moon.position[2] for moon in moons) / total_gm,
    )
    jupiter_velocity: Vector = (
        -sum(moon.gm * moon.velocity_km_day[0] for moon in moons) / total_gm,
        -sum(moon.gm * moon.velocity_km_day[1] for moon in moons) / total_gm,
        -sum(moon.gm * moon.velocity_km_day[2] for moon in moons) / total_gm,
    )
    shifted = [Body(jupiter.name, jupiter.gm_km3_s2, jupiter_position, jupiter_velocity)]
    for moon in moons:
        shifted.append(
            Body(
                moon.name,
                moon.gm_km3_s2,
                (
                    moon.position[0] + jupiter_position[0],
                    moon.position[1] + jupiter_position[1],
                    moon.position[2] + jupiter_position[2],
                ),
                (
                    moon.velocity_km_day[0] + jupiter_velocity[0],
                    moon.velocity_km_day[1] + jupiter_velocity[1],
                    moon.velocity_km_day[2] + jupiter_velocity[2],
                ),
            )
        )
    return shifted


def _phi(positions: list[float], velocities: list[float], gms: Sequence[float]) -> float:
    basis = fixed_jupiter_basis()
    longitudes = []
    for moon in range(1, 4):
        offset = 3 * moon
        relative_position = (
            positions[offset] - positions[0],
            positions[offset + 1] - positions[1],
            positions[offset + 2] - positions[2],
        )
        relative_velocity = (
            velocities[offset] - velocities[0],
            velocities[offset + 1] - velocities[1],
            velocities[offset + 2] - velocities[2],
        )
        elements = state_to_elements(
            rotate_to_basis(relative_position, basis),
            rotate_to_basis(relative_velocity, basis),
            gms[0] + gms[moon],
        )
        longitudes.append(elements.mean_longitude)
    return laplace_angle(*longitudes)


def integrate(
    bodies: Sequence[Body],
    days: int,
    step_days: float,
    include_j2: bool,
    callback: Callable[[int, list[float], list[float]], None] | None = None,
    mode: Literal["interacting", "independent"] = "interacting",
) -> list[IntegrationSample]:
    """Integrate with velocity Verlet and return exactly daily Laplace-angle samples."""
    steps_per_day_float = 1.0 / step_days
    steps_per_day = round(steps_per_day_float)
    if not math.isclose(steps_per_day_float, steps_per_day, abs_tol=1e-12):
        raise ValueError("step must divide one day exactly")
    if len(bodies) < 4:
        raise ValueError("Jupiter and at least three moons are required")
    gms = [body.gm for body in bodies]
    positions = [component for body in bodies for component in body.position]
    velocities = [component for body in bodies for component in body.velocity_km_day]
    samples = [IntegrationSample(day=0, phi=_phi(positions, velocities, gms))]
    current_acceleration = acceleration(positions, gms, include_j2, mode)
    total_steps = days * steps_per_day
    half_step = 0.5 * step_days
    for step in range(1, total_steps + 1):
        for index in range(len(velocities)):
            velocities[index] += half_step * current_acceleration[index]
            positions[index] += step_days * velocities[index]
        current_acceleration = acceleration(positions, gms, include_j2, mode)
        for index in range(len(velocities)):
            velocities[index] += half_step * current_acceleration[index]
        if step % steps_per_day == 0:
            day = step // steps_per_day
            samples.append(IntegrationSample(day=day, phi=_phi(positions, velocities, gms)))
            if callback is not None:
                callback(day, positions, velocities)
    return samples


def total_energy(bodies: Sequence[Body]) -> float:
    """Return point-mass kinetic plus potential energy in GM-weighted units."""
    kinetic = 0.0
    for body in bodies:
        kinetic += 0.5 * body.gm * dot(body.velocity_km_day, body.velocity_km_day)
    potential = 0.0
    for i, first in enumerate(bodies):
        for second in bodies[i + 1 :]:
            dx = first.position[0] - second.position[0]
            dy = first.position[1] - second.position[1]
            dz = first.position[2] - second.position[2]
            potential -= first.gm * second.gm / math.sqrt(dx * dx + dy * dy + dz * dz)
    return kinetic + potential


def state_energy(
    positions: Sequence[float], velocities: Sequence[float], gms: Sequence[float]
) -> float:
    """Return the same point-mass energy for flattened integration state arrays."""
    kinetic = sum(
        0.5
        * gm
        * (
            velocities[3 * index] ** 2
            + velocities[3 * index + 1] ** 2
            + velocities[3 * index + 2] ** 2
        )
        for index, gm in enumerate(gms)
    )
    potential = 0.0
    for first in range(len(gms)):
        for second in range(first + 1, len(gms)):
            dx = positions[3 * first] - positions[3 * second]
            dy = positions[3 * first + 1] - positions[3 * second + 1]
            dz = positions[3 * first + 2] - positions[3 * second + 2]
            potential -= gms[first] * gms[second] / math.sqrt(dx * dx + dy * dy + dz * dz)
    return kinetic + potential
