# Cache Opportunity Map

Date: 2026-06-28

Scope: read-only cache behavior and optimization opportunity map.

## Existing Cache Layers

| Area | Current cache mechanism | TTL / freshness |
| --- | --- | --- |
| Schedule | `st.cache_data` plus `data/cache/worldcup_schedule_cache.json` | live-aware, up to 24h for non-live schedule |
| API-Football fixture lookup | `st.cache_data` plus `fixture_cache.json` | match/team TTL from config |
| API-Football market odds | `st.cache_data` plus file cache | 48h market TTL |
| Correct score | `st.cache_data` plus file cache | 48h |
| Standings | `st.cache_data` plus file cache | schedule TTL |
| Team ID resolver | `st.cache_data` plus `team_id_cache.json` | 30 days |
| Team profile | `st.cache_data` | 7 days |
| The Odds API | `st.cache_data` plus daily file cache | 24h |
| Polymarket | client-level cache path, public market source | 30 minutes by config |
| User odds / portfolio | JSON under `data/history` | user-generated persistence |

## Opportunity Areas

### 1. Detail-page derived payload cache

The detail page recomputes many derived payloads after data loading:

- probabilities
- scores
- value analysis
- betting opinion
- result distribution
- decision engine
- portfolio candidates
- report payload

Future optimization can cache the derived read-only bundle keyed by match, fixture id, local DB timestamp, and user odds state.

### 2. Freshness contract consolidation

The app currently tracks:

- local data freshness
- runtime refresh status
- sample refresh status
- API-Football readiness
- cache TTLs

A future low-risk improvement should define a single display contract for these fields without changing recommendation logic.

### 3. API fan-out guard

`fetch_match_data()` can call several API-Football endpoints when local DB is missing:

- fixture lookup
- correct score
- Asian handicap
- standings
- injuries
- lineups
- recent fixtures

Future work should add explicit audit visibility for which paths were cache hits versus API attempts.

### 4. Rerun-sensitive widgets

Forms and buttons call `st.rerun()` after updates. Future UI work can reduce unnecessary recomputation by isolating user-input state from market-data state.

## Must Not Change Yet

- Ranking behavior.
- Portfolio behavior.
- Strategy scoring.
- Odds calculation or settlement.
- Backtest behavior.
- Golden JSON fixtures.
- `data/history` semantics.

## Recommended Next Step

Prepare an implementation proposal for a read-only "cache and fetch diagnostics panel" that displays cache hit/miss metadata without changing runtime data fetch behavior.
