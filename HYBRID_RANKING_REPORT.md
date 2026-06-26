# Hybrid Ranking Report v0.1

## Scope

- Phase A only: Hybrid Report Only.
- Reads saved history snapshots from `data/history/`.
- Reuses `attach_shadow_metadata(...)` to derive Scenario Rank and Shadow Verdict in memory.
- Computes `strategy["hybrid"]` in memory for reporting only.
- Writes only `HYBRID_RANKING_REPORT.md`.
- Does not modify `app.py`, UI, production sorting, recommendation logic, score functions, or data files.

## Hybrid Score v0.1 Inputs

- Legacy Score / expected yield / ROI proxy / Sharpe.
- Scenario Rank.
- Shadow Verdict.
- Scenario Consistency Score.
- Max Loss.
- Tail exposure and pure tempo penalty when available.
- Main Scenario Coverage and Secondary Insurance Coverage proxies from existing strategy fields.

## Cross-Match Summary

| Match | Legacy Top | Scenario Top | Hybrid Top | Hybrid Guardrail Status |
| --- | --- | --- | --- | --- |
| 土耳其 vs 巴拉圭 | 推荐组合 | 推荐组合 | 推荐组合 | Blocked |
| 美国 vs 澳大利亚 | 推荐组合（当前最优） | 推荐组合（当前最优） | 推荐组合（当前最优） | Blocked |
| 巴西 vs 海地 | 推荐组合 | 第4组合 | 推荐组合 | Blocked |
| 厄瓜多尔 vs 库拉索 | 推荐组合 | 第9组合 | 第3组合 | Eligible |
| 德国 vs 科特迪瓦 | 推荐组合 | 第5组合 | 第4组合 | Eligible |
| 荷兰 vs 瑞典 | 推荐组合 | 推荐组合 | 推荐组合 | Eligible |
| 苏格兰 vs 摩洛哥 | 推荐组合 | 第2组合 | 第2组合 | Blocked |
| 土耳其 vs 巴拉圭 | 推荐组合 | 第5组合 | 第4组合 | Blocked |
| 突尼斯 vs 日本 | 推荐组合 | 第7组合 | 第7组合 | Watch |
| 美国 vs 澳大利亚 | 推荐组合 | 推荐组合 | 推荐组合 | Blocked |
| 比利时 vs 伊朗 | 推荐组合 | 第4组合 | 第2组合 | Eligible |
| 厄瓜多尔 vs 库拉索 | 推荐组合 | 第8组合 | 第10组合 | Eligible |
| 新西兰 vs 埃及 | 推荐组合 | 第7组合 | 第7组合 | Watch |
| 西班牙 vs 沙特阿拉伯 | 推荐组合 | 第7组合 | 推荐组合 | Eligible |
| 突尼斯 vs 日本 | 推荐组合 | 第7组合 | 第4组合 | Eligible |
| 加拿大 vs 卡塔尔 | 推荐组合（当前最优） | 推荐组合（当前最优） | 推荐组合（当前最优） | Watch |
| 瑞士 vs 波黑 | 推荐组合（当前最优） | 备选组合4 | 备选组合3 | Blocked |

## Summary Metrics

- Snapshots scanned: 19.
- Snapshots with strategies: 17.
- Snapshots skipped because strategies were missing: 2.
- Legacy Top differs from Hybrid Top: 10.
- Scenario Top differs from Hybrid Top: 9.

## Match Details

## 土耳其 vs 巴拉圭

- Source snapshot: `data/history/2026_06_19_Turkey_Paraguay_pre.json`
- Strategy count: 9
- Legacy Top: 推荐组合
- Scenario Top: 推荐组合
- Hybrid Top: 推荐组合
- Hybrid Top Guardrail Status: Blocked

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 推荐组合 | 1 | 1 | 1 | 100.0 | 54.6 | Blocked |
| 第2组合 | 2 | 2 | 2 | 100.0 | 50.6 | Blocked |
| 第3组合 | 3 | 3 | 3 | 100.0 | 47.6 | Blocked |
| 第4组合 | 4 | 4 | 4 | 76.0 | 38.5 | Blocked |
| 推荐组合 | 5 | 5 | 5 | 65.0 | 35.8 | Blocked |
| 第6组合 | 6 | 6 | 6 | 54.0 | 25.8 | Blocked |
| 第7组合 | 7 | 7 | 7 | 37.0 | 1.2 | Blocked |
| 第8组合 | 8 | 8 | 8 | 37.0 | 1.2 | Blocked |
| 第9组合 | 9 | 9 | 9 | 36.0 | 0.0 | Blocked |

### Hybrid Top Reason

- Guardrails block this portfolio from default ranking leadership: Low scenario consistency

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: Yes
- Legacy Top == Hybrid Top: Yes
- Scenario Top == Hybrid Top: Yes

## 美国 vs 澳大利亚

- Source snapshot: `data/history/2026_06_19_United_States_Australia_pre.json`
- Strategy count: 5
- Legacy Top: 推荐组合（当前最优）
- Scenario Top: 推荐组合（当前最优）
- Hybrid Top: 推荐组合（当前最优）
- Hybrid Top Guardrail Status: Blocked

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 推荐组合（当前最优） | 1 | 1 | 1 | 80.0 | 59.5 | Blocked |
| 备选组合1 | 2 | 2 | 2 | 80.0 | 55.5 | Blocked |
| 备选组合2 | 3 | 3 | 3 | 80.0 | 52.5 | Blocked |
| 备选组合3 | 4 | 4 | 4 | 80.0 | 49.5 | Blocked |
| 备选组合4 | 5 | 5 | 5 | 80.0 | 49.5 | Blocked |

### Hybrid Top Reason

- Guardrails block this portfolio from default ranking leadership: Low scenario consistency

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: Yes
- Legacy Top == Hybrid Top: Yes
- Scenario Top == Hybrid Top: Yes

## 巴西 vs 海地

- Source snapshot: `data/history/2026_06_20_Brazil_Haiti_pre.json`
- Strategy count: 6
- Legacy Top: 推荐组合
- Scenario Top: 第4组合
- Hybrid Top: 推荐组合
- Hybrid Top Guardrail Status: Blocked

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 推荐组合 | 3 | 4 | 1 | 66.0 | 42.8 | Blocked |
| 第4组合 | 4 | 1 | 2 | 66.0 | 42.1 | Blocked |
| 第5组合 | 5 | 2 | 3 | 66.0 | 38.1 | Blocked |
| 第6组合 | 6 | 3 | 4 | 66.0 | 35.1 | Blocked |
| 推荐组合 | 1 | 5 | 5 | 80.0 | 15.6 | Blocked |
| 第2组合 | 2 | 6 | 6 | 80.0 | 15.6 | Blocked |

### Hybrid Top Reason

- Guardrails block this portfolio from default ranking leadership: Low scenario consistency

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: Yes
- Scenario Top == Hybrid Top: No

## 厄瓜多尔 vs 库拉索

- Source snapshot: `data/history/2026_06_20_Ecuador_Cura_ao_pre.json`
- Strategy count: 10
- Legacy Top: 推荐组合
- Scenario Top: 第9组合
- Hybrid Top: 第3组合
- Hybrid Top Guardrail Status: Eligible

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 第3组合 | 3 | 3 | 1 | 42.0 | 40.8 | Eligible |
| 第6组合 | 6 | 7 | 2 | 38.0 | 39.9 | Eligible |
| 第4组合 | 4 | 4 | 3 | 42.0 | 37.8 | Eligible |
| 第10组合 | 10 | 8 | 4 | 29.0 | 36.6 | Eligible |
| 第2组合 | 2 | 5 | 5 | 44.0 | 34.4 | Watch |
| 第9组合 | 9 | 1 | 6 | 32.0 | 32.7 | Watch |
| 第8组合 | 8 | 2 | 7 | 34.0 | 29.8 | Watch |
| 推荐组合 | 1 | 6 | 8 | 45.0 | 22.7 | Watch |
| 第5组合 | 5 | 9 | 9 | 38.0 | 12.9 | Watch |
| 第7组合 | 7 | 10 | 10 | 38.0 | 12.9 | Watch |

### Hybrid Top Reason

- Hybrid rank balances legacy value metrics with scenario consistency and controlled downside.

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: No
- Scenario Top == Hybrid Top: No

## 德国 vs 科特迪瓦

- Source snapshot: `data/history/2026_06_20_Germany_Ivory_Coast_pre.json`
- Strategy count: 10
- Legacy Top: 推荐组合
- Scenario Top: 第5组合
- Hybrid Top: 第4组合
- Hybrid Top Guardrail Status: Eligible

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 第4组合 | 4 | 2 | 1 | 100.0 | 47.5 | Eligible |
| 推荐组合 | 1 | 3 | 2 | 100.0 | 47.2 | Eligible |
| 第10组合 | 10 | 4 | 3 | 80.0 | 40.0 | Watch |
| 第5组合 | 5 | 1 | 4 | 100.0 | 39.3 | Watch |
| 第2组合 | 2 | 5 | 5 | 100.0 | 37.2 | Watch |
| 第3组合 | 3 | 8 | 6 | 100.0 | 34.2 | Watch |
| 第8组合 | 8 | 6 | 7 | 88.0 | 32.8 | Watch |
| 第9组合 | 9 | 9 | 8 | 86.0 | 31.8 | Eligible |
| 第6组合 | 6 | 7 | 9 | 97.0 | 27.9 | Watch |
| 第7组合 | 7 | 10 | 10 | 90.0 | 17.8 | Watch |

### Hybrid Top Reason

- Hybrid rank balances legacy value metrics with scenario consistency and controlled downside.

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: No
- Scenario Top == Hybrid Top: No

## 荷兰 vs 瑞典

- Source snapshot: `data/history/2026_06_20_Netherlands_Sweden_pre.json`
- Strategy count: 5
- Legacy Top: 推荐组合
- Scenario Top: 推荐组合
- Hybrid Top: 推荐组合
- Hybrid Top Guardrail Status: Eligible

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 推荐组合 | 1 | 1 | 1 | 80.0 | 63.4 | Eligible |
| 第2组合 | 2 | 2 | 2 | 80.0 | 59.4 | Eligible |
| 第3组合 | 3 | 3 | 3 | 80.0 | 56.4 | Eligible |
| 第4组合 | 4 | 4 | 4 | 80.0 | 53.4 | Eligible |
| 第5组合 | 5 | 5 | 5 | 80.0 | 53.4 | Eligible |

### Hybrid Top Reason

- Hybrid rank rewards Scenario Rank 1 with acceptable value and risk controls.

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: Yes
- Legacy Top == Hybrid Top: Yes
- Scenario Top == Hybrid Top: Yes

## 苏格兰 vs 摩洛哥

- Source snapshot: `data/history/2026_06_20_Scotland_Morocco_pre.json`
- Strategy count: 11
- Legacy Top: 推荐组合
- Scenario Top: 第2组合
- Hybrid Top: 第2组合
- Hybrid Top Guardrail Status: Blocked

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 第2组合 | 2 | 1 | 1 | 80.0 | 56.7 | Blocked |
| 第3组合 | 3 | 2 | 2 | 80.0 | 52.7 | Blocked |
| 第6组合 | 6 | 8 | 3 | 58.0 | 40.4 | Blocked |
| 推荐组合 | 4 | 4 | 4 | 60.0 | 32.3 | Blocked |
| 第5组合 | 5 | 5 | 5 | 60.0 | 30.4 | Blocked |
| 第7组合 | 7 | 6 | 6 | 56.0 | 28.7 | Blocked |
| 推荐组合 | 1 | 7 | 7 | 93.0 | 28.1 | Blocked |
| 第8组合 | 8 | 9 | 8 | 55.0 | 26.9 | Blocked |
| 第10组合 | 10 | 10 | 9 | 54.0 | 24.5 | Blocked |
| 第9组合 | 9 | 3 | 10 | 54.0 | 17.6 | Blocked |
| 第11组合 | 11 | 11 | 11 | 34.0 | 3.5 | Blocked |

### Hybrid Top Reason

- Guardrails block this portfolio from default ranking leadership: Low scenario consistency

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: No
- Scenario Top == Hybrid Top: Yes

## 土耳其 vs 巴拉圭

- Source snapshot: `data/history/2026_06_20_T_rkiye_Paraguay_pre.json`
- Strategy count: 11
- Legacy Top: 推荐组合
- Scenario Top: 第5组合
- Hybrid Top: 第4组合
- Hybrid Top Guardrail Status: Blocked

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 第4组合 | 4 | 2 | 1 | 80.0 | 49.9 | Blocked |
| 推荐组合 | 1 | 3 | 2 | 100.0 | 44.8 | Blocked |
| 第2组合 | 2 | 4 | 3 | 100.0 | 41.8 | Blocked |
| 第3组合 | 3 | 5 | 4 | 96.0 | 41.4 | Blocked |
| 第6组合 | 6 | 7 | 5 | 59.0 | 34.5 | Blocked |
| 第5组合 | 5 | 1 | 6 | 69.0 | 33.2 | Blocked |
| 第7组合 | 7 | 6 | 7 | 53.0 | 25.5 | Blocked |
| 第10组合 | 10 | 9 | 8 | 35.0 | 3.5 | Blocked |
| 第8组合 | 8 | 10 | 9 | 37.0 | 0.0 | Blocked |
| 第9组合 | 9 | 11 | 10 | 35.0 | 0.0 | Blocked |
| 推荐组合 | 11 | 8 | 11 | 34.0 | 0.0 | Blocked |

### Hybrid Top Reason

- Guardrails block this portfolio from default ranking leadership: Low scenario consistency

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: No
- Scenario Top == Hybrid Top: No

## 突尼斯 vs 日本

- Source snapshot: `data/history/2026_06_20_Tunisia_Japan_pre.json`
- Strategy count: 10
- Legacy Top: 推荐组合
- Scenario Top: 第7组合
- Hybrid Top: 第7组合
- Hybrid Top Guardrail Status: Watch

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 第7组合 | 7 | 1 | 1 | 40.0 | 39.4 | Watch |
| 第6组合 | 6 | 10 | 2 | 41.0 | 39.3 | Watch |
| 推荐组合 | 1 | 4 | 3 | 66.0 | 37.8 | Watch |
| 第2组合 | 2 | 5 | 4 | 66.0 | 37.8 | Watch |
| 第5组合 | 5 | 3 | 5 | 42.0 | 35.0 | Eligible |
| 第8组合 | 8 | 8 | 6 | 40.0 | 32.8 | Eligible |
| 第9组合 | 9 | 9 | 7 | 40.0 | 32.7 | Eligible |
| 第4组合 | 4 | 6 | 8 | 45.0 | 31.4 | Eligible |
| 第3组合 | 3 | 7 | 9 | 47.0 | 28.9 | Watch |
| 第10组合 | 10 | 2 | 10 | 34.0 | 28.9 | Watch |

### Hybrid Top Reason

- Hybrid rank keeps this portfolio under observation because: Shadow Disagreement, Not default-eligible without explanation

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: No
- Scenario Top == Hybrid Top: Yes

## 美国 vs 澳大利亚

- Source snapshot: `data/history/2026_06_20_United_States_Australia_pre.json`
- Strategy count: 5
- Legacy Top: 推荐组合
- Scenario Top: 推荐组合
- Hybrid Top: 推荐组合
- Hybrid Top Guardrail Status: Blocked

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 推荐组合 | 1 | 1 | 1 | 80.0 | 57.2 | Blocked |
| 第2组合 | 2 | 2 | 2 | 80.0 | 53.2 | Blocked |
| 第3组合 | 3 | 3 | 3 | 80.0 | 50.2 | Blocked |
| 第4组合 | 4 | 4 | 4 | 80.0 | 47.2 | Blocked |
| 第5组合 | 5 | 5 | 5 | 80.0 | 47.2 | Blocked |

### Hybrid Top Reason

- Guardrails block this portfolio from default ranking leadership: Low scenario consistency

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: Yes
- Legacy Top == Hybrid Top: Yes
- Scenario Top == Hybrid Top: Yes

## 比利时 vs 伊朗

- Source snapshot: `data/history/2026_06_21_Belgium_Iran_pre.json`
- Strategy count: 10
- Legacy Top: 推荐组合
- Scenario Top: 第4组合
- Hybrid Top: 第2组合
- Hybrid Top Guardrail Status: Eligible

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 第2组合 | 2 | 2 | 1 | 59.0 | 49.1 | Eligible |
| 第3组合 | 3 | 3 | 2 | 59.0 | 46.1 | Eligible |
| 第5组合 | 5 | 7 | 3 | 54.0 | 40.9 | Eligible |
| 推荐组合 | 1 | 4 | 4 | 66.0 | 38.0 | Watch |
| 第4组合 | 4 | 1 | 5 | 57.0 | 37.8 | Watch |
| 第6组合 | 6 | 8 | 6 | 52.0 | 37.0 | Eligible |
| 第8组合 | 8 | 6 | 7 | 41.0 | 27.0 | Watch |
| 第9组合 | 9 | 10 | 8 | 37.0 | 25.5 | Eligible |
| 第7组合 | 7 | 5 | 9 | 41.0 | 24.4 | Eligible |
| 第10组合 | 10 | 9 | 10 | 36.0 | 24.2 | Eligible |

### Hybrid Top Reason

- Hybrid rank balances legacy value metrics with scenario consistency and controlled downside.

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: No
- Scenario Top == Hybrid Top: No

## 厄瓜多尔 vs 库拉索

- Source snapshot: `data/history/2026_06_21_Ecuador_Cura_ao_pre.json`
- Strategy count: 11
- Legacy Top: 推荐组合
- Scenario Top: 第8组合
- Hybrid Top: 第10组合
- Hybrid Top Guardrail Status: Eligible

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 第10组合 | 10 | 8 | 1 | 29.0 | 35.0 | Eligible |
| 第6组合 | 6 | 3 | 2 | 36.0 | 34.9 | Watch |
| 第9组合 | 9 | 7 | 3 | 29.0 | 30.9 | Eligible |
| 第8组合 | 8 | 1 | 4 | 30.0 | 29.0 | Watch |
| 第7组合 | 7 | 2 | 5 | 34.0 | 25.1 | Watch |
| 推荐组合 | 1 | 4 | 6 | 45.0 | 21.5 | Watch |
| 第2组合 | 2 | 5 | 7 | 45.0 | 21.5 | Watch |
| 第3组合 | 3 | 6 | 8 | 42.0 | 18.3 | Watch |
| 第11组合 | 11 | 11 | 9 | 29.0 | 8.9 | Blocked |
| 第4组合 | 4 | 9 | 10 | 38.0 | 6.1 | Watch |
| 第5组合 | 5 | 10 | 11 | 38.0 | 6.1 | Watch |

### Hybrid Top Reason

- Hybrid rank balances legacy value metrics with scenario consistency and controlled downside.

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: No
- Scenario Top == Hybrid Top: No

## 新西兰 vs 埃及

- Source snapshot: `data/history/2026_06_21_New_Zealand_Egypt_pre.json`
- Strategy count: 9
- Legacy Top: 推荐组合
- Scenario Top: 第7组合
- Hybrid Top: 第7组合
- Hybrid Top Guardrail Status: Watch

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 第7组合 | 7 | 1 | 1 | 42.0 | 34.1 | Watch |
| 第5组合 | 5 | 6 | 2 | 44.0 | 33.9 | Eligible |
| 第8组合 | 8 | 2 | 3 | 42.0 | 30.1 | Watch |
| 第3组合 | 3 | 5 | 4 | 44.0 | 29.9 | Eligible |
| 第9组合 | 9 | 3 | 5 | 42.0 | 28.8 | Watch |
| 第6组合 | 6 | 9 | 6 | 42.0 | 21.1 | Watch |
| 推荐组合 | 1 | 4 | 7 | 44.0 | 20.9 | Watch |
| 第2组合 | 2 | 7 | 8 | 44.0 | 19.1 | Watch |
| 第4组合 | 4 | 8 | 9 | 44.0 | 18.3 | Watch |

### Hybrid Top Reason

- Hybrid rank keeps this portfolio under observation because: Shadow Disagreement, Not default-eligible without explanation

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: No
- Scenario Top == Hybrid Top: Yes

## 西班牙 vs 沙特阿拉伯

- Source snapshot: `data/history/2026_06_21_Spain_Saudi_Arabia_pre.json`
- Strategy count: 10
- Legacy Top: 推荐组合
- Scenario Top: 第7组合
- Hybrid Top: 推荐组合
- Hybrid Top Guardrail Status: Eligible

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 推荐组合 | 1 | 2 | 1 | 44.0 | 53.6 | Eligible |
| 第2组合 | 2 | 3 | 2 | 44.0 | 50.6 | Eligible |
| 第4组合 | 4 | 5 | 3 | 42.0 | 34.0 | Eligible |
| 第9组合 | 9 | 6 | 4 | 29.0 | 22.3 | Watch |
| 第7组合 | 7 | 1 | 5 | 33.0 | 20.7 | Watch |
| 第10组合 | 10 | 7 | 6 | 29.0 | 20.0 | Watch |
| 第8组合 | 8 | 4 | 7 | 30.0 | 13.4 | Watch |
| 第3组合 | 3 | 8 | 8 | 42.0 | 0.4 | Blocked |
| 第5组合 | 5 | 9 | 9 | 36.0 | 0.0 | Blocked |
| 第6组合 | 6 | 10 | 10 | 35.0 | 0.0 | Blocked |

### Hybrid Top Reason

- Hybrid rank balances legacy value metrics with scenario consistency and controlled downside.

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: Yes
- Scenario Top == Hybrid Top: No

## 突尼斯 vs 日本

- Source snapshot: `data/history/2026_06_21_Tunisia_Japan_pre.json`
- Strategy count: 10
- Legacy Top: 推荐组合
- Scenario Top: 第7组合
- Hybrid Top: 第4组合
- Hybrid Top Guardrail Status: Eligible

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 第4组合 | 4 | 4 | 1 | 59.0 | 43.5 | Eligible |
| 第7组合 | 7 | 1 | 2 | 57.0 | 38.6 | Watch |
| 第5组合 | 5 | 10 | 3 | 58.0 | 38.3 | Watch |
| 第2组合 | 2 | 6 | 4 | 60.0 | 36.1 | Watch |
| 第3组合 | 3 | 7 | 5 | 60.0 | 36.1 | Watch |
| 第6组合 | 6 | 2 | 6 | 58.0 | 35.9 | Watch |
| 第9组合 | 9 | 8 | 7 | 41.0 | 34.1 | Eligible |
| 第10组合 | 10 | 9 | 8 | 41.0 | 34.1 | Eligible |
| 第8组合 | 8 | 3 | 9 | 41.0 | 28.5 | Watch |
| 推荐组合 | 1 | 5 | 10 | 62.0 | 27.0 | Watch |

### Hybrid Top Reason

- Hybrid rank balances legacy value metrics with scenario consistency and controlled downside.

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: No
- Scenario Top == Hybrid Top: No

## 加拿大 vs 卡塔尔

- Source snapshot: `data/history/2026_06_18_Canada_Qatar.json`
- Strategy count: 5
- Legacy Top: 推荐组合（当前最优）
- Scenario Top: 推荐组合（当前最优）
- Hybrid Top: 推荐组合（当前最优）
- Hybrid Top Guardrail Status: Watch

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 推荐组合（当前最优） | 1 | 1 | 1 | 80.0 | 51.1 | Watch |
| 备选组合1 | 2 | 2 | 2 | 80.0 | 47.1 | Watch |
| 备选组合2 | 3 | 3 | 3 | 80.0 | 44.1 | Watch |
| 备选组合3 | 4 | 4 | 4 | 80.0 | 41.1 | Watch |
| 备选组合4 | 5 | 5 | 5 | 80.0 | 41.1 | Watch |

### Hybrid Top Reason

- Hybrid rank keeps this portfolio under observation because: Scenario consistency warning

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: Yes
- Legacy Top == Hybrid Top: Yes
- Scenario Top == Hybrid Top: Yes

## 瑞士 vs 波黑

- Source snapshot: `data/history/2026_06_18_Switzerland_Bosnia_and_Herzegovina.json`
- Strategy count: 11
- Legacy Top: 推荐组合（当前最优）
- Scenario Top: 备选组合4
- Hybrid Top: 备选组合3
- Hybrid Top Guardrail Status: Blocked

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 备选组合3 | 4 | 2 | 1 | 84.0 | 40.0 | Blocked |
| 推荐组合（当前最优） | 1 | 3 | 2 | 94.0 | 38.0 | Blocked |
| 备选组合4 | 5 | 1 | 3 | 80.0 | 38.0 | Watch |
| 第6优组合 | 6 | 7 | 4 | 78.0 | 32.5 | Blocked |
| 备选组合1 | 2 | 4 | 5 | 94.0 | 32.1 | Blocked |
| 第7优组合 | 7 | 5 | 6 | 72.0 | 29.9 | Blocked |
| 第8优组合 | 8 | 10 | 7 | 62.0 | 22.8 | Blocked |
| 备选组合2 | 3 | 6 | 8 | 88.0 | 21.7 | Blocked |
| 第9优组合 | 9 | 11 | 9 | 48.0 | 19.1 | Blocked |
| 第10优组合 | 10 | 9 | 10 | 38.0 | 18.1 | Blocked |
| 第11优组合 | 11 | 8 | 11 | 34.0 | 6.6 | Blocked |

### Hybrid Top Reason

- Guardrails block this portfolio from default ranking leadership: Low scenario consistency

### Legacy vs Scenario vs Hybrid

- Legacy Top == Scenario Top: No
- Legacy Top == Hybrid Top: No
- Scenario Top == Hybrid Top: No

## Automation Verdict

- `HYBRID_RANKING_REPORT.md` generated: Yes.
- Sorting changed: No.
- Recommendation logic changed: No.
- UI changed: No.
- Data files changed: No.
- Production authority changed: No.
