# Hybrid v0.2 Aggressive Upside Plan

Date: 2026-06-21

Scope: design only. This plan does not modify code, sorting, recommendation logic, UI, data files, branches, commits, or pushes.

## 1. Problem Statement

Phase B Benchmark Diagnosis showed:

- Hybrid Guardrails correctly identified tail-heavy risk.
- Legacy ROI was lifted by a few aggressive upside hits.
- Scenario / Hybrid controlled drawdown, but missed high-score upside.
- Current Hybrid is too binary: `Allowed` vs `Blocked`.

Hybrid v0.2 should distinguish:

1. `Uncontrolled Tail`
2. `Scenario-Supported Aggressive Upside`

The goal is not to let tail-heavy portfolios become default recommendations. The goal is to allow a capped upside sleeve when the match scenario supports it.

## 2. Core Definitions

## Aggressive Upside Candidate

An `Aggressive Upside Candidate` is a high-payout asset or sleeve that is not safe enough to be the core portfolio, but is justified by the match script.

Examples:

- 3:0, 3:1, 4:1, 4:2 correct-score exposure when the scenario supports favorite pressure and high scoring.
- Deep handicap cover exposure when the favorite has a strong win path.
- Over / high-score assets only when aligned with the main or secondary high-score scenario.

It is allowed only as a capped sleeve attached to a Core Portfolio.

It is not allowed to become the whole default portfolio.

## Uncontrolled Tail

`Uncontrolled Tail` is upside exposure that has high payout but weak scenario support.

Examples:

- 5:0, 5:1, 5:2, 5:3 correct-score cluster with no high-score scenario confirmation.
- Correct-score-only portfolio.
- Tail-heavy portfolio without direction asset.
- Tail assets that conflict with the selected main tempo path.
- High-odds picks selected mainly because they raise EV / ROI, not because they serve the scenario.

Treatment:

- Block from default recommendation.
- Exclude from Core Portfolio.
- Track separately in benchmark as `Legacy Tail-Heavy`.

## Scenario-Supported Aggressive Upside

`Scenario-Supported Aggressive Upside` is high-return exposure that passes scenario checks.

Required traits:

- It extends the Main Scenario or a named Secondary high-score scenario.
- It has direction support.
- It has reasonable role balance.
- It does not dominate the portfolio.
- It has an explicit risk explanation.

Treatment:

- Eligible for `Upside Sleeve`.
- Not eligible to replace Core Portfolio.
- May improve Hybrid Score through a capped bonus.

## 3. Entry Conditions For Aggressive Upside

Aggressive Upside may enter the portfolio only if at least 4 of the following 6 conditions are true:

| Condition | Requirement |
| --- | --- |
| Strong Favorite | Favorite win probability is materially higher than underdog probability. |
| Deep Handicap | Main handicap requires at least a 2-goal cover path, such as -1.25, -1.5, -1.75, or deeper. |
| High Score Scenario | Scenario Engine identifies a high-score or 3+ goal path as Main or Secondary. |
| Main Scenario Support | The upside asset still serves the main direction, not a contradictory path. |
| Market Support | Correct-score or totals market center includes high-score outcomes, not just edge outliers. |
| Auditor Clearance | Recommendation Auditor finds no Critical path conflict. |

Hard minimum:

- `Main Scenario Support` is required.
- `Auditor Clearance` is required.
- At least one Direction Asset must exist in the Core Portfolio.

If these hard minimums are missing, the asset remains `Uncontrolled Tail`.

## 4. Disallowed Aggressive Upside

Do not allow aggressive upside when:

- Main Scenario is low-score control and the upside requires 4+ total goals.
- The upside asset conflicts with handicap direction.
- Tail exposure would exceed the cap.
- The portfolio becomes correct-score-only.
- The asset is selected only by EV / ROI / Sharpe with no scenario explanation.
- `Shadow Verdict = Blocker Candidate`.
- Recommendation Auditor flags Critical conflict.

## 5. Exposure Limits

Hybrid v0.2 should use strict sleeve caps.

| Portfolio Type | Core Share | Upside Sleeve Max | Notes |
| --- | ---: | ---: | --- |
| Normal match | 85-90% | 10-15% | Default cap. |
| Strong favorite deep handicap | 80-85% | 15-20% | Allowed only with high-score support. |
| Explicit high-score scenario | 75-85% | 15-25% | Requires auditor clearance. |
| Cold upset risk | 90-95% | 5-10% | Upside must be very small. |
| Low-score scenario | 90-100% | 0-10% | High-score sleeve mostly disabled. |

Hard caps:

- Tail Asset total share should not exceed 25%.
- Any single correct-score tail should not exceed 8%.
- Extreme upside, such as 5:0 or 5:1, should not exceed 3-5% each.
- If max loss increases materially while Main Scenario Coverage falls, the sleeve is rejected.

## 6. Portfolio Structure

Hybrid v0.2 should rank a combined structure:

```text
Hybrid Portfolio =
  Core Portfolio
  + Upside Sleeve
```

## Core Portfolio

Core Portfolio is the decision foundation.

It should include:

- Direction Asset
- Main Return Asset
- Optional Tempo Asset
- Optional Secondary Insurance Asset

Core must pass:

- Scenario Consistency Score threshold
- Main Scenario Coverage threshold
- no Critical conflict
- acceptable max loss

## Upside Sleeve

Upside Sleeve is optional.

It can include:

- aggressive correct scores
- high-score return assets
- deep-cover extension assets

It must be:

- capped
- explained
- scenario-supported
- separated from Core in reporting

The UI or report should not present it as the primary recommendation unless explicitly promoted later.

## 7. Hybrid Score Integration

Hybrid Score v0.2 should preserve the existing structure:

```text
Hybrid Score =
  Value Layer
  + Scenario Layer
  + Coverage Layer
  + Stability Layer
  + Controlled Upside Bonus
  - Conflict Penalty
  - Uncontrolled Tail Penalty
  - Max Loss Penalty
```

## Controlled Upside Bonus

Add a capped bonus only when aggressive upside passes entry conditions.

Suggested bonus:

| Condition | Bonus |
| --- | ---: |
| Aggressive Upside Candidate passes hard minimum | +2 |
| Strong Favorite + Deep Handicap | +2 |
| High Score Scenario confirmed | +3 |
| Market center supports high-score outcomes | +2 |
| Sleeve risk capped below target | +1 |

Maximum Controlled Upside Bonus: `+8`.

## Uncontrolled Tail Penalty

Keep or increase penalty when the tail is not scenario-supported.

Suggested penalty:

| Condition | Penalty |
| --- | ---: |
| Tail-heavy without scenario support | -15 to -25 |
| Correct-score-only portfolio | -25 |
| Tail conflicts with Main Scenario | -30 |
| Tail selected only by EV / ROI | -15 |
| Critical conflict | default-ineligible |

## Guardrail Status v0.2

Replace binary labels with more precise states:

| Status | Meaning |
| --- | --- |
| Eligible Core | Can compete for main Hybrid Rank. |
| Aggressive Upside Candidate | Allowed only as capped sleeve. |
| Watch | Useful signal but not default-eligible without explanation. |
| Blocked Tail | Uncontrolled tail; blocked from default. |
| Critical Conflict | Must not be recommended. |

## 8. Benchmark Design

Phase C benchmark should compare three groups:

## Group A: Core

Scenario-disciplined portfolio without aggressive sleeve.

Measures:

- hit rate
- ROI
- max drawdown
- main scenario coverage

## Group B: Core + Upside

Same Core Portfolio plus capped Aggressive Upside Sleeve.

Measures:

- incremental ROI vs Core
- incremental drawdown vs Core
- frequency of sleeve hits
- whether high-score matches justify sleeve inclusion

## Group C: Legacy Tail-Heavy

Legacy Value Portfolio / tail-heavy structure.

Measures:

- ROI
- hit rate
- max drawdown
- tail win dependency
- drawdown volatility

## Benchmark Questions

The benchmark should answer:

1. Does Core + Upside beat Core without excessive drawdown?
2. Does Core + Upside recover meaningful upside from Legacy?
3. Does Core + Upside reduce the full-loss frequency of Legacy Tail-Heavy?
4. Are sleeve hits concentrated in high-score/deep-handicap scenarios?
5. Does the sleeve fail in low-score or upset-risk scenarios?

## 9. Success Criteria

Hybrid v0.2 is successful if:

- Core + Upside ROI > Core ROI.
- Core + Upside max drawdown is materially lower than Legacy Tail-Heavy.
- Core + Upside captures at least part of high-score upside.
- Uncontrolled Tail remains blocked from default recommendation.
- Aggressive sleeve inclusion is explainable before match start.
- Results remain stable across strong favorite, balanced, upset-risk, low-score, and high-score match types.

## 10. Failure Criteria

Hybrid v0.2 fails if:

- Core + Upside behaves like Legacy Tail-Heavy with a new label.
- Sleeve selection is mostly driven by odds value instead of scenario support.
- Drawdown approaches Legacy Tail-Heavy.
- Low-score scenarios still receive high-score tail sleeves.
- Guardrail labels become too permissive.

## 11. Implementation Boundary For Future Work

Future implementation should be staged:

### Phase A: Report Only

- Generate Core, Core + Upside, and Legacy Tail-Heavy benchmark rows.
- Do not change production sorting.
- Do not change UI.
- Do not change recommendation logic.

### Phase B: Visible Diagnostic

- Show whether a portfolio contains an Aggressive Upside Sleeve.
- Keep default ranking unchanged.
- Show sleeve exposure and reason only in advanced view.

### Phase C: Eligibility Guardrail

- Allow Scenario-supported sleeve to affect default eligibility.
- Keep hard block for Uncontrolled Tail.
- Maintain rollback to prior ranking.

## 12. Product Decision

Hybrid v0.2 should not ask:

```text
Should we allow tail?
```

It should ask:

```text
Is this upside supported by the match scenario, and is it capped enough to be useful without becoming the whole decision?
```

That is the distinction between `Uncontrolled Tail` and `Scenario-Supported Aggressive Upside`.

