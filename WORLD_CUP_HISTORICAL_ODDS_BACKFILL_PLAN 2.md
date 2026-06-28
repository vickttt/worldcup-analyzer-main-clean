# World Cup Historical Odds Backfill Plan

Date: 2026-06-21

Scope: design and readiness only. This plan does not implement backfill code, call full API pulls, write backfill data, modify `app.py`, modify `strategy_score(...)`, modify `evaluate_allocation(...)`, modify `strategy_comparison(...)`, modify UI, change recommendation logic, overwrite `data/history/`, commit, or push.

## 1. Data Goal

Backfill true pre-match odds snapshots for all completed 2026 World Cup matches where API-Football can provide usable odds.

Required markets:

- Match Winner.
- Asian Handicap.
- Over / Under.
- Correct Score.

API-Football market mapping confirmed by `API_FOOTBALL_HISTORICAL_ODDS_CHECK.md`:

| Market | API-Football Bet ID | API Name |
| --- | ---: | --- |
| Match Winner | 1 | Match Winner |
| Asian Handicap | 4 | Asian Handicap |
| Over / Under | 5 | Goals Over/Under |
| Correct Score | 10 | Exact Score |

Primary purpose:

```text
Create one high-quality pre-match odds snapshot per completed match, then benchmark Legacy Ranking, Scenario Ranking, and Hybrid Ranking against the final score.
```

## 2. Data Quality Rules

Every odds market row must record:

- `odds_source`
- `odds_update_timestamp`
- `kickoff_timestamp`
- `is_before_kickoff`
- `data_quality`

Strict rule:

```text
is_before_kickoff = odds_update_timestamp < kickoff_timestamp
```

If this condition is false, the odds row cannot be used for strict historical backtest.

Recommended quality labels:

| `data_quality` | Meaning | Benchmark Eligibility |
| --- | --- | --- |
| `true_pre_match` | Odds update exists and is before kickoff. | Eligible. |
| `questionable` | Timestamp exists but market coverage is incomplete, API-Football provider count is low, or kickoff mapping is uncertain. | Eligible only for sensitivity analysis, not primary benchmark. |
| `invalid` | Odds update is missing, after kickoff, or fixture mapping is unreliable. | Not eligible. |

Market-level status:

| Status | Meaning |
| --- | --- |
| `available_true_pre_match` | Market exists and update is before kickoff. |
| `available_questionable` | Market exists but quality is incomplete or uncertain. |
| `missing` | Market not returned for the fixture. |
| `invalid_post_kickoff` | Market update is at or after kickoff. |

Match-level quality:

```text
match.data_quality = minimum quality across required market coverage
```

Suggested primary benchmark eligibility:

- Match Winner must be `available_true_pre_match`.
- At least two of Asian Handicap / Over-Under / Correct Score must be `available_true_pre_match`.
- `odds_update_timestamp` must be before kickoff for all markets used in portfolio construction.
- Fixture identity must match home, away, date, and competition.

## 3. Save Path And Isolation

All backfilled snapshots must be stored under:

```text
data/history/backfill/
```

Per-match file path:

```text
data/history/backfill/<match_slug>_pre.json
```

Do not overwrite or edit:

```text
data/history/*_pre.json
data/history/*_post.json
data/history/my_portfolios/*.json
```

If a manually created snapshot already exists in `data/history/`, the backfilled snapshot remains separate and must include a pointer:

```json
{
  "manual_snapshot_reference": "data/history/<match_slug>_pre.json"
}
```

## 4. Backfill Snapshot Format

Each generated backfill snapshot should include:

```json
{
  "schema_version": 1,
  "snapshot_type": "pre_match_backfill",
  "source": "api_football_backfill",
  "is_backfill": true,
  "is_true_pre_match": true,
  "data_quality": "true_pre_match",
  "match_slug": "2026_06_20_Germany_Ivory_Coast",
  "match": {
    "home": "Germany",
    "away": "Ivory Coast",
    "display": "Germany vs Ivory Coast"
  },
  "fixture": {
    "api_football_fixture_id": 1489389,
    "league_id": 1,
    "season": 2026,
    "kickoff_time": "2026-06-20T00:30:00+00:00",
    "final_score_source": "api_football_fixture_result"
  },
  "odds_metadata": {
    "odds_source": "API-Football / Odds",
    "odds_timestamp": "2026-06-20T00:07:25+00:00",
    "kickoff_time": "2026-06-20T00:30:00+00:00",
    "is_before_kickoff": true,
    "available_markets": [
      "match_winner",
      "asian_handicap",
      "over_under",
      "correct_score"
    ],
    "missing_markets": [],
    "api_football_provider_count": 14
  },
  "markets": {
    "match_winner": {},
    "asian_handicap": {},
    "over_under": {},
    "correct_score": {}
  },
  "portfolio_inputs": {
    "legacy_ready": true,
    "scenario_ready": true,
    "hybrid_ready": true
  }
}
```

Required top-level fields:

- `source = api_football_backfill`
- `is_backfill = true`
- `is_true_pre_match = true / false`
- `odds_timestamp`
- `kickoff_time`
- `data_quality`
- `available_markets`

## 5. Backfill Pipeline Design

No implementation in this phase. Future implementation should follow this sequence:

```text
Official fixture list
↓
Completed-match filter
↓
Date / fixture odds query
↓
Market normalization
↓
Timestamp quality check
↓
Backfill snapshot write to data/history/backfill/
↓
Portfolio generation
↓
Post-match settlement
↓
Benchmark report
```

Required fixture source:

- Use official API-Football fixture IDs from `league=1`, `season=2026`.
- Do not rely on stale local fixture IDs.
- Match identity must be validated by home team, away team, kickoff date, league, and season.

Required odds query pattern:

```text
GET /odds?date=<YYYY-MM-DD>&league=1&season=2026&bet=<BET_ID>
```

or fixture-specific query only after official fixture IDs are confirmed:

```text
GET /odds?fixture=<official_api_football_fixture_id>&bet=<BET_ID>
```

## 6. Portfolio Generation Goal

For every valid backfill snapshot, generate:

- Legacy Top Portfolio.
- Scenario Top Portfolio.
- Hybrid Top Portfolio.
- Current Recommendation, if available from the generated portfolio set.
- My Portfolio, only if a matching historical user portfolio exists.

The backfilled benchmark must not use current UI state or current manually edited odds.

Portfolio generation should be deterministic from:

- backfilled odds snapshot,
- fixture metadata,
- existing portfolio construction logic,
- Scenario / Shadow / Hybrid metadata helpers.

Important safety rule:

```text
Portfolio generation for benchmark must not mutate production ranking order or app runtime behavior.
```

## 7. Post-Match Settlement Goal

Read final score for each completed match and settle:

- Legacy Top P/L.
- Scenario Top P/L.
- Hybrid Top P/L.
- ROI.
- Hit / Miss / Push.
- Max Drawdown.

Recommended settlement fields:

```json
{
  "portfolio_type": "Hybrid Top",
  "portfolio_name": "Example",
  "rank": 1,
  "hit_status": "hit",
  "profit_loss": 820,
  "roi": 0.41,
  "max_drawdown": 0,
  "settled_assets": []
}
```

Settlement should reuse the same asset outcome rules already used by post-match validation where possible, but in a separate benchmark script/report path.

## 8. Benchmark Output

Primary report:

```text
WORLD_CUP_RANKING_BENCHMARK_REPORT.md
```

Required report sections:

1. Scope and safety boundaries.
2. Data quality summary.
3. Per-match benchmark table.
4. Legacy vs Scenario vs Hybrid comparison.
5. Match-type breakdown.
6. Invalid / excluded matches.
7. Promotion or rollback recommendation.

Required summary metrics:

- Valid matches.
- Invalid odds matches.
- Legacy Wins.
- Scenario Wins.
- Hybrid Wins.
- Draws.
- Legacy ROI.
- Scenario ROI.
- Hybrid ROI.
- Hybrid vs Legacy Edge.
- Hybrid vs Scenario Edge.

Example benchmark table:

| Match | Quality | Legacy Top ROI | Scenario Top ROI | Hybrid Top ROI | Winner | Notes |
| --- | --- | ---: | ---: | ---: | --- | --- |
| Germany vs Ivory Coast | true_pre_match | -100.0% | 42.0% | 31.0% | Scenario | Hybrid avoided Legacy tail risk. |

## 9. Win / Draw Rules

For each match:

```text
highest ROI wins
```

Draw rule:

```text
If ROI gap between top systems is below 2 percentage points, count as Draw.
```

If all three systems miss:

- Count as Draw if ROI difference is immaterial.
- Count the least-negative ROI as winner only if the difference is material.

Hybrid edge formulas:

```text
Hybrid vs Legacy Edge = Hybrid ROI - Legacy ROI
Hybrid vs Scenario Edge = Hybrid ROI - Scenario ROI
```

## 10. Deduplication Rules

Same match may have multiple snapshots. Benchmark must count each match once.

Priority order:

1. Prefer `data_quality = true_pre_match`.
2. Prefer odds timestamp closest to kickoff while still earlier than kickoff.
3. Prefer complete market coverage:
   - Match Winner.
   - Asian Handicap.
   - Over / Under.
   - Correct Score.
4. Prefer larger API-Football provider coverage if timestamps are equivalent.
5. Exclude duplicates after selecting the benchmark snapshot.

Do not count by snapshot count.

Count by canonical match key:

```text
<competition>_<season>_<kickoff_date>_<home>_<away>
```

## 11. Match-Type Breakdown

Benchmark should classify each valid match into one or more types:

- Strong favorite / deep handicap.
- Balanced match.
- Upset-risk match.
- Low-score match.
- High-score match.

Classification sources:

- Pre-match implied probabilities.
- Asian Handicap line.
- Over / Under line.
- Final score.
- Scenario Engine labels if available.

Report should answer:

```text
Which match type does Hybrid improve most?
```

Required breakdown:

| Match Type | Legacy ROI | Scenario ROI | Hybrid ROI | Hybrid Edge | Notes |
| --- | ---: | ---: | ---: | ---: | --- |

## 12. Safety Boundaries

Allowed in future implementation phases:

- Add a historical odds quality check script.
- Add a limited backfill script.
- Add isolated files under `data/history/backfill/`.
- Add benchmark scripts and benchmark reports.
- Update governance docs.

Forbidden in this phase:

- Full API pull.
- Writing backfill data.
- Modifying `app.py`.
- Modifying `strategy_score(...)`.
- Modifying `evaluate_allocation(...)`.
- Modifying `strategy_comparison(...)`.
- Modifying UI.
- Modifying recommendation logic.
- Overwriting `data/history/`.
- Deleting files.
- Committing or pushing.

## 13. Phase Plan

### Phase A: Historical Odds Quality Check On 3 Sample Matches

Goal:

- Validate odds quality before any larger backfill.

Sample set:

- One strong favorite / deep handicap match.
- One balanced match.
- One upset-risk match.

Actions:

- Query only the three selected matches.
- Save outputs only if explicitly approved.
- Validate `update < kickoff` for all returned markets.
- Produce a quality report before portfolio generation.

Output:

```text
WORLD_CUP_ODDS_SAMPLE_QUALITY_REPORT.md
```

Risk: LOW.

### Phase B: Backfill 10 Completed Matches

Goal:

- Test the full isolated backfill and benchmark loop on a limited sample.

Actions:

- Write snapshots only to `data/history/backfill/`.
- Generate Legacy / Scenario / Hybrid portfolios from each valid snapshot.
- Generate a limited benchmark report.
- Confirm deduplication and data-quality filters.

Outputs:

```text
data/history/backfill/<match_slug>_pre.json
WORLD_CUP_BACKTEST_PORTFOLIOS.md
WORLD_CUP_RANKING_BENCHMARK_REPORT.md
```

Risk: MEDIUM.

### Phase C: Full Completed-Match Benchmark

Goal:

- Run benchmark on all completed World Cup matches with valid true pre-match odds.

Actions:

- Backfill completed matches only.
- Exclude invalid odds matches.
- Compare Legacy / Scenario / Hybrid.
- Produce final benchmark and recommendation for ranking migration.

Output:

```text
WORLD_CUP_RANKING_BENCHMARK_REPORT.md
```

Risk: MEDIUM-HIGH because benchmark results may influence production ranking decisions.

## 14. Readiness Verdict

Ready to proceed to Phase A only.

Do not proceed to Phase B or C until:

- sample odds quality has been confirmed,
- no snapshot overwrite risk exists,
- benchmark script boundaries are reviewed,
- and commit hygiene is clean enough to isolate generated backfill files.

