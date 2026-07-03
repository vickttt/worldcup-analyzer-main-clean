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

# Real Claude Integration Plan v1

Date: 2026-06-23

## Goal

Replace the current mock Claude Review workflow with a real Anthropic Claude API reviewer in a staged, safe way.

This plan is design-only. It does not implement the real Claude API call, does not modify GitHub Actions, and does not enable auto-merge.

## 1. Current Status Summary

Current automation status:

- GitHub Rulesets are active.
- `dev` and `main` are protected.
- `Agent QA` is a required check.
- PR approval is required.
- Mock `Claude Review` workflow has run successfully as a pass/fail check.
- PR #5 validated that `Agent QA` and `Claude Review` can both pass.
- Current `Claude Review` does not call the real Claude API.

What mock Claude Review has completed:

- PR-triggered workflow exists.
- PR metadata can be collected.
- changed files can be collected.
- PR diff can be collected.
- a strict JSON-shaped review result can be generated.
- risky file patterns can fail the check.
- low-risk docs / reports / workflow changes can pass.
- GitHub can surface the result as a check.

What is still missing:

- real Anthropic API call
- `ANTHROPIC_API_KEY` GitHub secret
- prompt construction with project context
- strict JSON parsing and schema validation from model output
- API failure handling
- token / diff size controls
- Claude review comments or artifact summary
- ruleset update to require real `Claude Review` after validation

Why the project cannot directly enable auto-merge:

- Claude Review is still mock-only.
- There is no real model judgement yet.
- The fix loop is not implemented.
- auto-merge labels and risk gates are not implemented.
- API failure / JSON parse failure behavior has not been validated.
- medium/high risk PRs still require Jin judgement.

## 2. Real Claude Review Architecture

### GitHub Action Trigger

The future real workflow should trigger on:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, edited, ready_for_review]
```

### Collect PR Metadata

The workflow should collect:

- PR number
- title
- body
- author
- labels
- base branch
- head branch
- commit SHA
- changed file list
- Agent QA status

Recommended command:

```bash
gh pr view "$PR_NUMBER" \
  --json title,body,author,labels,files,headRefName,baseRefName,statusCheckRollup
```

### Collect PR Diff

The workflow should collect a unified diff:

```bash
gh pr diff "$PR_NUMBER" > /tmp/pr.diff
```

Recommended additional outputs:

```text
/tmp/changed_files.txt
/tmp/pr_metadata.json
/tmp/pr.diff
```

### Read Linked Issue

The workflow should extract linked Issue numbers from PR body patterns:

- `Closes #123`
- `Fixes #123`
- `Resolves #123`

Then read Issue body:

```bash
gh issue view "$ISSUE_NUMBER" --json title,body,labels
```

If no linked Issue exists:

- Claude Review should fail or pause.
- `auto_merge_eligible` must be `false`.

### Read Project Context

Claude should receive bounded context from:

- `WORLDCUP.md`
- `SUPERVISOR.md`
- `AGENTS.md`
- `docs/QA_REPORT.md`
- `docs/CHANGELOG.md`
- `docs/TASK_QUEUE.md`
- `docs/TODAY_NEXT_ACTION.md` when present

Context reading rules:

- include only the top relevant sections when files are large
- prefer recent sections of `CHANGELOG.md` and `QA_REPORT.md`
- cap each context file by character limit
- never include secrets or `.env`

### Assemble Claude Prompt

The prompt should include:

1. system role: independent PR reviewer
2. hard safety rules
3. linked Issue scope
4. changed files
5. PR diff
6. project context
7. strict JSON schema
8. explicit instruction: return JSON only, no markdown

### Call Anthropic API

Recommended API:

```text
POST https://api.anthropic.com/v1/messages
```

Required headers:

```text
x-api-key: $ANTHROPIC_API_KEY
anthropic-version: 2023-06-01
content-type: application/json
```

Recommended initial model:

```text
claude-sonnet-4-20250514
```

Model choice should be pinned in the workflow for reproducibility and changed only through a separate PR.

### Parse Strict JSON

After response:

1. extract assistant text
2. parse as JSON
3. validate all required keys exist
4. validate `status` is `pass` or `fail`
5. validate `risk_level` is `low`, `medium`, `high`, or `critical`
6. fail the GitHub Action if parsing fails
7. upload parsed JSON artifact
8. optionally post summary comment

If JSON parsing fails:

- check must fail
- PR must not merge
- summary should say: `Claude Review returned invalid JSON`

## 3. GitHub Secrets Configuration

Required secret:

```text
ANTHROPIC_API_KEY
```

Where Jin sets it:

```text
Repository Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

Secret name must be exactly:

```text
ANTHROPIC_API_KEY
```

Rules:

- do not print the secret
- do not echo the secret
- do not write the secret into repo files
- do not store it in artifacts
- do not include it in PR comments
- do not expose request headers in logs

The workflow should reference it only through:

```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

If the secret is missing:

- Claude Review check should fail
- summary should say: `ANTHROPIC_API_KEY is not configured`
- auto-merge must be blocked

## 4. Claude Review Prompt Design

Claude must return strict JSON only:

```json
{
  "status": "pass | fail",
  "risk_level": "low | medium | high | critical",
  "summary": "...",
  "forbidden_files_changed": [],
  "protected_functions_changed": [],
  "data_writes_detected": [],
  "secrets_detected": false,
  "qa_missing": [],
  "docs_missing": [],
  "scope_violations": [],
  "required_fixes": [],
  "auto_merge_eligible": true
}
```

Prompt requirements:

- Review the PR as an independent safety gate.
- Do not suggest broad rewrites.
- Do not approve scope drift.
- Treat missing linked Issue as fail.
- Treat secret-like content as fail.
- Treat protected function changes as fail unless explicitly approved.
- Even when explicitly approved, mark high-risk PRs as not auto-merge eligible.
- Return JSON only.

Recommended prompt structure:

```text
You are Claude Reviewer for WorldCup Analyzer.

Your job:
- inspect Issue scope, changed files, PR diff, and project guardrails
- decide pass/fail
- return strict JSON only

Hard fail rules:
...

Pass rules:
...

Project context:
...

Linked Issue:
...

PR metadata:
...

Changed files:
...

PR diff:
...

Return exactly this JSON schema:
...
```

## 5. Fail / Pause Rules

Claude must fail or pause when PRs touch or imply:

- large `app.py` changes
- ranking logic
- recommendation logic
- `strategy_score(...)`
- `strategy_comparison(...)`
- `evaluate_allocation(...)`
- `data/history`
- `data/history/backfill` full writes
- `data/performance_logs/app_performance.jsonl`
- secrets
- tokens
- `.env`
- API full backfill
- deleted files
- force push instructions
- Git history rewrite instructions
- scope drift from linked Issue

Recommended status:

- `fail` for unsafe or unapproved changes
- `risk_level = high` or `critical`
- `auto_merge_eligible = false`

If PR includes approved tokens:

- `approved:ranking`
- `approved:data-write`

Claude may pass only if the Issue clearly authorizes the change and QA is adequate.

Even then:

- `auto_merge_eligible = false`
- Jin must manually review.

## 6. Pass Rules

Claude may pass when:

- PR is docs-only
- PR is reports-only
- PR updates workflow templates safely
- PR updates workflow runbooks safely
- PR contains low-risk display copy only
- no forbidden files changed
- no protected functions changed
- no data writes
- no secrets detected
- PR links an Issue
- PR body has safety checklist
- Agent QA has passed or is expected to pass

For low-risk display copy:

- PR must be labeled or described as low risk
- no ranking/recommendation behavior may change
- no default recommendation may change

## 7. Codex ↔ Claude Fix Loop

Loop definition:

```text
Claude Review fail
↓
Codex reads required_fixes
↓
Codex applies minimal scoped fix
↓
Codex pushes update
↓
Agent QA reruns
↓
Claude Review reruns
```

Maximum rounds: **3**

Round counter should be tracked by:

- PR comments
- workflow artifact
- PR label such as `fix-loop:1`, `fix-loop:2`, `fix-loop:3`

Stop conditions:

- more than 3 rounds
- secrets detected
- protected data touched
- ranking/recommendation changes require Jin
- Claude returns `risk_level = critical`
- Codex cannot fix without broad rewrite

When stopped:

- add label: `paused`
- leave PR open
- notify Jin
- summarize failed checks and required decisions

## 8. Cost / Token / Rate Limit

Each PR review input may include:

- PR metadata: small
- linked Issue body: usually 1k-5k tokens
- project context docs: 5k-20k tokens if not capped
- PR diff: highly variable
- QA status: small

Recommended limits:

- changed file list: include all
- Issue body: cap at 12,000 characters
- `WORLDCUP.md`: cap at 8,000 characters
- `SUPERVISOR.md`: cap at 8,000 characters
- `AGENTS.md`: cap at 6,000 characters
- latest `QA_REPORT.md`: cap at 12,000 characters
- latest `CHANGELOG.md`: cap at 12,000 characters
- PR diff: cap at 60,000 characters for normal review

If PR diff exceeds limit:

- do not silently truncate and pass
- return fail/pause
- set `risk_level = medium` or `high`
- set `auto_merge_eligible = false`
- require human review or split PR

Recommended large PR rule:

```text
If diff > 60,000 characters or changed files > 25:
  fail with "large PR requires manual review"
```

Cost control:

- skip real Claude API for draft PRs unless explicitly enabled
- skip API for dependency/cache/log-only changes and fail locally
- pre-filter forbidden files before calling Claude
- use mock/local guardrails first, Claude second
- cache no sensitive content

Rate limit behavior:

- API timeout: fail check
- 429/rate limit: fail check
- 5xx API error: fail check
- no auto-merge on API failure

## 9. Implementation Phases

### Phase A: Real Claude Report-Only

Goal:

- call real Claude API
- upload JSON artifact
- post PR comment
- do not make it required
- do not block merge
- do not auto-merge

Output:

- `claude-review-result.json`
- PR comment summary

### Phase B: Real Claude Pass/Fail Check

Goal:

- make workflow fail when Claude returns `fail`
- add `Claude Review` to rulesets as required check
- still no auto-merge

### Phase C: Low-Risk PR Auto-Merge

Goal:

- auto-merge only when:
  - `Agent QA` passed
  - `Claude Review` passed
  - `risk:low`
  - no forbidden files
  - no protected functions
  - no data writes

### Phase D: Codex-Claude Fix Loop

Goal:

- Codex reads `required_fixes`
- applies minimal fix
- reruns QA and Claude review
- max 3 rounds
- pause after 3 failures

### Phase E: Daily Autonomous Summary

Goal:

- Supervisor generates daily summary:
  - merged PRs
  - paused PRs
  - failed QA
  - dangerous changes
  - next Issue draft

## 10. Risk Control

Non-negotiable rules:

- Claude does not write code.
- Claude does not commit.
- Claude does not push.
- Claude does not merge.
- Claude does not change rulesets.
- Claude does not modify files.
- Do not auto-merge medium/high risk PRs.
- Do not auto-merge PRs with protected functions.
- Do not auto-merge PRs with data writes.
- Do not auto-merge on Claude API failure.
- Do not auto-merge on JSON parse failure.
- Do not auto-merge when `ANTHROPIC_API_KEY` is missing.

Failure behavior:

- Claude API failure -> check fail
- JSON parse failure -> check fail
- schema validation failure -> check fail
- missing linked Issue -> check fail
- forbidden files -> check fail
- secrets detected -> check fail

## 11. What Jin Must Do Manually

Jin must decide:

- whether to buy / enable Anthropic API access
- whether to create `ANTHROPIC_API_KEY`
- whether to add it to GitHub repository secrets
- whether to approve Phase A implementation
- whether to allow Claude Review PR comments
- when to add real `Claude Review` as a required check
- when to allow any auto-merge path

Manual GitHub setup:

```text
Repository Settings
→ Secrets and variables
→ Actions
→ New repository secret
→ ANTHROPIC_API_KEY
```

Jin should not paste secrets into:

- chat
- repo files
- PR comments
- workflow logs

## 12. Next Recommended Issue

Issue title:

```text
[Automation] Implement real Claude review report-only mode
```

Recommended scope:

- add a report-only real Claude Review workflow path
- read `ANTHROPIC_API_KEY` from GitHub Actions secret
- call Anthropic API
- produce strict JSON artifact
- post summary comment if safe
- do not make it required yet
- do not auto-merge
- keep mock guardrails as pre-filter

Allowed files:

- `.github/workflows/claude-review.yml`
- `CLAUDE_REVIEW_REPORT.md`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`

Forbidden files:

- `app.py`
- `scripts/`
- `modules/`
- `data/history/`
- `data/performance_logs/app_performance.jsonl`
- `.env`
- secrets

Risk level:

```text
Medium
```

Reason:

- touches GitHub workflow
- introduces external API dependency
- does not modify product logic
- does not enable required check or auto-merge yet

## Final Verdict

Real Claude integration should begin with Phase A report-only mode.

Do not replace the mock reviewer as a required gate until real Claude output has been validated on low-risk PRs and Jin approves adding `Claude Review` to the required checks.
