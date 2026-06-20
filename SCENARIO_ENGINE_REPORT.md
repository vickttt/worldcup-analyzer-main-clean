# Scenario Engine Report

## Match

- Match: Germany vs Ivory Coast
- Competition: World Cup 2026
- Round: group
- Group: E
- Venue: Toronto Stadium, Toronto, Canada
- Kickoff: 06/20/2026 16:00
- Data mode: read-only local snapshots

## Source Snapshot Summary

- Files read:
- `data/history/2026_06_20_Germany_Ivory_Coast_pre.json`
- `data/worldcup2026/2026_06_20_Germany_Ivory_Coast/pre_match.json`
- `data/worldcup2026/2026_06_20_Germany_Ivory_Coast/odds.json`
- `data/worldcup2026/2026_06_20_Germany_Ivory_Coast/fixture.json`
- System final recommendation: `Germany -1.5`
- Recommendation reason: 市场共识明显支持德国; 逆向分数处于偏高区间; 爆冷指数高于基准水平; 让球盘相比独赢具备更好的风险收益比
- Final confidence score: 92 / 100
- Value rating: A
- Participation advice: 强烈参与
- Recommended stake: 1800
- Favorite market probability: 63.3%
- Upset index: 60 / 100 (中等爆冷风险)
- Main total line: 2.5
- Top path distribution:
  - 德国赢2球: 26.4% - 盘口边界路径，决定让球盘输赢。
  - 德国赢3球以上: 23.0% - 强队大胜路径，过去版本容易低估。
  - 平局区间: 21.4% - 比赛进入低分差或胶着路径。
  - 德国小胜（1球）: 20.3% - 市场主路径之一，强队赢但不打穿深盘。
  - 科特迪瓦不败: 8.8% - 爆冷或热门方向失效路径。

## Main Scenario

- Name: 德国 handicap-cover path
- Probability: 49.5%
- Expected score: 2:0, 3:1
- Goal range: 2-4 total goals
- Tempo: medium
- Direction: 德国 win, leaning toward handicap cover
- Supporting evidence:
  - Final recommendation is `Germany -1.5`.
  - Favorite market probability is 63.3%.
  - Saved probability rows identify favorite cover and favorite dominance paths.
  - Correct-score and handicap assets can be mapped to the same cover script.
- Risk notes:
  - The scenario needs 德国 to win by at least 2 when the asset is a deep handicap.
  - Small-win and draw paths remain material risks.

## Secondary Scenario

- Name: 德国 wins but does not fully cover
- Probability: 20.3%
- Expected score: 1:0, 2:1
- Goal range: 1-3 total goals
- Tempo: low to medium
- Direction: 德国 win without enough margin for the main handicap
- Supporting evidence:
  - Saved path distribution includes a favorite one-goal-win bucket.
  - Risk-path notes identify favorite small win as a losing path for the deep handicap.
  - Moneyline-style assets can survive this scenario while handicap assets may fail.
- Risk notes:
  - This scenario should be labeled as insurance or secondary, not treated as the main return thesis.

## Upset Scenario

- Name: 科特迪瓦 resistance, draw, or unbeaten path
- Probability: 30.2%
- Expected score: 0:0, 1:1, 1:2
- Goal range: 0-3 total goals
- Tempo: low to unstable
- Direction: draw or 科特迪瓦 avoids defeat
- Supporting evidence:
  - Draw and underdog-unbeaten buckets are present in saved probability rows.
  - Upset index is 60 / 100.
  - Risk-path notes list draw and underdog win as losing paths for the main handicap.
- Risk notes:
  - This scenario should map to Tail Asset or explicit hedge logic only.

## Asset Mapping

| System asset | Market type | Scenario Engine role | Scenario served | Mapping note |
| --- | --- | --- | --- | --- |
| `Home -1.5` | `handicap` | Direction Asset + Return Asset | Main Scenario | Requires the favorite to cover the handicap path. |
| `Germany独赢` | `winner` | Direction Asset + Insurance Asset | Main + Secondary | Supports favorite direction and survives a narrow favorite win. |
| `波胆 2:0` | `correct_score` | Return Asset | Main Scenario | Core score path for the favorite cover scenario. |
| `波胆 3:0` | `correct_score` | Return Asset | Main Scenario | Core score path for the favorite cover scenario. |
| `波胆 3:1` | `correct_score` | Return Asset | Main Scenario | Core score path for the favorite cover scenario. |
| `波胆 4:0` | `correct_score` | Aggressive Return Asset / Tail Upside | Main Extreme Path | Supports a favorite blowout variant, but should be capped as upside rather than core evidence. |
| `波胆 4:1` | `correct_score` | Aggressive Return Asset / Tail Upside | Main Extreme Path | Supports a favorite blowout variant, but should be capped as upside rather than core evidence. |
| `波胆 4:2` | `correct_score` | Aggressive Return Asset / Tail Upside | Main Extreme Path | Supports a favorite blowout variant, but should be capped as upside rather than core evidence. |
| `波胆 5:0` | `correct_score` | Tail Asset / Extreme Upside | Upset / Extreme Upside | Covers a low-probability blowout tail and must not be core Main Scenario evidence. |
| `波胆 5:1` | `correct_score` | Tail Asset / Extreme Upside | Upset / Extreme Upside | Covers a low-probability blowout tail and must not be core Main Scenario evidence. |
| `波胆 5:2` | `correct_score` | Tail Asset / Extreme Upside | Upset / Extreme Upside | Covers a low-probability blowout tail and must not be core Main Scenario evidence. |
| `波胆 5:3` | `correct_score` | Tail Asset / Extreme Upside | Upset / Extreme Upside | Covers a low-probability blowout tail and must not be core Main Scenario evidence. |

## Scenario Consistency Score

- Score: 82 / 100
- Grade: Usable with warnings
- Summary: The recommendation is readable as a 德国 cover story, but high-score correct scores are treated as aggressive upside or tail exposure, not core Main Scenario evidence.

## Score Breakdown

| Component | Points | Reason |
| --- | ---: | --- |
| Scenario assignment coverage | 20 / 20 | Mapped available assets to Main, Secondary, or Upset scenarios. |
| Direction alignment | 20 / 20 | Winner and handicap assets support the favorite direction. |
| Tempo and score alignment | 14 / 20 | Core scores fit the cover path, while high-score tails should not be treated as core tempo evidence. |
| Role coherence | 10 / 15 | Core Return, Aggressive Return, and Tail assets are separated; many high-score assets reduce coherence. |
| Conflict penalty control | 8 / 15 | No Over3.5 primary conflict detected, but repeated high-score tails reduce confidence. |
| Evidence support | 10 / 10 | Saved probability, odds, decision, and risk-path data support the report. |

## Recommendation Auditor Handoff

- Check whether the main scenario is labeled as handicap cover, not simply favorite win.
- Check whether controlled low-score cover assets are separated from Over-based tempo stories.
- Check whether 4-goal and 5-goal correct scores remain capped as Aggressive Return or Tail assets.
- Check whether secondary small-win paths are treated as insurance, not contradiction.
- Check whether tail paths are labeled and prevented from silently driving the main recommendation.
- Check whether user portfolios receive the same scenario and consistency treatment.

## Portfolio Ranking Implication

- Future Portfolio Ranking can consume `Scenario Consistency Score`, role mapping, critical conflict count, and scenario coverage.
- EV, ROI, and Sharpe should remain value inputs, but they should not override critical scenario conflicts.
- A lower-EV portfolio with clearer scenario coverage may be preferable to a high-EV contradictory portfolio.
- Main recommendations should target a Scenario Consistency Score of at least 75.

## Automation Verdict

- Status: Pass
- The script generated this report from existing local data only.
- No data files were modified.
- No API refresh was performed.
- No Streamlit app was run.
- Output written: `SCENARIO_ENGINE_REPORT.md`
