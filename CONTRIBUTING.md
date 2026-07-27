# Contributing

## Development setup

Install the web and Python dependencies, then run both test suites before opening a change.

```bash
npm install
npm test
python -m pip install -e ".[dev]"
python -m pytest
```

## Contribution rules

- Keep default tests offline and deterministic
- Preserve valid-time and transaction-time semantics
- Record provenance for every derived responsibility claim
- Never turn historical agency fields into automatic gold labels
- Do not add an external submission path without a separate security and governance review
- Add a hard-case fixture and regression test for every routing bug
- Keep fictional demo records visibly fictional

## Source adapters

New adapters must archive the raw response, fetch metadata, checksum, schema version, license, rate-limit policy, and historical-label limitations. Recorded responses are required for tests.

## Pull requests

Describe the affected responsibility contract, evidence source, temporal behavior, safety impact, tests, and reproducibility impact.
