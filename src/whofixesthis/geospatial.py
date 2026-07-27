from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt


@dataclass(frozen=True)
class GeoCandidate:
    asset_id: str
    asset_type: str
    latitude: float
    longitude: float
    distance_m: float


def haversine_m(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    radius_m = 6_371_008.8
    delta_lat = radians(latitude_b - latitude_a)
    delta_lon = radians(longitude_b - longitude_a)
    a = (
        sin(delta_lat / 2) ** 2
        + cos(radians(latitude_a))
        * cos(radians(latitude_b))
        * sin(delta_lon / 2) ** 2
    )
    return 2 * radius_m * asin(sqrt(a))


def boundary_membership(
    longitude: float,
    latitude: float,
    bounds: tuple[float, float, float, float],
    *,
    epsilon: float = 1e-9,
) -> str:
    min_lon, min_lat, max_lon, max_lat = bounds
    on_lon = abs(longitude - min_lon) <= epsilon or abs(longitude - max_lon) <= epsilon
    on_lat = abs(latitude - min_lat) <= epsilon or abs(latitude - max_lat) <= epsilon
    within_lon = min_lon - epsilon <= longitude <= max_lon + epsilon
    within_lat = min_lat - epsilon <= latitude <= max_lat + epsilon
    if (on_lon and within_lat) or (on_lat and within_lon):
        return "boundary"
    if min_lon < longitude < max_lon and min_lat < latitude < max_lat:
        return "inside"
    return "outside"


def match_asset_candidates(
    latitude: float,
    longitude: float,
    uncertainty_m: float,
    assets: list[dict[str, object]],
) -> list[GeoCandidate]:
    candidates = []
    for asset in assets:
        distance = haversine_m(
            latitude,
            longitude,
            float(asset["latitude"]),
            float(asset["longitude"]),
        )
        if distance <= uncertainty_m:
            candidates.append(
                GeoCandidate(
                    asset_id=str(asset["asset_id"]),
                    asset_type=str(asset["asset_type"]),
                    latitude=float(asset["latitude"]),
                    longitude=float(asset["longitude"]),
                    distance_m=round(distance, 3),
                )
            )
    return sorted(candidates, key=lambda item: (item.distance_m, item.asset_id))
