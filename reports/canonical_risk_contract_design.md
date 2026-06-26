# Canonical Risk Contract Design

This report defines the canonical risk contract required before portfolio extraction or backtest enablement.

It is design-only. It does not modify runtime logic, extract portfolio logic, enable backtest logic, recompute golden outputs, or change recommendation behavior.

## Contract Goal

Create one auditable risk payload that can be produced by the current recommendation flow, saved in golden fixtures, replayed by a future portfolio module, and checked by future backtest code.

The contract must make these currently distributed semantics explicit:

- strategy-level loss, volatility, concentration, and reward/risk inputs
- scenario path coverage and failed-path probability
- market disagreement and upset pressure
- correct-score exposure and tail dependency
- rank eligibility gates
- stake sizing inputs and post-sizing allocation totals
- post-match realized risk outcomes

## Non-Goals

- Do not define a new scoring formula.
- Do not change `strategy_score`, `compute_portfolio_score`, `portfolio_risk_gate`, `rank_key_with_eligibility`, or stake allocation behavior.
- Do not move portfolio code out of `app.py`.
- Do not wire `modules/portfolio/shadow.py` into runtime.
- Do not enable independent backtest execution.
- Do not overwrite existing `reports/golden_output_snapshot_v1.json` or `reports/golden_output_snapshot_v2.json`.

## Contract Version

Canonical payload version: `risk_contract_v1`.

Every future payload must include:

- `contract_version`
- `contract_status`
- `producer`
- `source_snapshot_id`
- `generated_at`

Allowed `contract_status` values:

- `observed`: serialized from existing runtime output without changing behavior
- `replayed`: produced by a read-only replay runner
- `settled`: includes post-match realized risk outcome fields
- `invalid`: payload failed schema or invariant checks

## Canonical Payload Shape

```json
{
  "contract_version": "risk_contract_v1",
  "contract_status": "observed",
  "producer": {
    "name": "worldcup-analyzer",
    "mode": "runtime_snapshot",
    "code_ref": "git_sha_or_manual_ref"
  },
  "source_snapshot_id": "2026_06_25_Japan_Sweden_pre",
  "generated_at": "ISO-8601 timestamp",
  "match": {
    "match_id": "string_or_null",
    "home_team": "string",
    "away_team": "string",
    "kickoff_time": "ISO-8601 timestamp or null",
    "snapshot_phase": "pre"
  },
  "strategy_identity": {
    "strategy_id": "stable_string",
    "strategy_name": "string",
    "rank_position": 1,
    "asset_count": 3,
    "asset_types": ["winner", "handicap", "correct_score"]
  },
  "risk_inputs": {
    "total_stake": 1200,
    "max_loss": 1200,
    "loss_ratio": 1.0,
    "volatility": 1098.81,
    "concentration": 0.0,
    "risk_reward": 0.85,
    "expected_profit": 0,
    "expected_yield": 0.0,
    "sharpe_ratio": 0.0,
    "stability_score": 0.0
  },
  "scenario_risk": {
    "main_path_positive_coverage": 0.0,
    "zero_loss_coverage": 0.35,
    "failed_scenario_probability": null,
    "adjacent_path_failure": null,
    "narrow_exact_score_dependency": null,
    "pressure_strictness": null,
    "scenario_consistency_score": null,
    "shadow_verdict": "Agreement"
  },
  "market_risk": {
    "direction_confidence": 79,
    "market_disagreement": 21,
    "upset_index": 47,
    "value_rating": "A",
    "liquidity_quality": "unknown",
    "data_completeness": "complete"
  },
  "exposure_risk": {
    "correct_score_stake": 100,
    "correct_score_share": 0.0833,
    "correct_score_limit": 0.3,
    "correct_score_limit_source": "default",
    "tail_asset_stake": 0,
    "tail_asset_share": 0.0,
    "dominant_asset_share": 0.5833
  },
  "risk_gate": {
    "risk_level": "MEDIUM",
    "rank1_eligible": true,
    "gate_reasons": [],
    "hard_blockers": [],
    "soft_warnings": []
  },
  "stake_contract": {
    "decision_stake": 1200,
    "decision_stake_source": "decision.recommended_stake.amount",
    "display_stake": null,
    "rounding_unit": 100,
    "rounding_residue_target": "largest_share_or_highest_weight_item",
    "allocation_total": 1200,
    "allocation_matches_decision_stake": true
  },
  "risk_score_components": {
    "strategy_risk_control": 53,
    "portfolio_risk_adjusted_value": null,
    "portfolio_drawdown_zero_risk": null,
    "canonical_risk_score": null
  },
  "invariants": {
    "allocation_total_equals_decision_stake": true,
    "loss_ratio_matches_max_loss_over_total_stake": true,
    "correct_score_share_within_limit": true,
    "rank1_eligibility_has_gate_payload": true,
    "missing_required_fields": []
  },
  "post_match_risk_outcome": null
}
```

## Required Fields

### Identity Fields

| Field | Required | Purpose |
| --- | --- | --- |
| `contract_version` | yes | Stable schema version for fixture and migration checks. |
| `contract_status` | yes | Distinguishes observed, replayed, settled, and invalid payloads. |
| `source_snapshot_id` | yes | Links payload to the saved pre/post snapshot or golden fixture row. |
| `match.home_team` / `match.away_team` | yes | Human-readable fixture identity. |
| `strategy_identity.strategy_id` | yes | Stable key for replay comparisons. |
| `strategy_identity.rank_position` | yes | Required to audit Rank #1 eligibility and ranking drift. |

### Risk Input Fields

| Field | Required | Notes |
| --- | --- | --- |
| `total_stake` | yes | Capital at risk for this strategy after sizing. |
| `max_loss` | yes | Worst observed or modeled loss for the strategy. |
| `loss_ratio` | yes | Must equal `max_loss / total_stake` when `total_stake > 0`. |
| `volatility` | yes | Required for portfolio/backtest risk assertions. |
| `concentration` | yes | Required because current risk-control score penalizes concentration. |
| `risk_reward` | yes | Required to preserve current score explanation. |
| `expected_profit` | optional in v1 | May be missing in degraded snapshots. |
| `expected_yield` | optional in v1 | Required before backtest enablement. |
| `sharpe_ratio` | optional in v1 | Required before backtest enablement. |
| `stability_score` | optional in v1 | Required before backtest enablement. |

### Scenario Risk Fields

| Field | Required | Notes |
| --- | --- | --- |
| `main_path_positive_coverage` | yes | Must be explicit; use `null` only when not computable. |
| `zero_loss_coverage` | yes | Must be explicit; use `null` only when not computable. |
| `failed_scenario_probability` | yes | May be `null` in observed v1 but must exist as a key. |
| `adjacent_path_failure` | yes | Required to preserve `portfolio_risk_gate` semantics. |
| `narrow_exact_score_dependency` | yes | Required for tail-path dependency audit. |
| `pressure_strictness` | yes | Required for gate replay. |
| `scenario_consistency_score` | yes | May be `null` until Scenario Guardrails become canonical. |
| `shadow_verdict` | yes | Captures Agreement/Disagreement/Blocker Candidate behavior. |

### Market Risk Fields

| Field | Required | Notes |
| --- | --- | --- |
| `direction_confidence` | yes | Current saved stake explanations depend on this value. |
| `market_disagreement` | yes | Required even though current stake impact is not monotonic. |
| `upset_index` | yes | Required for upset-pressure audit. |
| `value_rating` | yes | Current saved stake explanations use value rating adjustments. |
| `liquidity_quality` | yes | Use `unknown` when unavailable. |
| `data_completeness` | yes | One of `complete`, `partial`, `missing`, `unknown`. |

### Exposure Risk Fields

| Field | Required | Notes |
| --- | --- | --- |
| `correct_score_stake` | yes | Required because correct-score floors and limits alter allocation. |
| `correct_score_share` | yes | Required for exposure caps and ranking penalty checks. |
| `correct_score_limit` | yes | Required for conservative/default/aggressive exposure policy. |
| `correct_score_limit_source` | yes | Example values: `conservative`, `default`, `aggressive`, `unknown`. |
| `tail_asset_stake` | yes | Required before backtest can classify tail-heavy portfolios. |
| `tail_asset_share` | yes | Required before backtest can classify tail-heavy portfolios. |
| `dominant_asset_share` | yes | Required to audit concentration and hidden single-asset exposure. |

### Risk Gate Fields

| Field | Required | Notes |
| --- | --- | --- |
| `risk_level` | yes | Allowed values: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, `UNKNOWN`. |
| `rank1_eligible` | yes | Must be explicit for future extraction. |
| `gate_reasons` | yes | List, empty when no reasons exist. |
| `hard_blockers` | yes | List, empty when none exist. |
| `soft_warnings` | yes | List, empty when none exist. |

### Stake Contract Fields

| Field | Required | Notes |
| --- | --- | --- |
| `decision_stake` | yes | Production-like total stake from saved decision layer. |
| `decision_stake_source` | yes | Must identify whether value came from saved decision, replay, or manual fixture. |
| `display_stake` | yes | May be `null`; prevents display stake from being confused with production stake. |
| `rounding_unit` | yes | Current value is `100`. |
| `rounding_residue_target` | yes | Required to replay stake allocation deterministically. |
| `allocation_total` | yes | Sum of allocated asset stakes. |
| `allocation_matches_decision_stake` | yes | Assertion field, not a recommendation input. |

### Risk Score Component Fields

| Field | Required | Notes |
| --- | --- | --- |
| `strategy_risk_control` | yes | Current `strategy_score` risk-control component. |
| `portfolio_risk_adjusted_value` | yes | May be `null` in observed v1. |
| `portfolio_drawdown_zero_risk` | yes | May be `null` in observed v1. |
| `canonical_risk_score` | yes | Must be `null` in v1 until a separate approved task defines the formula. |

## Post-Match Risk Outcome Shape

`post_match_risk_outcome` is `null` for pre-match payloads.

For settled payloads it must use this shape:

```json
{
  "actual_score": {
    "home": 2,
    "away": 1
  },
  "realized_profit": 0,
  "realized_drawdown": 0,
  "realized_loss_ratio": 0.0,
  "hit_path_category": "main_path",
  "failed_path_category": null,
  "risk_gate_result": {
    "false_positive": false,
    "false_negative": false,
    "notes": []
  },
  "correct_score_exposure_result": {
    "correct_score_hit": false,
    "correct_score_loss": 100,
    "tail_dependency_realized": false
  }
}
```

Allowed `hit_path_category` values:

- `main_path`
- `secondary_path`
- `upset_path`
- `tail_path`
- `zero_or_near_zero_path`
- `unknown`

Allowed `failed_path_category` values:

- `main_path_failed`
- `adjacent_path_failed`
- `favorite_pressure_failed`
- `upset_not_covered`
- `tail_overweight_failed`
- `none`
- `unknown`

## Golden Fixture Requirements

Before portfolio extraction or backtest enablement, create a new fixture file rather than modifying existing golden snapshots:

- proposed file: `reports/golden_risk_contract_v1.json`
- source: existing saved pre-match snapshots and saved post-match results only
- generation mode: read-only serialization first, replay validation later
- minimum coverage: all five golden v2 pre-match scenarios
- post-match coverage: at least five settled fixtures before `BACKTEST_READY` can become `YES`

Required scenario coverage:

| Scenario | Required | Reason |
| --- | --- | --- |
| high odds mismatch | yes | Tests market disagreement and stake caution. |
| balanced 50/50 market | yes | Tests high stake despite medium ranking score. |
| low-volatility favorite | yes | Tests low stake with strong ranking score. |
| upset-prone favorite/handicap tension | yes | Tests upset pressure and main-path coverage. |
| incomplete odds / degraded data | yes | Tests explicit data completeness and unknown fields. |
| correct-score-heavy strategy | yes | Tests correct-score exposure limit and floor logic. |
| tail-heavy portfolio | yes | Tests tail exposure and warning fields. |
| Rank #1 blocked by risk gate | yes before extraction | Tests eligibility gate behavior. |
| post-match realized drawdown | yes before backtest | Tests settlement risk outcome. |
| post-match risk-gate miss | yes before backtest | Tests false positive/false negative audit. |

Each fixture row must include:

- raw source snapshot reference
- top strategy risk contract
- at least one non-top strategy risk contract when available
- expected invariant results
- explicit `null` values for unavailable fields
- no recomputed ranking or allocation unless the fixture status is `replayed`

## Fixture Invariants

Golden risk fixtures must assert:

- `allocation_total == decision_stake` when all allocated item stakes are available
- `loss_ratio == max_loss / total_stake` when `total_stake > 0`
- `correct_score_share <= correct_score_limit` unless an explicit warning/blocker explains the breach
- `rank1_eligible` cannot be asserted unless `risk_gate` payload exists
- `canonical_risk_score` remains `null` until formula approval
- `display_stake` must not be used as `decision_stake`
- unknown data must be encoded as `null` or `unknown`, not silently defaulted to low risk
- post-match settled rows must preserve the pre-match risk payload and append outcome fields rather than mutating pre-match inputs

## Migration Plan

### Phase 0: Contract Approval

- Review this design and approve the field set.
- Do not change runtime code.
- Do not extract portfolio.
- Do not enable backtest.

Exit criteria:

- `reports/canonical_risk_contract_design.md` approved.
- `PORTFOLIO_EXTRACTION: BLOCKED`.
- `BACKTEST_READY: NO`.

### Phase 1: Read-Only Fixture Serializer

- Add a script that reads existing snapshots and emits `reports/golden_risk_contract_v1.json`.
- Serializer must not import Streamlit.
- Serializer must not call production ranking or allocation functions in a way that changes outputs.
- Missing fields must be explicit `null` or `unknown`.

Exit criteria:

- All five golden v2 pre-match rows have contract payloads.
- Schema validation passes.
- No runtime code imports the serializer.

### Phase 2: Replay Validator

- Add a read-only validator that compares observed fixture values against replayed values from current functions.
- Validator must report diffs only.
- No formula changes are allowed in this phase.

Exit criteria:

- Risk input, exposure, gate, and stake-contract invariants pass or are explicitly classified as coverage gaps.
- Portfolio extraction remains blocked if any Rank #1 strategy lacks a full gate payload.

### Phase 3: Settled Risk Fixtures

- Extend the fixture with post-match risk outcomes from saved post-match results.
- Classify hit path, failed path, realized drawdown, and correct-score exposure result.
- Keep benchmark/backtest disabled.

Exit criteria:

- At least five settled rows exist.
- Realized risk fields can be checked without changing ranking code.

### Phase 4: Extraction Readiness Gate

- Re-run golden assertion, risk contract validation, and settled fixture validation.
- Confirm the contract can represent all fields used by portfolio ranking and stake allocation.
- Only after this gate can a separate task propose portfolio extraction.

Exit criteria:

- `PORTFOLIO_EXTRACTION` may move from `BLOCKED` to `CANDIDATE` only by explicit approval.
- `BACKTEST_READY` remains `NO`.

### Phase 5: Backtest Readiness Gate

- Only after portfolio extraction has a stable contract and settled fixtures pass, evaluate backtest readiness.
- Backtest must consume contract fields instead of implicit UI/runtime state.

Exit criteria:

- `BACKTEST_READY` may move from `NO` to `CANDIDATE` only by explicit approval.

## Approval Gates

Portfolio extraction remains blocked until all are true:

- canonical risk fixture exists
- full `risk_gate` payload exists for Rank #1 strategies
- stake contract invariants pass
- correct-score exposure fields are covered
- replay validator can run without Streamlit UI state
- no missing required contract fields outside approved `null`/`unknown` cases

Backtest remains disabled until all are true:

- portfolio extraction gate has passed
- settled risk fixtures exist
- realized drawdown and failed-path categories are available
- post-match risk-gate false positive/negative checks are available
- benchmark runner can consume the risk contract without recomputing hidden UI state

## Current Decision

- Canonical risk contract: DESIGN DEFINED.
- Runtime logic affected: No.
- Portfolio extraction: BLOCKED.
- Backtest readiness: NO.
- Golden outputs changed: No.
- Next allowed task: read-only `golden_risk_contract_v1` fixture serializer, only after explicit approval.
