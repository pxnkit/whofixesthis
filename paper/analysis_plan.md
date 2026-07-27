# Analysis plan

## Primary estimand

Difference in joint first-touch provider and service accuracy between evidence-directed temporal graph search and the strongest static baseline on expert-corrected cases.

## Secondary outcomes

- Wrong-jurisdiction rate
- Duplicate precision and recall
- Evidence completeness
- Risk-coverage curve
- Expected calibration error
- Search action cost
- End-to-end latency
- Clarification count

Final resolution is excluded unless valid prospective outcomes become available.

## Baselines

- Nearest agency
- Complaint classifier plus nearest agency
- Static GIS rules
- Open311 service search
- Graph without time
- Graph without permits and contracts
- Generic multimodal agent
- Human routing sample

## Splits

Use grouped geographic and temporal splits. Keep nearby assets, duplicate chains, and service-version families in the same split. Freeze the decision-time source snapshot before label review.

## Statistical procedure

- Paired bootstrap confidence intervals by episode
- McNemar test for paired binary routing outcomes
- Effect sizes with confidence intervals
- Multiple seeds for stochastic baselines
- Family-stratified failure analysis
- Predefined correction for multiple primary comparisons

## Leakage checks

- No ticket outcome known after the decision timestamp
- No later service definition
- No duplicate chain split across train and test
- No annotation note included in model input
- No historical agency field treated as gold

## Kill criteria

Narrow or stop the study if expert-corrected responsibility is unavailable, cross-jurisdiction cases are sparse, the strongest simple baseline is within three percentage points, permit evidence never changes a choice, or no partner can validate operational routing.
