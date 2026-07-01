# Hybrid v0.2 Visible Diagnostic Plan

Date: 2026-06-21

Scope: design only. This plan does not write code, modify UI, change sorting, change default recommendations, change recommendation logic, modify `strategy_score(...)`, modify `evaluate_allocation(...)`, modify `strategy_comparison(...)`, modify data files, create branches, commit, or push.

## 1. Goal

Expose Hybrid v0.2 diagnostics in the user experience without changing the official Portfolio Ranking order.

The user should be able to see:

- which portfolio is the Core Portfolio
- whether an Upside Sleeve is allowed
- how large the sleeve is
- why the sleeve is allowed or restricted
- how the structure differs from Legacy Tail-Heavy

This is observation-only.

## 2. Non-Negotiable Boundaries

Do not change:

- production sorting
- default recommendation
- recommendation logic
- `strategy_score(...)`
- `evaluate_allocation(...)`
- `strategy_comparison(...)`
- score calculation
- data files

Visible Diagnostic only displays metadata that has already been calculated in report-only or runtime diagnostic layers.

## 3. Portfolio Ranking Page

## Should The Main Table Display Hybrid v0.2 Fields?

Yes, but only a minimal set.

The main Portfolio Ranking table should display at most four Hybrid v0.2 diagnostic fields:

| Field | Default Display | Reason |
| --- | --- | --- |
| Core Rank | Yes | Shows which portfolio is scenario-core aligned. |
| Core + Upside Rank | Optional / advanced | Useful, but can clutter the main table. |
| Sleeve % | Yes | Small numeric signal that shows how much aggressive upside exists. |
| Sleeve Status | Yes | Most important risk label. |

Recommended MVP table columns:

```text
组合名称
Scenario Rank
Shadow Verdict
Sleeve %
Sleeve Status
主剧本
EV
ROI
最大亏损
剧本一致性评分
综合评分
```

Do not add these to the default table yet:

- Core + Upside ROI
- Legacy Tail-Heavy ROI
- Sleeve Reason
- Guardrail Status detail
- Core + Upside Score
- Full benchmark metrics

Those belong in details or an advanced section.

## 4. Default vs Collapsed Information

## Default Visible

Keep default visible information limited to:

- `Sleeve %`
- `Sleeve Status`
- one warning caption

Suggested main table caption:

```text
Hybrid v0.2 仅为观察，不影响正式排序、默认推荐或评分。
```

If space allows, include:

```text
Sleeve 代表受限的进攻上行暴露，不等于默认推荐。
```

## Collapsed / Advanced

Place these in an expander or detail dialog:

- Core Portfolio
- Upside Sleeve
- Core + Upside Portfolio
- Legacy Tail-Heavy Portfolio
- Sleeve Reason
- Guardrail Status
- Core ROI
- Core + Upside ROI
- Legacy Tail-Heavy ROI
- Max Drawdown comparison

Reason:

- The Portfolio Ranking table is already the main decision surface.
- The user needs the warning signal first, not the whole benchmark matrix.
- Full structure comparison is valuable only after the user chooses to inspect a portfolio.

## 5. How To Avoid Table Complexity

Use three rules:

1. Do not add more than two new default columns beyond current Shadow MVP.
2. Never show raw benchmark metrics in the default table.
3. Move explanations into the detail dialog.

Recommended default columns to add:

```text
Sleeve %
Sleeve Status
```

Do not add:

```text
Core + Upside ROI
Legacy Tail ROI
Core + Upside Max Drawdown
Sleeve Reason
Guardrail Reason
```

If the table becomes too wide, hide `Core + Upside Rank` and show it only in details.

## 6. Required User-Facing Copy

Main warning copy:

```text
Hybrid v0.2 仅为观察，不影响正式排序、默认推荐或评分。
```

Sleeve explanation:

```text
Upside Sleeve 是受限的进攻上行暴露，用于观察高比分/深盘路径，不代表主推荐。
```

Blocked tail explanation:

```text
Blocked Tail 表示该组合过度依赖尾部路径，不能作为默认推荐。
```

Allowed sleeve explanation:

```text
Allowed Sleeve 表示该上行暴露有剧本支持，但仍只作为观察信号。
```

Legacy comparison copy:

```text
Legacy Tail-Heavy 可能捕捉更高收益，但回撤显著更大。
```

## 7. Detail Dialog Design

The detail dialog should have a dedicated section:

```text
Hybrid v0.2 Diagnostic
```

Recommended layout:

## A. Core Portfolio

Show:

- Core portfolio name
- Core rank / Scenario Rank
- Why it is the Core
- Main scenario it serves
- Core ROI if historical/report-only context is available

## B. Upside Sleeve

Show:

- Sleeve asset / sleeve portfolio name
- Sleeve %
- Sleeve Status
- Sleeve Reason
- Whether it is:
  - `Scenario-Supported Aggressive Upside`
  - `Watch: Small Upside Sleeve`
  - `Uncontrolled Tail`
  - `Blocked Tail`

## C. Core + Upside

Show:

- Combined structure
- How sleeve changes risk/reward
- Whether it improves expected upside
- Whether drawdown remains controlled

## D. Legacy Tail-Heavy Comparison

Show:

- Legacy Tail-Heavy portfolio name
- Why it is not the same as Core + Upside
- Whether Legacy has higher upside but worse max drawdown
- Why Legacy Tail-Heavy remains observation-only

## E. Decision Boundary

Show:

```text
本阶段只显示诊断信息，不改变排序、不改变推荐、不改变评分。
```

## 8. Sleeve Status Display Rules

Recommended status labels:

| Status | Display | Severity |
| --- | --- | --- |
| Scenario-Supported Aggressive Upside | 剧本支持上行 | Info |
| Watch: Small Upside Sleeve | 小仓观察 | Low |
| Uncontrolled Tail | 无控制尾部 | High |
| Blocked Tail | 尾部阻断 | High |
| No Sleeve | 无上行袖仓 | Neutral |

Use restrained visual treatment:

- Info: neutral badge
- Low: muted badge
- High: warning badge
- Neutral: plain text

Do not use this status to sort rows.

## 9. Data / Metadata Expectations

Visible Diagnostic needs these fields from report-only or runtime diagnostic metadata:

```python
strategy["hybrid_v2"] = {
    "core_rank": int,
    "core_portfolio": str,
    "upside_sleeve": str,
    "core_upside_rank": int | None,
    "sleeve_share": float,
    "sleeve_status": str,
    "sleeve_reason": str,
    "guardrail_status": str,
    "legacy_tail_heavy_portfolio": str,
}
```

Minimum display-safe fields:

```python
strategy["hybrid_v2"]["sleeve_share"]
strategy["hybrid_v2"]["sleeve_status"]
```

If metadata is missing:

```text
Sleeve % = "-"
Sleeve Status = "-"
```

Missing metadata must not break the Portfolio Ranking table.

## 10. Function Impact For Future Implementation

Expected future UI touch points:

| Function | Change Type | Risk |
| --- | --- | --- |
| `portfolio_ranking_rows(...)` | Add display-only columns for Sleeve % and Sleeve Status | LOW |
| `render_portfolio_ranking(...)` | Ensure diagnostic metadata exists before table render | MEDIUM |
| `render_strategy_detail_dialog(...)` | Add Hybrid v0.2 Diagnostic section | MEDIUM |
| `render_portfolio_detail_bundle(...)` | Optional shared detail formatting | MEDIUM |

Do not touch:

- `strategy_score(...)`
- `evaluate_allocation(...)`
- `strategy_comparison(...)` sorting logic

## 11. Risk Rating

Overall risk: `MEDIUM`

Why not LOW:

- The table is already a decision surface, so extra columns can degrade usability.
- Diagnostic metadata can be misunderstood as a recommendation change.
- Detail dialog content can become too dense.

Why not HIGH:

- No sorting change.
- No recommendation change.
- No scoring change.
- Missing metadata can degrade to `-`.

## 12. Recommended MVP Scope

Implement only:

- table caption
- `Sleeve %`
- `Sleeve Status`
- detail dialog Hybrid v0.2 Diagnostic section

Do not implement:

- Core + Upside sorting
- Core + Upside recommendation eligibility
- automatic default recommendation changes
- visible ROI benchmark columns in the main table

## 13. Exit Criteria

Visible Diagnostic is successful if:

- users can identify whether upside is controlled or uncontrolled
- the Portfolio Ranking table remains scannable
- no user interprets Hybrid v0.2 as the official ranking
- the detail dialog explains why sleeve is allowed or restricted
- production ranking remains unchanged

## 14. Final Recommendation

Proceed to a small Visible Diagnostic MVP only after commit hygiene is cleaned up.

The first visible version should show:

```text
Sleeve %
Sleeve Status
```

Everything else should remain inside detail or advanced views.

