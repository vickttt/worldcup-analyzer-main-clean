# Claude Review GitHub Action v1 Report

Date: 2026-06-22

## Summary

Implemented a mock Claude Review workflow design for GitHub PRs.

This version does **not** call the real Claude API. It is a guardrail rehearsal workflow intended to validate the pass/fail GitHub check shape before adding `ANTHROPIC_API_KEY` and real Claude review.

## Added Workflow

```text
.github/workflows/claude-review.yml
```

Workflow check name:

```text
Claude Review
```

Trigger:

```text
pull_request
```

Triggered on:

- opened
- synchronize
- reopened
- edited
- ready_for_review

## What The Mock Reviewer Reads

- PR title
- PR body
- PR number
- base branch
- head branch
- changed files
- full PR diff

The workflow prepares:

- `/tmp/changed_files.txt`
- `/tmp/pr.diff`
- `/tmp/pr_metadata.txt`

## Output

The workflow writes:

```text
claude-review-result.json
```

It also uploads the JSON as a GitHub Actions artifact named:

```text
claude-review-result
```

## Pass Conditions

The mock reviewer passes PRs that are low-risk:

- docs
- reports
- workflow templates
- workflow runbooks
- GitHub template changes
- low-risk display copy when explicitly marked `risk:low`

## Fail Conditions

The mock reviewer fails PRs when it detects:

- ranking logic changes
- recommendation logic risk
- protected function changes:
  - `strategy_score(...)`
  - `strategy_comparison(...)`
  - `evaluate_allocation(...)`
- `data/history` writes without `approved:data-write`
- performance logs
- secrets
- tokens
- `.env`
- private keys
- changes that cannot be classified as docs / reports / workflow / low-risk display copy

## JSON Shape

Example pass:

```json
{
  "status": "pass",
  "risk_level": "low",
  "summary": "Mock Claude Review passed: changes are low-risk.",
  "changed_files": [],
  "forbidden_files_changed": [],
  "protected_functions_changed": [],
  "data_writes_detected": [],
  "secrets_detected": false,
  "qa_missing": [],
  "docs_missing": [],
  "scope_violations": [],
  "required_fixes": [],
  "auto_merge_eligible": true,
  "reviewer_mode": "mock",
  "real_claude_api_called": false
}
```

## Required Secrets

No secret is required for v1 mock mode.

Future real Claude mode will require:

```text
ANTHROPIC_API_KEY
```

## Required GitHub Permissions

Current mock workflow:

```yaml
permissions:
  contents: read
  pull-requests: read
  issues: read
```

Future real review with comments/check annotations may require:

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: read
  checks: write
  statuses: write
```

## Level 3 Readiness

This workflow is a required-check rehearsal only.

Do not enable auto-merge until:

- `Claude Review` passes on a rehearsal PR
- `Claude Review` is added to the `dev` and `main` rulesets
- `Agent QA` remains required
- PR review remains required
- forbidden-file and protected-function behavior is validated
- real Claude API mode is designed and approved

## Safety Confirmation

This task does not modify:

- business code
- `app.py`
- `scripts/`
- `modules/`
- `data/history/`
- ranking logic
- recommendation logic
- production sorting

No PR was created. No commit was made. No push was performed.
