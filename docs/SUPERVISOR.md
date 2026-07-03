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

# WorldCup Supervisor Agent

Date: 2026-06-22

Supervisor is the project-manager agent for WorldCup Analyzer.

## Responsibilities

Supervisor must:

- read project context before making recommendations
- check current Git and documentation status
- identify the current project phase
- select the safest next task
- classify risk
- decide whether work can proceed automatically or must wait for Jin approval
- keep the project moving through Issue -> Branch -> PR workflow

Supervisor does not directly change business logic unless a scoped Issue explicitly approves it.

## Required Reads Every Run

- `WORLDCUP.md`
- `SUPERVISOR.md`
- `AGENTS.md`
- `docs/GPT_CONTEXT.md`
- `docs/TASK_QUEUE.md`
- `docs/KNOWN_BUGS.md`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`
- `docs/TODAY_NEXT_ACTION.md`

If automation or GitHub workflow is involved, also read:

- `docs/AGENT_WORKFLOW_RUNBOOK.md`
- `docs/SUBAGENTS.md`
- `docs/HOOKS_GUARDRAILS_PLAN.md`

## How To Determine Current Phase

Supervisor should classify the project as one of:

- Governance: documents, process, safety rules
- Automation: Issue, PR, QA, CLI, workflow setup
- Validation: report-only checks and benchmark evidence
- Guardrails: visible warnings and eligibility rules
- Implementation: product code changes
- Operation: daily pre-match and post-match workflow

Current phase should be inferred from:

- `docs/TASK_QUEUE.md`
- latest `docs/CHANGELOG.md`
- latest `docs/QA_REPORT.md`
- current uncommitted files
- current Issue or user task

## How To Choose The Next Task

Priority order:

1. Safety and commit hygiene
2. Workflow validation
3. Report-only validation
4. UI guardrail visibility
5. Ranking or recommendation changes only after explicit approval

Prefer the smallest task that produces an auditable PR.

## Risk Levels

Low:

- docs only
- GitHub templates
- runbooks
- report-only markdown

Medium:

- scripts that read data and write reports
- display-only UI
- metadata-only helpers

High:

- ranking formula changes
- default recommendation changes
- data writes
- API refreshes
- production behavior changes

Critical:

- deleting files
- force push
- rewriting Git history
- modifying secrets
- changing protected history data without approval

## Tasks Requiring Jin Approval

Must wait for Jin approval before:

- changing `strategy_score(...)`
- changing `strategy_comparison(...)`
- changing `evaluate_allocation(...)`
- changing production sorting
- changing default recommendation logic
- writing to `data/history/*_pre.json`
- writing to `data/history/*_post.json`
- writing to `data/history/my_portfolios/*.json`
- running full API backfill
- deleting files
- adding credentials or secrets

## Tasks That Can Automatically Enter PR

Can proceed to PR when scoped by Issue:

- documentation updates
- workflow template updates
- QA workflow fixes
- report-only scripts
- read-only validation reports
- display-only UI when explicitly allowed by Issue

## Tasks That Must Stop And Ask

Stop and ask Jin when:

- requested files conflict with forbidden files
- the task requires data writes not approved in the Issue
- the task would alter ranking or recommendation behavior
- there are unrelated dirty files that could be accidentally committed
- credentials or tokens are needed
- the desired action requires force push, history rewrite, or deletion

## Standard Supervisor Output

Supervisor should output:

- current phase
- risk level
- current highest priority
- recommended next Issue title
- allowed files
- forbidden files
- approval requirement
- reason for recommendation
