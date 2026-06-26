# Risk Feature Extraction v1

This report extracts the current risk semantics from strategy, portfolio, shadow, and saved golden v2 outputs. It is read-only and does not implement a new risk model.

## Source Files Read

- `modules/strategy/core.py`: `match_betting_score`, `recommended_stake_mvp`, `strategy_score`, `rank_key_with_eligibility`.
- `app.py`: `evaluate_allocation`, `evaluate_strategy`, `recommended_total_stake`, `stake_amounts`, UI risk rendering and orchestration.
- `modules/portfolio_engine.py`: `compute_portfolio_score`, `portfolio_risk_gate`, `correct_score_exposure_control`, `rank1_eligibility_check`.
- `modules/portfolio/shadow.py`: read-only mirror for stake/allocation observation.
- `reports/golden_output_snapshot_v2.json` sha256: `4fc5e5eeacdf6cbf6c38d8d2a72245a92311f22f271f1c9ce0106c8058c2bb40`.

## Extracted Risk Features

### Risk Score Computation

- There is no single explicit `risk_score` object.
- `strategy_score` contains a `风险控制` component derived from `loss_ratio = max_loss / total_stake` minus `concentration * 30`, clamped to 0-100 before contributing 20% to score.
- `compute_portfolio_score` creates `Risk-Adjusted Value` from expected yield and volatility, then adds `Drawdown / Zero Risk` from max loss ratio plus zero-risk coverage.
- `portfolio_risk_gate` classifies `LOW / MEDIUM / HIGH / CRITICAL` from failed scenario probability, adjacent-path failure, main-path positive coverage, narrow exact-score dependency, and pressure strictness.
- `rank_key_with_eligibility` converts risk gate level into a sort rank and subtracts correct-score exposure share.

### Stake Scaling Rules

- Decision stake in saved snapshots comes from `decision.recommended_stake.amount`, with saved explanation based on direction confidence and value rating.
- `stake_amounts` distributes decision stake by candidate `share`, rounds to hundreds, then reconciles rounding delta into the recommended item with largest share.
- `allocate_strategy_items` distributes total stake by correlation-adjusted weight, rounds to hundreds, then reconciles rounding delta into strongest weighted item.
- `recommended_stake_mvp` is display-layer stake guidance from match-level score bands: 0, 300, 500, 800, 1200, 1500; it is not the same as saved production decision stake.

### Clamp / Cap Logic

- Scores are clamped by `clamp(value, 0, 100)`.
- Amounts are rounded by `round_to_hundred`.
- `recommended_stake_mvp` caps display stake to 0-2000.
- `enforce_correct_score_floor` imposes a correct-score minimum of `max(100, round_to_hundred(total_stake * 0.16))` when correct-score and non-correct-score assets coexist.
- Correct-score exposure limits are 20% conservative, 30% default, 40% aggressive.

### Volatility Adjustments

- `evaluate_allocation` and `evaluate_strategy` compute variance, volatility, Sharpe ratio, max loss, and stability.
- Optimizer utility subtracts `risk_lambda * risk * 0.04`, where risk includes volatility, max loss, and correlation.
- Portfolio score penalizes volatility through `Risk-Adjusted Value` and max-loss/zero-risk through `Drawdown / Zero Risk`.

### Disagreement Penalties

- `market_disagreement` is displayed and saved in `decision`, but it is not a unified portfolio risk variable.
- `match_betting_score` penalizes shadow verdict `Disagreement` by -10 and `Blocker Candidate` by -25 when shadow metadata exists.
- Golden v2 saved decisions show market disagreement and upset index, but stake is not a direct monotonic function of either field.

## Golden v2 Extracted Risk Fields

| Match | Top strategy | Score | Max loss | Volatility | Risk component | Decision stake | Direction confidence | Disagreement | Upset | Coverage | Risk gate payload |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| Tunisia vs Japan | 只买最佳波胆 | 62 | 300 | 669.35 | 2 | 300 | 64 | 46 | 63 | main - / zero - | missing |
| Japan vs Sweden | 让球策略 | 49 | 1200 | 1098.81 | 53 | 1200 | 79 | 21 | 47 | main 0% / zero 35% | missing |
| Ecuador vs Germany | 独赢策略 | 74 | 200 | 150.96 | 55 | 200 | 57 | 0 | 52 | main 100% / zero 16% | missing |
| Scotland vs Brazil | 独赢策略 | 73 | 1100 | 599.58 | 44 | 1100 | 76 | 8 | 60 | main 100% / zero 14% | missing |
| New Zealand vs Egypt | 只买最佳波胆 | 44 | 100 | 213.01 | 2 | 100 | 0 | 0 | 47 | main - / zero - | missing |

## Extraction Result

- Risk behavior is distributed across scoring, gate, stake, coverage, and UI/display layers.
- `risk_gate` payload is missing from all golden v2 top strategies, preserving the assertion gate coverage gap.
- Current risk semantics are observable but not explicit enough for backtest or portfolio extraction.