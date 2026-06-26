# Portfolio Shadow Coupling Map

This report maps coupling discovered while creating `modules/portfolio/shadow.py`. It is analysis-only and does not change production behavior.

## Hidden Dependency On Strategy Scores

- `rank_key_with_eligibility` sorts by eligibility, risk gate level, correct-score exposure, and `strategy["score"]`.
- `strategy["score"]` is not a single pure formula result; `evaluate_strategy` later allows `modules.portfolio_engine.compute_portfolio_score` to overwrite or reshape scoring output.
- Raw strategy name and display `rank_name` can diverge because `strategy_comparison` rewrites the first display label to `推荐组合`.
- Any extraction must preserve `original_name`, `rank_name`, `score`, `rank1_eligibility`, `risk_gate`, and `correct_score_exposure` together.

## Implicit Normalization Logic

- Amounts are normalized to 100-unit increments through `round_to_hundred`.
- `stake_amounts` reconciles rounding delta into the recommended item with the largest `share`.
- `allocate_strategy_items` reconciles allocation rounding delta into the item with the largest correlation-adjusted weight.
- `enforce_correct_score_floor` mutates already allocated amounts to force a correct-score floor when correct-score and non-correct-score items coexist.
- `recommended_stake_mvp` uses display stake bands that resemble allocation policy but are separate from portfolio construction.

## Shared State With Odds

- Portfolio candidates carry odds fields from recommendation construction: `odds`, `effective_odds`, `standard_odds`, `actual_odds`, `actual_ev`, and `ev_lift`.
- `correlation_adjusted_weight` uses `ev_lift` and `coverage_rate`, so odds/value analysis affects stake distribution even before final portfolio scoring.
- `modules/odds/core.py` still imports line-normalization and settlement helpers from `modules.portfolio_engine`, so odds and portfolio contracts remain partially coupled.
- Golden v2 shows scenarios with missing actual odds; future extraction must preserve fallback behavior when `actual_odds` is empty.

## UI-Driven Portfolio Logic

- `render_core_decision` constructs combo candidates, applies `stake_amounts`, runs `strategy_comparison`, and renders ranking in one runtime path.
- `render_portfolio_ranking` adds My Portfolio, duplicate-display merging, and detail rendering around the same evaluated strategy list.
- UI copy treats Legacy rank and Hybrid v0.2 diagnostics as display-only, but they sit beside production ranking fields.
- Snapshot generation also happens near UI orchestration, so extraction must separate persisted output shape from visual table shape.

## Shadow Boundary Recommendation

- Keep `modules/portfolio/shadow.py` unused by runtime until a formal golden assertion gate exists.
- Next safe step is a read-only comparator that loads golden v2 and reports diffs for strategy order, raw/display names, item amounts, top score, max loss, and final recommendation.
- Portfolio extraction remains blocked until saved output diffing passes on all golden scenarios.
