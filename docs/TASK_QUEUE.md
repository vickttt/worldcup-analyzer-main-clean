# Task Queue

## P0 Agent automation context and workflow rehearsal

- Keep `WORLDCUP.md`, `SUPERVISOR.md`, `docs/TODAY_NEXT_ACTION.md`, `docs/SUBAGENTS.md`, and `docs/HOOKS_GUARDRAILS_PLAN.md` as the required automation context layer.
- Run the first real GitHub Issue -> Branch -> PR rehearsal using a documentation-only task.
- Confirm GitHub Actions Agent QA runs on the PR.
- Confirm Jin can review and approve the PR through GitHub.
- Group current uncommitted files by theme before any further development.
- Keep performance logs out of normal feature commits.
- Keep historical `data/history/*_pre.json` and `data/history/my_portfolios/*.json` in separate data commits only when explicitly approved.
- Keep `docs/CHANGELOG.md`, `docs/QA_REPORT.md`, and `docs/DAILY_REPORT.md` synchronized with completed governance and validation work.
- Use GitHub Issues as the default task source for new agent work.
- Use Pull Requests as the default review and approval path.
- Require GitHub Actions QA before merge once `.github/workflows/agent-qa.yml` is pushed.
- Do not modify production ranking, recommendation logic, UI, or data refresh code during cleanup.

## P1 Commit hygiene and GitHub agent workflow adoption

- Commit Agent Workflow / GitHub Automation documents separately from UI, benchmark, and data work.
- Keep `data/performance_logs/app_performance.jsonl` out of normal commits.
- Keep `.venv`, `__pycache__`, and secrets out of Git.
- Do not mix workflow infrastructure with product behavior changes.

## P2 Historical odds backfill plan

- Use `API_FOOTBALL_HISTORICAL_ODDS_CHECK.md` as the capability baseline.
- Use `WORLD_CUP_HISTORICAL_ODDS_BACKFILL_PLAN.md` as the safety and benchmark design baseline.
- Next implementation gate: Phase A, historical odds quality check on 3 sample matches only.
- Design a safe backfill pipeline that reads API-Football odds by official fixture/date, not by stale local fixture IDs.
- Store backfilled snapshots only in an isolated directory such as `data/history/backfill/`.
- Do not overwrite existing manual history snapshots.
- Require `odds_timestamp < kickoff_time` before marking a snapshot as true pre-match data.

## P3 Hybrid Ranking benchmark

- Continue Phase A report-only validation for Hybrid Ranking.
- Compare Legacy Top, Scenario Top, and Hybrid Top across historical snapshots.
- Use benchmark results before changing production sorting.
- Keep `strategy_score(...)`, `evaluate_allocation(...)`, and `strategy_comparison(...)` production behavior unchanged until an explicit implementation task is approved.

## P4 Scenario Guardrails UI / eligibility design

- Design how Scenario Guardrails should appear in the Portfolio Ranking UI.
- Keep Legacy ranking visible as reference during any transition.
- Add warnings for `Shadow Verdict = Disagreement`, tail-heavy portfolios, pure-tempo portfolios, and low-consistency portfolios.
- Do not promote Scenario or Hybrid signals into default recommendation eligibility without explicit review.
