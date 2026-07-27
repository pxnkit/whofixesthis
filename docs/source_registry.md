# Source registry

The machine-readable registry is [`configs/sources.yaml`](../configs/sources.yaml).

The current release registers authoritative standards and public data documentation as adapter targets. It does not ship copied source snapshots and it does not make live requests in default experiments.

## Registered sources

| Source | Authority | Decision role | Current snapshot state |
| --- | --- | --- | --- |
| [Open311 GeoReport v2](https://wiki.open311.org/GeoReport_v2/) | Open311 | Service request interoperability | Metadata contract only |
| [Open311 Service Discovery](https://wiki.open311.org/Service_Discovery/) | Open311 | Dated service catalog discovery | Metadata contract only |
| [NYC 311 API](https://data.cityofnewyork.us/resource/erm2-nwe9.json) | City of New York | Historical routing baseline | Excluded from default experiments |
| [Census TIGER/Line](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) | United States Census Bureau | Boundary candidate generation | Metadata contract only |
| [OGC API Features](https://ogcapi.ogc.org/features/) | Open Geospatial Consortium | Feature interoperability | Metadata contract only |
| [GeoParquet](https://geoparquet.org/) | GeoParquet project | Frozen geospatial fixture format | Metadata contract only |

## Required record fields

Every source entry records authority, jurisdiction, temporal validity, spatial coverage, canonical URL, access date, license, version, rate limit, snapshot state, legal decision role, and historical-label limitations.

The checksum value `unavailable:not-materialized` is intentional. It means no source response was fetched or frozen for this release. A future ingestion run must replace that value with a SHA-256 checksum before the source can participate in an experiment.

## Historical label policy

Submitted agency, closing agency, transfer destination, and data-system owner are operational fields. None of them automatically identifies the legally or operationally responsible provider.

Historical labels may be used for:

- Candidate generation
- Reroute pattern analysis
- Weakly supervised baselines
- Sampling cases for independent review

They may not be used as expert gold without independent correction.

## Freeze procedure

1. Record the canonical request, response headers, retrieval time, and rate-limit state
2. Store the raw response before parsing
3. Compute SHA-256 over the raw bytes
4. Record schema and API versions
5. Resolve license and redistribution terms
6. Register valid-time and transaction-time coverage
7. Document the source role and limitations
8. Add a deterministic parser contract test

Live source text is untrusted. It cannot grant permissions, change system policy, or trigger submission.
