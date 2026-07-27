from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE_PATH = PROJECT_ROOT / "data" / "fixtures" / "fixroutebench.jsonl"


def load_cases(path: Path | str = DEFAULT_FIXTURE_PATH) -> list[dict[str, Any]]:
    fixture_path = Path(path)
    cases = [
        json.loads(line)
        for line in fixture_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ids = [case["case_id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("fixture case ids must be unique")
    return cases


def find_case(case_id: str, path: Path | str = DEFAULT_FIXTURE_PATH) -> dict[str, Any]:
    for case in load_cases(path):
        if case["case_id"] == case_id:
            return case
    raise KeyError(f"unknown fixture case {case_id}")


def fixture_checksum(path: Path | str = DEFAULT_FIXTURE_PATH) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stable_jsonl(rows: Iterable[dict[str, Any]]) -> str:
    return "\n".join(
        json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        for row in rows
    ) + "\n"
