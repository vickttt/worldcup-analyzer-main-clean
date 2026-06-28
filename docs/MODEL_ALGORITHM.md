# WorldCup Analyzer Model Algorithm

Updated: 2026-06-25

Status: CURRENT MODEL DOCUMENTATION

This document explains the current recommendation and portfolio ranking model. It is descriptive, not a tuning proposal.

## 1. System Inputs

The model can use the following inputs when available:

- Match fixture: teams, kickoff, venue, status, final score after match.
- Match Winner odds: home win, draw, away win.
- Asian Handicap odds.
- Over/Under odds.
- Correct Score odds.
- Polymarket probabilities.
- API-Football fixture, team, lineup, injury, recent form, and standings data.
- Weather and venue metadata when available.
- User actual odds.
- User portfolio.
- Historical pre-match and post-match snapshots.

Missing inputs are not fabricated. Missing odds reduce data quality and may lower Match Investment Score.

## 2. Data Sources

Current source responsibilities:

- API-Football: Match Winner and Over/Under when available.
- API-Football: Asian Handicap, Correct Score, fixture, lineups, injuries, standings, recent form.
- Polymarket: market probabilities when a market is found.
- Local cache/history: previously fetched odds, match snapshots, my portfolios, post-match settlements.
- Manual seed data: third-round group qualification pressure in `data/worldcup2026/qualification_context_2026_06_24.json`.

The page should prefer local match data once a fixture has already been fetched and saved. Terminal refresh scripts are used for API data refresh.

## 3. Data Preprocessing

Preprocessing includes:

- Team name normalization and alias resolution.
- Local database lookup for existing match folders.
- Odds cache lookup before external calls.
- Snapshot restoration from `data/history` or `data/worldcup2026`.
- Conversion of API odds rows into normalized bet candidates.
- Translation of team display names for UI.
- Qualification context loading from manual seed or standings fallback.

## 4. Market Parsing

Each candidate bet is normalized into a common structure:

- `type`: winner, handicap, total, correct_score.
- `selection`: normalized selection text.
- `standard_odds`: market odds.
- `actual_odds`: user-entered odds, if present.
- `effective_odds`: actual odds first, otherwise market odds.
- `amount`: stake suggested or entered.
- `score`: candidate-level score.
- `roles`: asset-role tags.
- `bet_id`: stable identity used for deduplication.

## 5. Asian Handicap Split Settlement

Asian handicap lines are parsed by `normalize_handicap_line`.

Examples:

- `-1` -> one leg: -1.0
- `-1/1.5` -> split legs: -1.0 and -1.5
- `+2/2.5` -> split legs: +2.0 and +2.5
- `-1/2` -> shorthand: -0.5

Settlement is done leg by leg by `settle_asian_handicap`. This is used for EV, score-path simulation, strategy settlement, and post-match audit.

## 6. User Actual Odds Handling

User actual odds are parsed, normalized, saved, and restored per match. During candidate evaluation:

1. User odds are matched to a market type and selection.
2. If matched, `actual_odds` becomes the effective price.
3. Candidate EV and ranking can change.
4. Extreme high-odds paths that contradict the main scenario can be filtered as noise by Directional Odds Value.

User odds are not automatically treated as valuable. They must align with scenario plausibility and market support.

## 7. Market Odds Handling

Market odds are used to:

- Estimate implied probabilities.
- Identify favorite and underdog.
- Identify handicap center.
- Identify total-goals center.
- Build correct-score clusters.
- Build score scenario grid.
- Price candidate bets when user actual odds are missing.

The system does not estimate correct-score odds when real correct-score odds are missing.

## 8. Main Direction Identification

Main direction comes from:

- Match Winner implied probability.
- Polymarket probability when available.
- Handicap center.
- Candidate direction alignment.
- Game Behavior context.

The system asks: which side and which path does the market most clearly support?

## 9. Scenario Identification

The model separates outcome paths into:

- Favorite small win.
- Favorite win by 2.
- Favorite win by 3+.
- Draw / low-margin path.
- Underdog unbeaten path.
- Qualification pressure paths such as draw acceptable, must win, late chaos, low-tempo control, and rotation risk.

Scenario labels are used by Coverage Engine and Portfolio Ranking.

## 10. Score Scenario Grid

`build_score_scenario_grid` constructs a score grid. Each scenario row can include:

- `score`
- `home_goals`
- `away_goals`
- `margin`
- `total_goals`
- `winner`
- `raw_implied_probability`
- `devig_probability`
- `handicap_alignment`
- `total_alignment`
- `scenario_weight`
- `classification`: main, adjacent, reasonable tail, noise tail

Qualification pressure can reweight this grid.

## 11. Candidate Bet Generation

Candidate assets can include:

- Match Winner.
- Asian Handicap.
- Over/Under.
- Correct Score.

Each candidate is evaluated with:

- Odds.
- Scenario alignment.
- Plausibility.
- Role tags.
- Directional value.
- Coverage contribution.
- Noise flag.

## 12. Deduplication

The system prevents duplicate bets and duplicate portfolios:

- `build_bet_id` creates stable IDs by type, side, line, score, and odds.
- `dedupe_bets` merges duplicate bets and role tags.
- `portfolio_id` normalizes a portfolio as a sorted set of bet IDs.
- `dedupe_portfolios` keeps the highest-scoring portfolio for a duplicated bet set.

This prevents the same bet from appearing multiple times just because it has multiple roles.

## 13. Style Portfolio Generation

Current style portfolios include:

- Conservative Portfolio: winner + handicap + limited adjacent correct scores.
- Main Scenario Portfolio: winner + handicap + total + up to four adjacent/main correct scores.
- Aggressive Portfolio: handicap + total + up to four correct scores.
- Tail Hedge Portfolio: winner + up to four correct scores.
- User Portfolio: user-entered bets, evaluated using the same scoring path when available.

Correct-score bets are capped at four for system-generated portfolios.

## 14. Coverage Engine

Coverage Engine evaluates whether a portfolio covers:

- Main scenario.
- Adjacent scenario.
- Tail scenario.
- One-goal deviation risk.
- Zero-risk paths.

It answers: if the match deviates slightly from the main script, does the portfolio survive?

## 15. Coverage Efficiency

Coverage Efficiency evaluates whether adding or replacing a bet improves the portfolio enough to justify cost and complexity.

It can output:

- EV delta.
- ROI delta.
- Max-loss delta.
- Zero-risk delta.
- One-goal risk reduction.
- Recommendation: Add, Replace, Add Small, Do Not Add.

This is especially important for deciding whether a shallower handicap is a better insurance asset than a deeper line.

## 16. Directional Odds Value

Directional Odds Value asks whether an odds edge supports the main match direction.

It considers:

- Price edge.
- Scenario alignment.
- Plausibility.
- Market support.
- Noise penalty.
- Weighted edge.

High odds alone do not create value. A high-odds score that contradicts the main script can be ignored as noise.

## 17. Portfolio Score

Current code uses the following real weights:

Portfolio Score =

- Risk-Adjusted Value: 15%
- Scenario Consistency: 20%
- Coverage Quality: 20%
- Coverage Efficiency: 15%
- Directional Odds Value: 10%
- Drawdown / Zero Risk: 10%
- Simplicity: 10%

Status: PASS. The implementation in `compute_portfolio_score` matches this formula.

Current additional display component:

- Pressure Fit: reported as a score component and used inside Scenario Consistency and Coverage Quality. It is not an extra standalone final-weight bucket.

## 17A. Risk Gate

`portfolio_risk_gate` is now a hard Rank #1 eligibility check.

It evaluates whether a portfolio survives reasonable main, adjacent, and tail scenarios. A portfolio can still be displayed when it fails this gate, but it cannot become the official Recommendation unless no available portfolio passes.

The gate checks:

- reasonable scenario loss probability
- adjacent-path failure probability
- main-path positive coverage
- exact-score-only dependency
- stricter thresholds when qualification pressure raises deep handicap, draw, chaos, or late-volatility risk

Output fields:

- `passed`
- `reason`
- `failed_paths`
- `risk_level`

## 17B. Correct Score Exposure Control

Correct Score is treated as a satellite return/tail asset, not the primary risk source of a main recommendation.

`correct_score_exposure_control` checks:

- correct-score count
- correct-score stake share
- style-specific exposure limit
- exact-score dependency
- clean-sheet cluster risk
- high-margin cluster risk

Current limits:

- Conservative: 20%
- Main/default: 30%
- Aggressive: 40%

If Correct Score exposure fails, the portfolio may be shown as an alternative, but should not become Rank #1.

## 17C. Pressure-Based Portfolio Templates

Qualification pressure now affects candidate portfolio generation, not only scoring.

`generate_portfolio_templates_by_pressure` adds pressure-aware structures, for example:

- already-qualified favorite vs must-win underdog: favorite ML or shallow handicap plus small-win / underdog-goal coverage
- both draw acceptable: under, draw-like narrow scores, and conservative structures
- direct second-place battle: narrow scores and late-volatility-aware coverage
- must-win vs must-win: both-team scoring paths and late-volatility coverage
- qualified vs qualified: under / draw / narrow-score structures

## 17D. Rank #1 Eligibility

`rank1_eligibility_check` runs after Portfolio Score.

Rank #1 requires:

- Risk Gate passed
- Correct Score exposure controlled
- Pressure Fit not Low
- at least one main or adjacent path covered
- no exact-score-noise dependency

High-scoring but fragile portfolios are moved to alternatives and display their blockers.

## 17E. Portfolio Marginal Utility

`compute_portfolio_marginal_utility` compares structural variants, not only added bets.

Supported comparison types include:

- replacing deep handicap with shallower handicap
- replacing clean-sheet score with underdog-goal score
- adding draw tail
- reducing exact-score exposure
- switching from handicap to a safer core direction asset where available

The output compares EV, ROI, max loss, zero-risk, coverage gain, complexity change, and recommendation.

## 18. Portfolio Ranking

Ranking flow:

1. Build candidate bets.
2. Generate style portfolios.
3. Add pressure-based templates when qualification context is available.
4. Add optimized/user portfolios when available.
5. Deduplicate portfolios.
6. Evaluate every portfolio with the same scoring path.
7. Attach Risk Gate, Correct Score Exposure Control, Pressure Fit, and Rank #1 Eligibility.
8. Select official Rank #1 from eligible portfolios first, then score.
9. Rename first row as recommended portfolio and later rows as alternatives.

User Portfolio uses the same scoring framework when it is included in the ranking.

User actual odds can affect final ranking by changing effective odds, EV, ROI, Directional Odds Value, and portfolio score.

There is no manual human override in the normal ranking path. Some UI labels and fallback behavior are rule-based.

## 19. My Portfolio Analysis

My Portfolio can be entered in simplified or natural formats. It is parsed and matched to saved market odds or user actual odds.

The post-match audit can compare My Portfolio against system portfolios using:

- Total stake.
- Net profit.
- ROI.
- Hit/loss/push counts.
- Asset role contribution.
- Recommendation audit detail.

## 20. Match Investment Score

Current code uses:

Match Investment Score =

- Market Clarity: 20%
- Scenario Clarity: 25%
- Directional Odds Value: 20%
- Coverage Quality: 20%
- External Risk: 10%
- Data Quality / Timing: 5%

Status: PASS. The implementation in `compute_match_investment_score` matches the target weights.

The score increases when:

- Main direction is clear.
- Scenario consistency is high.
- Directional odds value is positive.
- Coverage quality is high.
- External risk is contained.
- API, Polymarket, and user odds data are complete.

The score decreases when:

- One-goal deviation risk is high.
- Deep handicap risk is raised by qualification pressure.
- Chaos or late-volatility risk is high.
- Polymarket data is missing or partial.
- API odds are incomplete.
- User actual odds are missing for key portfolio bets.

Already-qualified favorites reduce deep-handicap confidence because rotation and tempo control make margin less reliable.

Must-win underdogs raise tail risk because they may attack, create late volatility, or score even if they lose.

## 21. Game Behavior / Qualification Pressure

Qualification pressure is now part of the model through `modules/game_behavior_engine.py`.

It affects:

- Score distribution.
- Score scenario grid.
- External risk.
- Portfolio Pressure Fit.
- Handicap depth preference.
- Tail score selection.

See `docs/GAME_BEHAVIOR_MODEL.md` for the detailed status.

## 22. Post-Match Settlement

After a match finishes, portfolios can be settled against the final score.

Settlement outputs:

- Total stake.
- Profit.
- ROI.
- Per-bet result: win, lose, push, no odds.
- Role contribution.
- Recommendation audit.
- Prediction audit.

Asian handicap settlement uses split-leg logic.

## 23. Why This Portfolio Instead Of Another?

The system prefers a portfolio when it has a better combined profile across:

- It expresses the main match direction.
- It covers the main and adjacent score paths.
- It avoids fragile one-goal collapse.
- It does not overpay for noisy tails.
- It has acceptable EV/ROI.
- It controls max loss and zero-risk exposure.
- It uses a simple enough set of bets.
- It responds to qualification pressure.

A portfolio with higher raw EV can lose ranking if it is noisy, too concentrated, inconsistent with the match script, or exposed to qualification-driven risks.

## 24. Current Limitations

- Score-grid probabilities remain a heuristic blend of market structure and rule-based adjustments.
- Qualification pressure currently uses manual seed data first and standings fallback; full automatic qualification probability is not implemented.
- Directional Odds Value does not yet include liquidity, API-Football-provider-count stability, or time-series price movement.
- Correct-score value depends on available real odds. Missing correct-score odds are not estimated.
- Historical sample size is still small, so model quality must be judged through replay/backtest results before further tuning.
- The current system should not be tuned further until initial backtest results are reviewed.
