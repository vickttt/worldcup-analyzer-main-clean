# Decision UI + Betting Logic Review Plan

Date: 2026-06-21

Scope: design only. This plan does not write code, modify `app.py`, change sorting, change recommendation logic, modify UI, modify data, create branches, commit, or push.

## 1. Product Problem

Hybrid v0.2 Visible Diagnostic added useful signals, but the page is still not a clean betting decision surface.

Current user-facing problems:

- The page explains many portfolio metrics but does not clearly answer whether the match is worth betting.
- Portfolio rows contain too many rank/value/risk signals without a unified interpretation layer.
- Multiple portfolios can show effectively identical betting content under different names.
- Detail dialogs interrupt scanning and repeat table information.
- Asset roles are not yet consistent enough for quick decision-making.

The next UI refactor should move from "analysis table" to "decision workflow".

## 2. Match Betting Score

## Goal

Add a single match-level betting value score:

```text
Match Betting Score: 0-100
```

This score answers:

```text
Is this match worth betting at all?
```

## Score Dimensions

| Dimension | Weight | Meaning |
| --- | ---: | --- |
| Market Odds Completeness | 15 | Whether winner, handicap, totals, and correct score markets are available and fresh. |
| Main Scenario Clarity | 20 | Whether the main match script is coherent and supported by market data. |
| Portfolio Consistency | 20 | Whether top portfolios serve the same scenario rather than conflicting paths. |
| Scenario / Hybrid Agreement | 15 | Whether Legacy, Scenario, and Hybrid signals broadly agree. |
| Max Loss Control | 15 | Whether downside is acceptable relative to recommended stake. |
| Risk Warning Severity | 15 | Whether there are critical conflicts, tail-heavy exposure, or low-confidence warnings. |

Conceptual formula:

```text
Match Betting Score =
  Odds Completeness
  + Scenario Clarity
  + Portfolio Consistency
  + Scenario/Hybrid Agreement
  + Max Loss Control
  - Risk Warning Penalty
```

## Score Bands

| Score | Output | Meaning |
| ---: | --- | --- |
| 80-100 | 值得投注 | Clear scenario, controlled risk, strong portfolio agreement. |
| 60-79 | 小注观察 | Some value exists, but uncertainty or conflict remains. |
| 0-59 | 不建议投注 | Low clarity, high conflict, poor data, or excessive downside. |

## Required Display

Use a Match Summary Card near the top of the analysis page:

```text
Match Betting Score: 74 / 100
Decision: 小注观察
Reason: 主剧本清晰，但 Hybrid 与 Legacy 存在分歧，建议控制仓位。
```

This should appear above Portfolio Ranking.

## 3. Recommended Stake

## Goal

Convert decision quality into a recommended total betting amount:

```text
Recommended Stake: 0-2000 元
```

This is match-level stake, not per-asset stake.

## Stake Bands

| Amount | Label | Meaning |
| ---: | --- | --- |
| 0 | 不建议投注 | No actionable betting edge. |
| 200-500 | 观察局 | Small stake only; data or scenario conflict remains. |
| 500-1000 | 普通可投 | Clear enough to participate, but not high confidence. |
| 1000-1500 | 高信心 | Strong scenario, good consistency, controlled downside. |
| 1500-2000 | 极高信心 | Rare; requires strong agreement and low risk. |

## Stake Inputs

Recommended Stake should combine:

- Match Betting Score
- Scenario Consistency Score
- Max Loss
- Hybrid v0.2 Sleeve Status
- Shadow Verdict
- User risk preference

## Conceptual Rule

```text
Base Stake = Match Betting Score mapped to 0-2000

Adjustments:
  + if Scenario Consistency >= 85
  + if Shadow Verdict = Agreement
  + if Sleeve Status = Scenario-Supported Aggressive Upside and capped
  - if Shadow Verdict = Disagreement
  - if Sleeve Status = Blocked Tail / Uncontrolled Tail
  - if Max Loss exceeds user risk limit
  - if market odds completeness is weak
```

## Risk Preference Multiplier

| User Risk Preference | Multiplier |
| --- | ---: |
| Conservative | 0.60 |
| Balanced | 1.00 |
| Aggressive | 1.25 |

Hard caps:

- `Shadow Verdict = Blocker Candidate`: max 300 元.
- `Sleeve Status = Blocked Tail`: max 500 元.
- Match Betting Score below 50: 0 元 unless user manually overrides.
- Any critical conflict: 0 元.

## Display

Use a Recommended Stake Card:

```text
Recommended Stake: 600 元
Risk Mode: Balanced
Reason: Match score is 68, scenario is acceptable, but Shadow Verdict is Watch.
```

## 4. Duplicate Portfolio Detection

## Goal

Prevent identical actual betting plans from appearing as separate portfolios.

Two portfolios should be treated as duplicates if their actual betting exposure is the same.

## Duplicate Identity Fields

Compare normalized items by:

- betting target
- direction
- market type
- handicap line / total line / score
- odds
- amount
- asset role

Normalized key example:

```text
type:handicap|selection:Home -1.5|odds:1.91|amount:500|role:Direction Asset
```

Portfolio identity:

```text
canonical_portfolio_id = hash(sorted(item_identity_keys))
```

## Duplicate Output Fields

Each strategy should carry:

```python
portfolio["duplicate"] = {
    "is_duplicate": true / false,
    "duplicate_of": "portfolio_id_or_name",
    "canonical_portfolio_id": "stable_hash"
}
```

## Display Rule

Default table:

- show only canonical portfolio
- hide exact duplicates
- optionally show caption:

```text
已合并 2 个投注内容完全相同的组合。
```

Details:

- show duplicate source names only if user expands "重复组合".

## 5. Detail UI Redesign

## Problem

Current detail dialogs interrupt workflow and repeat information already visible in the main table.

## New Pattern

Replace pop-up dialogs with expandable sections below the main table.

Each portfolio row gets:

```text
展开详情
```

Expanded detail includes:

- Portfolio summary
- Betting asset details
- Asset roles
- Why recommended / why downgraded
- Hybrid v0.2 Diagnostic
- Risk warnings

## Do Not Repeat Main Table Fields

Do not repeat:

- EV
- ROI
- Max Loss
- Score
- Scenario Rank
- Sleeve %
- Sleeve Status

These already belong in the table.

## Detail Sections

Recommended structure:

## A. Portfolio Summary

- What scenario it serves
- What the portfolio is trying to win from
- Whether it is core, sleeve, insurance, or tail-heavy

## B. Betting Assets

Columns:

- Asset
- Market
- Selection
- Amount
- Odds
- Asset Role

## C. Why This Portfolio

- Recommendation reason
- Downgrade reason if applicable
- Scenario alignment

## D. Hybrid v0.2 Diagnostic

- Core Portfolio
- Upside Sleeve
- Sleeve %
- Sleeve Status
- Sleeve Reason

## E. Risk Warning

- max loss path
- scenario conflict
- tail-heavy warning
- duplicate warning

## 6. Metric Glossary

Add a unified glossary section, preferably collapsed by default.

## Required Terms

| Metric | Explanation |
| --- | --- |
| EV | Expected profit estimate based on probability and odds. Positive EV means the market price may be favorable. |
| ROI | Expected return relative to stake. Useful for efficiency, but can exaggerate tail bets. |
| 最大亏损 | Worst-case loss if all assets in the portfolio fail. |
| 综合评分 | Current Legacy-style portfolio score. It remains the official table sorting signal unless explicitly changed. |
| 剧本一致性评分 | Measures whether assets serve the same match scenario. |
| Scenario Rank | Scenario-aware observational rank. It does not change official sorting. |
| Shadow Verdict | Agreement / Watch / Disagreement signal between Legacy and Scenario perspectives. |
| Sleeve % | Share allocated to controlled aggressive upside exposure. |
| Sleeve Status | Whether upside exposure is scenario-supported, small-watch, blocked, or uncontrolled. |
| Hybrid v0.2 | Observation-only diagnostic layer combining Core Portfolio and optional Upside Sleeve. |
| Core Portfolio | The scenario-disciplined base portfolio. |
| Upside Sleeve | Capped aggressive exposure used only when scenario support exists. |

## Display Rule

Glossary should not live inside every detail section.

Use one collapsed section:

```text
指标说明
```

## 7. Asset Role Classification

## Goal

Reclassify assets by decision role, not just market type.

## Asset Roles

| Role | Meaning | Examples |
| --- | --- | --- |
| Direction Asset | Establishes match direction. | Winner, favorite handicap. |
| Main Return Asset | Pays on the main scenario. | 2:0, 3:0, 3:1 if aligned. |
| Tempo Asset | Expresses match pace / goal volume. | Over/Under. |
| Correct Score Asset | Scoreline exposure, role depends on path. | 1:0, 2:1, 4:2. |
| Insurance Asset | Protects against secondary path. | Draw/underdog cover, lower-risk hedge. |
| Upside Sleeve | Capped scenario-supported aggressive upside. | 4:1, 4:2 when high-score path is supported. |
| Tail Asset | High-payout, low-frequency exposure. | 5:0, 5:1, 5:2. |
| Blocked Tail | Tail asset that conflicts or lacks support. | Correct-score cluster without scenario support. |
| My Portfolio Asset | User-entered asset, evaluated under same role rules. | Any manually entered bet. |

## Classification Rule

Role should be assigned after scenario detection.

Example:

- `4:1` is not automatically bad.
- It can be `Upside Sleeve` if high-score scenario is supported.
- It is `Tail Asset` if weakly supported.
- It is `Blocked Tail` if it conflicts with the main path.

## 8. UI Review

## Move Up

Move these above Portfolio Ranking:

- Match Betting Score
- Recommended Stake
- top risk warning
- whether match is 值得投注 / 小注观察 / 不建议投注

## Hide By Default

Hide these behind expanders:

- metric glossary
- full asset explanations
- duplicate portfolio details
- Hybrid v0.2 benchmark-style explanation
- raw role allocation details

## Keep In Main Table

Recommended default columns:

- 组合名称
- Scenario Rank
- Shadow Verdict
- Sleeve %
- Sleeve Status
- 主剧本
- EV
- ROI
- 最大亏损
- 剧本一致性评分
- 综合评分

If table remains too wide, hide:

- 主剧本
- 剧本一致性评分

and move them into details.

## Move To Details

- asset list
- asset roles
- why recommended
- why downgraded
- sleeve reason
- risk paths
- duplicate explanation

## Cards Needed

## Match Summary Card

Yes.

Purpose:

- summarize decision state before portfolio details
- show match-level recommendation

## Recommended Stake Card

Yes.

Purpose:

- answer how much to bet before showing portfolios

## Risk Warning Card

Yes.

Purpose:

- surface critical risk early
- prevent user from over-reading high EV / ROI

Recommended top layout:

```text
Match Summary Card
Recommended Stake Card
Risk Warning Card
Portfolio Ranking
Expandable Details
Metric Glossary
```

## 9. Implementation Priority

## Phase A: Match Betting Score + Recommended Stake Design

Scope:

- Add match-level decision card.
- Add recommended stake card.
- Use existing signals only.

Risk: MEDIUM

Reason:

- It changes user decision framing, even if it does not change ranking.

## Phase B: Duplicate Portfolio Detection

Scope:

- Generate canonical portfolio IDs.
- Mark exact duplicates.
- Hide duplicate rows by default.

Risk: MEDIUM-HIGH

Reason:

- Could accidentally hide a portfolio that differs in meaningful risk role if normalization is too aggressive.

## Phase C: Foldable Details Instead Of Dialogs

Scope:

- Replace modal detail workflow with expandable portfolio details.
- Avoid repeating main table fields.

Risk: MEDIUM

Reason:

- UI structure changes, but not betting logic.

## Phase D: Metric Glossary + Asset Role Unification

Scope:

- Add collapsed glossary.
- Standardize asset role naming.
- Apply role classification to system and My Portfolio assets.

Risk: MEDIUM

Reason:

- Low technical risk, but high product-language risk if labels are inconsistent.

## 10. Highest Priority Changes

Most worth implementing first:

1. Match Betting Score
2. Recommended Stake
3. Duplicate Portfolio Detection

Reason:

- These solve the core decision problem before further UI polishing.

## 11. Highest Risk Changes

Highest risk:

1. Duplicate Portfolio Detection
2. Recommended Stake
3. Asset Role Reclassification

Why:

- Duplicate detection can hide meaningful alternatives if the identity rule is too broad.
- Recommended stake can be mistaken as financial advice unless clearly framed as system sizing guidance.
- Asset role reclassification affects user trust if labels do not match visible betting logic.

## 12. Final Recommendation

Do not continue adding columns to Portfolio Ranking.

The next product step should be:

```text
Match Betting Score + Recommended Stake
```

Those two elements answer the user's actual decision:

```text
Should I bet this match, and how much?
```

