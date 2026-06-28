# UI-CACHE-API Protocol

This document defines the current UI-CACHE-API route and boundaries.

## Phase Purpose

The UI-CACHE-API phase improves freshness visibility, refresh safety, cache behavior, and Streamlit load behavior without changing recommendation logic.

Current hard gates:

- `PORTFOLIO_EXTRACTION: BLOCKED`.
- `BACKTEST_READY: NO`.

## Completed Route So Far

1. Data Freshness / Refresh Status panel.
2. Refresh status layer.
3. Runtime refresh status moved to ignored `.runtime/ui_refresh_status.json`.
4. Stable tracked sample at `reports/samples/ui_refresh_status.sample.json`.
5. API-Football key readiness gate.
6. Controlled one-time API-Football refresh.

Task 5 completion note:

- Branch: `codex/ui-cache-api-api-football-one-time-refresh`.
- Final head: `7f447bbad9e70caaf9b0779bf214e0f6f26f21cd`.
- API call: exactly one `GET /fixtures?id=1489393`.
- Wrote ignored runtime artifacts plus tracked reports/docs/scripts.
- Claude Round 14 verdict: `PASS`.

## Current Route

1. Freshness panel.
2. Refresh status layer.
3. API-Football key readiness gate.
4. Controlled one-time API-Football refresh.
5. Dry-run refresh button.
6. Refresh log viewer.
7. Static metadata cache.
8. Streamlit loading optimization.

Do not skip into model upgrade, portfolio extraction, backtest enablement, or ranking changes while this route is active.

## Forbidden Areas For This Phase

Do not modify unless explicitly approved:

- Recommendation logic.
- Ranking logic.
- Portfolio logic.
- Strategy logic.
- Odds calculation or settlement logic.
- Backtest.
- `modules/ranking`.
- `modules/portfolio`.
- `modules/strategy`.
- `modules/backtest`.
- `data/history`.
- Golden JSON.
- `main-clean`.

## API-Football-Only Policy

- API-Football is the only keyed API target for this phase.
- `API_FOOTBALL_KEY` may be checked only by present/missing state.
- The key value must never be printed, committed, or included in reports.
- API-Football is disabled and not required.
- `API_FOOTBALL_KEY` must not block current UI-CACHE-API work.
- Polymarket remains public-only and is not part of API refresh tasks unless explicitly scoped.
- WorldCup2026 schedule API is public and separate.

## Runtime And Cache File Policy

- Runtime refresh status path: `.runtime/ui_refresh_status.json`.
- Task-specific runtime refresh artifacts should stay under `.runtime/`.
- `.runtime/` must remain ignored.
- Tracked sample path: `reports/samples/ui_refresh_status.sample.json`.
- Tracked sample JSON must be stable and must not contain generated runtime timestamps.
- Runtime outputs should not dirty tracked Git status.
- Do not commit raw API payloads unless a human explicitly approves a safe fixture.
- Do not write generated match snapshots to `data/history` during this phase.

## Freshness Panel Policy

The Data Freshness / Refresh Status panel may show:

- Refresh mode.
- API provider policy.
- API-Football key present/missing.
- Controlled refresh ready/completed/failed state.
- API call count.
- Last API refresh time.
- Status file path.
- Files written.
- Warnings.

The panel must not:

- Trigger real API calls.
- Add auto-refresh.
- Add a real refresh button without explicit scope.
- Claim system-wide market freshness from one bounded API call.
- Hide stale-data warnings.

## Local Streamlit 8501 Testing Protocol

For UI validation:

1. Confirm repo path and branch.
2. Confirm Git status.
3. Stop old Streamlit processes only if safe.
4. Check ports `8501-8505`.
5. Start Streamlit locked to `http://localhost:8501`.
6. Confirm page loads.
7. Confirm the Data Freshness / Refresh Status panel appears before Portfolio Ranking, Match Investment Score, and Recommended Stake.
8. Report layout issues.
9. Do not run refresh buttons or real API calls unless explicitly approved.

## Next Task Constraints

- A dry-run refresh button must be dry-run-only unless a human explicitly scopes a real call.
- A refresh log viewer should read local reports/runtime metadata only.
- Static metadata cache work must not mutate recommendation outputs.
- Loading optimization must preserve current behavior and avoid hidden API calls.
