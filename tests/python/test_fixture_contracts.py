from whofixesthis.fixtures import load_cases


def test_every_fixture_has_replayable_provenance() -> None:
    for case in load_cases():
        evidence_ids = {item["evidence_id"] for item in case["evidence"]}
        revealed_ids = {
            evidence_id
            for action in case["actions"]
            for evidence_id in action["evidence_ids"]
        }
        assert revealed_ids <= evidence_ids
        for item in case["evidence"]:
            assert item["checksum"]
            assert item["authority"]
            assert item["valid_start"]
            assert item["transaction_start"]


def test_minimum_sufficient_evidence_exists() -> None:
    for case in load_cases():
        evidence_ids = {item["evidence_id"] for item in case["evidence"]}
        assert set(case["gold"]["minimum_sufficient_evidence"]) <= evidence_ids


def test_historical_labels_are_explicitly_weak() -> None:
    for case in load_cases():
        assert "weak labels" in case["historical_label_limit"].lower()


def test_fixture_urls_are_non_routable() -> None:
    for case in load_cases():
        for item in case["evidence"]:
            assert item["canonical_url"].startswith("https://fixtures.invalid/")
