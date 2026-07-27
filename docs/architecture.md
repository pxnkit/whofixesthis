# Architecture

WhoFixesThis separates the live product surface from the research core while keeping a shared decision contract.

## Components

### Web workbench

The React client contains a local deterministic router and an offline MapLibre style with embedded GeoJSON. It supports issue descriptions, date changes, location uncertainty, asset identifiers, competing hypotheses, signed evidence, duplicates, abstention, and approved local export.

The public workbench uses fictional records. It makes no source or reporting requests.

### Typed domain layer

Pydantic models define observations, intervals, providers, services, evidence, search actions, duplicate candidates, and decisions. Extra fields are rejected so schema drift fails visibly.

### Temporal graph

`TemporalResponsibilityGraph` stores typed responsibility edges. Each edge has:

- A valid-time interval for when the claim applied
- A transaction-time interval for when the system knew the claim
- Provenance with authority, retrieval time, checksum, URL, and evidence span

Intervals are half open. An end timestamp is excluded.

### Evidence-directed resolver

The resolver begins with candidate priors, applies visible evidence, optionally reveals allowed frozen actions, filters evidence by valid and transaction time, penalizes broad location uncertainty, and sorts provider-service hypotheses.

A route is selected only when the top score passes both a confidence threshold and a score-margin requirement. Otherwise the resolver returns an unresolved state and a next evidence action.

### FixRouteBench

The benchmark reveal server is represented by deterministic JSONL episodes. Each episode controls what is visible at the start and what each search action reveals. This supports leakage tests and cost-aware search experiments without live network access.

### API and CLI

FastAPI exposes resolution, benchmark, report preparation, and local-export approval. The CLI reuses the same Python core for validation and reproduction.

## Trust boundaries

1. User text and media are untrusted observation inputs
2. Source adapters produce untrusted records with explicit provenance
3. Normalization never removes the original record
4. Derived evidence is filtered by two time axes
5. The decision engine can abstain
6. Report preparation is separate from approval
7. External submission is outside the current system

## Future adapters

The source registry defines contracts for Open311 service discovery, historical request data, and geospatial standards. Live adapters should record responses before parsing, use conditional requests, honor rate limits, and never run in deterministic tests.
