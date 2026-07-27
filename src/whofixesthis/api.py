from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status

from .benchmark import run_benchmark
from .engine import EvidenceDirectedResolver
from .fixtures import fixture_checksum, load_cases
from .models import (
    ApprovalRequest,
    PreparedReportRequest,
    ResolveRequest,
    ResponsibilityDecision,
)


app = FastAPI(
    title="WhoFixesThis API",
    version="0.1.0",
    description="Offline-first temporal responsibility routing research API",
)
resolver = EvidenceDirectedResolver()


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "frozen-fixtures",
        "cases": len(load_cases()),
        "fixture_checksum": fixture_checksum(),
        "external_mutations": False,
    }


@app.get("/v1/cases")
def list_fixture_cases() -> list[dict[str, str]]:
    return [
        {
            "case_id": case["case_id"],
            "title": case["title"],
            "family": case["family"],
            "jurisdiction": case["jurisdiction"],
        }
        for case in load_cases()
    ]


@app.post("/v1/resolve", response_model=ResponsibilityDecision)
def resolve(request: ResolveRequest) -> ResponsibilityDecision:
    try:
        if request.case_id:
            return resolver.resolve_case(request.case_id, reveal_all=request.reveal_all)
        assert request.observation is not None
        return resolver.resolve_observation(
            request.observation,
            reveal_all=request.reveal_all,
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/v1/benchmark")
def benchmark() -> dict[str, object]:
    summary, rows = run_benchmark()
    return {
        "summary": summary.model_dump(mode="json"),
        "failures": [
            row.as_dict()
            for row in rows
            if row.predicted_provider_id != row.gold_provider_id
            or row.predicted_service_code != row.gold_service_code
        ],
    }


@app.post("/v1/reports/prepare")
def prepare_report(request: PreparedReportRequest) -> dict[str, object]:
    canonical = json.dumps(
        request.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )
    preview_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "report_id": f"prepared-{preview_hash[:16]}",
        "preview_hash": preview_hash,
        "status": "prepared",
        "submission_attempted": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "warning": "No provider has been contacted. Approval applies to local export only.",
    }


@app.post("/v1/reports/approve")
def approve_report(request: ApprovalRequest) -> dict[str, object]:
    if not request.approved:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Explicit approval is required",
        )
    if not request.report_id.startswith("prepared-") or len(request.preview_hash) != 64:
        raise HTTPException(status_code=422, detail="Invalid prepared report reference")
    return {
        "report_id": request.report_id,
        "status": "approved_for_local_export",
        "submission_attempted": False,
        "external_side_effect": False,
    }
