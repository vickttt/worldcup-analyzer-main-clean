# Module Mapping v1

This report is a logical mapping only. No existing source files were moved, rewritten, or deleted.

## analysis

- `modules/game_behavior_engine.py`
- `modules/probability_model.py`
- `modules/rating_model.py`
- `modules/result_distribution.py`
- `modules/score_model.py`
- `modules/value_model.py`
- `scripts/generate_scenario_engine_report.py`
- `scripts/generate_scenario_engine_report 2.py`

## odds

- `modules/odds/core.py`
- `modules/market_utils.py`
- `modules/odds_client.py`
- `modules/polymarket_client.py`
- `removed legacy odds client`
- `modules/user_odds.py`
- `test_api.py`

## portfolio

- `modules/portfolio_engine.py`
- `scripts/test_portfolio_engine.py`

## strategy

- `modules/strategy/core.py`
- `modules/betting_opinion.py`
- `modules/decision_engine.py`
- `modules/shadow_metadata.py`
- `scripts/generate_shadow_metadata_report.py`
- `scripts/generate_shadow_metadata_report 2.py`

## backtest

- `scripts/backtest_attribution.py`
- `scripts/backtest_portfolio_engine.py`
- `scripts/generate_hybrid_ranking_report.py`
- `scripts/generate_hybrid_ranking_report 2.py`
- `scripts/generate_hybrid_v2_report_only.py`
- `scripts/generate_hybrid_v2_report_only 2.py`
- `scripts/generate_hybrid_v2_report_only 3.py`
- `scripts/generate_post_match_validation_report.py`
- `scripts/generate_post_match_validation_report 2.py`
- `scripts/generate_post_match_validation_report 3.py`
- `scripts/generate_world_cup_backfill_benchmark.py`
- `scripts/generate_world_cup_backfill_benchmark 2.py`

## data

- `modules/cache_config.py`
- `modules/match_parser.py`
- `modules/mock_data.py`
- `modules/perf_logger.py`
- `modules/pregame_content.py`
- `modules/schedule_client.py`
- `modules/team_profile_client.py`
- `modules/team_resolver.py`
- `modules/weather_client.py`
- `modules/worldcup_db.py`
- `scripts/build_worldcup_data_center.py`
- `scripts/build_worldcup_index.py`
- `scripts/performance_report.py`
- `scripts/refresh_api_data.py`
- `scripts/refresh_match_prematch_snapshot.py`
- `scripts/refresh_today_odds.py`
- `scripts/update_gpt_context.py`

## ui

- `app.py`
- `modules/report_generator.py`
- `scripts/validate_report_exports.py`
- `scripts/run_streamlit_8502.sh`
- `scripts/start_streamlit_8502.command`

## unknown

- `modules/__init__.py`
- `modules/analysis/__init__.py`
- `modules/odds/__init__.py`
- `modules/portfolio/__init__.py`
- `modules/strategy/__init__.py`
- `modules/backtest/__init__.py`
- `modules/data/__init__.py`
- `modules/ui/__init__.py`

## Manual Review Notes

- `modules/user_odds.py` belongs to odds parsing today, but it imports `modules.portfolio_engine` helpers; this should be split carefully in a later phase.
- `modules/pregame_content.py` is data/content support today, but some functions may become UI copy helpers later.
- Duplicate script files with suffixes such as ` 2.py` and ` 3.py` should be reviewed before any future move or deletion.
