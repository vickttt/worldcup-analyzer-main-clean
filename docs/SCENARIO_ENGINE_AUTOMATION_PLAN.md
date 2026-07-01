# Scenario Engine Read-Only Automation Plan

## Goal

Turn Scenario Engine Prototype v0.1 into a repeatable read-only reporting workflow.

This plan does not rewrite recommendation logic, modify UI, modify Portfolio Ranking, refresh API data, or mutate project data files. It only defines how a future read-only automation should load existing snapshots and generate a Scenario Engine report.

## Inputs

Scenario Engine automation should read from existing local files only.

## Primary Match Inputs

For a selected match folder such as `data/worldcup2026/YYYY_MM_DD_Home_Away/`:

- `pre_match.json`
- `odds.json`
- `fixture.json`

## Historical Snapshot Inputs

When available:

- `data/history/YYYY_MM_DD_Home_Away_pre.json`
- `data/history/YYYY_MM_DD_Home_Away_post.json`
- `data/history/my_portfolios/YYYY_MM_DD_Home_Away.json`

## Optional Context Inputs

When present and already saved locally:

- `lineups.json`
- `injuries.json`
- `players.json`
- `team_stats.json`
- `match_stats.json`
- `events.json`
- `post_match.json`

These files are optional. Missing optional context must not block report generation.

## Output

The automation should generate:

- `SCENARIO_ENGINE_REPORT.md`

The report format should follow `SCENARIO_ENGINE_PROTOTYPE_REPORT.md`:

- Match
- Source Snapshot Summary
- Main Scenario
- Secondary Scenario
- Upset Scenario
- Asset Mapping
- Scenario Consistency Score
- Score Breakdown
- Consistency Findings
- Recommendation Auditor Handoff
- Portfolio Ranking Implication
- Prototype / Automation Verdict

Future match-specific report location, if needed:

- `docs/scenario_reports/YYYY-MM-DD_match_slug.md`

## Workflow

```text
Snapshot
↓
Scenario Detection
↓
Asset Mapping
↓
Consistency Score
↓
Report
```

## Step 1: Snapshot

Load existing local data without refreshing anything.

Read order:

1. Historical pre-match snapshot, if available.
2. WorldCup data-center `pre_match.json`.
3. `odds.json`.
4. `fixture.json`.
5. Optional context files.

Snapshot step must collect:

- Match identity.
- Fixture metadata.
- Recommendation output.
- Portfolio list.
- Asset role list.
- Probability/path distribution.
- Risk paths.
- Odds market structure.
- Data source and snapshot timestamps.

## Step 2: Scenario Detection

Infer three scenario layers:

- Main Scenario.
- Secondary Scenario.
- Upset Scenario.

Detection should use:

- Existing probability distribution.
- Existing path labels such as favorite win by 1, favorite win by 2, favorite win by 3+, draw zone, underdog unbeaten.
- Final recommendation.
- Handicap line.
- Winner probability.
- Total line.
- Correct score candidates.
- Risk path notes.

Scenario Detection must not invent unavailable precision. If the source data lacks enough probability detail, mark data confidence as low and generate qualitative scenarios.

## Step 3: Asset Mapping

Map current system assets into Scenario Engine roles:

- Direction Asset.
- Tempo Asset.
- Return Asset.
- Insurance Asset.
- Tail Asset.

Mapping inputs:

- Portfolio items.
- `asset_roles`.
- Market type.
- Selection.
- Odds.
- Probability.
- Share / amount.
- Existing path consistency fields.
- Existing conflict or not-recommended reasons.

Mapping rules:

- Winner and handicap assets normally map to Direction Asset.
- Totals map to Tempo Asset unless used as explicit hedge.
- Correct scores near the main path map to Return Asset.
- Assets protecting a named main-scenario failure map to Insurance Asset.
- Low-probability upset or extreme score paths map to Tail Asset.

## Step 4: Consistency Score

Calculate Scenario Consistency Score from 0 to 100.

Recommended components:

| Component | Points |
| --- | ---: |
| Scenario assignment coverage | 20 |
| Direction alignment | 20 |
| Tempo and score alignment | 20 |
| Role coherence | 15 |
| Conflict penalty control | 15 |
| Evidence support | 10 |

Critical overrides:

- Over3.5 with 1:0 or 2:0 as primary drivers: maximum 40.
- Opposite winner directions without hedge labels: maximum 50.
- No scenario labels available: maximum 60.
- Tail Asset drives first place without explanation: maximum 65.

The score must include a short explanation and component breakdown.

## Step 5: Report

Generate `SCENARIO_ENGINE_REPORT.md` in Markdown.

The report must clearly state:

- Which files were read.
- Which fields were missing.
- Whether the report ran in full mode or degraded mode.
- The three scenarios.
- Asset mapping.
- Scenario Consistency Score.
- Recommendation Auditor handoff notes.
- Portfolio Ranking fields that could use the output later.

## Required Fields

The automation should require enough data to identify the match and at least one recommendation or portfolio.

Required fields:

- Match display name or home/away names.
- Pre-match snapshot or equivalent recommendation snapshot.
- At least one recommendation item, portfolio item, or strategy candidate.
- Market type or asset type for each mapped recommendation item.
- Selection name for each mapped recommendation item.

## Strongly Preferred Fields

These fields enable full-mode reporting:

- `probability_distribution`.
- `risk_paths`.
- `asset_roles`.
- `portfolios`.
- `recommendation_combo`.
- `strategy_snapshot.strategy_table`.
- `decision.final_recommendation`.
- Winner probability.
- Handicap line.
- Total line.
- Correct score candidates.
- Existing path consistency fields.

## Optional Fields

These improve evidence quality but must not block report generation:

- `lineups.json`.
- `injuries.json`.
- `players.json`.
- `team_stats.json`.
- `match_stats.json`.
- `events.json`.
- `post_match.json`.
- User portfolio snapshot.
- Polymarket fields.
- Market disagreement fields.
- Value rating breakdown.

## Degraded Mode

If fields are missing, automation should still generate a report with warnings.

Degradation rules:

- Missing `probability_distribution`: infer scenarios from recommendation, handicap, totals, and correct scores; mark probability confidence low.
- Missing `asset_roles`: infer roles from market type and selection; mark role confidence low.
- Missing `portfolios`: use `recommendation_combo` or strategy candidates; if neither exists, report cannot map assets.
- Missing `risk_paths`: derive simple risk notes from handicap, winner direction, total, and score paths.
- Missing correct score data: skip score-path mapping and lower evidence support.
- Missing odds data: report scenario structure but skip value/market evidence.
- Missing fixture metadata: use match name from snapshots and mark fixture context incomplete.

Minimum viable report:

- Match.
- Data limitations.
- Main Scenario.
- Asset Mapping from available recommendations.
- Scenario Consistency Score with low-confidence warning.

## Recommendation Auditor Integration

Scenario Engine should output these fields for Recommendation Auditor:

- Main Scenario.
- Secondary Scenario.
- Upset Scenario.
- Scenario probabilities.
- Expected scores.
- Goal ranges.
- Tempo labels.
- Match direction.
- Supporting evidence.
- Risk notes.
- Asset-to-scenario mapping.
- Asset role labels.
- Scenario Consistency Score.
- Score breakdown.
- Critical conflict flags.
- Missing-data warnings.

Recommendation Auditor should use these fields to check:

- Whether assets serve the assigned scenario.
- Whether primary drivers contain obvious path conflicts.
- Whether Over3.5 conflicts with 1:0 or 2:0.
- Whether insurance and tail assets are labeled correctly.
- Whether user and system portfolios use the same scenario logic.
- Whether Portfolio Ranking respects scenario consistency.

## Future Portfolio Ranking Integration

This automation should not change Portfolio Ranking yet.

Future Ranking may consume these fields:

- `scenario_consistency_score`.
- `main_scenario_probability`.
- `secondary_scenario_probability`.
- `upset_scenario_probability`.
- `main_scenario_coverage`.
- `secondary_insurance_coverage`.
- `tail_exposure`.
- `critical_conflict_count`.
- `asset_role_balance`.
- `data_confidence`.
- `user_decision_complexity`.

Future Portfolio Score concept:

```text
Portfolio Score =
  EV / ROI / Sharpe value layer
  + Scenario Consistency layer
  + Role Balance layer
  - Critical Conflict penalty
  - User Decision Complexity penalty
  - Data Confidence penalty
```

Ranking guardrails for future implementation:

- Critical scenario conflict cannot rank first.
- Main recommendation should require Scenario Consistency Score >= 75.
- Score below 60 should be marked with an audit warning.
- Tail-driven portfolios should be labeled aggressive/upset, not default recommendation.
- User portfolio and system portfolio should use the same consistency fields.

## Risk Controls

The automation must be read-only.

It must not modify:

- `app.py`.
- UI code.
- Recommendation logic.
- Portfolio Ranking logic.
- Data files.
- Historical snapshots.
- API cache files.

It must not:

- Refresh API data.
- Run the Streamlit app.
- Create branches.
- Commit Git changes.
- Push to GitHub.
- Force push.
- Rewrite Git history.
- Delete files.

Allowed write target:

- `SCENARIO_ENGINE_REPORT.md`

If match-specific reports are later enabled, only write report files under an approved docs/report folder.

## Validation Plan

Initial validation should use existing local matches only.

Recommended first validation cases:

- Germany vs Ivory Coast, because Prototype v0.1 already proved the report format.
- A match where the main recommendation includes correct scores.
- A match where the top path conflicts with the main handicap.
- A match with missing optional files to test degraded mode.

Validation checks:

- Report is reproducible from the same snapshots.
- No data files are modified.
- No API calls are made.
- No app is run.
- Scenario Consistency Score includes a component breakdown.
- Recommendation Auditor can read the output without additional interpretation.

## Acceptance Criteria

Scenario Engine read-only automation is ready to implement when:

- Inputs are defined.
- Output report path and format are defined.
- Snapshot-to-report workflow is defined.
- Required, preferred, optional, and degraded fields are defined.
- Recommendation Auditor handoff is defined.
- Future Portfolio Ranking fields are defined.
- Risk controls explicitly forbid business logic, UI, data, Git, branch, app, and API side effects.

