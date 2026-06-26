# Post Extraction Dependency Graph

This graph reflects the state after Phase 1 odds and strategy extraction. It is based on static import inspection and does not run the full app.

## app.py -> module calls

`app.py` now imports from:

- `modules.odds.core`
  - `actual_odds_completeness`
  - `actual_odds_completeness_for_match`
  - `correct_score_outcome`
  - `fmt_odds`
  - `handicap_outcome`
  - `handicap_profit_value`
  - `market_odds_overview_rows`
  - `parse_handicap_selection`
  - `parse_total_selection`
  - `total_outcome`
  - `winner_outcome`
- `modules.strategy.core`
  - `clamp`
  - `confidence_reason`
  - `hybrid_v2_status_label`
  - `item_path_consistency`
  - `market_disagreement_reason`
  - `match_betting_score`
  - `rank_key_with_eligibility`
  - `recommended_stake_mvp`
  - `round_to_hundred`
  - `shadow_verdict_label`
  - `strategy_path_consistency`
  - `strategy_score`

## module -> module calls

- `modules.odds.core`
  - imports `modules.portfolio_engine.normalize_handicap_line`
  - imports `modules.portfolio_engine.settle_asian_handicap`
  - imports `modules.user_odds.build_market_candidates`
  - imports `modules.user_odds.candidate_with_actual`
- `modules.strategy.core`
  - imports no project modules.

## circular dependency detection

- `modules.odds.core` does not import `modules.strategy.core`.
- `modules.strategy.core` does not import `modules.odds.core`.
- `app.py` imports both modules, but neither module imports `app.py`.
- No direct circular dependency was introduced between the extracted modules.

## UI coupling hotspots

- `app.py` still imports Streamlit and remains the runtime/UI entry.
- `modules.odds.core` does not import Streamlit directly.
- `modules.strategy.core` does not import Streamlit.
- Existing non-UI modules outside Phase 1 still import Streamlit for cache behavior:
  - `modules.odds_client.py`
  - `modules.polymarket_client.py`
  - `modules.schedule_client.py`
  - `modules.team_profile_client.py`
  - `modules.team_resolver.py`
  - `modules.the_odds_client.py`
  - `modules.weather_client.py`

## Dependency Risk Summary

- `modules.strategy.core`: Low import risk, medium contract risk.
- `modules.odds.core`: Medium import risk because it still reaches into `portfolio_engine` and `user_odds`.
- `app.py`: High coupling remains because it still orchestrates UI, data, portfolio, strategy, and post-match audit flows.

## Readiness Decision

- READY FOR PORTFOLIO EXTRACTION: NO.
  - Reason: portfolio functions remain tightly coupled with `app.py`, `modules.portfolio_engine`, odds candidates, and UI row shapes.
- READY FOR BACKTEST MODULE SPLIT: NO.
  - Reason: post-match audit and settlement logic still depend on shared app-level snapshot and strategy dictionaries.
