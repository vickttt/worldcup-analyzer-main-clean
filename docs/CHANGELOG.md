# Changelog

## 2026-06-21

- Implemented Shadow Metadata v0.1 as a metadata-only helper in `modules/shadow_metadata.py`.
- Added `scripts/generate_shadow_metadata_report.py` to validate `strategy["shadow"]` generation on Germany vs Ivory Coast, Scotland vs Morocco, and Brazil vs Haiti saved snapshots.
- Generated `SHADOW_METADATA_REPORT.md`.
- Added only in-memory `strategy["shadow"]` fields during report generation; did not change Legacy Ranking, scores, recommendation logic, UI, or data files.
- Added `INTEGRATION_PLAN_V1.md` to design Scenario Engine, Recommendation Auditor, and Portfolio Ranking 2.0 integration points.
- Mapped current data, recommendation logic, ranking, UI entry points, phased implementation order, and integration risks.
- Added `PORTFOLIO_RANKING_V2_PLAN.md` to define scenario-aware Portfolio Ranking 2.0.
- Designed ranking dimensions, Portfolio Score formula, guardrails, Tail Exposure handling, User Decision Complexity, and My Portfolio parity scoring.
- Ran Recommendation Auditor v0.1 on `SCENARIO_ENGINE_REPORT.md` and generated `docs/RECOMMENDATION_AUDIT_REPORT.md`.
- Refined Scenario Engine read-only script asset mapping so 4-goal correct scores are aggressive upside and 5-goal correct scores are tail/extreme upside, lowering the generated consistency score to 82.
- Added `scripts/generate_scenario_engine_report.py`, a read-only Scenario Engine report generator for saved local snapshots.
- Generated `SCENARIO_ENGINE_REPORT.md` for Germany vs Ivory Coast using existing local data only.
- Added `SCENARIO_ENGINE_AUTOMATION_PLAN.md` to define a read-only automation plan for repeatable Scenario Engine reporting.
- Defined Scenario Engine automation inputs, outputs, workflow, data dependencies, degraded mode, Recommendation Auditor handoff, future Portfolio Ranking fields, and risk controls.
- Added `SCENARIO_ENGINE_PROTOTYPE_REPORT.md`, a v0.1 Scenario Engine sample report for Germany vs Ivory Coast using existing local data only.
- Added `SCENARIO_ENGINE_V1_PLAN.md` to define Scenario Engine v1.
- Designed Main, Secondary, and Upset Scenario structures, asset mapping rules, Scenario Consistency Score, Recommendation Auditor collaboration, and Portfolio Ranking integration.
- Added `RECOMMENDATION_AUDITOR_PLAN.md` to define the Recommendation Auditor audit agent.
- Defined recommendation scenario conflict checks, path conflict rules, asset role alignment checks, Portfolio Ranking dependency checks, user/system parity checks, audit report format, prohibited actions, and future read-only automation path.
- Ran WorldCup Supervisor once and regenerated `docs/DAILY_REPORT.md`.
- Refined `WORLDCUP_SUPERVISOR_PLAN.md` so the Supervisor responsibilities directly match the requested project-manager duties.
- Added `WORLDCUP_SUPERVISOR_PLAN.md` to define the WorldCup Supervisor project-manager agent.
- Defined daily governance checks, required reads, daily report format, main-branch warning, changelog check, and task queue sync rules.
- Initialized project governance documentation under `docs/`.
- Added AI collaboration rules through root `AGENTS.md`.
- Added product principles, task queue, known bugs, QA report, daily report, and setup report.
- Recorded Git baseline and version-risk assessment.
- Did not modify business code, recommendation logic, data scripts, UI pages, or data files.
