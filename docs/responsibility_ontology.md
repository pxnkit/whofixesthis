# Responsibility ontology

## Node types

- Location
- Road segment
- Parcel
- Asset
- Agency
- Contractor
- Service
- Permit
- Contract
- Report
- Policy

## Edge types

- `owns`
- `maintains`
- `delegates`
- `operates`
- `intersects`
- `covered_by`
- `reports`
- `duplicates`
- `supersedes`
- `escalates`

## Time semantics

Every responsibility claim has valid time and transaction time. Derived edges inherit the narrowest applicable valid interval and must retain the provenance of every supporting record.

## Distinctions

Ownership, operation, maintenance, delegated first response, public reporting channel, historical submission, and closure are separate relations.

## Open-set states

- Private responsibility
- Unknown utility
- Shared or ambiguous responsibility
- No supported public route

Open-set states are valid outputs, not errors.
