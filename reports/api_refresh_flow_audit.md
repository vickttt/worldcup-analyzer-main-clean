# API Refresh Flow Audit

Date: 2026-06-28

Scope: read-only audit of API-Football and refresh-status flow.

## API Provider Boundaries

- Current keyed provider: API-Football only.
- The Odds API is disabled for the current UI-CACHE-API phase.
- Polymarket is public-only and not part of controlled API refresh work.
- WorldCup2026 schedule API is public and separate from keyed API-Football refresh.

## Refresh Status Flow

- Runtime status path: `.runtime/ui_refresh_status.json`.
- Stable sample path: `reports/samples/ui_refresh_status.sample.json`.
- `load_refresh_status_report()` reads runtime status first.
- If runtime status is absent, the app reads the sample status.
- `apply_api_football_readiness(...)` enriches status with redacted key readiness and provider policy.
- The UI displays present/missing key state, never key values.

## Controlled API-Football Refresh

- Script: `scripts/run_api_football_refresh_once.py`.
- Gate report path: `reports/api_football_refresh_gate.md`.
- Runtime payloads are written under `.runtime/api_football_refresh/`.
- The script has marker protection to prevent repeated uncontrolled refresh.
- The Streamlit panel displays metadata but does not execute the controlled refresh.

## Dry-Run Status Flow

- Script: `scripts/write_refresh_status_dry_run.py`.
- Writes local-only status to `.runtime/ui_refresh_status.json`.
- Does not make API calls.
- Reports API-Football key present/missing state only.

## Potential Fragility

- The runtime status and sample status share a display path but have different evidence strength.
- Manual schedule refresh and controlled API-Football refresh are distinct concepts; UI copy must keep them separate.
- API-Football match data functions still exist in runtime detail loading, so future UI changes must avoid accidentally creating live refresh loops.

## No-Action Confirmation

- No API call was made.
- No `.runtime/` file was written.
- No `.env` or secret file was read or printed.
- No workflow was triggered.
