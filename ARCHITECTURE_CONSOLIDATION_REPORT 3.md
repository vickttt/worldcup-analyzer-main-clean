# Architecture Consolidation Report

Date: 2026-06-21

Scope: architecture summary only. This report does not design new modules, write code, change business logic, modify data, update UI, create branches, commit, or push.

## 1. Current Project Architecture

Current target architecture:

```text
Data
  ↓
Scenario Engine
  ↓
Recommendation Auditor
  ↓
Portfolio Ranking
  ↓
Decision
```

### Data

Role:

- Provides match, odds, fixture, historical snapshot, recommendation, portfolio, and user portfolio inputs.

Current sources:

- `data/worldcup2026/<match_slug>/pre_match.json`
- `data/worldcup2026/<match_slug>/odds.json`
- `data/worldcup2026/<match_slug>/fixture.json`
- `data/history/*_pre.json`
- `data/history/*_post.json`
- `data/history/my_portfolios/*.json`

Current principle:

- API data is refreshed by terminal scripts.
- Web UI is responsible for display, not data refresh.
- Historical pre/post data must be preserved.

### Scenario Engine

Role:

- Converts raw recommendations and portfolio assets into Main, Secondary, and Upset scenario structure.
- Maps assets into Direction, Tempo, Return, Insurance, and Tail roles.
- Produces Scenario Consistency Score.

Current status:

- Designed.
- Prototype report completed.
- Read-only automation plan completed.
- Read-only script exists for report generation.

### Recommendation Auditor

Role:

- Checks whether recommendation assets serve coherent scenarios.
- Flags path conflicts such as Over3.5 with 1:0 or 2:0.
- Confirms whether aggressive and tail assets are properly downgraded.
- Produces recommendation audit status and severity.

Current status:

- Designed.
- One audit report completed against Scenario Engine output.

### Portfolio Ranking

Role:

- Ranks system portfolios and eventually My Portfolio using both value metrics and scenario-aware metrics.

Current production behavior:

- Existing ranking remains legacy behavior.
- Current score remains driven mainly by EV, ROI, Sharpe, risk, and existing path consistency.

Target behavior:

- Portfolio Ranking 2.0 consumes Scenario Consistency Score, Tail Exposure, Asset Role Balance, Main Scenario Coverage, Secondary Insurance Coverage, and Auditor warnings.

Current status:

- Portfolio Ranking 2.0 designed.
- Shadow Mode designed.
- Not yet implemented into production ranking.

### Decision

Role:

- Presents the final user-facing recommendation and portfolio decision.

Current principle:

- User decision efficiency has priority over metric volume.
- Scenario and audit outputs should improve clarity, not add confusing dashboard noise.

## 2. Completed Modules

| Module | Completion | Status | Implemented | Design Only |
| --- | ---: | --- | --- | --- |
| Project Governance | Complete | Active governance docs created | Yes | No |
| WorldCup Supervisor | Complete | Project-manager agent designed and run once | Partially, report workflow used manually | No |
| Recommendation Auditor | Complete for v0.1 | Audit rules and report format defined; audit report generated | Partially, report produced manually | No |
| Scenario Engine v1 | Complete as design | Scenario model, asset mapping, consistency score defined | No | Yes |
| Scenario Engine Prototype v0.1 | Complete | Germany vs Ivory Coast sample report produced | Yes, report artifact | No |
| Scenario Engine Read-Only Automation | Complete as plan | Repeatable read-only workflow designed | No | Yes |
| Scenario Engine Script v0.1 | Complete | Generates `SCENARIO_ENGINE_REPORT.md` from local data | Yes | No |
| Portfolio Ranking 2.0 | Complete as design | New dimensions and guardrails defined | No | Yes |
| Integration Plan v1 | Complete | Scenario → Auditor → Ranking connection designed | No | Yes |
| Phase 2 Readiness Report | Complete | Code impact and risk map completed | No | Yes |
| Portfolio Ranking Shadow Mode | Complete as design | Parallel ranking validation plan defined | No | Yes |

## 3. Unfinished Modules

### Phase 2 Unfinished Work

Phase 2 is the metadata and shadow-validation phase.

Unfinished Phase 2 items:

- Add Scenario Engine output as optional snapshot metadata.
- Add Recommendation Auditor output as optional snapshot metadata.
- Add Shadow Mode ranking output as optional metadata.
- Keep legacy ranking authoritative.
- Keep existing sort order unchanged.
- Keep existing recommendation output unchanged.
- Validate scenario-aware fields across more matches.

Phase 2 must not change:

- `strategy_score(...)`
- `evaluate_allocation(...)`
- `strategy_comparison(...)`
- default recommendation selection
- user-visible ranking order
- production decision logic

### Phase 3 Unfinished Work

Phase 3 is the controlled replacement phase.

Unfinished Phase 3 items:

- Make Scenario Rank visible in the UI after Shadow Mode validation.
- Use Auditor severity as a ranking guardrail.
- Make Scenario Consistency Score a first-class Portfolio Ranking input.
- Apply Tail Exposure penalties to default recommendation eligibility.
- Rank My Portfolio with the same scenario-aware logic as system portfolios.
- Consider replacing or augmenting legacy ranking only after enough completed-match evidence.

Phase 3 must be gated by:

- Shadow Mode evidence.
- Post-match review.
- No High/Critical unresolved audit conflicts.
- Stable snapshot and replay compatibility.

## 4. Current Roadmap

### Phase 2

Goal:

- Integrate scenario-aware metadata without changing production behavior.

Work:

- Scenario Engine runs beside current recommendation flow.
- Recommendation Auditor runs after Scenario Engine.
- Portfolio Ranking Shadow Mode calculates Scenario Rank beside Legacy Rank.
- Snapshot stores optional fields:
  - `scenario_engine`
  - `recommendation_audit`
  - `portfolio_ranking_shadow`
- Reports compare Legacy Rank and Scenario Rank.

Success condition:

- The project can observe whether Scenario-aware Ranking improves decisions while legacy ranking remains authoritative.

### Phase 3

Goal:

- Promote validated scenario-aware signals into user-visible ranking and decision logic.

Work:

- Surface Scenario Rank and audit warnings in UI.
- Add Ranking 2.0 guardrails.
- Decide whether Scenario Rank can affect default recommendation.
- Apply the same evaluation framework to My Portfolio.

Success condition:

- Scenario-aware ranking improves decision quality without reducing clarity or breaking existing snapshot/post-match/replay flows.

## 5. Most Important Next Step

Only one next step:

Implement Portfolio Ranking Shadow Mode as a read-only, non-authoritative metadata/reporting layer.

Reason:

- It is the safest bridge between current legacy ranking and Portfolio Ranking 2.0.
- It does not require changing ranking order.
- It does not require changing recommendation output.
- It gives evidence before replacing any production logic.
- It directly tests whether Scenario Consistency Score, Tail Exposure, Asset Role Balance, and Auditor warnings should influence future ranking.

Implementation boundary for that next step:

- Legacy Ranking remains authoritative.
- Scenario Rank is calculated in parallel only.
- Rank differences are recorded.
- No UI decision logic changes.
- No production score replacement.
