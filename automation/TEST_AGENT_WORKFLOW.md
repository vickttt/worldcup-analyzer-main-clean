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

# Test Agent Workflow

Date: 2026-06-21

Purpose: run the first low-risk agent-driven GitHub workflow rehearsal.

This test does not develop any World Cup analyzer feature. It only verifies the operating path:

```text
GitHub Issue
↓
Feature Branch
↓
Implementation
↓
Pull Request
↓
GitHub Actions QA
↓
Jin Review
```


## Rehearsal Execution

Issue: https://github.com/vickttt/worldcup-analyzer/issues/1

Branch:

```text
codex/1-agent-workflow-smoke-test
```

Expected PR status: open for Jin review, not merged by the agent.

## 1. Test Issue Content

Recommended GitHub Issue title:

```text
[Workflow] Add first agent workflow smoke-test document
```

Recommended labels:

- `agent-task`
- `type:qa`
- `risk:low`
- `no-business-code`

Issue body:

```markdown
## Goal

Verify the first Issue-driven agent workflow from GitHub Issue to PR review.

## Background

The project has added GitHub Issue templates, a PR template, and the Agent QA workflow. This task is a low-risk smoke test to confirm the workflow can be used without touching business code.

## Scope

Create or update only `TEST_AGENT_WORKFLOW.md`.

## Allowed Changes

- `TEST_AGENT_WORKFLOW.md`

## Forbidden Changes

- Do not modify `app.py`.
- Do not modify recommendation logic.
- Do not modify ranking logic.
- Do not modify `strategy_score(...)`.
- Do not modify `strategy_comparison(...)`.
- Do not modify `evaluate_allocation(...)`.
- Do not modify `data/`.
- Do not run API refreshes.

## Required Inputs

- `.github/ISSUE_TEMPLATE/agent_task.md`
- `.github/pull_request_template.md`
- `.github/workflows/agent-qa.yml`
- `docs/AGENT_WORKFLOW_RUNBOOK.md`

## Required Outputs

- `TEST_AGENT_WORKFLOW.md`

## Acceptance Criteria

- The PR contains only the smoke-test documentation change.
- GitHub Actions runs successfully.
- No business code is modified.
- Jin can review and approve the PR from GitHub.

## QA Requirements

- Confirm changed files do not include `app.py`, `scripts/*.py`, or `data/`.
- Confirm GitHub Actions passes.

## Risk Level

Low

## Approval Required Before

No special approval required unless the agent needs to modify files outside `TEST_AGENT_WORKFLOW.md`.

## Suggested Commit Message

`Add agent workflow smoke test document`
```

## 2. Test Branch Name

Recommended branch:

```text
codex/issue-001-agent-workflow-smoke-test
```

If the GitHub Issue number is known, use it:

```text
codex/<issue-number>-agent-workflow-smoke-test
```

Example:

```text
codex/42-agent-workflow-smoke-test
```

## 3. Test PR Template

Recommended PR title:

```text
[Workflow] Add agent workflow smoke-test document
```

Recommended PR body:

```markdown
## Summary

- Added `TEST_AGENT_WORKFLOW.md` as the first low-risk agent workflow smoke test.
- Documented the test Issue, branch name, PR expectations, QA expectations, and Jin approval flow.

## Linked Issue

Closes #<issue-number>

## Changes

- Added `TEST_AGENT_WORKFLOW.md`.

## QA

- [x] Python syntax check is not required because no Python files changed.
- [x] `docs/CHANGELOG.md` update is not required because this is a workflow smoke-test document only.
- [x] `docs/QA_REPORT.md` update is not required because this is a workflow smoke-test document only.
- [x] No API refresh was run.
- [x] No data files were modified.

## Safety Check

- [x] Did not change production sorting.
- [x] Did not change recommendation logic.
- [x] Did not change default recommendation.
- [x] Did not modify `strategy_score(...)`.
- [x] Did not modify `strategy_comparison(...)`.
- [x] Did not modify `evaluate_allocation(...)`.
- [x] Did not modify protected history data.

## Manual Review Required

Jin should confirm:

- The PR is linked to the correct Issue.
- The changed files list only contains `TEST_AGENT_WORKFLOW.md`.
- GitHub Actions passed.
- The workflow is understandable enough to use as the first agent-driven task rehearsal.
```

## 4. GitHub Actions Expected Result

Expected status: **Pass**

Reason:

- No `app.py` changes.
- No `scripts/*.py` changes.
- No protected ranking function changes.
- No protected `data/history` changes.
- Docs synchronization check should not trigger because no app or script code changed.

Expected checks:

| Check | Expected Result |
| --- | --- |
| Python syntax check | Pass |
| Forbidden ranking function diff check | Pass |
| Data safety check | Pass |
| Docs check for code changes | Pass |

If GitHub Actions fails, the first debugging target should be `.github/workflows/agent-qa.yml`, not the World Cup analyzer business code.

## 5. Jin Approval Flow

1. Jin creates the Issue using the `Agent Task` template.
2. Agent creates the branch:

   ```text
   codex/<issue-number>-agent-workflow-smoke-test
   ```

3. Agent adds or updates `TEST_AGENT_WORKFLOW.md`.
4. Agent opens a PR linked to the Issue.
5. GitHub Actions runs automatically.
6. Jin reviews:
   - PR changed files.
   - PR safety checklist.
   - GitHub Actions result.
   - Whether the PR closes the Issue.
7. If all checks pass, Jin approves and merges.
8. If checks fail, Jin requests changes and the agent fixes only workflow/test documentation issues.

## Final Test Verdict

This is the safest first Agent Workflow rehearsal because it exercises the full GitHub operating path without touching business code, ranking, recommendation logic, UI, API refreshes, or data files.
