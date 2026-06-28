# app.py Data Flow Trace

This report traces current data flow at the entry layer. It is descriptive only; no logic was changed.

## High-Level Flow

```text
Schedule/API/cache/history/user input
  -> fixture selection and match parsing
  -> odds and market candidate assembly
  -> probability and behavior model assembly
  -> strategy and portfolio construction
  -> ranking, score, and audit helpers
  -> Streamlit rendering and report/export output
```

## Input Sources

- Config: `config.yaml` via `load_config()`.
- Streamlit session state: page, selected fixture, selected match text, cached user inputs.
- Schedule/API data: `fetch_world_cup_schedule`, `fetch_match_data`, `fetch_odds`, `fetch_polymarket`, `fetch_team_profile`, `weather_for_fixture`.
- Local database/cache/history: `load_match_database`, `db_*` helpers, `data/history/*`, `data/worldcup2026/*`, user odds cache paths, my portfolio files.
- Manual user input: actual odds text area, my portfolio input text area, schedule search controls.

## Processing Flow

1. Runtime bootstrap initializes Streamlit page config and session state.
2. Schedule page loads schedule data and sets selected fixture through `open_fixture`.
3. Analysis page parses selected match text, resolves fixture context, and loads data sources.
4. Odds and market processing combine API-Football, API-Football, Polymarket, actual user odds, and market summaries.
5. Analysis pipeline builds match context, result distribution, value analysis, decision engine output, betting opinion, score suggestions, and risk notes.
6. Portfolio pipeline builds market candidates, recommendation slots, strategy libraries, allocation variants, strategy comparison rows, and visible metadata.
7. UI renders overview cards, market tabs, strategy ranking, actual odds comparison, my portfolio input, advanced research, and data source notes.
8. Post-match page loads snapshots and saved portfolios, settles outcomes, and renders audit/settlement tables.

## Where Odds Are Computed

- Imported odds clients: `modules.odds_client`, `removed legacy odds client`, `modules.polymarket_client`.
- In-file odds helpers: `market_odds_overview_rows`, `actual_odds_completeness`, `actual_odds_completeness_for_match`, `render_actual_odds_input`, `current_actual_odds`, `portfolio_market_candidates`, and `render_actual_market_odds_summary`.
- User odds parsing and enrichment are delegated to `modules.user_odds`, but UI/cache and some matching remain in `app.py`.

## Where Portfolio Decisions Are Made

- Imported portfolio helpers: `modules.portfolio_engine` functions including `compute_portfolio_score`, `portfolio_risk_gate`, `rank1_eligibility_check`, and settlement helpers.
- In-file portfolio construction/scoring helpers: `portfolio_metrics`, `optimizer_asset_pool`, `evaluate_allocation`, `optimize_betting_portfolio`, `build_strategy_library`, `build_auto_optimized_strategy`, `strategy_score`, `evaluate_strategy`, `strategy_comparison`, and `render_portfolio_ranking`.
- My Portfolio parsing and display: `parse_my_portfolio`, `render_my_portfolio_input`, `render_my_portfolio_settlement`, `evaluated_my_portfolio_strategy`.

## Where Strategy Logic Is Applied

- Imported strategy/decision helpers: `build_betting_opinion`, `build_decision_engine`, `attach_shadow_metadata`, `traffic_light`.
- In-file strategy helpers: `strategy_item_groups`, `main_path_correct_scores`, `strategy_direction_alignment`, `strategy_path_consistency`, `strategy_strategic_value`, `strategy_conclusion`, `match_betting_score`, `recommended_stake_mvp`, and hybrid v0.2 metadata helpers.

## Output Rendering

- Streamlit UI: all `render_*` functions and runtime bootstrap.
- Reports/export: `build_report`, `save_report`, `render_detail_data_source`, and `scripts/validate_report_exports.py` outside `app.py`.
- Persisted snapshots: `save_match_snapshot`, `save_post_match_snapshot`, `save_my_portfolio`, and performance database update helpers.

## Data Flow Risks For Future Extraction

- `app.py` uses Streamlit session state directly throughout the runtime path.
- Portfolio and strategy helpers share dict-shaped structures without explicit schemas.
- Odds matching depends on text normalization and line parsing across `app.py`, `modules.user_odds`, `modules.market_utils`, and `modules.portfolio_engine`.
- Post-match audit reuses pre-match structures, so extraction must preserve snapshot shape compatibility.
