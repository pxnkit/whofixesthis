from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DecisionStatus(StrEnum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"


class EvidenceDirection(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"


class Interval(StrictModel):
    start: datetime
    end: datetime | None = None

    @model_validator(mode="after")
    def valid_order(self) -> "Interval":
        if self.end is not None and self.end <= self.start:
            raise ValueError("interval end must be after start")
        return self

    def contains(self, instant: datetime) -> bool:
        return self.start <= instant and (self.end is None or instant < self.end)


class Provenance(StrictModel):
    source_id: str
    authority: str
    canonical_url: str
    retrieved_at: datetime
    checksum: str
    evidence_span: str | None = None


class IssueObservation(StrictModel):
    description: str = Field(min_length=3, max_length=500)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    uncertainty_m: float = Field(default=20, ge=1, le=5000)
    observed_at: datetime
    context_id: str | None = None
    asset_id: str | None = None
    image_refs: list[str] = Field(default_factory=list, max_length=4)
    category_distribution: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_distribution(self) -> "IssueObservation":
        if self.category_distribution:
            total = sum(self.category_distribution.values())
            if abs(total - 1.0) > 0.02:
                raise ValueError("category distribution must sum to one")
            if any(value < 0 or value > 1 for value in self.category_distribution.values()):
                raise ValueError("category probabilities must be between zero and one")
        return self


class Provider(StrictModel):
    provider_id: str
    name: str
    jurisdiction: str
    valid_time: Interval
    contact_endpoint: str | None = None
    fictional_fixture: bool = True


class ServiceDefinition(StrictModel):
    service_code: str
    name: str
    provider_id: str
    accepted_issue_types: list[str]
    required_fields: list[str]
    valid_time: Interval
    boundary_id: str | None = None


class EvidenceItem(StrictModel):
    evidence_id: str
    title: str
    detail: str
    direction: EvidenceDirection
    weight: float = Field(ge=-1, le=1)
    valid_time: Interval
    transaction_time: Interval
    provenance: Provenance


class ProviderServiceHypothesis(StrictModel):
    hypothesis_id: str
    provider_id: str | None
    provider_name: str
    service_code: str | None
    service_name: str
    score: float = Field(ge=0, le=1)


class DuplicateCandidate(StrictModel):
    case_id: str
    relation: str
    score: float = Field(ge=0, le=1)
    status: str
    same_physical_defect: bool | None = None


class SearchAction(StrictModel):
    action_id: str
    source_id: str
    query: str
    permission: str
    cost: float = Field(ge=0)
    expected_latency_ms: int = Field(ge=0)
    revealed_evidence_ids: list[str] = Field(default_factory=list)


class ResponsibilityDecision(StrictModel):
    case_id: str | None = None
    status: DecisionStatus
    provider_id: str | None = None
    provider_name: str | None = None
    service_code: str | None = None
    service_name: str | None = None
    confidence: float = Field(ge=0, le=1)
    hypotheses: list[ProviderServiceHypothesis]
    supporting_evidence: list[EvidenceItem]
    contradicting_evidence: list[EvidenceItem]
    duplicate_candidates: list[DuplicateCandidate] = Field(default_factory=list)
    unresolved_reason: str | None = None
    next_action: str | None = None
    escalation_path: list[str] = Field(default_factory=list)
    counterfactual: str
    decision_time: datetime
    action_trace: list[str] = Field(default_factory=list)


class ResolveRequest(StrictModel):
    case_id: str | None = None
    observation: IssueObservation | None = None
    reveal_all: bool = True

    @model_validator(mode="after")
    def has_input(self) -> "ResolveRequest":
        if not self.case_id and not self.observation:
            raise ValueError("case_id or observation is required")
        return self


class PreparedReportRequest(StrictModel):
    observation: IssueObservation
    decision: ResponsibilityDecision


class ApprovalRequest(StrictModel):
    report_id: str
    approved: bool
    preview_hash: str


class BenchmarkSummary(StrictModel):
    cases: int
    provider_accuracy: float
    service_accuracy: float
    joint_accuracy: float
    abstention_accuracy: float
    duplicate_accuracy: float
    wrong_jurisdiction_rate: float
    coverage: float
    mean_confidence: float
    fixture_checksum: str
    note: str


JsonObject = dict[str, Any]
