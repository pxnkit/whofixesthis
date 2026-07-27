from datetime import datetime, timezone

from whofixesthis.graph import (
    ResponsibilityEdge,
    ResponsibilityRelation,
    TemporalResponsibilityGraph,
)
from whofixesthis.models import Interval, Provenance


UTC = timezone.utc


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=UTC)


def edge(
    edge_id: str,
    *,
    valid_start: str,
    valid_end: str | None,
    known_from: str,
) -> ResponsibilityEdge:
    return ResponsibilityEdge(
        edge_id=edge_id,
        subject_id="road-17",
        relation=ResponsibilityRelation.MAINTAINS,
        object_id="regional-roads",
        valid_time=Interval(
            start=dt(valid_start),
            end=dt(valid_end) if valid_end else None,
        ),
        transaction_time=Interval(start=dt(known_from)),
        confidence=1.0,
        provenance=Provenance(
            source_id="fixture",
            authority="Fictional authority",
            canonical_url="https://fixtures.invalid/road-17",
            retrieved_at=dt(known_from),
            checksum="a" * 64,
        ),
    )


def test_snapshot_respects_event_time() -> None:
    graph = TemporalResponsibilityGraph(
        [
            edge(
                "old",
                valid_start="2024-01-01",
                valid_end="2025-01-01",
                known_from="2024-01-10",
            ),
            edge(
                "new",
                valid_start="2025-01-01",
                valid_end=None,
                known_from="2025-01-05",
            ),
        ]
    )
    snapshot = graph.snapshot(dt("2024-08-01"), dt("2025-10-01"))
    assert [item.edge_id for item in snapshot] == ["old"]


def test_snapshot_blocks_future_transaction_leakage() -> None:
    graph = TemporalResponsibilityGraph(
        [
            edge(
                "late-discovery",
                valid_start="2024-01-01",
                valid_end=None,
                known_from="2025-06-01",
            )
        ]
    )
    assert graph.snapshot(dt("2024-08-01"), dt("2025-05-01")) == []
    assert len(graph.snapshot(dt("2024-08-01"), dt("2025-07-01"))) == 1


def test_duplicate_edge_ids_are_rejected() -> None:
    graph = TemporalResponsibilityGraph()
    item = edge(
        "same",
        valid_start="2024-01-01",
        valid_end=None,
        known_from="2024-01-02",
    )
    graph.add_edge(item)
    try:
        graph.add_edge(item)
    except ValueError as error:
        assert "duplicate edge id" in str(error)
    else:
        raise AssertionError("duplicate edge was accepted")
