# WorldCup Analyzer

## Quick Access

Read First:
LATEST.md

Project Context:
GPT_CONTEXT.md

History:
CHANGELOG.md

## Project Status

Version: v1.64-dev

Updated: 2026-06-20 21:07

Modified Files:
- GPT_CONTEXT.md
- LATEST.md
- app.py
- data/history/portfolio_performance.json
- data/history/style_performance.json
- data/performance_logs/app_performance.jsonl
- data/team_aliases.yaml
- scripts/build_worldcup_data_center.py
- scripts/refresh_match_prematch_snapshot.py
- data/fetch_logs/20260620_203245_2026_06_20_refresh_summary.json
- data/fetch_logs/20260620_203647_2026_06_20_refresh_summary.json
- data/history/2026_06_19_United_States_Australia_post.json
- data/history/2026_06_20_Germany_Ivory_Coast_pre.json
- data/history/2026_06_20_Netherlands_Sweden_pre.json
- data/history/my_portfolios/2026_06_19_United_States_Australia.json
- data/history/my_portfolios/2026_06_20_Germany_Ivory_Coast.json
- data/worldcup2026/2026_06_20_Brazil_Haiti/events.json
- data/worldcup2026/2026_06_20_Brazil_Haiti/fixture.json
- data/worldcup2026/2026_06_20_Brazil_Haiti/injuries.json
- data/worldcup2026/2026_06_20_Brazil_Haiti/lineups.json
- data/worldcup2026/2026_06_20_Brazil_Haiti/match_stats.json
- data/worldcup2026/2026_06_20_Brazil_Haiti/odds.json
- data/worldcup2026/2026_06_20_Brazil_Haiti/players.json
- data/worldcup2026/2026_06_20_Brazil_Haiti/post_match.json
- data/worldcup2026/2026_06_20_Brazil_Haiti/pre_match.json
- data/worldcup2026/2026_06_20_Brazil_Haiti/team_stats.json
- data/worldcup2026/2026_06_20_Ecuador_Curacao/events.json
- data/worldcup2026/2026_06_20_Ecuador_Curacao/fixture.json
- data/worldcup2026/2026_06_20_Ecuador_Curacao/injuries.json
- data/worldcup2026/2026_06_20_Ecuador_Curacao/lineups.json
- data/worldcup2026/2026_06_20_Ecuador_Curacao/match_stats.json
- data/worldcup2026/2026_06_20_Ecuador_Curacao/odds.json
- data/worldcup2026/2026_06_20_Ecuador_Curacao/players.json
- data/worldcup2026/2026_06_20_Ecuador_Curacao/post_match.json
- data/worldcup2026/2026_06_20_Ecuador_Curacao/pre_match.json
- data/worldcup2026/2026_06_20_Ecuador_Curacao/team_stats.json
- data/worldcup2026/2026_06_20_Germany_Ivory_Coast/events.json
- data/worldcup2026/2026_06_20_Germany_Ivory_Coast/fixture.json
- data/worldcup2026/2026_06_20_Germany_Ivory_Coast/injuries.json
- data/worldcup2026/2026_06_20_Germany_Ivory_Coast/lineups.json
- data/worldcup2026/2026_06_20_Germany_Ivory_Coast/match_stats.json
- data/worldcup2026/2026_06_20_Germany_Ivory_Coast/odds.json
- data/worldcup2026/2026_06_20_Germany_Ivory_Coast/players.json
- data/worldcup2026/2026_06_20_Germany_Ivory_Coast/post_match.json
- data/worldcup2026/2026_06_20_Germany_Ivory_Coast/pre_match.json
- data/worldcup2026/2026_06_20_Germany_Ivory_Coast/team_stats.json
- data/worldcup2026/2026_06_20_Netherlands_Sweden/events.json
- data/worldcup2026/2026_06_20_Netherlands_Sweden/fixture.json
- data/worldcup2026/2026_06_20_Netherlands_Sweden/injuries.json
- data/worldcup2026/2026_06_20_Netherlands_Sweden/lineups.json
- data/worldcup2026/2026_06_20_Netherlands_Sweden/match_stats.json
- data/worldcup2026/2026_06_20_Netherlands_Sweden/odds.json
- data/worldcup2026/2026_06_20_Netherlands_Sweden/players.json
- data/worldcup2026/2026_06_20_Netherlands_Sweden/post_match.json
- data/worldcup2026/2026_06_20_Netherlands_Sweden/pre_match.json
- data/worldcup2026/2026_06_20_Netherlands_Sweden/team_stats.json
- data/worldcup2026/2026_06_20_Scotland_Morocco/events.json
- data/worldcup2026/2026_06_20_Scotland_Morocco/fixture.json
- data/worldcup2026/2026_06_20_Scotland_Morocco/injuries.json
- data/worldcup2026/2026_06_20_Scotland_Morocco/lineups.json
- data/worldcup2026/2026_06_20_Scotland_Morocco/match_stats.json
- data/worldcup2026/2026_06_20_Scotland_Morocco/odds.json
- data/worldcup2026/2026_06_20_Scotland_Morocco/players.json
- data/worldcup2026/2026_06_20_Scotland_Morocco/post_match.json
- data/worldcup2026/2026_06_20_Scotland_Morocco/pre_match.json
- data/worldcup2026/2026_06_20_Scotland_Morocco/team_stats.json
- data/worldcup2026/2026_06_20_Tunisia_Japan/events.json
- data/worldcup2026/2026_06_20_Tunisia_Japan/fixture.json
- data/worldcup2026/2026_06_20_Tunisia_Japan/injuries.json
- data/worldcup2026/2026_06_20_Tunisia_Japan/lineups.json
- data/worldcup2026/2026_06_20_Tunisia_Japan/match_stats.json
- data/worldcup2026/2026_06_20_Tunisia_Japan/odds.json
- data/worldcup2026/2026_06_20_Tunisia_Japan/players.json
- data/worldcup2026/2026_06_20_Tunisia_Japan/post_match.json
- data/worldcup2026/2026_06_20_Tunisia_Japan/pre_match.json
- data/worldcup2026/2026_06_20_Tunisia_Japan/team_stats.json
- data/worldcup2026/2026_06_20_Turkiye_Paraguay/events.json
- data/worldcup2026/2026_06_20_Turkiye_Paraguay/fixture.json
- data/worldcup2026/2026_06_20_Turkiye_Paraguay/injuries.json
- data/worldcup2026/2026_06_20_Turkiye_Paraguay/lineups.json
- data/worldcup2026/2026_06_20_Turkiye_Paraguay/match_stats.json
- data/worldcup2026/2026_06_20_Turkiye_Paraguay/odds.json
- data/worldcup2026/2026_06_20_Turkiye_Paraguay/players.json
- data/worldcup2026/2026_06_20_Turkiye_Paraguay/post_match.json
- data/worldcup2026/2026_06_20_Turkiye_Paraguay/pre_match.json
- data/worldcup2026/2026_06_20_Turkiye_Paraguay/team_stats.json
- data/worldcup2026/2026_06_20_USA_Australia/events.json
- data/worldcup2026/2026_06_20_USA_Australia/fixture.json
- data/worldcup2026/2026_06_20_USA_Australia/injuries.json
- data/worldcup2026/2026_06_20_USA_Australia/lineups.json
- data/worldcup2026/2026_06_20_USA_Australia/match_stats.json
- data/worldcup2026/2026_06_20_USA_Australia/odds.json
- data/worldcup2026/2026_06_20_USA_Australia/players.json
- data/worldcup2026/2026_06_20_USA_Australia/post_match.json
- data/worldcup2026/2026_06_20_USA_Australia/pre_match.json
- data/worldcup2026/2026_06_20_USA_Australia/team_stats.json
- data/worldcup2026/2026_06_20_refresh_summary.json

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
