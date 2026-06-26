# Entry Points

This report identifies current entry points only. No entry point was changed.

## runtime entry

- `app.py`
  - Primary Streamlit runtime file.
  - `scripts/run_streamlit_8502.sh` runs `streamlit run app.py`.
  - `scripts/start_streamlit_8502.command` runs `python -m streamlit run app.py`.
  - `START_APP.command` is a user-facing app launcher.

## UI entry

- `app.py`
  - Imports Streamlit directly.
  - Configures page state at the bottom of the file.
  - Routes between schedule, analysis, and post-match views.
  - Current UI, orchestration, and some display-specific decision formatting are still colocated.

## data pipeline entry

- `scripts/refresh_api_data.py`
- `scripts/refresh_today_odds.py`
- `scripts/refresh_match_prematch_snapshot.py`
- `scripts/build_worldcup_data_center.py`
- `scripts/build_worldcup_index.py`

## backtest and validation entry

- `scripts/backtest_portfolio_engine.py`
- `scripts/backtest_attribution.py`
- `scripts/generate_post_match_validation_report.py`
- `scripts/generate_hybrid_ranking_report.py`
- `scripts/generate_hybrid_v2_report_only.py`
- `scripts/generate_world_cup_backfill_benchmark.py`
- `scripts/test_portfolio_engine.py`

## reporting and maintenance entry

- `scripts/validate_report_exports.py`
- `scripts/performance_report.py`
- `scripts/update_gpt_context.py`
- `test_api.py`

## Entry Point Risk Notes

- `app.py` is the main runtime and UI entry, and is also the largest coupling point.
- Data refresh scripts call modules directly and should remain unchanged until a dedicated data-pipeline refactor is approved.
- Backtest scripts read historical data and should stay isolated from production runtime behavior.
