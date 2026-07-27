from whofixesthis.geospatial import (
    boundary_membership,
    haversine_m,
    match_asset_candidates,
)


def test_exact_boundary_is_not_inside() -> None:
    bounds = (13.4, 52.5, 13.5, 52.6)
    assert boundary_membership(13.4, 52.55, bounds) == "boundary"
    assert boundary_membership(13.45, 52.55, bounds) == "inside"
    assert boundary_membership(13.6, 52.55, bounds) == "outside"


def test_haversine_is_symmetric() -> None:
    forward = haversine_m(52.52, 13.4, 52.521, 13.402)
    reverse = haversine_m(52.521, 13.402, 52.52, 13.4)
    assert abs(forward - reverse) < 1e-9


def test_uncertainty_radius_expands_candidate_recall() -> None:
    assets = [
        {
            "asset_id": "near",
            "asset_type": "light",
            "latitude": 52.5201,
            "longitude": 13.4001,
        },
        {
            "asset_id": "far",
            "asset_type": "light",
            "latitude": 52.521,
            "longitude": 13.401,
        },
    ]
    narrow = match_asset_candidates(52.52, 13.4, 30, assets)
    broad = match_asset_candidates(52.52, 13.4, 200, assets)
    assert len(narrow) <= len(broad)
    assert [item.asset_id for item in broad] == ["near", "far"]


def test_candidates_are_distance_then_id_sorted() -> None:
    assets = [
        {
            "asset_id": "b",
            "asset_type": "pole",
            "latitude": 52.52,
            "longitude": 13.4,
        },
        {
            "asset_id": "a",
            "asset_type": "pole",
            "latitude": 52.52,
            "longitude": 13.4,
        },
    ]
    candidates = match_asset_candidates(52.52, 13.4, 10, assets)
    assert [item.asset_id for item in candidates] == ["a", "b"]
