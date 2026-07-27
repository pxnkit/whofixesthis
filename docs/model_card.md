# Model card

## Model details

WhoFixesThis 0.1 uses a deterministic evidence-scoring resolver. The default release does not call a language, vision, embedding, or external model.

## Intended use

- Research on temporal civic service routing
- Testing bitemporal graph and provenance contracts
- Studying calibrated abstention and evidence acquisition
- Demonstrating approval-gated local report preparation

## Out of scope

- Legal responsibility findings
- Enforcement, blame, or entitlement decisions
- Emergency dispatch
- Autonomous government submission
- Public utility topology discovery
- Real-world performance claims from fictional fixtures

## Inputs

Description, latitude, longitude, location uncertainty, observation time, optional context identifier, optional asset identifier, and optional local image references.

## Outputs

A provider-service hypothesis list, selected route or unresolved state, confidence, supporting and contradicting evidence, duplicates, next action, escalation path, and counterfactual.

## Decision rule

Evidence scores are filtered by event time and decision time. The top hypothesis must pass a confidence threshold and a margin over the runner-up. Broader GPS uncertainty lowers all candidate scores.

## Limitations

The deterministic keyword and fixture logic is not a trained model. Confidence values are engineering scores for testing selective decision paths. They are not calibrated against expert civic routing outcomes.

## Evaluation

FixRouteBench verifies internal contracts and expected behavior on fictional cases. A publishable empirical result requires independently corrected cases, pre-registered metrics, geographic splits, uncertainty intervals, and leakage controls.
