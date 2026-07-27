# Threat model

## Protected outcomes

- A resident is not silently routed to the wrong provider
- A report is not submitted without reviewed approval
- A historical agency field is not treated as truth
- Precise location and media are not exposed unnecessarily
- Sensitive infrastructure is not reconstructed or displayed
- Untrusted source text cannot change application policy

## Threats and controls

| Threat | Control |
| --- | --- |
| Prompt injection in source or attachment text | Parse as data, reject extra schema fields, never execute source instructions |
| Future outcome leakage | Transaction-time snapshot filtering |
| Stale service code | Valid-time service definitions |
| Overconfident boundary decision | Threshold, margin, and unresolved state |
| False duplicate suppression | Relation label and same-defect evidence |
| Silent external mutation | No submission endpoint and explicit local export gate |
| Identity or media retention | No public demo persistence |
| Utility topology exposure | General asset candidate only, no detailed topology |

## Residual risk

Fictional fixtures cannot establish operational safety in a real jurisdiction. A civic partner review, authoritative data agreement, redaction evaluation, accessibility audit, and prospective monitoring plan are required before deployment.
