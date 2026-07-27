from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from .engine import EvidenceDirectedResolver
from .fixtures import DEFAULT_FIXTURE_PATH, fixture_checksum, load_cases
from .models import BenchmarkSummary, DecisionStatus


@dataclass(frozen=True)
class EpisodeResult:
    case_id: str
    family: str
    gold_status: str
    predicted_status: str
    gold_provider_id: str | None
    predicted_provider_id: str | None
    gold_service_code: str | None
    predicted_service_code: str | None
    confidence: float
    duplicate_expected: bool
    duplicate_predicted: bool

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def run_benchmark(
    fixture_path: Path | str = DEFAULT_FIXTURE_PATH,
    *,
    threshold: float = 0.72,
    margin: float = 0.12,
) -> tuple[BenchmarkSummary, list[EpisodeResult]]:
    cases = load_cases(fixture_path)
    resolver = EvidenceDirectedResolver(threshold=threshold, margin=margin)
    rows: list[EpisodeResult] = []

    for case in cases:
        decision = resolver.resolve_case(case, reveal_all=True)
        gold = case["gold"]
        rows.append(
            EpisodeResult(
                case_id=case["case_id"],
                family=case["family"],
                gold_status=gold["status"],
                predicted_status=decision.status.value,
                gold_provider_id=gold.get("provider_id"),
                predicted_provider_id=decision.provider_id,
                gold_service_code=gold.get("service_code"),
                predicted_service_code=decision.service_code,
                confidence=decision.confidence,
                duplicate_expected=bool(gold.get("duplicate", False)),
                duplicate_predicted=bool(decision.duplicate_candidates),
            )
        )

    count = len(rows)
    resolved_gold = [row for row in rows if row.gold_status == DecisionStatus.RESOLVED]
    unresolved_gold = [row for row in rows if row.gold_status == DecisionStatus.UNRESOLVED]
    provider_accuracy = mean(
        row.predicted_provider_id == row.gold_provider_id for row in rows
    )
    service_accuracy = mean(
        row.predicted_service_code == row.gold_service_code for row in rows
    )
    joint_accuracy = mean(
        row.predicted_provider_id == row.gold_provider_id
        and row.predicted_service_code == row.gold_service_code
        and row.predicted_status == row.gold_status
        for row in rows
    )
    abstention_accuracy = (
        mean(row.predicted_status == DecisionStatus.UNRESOLVED for row in unresolved_gold)
        if unresolved_gold
        else 1.0
    )
    duplicate_accuracy = mean(
        row.duplicate_predicted == row.duplicate_expected for row in rows
    )
    wrong_jurisdiction_rate = (
        mean(row.predicted_provider_id != row.gold_provider_id for row in resolved_gold)
        if resolved_gold
        else 0.0
    )
    coverage = mean(row.predicted_status == DecisionStatus.RESOLVED for row in rows)

    summary = BenchmarkSummary(
        cases=count,
        provider_accuracy=round(provider_accuracy, 4),
        service_accuracy=round(service_accuracy, 4),
        joint_accuracy=round(joint_accuracy, 4),
        abstention_accuracy=round(abstention_accuracy, 4),
        duplicate_accuracy=round(duplicate_accuracy, 4),
        wrong_jurisdiction_rate=round(wrong_jurisdiction_rate, 4),
        coverage=round(coverage, 4),
        mean_confidence=round(mean(row.confidence for row in rows), 4),
        fixture_checksum=fixture_checksum(fixture_path),
        note=(
            "Deterministic fictional fixture smoke test only. "
            "These values are not evidence of real-world routing performance."
        ),
    )
    return summary, rows


def write_results(
    output_dir: Path,
    summary: BenchmarkSummary,
    rows: list[EpisodeResult],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        summary.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "predictions.jsonl").write_text(
        "\n".join(json.dumps(row.as_dict(), sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
