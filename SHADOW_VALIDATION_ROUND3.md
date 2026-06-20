# Shadow Validation Round 3

Date: 2026-06-21

Scope: validation report only. No code, UI, Ranking, recommendation logic, or data files were modified.

## Match Selection

Selected cold-risk match:

- Brazil vs Haiti
- Source snapshot: `data/history/2026_06_20_Brazil_Haiti_pre.json`

Selection reason:

- It is the highest available unused cold-risk match with strategy data.
- Upset index is 48 / 100, medium upset risk.
- Contrarian score is 95, meaning Brazil is a crowded popular side.
- Direction confidence is only 55 / 100 despite Brazil being a heavy favorite.
- Legacy top portfolio is a pure tempo asset, which is useful for testing whether Shadow Mode downgrades non-directional top recommendations.

## Source Snapshot Summary

- Match: Brazil vs Haiti
- Display: 巴西 vs 海地
- Final recommendation: Brazil
- Direction confidence: 55 / 100, observe
- Value rating: D
- Participation advice: only observe
- Recommended stake: 100
- Upset index: 48 / 100, medium upset risk
- Contrarian score: 95, high crowded-favorite pressure
- Main total line: 3.5
- Market note: Over 3.5 is attractive in value terms, but the match also has crowded-favorite and missing handicap/correct-score data risk.
- Strategy count: 6

## Scenario Engine Run

### Main Scenario

- Name: Brazil win, but uncertain margin
- Probability: 89.3% Brazil win-path aggregate from local path distribution
- Expected score: 2:0, 3:1, 4:1
- Goal range: 2-5 total goals
- Tempo: medium to high
- Direction: Brazil win
- Supporting evidence:
  - Final recommendation is Brazil.
  - Winner market probability is 86.7%.
  - Polymarket also supports Brazil at 88.3%.
  - Path distribution has Brazil win by 1, 2, and 3+ as the dominant combined paths.
- Risk notes:
  - Direction confidence is only 55 because handicap and real correct-score data are missing.
  - The top production strategy is Over 3.5, which is a tempo thesis rather than a Brazil direction thesis.
  - The system recommends only observation, not strong participation.

### Secondary Scenario

- Name: Brazil wins but game does not fully open
- Probability: 33.8% one-goal Brazil win path, plus part of the two-goal path
- Expected score: 1:0, 2:1, 2:0
- Goal range: 1-3 total goals
- Tempo: low to medium
- Direction: Brazil win, but not necessarily Over 3.5
- Supporting evidence:
  - Brazil small-win path is the largest single path at 33.8%.
  - Risk exposure explicitly says deep favorite bets lose on narrow favorite win, draw, or underdog win.
- Risk notes:
  - Over 3.5 does not cover this Secondary Scenario.
  - Brazil winner survives this path.

### Upset Scenario

- Name: Haiti resistance, draw, or favorite-crowding failure
- Probability: 10.7% explicit draw + Haiti-unbeaten buckets, with higher qualitative risk from contrarian pressure
- Expected score: 0:0, 1:1, 1:2
- Goal range: 0-3 total goals
- Tempo: low to unstable
- Direction: draw or Haiti avoids the expected script
- Supporting evidence:
  - Upset index is 48 / 100.
  - Contrarian score is 95, showing high popular-side crowding on Brazil.
  - Direction confidence is only observe-level.
- Risk notes:
  - This is not a reason to back Haiti as main thesis.
  - It is a reason to avoid over-promoting a single tempo asset as the top portfolio.

## Recommendation Auditor Run

### Overall Audit

- Status: Warning
- Severity: Medium
- Critical conflict: No
- High conflict: No

### Findings

- Brazil winner assets align with the Main Scenario.
- Over 3.5 aligns with the high-tempo / Brazil 3+ path, but does not cover the largest single path: Brazil narrow win.
- Over 3.5 is a valid Tempo Asset, not a complete recommendation by itself.
- Legacy top ranking puts a pure Tempo Asset first.
- Scenario-aware evaluation should prefer a Brazil direction asset when the final recommendation is Brazil and the system advice is only observation.
- No Over3.5 plus 1:0 / 2:0 correct-score primary conflict was detected because the portfolio does not pair Over3.5 with low-score correct scores.

## Portfolio Ranking Shadow Mode Run

Shadow rule:

```text
Legacy Ranking remains authoritative.
Scenario Ranking observes only.
No production ranking or recommendation changes.
```

Scenario Score inputs used from the existing snapshot:

- existing legacy score
- expected yield
- Sharpe
- strategy items
- role exposure
- Brazil winner assets
- Over 3.5 tempo assets
- direction confidence and upset-risk context

Main Scenario assets:

- Brazil winner
- Brazil direction exposure
- Over 3.5 as Tempo Asset only, not full Main Scenario proof

Secondary Scenario protection:

- Brazil winner, because it survives Brazil narrow-win paths

Conflict pressure:

- Pure Over 3.5 has high tempo exposure but no direction coverage.
- In a cold-risk / observe-level match, a pure tempo top portfolio should be downgraded relative to a direction asset.

## Shadow Ranking Table

| Portfolio | Legacy Rank | Legacy Score | Scenario Score | Scenario Rank | Rank Difference | Shadow Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 大小球策略 | 1 | 80 | 67.1 | 5 | +4 | Disagreement |
| 赔率分布优化器 | 2 | 80 | 67.1 | 6 | +4 | Disagreement |
| 当前推荐组合 | 3 | 66 | 76.4 | 1 | -2 | Watch |
| 独赢策略 | 4 | 66 | 76.4 | 2 | -2 | Watch |
| 独赢 + 让球 | 5 | 66 | 76.4 | 3 | -2 | Watch |
| 独赢 + 波胆 | 6 | 66 | 76.4 | 4 | -2 | Watch |

Rank Difference:

```text
scenario_rank - legacy_rank
```

Positive means Scenario Ranking downgrades the portfolio.

Negative means Scenario Ranking upgrades the portfolio.

## Legacy Top Portfolio

- Legacy Top Portfolio: 大小球策略
- Legacy Rank: 1
- Legacy Score: 80
- Scenario Rank: 5
- Scenario Score: 67.1
- Rank Difference: +4
- Shadow Verdict: Disagreement

Interpretation:

- Legacy Ranking favors Over 3.5 because it has strong expected yield and Sharpe in the snapshot.
- Scenario Ranking downgrades it because it is a pure Tempo Asset.
- It does not express the final Brazil direction recommendation.
- It does not survive the largest single path, Brazil narrow win, if the game stays under 3.5.
- In a cold-risk and observe-level match, a top portfolio should not be only a tempo bet.

## Scenario Top Portfolio

- Scenario Top Portfolio: 当前推荐组合
- Legacy Rank: 3
- Legacy Score: 66
- Scenario Rank: 1
- Scenario Score: 76.4
- Rank Difference: -2
- Shadow Verdict: Watch

Tie note:

- 当前推荐组合, 独赢策略, 独赢 + 让球, and 独赢 + 波胆 all resolve to Brazil winner exposure in the saved active items.
- The report assigns Scenario Rank 1 to 当前推荐组合 because it is the first Brazil-direction portfolio in the legacy list.

Interpretation:

- Scenario Ranking prefers Brazil winner exposure because it matches the final recommendation and survives narrow-win paths.
- This does not mean it should become a strong recommendation; the snapshot still says observe only.
- It means that, among available portfolios, direction coverage is more coherent than pure Over 3.5 exposure.

## Comparison With Round 1 And Round 2

| Round | Match Type | Match | Legacy Top | Scenario Top | Legacy Top Scenario Rank | Difference? | Verdict |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| Round 1 | Strong favorite / handicap-cover | Germany vs Ivory Coast | 让球策略 | 赔率分布优化器 | 4 | Yes | Disagreement |
| Round 2 | Balanced match | Scotland vs Morocco | 独赢 + 波胆 | 独赢策略 | 3 | Yes | Watch |
| Round 3 | Cold-risk / crowded favorite | Brazil vs Haiti | 大小球策略 | 当前推荐组合 | 5 | Yes | Disagreement |

## Cross-Round Pattern

### Round 1 Pattern

- Legacy top was directionally coherent but too narrow.
- Scenario Ranking preferred broader role balance.
- Main issue: role balance and tail/return structure.

### Round 2 Pattern

- Legacy top was coherent but score-specific.
- Scenario Ranking preferred simpler winner exposure in a balanced match.
- Main issue: avoiding over-specific score paths when draw-zone risk is material.

### Round 3 Pattern

- Legacy top is a pure Tempo Asset.
- Scenario Ranking prefers Brazil direction exposure.
- Main issue: high EV/Sharpe tempo asset outranking the actual final recommendation path.

## Validation Result

Primary watch case:

```text
Legacy Rank = 1
Scenario Rank != 1
```

Detected:

- Yes.

Severity:

- High watch case.

Reason:

- Legacy top falls to Scenario Rank 5.
- The difference is caused by EV/Sharpe over-promoting a pure Over 3.5 asset in a cold-risk match.

## Final Verdict

- Overall Shadow Verdict: Disagreement
- Critical conflict found: No
- High conflict found: No
- Legacy Top and Scenario Top differ: Yes
- Production impact: None

This validates Shadow Mode on a third match type:

- Round 1: role-balance disagreement.
- Round 2: balanced-match simplicity disagreement.
- Round 3: pure tempo asset overranking disagreement.

## Automation Verdict

- Status: Pass for Round 3 validation report.
- Generated: `SHADOW_VALIDATION_ROUND3.md`
- No code changed.
- No UI changed.
- No Ranking changed.
- No recommendation logic changed.
- No data files changed.
- No app was run.
- No API refresh was performed.
