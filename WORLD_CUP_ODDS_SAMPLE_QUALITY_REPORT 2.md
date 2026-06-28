# World Cup Odds Sample Quality Report

Date: 2026-06-21

Scope: Phase A quality check only. This report checks three sample matches and does not write backfill data, create `data/history/backfill/`, generate benchmark portfolios, modify `app.py`, modify ranking, modify recommendation logic, modify UI, commit, or push.

## Executive Verdict

Phase B Ready.

Reason:

- All 3 sample matches were found through official API-Football fixture IDs.
- All 4 required markets were available for every sample:
  - Match Winner.
  - Asian Handicap.
  - Over/Under.
  - Correct Score.
- Every sampled market had `odds update timestamp < kickoff timestamp`.
- API-Football provider coverage was strong across all markets.

Phase B should still remain limited to 10 completed matches and write only to the isolated `data/history/backfill/` directory.

## Sample Summary

| Match | Type | Fixture ID | Quality Score | Data Quality | Historical Benchmark |
| --- | --- | ---: | ---: | --- | --- |
| Germany vs Ivory Coast | Strong favorite / deep handicap | 1489393 | 96 / 100 | `true_pre_match` | Suitable |
| Scotland vs Morocco | Balanced match | 1489390 | 96 / 100 | `true_pre_match` | Suitable |
| Brazil vs Haiti | Upset-risk / crowded favorite | 1489389 | 94 / 100 | `true_pre_match` | Suitable |

Quality score rationale:

- 40 points: all required markets available.
- 40 points: all market update timestamps are before kickoff.
- 15 points: API-Football provider count is strong.
- 5 points: fixture identity is confirmed by official API-Football fixture list.

Brazil vs Haiti receives 94 instead of 96 because odds were updated 22 minutes before kickoff, which is valid and useful but should be watched for last-minute market movement sensitivity.

## Match 1: Germany vs Ivory Coast

Match type: Strong favorite / deep handicap.

- Official API-Football fixture ID: `1489393`.
- Kickoff timestamp: `2026-06-20T20:00:00+00:00`.
- Final score from API-Football fixture check: Germany 2-1 Ivory Coast.
- Data quality: `true_pre_match`.
- Historical Benchmark eligibility: Suitable.

| Market | Available | Odds Update Timestamp | Kickoff Timestamp | update < kickoff | API-Football Provider Count | Market Quality |
| --- | --- | --- | --- | --- | ---: | --- |
| Match Winner | Yes | `2026-06-20T18:00:19+00:00` | `2026-06-20T20:00:00+00:00` | Yes | 14 | `available_true_pre_match` |
| Asian Handicap | Yes | `2026-06-20T18:00:19+00:00` | `2026-06-20T20:00:00+00:00` | Yes | 11 | `available_true_pre_match` |
| Over/Under | Yes | `2026-06-20T18:00:19+00:00` | `2026-06-20T20:00:00+00:00` | Yes | 12 | `available_true_pre_match` |
| Correct Score | Yes | `2026-06-20T18:00:19+00:00` | `2026-06-20T20:00:00+00:00` | Yes | 13 | `available_true_pre_match` |

Missing markets: None.

Verdict:

```text
true_pre_match
```

## Match 2: Scotland vs Morocco

Match type: Balanced match.

- Official API-Football fixture ID: `1489390`.
- Kickoff timestamp: `2026-06-19T22:00:00+00:00`.
- Final score from API-Football fixture check: Scotland 0-1 Morocco.
- Data quality: `true_pre_match`.
- Historical Benchmark eligibility: Suitable.

| Market | Available | Odds Update Timestamp | Kickoff Timestamp | update < kickoff | API-Football Provider Count | Market Quality |
| --- | --- | --- | --- | --- | ---: | --- |
| Match Winner | Yes | `2026-06-19T20:07:20+00:00` | `2026-06-19T22:00:00+00:00` | Yes | 14 | `available_true_pre_match` |
| Asian Handicap | Yes | `2026-06-19T20:07:20+00:00` | `2026-06-19T22:00:00+00:00` | Yes | 11 | `available_true_pre_match` |
| Over/Under | Yes | `2026-06-19T20:07:20+00:00` | `2026-06-19T22:00:00+00:00` | Yes | 12 | `available_true_pre_match` |
| Correct Score | Yes | `2026-06-19T20:07:20+00:00` | `2026-06-19T22:00:00+00:00` | Yes | 13 | `available_true_pre_match` |

Missing markets: None.

Verdict:

```text
true_pre_match
```

## Match 3: Brazil vs Haiti

Match type: Upset-risk / crowded favorite.

- Official API-Football fixture ID: `1489389`.
- Kickoff timestamp: `2026-06-20T00:30:00+00:00`.
- Final score from API-Football fixture check: Brazil 3-0 Haiti.
- Data quality: `true_pre_match`.
- Historical Benchmark eligibility: Suitable.

| Market | Available | Odds Update Timestamp | Kickoff Timestamp | update < kickoff | API-Football Provider Count | Market Quality |
| --- | --- | --- | --- | --- | ---: | --- |
| Match Winner | Yes | `2026-06-20T00:07:25+00:00` | `2026-06-20T00:30:00+00:00` | Yes | 14 | `available_true_pre_match` |
| Asian Handicap | Yes | `2026-06-20T00:07:25+00:00` | `2026-06-20T00:30:00+00:00` | Yes | 11 | `available_true_pre_match` |
| Over/Under | Yes | `2026-06-20T00:07:25+00:00` | `2026-06-20T00:30:00+00:00` | Yes | 12 | `available_true_pre_match` |
| Correct Score | Yes | `2026-06-20T00:07:25+00:00` | `2026-06-20T00:30:00+00:00` | Yes | 13 | `available_true_pre_match` |

Missing markets: None.

Verdict:

```text
true_pre_match
```

Watch note:

- Odds update is only 22 minutes before kickoff.
- This is valid for a closing pre-match benchmark, but Phase B should record this as close-to-kickoff data rather than early opening odds.

## Cross-Sample Quality Findings

| Check | Result |
| --- | --- |
| Official fixture ID mapping works | Yes |
| Match Winner available | 3 / 3 |
| Asian Handicap available | 3 / 3 |
| Over/Under available | 3 / 3 |
| Correct Score available | 3 / 3 |
| All updates before kickoff | 12 / 12 markets |
| Any missing markets | No |
| Any invalid post-kickoff odds | No |
| Any benchmark blockers | No |

## Historical Benchmark Readiness

Phase B readiness decision:

```text
Phase B Ready
```

Allowed next step:

- Backfill 10 completed matches into `data/history/backfill/`.
- Keep all backfilled files isolated from existing `data/history/` snapshots.
- Generate a limited benchmark only after those 10 snapshots pass the same quality checks.

Required Phase B controls:

- Do not overwrite existing `data/history/*_pre.json`.
- Do not overwrite existing `data/history/*_post.json`.
- Do not overwrite `data/history/my_portfolios/*.json`.
- Every backfilled snapshot must include:
  - `source = api_football_backfill`
  - `is_backfill = true`
  - `is_true_pre_match`
  - `odds_timestamp`
  - `kickoff_time`
  - `data_quality`
  - `available_markets`
- Deduplicate by match, not by snapshot.

## Safety Confirmation

- Backfill data written: No.
- `data/history/backfill/` created: No.
- Benchmark generated: No.
- `app.py` modified: No.
- Ranking modified: No.
- Recommendation logic modified: No.
- UI modified: No.
- Git commit or push: No.

