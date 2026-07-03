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
- old SessionStart, PR guardrail, Supervisor-generated review, or hook automation plans must not be followed unless explicitly re-approved by the user

Do not use this document as execution guidance unless AGENTS.md is explicitly updated to restore it.

# Hooks And Guardrails Plan

Date: 2026-06-22

Purpose: define future automation hooks that prevent unsafe agent behavior before it reaches GitHub review.

This is a design plan only. No hooks are installed by this document.

## 1. PreToolUse Guardrails

Goal: block dangerous local actions before they run.

Block or require approval for:

- `rm -rf`
- `git reset --hard`
- `git clean`
- `git push --force`
- deleting `data/`
- deleting `docs/`
- writing secrets
- editing `.env`
- modifying private keys
- running full API backfills without approval

Expected behavior:

- low-risk read commands proceed
- destructive commands stop
- high-risk commands require Jin approval

## 2. PreCommit Guardrails

Goal: prevent unsafe commits.

Checks:

- detect modifications to `strategy_score(...)`
- detect modifications to `strategy_comparison(...)`
- detect modifications to `evaluate_allocation(...)`
- detect modifications to protected history data
- reject performance logs
- reject cache files
- reject secrets

Protected data:

- `data/history/*_pre.json`
- `data/history/*_post.json`
- `data/history/my_portfolios/*.json`

Always exclude:

- `data/performance_logs/app_performance.jsonl`
- `__pycache__/`
- `.venv/`
- `.env`
- keys and tokens

## 3. PostToolUse Guardrails

Goal: automatically run cheap validation after edits.

Recommended checks:

- `python -m py_compile app.py`
- `python -m py_compile scripts/*.py`
- YAML parse for `.github/workflows/*.yml`
- changed-file scope check
- docs sync check

Docs sync rule:

- if `app.py` or `scripts/*.py` changed, require:
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`

## 4. SessionStart Context Loading

Goal: every agent starts with correct project context.

Required reads:

- `WORLDCUP.md`
- `SUPERVISOR.md`
- `AGENTS.md`
- `docs/GPT_CONTEXT.md`
- `docs/TASK_QUEUE.md`
- `docs/QA_REPORT.md`
- `docs/CHANGELOG.md`
- `docs/TODAY_NEXT_ACTION.md`

Recommended output after SessionStart:

- current phase
- current risk level
- current next action
- dirty worktree warning

## 5. PR Guardrail

Goal: make GitHub the final safety gate.

Rules:

- protected ranking changes require `approved:ranking`
- protected data writes require `approved:data-write`
- code changes require Changelog and QA updates
- PR must link to Issue
- PR must use template safety checklist

Dangerous changes fail GitHub Actions unless explicitly approved.

## 6. Future Hook Implementation Order

Phase A:

- local changed-file scope checker
- YAML workflow checker
- docs sync checker

Phase B:

- function body diff checker for ranking-sensitive functions
- protected data checker
- performance log exclusion checker

Phase C:

- automatic SessionStart context loader
- agent task classifier
- auto-generated next Issue draft

Phase D:

- integrated pre-commit hook
- integrated pre-PR checklist
- Supervisor-generated PR risk review

## 7. Non-Negotiable Safety Rules

- no force push
- no Git history rewrite
- no deletion without explicit approval
- no protected data writes without explicit approval
- no ranking behavior change without explicit approval
- no secret handling through agent-generated files
