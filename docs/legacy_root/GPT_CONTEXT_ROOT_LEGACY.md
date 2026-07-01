# WorldCup Analyzer

## Quick Access

Read First:
LATEST.md

Project Context:
GPT_CONTEXT.md

History:
CHANGELOG.md

## Project Status

Version: v1.81-dev

Updated: 2026-06-26 18:46

Modified Files:
- CHANGELOG.md
- GPT_CONTEXT.md
- LATEST.md
- app.py
- data/history/portfolio_performance.json
- data/history/style_performance.json
- data/performance_logs/app_performance.jsonl
- data/team_aliases.yaml
- data/worldcup2026/index.json
- docs/DAILY_REPORT.md
- modules/betting_opinion.py
- modules/market_utils.py
- modules/odds_client.py
- modules/polymarket_client.py
- modules/pregame_content.py
- modules/report_generator.py
- modules/result_distribution.py
- modules/schedule_client.py
- modules/team_resolver.py
- modules/the_odds_client.py
- modules/user_odds.py
- modules/weather_client.py
- modules/worldcup_db.py
- scripts/refresh_match_prematch_snapshot.py
- scripts/update_gpt_context.py
- QA_REPORT.md
- REAL_CLAUDE_INTEGRATION_PLAN.md
- STARTUP_RECOVERY.md
- START_APP.command
- data/fetch_logs/20260624_165108_2026_06_24_pregame_refresh_summary.json
- data/fetch_logs/20260624_171647_2026_06_24_extra_local_schedule_refresh_summary.json
- data/history/2026_06_23_Colombia_Democratic_Republic_of_the_Congo_pre.json
- data/history/2026_06_24_Bosnia_and_Herzegovina_Qatar_post.json
- data/history/2026_06_24_Bosnia_and_Herzegovina_Qatar_pre.json
- data/history/2026_06_24_Colombia_DR_Congo_pre.json
- data/history/2026_06_24_Czech_Republic_Mexico_post.json
- data/history/2026_06_24_Czech_Republic_Mexico_pre.json
- data/history/2026_06_24_Morocco_Haiti_post.json
- data/history/2026_06_24_Morocco_Haiti_pre.json
- data/history/2026_06_24_Scotland_Brazil_post.json
- data/history/2026_06_24_Scotland_Brazil_pre.json
- data/history/2026_06_24_South_Africa_South_Korea_post.json
- data/history/2026_06_24_South_Africa_South_Korea_pre.json
- data/history/2026_06_24_Switzerland_Canada_post.json
- data/history/2026_06_24_Switzerland_Canada_pre.json
- data/history/2026_06_25_Cura_ao_Ivory_Coast_pre.json
- data/history/2026_06_25_Ecuador_Germany_pre.json
- data/history/2026_06_25_Japan_Sweden_pre.json
- data/history/2026_06_25_Paraguay_Australia_pre.json
- data/history/2026_06_25_Tunisia_Netherlands_pre.json
- data/history/2026_06_25_Turkey_United_States_pre.json
- data/history/my_portfolios/2026_06_23_Colombia_Democratic_Republic_of_the_Congo.json
- data/history/my_portfolios/2026_06_24_Bosnia_and_Herzegovina_Qatar.json
- data/history/my_portfolios/2026_06_24_Czech_Republic_Mexico.json
- data/history/my_portfolios/2026_06_24_Morocco_Haiti.json
- data/history/my_portfolios/2026_06_24_Scotland_Brazil.json
- data/history/my_portfolios/2026_06_24_South_Africa_South_Korea.json
- data/history/my_portfolios/2026_06_24_Switzerland_Canada.json
- data/history/my_portfolios/2026_06_25_Cura_ao_Ivory_Coast.json
- data/history/my_portfolios/2026_06_25_Ecuador_Germany.json
- data/history/my_portfolios/2026_06_25_Japan_Sweden.json
- data/history/my_portfolios/2026_06_25_Paraguay_Australia.json
- data/history/my_portfolios/2026_06_25_Tunisia_Netherlands.json
- data/history/my_portfolios/2026_06_25_Turkey_United_States.json
- data/worldcup2026/2026_06_24_Bosnia_and_Herzegovina_Qatar/events.json
- data/worldcup2026/2026_06_24_Bosnia_and_Herzegovina_Qatar/fixture.json
- data/worldcup2026/2026_06_24_Bosnia_and_Herzegovina_Qatar/injuries.json
- data/worldcup2026/2026_06_24_Bosnia_and_Herzegovina_Qatar/lineups.json
- data/worldcup2026/2026_06_24_Bosnia_and_Herzegovina_Qatar/match_stats.json
- data/worldcup2026/2026_06_24_Bosnia_and_Herzegovina_Qatar/odds.json
- data/worldcup2026/2026_06_24_Bosnia_and_Herzegovina_Qatar/players.json
- data/worldcup2026/2026_06_24_Bosnia_and_Herzegovina_Qatar/post_match.json
- data/worldcup2026/2026_06_24_Bosnia_and_Herzegovina_Qatar/pre_match.json
- data/worldcup2026/2026_06_24_Bosnia_and_Herzegovina_Qatar/team_stats.json
- data/worldcup2026/2026_06_24_Colombia_DR_Congo/events.json
- data/worldcup2026/2026_06_24_Colombia_DR_Congo/fixture.json
- data/worldcup2026/2026_06_24_Colombia_DR_Congo/injuries.json
- data/worldcup2026/2026_06_24_Colombia_DR_Congo/lineups.json
- data/worldcup2026/2026_06_24_Colombia_DR_Congo/match_stats.json
- data/worldcup2026/2026_06_24_Colombia_DR_Congo/odds.json
- data/worldcup2026/2026_06_24_Colombia_DR_Congo/players.json
- data/worldcup2026/2026_06_24_Colombia_DR_Congo/post_match.json
- data/worldcup2026/2026_06_24_Colombia_DR_Congo/pre_match.json
- data/worldcup2026/2026_06_24_Colombia_DR_Congo/team_stats.json
- data/worldcup2026/2026_06_24_Czechia_Mexico/events.json
- data/worldcup2026/2026_06_24_Czechia_Mexico/fixture.json
- data/worldcup2026/2026_06_24_Czechia_Mexico/injuries.json
- data/worldcup2026/2026_06_24_Czechia_Mexico/lineups.json
- data/worldcup2026/2026_06_24_Czechia_Mexico/match_stats.json
- data/worldcup2026/2026_06_24_Czechia_Mexico/odds.json
- data/worldcup2026/2026_06_24_Czechia_Mexico/players.json
- data/worldcup2026/2026_06_24_Czechia_Mexico/post_match.json
- data/worldcup2026/2026_06_24_Czechia_Mexico/pre_match.json
- data/worldcup2026/2026_06_24_Czechia_Mexico/team_stats.json
- data/worldcup2026/2026_06_24_Morocco_Haiti/events.json
- data/worldcup2026/2026_06_24_Morocco_Haiti/fixture.json
- data/worldcup2026/2026_06_24_Morocco_Haiti/injuries.json
- data/worldcup2026/2026_06_24_Morocco_Haiti/lineups.json
- data/worldcup2026/2026_06_24_Morocco_Haiti/match_stats.json
- data/worldcup2026/2026_06_24_Morocco_Haiti/odds.json
- data/worldcup2026/2026_06_24_Morocco_Haiti/players.json
- data/worldcup2026/2026_06_24_Morocco_Haiti/post_match.json
- data/worldcup2026/2026_06_24_Morocco_Haiti/pre_match.json
- data/worldcup2026/2026_06_24_Morocco_Haiti/team_stats.json
- data/worldcup2026/2026_06_24_Scotland_Brazil/events.json
- data/worldcup2026/2026_06_24_Scotland_Brazil/fixture.json
- data/worldcup2026/2026_06_24_Scotland_Brazil/injuries.json
- data/worldcup2026/2026_06_24_Scotland_Brazil/lineups.json
- data/worldcup2026/2026_06_24_Scotland_Brazil/match_stats.json
- data/worldcup2026/2026_06_24_Scotland_Brazil/odds.json
- data/worldcup2026/2026_06_24_Scotland_Brazil/players.json
- data/worldcup2026/2026_06_24_Scotland_Brazil/post_match.json
- data/worldcup2026/2026_06_24_Scotland_Brazil/pre_match.json
- data/worldcup2026/2026_06_24_Scotland_Brazil/team_stats.json
- data/worldcup2026/2026_06_24_South_Africa_South_Korea/events.json
- data/worldcup2026/2026_06_24_South_Africa_South_Korea/fixture.json
- data/worldcup2026/2026_06_24_South_Africa_South_Korea/injuries.json
- data/worldcup2026/2026_06_24_South_Africa_South_Korea/lineups.json
- data/worldcup2026/2026_06_24_South_Africa_South_Korea/match_stats.json
- data/worldcup2026/2026_06_24_South_Africa_South_Korea/odds.json
- data/worldcup2026/2026_06_24_South_Africa_South_Korea/players.json
- data/worldcup2026/2026_06_24_South_Africa_South_Korea/post_match.json
- data/worldcup2026/2026_06_24_South_Africa_South_Korea/pre_match.json
- data/worldcup2026/2026_06_24_South_Africa_South_Korea/team_stats.json
- data/worldcup2026/2026_06_24_Switzerland_Canada/events.json
- data/worldcup2026/2026_06_24_Switzerland_Canada/fixture.json
- data/worldcup2026/2026_06_24_Switzerland_Canada/injuries.json
- data/worldcup2026/2026_06_24_Switzerland_Canada/lineups.json
- data/worldcup2026/2026_06_24_Switzerland_Canada/match_stats.json
- data/worldcup2026/2026_06_24_Switzerland_Canada/odds.json
- data/worldcup2026/2026_06_24_Switzerland_Canada/players.json
- data/worldcup2026/2026_06_24_Switzerland_Canada/post_match.json
- data/worldcup2026/2026_06_24_Switzerland_Canada/pre_match.json
- data/worldcup2026/2026_06_24_Switzerland_Canada/team_stats.json
- data/worldcup2026/2026_06_24_extra_local_schedule_refresh_summary.json
- data/worldcup2026/2026_06_24_pregame_refresh_summary.json
- data/worldcup2026/2026_06_25_Curacao_Ivory_Coast/events.json
- data/worldcup2026/2026_06_25_Curacao_Ivory_Coast/fixture.json
- data/worldcup2026/2026_06_25_Curacao_Ivory_Coast/injuries.json
- data/worldcup2026/2026_06_25_Curacao_Ivory_Coast/lineups.json
- data/worldcup2026/2026_06_25_Curacao_Ivory_Coast/match_stats.json
- data/worldcup2026/2026_06_25_Curacao_Ivory_Coast/odds.json
- data/worldcup2026/2026_06_25_Curacao_Ivory_Coast/players.json
- data/worldcup2026/2026_06_25_Curacao_Ivory_Coast/post_match.json
- data/worldcup2026/2026_06_25_Curacao_Ivory_Coast/pre_match.json
- data/worldcup2026/2026_06_25_Curacao_Ivory_Coast/team_stats.json
- data/worldcup2026/2026_06_25_Ecuador_Germany/events.json
- data/worldcup2026/2026_06_25_Ecuador_Germany/fixture.json
- data/worldcup2026/2026_06_25_Ecuador_Germany/injuries.json
- data/worldcup2026/2026_06_25_Ecuador_Germany/lineups.json
- data/worldcup2026/2026_06_25_Ecuador_Germany/match_stats.json
- data/worldcup2026/2026_06_25_Ecuador_Germany/odds.json
- data/worldcup2026/2026_06_25_Ecuador_Germany/players.json
- data/worldcup2026/2026_06_25_Ecuador_Germany/post_match.json
- data/worldcup2026/2026_06_25_Ecuador_Germany/pre_match.json
- data/worldcup2026/2026_06_25_Ecuador_Germany/team_stats.json
- data/worldcup2026/2026_06_25_Japan_Sweden/events.json
- data/worldcup2026/2026_06_25_Japan_Sweden/fixture.json
- data/worldcup2026/2026_06_25_Japan_Sweden/injuries.json
- data/worldcup2026/2026_06_25_Japan_Sweden/lineups.json
- data/worldcup2026/2026_06_25_Japan_Sweden/match_stats.json
- data/worldcup2026/2026_06_25_Japan_Sweden/odds.json
- data/worldcup2026/2026_06_25_Japan_Sweden/players.json
- data/worldcup2026/2026_06_25_Japan_Sweden/post_match.json
- data/worldcup2026/2026_06_25_Japan_Sweden/pre_match.json
- data/worldcup2026/2026_06_25_Japan_Sweden/team_stats.json
- data/worldcup2026/2026_06_25_Paraguay_Australia/events.json
- data/worldcup2026/2026_06_25_Paraguay_Australia/fixture.json
- data/worldcup2026/2026_06_25_Paraguay_Australia/injuries.json
- data/worldcup2026/2026_06_25_Paraguay_Australia/lineups.json
- data/worldcup2026/2026_06_25_Paraguay_Australia/match_stats.json
- data/worldcup2026/2026_06_25_Paraguay_Australia/odds.json
- data/worldcup2026/2026_06_25_Paraguay_Australia/players.json
- data/worldcup2026/2026_06_25_Paraguay_Australia/post_match.json
- data/worldcup2026/2026_06_25_Paraguay_Australia/pre_match.json
- data/worldcup2026/2026_06_25_Paraguay_Australia/team_stats.json
- data/worldcup2026/2026_06_25_Tunisia_Netherlands/events.json
- data/worldcup2026/2026_06_25_Tunisia_Netherlands/fixture.json
- data/worldcup2026/2026_06_25_Tunisia_Netherlands/injuries.json
- data/worldcup2026/2026_06_25_Tunisia_Netherlands/lineups.json
- data/worldcup2026/2026_06_25_Tunisia_Netherlands/match_stats.json
- data/worldcup2026/2026_06_25_Tunisia_Netherlands/odds.json
- data/worldcup2026/2026_06_25_Tunisia_Netherlands/players.json
- data/worldcup2026/2026_06_25_Tunisia_Netherlands/post_match.json
- data/worldcup2026/2026_06_25_Tunisia_Netherlands/pre_match.json
- data/worldcup2026/2026_06_25_Tunisia_Netherlands/team_stats.json
- data/worldcup2026/2026_06_25_Turkiye_USA/events.json
- data/worldcup2026/2026_06_25_Turkiye_USA/fixture.json
- data/worldcup2026/2026_06_25_Turkiye_USA/injuries.json
- data/worldcup2026/2026_06_25_Turkiye_USA/lineups.json
- data/worldcup2026/2026_06_25_Turkiye_USA/match_stats.json
- data/worldcup2026/2026_06_25_Turkiye_USA/odds.json
- data/worldcup2026/2026_06_25_Turkiye_USA/players.json
- data/worldcup2026/2026_06_25_Turkiye_USA/post_match.json
- data/worldcup2026/2026_06_25_Turkiye_USA/pre_match.json
- data/worldcup2026/2026_06_25_Turkiye_USA/team_stats.json
- data/worldcup2026/2026_06_25_polymarket_refresh_summary.json
- data/worldcup2026/qualification_context_2026_06_24.json
- docs/GAME_BEHAVIOR_MODEL.md
- docs/MODEL_ALGORITHM.md
- modules/game_behavior_engine.py
- modules/portfolio_engine.py
- reports/backtests/backtest_attribution_20260625.csv
- reports/backtests/backtest_attribution_20260625.md
- reports/backtests/backtest_constraint_comparison_20260625.csv
- reports/backtests/backtest_constraint_comparison_20260625.md
- reports/backtests/backtest_results_20260625.csv
- reports/backtests/backtest_summary_20260625.md
- reports/validation/report_export_validation_20260625.md
- reports/validation/report_export_validation_20260626.md
- reports/validation/report_readability_validation_20260625.md
- requirements-dev.txt
- scripts/backtest_attribution.py
- scripts/backtest_portfolio_engine.py
- scripts/run_streamlit_8502.sh
- scripts/start_streamlit_8502.command
- scripts/test_portfolio_engine.py
- scripts/validate_report_exports.py

Status:
Running: http://localhost:8502

## Current Problems

1. Backtest attribution shows low-odds false safety, correct-score concentration, and handicap/path failures as the leading failure patterns.
2. Report explanation layer must stay aligned with Portfolio Ranking so coverage assets are not described as directional leans.
3. Live Streamlit report export should be spot-checked after page interaction to confirm Portfolio Eligibility carries actual top-strategy status.
4. New Risk Gate and Rank #1 Eligibility are active, but historical backtest aggregate is unchanged because saved portfolios were not regenerated.
5. Qualification Pressure Engine uses manual third-round seed data and still needs live standings automation.
6. Pre-match decision cockpit needs validation against finished matches and saved snapshots.
7. Score probability distribution still needs calibration against real match results.
8. Correct score marginal EV depends on bookmaker implied probability and may need de-vig adjustment.
9. Coverage Engine still needs stronger joint calibration from handicap/totals/correct-score odds.
10. Qualification pressure now uses API-Football standings when available, but live coverage still needs match-day validation.
11. Directional Odds Value noise filtering is improved but remains heuristic without liquidity and price-stability inputs.
12. API data refresh should be executed through terminal scripts first, then saved to cache/history.
13. Prediction Audit and Recommendation Audit need validation on finished matches.
14. Portfolio Style statistics need more post-match samples.

## Current Conclusions

- Do not use estimated correct score odds.
- Current model has been documented in docs/MODEL_ALGORITHM.md.
- Game behavior / qualification pressure model status is documented in docs/GAME_BEHAVIOR_MODEL.md.
- Backtest framework created under scripts/backtest_portfolio_engine.py.
- Backtest reports are saved under reports/backtests.
- Backtest attribution report has been generated.
- Turkey vs United States report no longer exports '- vs -' in Match Overview.
- Betting Opinion now separates Match Direction, Handicap Market Direction, Coverage / Insurance Candidate, Goals View, and Match Investment View.
- Turkey +0.5 is treated as coverage / insurance, not as the main market direction.
- Handicap center detection filters outlier API-Football rows and prefers shallow favorite-market centers.
- Total center detection identifies ranges such as 2.5-2.75 instead of mechanically outputting Lean Over 2.5.
- Value Analysis is scoped to Winner Market Value when comparing The Odds API with Polymarket.
- Report Data Quality Notes now flag missing lineups, Polymarket winner-only scope, handicap outliers, and pre-lineup injury ambiguity.
- Betting Opinion v2 is now global across match reports, not only Turkey vs USA.
- Match Direction, Handicap Market Direction, Coverage Candidate, Goals View, and Match Investment View are separated globally.
- Report export validates fixture metadata and avoids silent '-' fields for teams, competition, stage, kickoff, and venue.
- Value Analysis is scoped to winner-market comparison when using Polymarket.
- Portfolio Eligibility summary is included in report export when available; otherwise the report states why it is not available.
- Streamlit page and exported Markdown reports use Chinese user-facing labels.
- Same-sign API-Football Asian Handicap rows are normalized for favorite-side center detection when they would otherwise mislead the handicap center.
- Six-match report export validation is saved under reports/validation/report_export_validation_20260625.md.
- Report readability validation is saved under reports/validation/report_readability_validation_20260625.md.
- Exported reports now show real portfolio names, core bets, portfolio style, risk gate result, risk level, Rank #1 eligibility, and blockers/pass reasons.
- Asian Handicap and Over/Under report sections now show core summaries first, 3-5 nearby market rows, and full market details inside Markdown details blocks.
- Asian Handicap report rows map Home/Away labels to actual team names in visible summaries and full details.
- Data Quality Notes now state whether user-entered actual odds participated in final portfolio ranking.
- Risk Gate and Rank #1 Eligibility are now active for current portfolio generation.
- Zero Risk is now a rank eligibility gate, not only a score component.
- Correct Score exposure is controlled by stake share and dependency checks.
- Qualification Pressure now changes portfolio templates, not only scoring.
- Rank #1 requires eligibility checks beyond score.
- Portfolio Score weights remain unchanged in this round.
- Current priority is constraint-layer validation before tuning.
- Do not change Portfolio Score weights until Rank #1 eligibility behavior is validated.
- Initial negative ROI should be decomposed by style, pressure type, failure pattern, and constraint gate status.
- Current model should not be further tuned until initial backtest results are reviewed.
- Third-round group-stage qualification pressure is now part of Scenario Engine.
- Qualification Pressure Score affects external risk, coverage, handicap depth, tail score selection, and Match Investment Score.
- Already-qualified favorites receive deep-handicap risk adjustment.
- Must-win underdogs lift underdog goal tail and late volatility.
- Both-draw-acceptable matches lift draw/under paths and lower aggressive portfolio scores.
- Use real odds only for Match Winner, Asian Handicap, Over/Under, and Correct Score.
- Every betting item can carry multiple weighted asset roles, not just one market type.
- Correct Score can carry Return, Directional, Tail, or Insurance roles depending on score path and odds.
- Match Winner, Asian Handicap, and Over/Under can carry Insurance, Directional, Tempo, or Return roles depending on context.
- Recommended portfolio is generated by the optimizer, not by fixed slots.
- Pre-match page now mirrors post-match structure: ranking, role allocation, settlement preview, risk paths, and outcome preview.
- Portfolio Ranking and My Portfolio now share the same scoring path through evaluate_strategy.
- Match Investment Score uses fixed 20/25/20/20/10/5 weights and explicit Data Quality / Timing.
- Coverage Efficiency now reports EV/ROI/max-loss/zero-risk deltas and supports Add/Replace/Add Small/Do Not Add.
- User actual odds A/B regression proves ranking can change while extreme noise odds are filtered.
- Generated style portfolios are verified to keep correct-score bets at four or fewer.
- Pytest is installed as a dev dependency and currently passes 12 portfolio engine tests.
- Game Behavior Engine v1 adjusts tempo, goal distribution, upset probability, and handicap bias from API-Football standings-derived qualification pressure when available.
- API-Football standings are cached for 24 hours by league and season.
- Local app startup is protected by START_APP.command with port checks, stale-process cleanup, health check, browser open, PID file, and log output.
- Do not use LaunchAgent for this project while it remains inside Documents because macOS blocks background access to the virtualenv.
- When localhost is down, Codex should open START_APP.command first, then verify lsof -i :8502 and curl -I http://localhost:8502/.
- Detail page now uses indexed lightweight database loading instead of eager full JSON loading.
- Polymarket uses file cache and a 4-second page timeout to avoid blocking the decision page.
- Page-triggered network requests have shorter timeouts; full API refresh should still be done through terminal refresh scripts.
- Fractional Asian handicap settlement supports split-leg lines such as -1/1.5 and +2/2.5.
- Equivalent bets now deduplicate by normalized bet_id and merge role tags.
- Extreme correct-score paths can be filtered from Directional Odds Value as noise.
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

1. Review reports/backtests/backtest_attribution_20260625.md before changing weights.
2. Inspect Rank #1 failure rows for low-odds false safety, correct-score concentration, and missing adjacent paths.
3. Validate Qualification Pressure Engine on real third-round finished matches.
4. Validate Pre-Match Decision Cockpit on finished matches.
5. Validate multi-role Betting Asset Framework on finished matches.
6. Validate Post Match Analysis on finished matches.
7. Validate Prediction Audit on finished matches.
8. Validate Portfolio Style Performance after more settled matches.
9. Validate Odds Distribution Optimizer on finished matches.
10. Calibrate score probability distribution.
11. Calibrate role balance adjustment thresholds.
12. Review whether return and tail asset sizing is too aggressive or too conservative.

## GPT Focus

1. Which rank #1 failure pattern should be addressed first without overfitting?
2. Is low-odds false safety caused by too much confidence in single-path assets?
3. Does Qualification Pressure improve Rank #1 outcomes in third-round matches?
4. Are multi-role weights correctly assigned for winner, handicap, total, and correct score bets?
5. Does post-match role contribution correctly explain which asset roles helped or hurt?
