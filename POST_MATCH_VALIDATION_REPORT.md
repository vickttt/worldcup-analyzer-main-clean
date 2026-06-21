# Post-Match Validation Report v0.1

Date: 2026-06-21

## Scope

- Reads existing pre-match snapshots and post-match final scores.
- Reads standalone My Portfolio history files from `data/history/my_portfolios/` when available.
- Settles Legacy Top, Scenario Top, Current Recommendation, and My Portfolio when available.
- Generates this report only.
- Does not modify sorting, recommendation logic, scores, UI, or data files.

## Validation Summary

- Post-match files discovered: 14.
- Valid comparisons: 12.
- Insufficient comparisons: 2.

## 加拿大 vs 卡塔尔

- Pre snapshot: `data/history/2026_06_18_Canada_Qatar.json`
- Post result: `data/history/2026_06_18_Canada_Qatar_post.json`
- Final score: `6:0`
- Legacy Top Portfolio: 推荐组合（当前最优）
- Scenario Top Portfolio: 推荐组合（当前最优）
- Current Recommendation: 推荐组合（当前最优）
- My Portfolio source: `pre_snapshot.my_portfolio`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合（当前最优） | Legacy Top | 1 | 1 | Agreement | hit | +28 | 28.0% | -0 |
| 推荐组合（当前最优） | Scenario Top | 1 | 1 | Agreement | hit | +28 | 28.0% | -0 |
| 推荐组合（当前最优） | Current Recommendation | 1 | 1 | Agreement | hit | +28 | 28.0% | -0 |

### Legacy vs Scenario

- Result: `Draw`
- Reason: ROI gap is below the 2 percentage point material threshold.
- Legacy Rank 1 downgrade reason: Legacy ranking and scenario ranking broadly agree.

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

## Skipped: `2026_06_19_Brazil_Haiti_post.json`

- Reason: missing_score_or_strategies

## Skipped: `2026_06_19_Scotland_Morocco_post.json`

- Reason: missing_score_or_strategies

## 土耳其 vs 巴拉圭

- Pre snapshot: `data/history/2026_06_19_Turkey_Paraguay_pre.json`
- Post result: `data/history/2026_06_19_Turkey_Paraguay_post.json`
- Final score: `0:1`
- Legacy Top Portfolio: 推荐组合
- Scenario Top Portfolio: 推荐组合
- Current Recommendation: 推荐组合
- My Portfolio source: `pre_snapshot.my_portfolio`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合 | Legacy Top | 1 | 1 | Agreement | miss | -100 | -100.0% | -100 |
| 推荐组合 | Scenario Top | 1 | 1 | Agreement | miss | -100 | -100.0% | -100 |
| 推荐组合 | Current Recommendation | 1 | 1 | Agreement | miss | -100 | -100.0% | -100 |

### Legacy vs Scenario

- Result: `Draw`
- Reason: ROI gap is below the 2 percentage point material threshold.
- Legacy Rank 1 downgrade reason: Legacy ranking and scenario ranking broadly agree.

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

## 巴西 vs 海地

- Pre snapshot: `data/history/2026_06_20_Brazil_Haiti_pre.json`
- Post result: `data/history/2026_06_20_Brazil_Haiti_post.json`
- Final score: `3:0`
- Legacy Top Portfolio: 推荐组合
- Scenario Top Portfolio: 第4组合
- Current Recommendation: 推荐组合
- My Portfolio source: `pre_snapshot.my_portfolio`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合 | Legacy Top | 1 | 5 | Disagreement | miss | -100 | -100.0% | -100 |
| 第4组合 | Scenario Top | 4 | 1 | Disagreement | hit | +8 | 8.0% | -0 |
| 推荐组合 | Current Recommendation | 1 | 5 | Disagreement | miss | -100 | -100.0% | -100 |

### Legacy vs Scenario

- Result: `Scenario Winner`
- Reason: Scenario Top ROI is materially higher than Legacy Top ROI.
- Legacy Rank 1 downgrade reason: Scenario ranking downgraded this portfolio because it is mainly a tempo asset and has weak direction coverage.

## 厄瓜多尔 vs 库拉索

- Pre snapshot: `data/history/2026_06_20_Ecuador_Cura_ao_pre.json`
- Post result: `data/history/2026_06_20_Ecuador_Cura_ao_post.json`
- Final score: `0:0`
- Legacy Top Portfolio: 推荐组合
- Scenario Top Portfolio: 第9组合
- Current Recommendation: 推荐组合
- My Portfolio source: `data/history/my_portfolios/2026_06_20_Ecuador_Cura_ao.json`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合 | Legacy Top | 1 | 6 | Disagreement | miss | -1800 | -100.0% | -1800 |
| 第9组合 | Scenario Top | 9 | 1 | Disagreement | miss | -1800 | -100.0% | -1800 |
| 推荐组合 | Current Recommendation | 1 | 6 | Disagreement | miss | -1800 | -100.0% | -1800 |
| My Portfolio | My Portfolio | - | - | - | miss | -1000 | -100.0% | -1000 |

### Legacy vs Scenario

- Result: `Draw`
- Reason: ROI gap is below the 2 percentage point material threshold.
- Legacy Rank 1 downgrade reason: Scenario ranking downgraded this portfolio because its scenario structure is weaker than alternatives.

## 德国 vs 科特迪瓦

- Pre snapshot: `data/history/2026_06_20_Germany_Ivory_Coast_pre.json`
- Post result: `data/history/2026_06_20_Germany_Ivory_Coast_post.json`
- Final score: `2:1`
- Legacy Top Portfolio: 推荐组合
- Scenario Top Portfolio: 第5组合
- Current Recommendation: 推荐组合
- My Portfolio source: `data/history/my_portfolios/2026_06_20_Germany_Ivory_Coast.json`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合 | Legacy Top | 1 | 3 | Watch | miss | -1800 | -100.0% | -1800 |
| 第5组合 | Scenario Top | 5 | 1 | Disagreement | partial_hit | -1347 | -74.8% | -1500 |
| 推荐组合 | Current Recommendation | 1 | 3 | Watch | miss | -1800 | -100.0% | -1800 |
| My Portfolio | My Portfolio | - | - | - | partial_hit | -800 | -50.0% | -1500 |

### Legacy vs Scenario

- Result: `Scenario Winner`
- Reason: Scenario Top ROI is materially higher than Legacy Top ROI.
- Legacy Rank 1 downgrade reason: Scenario ranking downgraded this portfolio because its scenario structure is weaker than alternatives.

## 荷兰 vs 瑞典

- Pre snapshot: `data/history/2026_06_20_Netherlands_Sweden_pre.json`
- Post result: `data/history/2026_06_20_Netherlands_Sweden_post.json`
- Final score: `5:1`
- Legacy Top Portfolio: 推荐组合
- Scenario Top Portfolio: 推荐组合
- Current Recommendation: 推荐组合
- My Portfolio source: `pre_snapshot.my_portfolio`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合 | Legacy Top | 1 | 1 | Agreement | hit | +72 | 72.0% | -0 |
| 推荐组合 | Scenario Top | 1 | 1 | Agreement | hit | +72 | 72.0% | -0 |
| 推荐组合 | Current Recommendation | 1 | 1 | Agreement | hit | +72 | 72.0% | -0 |

### Legacy vs Scenario

- Result: `Draw`
- Reason: ROI gap is below the 2 percentage point material threshold.
- Legacy Rank 1 downgrade reason: Legacy ranking and scenario ranking broadly agree.

## 苏格兰 vs 摩洛哥

- Pre snapshot: `data/history/2026_06_20_Scotland_Morocco_pre.json`
- Post result: `data/history/2026_06_20_Scotland_Morocco_post.json`
- Final score: `0:1`
- Legacy Top Portfolio: 推荐组合
- Scenario Top Portfolio: 第2组合
- Current Recommendation: 推荐组合
- My Portfolio source: `pre_snapshot.my_portfolio`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合 | Legacy Top | 1 | 7 | Disagreement | hit | +594 | 197.9% | -0 |
| 第2组合 | Scenario Top | 2 | 1 | Agreement | hit | +210 | 70.0% | -0 |
| 推荐组合 | Current Recommendation | 1 | 7 | Disagreement | hit | +594 | 197.9% | -0 |

### Legacy vs Scenario

- Result: `Legacy Winner`
- Reason: Legacy Top ROI is materially higher than Scenario Top ROI.
- Legacy Rank 1 downgrade reason: Scenario ranking downgraded this portfolio because its scenario structure is weaker than alternatives.

## 土耳其 vs 巴拉圭

- Pre snapshot: `data/history/2026_06_20_T_rkiye_Paraguay_pre.json`
- Post result: `data/history/2026_06_20_T_rkiye_Paraguay_post.json`
- Final score: `0:1`
- Legacy Top Portfolio: 推荐组合
- Scenario Top Portfolio: 第5组合
- Current Recommendation: 推荐组合
- My Portfolio source: `pre_snapshot.my_portfolio`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合 | Legacy Top | 1 | 3 | Watch | miss | -1500 | -100.0% | -1500 |
| 第5组合 | Scenario Top | 5 | 1 | Disagreement | partial_hit | +2378 | 158.5% | -1100 |
| 推荐组合 | Current Recommendation | 1 | 3 | Watch | miss | -1500 | -100.0% | -1500 |

### Legacy vs Scenario

- Result: `Scenario Winner`
- Reason: Scenario Top ROI is materially higher than Legacy Top ROI.
- Legacy Rank 1 downgrade reason: Scenario ranking downgraded this portfolio because its scenario structure is weaker than alternatives.

## 突尼斯 vs 日本

- Pre snapshot: `data/history/2026_06_20_Tunisia_Japan_pre.json`
- Post result: `data/history/2026_06_20_Tunisia_Japan_post.json`
- Final score: `0:4`
- Legacy Top Portfolio: 推荐组合
- Scenario Top Portfolio: 第7组合
- Current Recommendation: 推荐组合
- My Portfolio source: `data/history/my_portfolios/2026_06_20_Tunisia_Japan.json`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合 | Legacy Top | 1 | 4 | Disagreement | hit | +350 | 50.0% | -0 |
| 第7组合 | Scenario Top | 7 | 1 | Disagreement | partial_hit | -400 | -57.1% | -500 |
| 推荐组合 | Current Recommendation | 1 | 4 | Disagreement | hit | +350 | 50.0% | -0 |
| My Portfolio | My Portfolio | - | - | - | partial_hit | +160 | 16.0% | -200 |

### Legacy vs Scenario

- Result: `Legacy Winner`
- Reason: Legacy Top ROI is materially higher than Scenario Top ROI.
- Legacy Rank 1 downgrade reason: Scenario ranking downgraded this portfolio because it has limited main-scenario return coverage.

## 美国 vs 澳大利亚

- Pre snapshot: `data/history/2026_06_20_United_States_Australia_pre.json`
- Post result: `data/history/2026_06_20_United_States_Australia_post.json`
- Final score: `2:0`
- Legacy Top Portfolio: 推荐组合
- Scenario Top Portfolio: 推荐组合
- Current Recommendation: 推荐组合
- My Portfolio source: `pre_snapshot.my_portfolio`

| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 推荐组合 | Legacy Top | 1 | 1 | Agreement | hit | +60 | 60.0% | -0 |
| 推荐组合 | Scenario Top | 1 | 1 | Agreement | hit | +60 | 60.0% | -0 |
| 推荐组合 | Current Recommendation | 1 | 1 | Agreement | hit | +60 | 60.0% | -0 |

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

- Valid matches: 12 / 5 required.
- Scenario wins: 3.
- Legacy wins: 3.
- Draws: 6.
- Legacy aggregate ROI: -40.8%.
- Scenario aggregate ROI: -2.1%.
- Promotion status: `Enter Scenario Guardrails Phase`.
- Reason: The 5-match promotion rule is satisfied.

## Automation Verdict

- `POST_MATCH_VALIDATION_REPORT.md` generated: Yes.
- Sorting changed: No.
- Recommendation logic changed: No.
- Score changed: No.
- Data files modified: No.
- Current production recommendation authority: Legacy Ranking remains authoritative.
