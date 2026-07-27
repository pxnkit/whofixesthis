from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AcquisitionCandidate:
    action_id: str
    expected_loss_reduction: float
    uncertainty_discount: float
    cost: float
    latency_ms: int
    allowed: bool = True

    @property
    def conservative_value(self) -> float:
        benefit = self.expected_loss_reduction * (1.0 - self.uncertainty_discount)
        acquisition_cost = self.cost + self.latency_ms / 10_000.0
        return benefit - acquisition_cost


def choose_next_action(candidates: list[AcquisitionCandidate]) -> AcquisitionCandidate | None:
    allowed = [candidate for candidate in candidates if candidate.allowed]
    if not allowed:
        return None
    ranked = sorted(
        allowed,
        key=lambda item: (-item.conservative_value, item.cost, item.action_id),
    )
    return ranked[0] if ranked[0].conservative_value > 0 else None
