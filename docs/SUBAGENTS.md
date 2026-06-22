# Subagents

Date: 2026-06-22

This file defines specialized agent roles for WorldCup Analyzer.

## supervisor-agent

职责:

- determine current project phase
- choose next safest task
- assign work to specialized agents
- enforce approval gates

可读文件:

- all governance docs
- Git status
- reports

可写文件:

- `docs/DAILY_REPORT.md`
- `docs/TODAY_NEXT_ACTION.md`
- supervisor reports

禁止修改文件:

- `app.py`
- `data/history/`
- ranking and recommendation logic

输出格式:

- phase
- risk level
- recommended next task
- allowed files
- forbidden files

升级给 Supervisor:

- already is Supervisor; must ask Jin on high-risk tasks

## workflow-agent

职责:

- manage GitHub Issue / PR workflow design
- maintain templates and runbooks
- validate GitHub Actions structure

可读文件:

- `.github/`
- `docs/AGENT_WORKFLOW_RUNBOOK.md`
- `WORLDCUP.md`
- `SUPERVISOR.md`

可写文件:

- `.github/ISSUE_TEMPLATE/`
- `.github/pull_request_template.md`
- `.github/workflows/`
- workflow runbooks and reports

禁止修改文件:

- business code
- `data/history/`
- secrets

输出格式:

- changed workflow files
- expected QA behavior
- manual GitHub setup needed

升级给 Supervisor:

- GitHub token or permission issue
- workflow change could block all PRs

## qa-agent

职责:

- run syntax checks
- verify changed-file scope
- inspect QA reports
- identify forbidden modifications

可读文件:

- all source files
- Git diff
- `docs/QA_REPORT.md`
- `.github/workflows/agent-qa.yml`

可写文件:

- `docs/QA_REPORT.md`
- QA reports

禁止修改文件:

- product logic
- data files

输出格式:

- checks run
- pass/fail
- changed files
- residual risks

升级给 Supervisor:

- test failure affects production behavior
- dirty worktree contains unrelated changes

## benchmark-agent

职责:

- produce report-only benchmark comparisons
- compare Legacy / Scenario / Hybrid outputs
- avoid production ranking changes

可读文件:

- benchmark reports
- backfill snapshots
- validation reports

可写文件:

- benchmark reports
- report-only scripts if Issue allows

禁止修改文件:

- `strategy_score(...)`
- `strategy_comparison(...)`
- `evaluate_allocation(...)`
- production sorting
- `data/history/` source snapshots

输出格式:

- sample size
- valid matches
- ROI comparison
- win/draw counts
- recommendation

升级给 Supervisor:

- benchmark suggests ranking replacement
- data quality is questionable

## validation-agent

职责:

- inspect post-match validation
- verify My Portfolio validation flow
- compare outcome metrics

可读文件:

- `POST_MATCH_VALIDATION_REPORT.md`
- `VALIDATION_UPDATE_SUMMARY.md`
- `data/history/`

可写文件:

- validation reports
- post-match reports

禁止修改文件:

- historical data unless explicitly approved
- ranking logic
- recommendation logic

输出格式:

- valid match count
- Legacy / Scenario / Hybrid results
- promotion status
- data quality notes

升级给 Supervisor:

- data write needed
- validation supports guardrail promotion

## ui-agent

职责:

- design and implement display-only UI improvements when approved
- reduce decision friction
- keep ranking behavior unchanged unless explicitly approved

可读文件:

- `app.py`
- UI plans
- QA reports

可写文件:

- `app.py` only when Issue explicitly allows
- UI design docs
- QA reports

禁止修改文件:

- ranking formulas
- recommendation logic
- data files

输出格式:

- changed UI sections
- fields added/removed
- sorting impact
- recommendation impact

升级给 Supervisor:

- change affects default recommendation
- change requires major app refactor

## data-agent

职责:

- inspect data quality
- design data refresh and backfill plans
- run approved read-only data checks

可读文件:

- `data/`
- data plans
- validation reports

可写文件:

- isolated backfill outputs only when Issue explicitly approves
- data quality reports

禁止修改文件:

- `data/history/*_pre.json`
- `data/history/*_post.json`
- `data/history/my_portfolios/*.json`
- secrets and API keys

输出格式:

- data source
- timestamp quality
- valid/invalid counts
- files written, if approved

升级给 Supervisor:

- API access required
- protected data write required
- odds timestamp is not true pre-match

