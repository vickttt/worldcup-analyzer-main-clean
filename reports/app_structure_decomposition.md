# app.py Structure Decomposition

This report maps `app.py` responsibilities for future extraction. No runtime code was changed.

## Summary

- `app.py` is 7079 lines and remains the runtime Streamlit entry point.
- It mixes UI rendering, route orchestration, market data assembly, odds input parsing, portfolio scoring/ranking display, strategy explanations, and post-match audit views.
- Existing domain modules already contain some business logic, but `app.py` still includes many helper functions that should eventually move behind module boundaries.

## Section Breakdown

| Lines | Section | Purpose | Estimated target |
|---:|---|---|---|
| 1-104 | `imports_config_globals` | Imports, version metadata, and configuration constants. | `ui/data` |
| 107-170 | `formatting_basic_helpers` | Formatting, parsing, flags, and small display utilities. | `ui` |
| 173-690 | `styling_and_team_display` | CSS, card display, market consensus, team display helpers. | `ui` |
| 702-785 | `fixture_selection_state` | Fixture conversion, identity checks, refresh routing, date keys. | `data/ui` |
| 788-998 | `debug_and_match_overview_ui` | Debug panels, safe market sections, match overview, betting opinion rendering. | `ui/strategy` |
| 1001-1205 | `decision_result_combo_ui` | Decision engine rendering, result distribution, extreme scenarios, staking display. | `ui/analysis/strategy` |
| 1208-1913 | `portfolio_metrics_and_detail_helpers` | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | `portfolio/ui` |
| 1916-2293 | `score_distribution_optimizer` | Bet identity, score probability, return matrix, allocation optimization. | `portfolio/strategy/analysis` |
| 2296-2870 | `settlement_and_audit` | Outcome settlement, prediction audit, performance persistence, model error summaries. | `backtest/portfolio/strategy` |
| 2873-3823 | `strategy_library_and_ranking` | Strategy construction, scoring, comparison, frontier, conclusion helpers. | `strategy/portfolio` |
| 3826-4691 | `actual_odds_and_manual_portfolio_input` | Rating breakdown, actual odds cache, history paths, manual portfolio parsing/input. | `odds/data/ui` |
| 4694-5508 | `portfolio_ranking_and_decision_cards` | My portfolio settlement, duplicate display, ranking rows, hybrid metadata, decision cards. | `portfolio/strategy/ui` |
| 5511-6224 | `match_analysis_tabs` | Path layers, market consensus, qualification behavior, team/market/risk render sections. | `analysis/odds/ui` |
| 6227-6385 | `post_match_and_technical_tabs` | Post-match audit UI, injuries, lineups, technical notes. | `backtest/ui/data` |
| 6388-6835 | `schedule_portal` | Schedule cards, search, date navigation, standings, teams, tournament info. | `ui/data` |
| 6838-7051 | `page_orchestration` | Analysis page and post-match page orchestration. | `ui/data/strategy/portfolio` |
| 7054-7079 | `runtime_bootstrap` | Config load, Streamlit page setup, session state, route dispatch. | `ui` |

## Extraction Boundary Notes

- UI rendering sections should eventually move to `modules/ui/`, but only after tests or snapshot comparisons protect behavior.
- Odds and manual portfolio parsing currently sit partly in `app.py` and partly in `modules/user_odds.py`; later extraction should avoid changing matching semantics.
- Portfolio ranking helpers from lines 1208-3823 include sensitive scoring and allocation functions; these must be treated as protected logic.
- Page orchestration and runtime bootstrap should be split last because they are the active Streamlit entry surface.
