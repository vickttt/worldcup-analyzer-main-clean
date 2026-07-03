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
- old PR, workflow cleanup, and Claude Review integration migration plans must not be followed unless explicitly re-approved by the user

Do not use this document as execution guidance unless AGENTS.md is explicitly updated to restore it.

# Automation Migration Plan

## Purpose

Prepare the next automation consolidation task without changing business logic, recommendation logic, UI, model code, odds code, backtest code, data files, or pipelines.

## Current Findings

- Active GitHub Actions files exist under `.github/workflows/`:
  - `.github/workflows/ci.yml`
  - `.github/workflows/agent-qa.yml`
  - `.github/workflows/claude-review.yml`
- Duplicate workflow copies also exist:
  - `.github/workflows/agent-qa 2.yml`
  - `.github/workflows/claude-review 2.yml`
- Duplicate template copies exist:
  - `.github/pull_request_template 2.md`
  - `.github/pull_request_template 3.md`
  - `.github/ISSUE_TEMPLATE/agent_task 2.md`
- Existing automation documentation exists under `docs/`:
  - `docs/AGENT_WORKFLOW_RUNBOOK.md`
  - `docs/HOOKS_GUARDRAILS_PLAN.md`
  - `docs/SUBAGENTS.md`

## Proposed Target Structure

- Keep active GitHub workflow entrypoints in `.github/workflows/`.
- Move detailed automation design notes into a dedicated documentation area:
  - `docs/automation/README.md`
  - `docs/automation/AGENT_QA_SPEC.md`
  - `docs/automation/CLAUDE_REVIEW_SPEC.md`
  - `docs/automation/GITHUB_ACTIONS_SPEC.md`
  - `docs/automation/MIGRATION_LOG.md`
- Keep PR and Issue templates in `.github/`.
- Treat duplicate files as migration candidates, not deletion candidates, until explicitly approved.

## Proposed Phases

### Phase 1: Inventory Only

- List every `.github/` workflow and template file.
- Identify canonical files and duplicate copies.
- Compare duplicate contents before any move or removal.
- Do not delete files.
- Do not change workflow triggers.

### Phase 2: Documentation Consolidation

- Create `docs/automation/`.
- Add specifications for CI, Agent QA, and Claude Review behavior.
- Record which files are active and which files are historical duplicates.
- Update `docs/CHANGELOG.md` and `docs/QA_REPORT.md`.

### Phase 3: Workflow Cleanup Proposal

- Prepare a separate PR that proposes which duplicate files can be removed.
- Require explicit user approval before deleting any duplicate workflow or template file.
- Keep `ci.yml` as the required main-merge gate.
- Keep Agent QA and Claude Review as auxiliary unless governance rules are changed.

### Phase 4: Optional Enforcement Upgrade

- Only after approval, consider making Agent QA run on `pull_request`.
- Only after approval, consider replacing mock Claude Review with real Claude API integration.
- Never store API keys, `.env` values, tokens, or secrets in code or Markdown.

## Allowed Files For Next Task

- `.github/workflows/*.yml`
- `.github/ISSUE_TEMPLATE/*.md`
- `.github/pull_request_template.md`
- `docs/automation/*.md`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`

## Forbidden Files For Next Task

- `app.py`
- `modules/`
- `data/`
- `data/history/`
- `reports/`
- `scripts/` unless explicitly approved for workflow tooling
- Production recommendation logic
- Portfolio Score logic
- API refresh or pipeline behavior

## Required QA For Next Task

- `git status --short --branch`
- `git diff --check`
- Review changed file list before commit.
- Confirm no `app.py`, `modules/`, `data/`, or `reports/` files changed.
- Confirm no secrets were added.
- If workflows change, create a PR and wait for GitHub CI.

## Recommendation

Start with Phase 1 and Phase 2 only. Defer deletion of duplicate workflow/template files until a separate approval is given.
