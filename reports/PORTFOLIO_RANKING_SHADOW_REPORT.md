# Portfolio Ranking Shadow Report v0.1

Date: 2026-06-21

Scope: report only. This run did not modify `strategy_score(...)`, `evaluate_allocation(...)`, `strategy_comparison(...)`, recommendation logic, UI, or any `data/` file.

## Match

- Match: Germany vs Ivory Coast
- Source snapshot: `data/history/2026_06_20_Germany_Ivory_Coast_pre.json`
- Scenario reference: `SCENARIO_ENGINE_REPORT.md`
- Shadow mode: enabled for report only
- Production authority: Legacy Ranking remains authoritative

## Shadow Mode Rule

```text
Legacy Ranking decides.
Scenario Ranking observes.
No recommendation, sorting, UI, or data behavior changes.
```

## Method

Legacy Rank:

- Uses the strategy order already stored in the pre-match snapshot.
- Uses existing `score` as `legacy_score`.
- Does not recalculate or alter production ranking.

Scenario Score:

- Computed only for this report from existing snapshot fields.
- Uses existing strategy metrics and Scenario Engine principles.
- Does not write back to snapshot data.

Scenario Score components:

| Component | Source |
| --- | --- |
| Value layer | Existing expected yield and Sharpe. |
| Scenario consistency layer | Existing path consistency score. |
| Asset role balance | Existing role constraint adjustment. |
| Main scenario coverage | Handicap cover assets and core correct-score assets. |
| Secondary insurance coverage | Winner/insurance assets. |
| Tail penalty | Tail exposure and extreme upside score assets. |

Main Scenario reference:

- Germany handicap-cover path.
- Core Main Return scores: 2:0, 3:0, 3:1.
- Aggressive/Tail scores: 4:0, 4:1, 4:2, 5:0, 5:1, 5:2, 5:3.

## Shadow Ranking Table

| Portfolio | Legacy Rank | Legacy Score | Scenario Score | Scenario Rank | Rank Difference | Shadow Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 让球策略 | 1 | 100 | 61.9 | 4 | +3 | Disagreement |
| 独赢 + 让球 | 2 | 100 | 64.1 | 3 | +1 | Minor Shift |
| 独赢 + 波胆 | 3 | 100 | 60.3 | 5 | +2 | Watch |
| 让球 + 波胆 | 4 | 100 | 65.8 | 2 | -2 | Watch |
| 赔率分布优化器 | 5 | 100 | 68.9 | 1 | -4 | Disagreement |
| 当前推荐组合 | 6 | 97 | 42.1 | 10 | +4 | Disagreement |
| 主路径波胆组合 | 7 | 90 | 43.3 | 8 | +1 | Minor Shift |
| 只买最佳波胆 | 8 | 88 | 50.3 | 7 | -1 | Minor Shift |
| 双波胆组合 | 9 | 86 | 43.2 | 9 | 0 | Agreement |
| 独赢策略 | 10 | 80 | 59.2 | 6 | -4 | Disagreement |

Rank Difference:

```text
scenario_rank - legacy_rank
```

Positive value means Scenario Ranking downgrades the portfolio.

Negative value means Scenario Ranking upgrades the portfolio.

## Legacy Top Portfolio

- Legacy Top Portfolio: 让球策略
- Legacy Rank: 1
- Legacy Score: 100
- Scenario Rank: 4
- Scenario Score: 61.9
- Rank Difference: +3
- Shadow Verdict: Disagreement

Reason:

- The portfolio directly expresses Germany -1.5 and therefore fits the Main Scenario direction.
- It is still narrow as a portfolio structure because it mainly depends on one handicap-cover path.
- Shadow Ranking downgrades it because role balance is weaker than more diversified scenario-aware portfolios.
- This does not change production ranking or recommendation behavior.

## Scenario Top Portfolio

- Scenario Top Portfolio: 赔率分布优化器
- Legacy Rank: 5
- Legacy Score: 100
- Scenario Rank: 1
- Scenario Score: 68.9
- Rank Difference: -4
- Shadow Verdict: Disagreement

Reason:

- It has the best role balance among available strategies.
- It combines Germany -1.5, Germany winner, and core correct-score paths 2:0, 3:0, 3:1.
- Tail exposure is 12.4%, which is inside the current target range.
- It serves the Germany handicap-cover path while keeping some secondary protection.

## Rank Difference Summary

Primary watch case detected:

```text
Legacy Rank = 1
Scenario Rank != 1
```

Observed result:

- Legacy top portfolio: 让球策略.
- Scenario top portfolio: 赔率分布优化器.
- Difference: Scenario Ranking prefers a more role-balanced portfolio over the pure handicap strategy.

Largest upgrades by Scenario Ranking:

| Portfolio | Legacy Rank | Scenario Rank | Difference | Reason |
| --- | ---: | ---: | ---: | --- |
| 赔率分布优化器 | 5 | 1 | -4 | Best role balance and broad Main Scenario coverage. |
| 独赢策略 | 10 | 6 | -4 | High value and insurance coverage, but weak Main Scenario return structure. |
| 让球 + 波胆 | 4 | 2 | -2 | Strong Main Scenario coverage with handicap plus 2:0 core return. |

Largest downgrades by Scenario Ranking:

| Portfolio | Legacy Rank | Scenario Rank | Difference | Reason |
| --- | ---: | ---: | ---: | --- |
| 当前推荐组合 | 6 | 10 | +4 | Tail exposure is high and many extreme correct scores reduce scenario clarity. |
| 让球策略 | 1 | 4 | +3 | Direction is clear, but role balance is narrow. |
| 独赢 + 波胆 | 3 | 5 | +2 | Has useful secondary coverage, but role balance is weaker. |

## Shadow Verdict

- Overall Shadow Verdict: Disagreement
- Severity: Medium
- Critical conflict detected: No
- High conflict detected: No
- Production impact: None

Interpretation:

- Shadow Mode found a meaningful difference between Legacy Ranking and Scenario Ranking.
- The difference is not a production failure because Shadow Ranking is non-authoritative.
- This is exactly the kind of case Shadow Mode is meant to observe before any ranking replacement.

## Notes For Future Validation

This single-match result is not enough to replace Legacy Ranking.

It does show that Shadow Mode is useful because:

- Legacy Ranking keeps multiple portfolios tied at 100.
- Scenario Ranking separates those tied portfolios by role balance and scenario coverage.
- Tail-heavy portfolios are downgraded.
- The legacy top portfolio remains coherent, but not the strongest scenario-aware portfolio.

Required next validation:

- Repeat across at least 20 completed matches.
- Track every case where `legacy_rank = 1` and `scenario_rank != 1`.
- Compare Shadow Verdict against post-match review.
- Keep Legacy Ranking authoritative until validation is complete.

## Automation Verdict

- Status: Pass for report-only Shadow Mode v0.1.
- `PORTFOLIO_RANKING_SHADOW_REPORT.md` generated.
- No business code changed.
- No recommendation logic changed.
- No UI changed.
- No data files changed.
- No app was run.
- No API refresh was performed.
