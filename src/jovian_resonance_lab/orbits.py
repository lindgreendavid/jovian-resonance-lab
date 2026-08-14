"""Cartesian-to-osculating-element conversion for bound Jovian moon states."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TypeAlias

Vector: TypeAlias = tuple[float, float, float]


@dataclass(frozen=True)
class OsculatingElements:
    semimajor_axis: float
    eccentricity: float
    inclination: float
    ascending_node: float
    argument_of_periapsis: float
    mean_anomaly: float

    @property
    def mean_longitude(self) -> float:
        return (self.ascending_node + self.argument_of_periapsis + self.mean_anomaly) % 360.0


def dot(a: Vector, b: Vector) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a: Vector, b: Vector) -> Vector:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def norm(value: Vector) -> float:
    return math.sqrt(dot(value, value))


def scale(value: Vector, factor: float) -> Vector:
    return (value[0] * factor, value[1] * factor, value[2] * factor)


def subtract(a: Vector, b: Vector) -> Vector:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def fixed_jupiter_basis() -> tuple[Vector, Vector, Vector]:
    """Return an orthonormal Jupiter-equator basis using the IAU J2000 pole."""
    ra = math.radians(268.056595)
    dec = math.radians(64.495303)
    z_axis = (math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec))
    icrf_z = (0.0, 0.0, 1.0)
    node = cross(icrf_z, z_axis)
    x_axis = scale(node, 1.0 / norm(node))
    y_axis = cross(z_axis, x_axis)
    return x_axis, y_axis, z_axis


def rotate_to_basis(value: Vector, basis: tuple[Vector, Vector, Vector]) -> Vector:
    """Project an ICRF vector onto an orthonormal basis."""
    return (dot(value, basis[0]), dot(value, basis[1]), dot(value, basis[2]))


def state_to_elements(position: Vector, velocity: Vector, mu: float) -> OsculatingElements:
    """Convert one bound state to classical osculating elements in degrees."""
    radius = norm(position)
    speed2 = dot(velocity, velocity)
    if radius <= 0.0 or mu <= 0.0:
        raise ValueError("radius and mu must be positive")
    h_vec = cross(position, velocity)
    h = norm(h_vec)
    if h == 0.0:
        raise ValueError("radial state has undefined angular elements")
    node_vec = (-h_vec[1], h_vec[0], 0.0)
    node = norm(node_vec)
    vxh = cross(velocity, h_vec)
    e_vec = subtract(scale(vxh, 1.0 / mu), scale(position, 1.0 / radius))
    eccentricity = norm(e_vec)
    if not 0.0 < eccentricity < 1.0:
        raise ValueError("only non-circular bound states are supported")
    semimajor_axis = 1.0 / (2.0 / radius - speed2 / mu)
    inclination = math.acos(max(-1.0, min(1.0, h_vec[2] / h)))

    if node < 1e-15:
        ascending_node = 0.0
        argument_of_periapsis = math.atan2(e_vec[1], e_vec[0])
    else:
        ascending_node = math.atan2(node_vec[1], node_vec[0])
        cos_arg = max(-1.0, min(1.0, dot(node_vec, e_vec) / (node * eccentricity)))
        sin_arg = dot(cross(node_vec, e_vec), h_vec) / (node * eccentricity * h)
        argument_of_periapsis = math.atan2(sin_arg, cos_arg)

    cos_true = max(-1.0, min(1.0, dot(e_vec, position) / (eccentricity * radius)))
    sin_true = dot(cross(e_vec, position), h_vec) / (eccentricity * radius * h)
    true_anomaly = math.atan2(sin_true, cos_true)
    eccentric_anomaly = math.atan2(
        math.sqrt(1.0 - eccentricity * eccentricity) * math.sin(true_anomaly),
        eccentricity + math.cos(true_anomaly),
    )
    mean_anomaly = eccentric_anomaly - eccentricity * math.sin(eccentric_anomaly)

    return OsculatingElements(
        semimajor_axis=semimajor_axis,
        eccentricity=eccentricity,
        inclination=math.degrees(inclination),
        ascending_node=math.degrees(ascending_node) % 360.0,
        argument_of_periapsis=math.degrees(argument_of_periapsis) % 360.0,
        mean_anomaly=math.degrees(mean_anomaly) % 360.0,
    )
