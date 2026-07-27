import copy

from whofixesthis.benchmark import run_benchmark
from whofixesthis.engine import EvidenceDirectedResolver
from whofixesthis.fixtures import find_case, load_cases
from whofixesthis.models import DecisionStatus


def test_fixture_count_and_ids() -> None:
    cases = load_cases()
    assert len(cases) == 50
    assert len({case["case_id"] for case in cases}) == 50


def test_state_road_case_resolves() -> None:
    decision = EvidenceDirectedResolver().resolve_case("frb-001")
    assert decision.status == DecisionStatus.RESOLVED
    assert decision.provider_id == "regional-roads"
    assert decision.service_code == "SR-07"
    assert decision.supporting_evidence


def test_boundary_case_abstains() -> None:
    decision = EvidenceDirectedResolver().resolve_case("frb-031")
    assert decision.status == DecisionStatus.UNRESOLVED
    assert decision.provider_id is None
    assert decision.unresolved_reason


def test_initial_evidence_has_lower_or_equal_confidence() -> None:
    resolver = EvidenceDirectedResolver()
    initial = resolver.resolve_case("frb-001", reveal_all=False)
    full = resolver.resolve_case("frb-001", reveal_all=True)
    assert initial.confidence <= full.confidence
    assert len(initial.action_trace) == 0
    assert len(full.action_trace) == 3


def test_location_uncertainty_is_monotonic() -> None:
    case = find_case("frb-001")
    broad = copy.deepcopy(case)
    broad["observation"]["uncertainty_m"] = 100
    resolver = EvidenceDirectedResolver()
    assert resolver.resolve_case(broad).confidence <= resolver.resolve_case(case).confidence


def test_benchmark_smoke_contract() -> None:
    summary, rows = run_benchmark()
    assert summary.cases == 50
    assert len(rows) == 50
    assert summary.joint_accuracy == 1.0
    assert summary.abstention_accuracy == 1.0
    assert "not evidence" in summary.note
