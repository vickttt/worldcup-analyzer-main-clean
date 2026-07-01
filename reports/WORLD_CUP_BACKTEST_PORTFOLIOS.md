# World Cup Backtest Portfolios

Date: 2026-06-21

## Scope

- Phase B pilot only: 10 completed matches.
- Reads API-Football historical odds for Match Winner, Asian Handicap, Over/Under, and Correct Score.
- Writes isolated snapshots under `data/history/backfill/` only.
- Generates report-only Legacy, Scenario, and Hybrid portfolio candidates.
- Does not modify production ranking, recommendation logic, UI, or existing history snapshots.

## France vs Senegal

- Fixture ID: `1489383`
- Sample type: 强队深盘 / 高比分局
- Final score: `3:1`
- Backfill snapshot: `data/history/backfill/2026_06_16_France_Senegal_pre.json`
- Data quality: `true_pre_match`
- Available markets: match_winner, asian_handicap, over_under, correct_score

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Shadow Verdict | Guardrail | Hybrid Rank Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Legacy Value Portfolio | 1 | 6 | 6 | 100.0 | 8.7 | Disagreement | Blocked | Guardrails block this portfolio from default ranking leadership: Shadow Disagreement, Tail-heavy, Not default-eligible without explanation |
| Tail Upside Portfolio | 2 | 4 | 4 | 100.0 | 39.6 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Recommended Blend Portfolio | 3 | 1 | 1 | 85.9 | 46.9 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Direction + Return Portfolio | 4 | 2 | 2 | 80.0 | 42.6 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Scenario Balanced Portfolio | 5 | 3 | 5 | 78.7 | 39.6 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Tempo Watch Portfolio | 6 | 5 | 3 | 70.0 | 41.1 | Agreement | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |

- Legacy Top: Legacy Value Portfolio | Hit: `miss` | P/L: -1000 | ROI: -100.0% | Max Drawdown: -1000
- Scenario Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: +834 | ROI: 83.4% | Max Drawdown: -172
- Hybrid Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: +834 | ROI: 83.4% | Max Drawdown: -172

- Match winner: `Draw`

## Argentina vs Algeria

- Fixture ID: `1489381`
- Sample type: 强队深盘
- Final score: `3:0`
- Backfill snapshot: `data/history/backfill/2026_06_17_Argentina_Algeria_pre.json`
- Data quality: `true_pre_match`
- Available markets: match_winner, asian_handicap, over_under, correct_score

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Shadow Verdict | Guardrail | Hybrid Rank Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Legacy Value Portfolio | 1 | 6 | 6 | 100.0 | 8.7 | Disagreement | Blocked | Guardrails block this portfolio from default ranking leadership: Shadow Disagreement, Tail-heavy, Not default-eligible without explanation |
| Tail Upside Portfolio | 2 | 4 | 5 | 100.0 | 39.6 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Recommended Blend Portfolio | 3 | 1 | 1 | 86.9 | 47.0 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Direction + Return Portfolio | 4 | 2 | 2 | 80.1 | 42.7 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Scenario Balanced Portfolio | 5 | 3 | 4 | 78.7 | 39.7 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Tempo Watch Portfolio | 6 | 5 | 3 | 70.3 | 41.1 | Agreement | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |

- Legacy Top: Legacy Value Portfolio | Hit: `partial_hit` | P/L: +1275 | ROI: 127.5% | Max Drawdown: -766
- Scenario Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: +1049 | ROI: 104.9% | Max Drawdown: -149
- Hybrid Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: +1049 | ROI: 104.9% | Max Drawdown: -149

- Match winner: `Legacy Winner`

## Portugal vs Congo DR

- Fixture ID: `1539003`
- Sample type: 冷门风险局 / 低比分局
- Final score: `1:1`
- Backfill snapshot: `data/history/backfill/2026_06_17_Portugal_Congo_DR_pre.json`
- Data quality: `true_pre_match`
- Available markets: match_winner, asian_handicap, over_under, correct_score

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Shadow Verdict | Guardrail | Hybrid Rank Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Legacy Value Portfolio | 1 | 6 | 6 | 100.0 | 2.3 | Disagreement | Blocked | Guardrails block this portfolio from default ranking leadership: Shadow Disagreement, Tail-heavy, Not default-eligible without explanation |
| Tail Upside Portfolio | 2 | 4 | 4 | 100.0 | 39.9 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Recommended Blend Portfolio | 3 | 1 | 1 | 82.8 | 46.5 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Direction + Return Portfolio | 4 | 2 | 2 | 78.7 | 42.5 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Scenario Balanced Portfolio | 5 | 3 | 5 | 77.6 | 39.4 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Tempo Watch Portfolio | 6 | 5 | 3 | 68.7 | 41.0 | Agreement | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |

- Legacy Top: Legacy Value Portfolio | Hit: `miss` | P/L: -1000 | ROI: -100.0% | Max Drawdown: -1000
- Scenario Top: Recommended Blend Portfolio | Hit: `miss` | P/L: -1000 | ROI: -100.0% | Max Drawdown: -1000
- Hybrid Top: Recommended Blend Portfolio | Hit: `miss` | P/L: -1000 | ROI: -100.0% | Max Drawdown: -1000

- Match winner: `Draw`

## England vs Croatia

- Fixture ID: `1489384`
- Sample type: 平衡局 / 高比分局
- Final score: `4:2`
- Backfill snapshot: `data/history/backfill/2026_06_17_England_Croatia_pre.json`
- Data quality: `true_pre_match`
- Available markets: match_winner, asian_handicap, over_under, correct_score

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Shadow Verdict | Guardrail | Hybrid Rank Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Legacy Value Portfolio | 1 | 6 | 6 | 100.0 | 8.7 | Disagreement | Blocked | Guardrails block this portfolio from default ranking leadership: Shadow Disagreement, Tail-heavy, Not default-eligible without explanation |
| Tail Upside Portfolio | 2 | 4 | 5 | 100.0 | 39.4 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Recommended Blend Portfolio | 3 | 1 | 1 | 82.2 | 46.9 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Direction + Return Portfolio | 4 | 2 | 2 | 76.1 | 42.5 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Scenario Balanced Portfolio | 5 | 3 | 4 | 75.0 | 39.5 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Tempo Watch Portfolio | 6 | 5 | 3 | 72.6 | 41.4 | Agreement | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |

- Legacy Top: Legacy Value Portfolio | Hit: `partial_hit` | P/L: +5182 | ROI: 518.2% | Max Drawdown: -903
- Scenario Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: +735 | ROI: 73.5% | Max Drawdown: -157
- Hybrid Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: +735 | ROI: 73.5% | Max Drawdown: -157

- Match winner: `Legacy Winner`

## Canada vs Qatar

- Fixture ID: `1489387`
- Sample type: 强队深盘 / 高比分局
- Final score: `6:0`
- Backfill snapshot: `data/history/backfill/2026_06_18_Canada_Qatar_pre.json`
- Data quality: `true_pre_match`
- Available markets: match_winner, asian_handicap, over_under, correct_score

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Shadow Verdict | Guardrail | Hybrid Rank Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Legacy Value Portfolio | 1 | 6 | 6 | 100.0 | 10.3 | Disagreement | Blocked | Guardrails block this portfolio from default ranking leadership: Shadow Disagreement, Tail-heavy, Not default-eligible without explanation |
| Tail Upside Portfolio | 2 | 4 | 4 | 100.0 | 39.9 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Recommended Blend Portfolio | 3 | 1 | 1 | 83.1 | 46.6 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Direction + Return Portfolio | 4 | 2 | 2 | 79.0 | 42.5 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Scenario Balanced Portfolio | 5 | 3 | 5 | 77.9 | 39.5 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Tempo Watch Portfolio | 6 | 5 | 3 | 68.8 | 41.0 | Agreement | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |

- Legacy Top: Legacy Value Portfolio | Hit: `miss` | P/L: -1000 | ROI: -100.0% | Max Drawdown: -1000
- Scenario Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: +274 | ROI: 27.4% | Max Drawdown: -201
- Hybrid Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: +274 | ROI: 27.4% | Max Drawdown: -201

- Match winner: `Draw`

## Scotland vs Morocco

- Fixture ID: `1489390`
- Sample type: 平衡局 / 冷门风险局
- Final score: `0:1`
- Backfill snapshot: `data/history/backfill/2026_06_19_Scotland_Morocco_pre.json`
- Data quality: `true_pre_match`
- Available markets: match_winner, asian_handicap, over_under, correct_score

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Shadow Verdict | Guardrail | Hybrid Rank Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Legacy Value Portfolio | 1 | 6 | 6 | 100.0 | 5.9 | Disagreement | Blocked | Guardrails block this portfolio from default ranking leadership: Shadow Disagreement, Tail-heavy, Not default-eligible without explanation |
| Tail Upside Portfolio | 2 | 4 | 5 | 100.0 | 39.4 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Recommended Blend Portfolio | 3 | 1 | 1 | 82.1 | 46.9 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Direction + Return Portfolio | 4 | 2 | 2 | 75.9 | 42.6 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Scenario Balanced Portfolio | 5 | 3 | 4 | 74.8 | 39.6 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Tempo Watch Portfolio | 6 | 5 | 3 | 72.3 | 41.3 | Agreement | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |

- Legacy Top: Legacy Value Portfolio | Hit: `miss` | P/L: -1000 | ROI: -100.0% | Max Drawdown: -1000
- Scenario Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: -205 | ROI: -20.5% | Max Drawdown: -622
- Hybrid Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: -205 | ROI: -20.5% | Max Drawdown: -622

- Match winner: `Draw`

## Brazil vs Haiti

- Fixture ID: `1489389`
- Sample type: 强队深盘
- Final score: `3:0`
- Backfill snapshot: `data/history/backfill/2026_06_20_Brazil_Haiti_pre.json`
- Data quality: `true_pre_match`
- Available markets: match_winner, asian_handicap, over_under, correct_score

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Shadow Verdict | Guardrail | Hybrid Rank Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Legacy Value Portfolio | 1 | 6 | 6 | 100.0 | 6.1 | Disagreement | Blocked | Guardrails block this portfolio from default ranking leadership: Shadow Disagreement, Tail-heavy, Not default-eligible without explanation |
| Recommended Blend Portfolio | 2 | 5 | 5 | 92.6 | 22.4 | Disagreement | Watch | Hybrid rank keeps this portfolio under observation because: Shadow Disagreement, Scenario consistency warning, Not default-eligible without explanation |
| Direction + Return Portfolio | 3 | 1 | 1 | 80.1 | 46.5 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Scenario Balanced Portfolio | 4 | 2 | 2 | 78.7 | 42.6 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Tempo Watch Portfolio | 5 | 3 | 3 | 73.8 | 40.5 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Tail Upside Portfolio | 6 | 4 | 4 | 73.8 | 37.5 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |

- Legacy Top: Legacy Value Portfolio | Hit: `partial_hit` | P/L: +685 | ROI: 68.5% | Max Drawdown: -734
- Scenario Top: Direction + Return Portfolio | Hit: `partial_hit` | P/L: +729 | ROI: 72.9% | Max Drawdown: -112
- Hybrid Top: Direction + Return Portfolio | Hit: `partial_hit` | P/L: +729 | ROI: 72.9% | Max Drawdown: -112

- Match winner: `Draw`

## Netherlands vs Sweden

- Fixture ID: `1539007`
- Sample type: 平衡局 / 高比分局
- Final score: `5:1`
- Backfill snapshot: `data/history/backfill/2026_06_20_Netherlands_Sweden_pre.json`
- Data quality: `true_pre_match`
- Available markets: match_winner, asian_handicap, over_under, correct_score

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Shadow Verdict | Guardrail | Hybrid Rank Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Legacy Value Portfolio | 1 | 6 | 6 | 100.0 | 9.0 | Disagreement | Blocked | Guardrails block this portfolio from default ranking leadership: Shadow Disagreement, Tail-heavy, Not default-eligible without explanation |
| Tail Upside Portfolio | 2 | 4 | 5 | 100.0 | 39.6 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Recommended Blend Portfolio | 3 | 1 | 1 | 88.4 | 47.2 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Direction + Return Portfolio | 4 | 2 | 2 | 82.2 | 42.9 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Scenario Balanced Portfolio | 5 | 3 | 4 | 80.8 | 39.9 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Tempo Watch Portfolio | 6 | 5 | 3 | 71.5 | 41.2 | Agreement | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |

- Legacy Top: Legacy Value Portfolio | Hit: `partial_hit` | P/L: +3507 | ROI: 350.6% | Max Drawdown: -908
- Scenario Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: +831 | ROI: 83.1% | Max Drawdown: -201
- Hybrid Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: +831 | ROI: 83.1% | Max Drawdown: -201

- Match winner: `Legacy Winner`

## Germany vs Ivory Coast

- Fixture ID: `1489393`
- Sample type: 强队深盘 / 盘口边界
- Final score: `2:1`
- Backfill snapshot: `data/history/backfill/2026_06_20_Germany_Ivory_Coast_pre.json`
- Data quality: `true_pre_match`
- Available markets: match_winner, asian_handicap, over_under, correct_score

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Shadow Verdict | Guardrail | Hybrid Rank Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Legacy Value Portfolio | 1 | 6 | 6 | 100.0 | 8.8 | Disagreement | Blocked | Guardrails block this portfolio from default ranking leadership: Shadow Disagreement, Tail-heavy, Not default-eligible without explanation |
| Tail Upside Portfolio | 2 | 4 | 5 | 100.0 | 39.6 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Recommended Blend Portfolio | 3 | 1 | 1 | 85.6 | 46.9 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Direction + Return Portfolio | 4 | 2 | 2 | 80.3 | 42.7 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Scenario Balanced Portfolio | 5 | 3 | 4 | 79.2 | 39.7 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Tempo Watch Portfolio | 6 | 5 | 3 | 69.8 | 41.1 | Agreement | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |

- Legacy Top: Legacy Value Portfolio | Hit: `miss` | P/L: -1000 | ROI: -100.0% | Max Drawdown: -1000
- Scenario Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: -428 | ROI: -42.8% | Max Drawdown: -612
- Hybrid Top: Recommended Blend Portfolio | Hit: `partial_hit` | P/L: -428 | ROI: -42.8% | Max Drawdown: -612

- Match winner: `Draw`

## Ecuador vs Curaçao

- Fixture ID: `1489392`
- Sample type: 平衡局 / 低比分局
- Final score: `0:0`
- Backfill snapshot: `data/history/backfill/2026_06_21_Ecuador_Cura_ao_pre.json`
- Data quality: `true_pre_match`
- Available markets: match_winner, asian_handicap, over_under, correct_score

| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Shadow Verdict | Guardrail | Hybrid Rank Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Legacy Value Portfolio | 1 | 6 | 6 | 100.0 | 9.8 | Disagreement | Blocked | Guardrails block this portfolio from default ranking leadership: Shadow Disagreement, Tail-heavy, Not default-eligible without explanation |
| Tail Upside Portfolio | 2 | 4 | 4 | 100.0 | 39.9 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Recommended Blend Portfolio | 3 | 1 | 1 | 81.7 | 46.5 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Scenario Balanced Portfolio | 4 | 2 | 2 | 77.0 | 42.5 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Direction + Return Portfolio | 5 | 3 | 5 | 75.6 | 39.2 | Watch | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |
| Tempo Watch Portfolio | 6 | 5 | 3 | 67.9 | 40.9 | Agreement | Watch | Hybrid rank keeps this portfolio under observation because: Scenario consistency warning |

- Legacy Top: Legacy Value Portfolio | Hit: `miss` | P/L: -1000 | ROI: -100.0% | Max Drawdown: -1000
- Scenario Top: Recommended Blend Portfolio | Hit: `miss` | P/L: -1000 | ROI: -100.0% | Max Drawdown: -1000
- Hybrid Top: Recommended Blend Portfolio | Hit: `miss` | P/L: -1000 | ROI: -100.0% | Max Drawdown: -1000

- Match winner: `Draw`
