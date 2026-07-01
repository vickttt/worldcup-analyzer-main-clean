# Visible Shadow Mode v0.1 Plan

Date: 2026-06-21

Scope: design only. This plan does not write code, modify UI, change business logic, change Ranking, alter recommendation logic, modify data files, create branches, commit, or push.

## Goal

Make Shadow Mode visible as auxiliary information inside Portfolio Ranking without changing production behavior.

Visible Shadow Mode v0.1 should help the user notice when Legacy Ranking and Scenario Ranking disagree, while keeping Legacy Ranking as the only official ranking.

## Background

Shadow Mode has completed three validation rounds:

| Round | Match Type | Match | Legacy Top | Scenario Top | Verdict |
| --- | --- | --- | --- | --- | --- |
| Round 1 | Strong favorite / handicap-cover | Germany vs Ivory Coast | 让球策略 | 赔率分布优化器 | Disagreement |
| Round 2 | Balanced match | Scotland vs Morocco | 独赢 + 波胆 | 独赢策略 | Watch |
| Round 3 | Cold-risk / crowded favorite | Brazil vs Haiti | 大小球策略 | 当前推荐组合 | Disagreement |

Common result:

```text
Legacy Rank 1 != Scenario Rank 1
```

Conclusion:

- Scenario Ranking provides useful decision context.
- Scenario Ranking is not yet validated enough to replace Legacy Ranking.
- The UI should expose Shadow signals carefully and non-authoritatively.

## Non-Negotiable Principles

Visible Shadow Mode v0.1 must not:

- change Legacy Ranking sort order
- change default recommendation
- change `strategy_score(...)`
- change `evaluate_allocation(...)`
- change `strategy_comparison(...)`
- change recommendation logic
- change data files
- make Scenario Rank look like the official ranking

Visible Shadow Mode v0.1 may:

- show Scenario Rank as auxiliary metadata
- show Shadow Verdict
- show rank movement
- show Tail Exposure warnings
- explain why a portfolio was upgraded or downgraded by Scenario Ranking

## 1. Portfolio Ranking Table Fields

The Portfolio Ranking table should keep Legacy Ranking as the main ordering.

Recommended visible columns:

| Column | Purpose | Default Visibility |
| --- | --- | --- |
| Legacy Rank | Existing official rank. | Visible |
| Portfolio Name | Existing portfolio label. | Visible |
| Legacy Score | Existing score. | Visible |
| Scenario Rank | Shadow rank. | Visible |
| Rank Difference | Movement between Legacy and Scenario ranks. | Visible |
| Shadow Verdict | Agreement / Watch / Disagreement. | Visible |
| Scenario Score | Shadow score. | Collapsed by default or secondary |
| Scenario Consistency Score | Scenario alignment, 0-100. | Collapsed by default |
| Tail Exposure Warning | Warns if tail exposure is high. | Visible only when warning exists |

### Minimal First-Screen Columns

To avoid table clutter, the first visible version should show only:

- Scenario Rank
- Rank Difference
- Shadow Verdict

Scenario Score and Scenario Consistency Score should be available in an expanded view or detail dialog.

### Rank Difference Display

Suggested formatting:

| Rank Difference | Meaning | Display |
| ---: | --- | --- |
| 0 | no movement | Stable |
| +1 or +2 | Scenario downgrades slightly | Downgraded by 1 / 2 |
| +3 or more | Scenario downgrades materially | Scenario Warning |
| -1 or -2 | Scenario upgrades slightly | Upgraded by 1 / 2 |
| -3 or less | Scenario upgrades materially | Scenario Candidate |

Important:

- Positive means Scenario Ranking downgrades the portfolio.
- Negative means Scenario Ranking upgrades the portfolio.

### Shadow Verdict Display

| Verdict | Meaning | Suggested UI Tone |
| --- | --- | --- |
| Agreement | Legacy and Scenario broadly agree. | neutral |
| Watch | Scenario Ranking sees a meaningful but not severe difference. | caution |
| Disagreement | Scenario Ranking materially disagrees. | warning |
| Blocker Candidate | Scenario Ranking sees critical risk, but does not block yet. | strong warning |

## 2. Detail Dialog Additions

Each Portfolio detail dialog should add a collapsed section:

```text
Shadow Mode Details
```

Default state:

- collapsed

Expanded state should show:

### Legacy vs Scenario

Fields:

- Legacy Rank
- Legacy Score
- Scenario Rank
- Scenario Score
- Rank Difference
- Shadow Verdict

Purpose:

- Make it clear that the user is seeing two ranking perspectives.
- Avoid implying Scenario Rank is official.

### Why Upgraded / Downgraded

The detail dialog should explain the movement in plain language.

Examples:

Round 1 style:

```text
Scenario Ranking downgraded this portfolio because it is directionally clear but too narrow compared with more role-balanced portfolios.
```

Round 2 style:

```text
Scenario Ranking slightly downgraded this portfolio because it is score-specific in a balanced match where simpler winner exposure is more robust.
```

Round 3 style:

```text
Scenario Ranking downgraded this portfolio because it is a pure tempo asset and does not fully express the final match direction.
```

### Tail Exposure

Fields:

- Tail Exposure percentage or label
- Tail-heavy warning
- Tail asset list, if available

Suggested labels:

| Tail Exposure | Label |
| ---: | --- |
| 0-15% | Normal |
| >15-20% | Watch |
| >20-35% | Tail-heavy |
| >35% | Not default-eligible in future Ranking 2.0 |

### Scenario Consistency

Fields:

- Scenario Consistency Score
- Main Scenario Coverage
- Secondary Insurance Coverage
- Conflict Flags

Suggested labels:

| Scenario Consistency Score | Label |
| ---: | --- |
| 85-100 | Strong |
| 75-84 | Usable |
| 60-74 | Warning |
| below 60 | Weak |

## 3. Risk Prompt Text

Visible Shadow Mode must show short risk prompts wherever Scenario Rank appears.

### Table-Level Prompt

Suggested copy:

```text
Legacy 排名仍为正式排序。Scenario Rank 仅供观察，不影响推荐结果。
```

### Detail Dialog Prompt

Suggested copy:

```text
Shadow Mode 展示的是旁路评估结果。它不会改变当前推荐、排序或下注建议。
```

### Disagreement Prompt

Suggested copy:

```text
Scenario Ranking 与 Legacy Ranking 存在差异。请查看原因，但当前正式排序仍以 Legacy Ranking 为准。
```

### Tail Exposure Prompt

Suggested copy:

```text
该组合包含较高 Tail Exposure。它可能更依赖低概率路径，不应被视为稳健主推荐。
```

### Scenario Consistency Prompt

Suggested copy:

```text
Scenario Consistency Score 衡量组合是否服务同一个比赛剧本，而不是单独看 EV / ROI / Sharpe。
```

## 4. UI Display Principles

### Keep The Core Page Clean

Portfolio Ranking table should not become a metrics dump.

Core page should show at most:

- Scenario Rank
- Shadow Verdict

Rank Difference can be shown as compact movement text or a small badge.

### Default Advanced Details Collapsed

Collapsed by default:

- Scenario Score
- Scenario Consistency Score breakdown
- Tail Exposure details
- conflict flags
- reason text
- score component details

Expanded only when the user opens a detail row or dialog.

### Use One Primary Warning At A Time

If a portfolio has multiple Shadow warnings, show only the highest-signal warning in the table.

Priority:

1. Critical / High conflict
2. Disagreement
3. Tail-heavy
4. Low Scenario Consistency
5. Large rank movement

### Do Not Reorder

Even if Scenario Rank is 1, the row should stay in its Legacy Rank position.

The table should visually communicate:

```text
This row is Legacy Rank X, Scenario Rank Y.
```

Not:

```text
This row should replace the official rank.
```

## 5. Implementation Boundary

Visible Shadow Mode v0.1 must be display-only.

Allowed future implementation:

- add auxiliary columns to Portfolio Ranking table
- add collapsed Shadow Mode details in strategy dialog
- add short risk prompt text
- read existing Shadow Mode metadata or report-derived fields

Not allowed:

- changing production sort order
- changing default recommendation
- changing `strategy_score(...)`
- changing `evaluate_allocation(...)`
- changing `strategy_comparison(...)`
- changing optimizer behavior
- changing recommendation logic
- changing snapshot data files
- hiding portfolios based on Scenario Rank
- making Scenario Rank the default recommendation driver

## 6. Suggested UI States

### Agreement

Table display:

```text
Scenario Rank: same
Shadow Verdict: Agreement
```

Detail summary:

```text
Legacy and Scenario Ranking broadly agree.
```

### Watch

Table display:

```text
Scenario Rank: 3
Shadow Verdict: Watch
```

Detail summary:

```text
Scenario Ranking sees a meaningful difference, but no critical conflict.
```

### Disagreement

Table display:

```text
Scenario Rank: 5
Shadow Verdict: Disagreement
```

Detail summary:

```text
Scenario Ranking materially disagrees with Legacy Ranking. Legacy Ranking remains official.
```

### Tail-Heavy

Table display:

```text
Tail Warning
```

Detail summary:

```text
This portfolio has elevated Tail Exposure and may depend on low-probability paths.
```

## 7. Acceptance Criteria

Visible Shadow Mode v0.1 is acceptable when:

- Legacy Ranking order remains unchanged.
- Default recommendation remains unchanged.
- Scenario Rank appears only as auxiliary information.
- The table adds no more than 1-2 high-signal Shadow indicators by default.
- Advanced Shadow details are collapsed by default.
- Every Shadow display includes clear non-authoritative wording.
- Tail-heavy and Disagreement cases are visible but do not block portfolios.
- No business logic or scoring formula changes are required.

## Final Recommendation

Proceed with Visible Shadow Mode only after Shadow metadata is reliably available.

The first visible version should be conservative:

1. Add Scenario Rank.
2. Add Shadow Verdict.
3. Keep details collapsed.
4. Add clear wording that Legacy Ranking remains official.
5. Do not show Scenario Score as a headline metric until users can understand why it differs.
