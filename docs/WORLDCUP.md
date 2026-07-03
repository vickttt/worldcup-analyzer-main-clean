# DEPRECATED — HISTORICAL REFERENCE ONLY

This document is no longer an active workflow authority.
The current active repository rules are defined only in AGENTS.md.

Current active workflow:
- dev-clean is the only development branch
- no automatic branch creation or branch switching
- Codex is the only execution engine
- Claude is read-only review only
- the user is the final decision authority
- no parallel agent workflows are allowed
- old Issue -> Branch -> PR, Supervisor-driven branch workflows, and multi-agent automation loops must not be followed unless explicitly re-approved by the user

Do not use this document as execution guidance unless AGENTS.md is explicitly updated to restore it.

# WorldCup Analyzer

Date: 2026-06-22

This file is the top-level context document for agents working on WorldCup Analyzer.

## Project Goal

WorldCup Analyzer helps Jin make pre-match betting decisions by combining market odds, scenario logic, portfolio ranking, user portfolio tracking, and post-match validation.

The product goal is not to maximize isolated metrics. The product goal is to improve decision quality:

- clearer match-level betting judgement
- scenario-consistent recommendations
- auditable portfolio construction
- measurable post-match validation
- safer automation through GitHub Issues, PRs, and QA gates

## Current Product Status

Current stage: **Validation / Guardrails Transition**

The project has moved beyond raw recommendation generation. It now has:

- Scenario Engine design and read-only reporting
- Recommendation Auditor design and reports
- Shadow Metadata
- Visible Shadow Mode
- Hybrid Ranking report-only work
- Post-Match Validation
- GitHub Issue / PR workflow infrastructure

Current ranking posture:

- Legacy ranking is still a known baseline.
- Scenario ranking has shown decision value.
- Hybrid ranking is a candidate replacement path, but production sorting must not be changed without explicit approval.

## Current Automation Status

Completed automation infrastructure:

- GitHub Issue template
- Pull Request template
- GitHub Actions Agent QA workflow
- Agent workflow runbook
- GitHub CLI installation attempted and documented
- Agent workflow smoke-test document

Current automation gap:

- Agents can read project context and prepare work, but full Issue -> Branch -> PR execution should still be validated through the first real GitHub workflow rehearsal.

## Current Core Modules

- Scenario Engine
- Recommendation Auditor
- Shadow Metadata
- Visible Shadow Mode
- Hybrid Ranking reports
- Post-Match Validation
- Portfolio Ranking UI
- My Portfolio capture and validation
- GitHub Agent Workflow

## Current Forbidden Areas

Agents must not modify these areas without explicit Issue approval:

- `app.py` production ranking behavior
- `strategy_score(...)`
- `strategy_comparison(...)`
- `evaluate_allocation(...)`
- recommendation logic
- default recommendation selection
- `data/history/*_pre.json`
- `data/history/*_post.json`
- `data/history/my_portfolios/*.json`
- secrets, tokens, credentials, `.env`
- Git history, force push, destructive branch operations

Performance logs should not be committed:

- `data/performance_logs/app_performance.jsonl`

## Recommended Development Route

1. Finish commit hygiene and GitHub workflow validation.
2. Run First Real Issue -> Branch -> PR smoke test.
3. Use GitHub Actions as the required quality gate.
4. Continue report-only validation before changing ranking behavior.
5. Only after explicit approval, implement guardrail-visible UI changes.
6. Do not replace production ranking until benchmark evidence and approval are both present.

## GitHub Issue / PR Working Method

Default workflow:

```text
Jin creates GitHub Issue
↓
Agent reads context docs
↓
Agent creates feature branch
↓
Agent implements scoped task
↓
Agent opens PR
↓
GitHub Actions runs QA
↓
Jin reviews and approves
```

Every implementation Issue should state:

- allowed files
- forbidden files
- acceptance criteria
- QA requirements
- approval tokens needed, if any

High-risk PR body tokens:

- `approved:ranking`
- `approved:data-write`

## Required Reading Before Agent Work

Every agent must read:

- `WORLDCUP.md`
- `SUPERVISOR.md`
- `AGENTS.md`
- `docs/GPT_CONTEXT.md`
- `docs/PRODUCT_PRINCIPLES.md`
- `docs/TASK_QUEUE.md`
- `docs/KNOWN_BUGS.md`
- `docs/QA_REPORT.md`
- `docs/CHANGELOG.md`
- `docs/TODAY_NEXT_ACTION.md`

Specialized agents should also read:

- `docs/SUBAGENTS.md`
- `docs/HOOKS_GUARDRAILS_PLAN.md`
- `docs/AGENT_WORKFLOW_RUNBOOK.md`
