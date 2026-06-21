# Scenario Guardrails Review

Date: 2026-06-21

## Decision

Enter Scenario Guardrails

## Why

- Valid post-match validations: 12, above the 5-match threshold.
- Scenario Wins: 3.
- Legacy Wins: 3.
- Draws: 6.
- Scenario aggregate ROI: -2.1%.
- Legacy aggregate ROI: -40.8%.
- Scenario Ranking is not conclusively ready to replace Legacy Ranking, but it has shown enough value to add stronger production guardrails.

## Rejected Options

### Keep Shadow Mode

Not selected. Shadow Mode has produced enough post-match evidence to justify stronger warnings and eligibility checks.

### Promote Scenario Signals

Not selected. Scenario ROI is better than Legacy ROI but still negative, and the current validation set contains multiple snapshots for some fixtures. Full promotion would be premature.

## Guardrails Phase Rules

- Legacy Rank 1 remains the official table order for now.
- If Legacy Rank 1 has `Shadow Verdict = Disagreement`, display a stronger warning.
- Scenario Rank 1 may be marked as a `剧本优先候选`.
- Tail-heavy, pure-tempo, or low-consistency portfolios must not become default recommendations without warning.
- Scenario Rank may influence default recommendation eligibility in a future controlled implementation.
- Do not replace `strategy_score(...)` yet.
- Do not change production sorting yet.

## Next Operational Step

Design the minimal Scenario Guardrails UI and eligibility layer before changing any recommendation behavior.
