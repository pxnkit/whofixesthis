from whofixesthis.acquisition import AcquisitionCandidate, choose_next_action
from whofixesthis.retrieval import DuplicateFeatures, assess_duplicate


def test_same_asset_different_issue_is_not_suppressed() -> None:
    result = assess_duplicate(
        DuplicateFeatures(
            distance_m=2,
            same_asset=True,
            same_issue_class=False,
            text_similarity=0.9,
            image_similarity=0.9,
            days_apart=1,
            prior_status="open",
        )
    )
    assert result.relation == "same asset, different defect"
    assert not result.suppress_new_report


def test_reopened_issue_after_closure_is_not_suppressed() -> None:
    result = assess_duplicate(
        DuplicateFeatures(
            distance_m=1,
            same_asset=True,
            same_issue_class=True,
            text_similarity=0.95,
            image_similarity=0.95,
            days_apart=60,
            prior_status="closed",
        )
    )
    assert result.relation == "recurring defect after closure"
    assert not result.suppress_new_report


def test_strong_open_duplicate_can_be_suppressed() -> None:
    result = assess_duplicate(
        DuplicateFeatures(
            distance_m=1,
            same_asset=True,
            same_issue_class=True,
            text_similarity=0.98,
            image_similarity=0.98,
            days_apart=1,
            prior_status="open",
        )
    )
    assert result.relation == "same physical defect"
    assert result.suppress_new_report


def test_acquisition_uses_conservative_cost_normalized_value() -> None:
    choice = choose_next_action(
        [
            AcquisitionCandidate("cheap", 0.4, 0.1, 0.05, 20),
            AcquisitionCandidate("expensive", 0.6, 0.2, 0.4, 200),
        ]
    )
    assert choice is not None
    assert choice.action_id == "cheap"


def test_acquisition_stops_when_no_action_has_positive_value() -> None:
    choice = choose_next_action(
        [AcquisitionCandidate("lossy", 0.1, 0.5, 0.2, 500)]
    )
    assert choice is None


def test_disallowed_action_is_never_selected() -> None:
    choice = choose_next_action(
        [AcquisitionCandidate("submit", 1.0, 0.0, 0.0, 0, allowed=False)]
    )
    assert choice is None
