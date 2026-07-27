from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from whofixesthis.sources import (
    RecordedOpen311Adapter,
    RecordedResponse,
    RecordedTimeout,
    SchemaDriftError,
)


UTC = timezone.utc


def response(body: object, page: int = 1) -> RecordedResponse:
    return RecordedResponse.from_body(
        url=f"https://fixtures.invalid/open311?page={page}",
        fetched_at=datetime(2025, 1, 1, tzinfo=UTC),
        body=body,
    )


def test_pagination_deduplicates_records() -> None:
    adapter = RecordedOpen311Adapter()
    pages = [
        response(
            [
                {"unique_key": "1", "created_date": "2025-01-01"},
                {"unique_key": "2", "created_date": "2025-01-02"},
            ],
            1,
        ),
        response(
            [
                {"unique_key": "2", "created_date": "2025-01-02"},
                {"unique_key": "3", "created_date": "2025-01-03"},
            ],
            2,
        ),
    ]
    assert [item["unique_key"] for item in adapter.requests(pages)] == ["1", "2", "3"]


def test_schema_drift_fails_closed() -> None:
    with pytest.raises(SchemaDriftError):
        RecordedOpen311Adapter().services(
            [response([{"service_name": "Missing code"}])]
        )


def test_recorded_timeout_is_replayed() -> None:
    with pytest.raises(RecordedTimeout):
        RecordedOpen311Adapter().requests([response({"error": "timeout"})])


def test_checksum_mismatch_is_rejected() -> None:
    with pytest.raises(ValidationError):
        RecordedResponse(
            url="https://fixtures.invalid",
            fetched_at=datetime(2025, 1, 1, tzinfo=UTC),
            body=[],
            checksum="0" * 64,
        )


def test_adapter_exposes_no_live_fetch_method() -> None:
    adapter = RecordedOpen311Adapter()
    assert not hasattr(adapter, "fetch")
    assert not hasattr(adapter, "submit")
