from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DuplicateFeatures:
    distance_m: float
    same_asset: bool
    same_issue_class: bool
    text_similarity: float
    image_similarity: float | None
    days_apart: float
    prior_status: str


@dataclass(frozen=True)
class DuplicateAssessment:
    score: float
    relation: str
    suppress_new_report: bool


def assess_duplicate(features: DuplicateFeatures) -> DuplicateAssessment:
    spatial = max(0.0, 1.0 - features.distance_m / 100.0)
    temporal = max(0.0, 1.0 - features.days_apart / 180.0)
    image = features.image_similarity if features.image_similarity is not None else 0.5
    score = (
        0.25 * spatial
        + 0.25 * float(features.same_asset)
        + 0.20 * float(features.same_issue_class)
        + 0.15 * features.text_similarity
        + 0.10 * image
        + 0.05 * temporal
    )

    if features.same_asset and not features.same_issue_class:
        return DuplicateAssessment(round(score, 4), "same asset, different defect", False)
    if features.prior_status == "closed" and features.days_apart > 14:
        return DuplicateAssessment(round(score, 4), "recurring defect after closure", False)
    if score >= 0.82 and features.same_asset and features.same_issue_class:
        return DuplicateAssessment(round(score, 4), "same physical defect", True)
    return DuplicateAssessment(round(score, 4), "nearby distinct issue", False)
