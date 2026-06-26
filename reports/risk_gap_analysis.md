# Risk Gap Analysis

This report identifies missing risk variables, implicit assumptions, hidden normalization, and UI-driven risk overrides. It is read-only.

## Missing Risk Variables

- No canonical `risk_score` field linking strategy, portfolio, decision stake, and backtest.
- Missing full `risk_gate` payloads in golden v2 top strategy snapshots.
- Missing explicit volatility bands and max-loss bands in snapshot schema.
- Missing explicit mapping from market disagreement/upset index to stake adjustment.
- Missing post-match risk outcome variables: realized drawdown, hit-path category, risk-gate false positive/negative.

## Implicit Assumptions In app.py

- Decision stake is assumed available from `decision.recommended_stake`; portfolio construction trusts it as total stake.
- `render_core_decision` couples candidate generation, stake assignment, strategy comparison, portfolio ranking display, and risk notes.
- Portfolio ranking assumes dict schemas with fields like `risk_gate`, `correct_score_exposure`, `coverage_metrics`, and `portfolio_score_components` when present.
- Missing market data can fall back to neutral or default behavior instead of explicit risk class.

## Hidden Normalization Functions

- `round_to_hundred` normalizes capital amounts.
- `clamp` normalizes score ranges.
- `stake_amounts` shifts rounding residue to largest share candidate.
- `allocate_strategy_items` shifts rounding residue to highest correlation-adjusted item.
- `enforce_correct_score_floor` mutates allocated capital after initial weights.
- `correct_score_exposure_control` changes exposure limit by style label.

## UI-Driven Risk Overrides

- `render_core_risk_summary`, `render_risk_analysis`, and `render_portfolio_detail_expanders` present risk warnings from different sources, without one canonical risk object.
- `recommended_stake_mvp` is display guidance and can be mistaken for production stake policy.
- UI/session state controls My Portfolio parsing and detail expansion around the same strategy list used for production-looking output.

## Gap Classification

HIGH RISK GAP (BLOCKER)

## Why This Blocks Extraction

- Backtest and portfolio extraction need reproducible risk semantics, not only saved output alignment.
- Current golden v2 proves allocation/stake alignment for available fields but does not prove full risk-gate internals.
- Risk semantics cross app, strategy, portfolio engine, shadow module, saved decision fields, and UI display paths.