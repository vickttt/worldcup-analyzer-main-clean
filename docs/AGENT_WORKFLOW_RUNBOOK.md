# DEPRECATED — HISTORICAL REFERENCE ONLY

This document is no longer an active workflow authority.
The current active repository rules are defined only in AGENTS.md.

Current active workflow:
- dev-clean is the only development branch
- no automatic branch creation or branch switching
- Codex is the only execution engine
- Claude is read-only review only
- the user is the final decision authority
- old Issue -> Branch -> PR or multi-branch agent workflows must not be followed unless explicitly re-approved by the user

Do not use this document as execution guidance unless AGENTS.md is explicitly updated to restore it.

# Agent Workflow Runbook

Date: 2026-06-21

Purpose: use GitHub Issues and Pull Requests as the operating system for Codex / Claude agent work, so Jin reviews PRs instead of copying tasks between tools.

## 1. Jin Creates An Issue

1. Open a new GitHub Issue.
2. Choose the `Agent Task` template.
3. Fill in Goal, Background, Scope, Allowed Changes, Forbidden Changes, Required Inputs, Required Outputs, Acceptance Criteria, QA Requirements, Risk Level, Approval Required Before, and Suggested Commit Message.
4. Add labels:
   - `type:design`, `type:implementation`, or `type:qa`
   - `risk:low`, `risk:medium`, or `risk:high`
   - `needs-approval` when the agent must stop before a sensitive action
5. Attach screenshots, report links, and exact file paths when possible.

## 2. Agent Creates A Branch

1. Agent reads the Issue and required project docs before editing:
   - `AGENTS.md`
   - `docs/GPT_CONTEXT.md`
   - `docs/TASK_QUEUE.md`
   - `docs/KNOWN_BUGS.md`
   - `docs/CHANGELOG.md`
   - `docs/QA_REPORT.md`
2. Agent creates a feature branch from the current development branch.
3. Branch naming convention:
   - `codex/<issue-number>-short-task-name`
4. Agent must not start high-risk work if the Issue lacks explicit approval.

## 3. Agent Executes The Task

1. Stay inside the Issue scope.
2. Do not modify forbidden files or functions.
3. Update `docs/CHANGELOG.md` and `docs/QA_REPORT.md` for code, workflow, automation, or report changes.
4. Run required QA locally when possible.
5. Do not push secrets, generated cache files, performance logs, or unapproved data writes.

## 4. Agent Opens A Pull Request

1. Use the PR template.
2. Link the Issue with `Closes #<issue-number>`.
3. Summarize changed files and QA results.
4. State clearly whether sorting, recommendation logic, default recommendation, UI, data files, or protected functions changed.
5. Include `approved:ranking` only when Jin explicitly approved ranking-sensitive function changes.
6. Include `approved:data-write` only when Jin explicitly approved protected history data changes.

## 5. GitHub Actions QA

The `Agent QA` workflow checks:

- Python syntax for `app.py` and `scripts/*.py`.
- Whether `strategy_score(...)`, `strategy_comparison(...)`, or `evaluate_allocation(...)` changed without `approved:ranking`.
- Whether protected history data changed without `approved:data-write`.
- Whether code changes also updated `docs/CHANGELOG.md` and `docs/QA_REPORT.md`.

The PR should not be merged until required checks pass or Jin explicitly decides to override them.

## 6. Jin Reviews And Approves

Jin should review:

- Whether the PR matches the Issue.
- Whether the PR avoided forbidden changes.
- Whether QA output is credible.
- Whether screenshots or generated reports match the intended product behavior.
- Whether any manual approval token in the PR body was intentionally granted.

## 7. Manual Approval Required

Agent must stop and ask Jin before:

- Modifying `strategy_score(...)`, `strategy_comparison(...)`, or `evaluate_allocation(...)`.
- Changing production sorting or default recommendation logic.
- Writing to `data/history/*_pre.json`, `data/history/*_post.json`, or `data/history/my_portfolios/*.json`.
- Running full API backfills or data refreshes.
- Deleting files.
- Force pushing or rewriting Git history.
- Making large `app.py` UI changes unless the Issue explicitly approves them.

## 8. Files Agents Should Avoid Unless Approved

- `data/history/*_pre.json`
- `data/history/*_post.json`
- `data/history/my_portfolios/*.json`
- `data/performance_logs/*`
- `strategy_score(...)`
- `strategy_comparison(...)`
- `evaluate_allocation(...)`
- Major `app.py` UI refactors

## 9. Default Operating Rule

Issue defines the task. Pull Request proves the task. GitHub Actions checks the guardrails. Jin approves the merge.
