# API-Football Historical Odds Check

Date: 2026-06-21

Scope: task one only. This report checks whether the current API-Football integration can support historical pre-match odds backfill. It does not write backfill code, pull full historical data, modify `app.py`, modify ranking logic, modify UI, overwrite snapshots, delete files, commit, or push.

## Executive Verdict

API-Football can return odds for past match dates through the `/odds` endpoint when queried by `date`, `league`, `season`, and `bet`.

However, this should be treated as a conditional historical pre-match odds source, not a guaranteed full historical odds archive.

Backfill is feasible only if each returned odds row passes this validation:

```text
odds update timestamp < kickoff timestamp
```

If `update >= kickoff`, or if no `update` timestamp exists, that odds record must be marked:

```text
is_true_pre_match = false
not valid for strict historical backtest
```

## API Capability Summary

### Supported Markets

The current API-Football odds mapping confirms these bet IDs:

| Required Market | API-Football Bet ID | API Name |
| --- | ---: | --- |
| Match Winner | 1 | Match Winner |
| Asian Handicap | 4 | Asian Handicap |
| Over/Under | 5 | Goals Over/Under |
| Correct Score | 10 | Exact Score |

This means the required market categories are available in the API taxonomy.

### Endpoint Behavior Observed

Current project code uses:

```text
GET /odds
```

with parameters such as:

```text
fixture
date
league
season
bet
```

Existing project functions:

- `modules/odds_client.py`
- `scripts/refresh_today_odds.py`

already use `/odds` for API-Football market pulls.

## Probe Results

### Fixture-Based Historical Query

Probed ended fixture IDs from local history and API-style local snapshots.

Result:

| Query Type | Result |
| --- | --- |
| Local small fixture IDs, e.g. `33`, `34`, `35` | 0 odds rows |
| Local API-style fixture IDs, e.g. `760442`-`760445` | 0 odds rows |

Interpretation:

- Existing local fixture IDs are not reliable for historical API-Football odds backfill.
- A backfill pipeline must first fetch the official API-Football World Cup fixture list and use the API-returned fixture IDs.
- Do not assume current local `fixture_id` values can directly backfill odds.

### Date-Based Historical Query

Probed:

```text
GET /odds?date=<date>&league=1&season=2026&bet=1
```

Observed World Cup odds rows:

| Date | Items Returned | Example Fixture IDs / Update Times |
| --- | ---: | --- |
| 2026-06-16 | 3 | `1489378`, `1489383`, `1539016` |
| 2026-06-17 | 5 | `1489381`, `1489382`, `1489384`, `1489385`, `1539003` |
| 2026-06-18 | 4 | `1489386`, `1489387`, `1539004`, `1539005` |
| 2026-06-19 | 3 | `1489388`, `1489390`, `1489391` |
| 2026-06-20 | 4 | `1489389`, `1489393`, `1539006`, `1539007` |
| 2026-06-21 | 5 | `1489392`, `1489394`, `1489395`, `1489397`, `1489398` |

Sample row structure included:

```text
fixture_id = 1489389
fixture date = 2026-06-20T00:30:00+00:00
league_id = 1
league_name = World Cup
season = 2026
update = 2026-06-20T00:07:25+00:00
api_football_providers = 14
```

This sample update is before kickoff, so it can be treated as a candidate true pre-match odds snapshot.

## Historical Backtest Suitability

### Can API-Football Support Historical Odds Backfill?

Yes, with conditions.

The API can return odds for past dates and World Cup season filters. The returned odds include an `update` timestamp that can be compared against kickoff.

### Can It Prove True Pre-Match Odds?

Only per row.

Each row must satisfy:

```text
update < fixture.date
```

If this is true, mark:

```text
is_true_pre_match = true
```

If false or missing, mark:

```text
is_true_pre_match = false
data_quality = not_valid_for_strict_backtest
```

### Can It Retrieve All Needed Markets?

Likely yes, but must be verified per fixture and per bet:

- Match Winner: `bet=1`
- Asian Handicap: `bet=4`
- Goals Over/Under: `bet=5`
- Exact Score / Correct Score: `bet=10`

Backfill should not assume every fixture has every market. Missing markets should degrade snapshot quality instead of blocking the entire fixture.

## Key Limitation

API-Football `/odds` appears to return the available stored odds snapshot for a fixture/date, not a full odds movement timeline.

Therefore it should not be described as:

```text
full historical line movement
opening odds archive
closing odds archive
```

It should be described as:

```text
historical odds row with API update timestamp
```

The backtest must use `odds_timestamp` and `kickoff_time` to decide whether the odds were genuinely pre-match.

## Backfill Feasibility Decision

Proceed to design Backfill Pipeline, but with strict data-quality labels.

Recommended labels:

| Field | Meaning |
| --- | --- |
| `source` | `api_football_backfill` |
| `odds_timestamp` | API `update` field |
| `kickoff_time` | API fixture date |
| `is_true_pre_match` | `true` only when `odds_timestamp < kickoff_time` |
| `data_quality` | `true_pre_match`, `missing_market`, `post_kickoff_odds`, `missing_timestamp`, `unusable` |
| `market_coverage` | Which of Match Winner / Asian Handicap / Over-Under / Exact Score were returned |

## Required Next Checks Before Full Backfill

Before writing a full backfill script:

1. Fetch official API-Football fixtures for `league=1`, `season=2026`.
2. Build a fixture ID mapping from API-Football, not from existing local fixture IDs.
3. For each fixture, query odds by official `fixture_id` or date+league+season page results.
4. For each returned odds row, compare `update` against kickoff.
5. Mark every market and fixture with explicit `data_quality`.
6. Store all backfilled snapshots only under an isolated path such as:

```text
data/history/backfill/<match_slug>_pre.json
```

7. Never overwrite existing hand-made `data/history/*_pre.json` snapshots.

## Safety Verdict

- Backfill code written: No.
- Full data pulled: No.
- Existing snapshots overwritten: No.
- Data files modified: No.
- App code modified: No.
- Ranking logic modified: No.
- UI modified: No.
- Git commit or push: No.

