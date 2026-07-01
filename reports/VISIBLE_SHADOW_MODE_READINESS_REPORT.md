# Visible Shadow Mode v0.1 Implementation Readiness Report

Date: 2026-06-21

Scope: static implementation readiness check only. No code, UI, Ranking, recommendation logic, or data files were modified.

## Executive Verdict

Visible Shadow Mode v0.1 is partially ready.

The UI has clear insertion points for display-only Shadow fields, but the system does not yet have structured Shadow metadata inside strategy objects or snapshots.

Current readiness:

- UI insertion points: ready.
- Structured Shadow metadata: not ready.
- Markdown reports: available.
- Safe minimal display-only implementation: feasible after metadata is structured.

Recommended next implementation step:

```text
Create structured Shadow metadata first.
Then expose only Scenario Rank and Shadow Verdict in Portfolio Ranking.
```

## 1. Portfolio Ranking Data Structure

Current Portfolio Ranking row data is generated in:

- `app.py`
- `portfolio_ranking_rows(strategies, baseline=None)`

Current row fields:

- `组合名称`
- `主剧本`
- `让球资产`
- `大小球资产`
- `波胆资产`
- `EV`
- `ROI`
- `最大亏损`
- `剧本一致性评分`
- `综合评分`

Current display path:

```text
strategy_comparison(...)
  ↓
render_portfolio_ranking(...)
  ↓
portfolio_ranking_rows(...)
  ↓
st.dataframe(...)
```

Current production ranking order:

- `strategy_comparison(...)` sorts by existing `score`.
- `render_portfolio_ranking(...)` re-sorts comparison rows by existing `score`.
- `portfolio_ranking_rows(...)` only formats display rows.

Readiness:

- Adding display-only Shadow columns in `portfolio_ranking_rows(...)` is technically straightforward.
- It must not change the input `strategies` order.
- It must not change `score`.
- It must not change sort logic.

Risk: LOW if display-only and metadata already exists.

## 2. Current Shadow Metadata Availability

Checked fields:

- `scenario_rank`
- `scenario_score`
- `rank_difference`
- `shadow_verdict`
- `portfolio_ranking_shadow`

Result:

- These fields do not exist in `app.py` strategy objects.
- These fields do not appear as structured runtime fields in the current Portfolio Ranking flow.
- They currently exist only in Markdown design and validation reports.

Available Markdown reports:

- `PORTFOLIO_RANKING_SHADOW_REPORT.md`
- `SHADOW_VALIDATION_ROUND2.md`
- `SHADOW_VALIDATION_ROUND3.md`
- `SHADOW_BATCH_VALIDATION_PLAN.md`
- `VISIBLE_SHADOW_MODE_V0_1_PLAN.md`

Conclusion:

```text
Visible Shadow Mode cannot safely rely on structured app metadata yet.
```

Risk if implemented by parsing Markdown:

- MEDIUM to HIGH

Reason:

- Markdown reports are human-readable artifacts, not stable app data.
- Parsing report tables would be brittle.
- Report filenames are not match-keyed in the current UI flow.
- The app runtime does not know which Markdown report belongs to which match.
- Parsing Markdown inside UI would mix reporting artifacts with production rendering.

## 3. If No Structured Metadata Exists

Current fallback:

- Only Markdown reports contain Shadow Ranking output.

Readiness implication:

- The system can show Visible Shadow Mode only if one of these happens first:
  - Shadow metadata is attached to strategy objects in memory.
  - Shadow metadata is added to snapshot payload as structured data.
  - A read-only Shadow report generator creates structured JSON/CSV alongside Markdown.

Recommended structured shape:

```json
{
  "portfolio_ranking_shadow": {
    "mode": "shadow",
    "legacy_authoritative": true,
    "rows": [
      {
        "portfolio_name": "让球策略",
        "legacy_rank": 1,
        "legacy_score": 100,
        "scenario_rank": 4,
        "scenario_score": 61.9,
        "rank_difference": 3,
        "shadow_verdict": "Disagreement",
        "tail_exposure_warning": null,
        "scenario_consistency_score": 82
      }
    ]
  }
}
```

Minimum required metadata for v0.1:

- `scenario_rank`
- `shadow_verdict`

Recommended metadata for detail view:

- `scenario_score`
- `rank_difference`
- `tail_exposure_warning`
- `scenario_consistency_score`
- `scenario_rank_reason`

## 4. Affected Functions

### `portfolio_ranking_rows(...)`

Current role:

- Converts evaluated strategies into table rows.

Visible Shadow Mode impact:

- Add display-only columns:
  - `Scenario Rank`
  - `Shadow Verdict`
  - optionally `Rank Difference`

Risk:

- LOW if it only reads optional metadata.
- MEDIUM if it tries to parse Markdown reports.

Recommended boundary:

- Use `strategy.get("shadow")` or equivalent structured metadata.
- If missing, show `-`.
- Do not compute Shadow Rank here.
- Do not mutate `strategy`.

### `render_portfolio_ranking(...)`

Current role:

- Builds comparison list.
- Appends My Portfolio if present.
- Sorts by existing `score`.
- Selects shown rows.
- Displays table.
- Opens detail dialogs.

Visible Shadow Mode impact:

- Add one short caption explaining Shadow Mode.
- Pass strategies with optional Shadow metadata into row formatter.
- Keep existing sort unchanged.

Risk:

- MEDIUM

Reason:

- This function controls official ranking display and My Portfolio insertion.
- Any change to sort, slicing, or comparison list can affect user-visible behavior.

Recommended boundary:

- Do not change:
  - `comparison = sorted(... score ...)`
  - `shown = comparison[:6]`
  - My Portfolio inclusion logic
  - default recommendation logic

### `render_strategy_detail_dialog(...)`

Current role:

- Opens strategy detail dialog.
- Shows portfolio differences, bet contents, EV, ROI, max loss, and score.

Visible Shadow Mode impact:

- Add collapsed `Shadow Mode Details` section.
- Show:
  - Legacy Rank vs Scenario Rank
  - Scenario Score
  - Rank Difference
  - Shadow Verdict
  - upgrade/downgrade reason

Risk:

- LOW to MEDIUM

Reason:

- Detail-only additions are less likely to disrupt core ranking.
- Risk rises if the dialog starts recomputing Shadow scores.

Recommended boundary:

- Read optional metadata only.
- Default collapsed.
- No ranking or recommendation changes.

### `render_portfolio_detail_bundle(...)`

Current role:

- Renders asset-level detail rows from `portfolio_detail_rows(...)`.

Visible Shadow Mode impact:

- Optional future location for asset-level scenario labels.
- Not required for v0.1.

Risk:

- LOW if untouched.
- MEDIUM if adding asset-level Shadow labels now.

Recommended boundary:

- Do not modify for v0.1 unless structured asset-level metadata already exists.

## 5. Minimal Implementation Feasibility

### Can Portfolio Ranking table add Scenario Rank and Shadow Verdict only?

Answer:

- Yes, after structured metadata exists.

Minimum table addition:

- `Scenario Rank`
- `Shadow Verdict`

Optional third field:

- `Rank Difference`

Do not add by default in v0.1:

- full Scenario Score component breakdown
- full Tail Exposure details
- conflict flag table
- long reason text

Risk:

- LOW with structured metadata.
- MEDIUM/HIGH if derived by Markdown parsing.

### Can details be collapsed by default?

Answer:

- Yes.

Best location:

- inside `render_strategy_detail_dialog(...)`

Recommended display:

```text
Shadow Mode Details
Legacy Rank:
Scenario Rank:
Rank Difference:
Shadow Verdict:
Why changed:
```

Risk:

- LOW

### Can implementation avoid changing sorting and recommendation?

Answer:

- Yes.

Required constraints:

- Do not change `strategy_comparison(...)`.
- Do not change `strategy_score(...)`.
- Do not change `evaluate_allocation(...)`.
- Do not change `render_portfolio_ranking(...)` sorting line.
- Do not use `scenario_rank` for slicing, ranking, labels, or default recommendation.

Risk:

- LOW if these constraints are followed.

## 6. Readiness By Requirement

| Requirement | Current Status | Ready? | Risk |
| --- | --- | --- | --- |
| Portfolio Ranking data generation identified | `portfolio_ranking_rows(...)` | Yes | LOW |
| Portfolio Ranking display path identified | `render_portfolio_ranking(...)` | Yes | LOW |
| Detail dialog path identified | `render_strategy_detail_dialog(...)` | Yes | LOW |
| Asset detail path identified | `render_portfolio_detail_bundle(...)` | Yes | LOW |
| Structured Scenario Rank exists | Not found | No | MEDIUM |
| Structured Scenario Score exists | Not found | No | MEDIUM |
| Structured Rank Difference exists | Not found | No | MEDIUM |
| Structured Shadow Verdict exists | Not found | No | MEDIUM |
| Markdown reports exist | Yes | Partial | MEDIUM/HIGH if parsed |
| Minimal table-only visible mode possible | Yes, after metadata | Partial | LOW/MEDIUM |
| No sorting change required | Yes | Yes | LOW |
| No recommendation change required | Yes | Yes | LOW |

## 7. Risk Ratings

### LOW Risk

- Add optional table columns from already-structured metadata.
- Add a static caption saying Legacy Ranking remains official.
- Add collapsed Shadow detail section in dialog.
- Show `-` when Shadow metadata is missing.

### MEDIUM Risk

- Add metadata calculation in app runtime.
- Attach Shadow metadata to strategies before display.
- Add `portfolio_ranking_shadow` to snapshot payload.
- Include My Portfolio in Shadow comparison.

### HIGH Risk

- Parse Markdown reports inside the app UI.
- Change sorting from `score` to `scenario_rank`.
- Use Shadow Verdict to hide or block portfolios.
- Change `strategy_score(...)`.
- Change `evaluate_allocation(...)`.
- Change `strategy_comparison(...)`.
- Make Scenario Rank drive default recommendation.

## 8. Recommended Next Step

Do not implement visible UI directly from Markdown reports.

Recommended next step:

```text
Design or implement structured Shadow metadata generation before UI display.
```

Minimum structured field target:

```text
strategy["shadow"] = {
  "scenario_rank": ...,
  "scenario_score": ...,
  "rank_difference": ...,
  "shadow_verdict": ...
}
```

Then Visible Shadow Mode v0.1 can safely:

- add `Scenario Rank`
- add `Shadow Verdict`
- keep details collapsed
- keep Legacy Ranking order unchanged
- keep default recommendation unchanged

## Final Readiness Decision

Visible Shadow Mode v0.1 is not ready for UI implementation until structured Shadow metadata exists.

It is ready for a metadata-first implementation step.

Once metadata exists, a minimal UI display is LOW risk if it only reads optional fields and keeps all production ranking behavior unchanged.
