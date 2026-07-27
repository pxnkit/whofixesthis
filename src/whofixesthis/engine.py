from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any

from .fixtures import find_case, load_cases
from .models import (
    DecisionStatus,
    DuplicateCandidate,
    EvidenceDirection,
    EvidenceItem,
    Interval,
    IssueObservation,
    ProviderServiceHypothesis,
    Provenance,
    ResponsibilityDecision,
)


class EvidenceDirectedResolver:
    """Deterministic resolver used by the demo, tests, and benchmark."""

    def __init__(self, threshold: float = 0.72, margin: float = 0.12) -> None:
        self.threshold = threshold
        self.margin = margin

    def resolve_case(
        self,
        case: dict[str, Any] | str,
        *,
        reveal_all: bool = True,
    ) -> ResponsibilityDecision:
        episode = find_case(case) if isinstance(case, str) else copy.deepcopy(case)
        observation = IssueObservation.model_validate(episode["observation"])
        decision_time = datetime.fromisoformat(episode["decision_time"])
        scores = {
            item["hypothesis_id"]: float(item["base_score"])
            for item in episode["hypotheses"]
        }
        included_evidence: list[EvidenceItem] = []
        action_trace: list[str] = []

        for action in episode["actions"]:
            if reveal_all:
                action_trace.append(action["action_id"])

        revealed_ids = {
            evidence_id
            for action in episode["actions"]
            for evidence_id in action["evidence_ids"]
        }

        for raw in episode["evidence"]:
            visible = raw.get("initially_visible", False)
            revealed = raw["evidence_id"] in revealed_ids
            if not visible and not (reveal_all and revealed):
                continue
            evidence = self._evidence_item(raw)
            if not evidence.valid_time.contains(observation.observed_at):
                continue
            if not evidence.transaction_time.contains(decision_time):
                continue
            included_evidence.append(evidence)
            target = raw["target_hypothesis_id"]
            scores[target] = scores.get(target, 0) + float(raw["weight"])

        uncertainty_penalty = max(0.0, observation.uncertainty_m - 20.0) * 0.002
        hypotheses: list[ProviderServiceHypothesis] = []
        by_id = {item["hypothesis_id"]: item for item in episode["hypotheses"]}
        for hypothesis_id, score in scores.items():
            raw = by_id[hypothesis_id]
            hypotheses.append(
                ProviderServiceHypothesis(
                    hypothesis_id=hypothesis_id,
                    provider_id=raw.get("provider_id"),
                    provider_name=raw["provider_name"],
                    service_code=raw.get("service_code"),
                    service_name=raw["service_name"],
                    score=max(0.0, min(0.99, score - uncertainty_penalty)),
                )
            )
        hypotheses.sort(key=lambda item: (-item.score, item.hypothesis_id))

        top = hypotheses[0]
        runner_up = hypotheses[1] if len(hypotheses) > 1 else None
        score_margin = top.score - (runner_up.score if runner_up else 0)
        resolved = (
            top.score >= self.threshold
            and score_margin >= self.margin
            and top.provider_id is not None
            and top.service_code is not None
        )
        status = DecisionStatus.RESOLVED if resolved else DecisionStatus.UNRESOLVED

        supporting = [
            item
            for item in included_evidence
            if item.direction == EvidenceDirection.SUPPORTS
            and self._raw_target(episode, item.evidence_id) == top.hypothesis_id
        ]
        contradicting = [
            item
            for item in included_evidence
            if item.direction == EvidenceDirection.CONTRADICTS
            or self._raw_target(episode, item.evidence_id) != top.hypothesis_id
        ]

        return ResponsibilityDecision(
            case_id=episode["case_id"],
            status=status,
            provider_id=top.provider_id if resolved else None,
            provider_name=top.provider_name if resolved else None,
            service_code=top.service_code if resolved else None,
            service_name=top.service_name if resolved else None,
            confidence=top.score,
            hypotheses=hypotheses,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            duplicate_candidates=[
                DuplicateCandidate.model_validate(item)
                for item in episode.get("duplicates", [])
            ],
            unresolved_reason=None
            if resolved
            else episode.get(
                "unresolved_reason",
                "No provider and service pair passed the calibrated evidence threshold",
            ),
            next_action=episode.get("next_action"),
            escalation_path=episode.get("escalation_path", []),
            counterfactual=episode["counterfactual"],
            decision_time=decision_time,
            action_trace=action_trace,
        )

    def resolve_observation(
        self,
        observation: IssueObservation,
        *,
        reveal_all: bool = True,
    ) -> ResponsibilityDecision:
        cases = load_cases()
        context_matches = [
            case
            for case in cases
            if case["observation"].get("context_id") == observation.context_id
        ]
        if not context_matches:
            text = observation.description.lower()
            family = (
                "transit_property"
                if "station" in text or "transit" in text
                else "active_permit"
                if "permit" in text or "construction" in text
                else "utility_attachment"
                if "pole" in text or "cable" in text
                else "state_road"
            )
            context_matches = [case for case in cases if case["family"] == family]

        template = copy.deepcopy(context_matches[0])
        template["case_id"] = "ad-hoc"
        template["observation"] = observation.model_dump(mode="json")
        template["decision_time"] = datetime.now(timezone.utc).isoformat()
        return self.resolve_case(template, reveal_all=reveal_all)

    @staticmethod
    def _raw_target(episode: dict[str, Any], evidence_id: str) -> str:
        return next(
            item["target_hypothesis_id"]
            for item in episode["evidence"]
            if item["evidence_id"] == evidence_id
        )

    @staticmethod
    def _evidence_item(raw: dict[str, Any]) -> EvidenceItem:
        return EvidenceItem(
            evidence_id=raw["evidence_id"],
            title=raw["title"],
            detail=raw["detail"],
            direction=EvidenceDirection(raw["direction"]),
            weight=raw["weight"],
            valid_time=Interval(
                start=datetime.fromisoformat(raw["valid_start"]),
                end=datetime.fromisoformat(raw["valid_end"])
                if raw.get("valid_end")
                else None,
            ),
            transaction_time=Interval(
                start=datetime.fromisoformat(raw["transaction_start"]),
                end=datetime.fromisoformat(raw["transaction_end"])
                if raw.get("transaction_end")
                else None,
            ),
            provenance=Provenance(
                source_id=raw["source_id"],
                authority=raw["authority"],
                canonical_url=raw["canonical_url"],
                retrieved_at=datetime.fromisoformat(raw["retrieved_at"]),
                checksum=raw["checksum"],
                evidence_span=raw.get("evidence_span"),
            ),
        )
