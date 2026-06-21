# Post-Match Validation Report v0.1

Date: 2026-06-21

## Scope

- Reads existing pre-match snapshots and post-match final scores.
- Reads standalone My Portfolio history files from `data/history/my_portfolios/` when available.
- Settles Legacy Top, Scenario Top, Current Recommendation, and My Portfolio when available.
- Generates this report only.
- Does not modify sorting, recommendation logic, scores, UI, or data files.

## Validation Summary

- Post-match files discovered: 2.
- Valid comparisons: 2.
- Insufficient comparisons: 0.

## 瑞士 vs 波黑

- Pre snapshot: `data/history/2026_06_18_Switzerland_Bosnia_and_Herzegovina.json`
- Post result: `data/history/2026_06_18_Switzerland_Bosnia_and_Herzegovina_post.json`
- Final score: `4:1`
- Legacy Top Portfolio: 推荐组合（当前最优）
- Scenario Top Portfolio: 备选组合4
- Current Recommendation: 推荐组合（当前最优）
- My Portfolio source: `data/history/my_portfolios/2026_06_18_Switzerland_Bosnia_and_Herzegovina.json`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合（当前最优） | Legacy Top | 1 | 3 | Watch | hit | +906 | 75.5% | -0 |
| 备选组合4 | Scenario Top | 5 | 1 | Disagreement | hit | +660 | 55.0% | -0 |
| 推荐组合（当前最优） | Current Recommendation | 1 | 3 | Watch | hit | +906 | 75.5% | -0 |
| My Portfolio | My Portfolio | - | - | - | miss | -1500 | -100.0% | -1500 |

### Legacy vs Scenario

- Result: `Legacy Winner`
- Reason: Legacy Top ROI is materially higher than Scenario Top ROI.
- Legacy Rank 1 downgrade reason: Scenario ranking downgraded this portfolio because it has limited main-scenario return coverage.

## 美国 vs 澳大利亚

- Pre snapshot: `data/history/2026_06_19_United_States_Australia_pre.json`
- Post result: `data/history/2026_06_19_United_States_Australia_post.json`
- Final score: `2:0`
- Legacy Top Portfolio: 推荐组合（当前最优）
- Scenario Top Portfolio: 推荐组合（当前最优）
- Current Recommendation: 推荐组合（当前最优）
- My Portfolio source: `data/history/my_portfolios/2026_06_19_United_States_Australia.json`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合（当前最优） | Legacy Top | 1 | 1 | Agreement | hit | +66 | 66.0% | -0 |
| 推荐组合（当前最优） | Scenario Top | 1 | 1 | Agreement | hit | +66 | 66.0% | -0 |
| 推荐组合（当前最优） | Current Recommendation | 1 | 1 | Agreement | hit | +66 | 66.0% | -0 |
| My Portfolio | My Portfolio | - | - | - | hit | +858 | 57.2% | -0 |

### Legacy vs Scenario

- Result: `Draw`
- Reason: ROI gap is below the 2 percentage point material threshold.
- Legacy Rank 1 downgrade reason: Legacy ranking and scenario ranking broadly agree.

## 5-Match Promotion Rule

After 5 valid post-match validations, enter `Scenario Guardrails Phase` only if all conditions hold:

- Scenario Top ROI >= Legacy Top ROI.
- Scenario Top wins at least 3 matches or is not worse than Legacy.
- Scenario Top does not have materially larger drawdown.
- Scenario Rank downgrade reasons for Legacy Rank 1 are supported by post-match outcomes.

Scenario Guardrails Phase means:

- Legacy Rank 1 with `Shadow Verdict = Disagreement` must show a strong warning.
- Scenario Rank 1 can be marked as `剧本优先候选`.
- Tail-heavy / pure tempo / low consistency portfolios cannot become default recommendations without warning.
- Scenario Rank can influence default recommendation eligibility.
- Legacy score sorting remains in place temporarily.

It does not mean replacing `strategy_score(...)` or changing production sorting immediately.

## Current Promotion Evaluation

- Valid matches: 2 / 5 required.
- Scenario wins: 0.
- Legacy wins: 1.
- Draws: 1.
- Legacy aggregate ROI: 74.8%.
- Scenario aggregate ROI: 55.8%.
- Promotion status: `Keep Shadow Mode`.
- Reason: Only 2 valid post-match validations are available; 5 are required.

## Automation Verdict

- `POST_MATCH_VALIDATION_REPORT.md` generated: Yes.
- Sorting changed: No.
- Recommendation logic changed: No.
- Score changed: No.
- Data files modified: No.
- Current production recommendation authority: Legacy Ranking remains authoritative.
