from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from pydantic import Field, model_validator

from ..models import StrictModel


class SchemaDriftError(ValueError):
    pass


class RecordedTimeout(RuntimeError):
    pass


class RecordedResponse(StrictModel):
    url: str
    fetched_at: datetime
    headers: dict[str, str] = Field(default_factory=dict)
    body: list[dict[str, Any]] | dict[str, Any]
    checksum: str

    @model_validator(mode="after")
    def checksum_matches(self) -> "RecordedResponse":
        canonical = json.dumps(
            self.body,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        actual = hashlib.sha256(canonical).hexdigest()
        if actual != self.checksum:
            raise ValueError("recorded response checksum mismatch")
        return self

    @classmethod
    def from_body(
        cls,
        *,
        url: str,
        fetched_at: datetime,
        body: list[dict[str, Any]] | dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> "RecordedResponse":
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
        return cls(
            url=url,
            fetched_at=fetched_at,
            headers=headers or {},
            body=body,
            checksum=hashlib.sha256(canonical).hexdigest(),
        )


class RecordedOpen311Adapter:
    """Parser for archived Open311-like responses with no network methods."""

    SERVICE_REQUIRED = {"service_code", "service_name"}
    REQUEST_REQUIRED = {"unique_key", "created_date"}

    def services(self, pages: list[RecordedResponse]) -> list[dict[str, Any]]:
        return self._merge_pages(pages, self.SERVICE_REQUIRED, "service_code")

    def requests(self, pages: list[RecordedResponse]) -> list[dict[str, Any]]:
        return self._merge_pages(pages, self.REQUEST_REQUIRED, "unique_key")

    @staticmethod
    def _merge_pages(
        pages: list[RecordedResponse],
        required: set[str],
        unique_field: str,
    ) -> list[dict[str, Any]]:
        merged: dict[str, dict[str, Any]] = {}
        for page in pages:
            if isinstance(page.body, dict) and page.body.get("error") == "timeout":
                raise RecordedTimeout(f"recorded timeout at {page.url}")
            if not isinstance(page.body, list):
                raise SchemaDriftError("expected a list response")
            for record in page.body:
                missing = required - record.keys()
                if missing:
                    fields = ", ".join(sorted(missing))
                    raise SchemaDriftError(f"missing required fields: {fields}")
                key = str(record[unique_field])
                if key not in merged:
                    merged[key] = record
        return [merged[key] for key in sorted(merged)]
