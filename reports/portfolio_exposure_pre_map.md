# Portfolio Exposure Pre-Map

This report identifies portfolio exposure and allocation coupling points before any portfolio extraction. It is analysis-only.

## Allocation Size Decisions

- `app.py::recommended_total_stake(decision)` decides the total stake budget used by `render_core_decision` and snapshot generation.
- `app.py::stake_amounts(combo, decision)` applies decision-level stake values to recommendation candidates before strategy comparison.
- `app.py::optimize_betting_portfolio(match, distribution, combo, total_stake, risk_profile="standard")` rounds total stake into 100-unit allocation units and searches allocation vectors.
- `app.py::evaluate_allocation(...)` converts allocation vector units to amounts with `amounts = [unit * 100 for unit in vector]`.
- `app.py::allocate_strategy_items(items, total_stake)` assigns strategy item amounts by weighted share and then reconciles rounding difference.
- `modules/strategy/core.py::recommended_stake_mvp(match_score)` maps match-level score bands to display stake amounts.

## Stake Scaling Logic

- `allocate_strategy_items` uses `correlation_adjusted_weight` to scale stake by item type, score boost, EV lift, coverage boost, and correlation penalty.
- `optimize_betting_portfolio` constrains allocations to 100-unit steps through `units = max(1, int(round(total_stake / 100)))`.
- `evaluate_allocation` converts allocation vectors to real stake amounts using 100-unit increments.
- `recommended_stake_mvp` uses fixed display tiers: 0, 300, 500, 800, 1200, and 1500, then clamps to 0-2000 and rounds to hundreds.

## Risk Adjustment Logic

- `evaluate_allocation` computes expected profit, hit probability, volatility, max loss, correlation, strategic value, consistency score, Sharpe ratio, stability, and utility.
- `strategy_score` in `modules/strategy/core.py` applies EV/ROI, risk control, script consistency, odds value, and simplicity weights.
- `modules/portfolio_engine.py::compute_portfolio_score` overwrites final portfolio score after evaluating coverage, directional odds value, pressure fit, drawdown, and simplicity.
- `portfolio_risk_gate`, `correct_score_exposure_control`, and `rank1_eligibility_check` in `modules/portfolio_engine.py` affect downstream display eligibility and ranking order.

## Constraints, Caps, Clamps, And Normalization

- `allocate_strategy_items` rounds each allocation to hundreds and reconciles total stake difference into the strongest weighted item.
- `enforce_correct_score_floor` enforces a minimum correct-score stake target of `max(100, round_to_hundred(total_stake * 0.16))` when correct-score and non-correct-score assets coexist.
- `enforce_correct_score_floor` protects other items from dropping below 100 while transferring stake.
- `strategy_item_groups` limits correct-score items and core market items before strategy construction.
- `build_strategy_library` caps correct-score exposure in constructed strategy item lists and dedupes portfolios.
- `rank_key_with_eligibility` sorts by rank eligibility, risk gate level, correct-score stake share penalty, and score.

## High Risk Coupling Points

- HIGH RISK: `evaluate_strategy` both allocates items and computes output metrics; moving it can change item amounts, max loss, and ranking if imports or helper contracts drift.
- HIGH RISK: `compute_portfolio_score` overwrites strategy score after app-level metrics are computed, creating a cross-module scoring contract.
- HIGH RISK: `rank_key_with_eligibility` depends on `risk_gate`, `correct_score_exposure`, and `rank1_eligibility` fields injected by `evaluate_strategy`.
- HIGH RISK: `enforce_correct_score_floor` mutates item amounts after initial allocation and can affect all downstream score and exposure values.
- HIGH RISK: `stake_amounts`, `recommended_total_stake`, and `recommendation_combo` determine the candidate amounts before portfolio construction.
- MEDIUM RISK: `recommended_stake_mvp` is display-oriented but uses the same capital language as portfolio allocation and must remain distinct from actual strategy allocation.

## Extraction Guidance

Do not extract portfolio code until a diff-based golden test can compare at least: strategy order, strategy scores, item selections, item amounts, max_loss, final recommendation, and saved decision stake fields for all v2 golden matches.
