# API-Football One-Time Refresh Gate

Generated before any Task 5 real API call.

## Gate Decision

- Branch: `codex/ui-cache-api-api-football-one-time-refresh`.
- API provider: API-Football only.
- Key present: `true`; value redacted.
- Key source: `dotenv`.
- The Odds API required: `false`.
- Polymarket refresh: `not used`.
- Real API call performed by this gate report: `false`.

## Planned Endpoint

- Function/script: `scripts/run_api_football_refresh_once.py --execute`.
- Endpoint: `GET https://v3.football.api-sports.io/fixtures`.
- Parameters: `id=1489393`.
- Estimated API calls: `1`.

## Why This Is Bounded

- The request targets one explicit fixture ID.
- The script has no loop and no retry path.
- A runtime marker blocks a second accidental execution unless a future task explicitly overrides it.
- The script does not call The Odds API, Polymarket, WorldCup2026 schedule APIs, or broad all-league/date endpoints.

## Files Written

- Ignored runtime API payload: `.runtime/api_football_refresh/fixture_1489393_status.json`.
- Ignored runtime one-time marker: `.runtime/api_football_refresh/one_time_refresh_marker.json`.
- Ignored UI status: `.runtime/ui_refresh_status.json`.
- Tracked audit report: `reports/api_football_one_time_refresh_report.md`.

## Protected Areas

- `data/history` will not be read or written by the script.
- Golden JSON will not be read or written by the script.
- Recommendation, ranking, portfolio, strategy, odds settlement, and backtest logic are not touched.
- No product model outputs are mutated.

## Secret Safety

- `API_FOOTBALL_KEY` is loaded from process environment, Streamlit secrets, or repo `.env`.
- The key value is used only in the request header.
- The script prints and records only present/missing state and source label, never the key value.
- `.env` remains ignored and must not be staged.
