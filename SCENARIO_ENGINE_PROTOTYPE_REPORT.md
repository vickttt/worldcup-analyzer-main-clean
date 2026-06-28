# Scenario Engine Prototype Report v0.1

## Match

- Match: Germany vs Ivory Coast
- Competition: World Cup 2026, Group E
- Venue: Toronto Stadium, Toronto, Canada
- Kickoff: 2026-06-20 16:00 UTC
- Data used: existing local snapshots only
- Primary files:
  - `data/history/2026_06_20_Germany_Ivory_Coast_pre.json`
  - `data/worldcup2026/2026_06_20_Germany_Ivory_Coast/pre_match.json`
  - `data/worldcup2026/2026_06_20_Germany_Ivory_Coast/odds.json`
  - `data/worldcup2026/2026_06_20_Germany_Ivory_Coast/fixture.json`
- Prototype status: design validation report, not code execution.

## Source Snapshot Summary

- System final recommendation: `Germany -1.5`
- Final confidence score: 92 / 100
- Value rating: A
- Participation advice: 强烈参与
- Recommended stake: 1800
- Germany market probability: 63.6%
- Polymarket Germany probability: 64.5%
- Market disagreement: low, about +1.0 percentage point on Germany
- Upset index: 60 / 100, marked as medium upset risk
- Main handicap: `Home -1.5`
- Main total: 2.5, market slightly favors Over
- Top path distribution from existing snapshot:
  - Germany small win by 1: 26.7%
  - Germany win by 2: 23.3%
  - Draw zone: 20.7%
  - Germany win by 3+: 20.5%
  - Ivory Coast unbeaten: 8.8%

## Main Scenario

- Name: Germany controlled win, handicap boundary path
- Probability: 43.8%
- Expected score: 2:0, 3:1
- Goal range: 2-4 total goals
- Tempo: medium
- Direction: Germany win, with the portfolio leaning toward Germany covering `-1.5`
- Supporting evidence:
  - Current system recommendation is `Germany -1.5`.
  - Direction confidence is 92 / 100.
  - Market winner probability has Germany around 63.6%.
  - Polymarket also supports Germany around 64.5%.
  - Asian handicap main line is `Home -1.5`, aligned with Germany direction.
  - Value rating is A, driven by handicap consistency, Asian handicap structure, correct score structure, and normal market margin.
  - Correct score assets `2:0` and `3:1` both support Germany winning by 2.
- Risk notes:
  - The highest single path in the distribution is Germany small win by 1, which loses `Germany -1.5`.
  - Draw zone is material at 20.7%.
  - Upset index is medium at 60 / 100.
  - The Main Scenario is not simply “Germany wins”; it specifically needs Germany to win by at least 2 for the main handicap asset.

## Secondary Scenario

- Name: Germany wins but does not cover deep handicap
- Probability: 26.7%
- Expected score: 1:0, 2:1
- Goal range: 1-3 total goals
- Tempo: low to medium
- Direction: Germany win, but not enough margin for `Home -1.5`
- Supporting evidence:
  - Existing probability distribution marks “Germany small win by 1” as the highest individual path at 26.7%.
  - Risk exposure for Germany `-1.5` explicitly lists “Germany only wins by 1” as a losing path.
  - Non-recommended correct scores `1:0` and `2:1` are directionally Germany-aligned but fail to cover `Home -1.5`.
  - Germany moneyline functions as a softer direction asset that still survives this scenario.
- Risk notes:
  - This scenario protects the broad Germany direction but conflicts with the main handicap return thesis.
  - If this scenario is treated as primary, `Germany -1.5` should not be the main recommendation.
  - Scenario Engine should force the UI to label this as a secondary or insurance path.

## Upset Scenario

- Name: Ivory Coast resistance, draw or unbeaten path
- Probability: 29.5%
- Expected score: 0:0, 1:1, 1:2
- Goal range: 0-3 total goals
- Tempo: low to unstable
- Direction: Draw or Ivory Coast avoids defeat
- Supporting evidence:
  - Draw zone is 20.7%.
  - Ivory Coast unbeaten path is 8.8%.
  - System upset index is 60 / 100, meaning medium upset risk.
  - Risk exposure for Germany `-1.5` lists draw and Ivory Coast win as losing paths.
  - Correct score candidates such as `1:1`, `0:0`, `1:2`, and `0:1` exist in the snapshot but are not recommended because they conflict with the main Germany direction.
- Risk notes:
  - This scenario should only support Tail Asset or explicit hedge logic.
  - It must not be mixed into the main recommendation without a hedge label.
  - Current recommended portfolio has limited direct tail protection, so this remains a named risk rather than a covered path.

## Asset Mapping

| Current system asset | Existing role signal | Scenario Engine role | Scenario served | Mapping verdict |
| --- | --- | --- | --- | --- |
| `Home -1.5` / `Germany -1.5` | 方向增强资产 / final recommendation | Direction Asset + Return Asset | Main Scenario | Strong alignment with Germany cover path; fails if Secondary Scenario occurs. |
| `Germany独赢` | 主方向资产 / insurance-heavy portfolio component | Direction Asset + Insurance Asset | Main + Secondary | Supports Germany direction and protects against Germany one-goal win, but not draw/upset. |
| `大于 2.5 球` | 节奏资产, not recommended in one snapshot | Tempo Asset | Main Scenario only when paired with 3:0 or 3:1 | Usable tempo signal, but should not be silently paired with 2:0 as a primary driver. |
| `小于 2.5 球` | 节奏资产, not recommended | Insurance Asset / Tempo hedge | Secondary Scenario | Could support 1:0 or 2:0 control paths, but current system does not use it as a main asset. |
| `波胆 2:0` | 收益放大资产 | Return Asset | Main boundary path | Supports `Home -1.5` and Germany win by 2, but conflicts with Over2.5 tempo. Needs explicit “controlled 2-goal win” label. |
| `波胆 3:1` | 收益放大资产 | Return Asset | Main boundary path | Strong Main Scenario fit: Germany by 2 and Over2.5 compatible. |
| `波胆 3:0` | 收益放大资产 | Return Asset | Main / dominance path | Supports Germany cover and Over2.5. Slightly more aggressive than 2:0. |
| `波胆 4:0`, `4:1`, `4:2` | 边缘路径 / 收益放大资产 | Tail Asset or aggressive Return Asset | Main extreme path | Should be labeled as Tail or aggressive upside, not core proof of Main Scenario. |
| `波胆 1:0`, `2:1` | not recommended due path conflict | Insurance Asset candidate | Secondary Scenario | Correctly excluded from main path because they do not cover `Home -1.5`; useful as explicit secondary protection only. |
| `波胆 1:1`, `0:0`, `1:2`, `0:1` | not recommended due path conflict | Tail Asset | Upset Scenario | Correctly excluded from main recommendation; should remain upset/hedge only. |

## Scenario Consistency Score

- Score: 82 / 100
- Grade: Usable, audit-ready with warnings

## Score Breakdown

| Component | Points | Reason |
| --- | ---: | --- |
| Scenario assignment coverage | 18 / 20 | Most assets can be mapped to Main, Secondary, or Upset. Some high-score correct score assets need clearer Tail labels. |
| Direction alignment | 20 / 20 | Primary recommended assets overwhelmingly support Germany direction. |
| Tempo and score alignment | 14 / 20 | `3:1` and `3:0` align with Over2.5, while `2:0` supports the handicap but conflicts with an Over2.5 tempo thesis. |
| Role coherence | 12 / 15 | Direction and Return roles are clear. Insurance and Tail roles are present as risks but not fully represented in the selected portfolio. |
| Conflict penalty control | 11 / 15 | The system excludes `1:0`/`2:1` from main recommendation, but still mixes `2:0` with an Over2.5-friendly path narrative. No Over3.5 conflict appears. |
| Evidence support | 7 / 10 | Market and snapshot evidence are strong, but data confidence is limited by using static local snapshots and no live refresh. |

## Consistency Findings

- The prototype validates that Scenario Engine can be applied to current saved data.
- The main recommendation is scenario-readable: Germany direction, mostly Germany cover path.
- The biggest design issue is not an Over3.5 versus 1:0 conflict. It is the tension between the highest probability path, Germany small win by 1, and the actual main recommendation, Germany `-1.5`.
- `2:0` is acceptable as a Main Scenario Return Asset if the scenario is “controlled Germany cover,” but it should not be justified through an Over2.5 tempo story.
- `Germany独赢` should be labeled as Direction/Insurance because it survives the Secondary Scenario while `Germany -1.5` does not.
- Edge correct scores such as `4:0`, `4:1`, `5:0`, and `5:1` should be Tail or aggressive-upside assets, not core recommendation evidence.

## Recommendation Auditor Handoff

Recommendation Auditor should check:

- Whether Main Scenario is correctly labeled as Germany cover, not just Germany win.
- Whether `Germany -1.5` is allowed to outrank safer Germany win paths despite the small-win path being the highest single probability bucket.
- Whether `2:0` is presented as controlled-cover Return Asset instead of an Over2.5-compatible asset.
- Whether high-score correct scores are labeled Tail/aggressive rather than core.
- Whether user portfolio scoring uses the same scenario labels and consistency scoring.

## Portfolio Ranking Implication

Future Portfolio Ranking should not rank by EV/ROI/Sharpe alone.

For this match:

- `Germany -1.5` has strong strategic value but depends on the boundary/cover path.
- `Germany独赢` has lower payout but covers Main and Secondary Germany-win scenarios.
- Correct score returns add upside but should be capped by Scenario Consistency Score.
- A lower-EV but clearer scenario portfolio may be preferable if user decision efficiency is the priority.

Recommended future ranking inputs:

- EV
- ROI
- Sharpe
- Scenario Consistency Score
- Main Scenario coverage
- Secondary Scenario insurance value
- Tail exposure clarity
- User decision complexity penalty

## Prototype Verdict

- Scenario Engine design is executable on current saved data.
- The report can identify Main, Secondary, and Upset scenarios without new code.
- Asset mapping is feasible using existing portfolio, role, odds, and path consistency fields.
- Scenario Consistency Score is meaningful and exposes a real product issue: current recommendation logic can favor a handicap cover path even when the highest individual probability bucket is a one-goal win.
- Next step should be read-only automation that generates this report from saved snapshots before any recommendation logic rewrite.

