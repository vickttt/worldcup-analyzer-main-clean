# Module Extraction Plan v1

This is a future plan only. No code extraction was executed.

## Phase 1: Odds Extraction

Source blocks:

- `market_odds_overview_rows`
- `actual_odds_completeness`
- `actual_odds_completeness_for_match`
- `actual_odds_example`
- `user_odds_slug`
- `load_user_odds_cache`
- `save_user_odds_cache`
- `clear_user_odds_cache`
- `render_actual_odds_input` should remain UI but call an odds service.
- `portfolio_market_candidates`
- `match_portfolio_candidate`
- `infer_portfolio_type_and_selection`

Target modules:

- `modules/odds/actual_odds.py`
- `modules/odds/market_matching.py`
- `modules/ui/actual_odds_input.py`

Risks:

- Text matching, handicap parsing, and correct-score normalization are fragile.
- `modules.user_odds` already owns some logic, so extraction must avoid duplicate behavior.
- Streamlit form/cache behavior should stay in UI adapters.

Dependency concerns:

- Depends on `modules.market_utils`, `modules.user_odds`, `modules.team_resolver`, and `modules.portfolio_engine` line helpers.

## Phase 1: Strategy Extraction

Source blocks:

- `confidence_reason`
- `market_disagreement_reason`
- `strategy_item_groups`
- `main_path_correct_scores`
- `item_direction_alignment`
- `strategy_direction_alignment`
- `item_strategic_value`
- `strategy_strategic_value`
- `item_path_consistency`
- `strategy_path_consistency`
- `strategy_conclusion`
- `strategy_j_comparison`
- Hybrid metadata helpers
- `match_betting_score`
- `recommended_stake_mvp`

Target modules:

- `modules/strategy/explanations.py`
- `modules/strategy/path_consistency.py`
- `modules/strategy/hybrid_visible_metadata.py`
- `modules/strategy/match_decision.py`

Risks:

- Recommendation logic is product-sensitive.
- Strategy copy and score components are shown directly in UI.
- Must preserve current ranking behavior exactly.

Dependency concerns:

- Depends on portfolio structures and result distribution structures.

## Phase 2: Portfolio Extraction

Source blocks:

- `portfolio_metrics`
- `bet_correlation`
- `weighted_combo_correlation`
- `kelly_reference_rows`
- `strategy_holdings_rows`
- asset-role helpers
- `evaluate_allocation`
- `optimize_betting_portfolio`
- `build_strategy_library`
- `build_auto_optimized_strategy`
- `strategy_score`
- `evaluate_strategy`
- `strategy_comparison`
- ranking row/detail helpers

Target modules:

- `modules/portfolio/metrics.py`
- `modules/portfolio/allocation.py`
- `modules/portfolio/strategy_library.py`
- `modules/portfolio/ranking.py`
- `modules/ui/portfolio_ranking.py`

Risks:

- Highest-risk phase because Portfolio Ranking is core product logic.
- Protected functions must not change behavior: `strategy_score`, `evaluate_allocation`, `strategy_comparison`.
- Requires snapshot comparison tests before any move.

Dependency concerns:

- Depends on odds candidates, result distribution, portfolio engine helpers, and UI display row shapes.

## Phase 3: Analysis And Data Cleanup

Source blocks:

- score distribution helpers
- scenario probability helpers
- outcome settlement helpers
- snapshot path/load/save helpers
- fixture refresh helpers
- schedule data helpers
- team intelligence render prep

Target modules:

- `modules/analysis/score_paths.py`
- `modules/analysis/risk.py`
- `modules/data/snapshots.py`
- `modules/data/fixtures.py`
- `modules/backtest/settlement.py`

Risks:

- Snapshot schema compatibility must be preserved.
- Data/history files are protected and must not be rewritten during extraction.
- Schedule and API refresh paths must remain terminal-script driven.

Dependency concerns:

- Depends on `modules.result_distribution`, `modules.worldcup_db`, `modules.schedule_client`, and local history paths.

## Phase 4: UI Separation

Source blocks:

- all `render_*` functions
- page orchestration functions
- runtime bootstrap block
- CSS and visual helpers
- schedule portal components

Target modules:

- `modules/ui/common.py`
- `modules/ui/schedule_page.py`
- `modules/ui/analysis_page.py`
- `modules/ui/post_match_page.py`
- `modules/ui/portfolio_components.py`
- `modules/ui/market_components.py`

Risks:

- Streamlit rerun/session behavior can change subtly.
- UI display copy and table column order are decision-facing product behavior.
- Large move should be done in small PRs with screenshot/manual QA.

Dependency concerns:

- UI modules should depend on orchestration/service outputs, not call low-level data clients directly.

## Required Gates Before Any Extraction

- Confirm exact allowed and forbidden files for each phase.
- Add snapshot or golden-output checks around Portfolio Ranking and odds matching.
- Run `git diff --check` and Python syntax checks.
- Update `docs/CHANGELOG.md` and `docs/QA_REPORT.md` for each implementation PR.
- Keep `app.py` as runtime entry until all page modules are verified.
