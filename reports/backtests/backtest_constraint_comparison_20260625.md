# Backtest Constraint Comparison 20260625

## Purpose

This report compares the existing backtest baseline with the current constraint-layer implementation.

Scope: risk constraints and portfolio generation rules only.

No Portfolio Score weights were changed in this round.

## Baseline Files

- `reports/backtests/backtest_summary_20260625.md`
- `reports/backtests/backtest_results_20260625.csv`
- `reports/backtests/backtest_attribution_20260625.md`
- `reports/backtests/backtest_attribution_20260625.csv`

## Implemented Constraint Layer

- Zero Risk is now a Rank #1 eligibility gate, not only a score component.
- Correct Score exposure is controlled by stake share, dependency checks, and cluster detection.
- Qualification Pressure now changes portfolio templates, not only scenario scoring.
- Rank #1 requires eligibility checks beyond raw score.
- Portfolio Marginal Utility can compare structural variants such as replacing a deep handicap with a shallower line or replacing clean-sheet scores with underdog-goal scores.

## Before / After Metrics

| Metric | Before | After | Delta | Status |
| --- | ---: | ---: | ---: | --- |
| Total ROI | -13.8% | -13.8% | 0.0pp | Unchanged |
| Rank #1 Profit Rate | 52.4% | 52.4% | 0.0pp | Unchanged |
| Zero Risk Trigger Count | 65 | 65 | 0 | Unchanged |
| Low-Odds False Safety Count | 65 | 65 | 0 | Unchanged |
| Correct-Score Concentration Count | 42 | 42 | 0 | Unchanged |

## Interpretation

The aggregate historical backtest did not improve in this run because the backtest framework primarily settles saved pre-match portfolio snapshots. Most saved snapshots were generated before the new eligibility layer existed.

The new logic is active in the current generation path, but the existing historical report is not a full replay of newly generated portfolios.

## Constraint Effects Now Available

### Risk Gate

Fragile high-score portfolios can be displayed as alternatives, but they cannot become the official Recommendation if they fail adjacent-path or zero-risk checks.

### Correct Score Exposure Control

Correct Score can remain a return or tail asset, but it cannot dominate the main recommendation through stake concentration or clean-sheet clustering.

### Pressure Template Generation

Qualification pressure can now alter portfolio construction. Examples:

- Already-qualified favorite vs must-win underdog: lower handicap depth, add small-win or underdog-goal tail.
- Both draw acceptable: lift draw, under, and narrow-score structures.
- Must win vs must win: lift late volatility and both-team scoring paths.

### Rank #1 Eligibility

Official Rank #1 now requires:

- risk gate passed
- correct-score exposure under control
- no critical scenario inconsistency
- at least one main or adjacent path covered
- Pressure Fit not Low

## Remaining Failure Modes

- Historical low-odds false safety rows remain until snapshots are regenerated or replayed from raw odds.
- Correct-score concentration remains visible in old attribution rows.
- Qualification Pressure impact is still partial in older snapshots because pressure metadata is missing or unknown.

## Conclusion

Status: PASS / PARTIAL.

PASS: the structural constraint layer has been implemented without changing Portfolio Score weights.

PARTIAL: existing backtest aggregate ROI is unchanged because historical saved portfolios were not regenerated.
