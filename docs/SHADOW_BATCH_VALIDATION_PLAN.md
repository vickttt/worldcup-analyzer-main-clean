# Shadow Mode Batch Validation Plan

Date: 2026-06-21

Scope: design only. This plan does not write code, change business logic, modify UI, change Ranking, modify recommendation logic, refresh API data, create branches, commit, or push.

## Goal

Batch-validate Portfolio Ranking Shadow Mode across historical matches.

Germany vs Ivory Coast showed a clear case where:

```text
Legacy Rank = 1
Scenario Rank = 4
```

That single result is useful, but not enough to replace or change Ranking. Batch validation exists to collect enough match evidence before any production ranking decision.

## 1. Batch Input Sources

Batch validation should read historical local snapshots only.

Primary source:

- `data/history/*_pre.json`

Optional supporting sources:

- `data/history/*_post.json`
- `data/history/my_portfolios/*.json`
- `data/worldcup2026/<match_slug>/pre_match.json`
- `data/worldcup2026/<match_slug>/odds.json`
- `data/worldcup2026/<match_slug>/fixture.json`
- existing `SCENARIO_ENGINE_REPORT.md` for current manual sample

Required minimum data per match:

- match identity
- `strategy_snapshot.strategies`
- each strategy's existing legacy `score`
- each strategy's existing order or rank
- strategy items
- expected yield / ROI proxy
- Sharpe
- path consistency or consistency score
- role exposure or role constraint data

If a match lacks `strategy_snapshot.strategies`, it should be skipped and recorded as `insufficient_data`.

## 2. Batch Workflow

Recommended batch flow:

```text
Discover historical pre-match snapshots
  ↓
Load each eligible match snapshot
  ↓
Extract Legacy Ranking
  ↓
Compute Scenario Ranking in Shadow Mode
  ↓
Compare ranks
  ↓
Generate per-match Shadow Report
  ↓
Append batch summary row
  ↓
Aggregate 20 / 30 / 50 match validation metrics
```

Important rule:

```text
Legacy Ranking remains authoritative.
Scenario Ranking is observational only.
```

## 3. Per-Match Shadow Report

For each eligible match, generate one report using the existing single-match format.

Suggested report location:

```text
docs/shadow_reports/YYYY-MM-DD_match_slug_PORTFOLIO_RANKING_SHADOW_REPORT.md
```

Report filename examples:

- `docs/shadow_reports/2026-06-20_germany_ivory_coast_PORTFOLIO_RANKING_SHADOW_REPORT.md`
- `docs/shadow_reports/2026-06-21_team_a_team_b_PORTFOLIO_RANKING_SHADOW_REPORT.md`

Each per-match report should include:

- Match
- Source snapshot
- Legacy Top Portfolio
- Scenario Top Portfolio
- Ranking table
- Rank Difference summary
- Tail-heavy downgrade findings
- Critical conflict downgrade findings
- Shadow Verdict
- Automation Verdict

The existing root-level `PORTFOLIO_RANKING_SHADOW_REPORT.md` can remain the latest/manual sample report.

## 4. Batch Summary Output

Batch validation should also generate one aggregate summary.

Suggested output:

```text
SHADOW_BATCH_VALIDATION_REPORT.md
```

Suggested structured data output, if needed later:

```text
docs/shadow_reports/shadow_batch_results.json
docs/shadow_reports/shadow_batch_results.csv
```

This plan defines the outputs only. It does not implement them.

## 5. Fields To Record Per Portfolio

Each portfolio row should record:

| Field | Meaning |
| --- | --- |
| `match_id` | Stable match identifier or slug. |
| `match_name` | Human-readable match name. |
| `snapshot_path` | Source historical pre-match snapshot. |
| `portfolio_name` | Strategy or portfolio name. |
| `legacy_rank` | Production rank from existing snapshot order. |
| `legacy_score` | Existing production score. |
| `scenario_score` | Shadow scenario-aware score. |
| `scenario_rank` | Shadow rank. |
| `rank_difference` | `scenario_rank - legacy_rank`. |
| `ev` | Existing EV or expected profit/yield signal. |
| `roi` | Existing expected yield / capital efficiency. |
| `sharpe` | Existing Sharpe ratio. |
| `scenario_consistency_score` | Existing or computed consistency score. |
| `tail_exposure` | Tail share from role exposure or inferred assets. |
| `asset_role_balance` | Existing role constraint or computed role balance. |
| `main_scenario_coverage` | Whether portfolio serves Main Scenario. |
| `secondary_insurance_coverage` | Whether portfolio protects secondary path. |
| `audit_status` | Pass / Warning / Fail when available. |
| `audit_severity` | None / Low / Medium / High / Critical. |
| `conflict_flags` | Detected path conflicts. |
| `shadow_verdict` | Agreement / Watch / Disagreement / Blocker Candidate. |

## 6. Fields To Record Per Match

Each match summary row should record:

| Field | Meaning |
| --- | --- |
| `match_id` | Match identifier. |
| `match_name` | Human-readable match name. |
| `snapshot_path` | Source snapshot path. |
| `eligible` | Whether match had enough data. |
| `skip_reason` | Reason if not eligible. |
| `legacy_top_portfolio` | Portfolio ranked first by legacy ranking. |
| `scenario_top_portfolio` | Portfolio ranked first by Scenario Ranking. |
| `legacy_top_scenario_rank` | Scenario Rank of the Legacy top portfolio. |
| `legacy_top_rank_difference` | Rank Difference for Legacy top portfolio. |
| `agreement` | Whether Legacy top equals Scenario top. |
| `max_rank_difference` | Largest absolute rank movement. |
| `tail_heavy_downgrade_count` | Count of tail-heavy portfolios downgraded by Scenario Ranking. |
| `critical_conflict_downgrade_count` | Count of Critical conflict portfolios downgraded by Scenario Ranking. |
| `high_conflict_downgrade_count` | Count of High conflict portfolios downgraded by Scenario Ranking. |
| `shadow_verdict` | Overall match-level verdict. |

## 7. Metrics To Calculate

### Agreement Rate

Definition:

```text
Agreement Rate =
  matches where Legacy Top Portfolio = Scenario Top Portfolio
  / eligible matches
```

Interpretation:

- High Agreement Rate means Shadow Ranking mostly agrees with production.
- Low Agreement Rate means Scenario-aware ranking is materially different and needs review.

### Disagreement Rate

Definition:

```text
Disagreement Rate =
  matches where Legacy Top Portfolio != Scenario Top Portfolio
  / eligible matches
```

This is the inverse of Agreement Rate.

### Legacy Rank 1 But Scenario Rank Not 1

Definition:

```text
Legacy Rank 1 but Scenario Rank != 1 =
  count of matches where the production top portfolio is not Scenario Rank 1
```

This is the primary watch metric.

Severity buckets:

| Condition | Severity |
| --- | --- |
| Legacy top Scenario Rank = 2 | Low |
| Legacy top Scenario Rank = 3 | Medium |
| Legacy top Scenario Rank >= 4 | High |

Germany vs Ivory Coast example:

```text
Legacy top: 让球策略
Scenario Rank: 4
Severity: High watch case
```

### Tail-Heavy Downgrade

Definition:

```text
Tail-heavy downgrade =
  portfolio has tail exposure above threshold
  and Scenario Rank is worse than Legacy Rank
```

Suggested thresholds:

- Tail Exposure > 15%: warning.
- Tail Exposure > 20%: tail-heavy.
- Tail Exposure > 35%: cannot be default recommendation in future Ranking 2.0.

Metrics:

- number of tail-heavy portfolios
- number of tail-heavy portfolios downgraded
- downgrade rate among tail-heavy portfolios
- number of tail-heavy legacy top portfolios

### Critical Conflict Downgrade

Definition:

```text
Critical conflict downgrade =
  portfolio has Critical conflict
  and Scenario Rank is worse than Legacy Rank
```

Metrics:

- Critical conflict count
- Critical conflict downgrade count
- Critical conflict not-downgraded count

Critical conflict not-downgraded should trigger rule review.

### High Conflict Downgrade

Definition:

```text
High conflict downgrade =
  portfolio has High conflict
  and Scenario Rank is worse than Legacy Rank
```

High conflict downgrade is useful but not as strict as Critical conflict downgrade.

## 8. 20 / 30 / 50 Match Validation Windows

### 20-Match Checkpoint

Purpose:

- Confirm Shadow Mode is stable enough for continued observation.

Minimum questions:

- Can all eligible matches generate Shadow Reports?
- How many matches are skipped for missing data?
- How often does Legacy Rank 1 differ from Scenario Rank 1?
- Are tail-heavy portfolios consistently downgraded?
- Are Critical conflicts downgraded?

Pass condition:

- Batch process can produce reports without modifying data.
- Metrics are explainable.
- No evidence that Scenario Ranking creates obvious worse decisions.

Decision after 20 matches:

- Continue Shadow Mode.
- Do not replace Legacy Ranking yet.
- Consider limited internal review of Scenario Rank differences.

### 30-Match Checkpoint

Purpose:

- Check whether disagreement patterns are stable across match types.

Required breakdown:

- favorite-heavy matches
- balanced matches
- upset-sensitive matches
- correct-score-rich matches
- low-tempo matches
- high-tempo matches

Questions:

- Does Scenario Ranking only disagree in specific match types?
- Does it over-downgrade insurance-heavy portfolios?
- Does it properly downgrade tail-heavy portfolios?
- Does it avoid promoting low-clarity portfolios?

Pass condition:

- Disagreements have consistent explanations.
- Tail-heavy downgrades are intentional.
- Critical/High conflicts are downgraded.
- Legacy top disagreement cases are reviewable.

Decision after 30 matches:

- Keep Legacy Ranking authoritative.
- Prepare Phase 3 UI-readiness review only if post-match evidence supports Scenario Rank.

### 50-Match Checkpoint

Purpose:

- Decide whether Scenario Ranking is mature enough for controlled promotion.

Required evidence:

- Agreement / Disagreement trend is stable.
- Scenario Ranking improves post-match audit quality.
- Legacy Rank 1 disagreement cases are explainable.
- Tail-heavy and conflict portfolios are handled better than Legacy Ranking.
- User decision clarity is not worse.
- Snapshot and replay compatibility remain intact.

Possible decisions:

| Result | Action |
| --- | --- |
| Scenario Rank consistently improves decisions | Consider Phase 3 limited UI display. |
| Scenario Rank is mixed but explainable | Continue Shadow Mode and refine scoring. |
| Scenario Rank creates unclear or worse outcomes | Keep Legacy Ranking and revise Shadow formula. |

Important:

Even after 50 matches, replacement should not happen automatically. It requires explicit user approval.

## 9. Batch Report Format

Suggested `SHADOW_BATCH_VALIDATION_REPORT.md` structure:

```markdown
# Shadow Batch Validation Report

## Summary

- Eligible matches:
- Skipped matches:
- Agreement Rate:
- Disagreement Rate:
- Legacy Rank 1 but Scenario Rank not 1:
- Tail-heavy downgrade rate:
- Critical conflict downgrade rate:
- Overall verdict:

## Match-Level Results

| Match | Legacy Top | Scenario Top | Legacy Top Scenario Rank | Difference | Verdict |
| --- | --- | --- | ---: | ---: | --- |

## Portfolio-Level Highlights

### Largest Legacy Downgrades

### Largest Scenario Upgrades

### Tail-Heavy Downgrades

### Critical Conflict Downgrades

## 20 / 30 / 50 Match Checkpoints

## Replacement Readiness

## Required Follow-Ups
```

## 10. Validation Rules

Batch validation must preserve these rules:

- Do not modify `strategy_score(...)`.
- Do not modify `evaluate_allocation(...)`.
- Do not modify `strategy_comparison(...)`.
- Do not change recommendation output.
- Do not change production ranking order.
- Do not change UI decision logic.
- Do not modify data files.
- Do not refresh API data.

## 11. Success Criteria

Shadow Batch Validation is successful when:

- historical eligible matches can be processed consistently
- every match gets a per-match Shadow Report
- batch summary records Legacy Rank, Scenario Rank, and Rank Difference
- Agreement Rate and Disagreement Rate are measurable
- Legacy Rank 1 but Scenario Rank not 1 cases are easy to inspect
- tail-heavy portfolios are tracked
- Critical and High conflict downgrades are tracked
- 20 / 30 / 50 match checkpoints produce clear replacement readiness signals

## Final Recommendation

Run Shadow Mode in batch before any Ranking 2.0 production change.

The next implementation should remain report-only:

1. Read historical snapshots.
2. Generate per-match Shadow Reports.
3. Generate one batch validation summary.
4. Keep Legacy Ranking authoritative.
5. Use 20 / 30 / 50 match checkpoints to decide whether Phase 3 should proceed.
