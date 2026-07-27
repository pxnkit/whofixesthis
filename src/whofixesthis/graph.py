from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from .models import Interval, Provenance, StrictModel


class ResponsibilityRelation(StrEnum):
    OWNS = "owns"
    MAINTAINS = "maintains"
    DELEGATES = "delegates"
    OPERATES = "operates"
    COVERED_BY = "covered_by"
    REPORTS = "reports"
    DUPLICATES = "duplicates"
    SUPERSEDES = "supersedes"
    ESCALATES = "escalates"


class ResponsibilityEdge(StrictModel):
    edge_id: str
    subject_id: str
    relation: ResponsibilityRelation
    object_id: str
    valid_time: Interval
    transaction_time: Interval
    confidence: float = Field(ge=0, le=1)
    provenance: Provenance

    def visible_at(self, event_time: datetime, decision_time: datetime) -> bool:
        return (
            self.valid_time.contains(event_time)
            and self.transaction_time.contains(decision_time)
            and self.transaction_time.start <= decision_time
        )


class TemporalResponsibilityGraph:
    """Small typed graph with explicit valid and transaction time semantics."""

    def __init__(self, edges: list[ResponsibilityEdge] | None = None) -> None:
        self._edges: dict[str, ResponsibilityEdge] = {}
        for edge in edges or []:
            self.add_edge(edge)

    def add_edge(self, edge: ResponsibilityEdge) -> None:
        if edge.edge_id in self._edges:
            raise ValueError(f"duplicate edge id {edge.edge_id}")
        self._edges[edge.edge_id] = edge

    def snapshot(self, event_time: datetime, decision_time: datetime) -> list[ResponsibilityEdge]:
        return sorted(
            (
                edge
                for edge in self._edges.values()
                if edge.visible_at(event_time, decision_time)
            ),
            key=lambda edge: edge.edge_id,
        )

    def objects(
        self,
        subject_id: str,
        relation: ResponsibilityRelation,
        event_time: datetime,
        decision_time: datetime,
    ) -> list[str]:
        return [
            edge.object_id
            for edge in self.snapshot(event_time, decision_time)
            if edge.subject_id == subject_id and edge.relation == relation
        ]

    def checksum_material(self) -> str:
        return "\n".join(
            edge.model_dump_json()
            for edge in sorted(self._edges.values(), key=lambda item: item.edge_id)
        )
