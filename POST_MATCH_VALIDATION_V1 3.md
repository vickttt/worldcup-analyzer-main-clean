# Post-Match Validation Framework v1

Date: 2026-06-21

Scope: design only. This framework does not write code, change business logic, modify UI, modify recommendation logic, modify data files, refresh API data, create branches, commit, or push.

## Goal

Answer one question:

```text
Scenario Ranking 是否比 Legacy Ranking 更有效？
```

Current evidence shows that `Legacy Rank` and `Scenario Rank` often disagree.

That is not enough. A disagreement is useful only if post-match outcomes prove that one ranking method produces better long-term decisions.

This framework defines how to compare them after final results are known.

## 1. 赛后记录结构

Each completed match should have one validation record.

Recommended record identity:

| Field | Meaning |
| --- | --- |
| `match_id` | Stable match identifier or slug. |
| `match_name` | Human-readable match, for example `Germany vs Ivory Coast`. |
| `match_date` | Match date. |
| `pre_snapshot_path` | Original pre-match snapshot used for recommendations. |
| `post_snapshot_path` | Post-match result or review snapshot when available. |
| `validation_status` | `complete`, `partial`, or `insufficient_data`. |

### Final Result Fields

| Field | Meaning |
| --- | --- |
| `final_score` | Final score, for example `2:0`. |
| `home_goals` | Final home goals. |
| `away_goals` | Final away goals. |
| `winner_result` | `home_win`, `draw`, or `away_win`. |
| `total_goals` | `home_goals + away_goals`. |
| `goal_band` | Suggested bands: `0-1`, `2-3`, `4+`. |
| `handicap_result` | Settlement result for the main handicap line. |
| `total_result` | Settlement result for the main total line. |
| `correct_score_result` | Whether any correct-score asset hit. |

### Market Result Fields

| Field | Meaning |
| --- | --- |
| `main_handicap_line` | The main handicap line used by the recommendation. |
| `main_total_line` | The main total-goals line used by the recommendation. |
| `winner_market_result` | Winning side in winner market. |
| `handicap_market_result` | Win / push / lose for handicap asset. |
| `total_market_result` | Over / under / push result. |
| `correct_score_market_result` | Exact-score settlement. |

The post-match record must be able to settle every portfolio that existed in the pre-match snapshot.

## 2. Portfolio Validation

Each match should compare at least four portfolio identities.

| Portfolio Type | Required | Meaning |
| --- | --- | --- |
| `legacy_top_portfolio` | Yes | Portfolio ranked first by production Legacy Ranking. |
| `scenario_top_portfolio` | Yes | Portfolio ranked first by Scenario Ranking / Shadow Ranking. |
| `current_recommendation_portfolio` | Yes | The portfolio or combo the system presented as the current recommendation. |
| `my_portfolio` | Optional | User-entered portfolio when available. |

### Portfolio Snapshot Fields

For each portfolio, record:

| Field | Meaning |
| --- | --- |
| `portfolio_name` | Display name. |
| `portfolio_type` | `legacy_top`, `scenario_top`, `current_recommendation`, `my_portfolio`, or `other`. |
| `legacy_rank` | Production rank before the match. |
| `legacy_score` | Production score before the match. |
| `scenario_rank` | Shadow / Scenario rank before the match. |
| `scenario_score` | Scenario-aware score before the match. |
| `shadow_verdict` | Agreement / Watch / Disagreement / Blocker Candidate. |
| `scenario_rank_reason` | Short explanation when available. |
| `assets` | Portfolio asset list. |
| `total_stake` | Total stake amount. |

### Required Comparison Rule

The validation must compare portfolios as they existed before kickoff.

Do not recalculate the pre-match decision using post-match data.

## 3. Portfolio Outcome

Each validated portfolio should produce one outcome row.

| Field | Meaning |
| --- | --- |
| `hit_status` | `hit`, `partial_hit`, `miss`, or `push`. |
| `profit_loss` | Net profit or loss amount. |
| `roi` | `profit_loss / total_stake`. |
| `max_drawdown` | Worst settlement loss within the portfolio path. |
| `settlement_notes` | Short explanation of which assets won, lost, pushed, or missed. |

### Asset-Level Outcome

Each asset inside a portfolio should be settleable.

| Field | Meaning |
| --- | --- |
| `asset_name` | Market / selection name. |
| `asset_type` | winner, handicap, total, correct_score, or other. |
| `stake` | Stake amount. |
| `odds` | Odds used at recommendation time. |
| `settlement` | win, lose, push, void, or unknown. |
| `profit_loss` | Asset-level net result. |

The portfolio outcome is the sum of asset-level outcomes.

## 4. Legacy vs Scenario

The core comparison is between:

```text
Legacy Top Portfolio
vs
Scenario Top Portfolio
```

### Match-Level Winner Rule

Use ROI as the primary comparison.

```text
if scenario_top_roi > legacy_top_roi:
    result = Scenario Winner
elif legacy_top_roi > scenario_top_roi:
    result = Legacy Winner
else:
    result = Draw
```

### Tie Handling

If ROI is equal, use this order:

1. Higher `profit_loss`.
2. Lower `max_drawdown`.
3. Lower decision complexity.
4. Otherwise `Draw`.

### Minimum Difference Threshold

To avoid overreading tiny differences:

```text
material_roi_gap = 0.02
```

If absolute ROI difference is below 2 percentage points:

```text
result = Draw
```

unless one portfolio has materially lower max drawdown.

### Labels

| Label | Meaning |
| --- | --- |
| `Scenario Winner` | Scenario Top outperformed Legacy Top materially. |
| `Legacy Winner` | Legacy Top outperformed Scenario Top materially. |
| `Draw` | Outcome difference was too small or equivalent. |
| `Invalid` | Missing settlement data prevents comparison. |

## 5. 长期统计

Post-match validation should aggregate results across match batches.

### Core Metrics

| Metric | Formula |
| --- | --- |
| `Legacy Win Rate` | `Legacy Winner count / valid comparisons`. |
| `Scenario Win Rate` | `Scenario Winner count / valid comparisons`. |
| `Draw Rate` | `Draw count / valid comparisons`. |
| `Legacy ROI` | Sum of Legacy Top profit/loss divided by Sum of Legacy Top stake. |
| `Scenario ROI` | Sum of Scenario Top profit/loss divided by Sum of Scenario Top stake. |
| `Legacy Average Rank` | Average pre-match Legacy Rank of the winner portfolio when Legacy wins. |
| `Scenario Average Rank` | Average pre-match Scenario Rank of the winner portfolio when Scenario wins. |

### Additional Metrics

| Metric | Meaning |
| --- | --- |
| `Scenario Edge` | `Scenario ROI - Legacy ROI`. |
| `Profit Difference` | Scenario Top total P/L minus Legacy Top total P/L. |
| `Max Drawdown Difference` | Scenario Top max drawdown minus Legacy Top max drawdown. |
| `Disagreement Win Rate` | Scenario win rate only on matches where Legacy Top != Scenario Top. |
| `Agreement Stability` | ROI when Legacy Top = Scenario Top. |

### Batch Sizes

Use fixed checkpoints:

| Batch Size | Purpose |
| ---: | --- |
| 20 matches | Early signal only. Do not replace Legacy Ranking. |
| 30 matches | Directional confidence. Review guardrails. |
| 50 matches | Minimum serious evidence for ranking policy discussion. |

No production ranking replacement should be considered before the 50-match checkpoint.

## 6. Decision Journal

Every match should preserve a short decision journal.

The journal should answer:

```text
What did the system believe before the match?
What warning did Scenario Ranking raise?
What actually happened after the match?
```

### Required Journal Fields

| Field | Meaning |
| --- | --- |
| `pre_match_recommendation_reason` | Why the system recommended the portfolio at the time. |
| `main_scenario` | Main Scenario before kickoff. |
| `secondary_scenario` | Secondary Scenario before kickoff. |
| `upset_scenario` | Upset Scenario before kickoff. |
| `scenario_warning` | Scenario Engine or Auditor warning. |
| `shadow_verdict` | Match-level Shadow Verdict. |
| `legacy_top_reason` | Why Legacy Rank 1 was ranked first. |
| `scenario_top_reason` | Why Scenario Rank 1 was ranked first. |
| `post_match_result_summary` | What happened in the actual match. |
| `validation_conclusion` | Legacy Winner / Scenario Winner / Draw / Invalid. |

### Journal Example

```text
Pre-match:
Legacy Top was ranked first because it had the strongest production score.
Scenario Top was ranked first because it had better role balance and served the Main Scenario more completely.

Warning:
Shadow Verdict = Disagreement.

Post-match:
Final score matched the handicap-cover path, but exact-score tail assets missed.

Conclusion:
Scenario Winner, because Scenario Top generated higher ROI with lower drawdown.
```

## 7. Output Format

Each completed match should produce one post-match validation report.

Suggested filename:

```text
docs/post_match_validation/YYYY-MM-DD_match_slug_VALIDATION.md
```

The root latest/manual report can be:

```text
POST_MATCH_VALIDATION_REPORT.md
```

The aggregate report can be:

```text
POST_MATCH_VALIDATION_SUMMARY.md
```

This framework defines the format only. It does not implement report generation.

## 8. Required Per-Match Report Sections

Each report should include:

1. Match
2. Final Result
3. Pre-Match Decision Snapshot
4. Portfolio Validation Table
5. Portfolio Outcome Table
6. Legacy vs Scenario Result
7. Decision Journal
8. Validation Verdict

### Portfolio Validation Table

| Portfolio | Type | Legacy Rank | Legacy Score | Scenario Rank | Scenario Score | Shadow Verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Portfolio A | Legacy Top | 1 | 100 | 4 | 61.9 | Disagreement |
| Portfolio B | Scenario Top | 5 | 100 | 1 | 68.9 | Disagreement |

### Portfolio Outcome Table

| Portfolio | Type | Hit Status | P/L | ROI | Max Drawdown |
| --- | --- | --- | ---: | ---: | ---: |
| Portfolio A | Legacy Top | partial_hit | +120 | 12% | -300 |
| Portfolio B | Scenario Top | hit | +180 | 18% | -220 |

### Legacy vs Scenario Result

```text
Scenario Winner
```

Reason:

- Scenario Top ROI exceeded Legacy Top ROI by more than the material threshold.
- Scenario Top also had lower max drawdown.

## 9. Validation Guardrails

Do not use this framework to change production ranking until enough evidence exists.

Guardrails:

- Do not use post-match data to recalculate pre-match ranks.
- Do not compare a portfolio that did not exist before kickoff.
- Do not replace Legacy Ranking based on one match.
- Do not treat `Scenario Winner` as proof unless results hold across batches.
- Do not ignore drawdown; ROI alone is not enough.
- Do not let one extreme correct-score hit dominate conclusions.

## 10. Decision Rule For Future Replacement

Scenario Ranking can be considered stronger only if, across at least 50 valid matches:

- Scenario ROI is materially higher than Legacy ROI.
- Scenario Win Rate is higher than Legacy Win Rate.
- Scenario does not increase max drawdown.
- Scenario improves disagreement cases where Legacy Rank 1 and Scenario Rank 1 differ.
- Recommendation Auditor warnings correlate with worse post-match outcomes.

If those conditions are not met:

```text
Legacy Ranking remains authoritative.
Scenario Ranking remains observational.
```

## 11. Final Answer This Framework Must Produce

For every validation batch, the final answer should be one of:

| Verdict | Meaning |
| --- | --- |
| `Keep Legacy` | Legacy remains better or evidence is insufficient. |
| `Keep Shadow Mode` | Scenario adds useful signal but is not yet proven. |
| `Promote Scenario Guardrails` | Scenario warnings should influence eligibility but not full ranking. |
| `Consider Scenario Ranking` | Scenario has enough evidence to become a ranking input. |

Current expected status:

```text
Keep Shadow Mode
```

Reason:

- Scenario Ranking has shown meaningful disagreement with Legacy Ranking.
- It has not yet proven long-term superiority through post-match outcomes.
