from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "fixtures" / "fixroutebench.jsonl"
UTC = timezone.utc


PATTERNS = [
    {
        "family": "state_road",
        "title": "City boundary on a regional route",
        "jurisdiction": "Harbor City",
        "context_id": "harbor-boundary",
        "description": "Pothole in the travel lane beside regional Route 17 marker",
        "provider_id": "regional-roads",
        "provider_name": "Regional Roads Authority",
        "service_code": "SR-07",
        "service_name": "State route surface defect",
        "alternative": ("harbor-public-realm", "Harbor City Public Realm", "HC-ROAD-02", "Local street repair"),
        "duplicate": False,
    },
    {
        "family": "local_road",
        "title": "Parallel local street beside a state road",
        "jurisdiction": "Northbank",
        "context_id": "northbank-local-road",
        "description": "Broken road surface on the local service lane parallel to Route 17",
        "provider_id": "northbank-streets",
        "provider_name": "Northbank Streets",
        "service_code": "NB-RD-11",
        "service_name": "Local road maintenance",
        "alternative": ("regional-roads", "Regional Roads Authority", "SR-07", "State route surface defect"),
        "duplicate": False,
    },
    {
        "family": "transit_property",
        "title": "Station entrance embedded in a sidewalk",
        "jurisdiction": "Northbank",
        "context_id": "northbank-transit",
        "description": "Failed light attached to the canopy over a station entrance",
        "provider_id": "northbank-transit",
        "provider_name": "Northbank Transit Operations",
        "service_code": "TR-LIGHT",
        "service_name": "Station entrance lighting",
        "alternative": ("northbank-streets", "Northbank Streets", "NB-LGT-01", "Public lighting"),
        "duplicate": False,
    },
    {
        "family": "utility_attachment",
        "title": "Shared pole with multiple attached assets",
        "jurisdiction": "Northbank",
        "context_id": "northbank-utility",
        "description": "Damaged public lighting fixture on a shared utility pole",
        "provider_id": "northbank-streets",
        "provider_name": "Northbank Streets",
        "service_code": "NB-LGT-01",
        "service_name": "Public lighting",
        "alternative": (None, "Unknown utility", None, "Attachment fault"),
        "duplicate": False,
    },
    {
        "family": "private_frontage",
        "title": "Private frontage at a public sidewalk",
        "jurisdiction": "Harbor City",
        "context_id": "harbor-frontage",
        "description": "Loose private sign overhangs the sidewalk from a shop frontage",
        "provider_id": None,
        "provider_name": "Private frontage responsibility",
        "service_code": None,
        "service_name": "No supported public reporting route",
        "alternative": ("harbor-public-realm", "Harbor City Public Realm", "HC-WALK-04", "Sidewalk obstruction"),
        "duplicate": False,
    },
    {
        "family": "active_permit",
        "title": "Contractor obligation during active works",
        "jurisdiction": "Harbor City",
        "context_id": "harbor-works",
        "description": "Construction barriers block the sidewalk inside an active permit area",
        "provider_id": "harbor-works",
        "provider_name": "Harbor City Works Coordination",
        "service_code": "HC-PERMIT-08",
        "service_name": "Active permit obstruction",
        "alternative": ("harbor-public-realm", "Harbor City Public Realm", "HC-WALK-04", "Sidewalk obstruction"),
        "duplicate": False,
    },
    {
        "family": "boundary_ambiguity",
        "title": "Coordinate exactly on a jurisdiction boundary",
        "jurisdiction": "Harbor City and Northbank",
        "context_id": "shared-boundary",
        "description": "Surface defect centered on the mapped municipal boundary",
        "provider_id": None,
        "provider_name": "Shared boundary responsibility",
        "service_code": None,
        "service_name": "No sufficiently supported route",
        "alternative": ("northbank-streets", "Northbank Streets", "NB-RD-11", "Local road maintenance"),
        "duplicate": False,
    },
    {
        "family": "duplicate_open",
        "title": "Nearby open report on the same asset",
        "jurisdiction": "Harbor City",
        "context_id": "harbor-lighting",
        "description": "Street light is dark beside asset label HC-L-204",
        "provider_id": "harbor-public-realm",
        "provider_name": "Harbor City Public Realm",
        "service_code": "HC-LGT-02",
        "service_name": "Street lighting fault",
        "alternative": ("northbank-streets", "Northbank Streets", "NB-LGT-01", "Public lighting"),
        "duplicate": True,
    },
    {
        "family": "service_version",
        "title": "Service code changed between snapshots",
        "jurisdiction": "Harbor City",
        "context_id": "harbor-lighting",
        "description": "Street light fault reported against the historical service catalog",
        "provider_id": "harbor-public-realm",
        "provider_name": "Harbor City Public Realm",
        "service_code": "HC-LGT-02",
        "service_name": "Street lighting fault",
        "alternative": ("harbor-public-realm", "Harbor City Public Realm", "HC-LGT-01", "Legacy lighting service"),
        "duplicate": False,
    },
    {
        "family": "historical_misroute",
        "title": "Historical ticket closed by the wrong provider",
        "jurisdiction": "Northbank",
        "context_id": "northbank-local-road",
        "description": "Sidewalk defect beside a road historically routed to the regional authority",
        "provider_id": "northbank-streets",
        "provider_name": "Northbank Streets",
        "service_code": "NB-WALK-03",
        "service_name": "Sidewalk repair",
        "alternative": ("regional-roads", "Regional Roads Authority", "SR-07", "State route surface defect"),
        "duplicate": False,
    },
]


def iso(value: datetime) -> str:
    return value.isoformat()


def checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def evidence(
    case_id: str,
    number: int,
    *,
    title: str,
    detail: str,
    direction: str,
    weight: float,
    target: str,
    visible: bool,
    valid_start: datetime,
    valid_end: datetime | None,
    transaction_start: datetime,
) -> dict[str, object]:
    evidence_id = f"{case_id}-ev-{number}"
    return {
        "evidence_id": evidence_id,
        "title": title,
        "detail": detail,
        "direction": direction,
        "weight": weight,
        "target_hypothesis_id": target,
        "initially_visible": visible,
        "valid_start": iso(valid_start),
        "valid_end": iso(valid_end) if valid_end else None,
        "transaction_start": iso(transaction_start),
        "transaction_end": None,
        "source_id": f"fixture-{title.lower().replace(' ', '-')}",
        "authority": "Fictional benchmark authority",
        "canonical_url": f"https://fixtures.invalid/{case_id}/{evidence_id}",
        "retrieved_at": iso(transaction_start),
        "checksum": checksum(f"{case_id}:{evidence_id}:{detail}"),
        "evidence_span": detail,
    }


def build_case(pattern: dict[str, object], variant: int, index: int) -> dict[str, object]:
    case_id = f"frb-{index:03d}"
    observed = datetime(2025, 7, 10, 9, 0, tzinfo=UTC) + timedelta(days=variant * 7)
    uncertainty = 8 + variant * 3
    provider_id = pattern["provider_id"]
    service_code = pattern["service_code"]
    status = "resolved" if provider_id and service_code else "unresolved"

    if pattern["family"] == "utility_attachment" and variant >= 3:
        provider_id = None
        service_code = None
        status = "unresolved"
        uncertainty = 32 + variant * 4

    if pattern["family"] == "service_version" and variant < 2:
        observed = datetime(2024, 10, 10, 9, 0, tzinfo=UTC) + timedelta(days=variant * 20)
        service_code = "HC-LGT-01"

    top_id = f"{case_id}-primary"
    alt_id = f"{case_id}-alternative"
    unknown_id = f"{case_id}-open-set"
    alternative = pattern["alternative"]
    assert isinstance(alternative, tuple)

    top_base = 0.42 if status == "resolved" else 0.45
    alt_base = 0.38 if status == "resolved" else 0.43
    primary_valid_end = None
    if pattern["family"] == "service_version" and service_code == "HC-LGT-01":
        primary_valid_end = datetime(2025, 1, 1, tzinfo=UTC)
    primary_valid_start = (
        datetime(2020, 1, 1, tzinfo=UTC)
        if service_code != "HC-LGT-02"
        else datetime(2025, 1, 1, tzinfo=UTC)
    )

    evidence_rows = [
        evidence(
            case_id,
            1,
            title="Spatial candidate",
            detail="The observation intersects the candidate asset or service boundary",
            direction="supports",
            weight=0.08 if status == "unresolved" else 0.20,
            target=top_id,
            visible=True,
            valid_start=primary_valid_start,
            valid_end=primary_valid_end,
            transaction_start=datetime(2024, 1, 15, tzinfo=UTC),
        ),
        evidence(
            case_id,
            2,
            title="Dated responsibility record",
            detail="The frozen record assigns the maintenance obligation at event time",
            direction="supports",
            weight=0.04 if status == "unresolved" else 0.19,
            target=top_id,
            visible=False,
            valid_start=primary_valid_start,
            valid_end=primary_valid_end,
            transaction_start=datetime(2024, 2, 1, tzinfo=UTC),
        ),
        evidence(
            case_id,
            3,
            title="Competing jurisdiction",
            detail="A nearby boundary or historical route supports a competing provider",
            direction="supports",
            weight=0.07 if status == "unresolved" else 0.03,
            target=alt_id,
            visible=True,
            valid_start=datetime(2020, 1, 1, tzinfo=UTC),
            valid_end=None,
            transaction_start=datetime(2024, 1, 20, tzinfo=UTC),
        ),
        evidence(
            case_id,
            4,
            title="Service compatibility",
            detail="The issue and required evidence are compatible with the dated service definition",
            direction="supports",
            weight=0.03 if status == "unresolved" else 0.16,
            target=top_id,
            visible=False,
            valid_start=primary_valid_start,
            valid_end=primary_valid_end,
            transaction_start=datetime(2024, 3, 1, tzinfo=UTC),
        ),
        evidence(
            case_id,
            5,
            title="Historical agency field",
            detail="A prior ticket names a different agency and is retained only as noisy evidence",
            direction="contradicts",
            weight=-0.02,
            target=top_id,
            visible=False,
            valid_start=datetime(2020, 1, 1, tzinfo=UTC),
            valid_end=None,
            transaction_start=datetime(2024, 3, 10, tzinfo=UTC),
        ),
    ]

    if pattern["family"] == "active_permit":
        for row in evidence_rows[:2]:
            row["valid_start"] = iso(datetime(2025, 6, 1, tzinfo=UTC))
            row["valid_end"] = iso(datetime(2025, 8, 31, 23, 59, tzinfo=UTC))

    actions = [
        {
            "action_id": f"{case_id}-ownership",
            "source_id": "frozen-asset-register",
            "query": "Inspect dated ownership and maintenance record",
            "cost": 1.0,
            "latency_ms": 30,
            "evidence_ids": [evidence_rows[1]["evidence_id"]],
        },
        {
            "action_id": f"{case_id}-service",
            "source_id": "frozen-service-catalog",
            "query": "Inspect decision-time service definition",
            "cost": 0.5,
            "latency_ms": 20,
            "evidence_ids": [evidence_rows[3]["evidence_id"]],
        },
        {
            "action_id": f"{case_id}-history",
            "source_id": "frozen-ticket-history",
            "query": "Inspect noisy historical routing field",
            "cost": 0.3,
            "latency_ms": 15,
            "evidence_ids": [evidence_rows[4]["evidence_id"]],
        },
    ]

    duplicates = []
    if pattern["duplicate"]:
        duplicates = [
            {
                "case_id": f"historic-{index:03d}",
                "relation": "same physical asset and active issue class",
                "score": round(0.89 + variant * 0.01, 2),
                "status": "open",
                "same_physical_defect": True,
            }
        ]

    return {
        "case_id": case_id,
        "title": f"{pattern['title']} {variant + 1}",
        "family": pattern["family"],
        "jurisdiction": pattern["jurisdiction"],
        "decision_time": iso(datetime(2025, 10, 15, 12, 0, tzinfo=UTC)),
        "observation": {
            "description": f"{pattern['description']} #{variant + 1}",
            "latitude": round(52.5200 + index * 0.0001, 6),
            "longitude": round(13.4000 + index * 0.0001, 6),
            "uncertainty_m": uncertainty,
            "observed_at": iso(observed),
            "context_id": pattern["context_id"],
            "asset_id": None if status == "unresolved" else f"ASSET-{index:03d}",
            "image_refs": [],
            "category_distribution": {},
        },
        "hypotheses": [
            {
                "hypothesis_id": top_id,
                "provider_id": provider_id,
                "provider_name": pattern["provider_name"],
                "service_code": service_code,
                "service_name": pattern["service_name"],
                "base_score": top_base,
            },
            {
                "hypothesis_id": alt_id,
                "provider_id": alternative[0],
                "provider_name": alternative[1],
                "service_code": alternative[2],
                "service_name": alternative[3],
                "base_score": alt_base,
            },
            {
                "hypothesis_id": unknown_id,
                "provider_id": None,
                "provider_name": "Unknown or shared responsibility",
                "service_code": None,
                "service_name": "No supported route",
                "base_score": 0.30,
            },
        ],
        "evidence": evidence_rows,
        "actions": actions,
        "duplicates": duplicates,
        "gold": {
            "status": status,
            "provider_id": provider_id if status == "resolved" else None,
            "service_code": service_code if status == "resolved" else None,
            "duplicate": bool(pattern["duplicate"]),
            "minimum_sufficient_evidence": [
                evidence_rows[0]["evidence_id"],
                evidence_rows[1]["evidence_id"],
                evidence_rows[3]["evidence_id"],
            ],
        },
        "unresolved_reason": (
            "Public records do not distinguish the competing responsibility hypotheses"
            if status == "unresolved"
            else None
        ),
        "next_action": (
            "Request one asset identifier or a more precise map correction"
            if status == "unresolved"
            else "Review required fields and likely duplicates before local export"
        ),
        "escalation_path": [
            "Record any wrong-jurisdiction rejection reason",
            "Rebuild the decision from evidence valid at the rejection time",
            "Offer the next documented official channel after user review",
        ],
        "counterfactual": (
            "A verified identifier or a dated maintenance record would separate the top candidates"
            if status == "unresolved"
            else "A superseding dated ownership or service record would change the selected route"
        ),
        "historical_label_limit": (
            "Historical submitted and closing agency fields are weak labels only"
        ),
    }


def main() -> None:
    cases = []
    index = 1
    for pattern in PATTERNS:
        for variant in range(5):
            cases.append(build_case(pattern, variant, index))
            index += 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        json.dumps(case, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        for case in cases
    ) + "\n"
    OUTPUT.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote {len(cases)} fixtures to {OUTPUT}")
    print(hashlib.sha256(content.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main()
