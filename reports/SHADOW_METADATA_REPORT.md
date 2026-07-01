# Shadow Metadata Report

## Scope

- Validates `attach_shadow_metadata(...)` on three saved local snapshots.
- Adds only in-memory `strategy["shadow"]` metadata during report generation.
- Does not modify Legacy Ranking, scores, recommendation logic, UI, or data files.

## Required Shadow Fields

- `legacy_rank`
- `legacy_score`
- `scenario_rank`
- `scenario_score`
- `rank_difference`
- `shadow_verdict`
- `scenario_rank_reason`

## Germany vs Ivory Coast

- Validation label: Round 1 strong favorite / handicap-cover
- Source snapshot: `data/history/2026_06_20_Germany_Ivory_Coast_pre.json`
- Match display: 德国 vs 科特迪瓦
- Strategy count: 10
- Every strategy has `shadow`: Yes
- Legacy top portfolio: 推荐组合
- Scenario top portfolio: 第5组合
- Legacy top Scenario Rank: 3
- Legacy top Shadow Verdict: Watch

| Portfolio | Legacy Rank | Legacy Score | Scenario Rank | Scenario Score | Rank Difference | Shadow Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 推荐组合 | 1 | 100 | 3 | 58.2 | +2 | Watch |
| 第2组合 | 2 | 100 | 5 | 49.3 | +3 | Disagreement |
| 第3组合 | 3 | 100 | 8 | 43.9 | +5 | Disagreement |
| 第4组合 | 4 | 100 | 2 | 60.7 | -2 | Watch |
| 第5组合 | 5 | 100 | 1 | 64.6 | -4 | Disagreement |
| 第6组合 | 6 | 97 | 7 | 47.1 | +1 | Agreement |
| 第7组合 | 7 | 90 | 10 | 36.8 | +3 | Disagreement |
| 第8组合 | 8 | 88 | 6 | 49.2 | -2 | Watch |
| 第9组合 | 9 | 86 | 9 | 37.2 | +0 | Agreement |
| 第10组合 | 10 | 80 | 4 | 57.1 | -6 | Disagreement |

### Legacy Top Reason

- Scenario ranking downgraded this portfolio because its scenario structure is weaker than alternatives.

## Scotland vs Morocco

- Validation label: Round 2 balanced match
- Source snapshot: `data/history/2026_06_20_Scotland_Morocco_pre.json`
- Match display: 苏格兰 vs 摩洛哥
- Strategy count: 11
- Every strategy has `shadow`: Yes
- Legacy top portfolio: 推荐组合
- Scenario top portfolio: 第2组合
- Legacy top Scenario Rank: 7
- Legacy top Shadow Verdict: Disagreement

| Portfolio | Legacy Rank | Legacy Score | Scenario Rank | Scenario Score | Rank Difference | Shadow Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 推荐组合 | 1 | 93 | 7 | 45.0 | +6 | Disagreement |
| 第2组合 | 2 | 80 | 1 | 55.2 | -1 | Agreement |
| 第3组合 | 3 | 80 | 2 | 55.2 | -1 | Agreement |
| 推荐组合 | 4 | 60 | 4 | 48.6 | +0 | Agreement |
| 第5组合 | 5 | 60 | 5 | 46.8 | +0 | Agreement |
| 第6组合 | 6 | 58 | 8 | 43.2 | +2 | Watch |
| 第7组合 | 7 | 56 | 6 | 45.1 | -1 | Agreement |
| 第8组合 | 8 | 55 | 9 | 42.4 | +1 | Agreement |
| 第9组合 | 9 | 54 | 3 | 48.7 | -6 | Disagreement |
| 第10组合 | 10 | 54 | 10 | 41.0 | +0 | Agreement |
| 第11组合 | 11 | 34 | 11 | 15.2 | +0 | Agreement |

### Legacy Top Reason

- Scenario ranking downgraded this portfolio because its scenario structure is weaker than alternatives.

## Brazil vs Haiti

- Validation label: Round 3 cold-risk / crowded favorite
- Source snapshot: `data/history/2026_06_20_Brazil_Haiti_pre.json`
- Match display: 巴西 vs 海地
- Strategy count: 6
- Every strategy has `shadow`: Yes
- Legacy top portfolio: 推荐组合
- Scenario top portfolio: 第4组合
- Legacy top Scenario Rank: 5
- Legacy top Shadow Verdict: Disagreement

| Portfolio | Legacy Rank | Legacy Score | Scenario Rank | Scenario Score | Rank Difference | Shadow Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 推荐组合 | 1 | 80 | 5 | 29.2 | +4 | Disagreement |
| 第2组合 | 2 | 80 | 6 | 29.2 | +4 | Disagreement |
| 推荐组合 | 3 | 66 | 4 | 54.1 | +1 | Agreement |
| 第4组合 | 4 | 66 | 1 | 55.8 | -3 | Disagreement |
| 第5组合 | 5 | 66 | 2 | 55.8 | -3 | Disagreement |
| 第6组合 | 6 | 66 | 3 | 55.8 | -3 | Disagreement |

### Legacy Top Reason

- Scenario ranking downgraded this portfolio because it is mainly a tempo asset and has weak direction coverage.

## Cross-Match Summary

| Match | Strategies | All Have Shadow | Legacy Top | Scenario Top | Legacy Top Scenario Rank | Verdict |
| --- | ---: | --- | --- | --- | ---: | --- |
| Germany vs Ivory Coast | 10 | Yes | 推荐组合 | 第5组合 | 3 | Watch |
| Scotland vs Morocco | 11 | Yes | 推荐组合 | 第2组合 | 7 | Disagreement |
| Brazil vs Haiti | 6 | Yes | 推荐组合 | 第4组合 | 5 | Disagreement |

## Verification Verdict

- `strategy["shadow"]` generated: Yes
- Legacy order changed: No
- Legacy score changed: No
- Recommendation logic changed: No
- UI changed: No
- Data files changed: No
