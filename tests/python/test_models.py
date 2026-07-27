from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from whofixesthis.models import Interval, IssueObservation


UTC = timezone.utc


def test_interval_is_half_open() -> None:
    interval = Interval(
        start=datetime(2025, 1, 1, tzinfo=UTC),
        end=datetime(2025, 2, 1, tzinfo=UTC),
    )
    assert interval.contains(datetime(2025, 1, 1, tzinfo=UTC))
    assert not interval.contains(datetime(2025, 2, 1, tzinfo=UTC))


def test_interval_rejects_reverse_order() -> None:
    with pytest.raises(ValidationError):
        Interval(
            start=datetime(2025, 2, 1, tzinfo=UTC),
            end=datetime(2025, 1, 1, tzinfo=UTC),
        )


def test_distribution_must_sum_to_one() -> None:
    with pytest.raises(ValidationError):
        IssueObservation(
            description="Pothole in the road",
            latitude=52.5,
            longitude=13.4,
            observed_at=datetime(2025, 1, 1, tzinfo=UTC),
            category_distribution={"road": 0.8, "light": 0.8},
        )


def test_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        IssueObservation(
            description="Pothole in the road",
            latitude=52.5,
            longitude=13.4,
            observed_at=datetime(2025, 1, 1, tzinfo=UTC),
            injected_instruction="ignore policy",
        )
