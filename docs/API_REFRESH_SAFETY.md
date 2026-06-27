# API Refresh Safety

This document defines API, secret, runtime, and failure-safety rules for World Cup Analyzer refresh work.

## Secret Policy

- Never print `.env`.
- Never print API key values.
- Never commit `.env`, `.env.*`, `*.env`, or `.streamlit/secrets.toml`.
- Show only key present/missing state.
- `.env` must be ignored by Git.
- `.streamlit/secrets.toml` must be ignored if used.
- Secret scans must run on changed tracked files before commit.

## Current API Policy

- Current keyed provider: API-Football only.
- Current key: `API_FOOTBALL_KEY`.
- The Odds API is disabled for the current UI-CACHE-API phase.
- `THE_ODDS_API_KEY` is not required and must not block API-Football readiness.
- Polymarket is public-only and not part of current API refresh work unless explicitly scoped.
- WorldCup2026 schedule API is public and separate.

## Real API Refresh Rules

A real API refresh must be:

- Explicitly approved.
- One-time.
- Bounded to a named endpoint and fixed parameter set.
- Logged with start and finish timestamps.
- Logged with provider, endpoint, parameters, call count, files written, and status.
- Protected from repeated loops.
- Failure-safe.

Do not run broad all-league, all-date, all-market, or repeated refresh loops.

## One-Time Bounded Refresh Gate

Before a real keyed API call:

1. Confirm branch and clean Git status.
2. Confirm `.env` and `.runtime/` are ignored.
3. Confirm key presence without printing value.
4. Identify endpoint/function.
5. Estimate API call count.
6. Identify files written.
7. Confirm no `data/history` write.
8. Confirm no golden JSON write.
9. Confirm no ranking, portfolio, strategy, odds, or backtest logic change.
10. Generate a gate report.

Task 5 precedent:

- Branch: `codex/ui-cache-api-api-football-one-time-refresh`.
- Final head: `7f447bbad9e70caaf9b0779bf214e0f6f26f21cd`.
- Endpoint: API-Football `GET /fixtures?id=1489393`.
- API calls: exactly `1`.
- Claude Round 14 verdict: `PASS`.

## Runtime Status

- Runtime status path: `.runtime/ui_refresh_status.json`.
- Tracked sample path: `reports/samples/ui_refresh_status.sample.json`.
- `.runtime/` must remain ignored.
- The sample file is documentation/reference only and must not be treated as real freshness evidence.

Runtime status should include when applicable:

- `api_provider_policy`.
- `api_football_key_present`.
- `real_api_refresh_performed`.
- `api_called`.
- `api_call_count`.
- `refresh_started_at`.
- `refresh_finished_at`.
- `status`.
- `files_written`.
- `warnings`.

## File Mutation Rules

- Runtime outputs go under ignored `.runtime/`.
- Stable samples may live under tracked `reports/samples/`.
- Audit reports may live under tracked `reports/`.
- Do not write generated match snapshots to `data/history` unless explicitly approved.
- Do not modify golden JSON unless explicitly approved.
- Do not mutate recommendation outputs as part of refresh work.

## Failure-Safe Behavior

On API failure:

- Do not retry repeatedly.
- Do not corrupt existing cache/runtime files.
- Write a failed status report if safe.
- Record the error without secrets.
- Preserve `data/history` and golden JSON.
- Keep UI wording conservative.
- Stop if secret exposure or unexpected writes are suspected.

## API Call Logging Requirements

Every real API refresh report must include:

- Branch.
- Script/function used.
- Provider.
- Endpoint and fixed parameters.
- Key present/missing state with value redacted.
- Call count.
- Start/end timestamp.
- Status.
- Files written.
- Whether files are ignored/tracked.
- Whether `data/history` and golden JSON were untouched.
- Whether recommendation/ranking/portfolio/strategy/odds/backtest logic was untouched.
- Failure details if any.
- Next safe task recommendation.
