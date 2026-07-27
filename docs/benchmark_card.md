# FixRouteBench card

## Summary

FixRouteBench 0.1 is a 50-case deterministic benchmark for civic responsibility routing. It uses fictional jurisdictions and providers so it can be distributed and replayed without presenting stale contact guidance.

## Composition

- 50 episodes
- 10 hard-case families
- 2 adjacent fictional municipalities
- 1 fictional regional road provider
- 3 main issue classes
- Resolved and open-set outcomes

## Episode fields

Each JSONL row includes the observation, event time, decision time, hypotheses, initially visible evidence, action-revealed evidence, costs, latency, duplicate candidates, corrected target, minimum sufficient evidence, escalation path, and historical-label limitation.

## Intended metrics

- Provider accuracy
- Service-code accuracy
- Joint provider and service accuracy
- Wrong-jurisdiction rate
- Duplicate accuracy
- Selective coverage
- Abstention accuracy
- Confidence summaries
- Search cost and latency

## Non-claims

The benchmark does not estimate real-world accuracy, fairness, resident outcomes, resolution time, or final resolution rate. The generated cases are contract tests and feasibility scaffolding.

## Expansion protocol

A 500-case release should use two annotators and one adjudicator, retain source spans, track disagreement, compute agreement by field, preserve decision-time snapshots, and separate expert gold from historical weak labels.
