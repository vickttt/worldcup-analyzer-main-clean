# Backtest Attribution Review 20260625

## Executive Summary

- Reviewed: `/Users/zijianchen/Documents/Codex/2026-06-14/1-vs-2-polymarket-3-4/worldcup-analyzer/reports/backtests/backtest_summary_20260625.md` and `/Users/zijianchen/Documents/Codex/2026-06-14/1-vs-2-polymarket-3-4/worldcup-analyzer/reports/backtests/backtest_results_20260625.csv`
- Total matches: 15
- Portfolio rows: 161
- Total stake: 144500
- Net profit: -19874
- Total ROI: -13.8%
- Win rate: 43.5%
- Rank #1 losing rows: 10
- Best style by total profit: Aggressive
- Worst style by total profit: System

Main conclusion: the first negative ROI is mainly explained by zero-risk portfolio collapse, one-goal handicap deviation, and draw/adjacent paths not being covered. This report is attribution only; no weights were changed.

## Overall Results

- Backtest matches: 17
- Portfolio rows: 161
- Overall ROI from source summary: -13.8%
- Recomputed total ROI from CSV: -13.8%

## Portfolio Style Performance

| portfolio_style | matches_count | total_stake | total_profit | roi | win_rate | average_profit | max_loss | best_match | worst_match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Aggressive | 4 | 3900 | -351 | -9.0% | 25.0% | -88 | -714 | 苏格兰 vs 巴西 | 摩洛哥 vs 海地 |
| Tail Hedge | 4 | 3900 | -671 | -17.2% | 25.0% | -168 | -988 | 苏格兰 vs 巴西 | 摩洛哥 vs 海地 |
| Conservative | 1 | 1100 | -710 | -64.5% | 0.0% | -710 | -710 | 苏格兰 vs 巴西 | 苏格兰 vs 巴西 |
| Recommendation / Rank #1 | 15 | 15300 | -1156 | -7.6% | 52.4% | -55 | -1800 | 波黑 vs 卡塔尔 | 厄瓜多尔 vs 库拉索 |
| My Portfolio | 7 | 8400 | -1689 | -20.1% | 42.9% | -241 | -1500 | 美国 vs 澳大利亚 | Switzerland vs Bosnia and Herzegovina |
| System | 15 | 111900 | -15297 | -13.7% | 43.5% | -123 | -1800 | 土耳其 vs 巴拉圭 | 厄瓜多尔 vs 库拉索 |

## Rank #1 Failure Review

| match_name | actual_score | portfolio | style | profit | roi | patterns |
| --- | --- | --- | --- | --- | --- | --- |
| 土耳其 vs 巴拉圭 | 0:1 | 推荐组合 | Recommendation / Rank #1 | -100.0 | -1.0 | low_odds_false_safety;market_direction_wrong |
| 土耳其 vs 巴拉圭 | 0:1 | 推荐组合 | Recommendation / Rank #1 | -100.0 | -1.0 | low_odds_false_safety;market_direction_wrong |
| 巴西 vs 海地 | 3:0 | 推荐组合 | Recommendation / Rank #1 | -100.0 | -1.0 | low_odds_false_safety |
| 厄瓜多尔 vs 库拉索 | 0:0 | 推荐组合 | Recommendation / Rank #1 | -1800.0 | -1.0 | draw_path_missed;low_odds_false_safety |
| 德国 vs 科特迪瓦 | 2:1 | 推荐组合 | Recommendation / Rank #1 | -1800.0 | -1.0 | low_odds_false_safety;market_direction_wrong |
| 土耳其 vs 巴拉圭 | 0:1 | 推荐组合 | Recommendation / Rank #1 | -1500.0 | -1.0 | low_odds_false_safety;market_direction_wrong |
| 土耳其 vs 巴拉圭 | 0:1 | 推荐组合 | Recommendation / Rank #1 | -351.69 | -0.2345 | market_direction_wrong |
| 捷克 vs 墨西哥 | 0:3 | 推荐组合 | Recommendation / Rank #1 | -100.0 | -1.0 | correct_score_over_concentrated;low_odds_false_safety |
| 摩洛哥 vs 海地 | 4:2 | 推荐组合 | Recommendation / Rank #1 | -94.0 | -0.052 | correct_score_over_concentrated;underdog_goal_broke_clean_sheet |
| 南非 vs 韩国 | 1:0 | 推荐组合 | Recommendation / Rank #1 | -300.0 | -1.0 | correct_score_over_concentrated;low_odds_false_safety;market_direction_wrong |

## Strong Favorite Not Covering Review

- Rank #1 deep/handicap related failures: 0
- This pattern indicates that deep or margin-sensitive assets need review before any further score tuning.

Affected rows:

- None.

## Underdog Goal Tail Review

- Rank #1 failures with clean-sheet score exposure broken by underdog goal: 1
- Recommendation direction: review 2:1 / 3:1 / 1:1 tails when the underdog has must-score motivation or late volatility.

| match_name | actual_score | portfolio_name | profit | underdog_goal_tail_included | recommended_fix |
| --- | --- | --- | --- | --- | --- |
| 摩洛哥 vs 海地 | 4:2 | 推荐组合 | -94.0 | False | Add or reweight underdog-goal adjacent score paths. |

## Draw Path Review

- Rank #1 draw-path failures: 1
- Recommendation direction: review draw / under / 1:1 / 0:0 coverage in both-draw-acceptable and direct qualification battle matches.

| match_name | actual_score | portfolio_name | profit | draw_path_included | recommended_fix |
| --- | --- | --- | --- | --- | --- |
| 厄瓜多尔 vs 库拉索 | 0:0 | 推荐组合 | -1800.0 | False | Review draw/under coverage in pressure-sensitive games. |

## Qualification Pressure Review

| match_pressure_type | matches | rank1_roi | conservative_roi | aggressive_roi | tail_hedge_roi | common_failure_pattern |
| --- | --- | --- | --- | --- | --- | --- |
| unknown | 15 | - | - | - | - | low_odds_false_safety |

Current evidence is partial because many historical snapshots were generated before full pressure metadata was saved. Where pressure type is missing, the report marks it as `unknown`.

## My Portfolio vs System

| match_name | my_portfolio_profit | system_rank1_profit | difference | winner | reason |
| --- | --- | --- | --- | --- | --- |
| Switzerland vs Bosnia and Herzegovina | -1500 | 906 | -2406 | System | 系统首选更高或相同 |
| 美国 vs 澳大利亚 | 858 | 66 | 792 | My Portfolio | 用户组合收益更高 |
| 波黑 vs 卡塔尔 | -100 | 1545 | -1645 | System | 系统首选更高或相同 |
| 捷克 vs 墨西哥 | 0 | -100 | 100 | My Portfolio | 用户组合收益更高 |
| 苏格兰 vs 巴西 | 77 | 330 | -253 | System | 系统首选更高或相同 |
| 南非 vs 韩国 | -1400 | -300 | -1100 | System | 系统首选更高或相同 |
| 瑞士 vs 加拿大 | 376 | 905 | -529 | System | 系统首选更高或相同 |

## Failure Pattern Frequency

- low_odds_false_safety: 65
- correct_score_over_concentrated: 42
- market_direction_wrong: 38
- underdog_goal_broke_clean_sheet: 20
- draw_path_missed: 10
- over_under_wrong: 3

## Tuning Recommendations

1. Reduce deep handicap preference when a favorite is already qualified, draw acceptable, or favorite win margin is not required.
   Evidence: one-goal deviation and handicap-related failures appear repeatedly in Rank #1 losing rows.

2. Increase underdog-goal tail review when the underdog must win or the favorite may rotate/control tempo.
   Evidence: clean-sheet correct-score concentration can lose when actual score includes an underdog goal.

3. Improve draw coverage when both teams can accept a draw or qualification battle incentives reduce early tempo.
   Evidence: draw-path failures exist and current pressure metadata is incomplete in older snapshots.

4. Limit correct-score concentration when the portfolio contains only clean-sheet favorite scores.
   Evidence: correct-score over-concentration appears as a recurring losing-row label.

5. Review Coverage Efficiency thresholds only after inspecting per-match rows, not from aggregate ROI alone.

## What Not To Change Yet

- Do not change Portfolio Score weights from this report alone.
- Do not remove Tail Hedge or Aggressive portfolios before comparing per-pressure-type samples.
- Do not assume Qualification Pressure failed where historical pressure metadata is missing.
- Do not tune correct-score probabilities until more post-match samples are reviewed.
- Do not add new data sources for this attribution round.
