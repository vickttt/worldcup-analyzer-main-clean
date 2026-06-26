# Game Behavior Model

Updated: 2026-06-25

Current status: IMPLEMENTED / PARTIAL

The Game Behavior Model is implemented as a minimum viable rules engine. It is connected to Scenario Engine, Coverage Engine, Match Investment Score, and Portfolio Ranking. It is still PARTIAL because full automatic qualification probability is not implemented; third-round group pressure currently uses manual seed data first, then API-Football standings fallback where available.

## 1. Purpose

Odds tell us how the market prices the match.

Qualification pressure tells us how teams may play the match.

This model exists to adjust the portfolio engine for:

- Already-qualified rotation risk.
- Draw-acceptable matches.
- Must-win pressure.
- Must-win-big pressure.
- Direct second-place battles.
- Must-win underdog goal tails.
- Late-game volatility.
- Deep-handicap risk.

## 2. Qualification Pressure Score

Each team can receive one pressure score:

| Score | Meaning |
| ---: | --- |
| 0 | Already eliminated / no clear motivation |
| 1 | Already qualified, rotation / tempo-control risk |
| 2 | Draw acceptable |
| 3 | Must avoid loss |
| 4 | Must win |
| 5 | Must win big / depends on others |

Current sources:

1. Manual seed file: `data/worldcup2026/qualification_context_2026_06_24.json`
2. API-Football standings fallback when available.
3. Neutral fallback: pressure score 3.

## 3. Match Pressure Type

The model classifies a match from the two team pressure scores.

Current implemented types:

- `qualified_favorite_vs_must_win_underdog`
- `both_draw_acceptable`
- `direct_second_place_battle`
- `must_win_vs_must_win`
- `qualified_vs_qualified`
- `favorite_must_win`
- `dead_rubber_or_low_motivation`
- `neutral_group_context`

## 4. Behavior Adjustments

The engine outputs structured adjustments:

- `deep_handicap_risk_delta`
- `favorite_small_win_weight_delta`
- `underdog_goal_weight_delta`
- `draw_weight_delta`
- `over_weight_delta`
- `under_weight_delta`
- `late_goal_volatility_delta`
- `rotation_risk_delta`
- `tempo_control_delta`
- `chaos_risk_delta`
- `recommended_coverage_shift`

Each numeric delta usually ranges from -2 to +2.

## 5. Current Scenario Effects

### Already-qualified favorite vs must-win underdog

Example: Ecuador vs Germany.

Effects:

- Deep handicap risk up.
- Favorite small-win path up.
- Underdog goal tail up.
- Late volatility up.
- Rotation risk up.

Betting implication:

The favorite can remain the stronger side, but deep handicap and extreme blowout exposure should be reduced.

### Both draw acceptable

Example: Switzerland vs Canada.

Effects:

- Draw path up.
- Under path up.
- Tempo control up.
- Blowout path down.

Betting implication:

Aggressive one-sided portfolios should be downgraded.

### Must win vs must win

Example: Bosnia and Herzegovina vs Qatar.

Effects:

- Draw value down.
- Late volatility up.
- Chaos path up.
- Both-team scoring and 2:1 / 1:2 / 2:2 paths become more relevant.

Betting implication:

Avoid portfolios that only cover one narrow path.

### Direct second-place battle

Example: Japan vs Sweden.

Effects:

- Early caution and late volatility coexist.
- Narrow-score coverage matters.
- Draw and underdog goal paths need some weight.

Betting implication:

Do not overconcentrate on one side winning big.

### Favorite must win

Example: Panama vs England.

Effects:

- Favorite direction remains valid.
- One-goal win and underdog scoring tail stay relevant.
- Deep blowout should not become automatic.

## 6. Current Code Integration

Implemented in:

- `modules/game_behavior_engine.py`
- `modules/result_distribution.py`
- `modules/portfolio_engine.py`
- `app.py`

Connected areas:

- Result Distribution: `apply_behavior_to_distribution`
- Score Scenario Grid: `qualification_score_multiplier`
- Match Investment Score: External Risk and Data Quality note
- Portfolio Ranking: `Pressure Fit`
- Portfolio Generation: pressure-specific templates for shallow handicap, draw/under, narrow scores, underdog-goal tail, and late volatility
- Core Decision UI: Qualification & Game Behavior section

## 6A. Portfolio Template Generation

Qualification Pressure now changes candidate portfolio structure, not only final scoring.

Current pressure templates:

- `qualified_favorite_vs_must_win_underdog`: lower favorite handicap depth and add underdog-goal or small-win paths.
- `both_draw_acceptable`: lift under / draw-like narrow-score structures and avoid aggressive one-sided portfolios.
- `direct_second_place_battle`: prefer narrow-score structures and late-volatility-aware coverage.
- `must_win_vs_must_win`: lift both-team scoring paths and reduce draw-as-main exposure.
- `favorite_must_win`: keep favorite direction but add underdog-goal or one-goal deviation coverage.
- `qualified_vs_qualified`: prefer under / draw / narrow-score portfolios and downgrade deep handicap structures.

This is intentionally a minimum viable rules layer. It does not change Portfolio Score weights.

## 7. Pressure Fit

Portfolio Ranking now has a `Pressure Fit` field.

Meaning:

- High: the portfolio responds to current qualification pressure.
- Medium: partial response.
- Low: ignores important qualification-driven risk.

Examples:

- If an already-qualified favorite has deep handicap risk, portfolios with only deep handicap and blowout scores should score lower.
- If both teams can accept a draw, portfolios with draw/under/narrow-score coverage should score higher.
- If both teams must win, portfolios that include late volatility or scoring tail coverage should score higher.

## 8. Current Seed Data

Manual seed file:

`data/worldcup2026/qualification_context_2026_06_24.json`

It covers Groups A-L and key remaining third-round matches. This is intentionally a seed file, not a permanent substitute for live standings computation.

## 9. What Is Implemented

Implemented:

- Qualification Pressure Score.
- Match Pressure Type classification.
- Structured Behavior Adjustments.
- Scenario distribution adjustment.
- Score-grid adjustment.
- Portfolio Pressure Fit.
- Pressure-based portfolio template generation.
- Rank #1 eligibility constraints can use Pressure Fit as a blocker when it is Low.
- Match Investment Score risk adjustment.
- Core Decision UI display.
- Regression tests for representative third-round cases.

## 10. What Is Partial

PARTIAL:

- Full automatic qualification probability is not implemented.
- Third-place qualification math is not fully simulated.
- Live standings fallback exists, but seed data is still the primary source for third-round context.
- Pressure Fit is rule-based and needs validation against finished match results.
- Exact adjustment strength still needs backtest validation.

## 11. Validation Cases

Current tests cover:

- Germany vs Ecuador: already-qualified favorite vs must-win underdog.
- Switzerland vs Canada: both draw acceptable.
- Bosnia and Herzegovina vs Qatar: both must win.
- Morocco vs Haiti: favorite must win.
- Japan vs Sweden: direct second-place battle.
- England vs Panama: favorite direction with deep handicap caution.

## 12. Current Conclusion

Current status: IMPLEMENTED / PARTIAL.

The model is active and connected, but should not be further tuned until replay/backtest reports show whether the pressure adjustments improve portfolio ranking and post-match settlement.
