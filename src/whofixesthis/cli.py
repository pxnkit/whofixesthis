from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import yaml

from .benchmark import run_benchmark, write_results
from .engine import EvidenceDirectedResolver
from .fixtures import DEFAULT_FIXTURE_PATH, fixture_checksum


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="whofixesthis",
        description="Temporal responsibility routing research tools",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Validate a frozen source configuration")
    ingest.add_argument("--jurisdiction", required=True, type=Path)

    benchmark = subparsers.add_parser("benchmark", help="Run FixRouteBench")
    benchmark.add_argument("--config", type=Path, default=Path("configs/smoke.yaml"))
    benchmark.add_argument("--output", type=Path)

    resolve = subparsers.add_parser("resolve", help="Resolve one frozen benchmark case")
    resolve.add_argument("--case", required=True)
    resolve.add_argument("--initial-only", action="store_true")

    reproduce = subparsers.add_parser("reproduce", help="Reproduce a saved benchmark manifest")
    reproduce.add_argument("--manifest", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "ingest":
        config = yaml.safe_load(args.jurisdiction.read_text(encoding="utf-8"))
        print(
            json.dumps(
                {
                    "status": "validated",
                    "jurisdiction": config["jurisdiction"]["name"],
                    "mode": "frozen-only",
                    "live_fetch": False,
                },
                indent=2,
            )
        )
        return 0

    if args.command == "benchmark":
        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        fixture_path = Path(config.get("fixture_path", DEFAULT_FIXTURE_PATH))
        summary, rows = run_benchmark(
            fixture_path,
            threshold=float(config["resolver"]["threshold"]),
            margin=float(config["resolver"]["margin"]),
        )
        if args.output:
            write_results(args.output, summary, rows)
        print(summary.model_dump_json(indent=2))
        return 0

    if args.command == "resolve":
        decision = EvidenceDirectedResolver().resolve_case(
            args.case,
            reveal_all=not args.initial_only,
        )
        print(decision.model_dump_json(indent=2))
        return 0

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    actual_checksum = fixture_checksum(manifest["fixture_path"])
    if actual_checksum != manifest["fixture_checksum"]:
        raise SystemExit("fixture checksum does not match the manifest")
    summary, _ = run_benchmark(
        manifest["fixture_path"],
        threshold=manifest["threshold"],
        margin=manifest["margin"],
    )
    print(summary.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
