# Streamlit Load Flow Map

Date: 2026-06-28

Scope: read-only mapping of Streamlit load and rerun behavior.

## Entry

- `load_config()` reads `config.yaml`.
- `st.set_page_config(...)` initializes wide layout.
- `st.session_state.page` controls routing:
  - `schedule`
  - `analysis`
  - `post_match`

## Schedule Page Flow

1. User lands on `schedule`.
2. Optional "刷新赛程状态" button clears `fetch_world_cup_schedule` cache.
3. `fetch_world_cup_schedule(force_refresh=...)` loads schedule.
4. UI renders:
   - portal banner
   - search
   - date navigation
   - standings
   - tournament stats
   - optional full schedule
   - cache notes

## Analysis Page Flow

1. User opens a fixture from schedule.
2. `parse_match(match_text)` creates the match object.
3. `refresh_selected_fixture_if_needed(...)` may update session state if a fixture status changed.
4. `load_match_database(..., full=False)` tries local saved data first.
5. If local data exists:
   - `db_api_football_data(local_db)`
   - `db_odds(local_db)`
   - `db_polymarket(local_db)`
6. If local data is missing:
   - `fetch_match_data(...)`
   - `fetch_odds(...)`
   - `fetch_polymarket(...)`
7. Base models and UI payloads are built:
   - probabilities
   - score recommendations
   - rating
   - value analysis
   - betting opinion
   - result distribution
   - decision engine
   - portfolio candidates
   - report content
8. Tabs render:
   - core
   - team
   - market
   - post
   - source

## Rerun Triggers

- Schedule refresh button.
- Opening a match.
- Returning to schedule.
- User odds form actions.
- Portfolio form actions.
- Date navigation buttons.
- Some fixture status transitions.

## Performance Notes

- Homepage is relatively bounded because expensive full schedule rendering is behind a checkbox.
- Detail page is much heavier because data loading, recommendation payloads, portfolio ranking, and report generation are assembled in one request path.
- Existing `perf_timer` coverage is useful and should be preserved.
- A future optimization should target detail-page derived payload caching, not ranking or portfolio behavior changes.

## No-Action Confirmation

- No Streamlit server was started.
- No browser smoke test was run.
- No product code changed.
