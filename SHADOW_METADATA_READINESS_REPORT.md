# Shadow Metadata v0.1 Implementation Readiness Report

Date: 2026-06-21

Scope: static implementation readiness check only. No code, UI, Ranking, recommendation logic, or data files were modified.

## Executive Verdict

Shadow Metadata v0.1 is ready for a safe, metadata-only implementation.

The current `strategy_comparison(...)` output already contains enough per-strategy information to attach minimal `strategy["shadow"]` metadata after Legacy Ranking is complete.

Recommended first implementation:

```text
snapshot_strategies = strategy_comparison(...)
snapshot_strategies = attach_shadow_metadata(snapshot_strategies, ...)
```

This approach can:

- preserve the existing strategy order
- preserve existing `score`
- preserve Legacy Ranking
- preserve recommendation logic
- add only `strategy["shadow"]`

## 1. Current `strategy_comparison(...)` Return Structure

Current flow:

```text
strategy_comparison(...)
  ↓
build_strategy_library(...)
  ↓
evaluate_strategy(...) for each strategy
  ↓
build_auto_optimized_strategy(...)
  ↓
sort by existing score
  ↓
assign original_name and rank_name
  ↓
return ranked list
```

Important current behavior:

```python
ranked = sorted(evaluated, key=lambda item: item["score"], reverse=True)
```

Then:

```python
strategy["original_name"] = strategy["name"]
strategy["rank_name"] = "推荐组合" if index == 0 else f"第{index + 1}组合"
```

Returned object:

- a list of evaluated strategy dictionaries
- already sorted by Legacy `score`
- already carrying Legacy rank labels through `rank_name`

Readiness:

- The returned list is the right place to infer `legacy_rank`.
- The returned list is the right input for a separate Shadow helper.
- The returned list must not be re-sorted after Shadow metadata is attached.

Risk: LOW if helper only annotates each strategy.

## 2. Existing Per-Strategy Fields

Current strategy objects already include:

| Requirement | Existing Field | Ready |
| --- | --- | --- |
| name / label | `name`, `rank_name`, `original_name`, `code` | Yes |
| score | `score`, `score_components` | Yes |
| EV | `expected_profit` | Yes |
| ROI | `expected_yield`, `capital_efficiency` | Yes |
| Sharpe | `sharpe_ratio` | Yes |
| path consistency | `consistency_score` | Yes |
| role exposure | `portfolio_style.role_exposure` | Yes |
| role balance | `role_constraint.adjustment`, `role_constraint.rows` | Yes |
| assets | `items` | Yes |
| score rows | `score_rows` | Yes |

Sample current strategy keys from existing snapshot:

```text
capital_efficiency
code
concentration
consistency_score
coverage
direction_alignment
expected_profit
expected_yield
hit_rate
items
max_loss
max_profit
name
original_name
portfolio_style
rank_name
risk_reward
role_constraint
score
score_components
score_rows
sharpe_ratio
stability_score
strategic_value
volatility
```

Conclusion:

```text
The existing strategy structure is sufficient for Shadow Metadata v0.1.
```

## 3. Can An Independent Helper Be Called After `strategy_comparison(...)`?

Answer:

- Yes.

Recommended placement:

```text
strategy_comparison(...)
  ↓
attach_shadow_metadata(strategies, match, distribution, optional_context)
  ↓
render / snapshot / report
```

Best first integration point:

- immediately after `snapshot_strategies = strategy_comparison(...)`

Reason:

- Legacy Ranking has already been produced.
- `rank_name` already exists.
- all strategies are available for relative Scenario Ranking.
- helper can compute `scenario_rank` without changing Legacy order.

Recommended helper contract:

```python
attach_shadow_metadata(strategies, match, distribution, scenario_engine=None, recommendation_audit=None)
```

Return behavior:

- may return the same list with each strategy annotated
- or return a shallow-copied list with `shadow` added

Safer first implementation:

- shallow-copy each strategy before adding `shadow`
- preserve list order exactly

Risk: LOW to MEDIUM depending on whether mutation is used.

## 4. Helper Safety Requirements

The helper must:

- not change list order
- not change `score`
- not change `rank_name`
- not change `original_name`
- not change `items`
- not change allocation amounts
- not change `score_components`
- not call `strategy_score(...)`
- not call `evaluate_allocation(...)`
- not call `strategy_comparison(...)` recursively
- not change default recommendation logic

The helper may:

- read existing fields
- compute Scenario Score separately
- compute Scenario Rank on a separate internal sorted copy
- attach `strategy["shadow"]`
- return annotated strategies in original Legacy order

Safe internal pattern:

```text
legacy_order = strategies as-is
scenario_order = sorted copy by scenario_score
attach ranks back by stable strategy identity
return legacy_order
```

Identity key recommendation:

- primary: `code`
- fallback: `rank_name`
- fallback: `name`
- fallback: list index

Risk: LOW if this pattern is followed.

## 5. Minimum v0.1 Fields

Recommended minimum `strategy["shadow"]`:

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
    "shadow_verdict": "Disagreement",
    "scenario_rank_reason": "Direction is clear, but role balance is narrow."
}
```

These fields are enough to support:

- Visible Shadow Mode table
- Shadow report generation
- detail dialog explanation later

Risk: LOW.

## 6. Scenario Score Feasibility

Minimal Scenario Score can be computed from existing fields:

| Scenario Score Input | Existing Source |
| --- | --- |
| value layer | `expected_yield`, `sharpe_ratio`, `expected_profit` |
| consistency layer | `consistency_score` |
| role balance | `portfolio_style.role_exposure`, `role_constraint.adjustment` |
| tail exposure | `portfolio_style.tail_share` |
| tempo exposure | `portfolio_style.tempo_share` |
| asset role hints | `items[].type`, `items[].selection`, `items[].share` |
| direction coverage | `direction_alignment`, winner/handicap assets |

Limitations:

- Full Scenario Engine metadata is not yet attached to strategy objects.
- Recommendation Auditor conflict flags are not yet structured in app runtime.
- v0.1 Scenario Score will be a Shadow approximation, not final Ranking 2.0.

Readiness:

- Good enough for metadata-only validation.
- Not enough to replace Legacy Ranking.

Risk: MEDIUM if interpreted as official score.
Risk: LOW if clearly labeled as Shadow-only.

## 7. Snapshot Payload Decision

Question:

- Should v0.1 write `portfolio_ranking_shadow` into `snapshot_payload`?

Recommendation:

- Not in the first v0.1 implementation.

Reason:

- User explicitly wants safe implementation.
- Snapshot writes increase compatibility risk.
- In-memory + report validation is enough for the next step.
- Snapshot schema can be added after helper behavior is validated.

Recommended v0.1 storage:

- in memory: `strategy["shadow"]`
- report output: generated Shadow metadata table
- no snapshot write yet

Future v0.2:

- add `portfolio_ranking_shadow` to `snapshot_payload`
- optionally persist per-strategy `shadow` in `strategy_snapshot.strategies`

Risk if no snapshot write:

- LOW

Tradeoff:

- Shadow metadata will not survive app reload unless report output is generated.

## 8. My Portfolio Compatibility

Current My Portfolio path:

```text
evaluated_my_portfolio_strategy(...)
  ↓
evaluate_strategy(...)
  ↓
append to comparison in render_portfolio_ranking(...)
```

Readiness:

- My Portfolio can receive Shadow metadata only if helper runs after My Portfolio is appended to the comparison list.
- Current `snapshot_strategies` generation does not include My Portfolio by default.

Recommended v0.1:

- Do not include My Portfolio in first metadata helper unless the helper is called inside `render_portfolio_ranking(...)` after My Portfolio append.
- For the first safe metadata/report implementation, focus on system strategies only.

Future compatibility:

- call Shadow helper on the combined comparison list when My Portfolio parity is needed.
- mark My Portfolio with `code == "my_portfolio"`.

Risk:

- LOW if excluded from v0.1.
- MEDIUM if included immediately due to extra rank-context complexity.

## 9. Function Impact Assessment

| Function | Need To Modify For Metadata v0.1? | Risk | Notes |
| --- | --- | --- | --- |
| `strategy_score(...)` | No | HIGH if modified | Must remain unchanged. |
| `evaluate_allocation(...)` | No | HIGH if modified | Must remain unchanged. |
| `evaluate_strategy(...)` | No | MEDIUM if modified | Already provides required fields. |
| `strategy_comparison(...)` | Prefer no direct change | MEDIUM | Best to call helper after this function, not inside it initially. |
| `portfolio_ranking_rows(...)` | No for metadata only | LOW | UI display comes later. |
| `render_portfolio_ranking(...)` | No for metadata-only report | MEDIUM | Needed later for Visible Shadow Mode. |
| Snapshot payload construction | No for v0.1 | MEDIUM | Defer snapshot persistence. |

## 10. Recommended v0.1 Implementation Boundary

Allowed in future v0.1 implementation:

- create independent `attach_shadow_metadata(...)`
- call it after `strategy_comparison(...)`
- compute minimal Shadow fields
- attach only `strategy["shadow"]`
- generate report from annotated in-memory strategies

Not allowed:

- changing Legacy sort
- changing default recommendation
- changing `score`
- writing snapshot payload
- modifying UI
- modifying data files
- using Shadow fields as production ranking

## 11. Readiness By Requirement

| Requirement | Readiness | Risk |
| --- | --- | --- |
| `strategy_comparison(...)` return structure known | Ready | LOW |
| strategy has name / label | Ready | LOW |
| strategy has score | Ready | LOW |
| strategy has EV / ROI / Sharpe | Ready | LOW |
| strategy has path consistency | Ready | LOW |
| strategy has role exposure | Ready | LOW |
| helper can run after `strategy_comparison(...)` | Ready | LOW |
| helper can preserve order | Ready | LOW |
| helper can preserve score | Ready | LOW |
| helper can preserve ranking | Ready | LOW |
| helper can add only `strategy["shadow"]` | Ready | LOW |
| minimal fields are enough | Ready | LOW |
| skip snapshot write in v0.1 | Recommended | LOW |

## Final Decision

Shadow Metadata v0.1 is safe to implement as an in-memory, report-only annotation step.

Best next implementation shape:

```text
strategy_comparison(...) produces Legacy-ranked strategies
attach_shadow_metadata(...) adds strategy["shadow"]
report generation reads strategy["shadow"]
Legacy order remains unchanged
```

Do not write to snapshot payload in v0.1.

Do not expose in UI until the metadata helper is validated.
