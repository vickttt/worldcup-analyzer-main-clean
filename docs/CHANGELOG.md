# Changelog

## 2026-06-21

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
