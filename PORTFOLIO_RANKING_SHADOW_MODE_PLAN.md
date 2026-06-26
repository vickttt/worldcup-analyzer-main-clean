# Portfolio Ranking 2.0 Shadow Mode Plan

Date: 2026-06-21

Scope: design only. This plan does not modify code, ranking order, UI logic, recommendation logic, data files, branches, commits, or Git history.

## Goal

Build a Shadow Mode for Portfolio Ranking 2.0.

The current Portfolio Ranking continues to run normally and remains the only ranking that affects users. Portfolio Ranking 2.0 runs in parallel, records its own score and rank, and produces comparison data for validation.

Shadow Mode exists to answer one question:

Does Scenario-aware Ranking make better ranking decisions than the legacy EV/ROI/Sharpe-first ranking without breaking user decision clarity?

## 1. What Is Shadow Mode

Shadow Mode means:

- Legacy Ranking remains authoritative.
- Legacy Rank still determines displayed order and default recommendation.
- Portfolio Ranking 2.0 calculates a parallel Scenario Rank.
- Scenario Rank is recorded for review but does not affect the user.
- No UI decision logic changes.
- No recommendation output changes.
- No sorting changes.

### Shadow Mode Rule

```text
Legacy Ranking decides.
Scenario Ranking observes.
Auditor explains differences.
```

### Not Allowed In Shadow Mode

- Do not modify `strategy_score(...)`.
- Do not modify `evaluate_allocation(...)`.
- Do not modify `strategy_comparison(...)`.
- Do not change default recommendation selection.
- Do not change ranking order shown to users.
- Do not block any portfolio based on Scenario Rank.
- Do not rewrite UI decision logic.

## 2. Shadow Ranking Output

Each portfolio should receive two rank views:

| Field | Meaning |
| --- | --- |
| `legacy_rank` | Current production rank from existing Portfolio Ranking. |
| `legacy_score` | Existing score currently used by the app. |
| `scenario_rank` | Shadow rank from Portfolio Ranking 2.0 logic. |
| `scenario_score` | Shadow Portfolio Score using scenario-aware dimensions. |
| `rank_difference` | `scenario_rank - legacy_rank`. |
| `rank_shift_label` | Human-readable movement label. |
| `shadow_verdict` | Whether Scenario Ranking agrees with Legacy Ranking. |

### Rank Difference Interpretation

```text
rank_difference = 0
  Legacy and Scenario rankings agree.

rank_difference > 0
  Scenario Ranking downgrades the portfolio.

rank_difference < 0
  Scenario Ranking upgrades the portfolio.
```

### Suggested Rank Shift Labels

| Condition | Label |
| --- | --- |
| `rank_difference = 0` | Stable |
| `abs(rank_difference) = 1` | Minor Shift |
| `abs(rank_difference) = 2` | Material Shift |
| `abs(rank_difference) >= 3` | Major Shift |

## 3. Recorded Fields

Shadow Mode should record one structured row per portfolio.

Required fields:

| Field | Purpose |
| --- | --- |
| `match_id` | Match identifier. |
| `match_name` | Human-readable match name. |
| `snapshot_time` | When the ranking snapshot was generated. |
| `portfolio_name` | Strategy or portfolio label. |
| `ev` | Existing expected value metric. |
| `roi` | Existing ROI metric. |
| `sharpe` | Existing Sharpe/stability metric. |
| `scenario_consistency_score` | Scenario alignment score, 0-100. |
| `tail_exposure` | Share or label of Tail/Aggressive Tail dependency. |
| `asset_role_balance` | Balance of Direction, Tempo, Return, Insurance, Tail roles. |
| `main_scenario_coverage` | Whether the portfolio serves Main Scenario. |
| `secondary_insurance_coverage` | Whether the portfolio protects named failure paths. |
| `audit_status` | Pass, Warning, or Fail from Recommendation Auditor. |
| `audit_severity` | None, Low, Medium, High, or Critical. |
| `conflict_flags` | Any detected path conflicts. |
| `legacy_score` | Existing production score. |
| `legacy_rank` | Existing production rank. |
| `scenario_score` | Shadow scenario-aware score. |
| `scenario_rank` | Shadow scenario-aware rank. |
| `rank_difference` | Difference between Scenario Rank and Legacy Rank. |
| `shadow_verdict` | Agreement, Watch, or Disagreement. |

### Optional Fields

- `user_decision_complexity`
- `default_recommendation_eligible_v2`
- `tail_heavy_warning`
- `critical_conflict_count`
- `high_conflict_count`
- `scenario_rank_reason`
- `legacy_vs_scenario_notes`

## 4. Scenario Score Concept

Shadow Mode can calculate a separate Scenario Score without touching production score.

Conceptual formula:

```text
Scenario Score =
  Value Layer
  + Scenario Layer
  + Role Balance Layer
  + Coverage Layer
  - Tail Penalty
  - Conflict Penalty
  - Decision Complexity Penalty
```

Suggested weighting for observation:

| Layer | Suggested Weight |
| --- | ---: |
| EV / ROI / Sharpe | 30 |
| Scenario Consistency Score | 25 |
| Asset Role Balance | 15 |
| Main Scenario Coverage | 10 |
| Secondary Insurance Coverage | 10 |
| Tail Exposure penalty | -5 to -20 |
| Conflict penalty | -10 to -50 |
| Decision Complexity penalty | -5 to -15 |

Shadow Mode should store the component scores so differences can be audited later.

## 5. Observation Metrics

The most important observation is disagreement between production rank and scenario-aware rank.

### Primary Watch Case

```text
Legacy Rank = 1
Scenario Rank != 1
```

This means the current production top portfolio may not be the best scenario-aware recommendation.

### Important Disagreement Cases

| Case | Meaning |
| --- | --- |
| `legacy_rank = 1` and `scenario_rank >= 3` | Production top choice may be materially overranked. |
| `legacy_rank <= 2` and `scenario_rank >= 4` | Legacy ranking may favor value metrics over scenario quality. |
| `legacy_rank >= 4` and `scenario_rank = 1` | Scenario Ranking found a candidate legacy ranking may be undervaluing. |
| `legacy_rank = 1` and `audit_severity in High/Critical` | Production top choice has a serious logic warning. |
| `legacy_rank = 1` and `tail_exposure` is high | Production top choice may be too tail-heavy. |
| `legacy_rank = 1` and `scenario_consistency_score < 75` | Production top choice fails the recommended consistency warning threshold. |

### Secondary Watch Cases

- High EV portfolio is downgraded because of weak Main Scenario Coverage.
- High Sharpe portfolio is downgraded because it lacks clear insurance logic.
- Correct-score-heavy portfolio is downgraded because Tail Exposure is excessive.
- My Portfolio ranks much differently under Scenario Rank than under Legacy Rank.
- Auditor finds Over3.5 plus low-score correct-score conflict in a high-ranked portfolio.

## 6. Shadow Verdict Labels

Each portfolio comparison can receive a Shadow Verdict.

| Verdict | Condition |
| --- | --- |
| Agreement | Rank difference is 0 or 1 and no High/Critical conflict exists. |
| Watch | Rank difference is 2, or Scenario Score flags warning-level issues. |
| Disagreement | Rank difference is 3 or more, or Legacy Rank 1 is not Scenario Rank 1. |
| Blocker Candidate | Legacy Rank 1 has High/Critical audit severity or Scenario Consistency Score below 60. |

Shadow Verdict is for review only. It must not affect user-visible ranking during Shadow Mode.

## 7. Validation Standard

Shadow Mode should run long enough to cover different match types.

Minimum validation window:

- at least 20 completed matches
- at least 5 favorite-heavy matches
- at least 5 balanced matches
- at least 3 upset or draw-sensitive matches
- at least 5 matches with rich correct-score markets

Replacement can be considered only if:

- Scenario Rank agrees with post-match review more often than Legacy Rank.
- Legacy Rank 1 versus Scenario Rank disagreement is explainable and repeatable.
- High/Critical conflict portfolios are consistently downgraded by Scenario Rank.
- Tail-heavy portfolios are no longer silently promoted to default recommendation.
- My Portfolio and system portfolios use the same evaluation fields.
- User decision clarity improves or remains stable.
- No snapshot, replay, post-match, or report flow breaks.

Suggested decision threshold:

```text
After 20+ reviewed matches:
  If Scenario Rank improves audit quality without breaking clarity,
  move to Phase 3 limited UI display.

After 40+ reviewed matches:
  If Scenario Rank continues to outperform Legacy Rank,
  consider making Scenario Rank eligible for default recommendation logic.
```

## 8. Replacement Gate

Do not replace Legacy Ranking until all gates pass.

Required gates:

- No unresolved Critical audit conflicts in Scenario Ranking rules.
- Scenario Score components are explainable.
- Scenario Rank handles Tail Exposure correctly.
- Scenario Rank handles insurance assets separately from main return assets.
- Scenario Rank does not over-penalize reasonable Secondary Scenario protection.
- My Portfolio uses the same score fields as system portfolios.
- Historical snapshots remain readable.
- Post-match review confirms better ranking decisions.

## 9. Recommended Shadow Mode Output Location

Future implementation can write Shadow Mode output as structured snapshot metadata.

Suggested top-level snapshot field:

```json
{
  "portfolio_ranking_shadow": {
    "mode": "shadow",
    "legacy_authoritative": true,
    "rows": []
  }
}
```

Optional report output:

- `PORTFOLIO_RANKING_SHADOW_REPORT.md`

The report should summarize:

- Legacy top portfolio
- Scenario top portfolio
- rank differences
- disagreement cases
- audit warnings
- tail-heavy portfolios
- replacement readiness status

## 10. Implementation Boundary For Future Phase

Allowed future Shadow Mode implementation:

- calculate Scenario Score in parallel
- record Scenario Rank
- record Rank Difference
- generate review report
- keep legacy ranking authoritative

Not allowed during Shadow Mode:

- use Scenario Rank to sort production ranking
- hide portfolios based on Scenario Rank
- change existing `score`
- change optimizer utility
- change UI default recommendation
- overwrite historical data

## Final Recommendation

Proceed with Shadow Mode before any Portfolio Ranking 2.0 replacement.

The first implementation should be silent and report-driven:

1. Legacy Ranking remains production behavior.
2. Scenario Ranking runs in parallel.
3. Differences are recorded.
4. Disagreement cases are reviewed after completed matches.
5. Replacement is considered only after enough match evidence is collected.
