# Data governance

## Data classes

| Class | Examples | Default handling |
| --- | --- | --- |
| Public metadata | Service definitions and public boundaries | Frozen with provenance |
| User observation | Description and observation time | Session scoped |
| Precise location | GPS point and uncertainty | Minimize and allow coarsening |
| User media | Issue photo and close-up | Local browser session only |
| Derived decision | Hypotheses, evidence, confidence | Export only after review |
| Sensitive infrastructure | Utility topology and protected assets | Do not expose |

## Collection principles

- Collect only what can change the route
- Keep uncertainty rather than inventing precision
- Do not infer identity, blame, liability, or entitlement
- Separate media analysis from provider responsibility
- Preserve original public records alongside normalized records
- Retain contradictions

## Retention

The public demo has no server-side user data store. Browser media references and form state disappear with the session. A local prepared report is created only after the user checks the review box and presses export.

Future deployments with persistence must define a retention window, deletion path, export path, encryption policy, access audit, and incident process before collecting user data.

## Provenance

Each evidence item carries a source identifier, authority, canonical URL, retrieval timestamp, checksum, evidence span, valid-time interval, and transaction-time interval.

## Governance review gates

- Source redistribution rights
- Historical label validity
- Geographic and demographic coverage gaps
- Sensitive infrastructure exposure
- Media redaction quality
- Provider dispute and correction process
- Approval enforcement
- Prospective outcome access
