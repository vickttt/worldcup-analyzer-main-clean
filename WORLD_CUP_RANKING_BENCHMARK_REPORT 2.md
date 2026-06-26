# World Cup Ranking Benchmark Report

Date: 2026-06-21

## Phase B Pilot Summary

- Valid matches: 10.
- Invalid odds matches: 0.
- Legacy Wins: 3.
- Scenario Wins: 0.
- Hybrid Wins: 0.
- Draws: 7.
- Legacy ROI: 46.5%.
- Scenario ROI: 18.2%.
- Hybrid ROI: 18.2%.
- Hybrid vs Legacy Edge: -28.3%.
- Hybrid vs Scenario Edge: 0.0%.
- Best system in this pilot: `Legacy`.

## Match-Level Benchmark

| Match | Type | Quality | Legacy Top ROI | Scenario Top ROI | Hybrid Top ROI | Winner |
| --- | --- | --- | ---: | ---: | ---: | --- |
| France vs Senegal | 强队深盘 / 高比分局 | true_pre_match | -100.0% | 83.4% | 83.4% | Draw |
| Argentina vs Algeria | 强队深盘 | true_pre_match | 127.5% | 104.9% | 104.9% | Legacy Winner |
| Portugal vs Congo DR | 冷门风险局 / 低比分局 | true_pre_match | -100.0% | -100.0% | -100.0% | Draw |
| England vs Croatia | 平衡局 / 高比分局 | true_pre_match | 518.2% | 73.5% | 73.5% | Legacy Winner |
| Canada vs Qatar | 强队深盘 / 高比分局 | true_pre_match | -100.0% | 27.4% | 27.4% | Draw |
| Scotland vs Morocco | 平衡局 / 冷门风险局 | true_pre_match | -100.0% | -20.5% | -20.5% | Draw |
| Brazil vs Haiti | 强队深盘 | true_pre_match | 68.5% | 72.9% | 72.9% | Draw |
| Netherlands vs Sweden | 平衡局 / 高比分局 | true_pre_match | 350.6% | 83.1% | 83.1% | Legacy Winner |
| Germany vs Ivory Coast | 强队深盘 / 盘口边界 | true_pre_match | -100.0% | -42.8% | -42.8% | Draw |
| Ecuador vs Curaçao | 平衡局 / 低比分局 | true_pre_match | -100.0% | -100.0% | -100.0% | Draw |

## Data Quality

| Match | Match Winner | Asian Handicap | Over/Under | Correct Score |
| --- | --- | --- | --- | --- |
| France vs Senegal | true_pre_match | true_pre_match | true_pre_match | true_pre_match |
| Argentina vs Algeria | true_pre_match | true_pre_match | true_pre_match | true_pre_match |
| Portugal vs Congo DR | true_pre_match | true_pre_match | true_pre_match | true_pre_match |
| England vs Croatia | true_pre_match | true_pre_match | true_pre_match | true_pre_match |
| Canada vs Qatar | true_pre_match | true_pre_match | true_pre_match | true_pre_match |
| Scotland vs Morocco | true_pre_match | true_pre_match | true_pre_match | true_pre_match |
| Brazil vs Haiti | true_pre_match | true_pre_match | true_pre_match | true_pre_match |
| Netherlands vs Sweden | true_pre_match | true_pre_match | true_pre_match | true_pre_match |
| Germany vs Ivory Coast | true_pre_match | true_pre_match | true_pre_match | true_pre_match |
| Ecuador vs Curaçao | true_pre_match | true_pre_match | true_pre_match | true_pre_match |

## Phase C Recommendation

- Recommendation: `Phase C Ready`.
- Phase C should still remain report-only until the full completed-match benchmark confirms Hybrid stability.
- No production sorting, UI, recommendation logic, or historical source snapshots were modified by this pilot.
