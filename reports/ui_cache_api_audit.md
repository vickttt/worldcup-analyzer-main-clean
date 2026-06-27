# UI-CACHE-API Audit

Date: 2026-06-28

Branch: `dev-clean`

Scope: read-only audit for `NODE 1 - UI-CACHE-API AUDIT`.

## Summary

- Product code modified: No.
- API calls performed: No.
- Streamlit app executed: No.
- Audit method: static source review only.

## Current Flow

- The app starts from `app.py` and routes by `st.session_state.page`.
- Schedule page calls `render_schedule_page()`.
- Detail page calls `render_analysis_page(match_text)`.
- Post-match page calls `render_post_match_page(fixture)`.
- Refresh visibility is rendered by `render_data_freshness_panel(freshness)`.

## Main UI-CACHE-API Observations

### UI load flow

- `render_schedule_page()` wraps major homepage blocks in `perf_timer` scopes.
- Schedule loading is centralized through `fetch_world_cup_schedule(force_refresh=False)`.
- The schedule refresh button clears Streamlit cache and reruns the page.
- Detail page is heavier: it loads local DB or falls back to multiple API/cache-backed calls, then computes decision, portfolio candidates, report content, and multiple tabs.

### API refresh flow

- Runtime refresh status is read from `.runtime/ui_refresh_status.json`.
- If runtime status is missing, the app falls back to `reports/samples/ui_refresh_status.sample.json`.
- The UI refresh panel does not trigger a real API call.
- Controlled one-time API-Football refresh is handled by `scripts/run_api_football_refresh_once.py`, not by the Streamlit page.

### Cache behavior

- Schedule cache uses `modules/schedule_client.py` and `data/cache/worldcup_schedule_cache.json`.
- API-Football market, fixture, standings, team, and recent-form calls are protected by `st.cache_data` plus file caches in several paths.
- The app still has many cache layers with different TTLs, making freshness easy to display but harder to reason about globally.

### Page performance bottlenecks

- Detail page is the main bottleneck because it combines data loading, model computation, portfolio construction, report generation, and rendering in one pass.
- `fetch_match_data()` may fan out to fixture lookup, correct score, Asian handicap, standings, injuries, lineups, and recent fixtures.
- `fetch_odds()` and `fetch_polymarket()` are separate from API-Football match data and can add more fetch/cache paths.
- Full schedule rendering is gated behind a checkbox, which is good for homepage load.

## Risks

- The detail page can recompute portfolio and report structures on every rerun even when only UI state changes.
- Refresh state and freshness state are adjacent but not a single contract; this can make user-facing freshness interpretation conservative but fragmented.
- Schedule refresh is still a UI button that can clear cache and rerun; it is not the same as keyed API-Football refresh, but the distinction needs to remain clear.

## Recommended Next Improvements

- Add a read-only performance map before changing any code.
- Separate "data availability", "runtime refresh status", and "market freshness" in the UI contract.
- Consider caching derived detail-page payloads after a future approved implementation task.
- Keep real API refresh outside Streamlit unless explicitly approved.

## Gate Status

- `PORTFOLIO_EXTRACTION`: `BLOCKED`.
- `BACKTEST_READY`: `NO`.
- Next recommended node: `NODE 2 - MODEL-DESIGN ANALYSIS` suggestion only.
- Auto-advance: No.
