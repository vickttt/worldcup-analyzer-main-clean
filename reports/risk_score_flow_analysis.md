# Risk Score Flow Analysis

Date: 2026-06-28
Task graph node: `NODE 2 - MODEL-DESIGN ANALYSIS (READ ONLY)`

## Executive Result

There is no single canonical `risk_score` contract. Risk behavior is currently inferred from several separate scoring, gating, ranking, exposure, and display mechanisms.

## Current Risk Signal Sources

| Source | Location | Risk signal | Downstream use |
| --- | --- | --- | --- |
| decision engine | `modules/decision_engine.py` and app imports | participation advice, upset/path risk, stake guidance | recommendation framing |
| strategy score | `modules/strategy/core.py` | loss ratio, concentration penalty, consistency, odds value | strategy ranking score |
| match betting score | `modules/strategy/core.py` | top strategy score, shadow verdict, sleeve status, max loss | match-level investment posture |
| ranking key | `modules/strategy/core.py` | risk gate level, rank-1 eligibility, correct-score exposure | ranking order |
| portfolio risk gate | `modules/portfolio_engine.py` | portfolio risk level and eligibility constraints | rank gating and display |
| portfolio score | `modules/portfolio_engine.py` | expected value, drawdown, coverage, pressure fit, efficiency | portfolio candidate score |
| app-local stake display | `app.py` | decision-to-stake display bands and combo stake mapping | UI and recommendation display |
| app-local optimizer | `app.py` | volatility, max loss, concentration, return matrix | optimized portfolio construction |

## Observed Flow

```text
odds / match / context inputs
  -> probability and result distribution
  -> decision and recommendation combo
  -> stake display hints
  -> strategy score
  -> portfolio score
  -> portfolio risk gate and rank eligibility
  -> ranking key
  -> recommendation display and golden outputs
```

## Strategy Score Path

`strategy_score` currently combines:

- EV/ROI quality.
- risk control derived from max loss relative to total stake.
- concentration penalty.
- script consistency.
- odds value.
- simplicity.

This produces a strategy score, not a standalone risk score. Risk is one component of a blended quality score.

## Portfolio Risk Path

Portfolio risk appears through:

- portfolio drawdown and max loss.
- exposure concentration.
- correct-score exposure share.
- rank-1 eligibility constraints.
- portfolio risk gate level.
- style and pressure-fit scoring.

These signals influence ranking and display, but they are not normalized into a single reusable risk object.

## Stake And Allocation Path

```text
strategy_score / match_betting_score / decision
  -> recommended stake display
  -> combo stake map
  -> portfolio allocation or optimized vector
  -> rendered portfolio weight
```

Known gap: same displayed risk posture does not necessarily imply a single deterministic stake rule because score bands, decision labels, and portfolio allocation functions are separate.

## Golden Validation Dependencies

- `reports/golden_output_snapshot_v1.json`.
- `reports/golden_output_snapshot_v2.json`.
- `reports/golden_risk_contract_v1.json` if present in the current branch.
- portfolio shadow reports.
- risk semantics reports.

Golden snapshots protect observable behavior, but they do not yet define the missing canonical risk contract.

## Gaps

- No explicit `RiskAssessment` object.
- No canonical field for `risk_score`.
- Risk labels and numerical risk controls can diverge.
- UI display stake and portfolio allocation are separate concepts.
- App-local portfolio helpers still mix optimization, scoring, comparison, and rendering responsibilities.
- Backtest cannot safely rely on current risk semantics without a stable contract.

## Conservative Gate Result

- `PORTFOLIO_EXTRACTION`: `BLOCKED`.
- `BACKTEST_READY`: `NO`.
- NODE 2 read-only analysis may proceed.
- Model or risk implementation must wait for an approved canonical risk contract.
