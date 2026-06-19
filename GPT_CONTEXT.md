# WorldCup Analyzer

## Quick Access

Read First:
LATEST.md

Project Context:
GPT_CONTEXT.md

History:
CHANGELOG.md

## Project Status

Version: v1.60-dev

Updated: 2026-06-19 15:58

Modified Files:
- CHANGELOG.md
- GPT_CONTEXT.md
- LATEST.md
- app.py
- data/history/2026_06_18_Switzerland_Bosnia_and_Herzegovina_post.json
- data/team_aliases.yaml
- modules/team_resolver.py
- requirements.txt
- data/fetch_logs/20260619_155517_2026_06_19_refresh_summary.json
- data/history/2026_06_19_Brazil_Haiti_pre.json
- data/history/2026_06_19_Scotland_Morocco_pre.json
- data/history/my_portfolios/2026_06_18_Switzerland_Bosnia_and_Herzegovina.json
- data/history/portfolio_performance.json
- data/worldcup2026/2026_06_16_France_Senegal/events.json
- data/worldcup2026/2026_06_16_France_Senegal/fixture.json
- data/worldcup2026/2026_06_16_France_Senegal/injuries.json
- data/worldcup2026/2026_06_16_France_Senegal/lineups.json
- data/worldcup2026/2026_06_16_France_Senegal/match_stats.json
- data/worldcup2026/2026_06_16_France_Senegal/odds.json
- data/worldcup2026/2026_06_16_France_Senegal/players.json
- data/worldcup2026/2026_06_16_France_Senegal/post_match.json
- data/worldcup2026/2026_06_16_France_Senegal/pre_match.json
- data/worldcup2026/2026_06_16_France_Senegal/team_stats.json
- data/worldcup2026/2026_06_17_England_Croatia/events.json
- data/worldcup2026/2026_06_17_England_Croatia/fixture.json
- data/worldcup2026/2026_06_17_England_Croatia/injuries.json
- data/worldcup2026/2026_06_17_England_Croatia/lineups.json
- data/worldcup2026/2026_06_17_England_Croatia/match_stats.json
- data/worldcup2026/2026_06_17_England_Croatia/odds.json
- data/worldcup2026/2026_06_17_England_Croatia/players.json
- data/worldcup2026/2026_06_17_England_Croatia/post_match.json
- data/worldcup2026/2026_06_17_England_Croatia/pre_match.json
- data/worldcup2026/2026_06_17_England_Croatia/team_stats.json
- data/worldcup2026/2026_06_17_Portugal_DR_Congo/events.json
- data/worldcup2026/2026_06_17_Portugal_DR_Congo/fixture.json
- data/worldcup2026/2026_06_17_Portugal_DR_Congo/injuries.json
- data/worldcup2026/2026_06_17_Portugal_DR_Congo/lineups.json
- data/worldcup2026/2026_06_17_Portugal_DR_Congo/match_stats.json
- data/worldcup2026/2026_06_17_Portugal_DR_Congo/odds.json
- data/worldcup2026/2026_06_17_Portugal_DR_Congo/players.json
- data/worldcup2026/2026_06_17_Portugal_DR_Congo/post_match.json
- data/worldcup2026/2026_06_17_Portugal_DR_Congo/pre_match.json
- data/worldcup2026/2026_06_17_Portugal_DR_Congo/team_stats.json
- data/worldcup2026/2026_06_18_Switzerland_Bosnia_and_Herzegovina/events.json
- data/worldcup2026/2026_06_18_Switzerland_Bosnia_and_Herzegovina/fixture.json
- data/worldcup2026/2026_06_18_Switzerland_Bosnia_and_Herzegovina/injuries.json
- data/worldcup2026/2026_06_18_Switzerland_Bosnia_and_Herzegovina/lineups.json
- data/worldcup2026/2026_06_18_Switzerland_Bosnia_and_Herzegovina/match_stats.json
- data/worldcup2026/2026_06_18_Switzerland_Bosnia_and_Herzegovina/odds.json
- data/worldcup2026/2026_06_18_Switzerland_Bosnia_and_Herzegovina/players.json
- data/worldcup2026/2026_06_18_Switzerland_Bosnia_and_Herzegovina/post_match.json
- data/worldcup2026/2026_06_18_Switzerland_Bosnia_and_Herzegovina/pre_match.json
- data/worldcup2026/2026_06_18_Switzerland_Bosnia_and_Herzegovina/team_stats.json
- data/worldcup2026/2026_06_19_Brazil_Haiti/events.json
- data/worldcup2026/2026_06_19_Brazil_Haiti/fixture.json
- data/worldcup2026/2026_06_19_Brazil_Haiti/injuries.json
- data/worldcup2026/2026_06_19_Brazil_Haiti/lineups.json
- data/worldcup2026/2026_06_19_Brazil_Haiti/match_stats.json
- data/worldcup2026/2026_06_19_Brazil_Haiti/odds.json
- data/worldcup2026/2026_06_19_Brazil_Haiti/players.json
- data/worldcup2026/2026_06_19_Brazil_Haiti/post_match.json
- data/worldcup2026/2026_06_19_Brazil_Haiti/pre_match.json
- data/worldcup2026/2026_06_19_Brazil_Haiti/team_stats.json
- data/worldcup2026/2026_06_19_Scotland_Morocco/events.json
- data/worldcup2026/2026_06_19_Scotland_Morocco/fixture.json
- data/worldcup2026/2026_06_19_Scotland_Morocco/injuries.json
- data/worldcup2026/2026_06_19_Scotland_Morocco/lineups.json
- data/worldcup2026/2026_06_19_Scotland_Morocco/match_stats.json
- data/worldcup2026/2026_06_19_Scotland_Morocco/odds.json
- data/worldcup2026/2026_06_19_Scotland_Morocco/players.json
- data/worldcup2026/2026_06_19_Scotland_Morocco/post_match.json
- data/worldcup2026/2026_06_19_Scotland_Morocco/pre_match.json
- data/worldcup2026/2026_06_19_Scotland_Morocco/team_stats.json
- data/worldcup2026/2026_06_19_Turkiye_Paraguay/events.json
- data/worldcup2026/2026_06_19_Turkiye_Paraguay/fixture.json
- data/worldcup2026/2026_06_19_Turkiye_Paraguay/injuries.json
- data/worldcup2026/2026_06_19_Turkiye_Paraguay/lineups.json
- data/worldcup2026/2026_06_19_Turkiye_Paraguay/match_stats.json
- data/worldcup2026/2026_06_19_Turkiye_Paraguay/odds.json
- data/worldcup2026/2026_06_19_Turkiye_Paraguay/players.json
- data/worldcup2026/2026_06_19_Turkiye_Paraguay/post_match.json
- data/worldcup2026/2026_06_19_Turkiye_Paraguay/pre_match.json
- data/worldcup2026/2026_06_19_Turkiye_Paraguay/team_stats.json
- data/worldcup2026/2026_06_19_USA_Australia/events.json
- data/worldcup2026/2026_06_19_USA_Australia/fixture.json
- data/worldcup2026/2026_06_19_USA_Australia/injuries.json
- data/worldcup2026/2026_06_19_USA_Australia/lineups.json
- data/worldcup2026/2026_06_19_USA_Australia/match_stats.json
- data/worldcup2026/2026_06_19_USA_Australia/odds.json
- data/worldcup2026/2026_06_19_USA_Australia/players.json
- data/worldcup2026/2026_06_19_USA_Australia/post_match.json
- data/worldcup2026/2026_06_19_USA_Australia/pre_match.json
- data/worldcup2026/2026_06_19_USA_Australia/team_stats.json
- data/worldcup2026/2026_06_19_refresh_summary.json
- data/worldcup2026/history_backfill_summary.json
- modules/worldcup_db.py
- scripts/build_worldcup_data_center.py
- scripts/refresh_api_data.py
- scripts/refresh_match_prematch_snapshot.py

Status:
Running: http://localhost:8502

## Current Problems

1. Pre-match decision cockpit needs validation against finished matches and saved snapshots.
2. Score probability distribution still needs calibration against real match results.
3. Correct score marginal EV depends on bookmaker implied probability and may need de-vig adjustment.
4. Insurance, return, directional, tempo, and tail role sizing needs more live-match validation.
5. Some matches still lack full API-Football handicap or correct score coverage.
6. API data refresh should be executed through terminal scripts first, then saved to cache/history.
7. Prediction Audit and Recommendation Audit need validation on finished matches.
8. Portfolio Style statistics need more post-match samples.

## Current Conclusions

- Do not use estimated correct score odds.
- Use real odds only for Match Winner, Asian Handicap, Over/Under, and Correct Score.
- Every betting item can carry multiple weighted asset roles, not just one market type.
- Correct Score can carry Return, Directional, Tail, or Insurance roles depending on score path and odds.
- Match Winner, Asian Handicap, and Over/Under can carry Insurance, Directional, Tempo, or Return roles depending on context.
- Recommended portfolio is generated by the optimizer, not by fixed slots.
- Pre-match page now mirrors post-match structure: ranking, role allocation, settlement preview, risk paths, and outcome preview.
- Optimizer now adjusts utility based on asset role balance.
- Portfolio naming is unified as Recommendation and Alternatives.
- Odds data should be cached for at least 24 hours per match.
- Match Snapshot is saved under data/history and should not be overwritten.
- My Portfolio is saved separately and used for post-match settlement.
- Post-match analysis now splits profit and stake across multiple asset roles.
- Permanent history lives under data/history and is separate from expiring API cache.
- Pre-match snapshots use *_pre.json and post-match snapshots use *_post.json.
- API pulls should be verified through terminal scripts before relying on page rendering.
- Prediction Audit links pre-match recommendation reasons to post-match outcomes.
- Recommendation Audit records which recommendation logic failed or worked.
- Portfolio Style classifies strategies as Aggressive, Balanced, or Conservative.
- Model Version Tracking is saved into each new pre/post-match snapshot.

## Next Step

1. Validate Pre-Match Decision Cockpit on finished matches.
2. Validate multi-role Betting Asset Framework on finished matches.
3. Validate Post Match Analysis on finished matches.
4. Validate Prediction Audit on finished matches.
5. Validate Portfolio Style Performance after more settled matches.
6. Validate Odds Distribution Optimizer on finished matches.
7. Calibrate score probability distribution.
8. Calibrate role balance adjustment thresholds.
9. Review whether return and tail asset sizing is too aggressive or too conservative.

## GPT Focus

1. Does the pre-match strategy ranking predict which strategy performs best after the match?
2. Are multi-role weights correctly assigned for winner, handicap, total, and correct score bets?
3. Does post-match role contribution correctly explain which asset roles helped or hurt?
