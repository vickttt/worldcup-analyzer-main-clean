# Shadow Metadata v1

Date: 2026-06-21

Scope: metadata structure design only. This document does not write code, modify UI, change sorting, change recommendation logic, modify Ranking formulas, alter data files, create branches, commit, or push.

## Goal

Define structured Shadow Metadata so Visible Shadow Mode can read Scenario Ranking information without parsing Markdown reports.

Primary target:

```python
strategy["shadow"]
```

This metadata must be observational only. It must not change Legacy Ranking, default recommendation, sorting, `strategy_score(...)`, `evaluate_allocation(...)`, or `strategy_comparison(...)` production behavior.

## 1. Why Shadow Metadata Is Needed

Visible Shadow Mode Readiness confirmed:

- `scenario_rank`
- `scenario_score`
- `rank_difference`
- `shadow_verdict`

currently exist only in Markdown reports.

Markdown is not a stable runtime data source.

Therefore, Visible Shadow Mode should read structured metadata attached to each strategy instead of parsing report text.

## 2. Strategy-Level Structure

Recommended strategy-level field:

```python
strategy["shadow"] = {
    "enabled": True,
    "mode": "shadow",
    "legacy_authoritative": True,
    "legacy_rank": 1,
    "legacy_score": 100,
    "scenario_rank": 4,
    "scenario_score": 61.9,
    "rank_difference": 3,
    "rank_shift_label": "Major Downgrade",
    "shadow_verdict": "Disagreement",
    "scenario_rank_reason": "Direction is clear, but role balance is narrow.",
    "scenario_consistency_score": 82,
    "tail_exposure": 0.124,
    "tail_exposure_warning": None,
    "asset_role_balance_score": 68,
    "main_scenario_coverage": 0.78,
    "secondary_insurance_coverage": 0.32,
    "conflict_flags": [],
    "audit_status": "Pass",
    "audit_severity": "None",
    "data_confidence": "medium"
}
```

## 3. Required Fields For v1

These fields are required for Visible Shadow Mode v0.1:

| Field | Type | Meaning |
| --- | --- | --- |
| `enabled` | boolean | Whether Shadow metadata is available. |
| `mode` | string | Always `shadow`. |
| `legacy_authoritative` | boolean | Always true in v1. |
| `legacy_rank` | integer | Production rank from Legacy Ranking. |
| `legacy_score` | number | Existing production score. |
| `scenario_rank` | integer or null | Scenario-aware observational rank. |
| `scenario_score` | number or null | Scenario-aware observational score. |
| `rank_difference` | integer or null | `scenario_rank - legacy_rank`. |
| `shadow_verdict` | string | `Agreement`, `Watch`, `Disagreement`, or `Blocker Candidate`. |
| `scenario_rank_reason` | string | Short explanation for upgrade/downgrade. |

Minimum visible UI can use only:

- `scenario_rank`
- `shadow_verdict`

But the metadata should still store rank difference and reason so the detail dialog can explain the result.

## 4. Optional Fields

Optional fields for future detail display:

| Field | Type | Meaning |
| --- | --- | --- |
| `rank_shift_label` | string | Stable, Minor Shift, Material Shift, Major Shift. |
| `scenario_consistency_score` | number | 0-100 scenario alignment score. |
| `tail_exposure` | number | Tail share from 0 to 1. |
| `tail_exposure_warning` | string or null | `Watch`, `Tail-heavy`, or `Not default-eligible in future v2`. |
| `asset_role_balance_score` | number | Role-balance score. |
| `main_scenario_coverage` | number | Main Scenario coverage from 0 to 1. |
| `secondary_insurance_coverage` | number | Secondary Scenario protection from 0 to 1. |
| `conflict_flags` | list | Auditor conflict labels. |
| `audit_status` | string | Pass, Warning, Fail. |
| `audit_severity` | string | None, Low, Medium, High, Critical. |
| `data_confidence` | string | high, medium, low. |
| `shadow_components` | object | Score component breakdown. |

## 5. Snapshot-Level Structure

Recommended snapshot field:

```json
{
  "portfolio_ranking_shadow": {
    "schema_version": 1,
    "mode": "shadow",
    "legacy_authoritative": true,
    "generated_at": "ISO-8601 timestamp",
    "source": "runtime",
    "summary": {
      "legacy_top_portfolio": "让球策略",
      "scenario_top_portfolio": "赔率分布优化器",
      "legacy_top_scenario_rank": 4,
      "agreement": false,
      "overall_shadow_verdict": "Disagreement"
    },
    "rows": []
  }
}
```

Each `rows[]` entry should mirror `strategy["shadow"]` plus identifying fields:

```json
{
  "portfolio_code": "E",
  "portfolio_name": "让球策略",
  "legacy_rank": 1,
  "legacy_score": 100,
  "scenario_rank": 4,
  "scenario_score": 61.9,
  "rank_difference": 3,
  "shadow_verdict": "Disagreement",
  "scenario_rank_reason": "Direction is clear, but role balance is narrow."
}
```

## 6. Best Generation Position

### Not Best: `evaluate_strategy(...)`

`evaluate_strategy(...)` evaluates one strategy at a time.

It can compute:

- expected profit
- ROI
- Sharpe
- role structure
- legacy score inputs
- path consistency

But it cannot know:

- final Legacy Rank
- final Scenario Rank
- rank difference
- whether another strategy is Scenario Rank 1

Therefore:

```text
Do not generate final strategy["shadow"] inside evaluate_strategy(...).
```

It may later provide input metrics for Shadow scoring, but not the final metadata.

### Best: After Legacy Ranking In `strategy_comparison(...)`

Best generation point:

```text
strategy_comparison(...)
  ↓
evaluate all strategies
  ↓
sort by existing legacy score
  ↓
assign rank_name
  ↓
compute Shadow Ranking on the ranked list
  ↓
attach strategy["shadow"]
  ↓
return ranked list in original Legacy order
```

Reason:

- all strategies are available
- Legacy order is already known
- Scenario score can compare portfolios against each other
- `scenario_rank` and `rank_difference` can be computed
- no production sort needs to change

Critical implementation rule:

```text
Shadow metadata must be attached after Legacy sorting and must not re-sort the returned strategies.
```

### Alternative: Separate Helper After `strategy_comparison(...)`

Safer future design:

```python
snapshot_strategies = strategy_comparison(...)
snapshot_strategies = attach_shadow_metadata(snapshot_strategies, match, result_distribution, scenario_engine, recommendation_audit)
```

This keeps `strategy_comparison(...)` unchanged and makes Shadow Mode easier to audit.

Recommended for first implementation:

- Prefer a separate helper after `strategy_comparison(...)`.
- Do not edit `strategy_score(...)`.
- Do not edit `evaluate_allocation(...)`.
- Do not change the sort key in `strategy_comparison(...)`.

## 7. Storage Location

### In-Memory Strategy Object

Primary UI read location:

```python
strategy["shadow"]
```

Visible Shadow Mode should read:

```python
shadow = strategy.get("shadow") or {}
```

If missing:

- show `-`
- do not fail
- do not parse Markdown reports

### Snapshot Payload

Recommended future snapshot location:

```python
snapshot_payload["portfolio_ranking_shadow"]
```

And because strategies are already stored in:

```python
snapshot_payload["strategy_snapshot"]["strategies"]
```

each strategy may also include its own `shadow` object.

Recommended storage approach:

- store per-strategy `shadow` in each strategy object
- store aggregate summary in top-level `portfolio_ranking_shadow`

Reason:

- UI can read strategy-level metadata directly.
- reports can read aggregate summary.
- snapshots remain self-contained.

## 8. My Portfolio Compatibility

Current My Portfolio path:

```text
evaluated_my_portfolio_strategy(...)
  ↓
evaluate_strategy(...)
  ↓
render_portfolio_ranking(...)
  ↓
append to comparison
```

My Portfolio compatibility requirement:

- My Portfolio should receive Shadow metadata using the same scoring and verdict rules as system portfolios.

Recommended behavior:

- Include My Portfolio in the Shadow comparison list after it is evaluated.
- Assign:
  - `legacy_rank` based on current Legacy comparison rank
  - `scenario_rank` based on Shadow comparison rank
  - `rank_difference`
  - `shadow_verdict`

Important:

- My Portfolio Shadow metadata must not affect system portfolio ranks.
- My Portfolio display can show its Scenario Rank among the combined comparison set.
- If My Portfolio is missing from snapshot, omit it from stored snapshot shadow rows.

## 9. Connection To Scenario Engine

Scenario Engine should provide inputs for Shadow Metadata:

- Main Scenario
- Secondary Scenario
- Upset Scenario
- asset scenario mapping
- scenario consistency score
- main scenario coverage
- secondary insurance coverage
- tail exposure
- data confidence

Shadow Metadata should consume these fields but not own their definitions.

Recommended dependency direction:

```text
Scenario Engine
  ↓
Shadow Metadata
```

Shadow Metadata should not recreate Scenario Engine logic if structured Scenario Engine output already exists.

## 10. Connection To Recommendation Auditor

Recommendation Auditor should provide:

- audit status
- audit severity
- conflict flags
- critical conflict count
- high conflict count
- downgrade reasons

Shadow Metadata should use Auditor output for:

- `shadow_verdict`
- `conflict_flags`
- `audit_status`
- `audit_severity`
- `scenario_rank_reason`

Recommended dependency direction:

```text
Scenario Engine
  ↓
Recommendation Auditor
  ↓
Shadow Metadata
```

If Auditor data is missing:

- Shadow Metadata can still generate basic rank fields
- `audit_status` should be `Unknown`
- `data_confidence` should be no higher than `medium`

## 11. Visible Shadow Mode Read Path

Visible Shadow Mode should read:

```python
shadow = strategy.get("shadow") or {}
```

Table v0.1 reads:

- `shadow["scenario_rank"]`
- `shadow["shadow_verdict"]`

Detail dialog reads:

- `legacy_rank`
- `legacy_score`
- `scenario_rank`
- `scenario_score`
- `rank_difference`
- `scenario_rank_reason`
- `tail_exposure_warning`
- `scenario_consistency_score`

Missing metadata behavior:

- display `-`
- do not raise errors
- do not parse Markdown
- do not hide the strategy

## 12. Verdict Rules

Suggested v1 rules:

| Condition | `shadow_verdict` |
| --- | --- |
| `rank_difference` is 0 or 1 and no High/Critical conflict | Agreement |
| `abs(rank_difference) == 2` and no High/Critical conflict | Watch |
| `abs(rank_difference) >= 3` | Disagreement |
| High/Critical conflict on Legacy Rank 1 | Blocker Candidate |

The verdict is informational only.

It must not:

- reorder portfolios
- block portfolios
- change default recommendation
- change score

## 13. Implementation Boundaries

Allowed future implementation:

- attach `strategy["shadow"]`
- add `portfolio_ranking_shadow` to snapshot payload
- show `Scenario Rank` and `Shadow Verdict` in UI
- show details in collapsed dialog

Not allowed:

- changing `strategy_score(...)`
- changing `evaluate_allocation(...)`
- changing Legacy sort order
- using `scenario_rank` as production rank
- making `shadow_verdict` block recommendations
- parsing Markdown reports in runtime UI
- mutating data files to backfill old reports without explicit approval

## Final Recommendation

Implement Shadow Metadata before Visible Shadow Mode.

Recommended order:

1. Generate structured Shadow metadata after Legacy Ranking is known.
2. Attach metadata to each strategy under `strategy["shadow"]`.
3. Store aggregate metadata under `snapshot_payload["portfolio_ranking_shadow"]`.
4. Let Visible Shadow Mode read only optional `strategy["shadow"]` fields.
5. Keep Legacy Ranking authoritative.
