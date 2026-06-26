# Shadow Validation Round 2

Date: 2026-06-21

Scope: validation report only. No code, UI, Ranking, recommendation logic, or data files were modified.

## Match Selection

Requested examples:

- Netherlands vs Japan
- Belgium vs Iran

Local data result:

- Neither requested example was found in the available local historical snapshots.

Selected Round 2 match:

- Scotland vs Morocco
- Source snapshot: `data/history/2026_06_20_Scotland_Morocco_pre.json`

Selection reason:

- It is a better available balanced-match proxy than the Germany vs Ivory Coast strong-favorite case.
- The market direction supports Morocco, but the main handicap is `Home +0.5`, creating a useful direction-vs-handicap tension.
- The snapshot has 11 portfolio strategies, enough for Shadow Ranking comparison.

## Source Snapshot Summary

- Match: Scotland vs Morocco
- Display: 苏格兰 vs 摩洛哥
- Final recommendation: Morocco
- Direction confidence: 68 / 100, cautious participation
- Upset index: 47 / 100, medium upset risk
- Market disagreement: low
- Main path: Morocco narrow win by 1
- Draw-zone probability: 27.9%
- Scotland unbeaten probability: 10.0%
- Strategy count: 11

## Scenario Engine Run

### Main Scenario

- Name: Morocco narrow-win path
- Probability: 29.2%
- Expected score: 0:1, 1:2
- Goal range: 1-3 total goals
- Tempo: low to medium
- Direction: Morocco win
- Supporting evidence:
  - Final recommendation is Morocco.
  - Winner market direction points to Morocco.
  - Probability distribution lists Morocco one-goal win as the main path.
  - Core correct-score assets include 0:1 and 1:2.
- Risk notes:
  - Main path is narrow, not a Morocco blowout path.
  - The handicap market `Home +0.5` protects Scotland/draw and conflicts with a Morocco win if treated as a main driver.

### Secondary Scenario

- Name: Draw-zone or Scotland +0.5 survival path
- Probability: 27.9%
- Expected score: 0:0, 1:1
- Goal range: 0-2 total goals
- Tempo: low
- Direction: draw or Scotland avoids losing by the bet condition
- Supporting evidence:
  - Draw-zone probability is material.
  - Main handicap is `Home +0.5`.
  - Under 2.5 aligns with low-tempo draw-zone protection.
- Risk notes:
  - This should be insurance, not the main Morocco recommendation thesis.

### Upset Scenario

- Name: Scotland unbeaten or Morocco direction fails
- Probability: 10.0% explicit Scotland-unbeaten bucket, with broader upset sensitivity from draw risk
- Expected score: 1:0, 2:1, 1:1
- Goal range: 1-3 total goals
- Tempo: low to unstable
- Direction: Scotland avoids defeat or wins
- Supporting evidence:
  - Scotland unbeaten appears in the probability distribution.
  - Upset index is medium at 47 / 100.
- Risk notes:
  - Scotland-positive assets must be labeled as insurance or upset protection.

## Recommendation Auditor Run

### Overall Audit

- Status: Warning
- Severity: Medium
- Critical conflict: No
- High conflict: No

### Findings

- Morocco winner and Morocco correct-score assets are coherent with the Main Scenario.
- `0:1` and `1:2` are valid Main Scenario Return assets.
- `Home +0.5` is not a Main Scenario asset for a Morocco-win thesis.
- `Home +0.5` can be treated as Secondary Scenario insurance only if clearly labeled.
- Portfolios that combine large `Home +0.5` exposure with Morocco-score assets should be downgraded in Scenario Ranking.
- No Over3.5 plus 1:0 / 2:0 style critical path conflict was detected.

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
- winner assets
- handicap assets
- correct-score assets
- tail or conflict exposure

Main Scenario core assets:

- Morocco winner
- correct score 0:1
- correct score 1:2

Secondary Scenario insurance assets:

- Home +0.5
- Under 2.5
- draw-zone compatible protection

Conflict pressure:

- Home +0.5 combined with Morocco-win thesis
- Home +0.5 combined with Morocco correct-score return assets

## Shadow Ranking Table

| Portfolio | Legacy Rank | Legacy Score | Scenario Score | Scenario Rank | Rank Difference | Shadow Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 独赢 + 波胆 | 1 | 93 | 76.2 | 3 | +2 | Watch |
| 独赢策略 | 2 | 80 | 78.5 | 1 | -1 | Minor Shift |
| 赔率分布优化器 | 3 | 80 | 78.5 | 2 | -1 | Minor Shift |
| 当前推荐组合 | 4 | 60 | 47.0 | 9 | +5 | Disagreement |
| 让球策略 | 5 | 60 | 40.3 | 11 | +6 | Disagreement |
| 独赢 + 让球 | 6 | 58 | 47.2 | 8 | +2 | Watch |
| 只买最佳波胆 | 7 | 56 | 58.8 | 4 | -3 | Disagreement |
| 双波胆组合 | 8 | 55 | 58.5 | 5 | -3 | Disagreement |
| 让球 + 波胆 | 9 | 54 | 46.4 | 10 | +1 | Minor Shift |
| 主路径波胆组合 | 10 | 54 | 55.8 | 6 | -4 | Disagreement |
| 大小球策略 | 11 | 34 | 49.9 | 7 | -4 | Disagreement |

Rank Difference:

```text
scenario_rank - legacy_rank
```

Positive means Scenario Ranking downgrades the portfolio.

Negative means Scenario Ranking upgrades the portfolio.

## Legacy Top Portfolio

- Legacy Top Portfolio: 独赢 + 波胆
- Legacy Rank: 1
- Legacy Score: 93
- Scenario Rank: 3
- Scenario Score: 76.2
- Rank Difference: +2
- Shadow Verdict: Watch

Interpretation:

- Legacy top is coherent: Morocco winner plus 0:1 correct score supports the Morocco narrow-win scenario.
- Scenario Ranking does not reject it.
- It is downgraded from 1 to 3 because pure Morocco winner exposure has better stability and lower path specificity in this balanced setup.

## Scenario Top Portfolio

- Scenario Top Portfolio: 独赢策略
- Legacy Rank: 2
- Legacy Score: 80
- Scenario Rank: 1
- Scenario Score: 78.5
- Rank Difference: -1
- Shadow Verdict: Minor Shift

Tie note:

- 赔率分布优化器 also scored 78.5.
- The report gives Scenario Rank 1 to 独赢策略 because it has the earlier Legacy Rank among tied Scenario Scores and is simpler.

Interpretation:

- Scenario Ranking prefers Morocco winner-only exposure in a balanced match.
- This avoids over-committing to exact-score paths.
- It also avoids the `Home +0.5` conflict that appears in some mixed portfolios.

## Comparison With Round 1

Round 1 Germany vs Ivory Coast:

- Legacy Top: 让球策略
- Scenario Top: 赔率分布优化器
- Legacy top Scenario Rank: 4
- Verdict: Disagreement

Round 2 Scotland vs Morocco:

- Legacy Top: 独赢 + 波胆
- Scenario Top: 独赢策略
- Legacy top Scenario Rank: 3
- Verdict: Watch

Key difference:

- Round 1 showed a strong disagreement caused by role balance and tail exposure.
- Round 2 shows a softer disagreement caused by balanced-match uncertainty and the risk of over-specific score paths.

## Validation Result

Primary watch case:

```text
Legacy Rank = 1
Scenario Rank != 1
```

Detected:

- Yes.

Severity:

- Medium watch case.

Reason:

- Legacy top remains scenario-coherent, but Scenario Ranking prefers a simpler Morocco winner portfolio.

## Final Verdict

- Overall Shadow Verdict: Watch
- Critical conflict found: No
- High conflict found: No
- Legacy Top and Scenario Top differ: Yes
- Production impact: None

This validates that Shadow Mode is useful for balanced matches because it separates:

- a good but path-specific Legacy top portfolio
- from a simpler Scenario top portfolio that better handles uncertainty

## Automation Verdict

- Status: Pass for Round 2 validation report.
- Generated: `SHADOW_VALIDATION_ROUND2.md`
- No code changed.
- No UI changed.
- No Ranking changed.
- No recommendation logic changed.
- No data files changed.
- No app was run.
- No API refresh was performed.
