# Portfolio Ranking 2.0 Plan

## Goal

Portfolio Ranking 2.0 moves ranking from metric-first to scenario-first.

The current Recommendation Audit shows that recommendation logic can now produce a coherent scenario structure, but ranking still needs to consume Scenario Consistency Score, Asset Role Balance, Tail Exposure, and User Decision Clarity as first-class ranking inputs.

This is a design plan only. It does not modify business code, recommendation logic, UI, Portfolio Ranking code, data files, branches, or Git history.

## 1. Current Ranking Problems

Current Portfolio Ranking is still too dependent on:

- EV.
- ROI.
- Sharpe.

Known issues:

- A portfolio can look attractive because of EV/ROI while still carrying weak scenario structure.
- Tail-heavy correct-score portfolios can appear appealing because of upside, even when they should be labeled aggressive or speculative.
- Scenario Consistency Score exists in reports but is not yet a ranking gate.
- Asset role structure is visible but not strong enough as a ranking constraint.
- User decision clarity is not directly scored.
- My Portfolio is not guaranteed to be ranked with the same logic as system portfolios.

## 2. Ranking Dimensions

Portfolio Ranking 2.0 should use these dimensions:

| Dimension | Purpose |
| --- | --- |
| EV | Measures expected value. |
| ROI | Measures capital efficiency. |
| Sharpe | Measures return stability versus volatility. |
| Scenario Consistency Score | Measures whether assets serve one coherent match script. |
| Asset Role Balance | Measures whether Direction, Tempo, Return, Insurance, and Tail roles are proportionate. |
| Tail Exposure | Measures how much of the portfolio depends on extreme or low-probability paths. |
| User Decision Complexity | Penalizes portfolios that are hard to understand or explain. |
| Main Scenario Coverage | Rewards coverage of the primary scenario. |
| Secondary Insurance Coverage | Rewards protection against named Main Scenario failure paths. |
| Critical Conflict Count | Penalizes impossible or contradictory paths. |
| Data Confidence | Penalizes rankings based on incomplete scenario or market data. |

## 3. Portfolio Score Design

Conceptual formula:

```text
Portfolio Score =
  Value Layer
  + Scenario Layer
  + Role Layer
  + Coverage Layer
  - Conflict Penalty
  - Tail Penalty
  - Decision Complexity Penalty
  - Data Confidence Penalty
```

Suggested v2 weighting:

| Layer | Weight | Inputs |
| --- | ---: | --- |
| Value Layer | 30 | EV, ROI, Sharpe |
| Scenario Layer | 25 | Scenario Consistency Score |
| Role Layer | 15 | Asset Role Balance |
| Coverage Layer | 15 | Main Scenario Coverage, Secondary Insurance Coverage |
| Risk Penalties | -15 to -40 | Critical conflicts, tail exposure, decision complexity, weak data |

Suggested Value Layer split:

- EV: 12
- ROI: 10
- Sharpe: 8

Suggested Scenario Layer:

- Scenario Consistency Score contributes up to 25 points.
- Score below 75 must reduce final rank even when EV is strong.
- Score below 60 should mark the portfolio as audit-warning only.

## 4. Ranking Guardrails

Hard guardrails:

- Critical Conflict cannot rank first.
- Over3.5 plus 1:0 or 2:0 as primary drivers cannot rank first.
- Opposite winner directions without hedge labels cannot rank first.
- Portfolio with Scenario Consistency Score below 60 cannot be default recommendation.
- Portfolio missing scenario labels cannot be default recommendation.

Warning guardrails:

- Scenario Consistency Score below 75 must show a warning.
- Tail-heavy portfolio cannot be default recommendation unless explicitly labeled aggressive/upset.
- Aggressive Return or Tail assets cannot be used as core Main Scenario evidence.
- Portfolio with high EV but weak Main Scenario Coverage must be downgraded.
- Portfolio with high User Decision Complexity must be downgraded.

Default recommendation guardrails:

- Must have Scenario Consistency Score >= 75.
- Must have no Critical or High conflict.
- Must identify Main Scenario coverage.
- Must explain Insurance and Tail assets separately.
- Must be understandable in one decision sentence.

## 5. Asset Role Balance

Portfolio Ranking 2.0 should distinguish:

- Direction Asset.
- Tempo Asset.
- Core Return Asset.
- Aggressive Return Asset.
- Insurance Asset.
- Tail Asset.

Role balance expectations:

- Direction Asset should support the main match direction.
- Core Return Asset should monetize the Main Scenario.
- Aggressive Return Asset should be capped as upside, not core evidence.
- Insurance Asset should protect a named Secondary Scenario.
- Tail Asset should protect or express a named Upset Scenario.
- Tail exposure should be visible and penalized if excessive.

Example rule:

```text
If Tail Asset share > 20%, apply Tail Heavy warning.
If Tail Asset share > 35%, portfolio cannot be default recommendation.
```

## 6. Main And Secondary Coverage

Main Scenario Coverage should measure how much of the portfolio pays or remains valid when the Main Scenario occurs.

Secondary Insurance Coverage should measure how much of the portfolio survives named failure paths such as:

- Favorite wins by only 1.
- Draw zone.
- Tempo mismatch.
- Favorite wins but does not cover handicap.

Ranking behavior:

- Strong Main Coverage improves ranking.
- Strong Secondary Insurance Coverage improves stability.
- Low Main Coverage with high Tail Exposure should rank as speculative, not default.

## 7. User Decision Complexity

User Decision Complexity should penalize portfolios that are hard to act on.

Complexity signals:

- Too many assets.
- Too many correct scores.
- Mixed Main/Aggressive/Tail assets without separation.
- Weak explanation.
- High tail exposure.
- Multiple scenarios competing for attention.

Recommended labels:

- Clear: user can understand the recommendation quickly.
- Moderate: user needs to inspect scenario details.
- Complex: user may not understand what the portfolio is really betting on.

Complex portfolios can still rank, but should not default to the top unless their scenario and risk labels are excellent.

## 8. My Portfolio Score

My Portfolio must use the same evaluation system as system portfolios.

My Portfolio Score should include:

- EV.
- ROI.
- Sharpe.
- Scenario Consistency Score.
- Asset Role Balance.
- Tail Exposure.
- Main Scenario Coverage.
- Secondary Insurance Coverage.
- User Decision Complexity.
- Critical Conflict Count.

Parity requirements:

- Same asset role classifier.
- Same scenario mapping.
- Same conflict rules.
- Same consistency scoring.
- Same tail exposure penalty.
- Same decision complexity labels.
- Same post-match audit fields.

My Portfolio output should show:

- Rank among system portfolios.
- Scenario Consistency Score.
- Where it aligns with the system Main Scenario.
- Where it differs from the system recommendation.
- Whether it is safer, more aggressive, more tail-heavy, or more contradictory.

## 9. Output Fields For Future Implementation

Each ranked portfolio should expose:

- `portfolio_name`
- `portfolio_score`
- `ev_score`
- `roi_score`
- `sharpe_score`
- `scenario_consistency_score`
- `asset_role_balance_score`
- `tail_exposure`
- `main_scenario_coverage`
- `secondary_insurance_coverage`
- `critical_conflict_count`
- `user_decision_complexity`
- `ranking_warnings`
- `default_recommendation_eligible`

## 10. Relationship With Scenario Engine And Auditor

Scenario Engine provides:

- Main Scenario.
- Secondary Scenario.
- Upset Scenario.
- Asset mapping.
- Scenario Consistency Score.
- Tail exposure labels.
- Conflict flags.

Recommendation Auditor checks:

- Whether Scenario Engine output is coherent.
- Whether role labels are correct.
- Whether obvious path conflicts exist.
- Whether Portfolio Ranking respects the Scenario Consistency Score.

Portfolio Ranking 2.0 consumes:

- Scenario Consistency Score.
- Asset role labels.
- Conflict flags.
- Tail exposure.
- Coverage fields.
- Decision complexity fields.

Ranking must not override Auditor Critical or High conflicts.

## 11. Acceptance Criteria

Portfolio Ranking 2.0 design is ready when:

- EV/ROI/Sharpe are no longer sufficient to rank first.
- Scenario Consistency Score is a first-class ranking dimension.
- Critical conflict guardrails are defined.
- Tail-heavy portfolios are prevented from becoming default recommendation.
- Core Return, Aggressive Return, Insurance, and Tail roles are separated.
- My Portfolio uses the same scoring framework as system portfolios.
- Ranking output includes clear warnings and default-recommendation eligibility.

