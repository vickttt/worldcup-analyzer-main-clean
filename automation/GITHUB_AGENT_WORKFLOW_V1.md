# GitHub Agent Workflow v1

Date: 2026-06-21

Scope: design only. This workflow does not modify code, GitHub configuration, GitHub Actions, project data, branches, commits, or pull requests.

## 1. Goal

Reduce manual copy-paste between GPT, Codex, Claude, and GitHub Desktop.

GitHub becomes the shared task source:

```text
Jin creates GitHub Issue
↓
Codex / Claude reads Issue
↓
Agent creates feature branch
↓
Agent implements task
↓
Agent runs QA
↓
Agent opens Pull Request
↓
Agent writes PR summary + review notes
↓
Jin approves / requests changes
↓
GitHub records final merge history
```

## 2. Roles

| Role | Responsibility |
| --- | --- |
| Jin | Product decision, approval, merge decision, rollback decision. |
| ChatGPT | Product architecture, task framing, issue drafting, acceptance criteria. |
| Codex | Implementation, tests, automation, local QA, PR preparation. |
| Claude Code | Optional second implementation/review agent. |
| GitHub Issues | Source of truth for tasks. |
| GitHub Pull Requests | Source of truth for code review and change history. |
| GitHub Actions | Automated QA gate. |
| GitHub Desktop | Manual commit/sync/rollback when Jin wants visual control. |

## 3. How Jin Creates A GitHub Issue

Each task should start as one GitHub Issue.

Recommended title format:

```text
[Area] Short action-oriented task
```

Examples:

```text
[UI] Add Match Betting Score card
[Ranking] Implement Hybrid v0.2 report-only benchmark
[Validation] Backfill 10 historical odds snapshots
[Governance] Update QA report and task queue
```

Labels:

| Label | Meaning |
| --- | --- |
| `type:design` | Plan only, no code. |
| `type:implementation` | Code change expected. |
| `type:qa` | Validation/report-only task. |
| `risk:low` | Docs/display-only/safe. |
| `risk:medium` | UI/report/ranking metadata. |
| `risk:high` | Recommendation logic, ranking, data writes. |
| `needs-approval` | Agent must stop before sensitive action. |
| `no-business-code` | Docs/report-only work. |

Milestones:

- `Governance`
- `Scenario Engine`
- `Hybrid Ranking`
- `Decision UI`
- `Post-Match Validation`
- `Historical Benchmark`

## 4. Issue Template

Recommended Issue template:

```md
## Goal

Describe the user-facing or project-governance objective.

## Background

Relevant context, prior reports, current conclusion.

## Scope

Allowed changes:
- ...

Forbidden changes:
- ...

## Required Inputs

Files/reports/scripts the agent must read:
- ...

## Required Outputs

Files/reports/code changes expected:
- ...

## Acceptance Criteria

- [ ] ...
- [ ] ...
- [ ] ...

## QA Requirements

- [ ] Syntax check
- [ ] Relevant script run
- [ ] Report regenerated
- [ ] No forbidden files modified
- [ ] CHANGELOG updated
- [ ] QA_REPORT updated

## Risk Level

LOW / MEDIUM / HIGH

## Approval Required Before

- [ ] Modifying `app.py`
- [ ] Modifying ranking logic
- [ ] Writing data files
- [ ] Creating PR
- [ ] Running API backfill

## Suggested Commit Message

...
```

## 5. Codex / Claude Reading The Issue

Agent startup checklist:

1. Read the GitHub Issue body.
2. Read linked prior reports.
3. Read governance docs:
   - `AGENTS.md`
   - `docs/GPT_CONTEXT.md`
   - `docs/TASK_QUEUE.md`
   - `docs/KNOWN_BUGS.md`
   - `docs/CHANGELOG.md`
   - `docs/QA_REPORT.md`
4. Check current branch and worktree status.
5. Confirm forbidden files and functions.
6. Execute only the task described in the Issue.

Agent must post a short Issue comment before work:

```md
I have read the issue and governance docs.

Planned scope:
- ...

Forbidden scope I will avoid:
- ...
```

## 6. Feature Branch Creation

Branch rule:

```text
codex/<issue-number>-short-slug
```

Examples:

```text
codex/42-match-betting-score
codex/51-hybrid-v2-report-only
codex/58-post-match-validation
```

Branch creation rule:

- Low-risk docs-only tasks: agent may create branch automatically.
- Medium-risk tasks: agent may create branch automatically if Issue says implementation is approved.
- High-risk tasks: Jin must explicitly approve branch creation and scope.

Never work directly on `main`.

Preferred base branch:

```text
dev
```

## 7. Implementation Workflow

Recommended Codex / Claude loop:

```text
Read Issue
↓
Create feature branch
↓
Inspect current code
↓
Implement minimal scoped change
↓
Run QA
↓
Update docs/CHANGELOG.md
↓
Update docs/QA_REPORT.md
↓
Generate report artifacts if required
↓
Check git diff
↓
Open PR
```

Agent must not expand the scope unless the Issue is updated.

If agent discovers a larger problem:

- stop
- comment on Issue
- propose follow-up Issue

## 8. Pull Request Generation

PR title:

```text
<Issue title>
```

PR body template:

```md
## Summary

- ...

## Linked Issue

Closes #<issue-number>

## Changes

- ...

## QA

- [ ] Syntax check passed
- [ ] Relevant scripts ran
- [ ] Reports regenerated
- [ ] No forbidden files modified
- [ ] CHANGELOG updated
- [ ] QA_REPORT updated

## Safety Check

- Sorting changed: Yes/No
- Recommendation logic changed: Yes/No
- UI changed: Yes/No
- Data files changed: Yes/No
- API refreshed: Yes/No

## Manual Review Required

- ...
```

## 9. Automatic QA Through GitHub Actions

Recommended GitHub Actions jobs:

## A. Static Safety Check

Checks:

- forbidden functions modified:
  - `strategy_score(...)`
  - `strategy_comparison(...)`
  - `evaluate_allocation(...)`
- forbidden directories modified:
  - `data/history/` original files
- `app.py` changed without Issue label:
  - `approved:app-ui`
  - `approved:app-logic`

## B. Python Syntax Check

Run:

```bash
python -m py_compile app.py
python -m py_compile scripts/*.py
```

## C. Report Script Check

For report-only tasks, run relevant scripts:

```bash
python scripts/generate_hybrid_v2_report_only.py
python scripts/generate_post_match_validation_report.py
```

Only run scripts explicitly approved by Issue labels.

## D. Documentation Check

Require updates when code changes:

- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`

## E. Data Safety Check

Fail PR if modified files include:

```text
data/history/*_pre.json
data/history/*_post.json
data/history/my_portfolios/*.json
```

unless Issue has:

```text
approved:data-write
```

## 10. Automatic PR Review

Agent-generated PR review should include:

```md
## Review Summary

Risk level:

## Files Changed

## Forbidden Area Check

- data/history changed:
- strategy_score changed:
- strategy_comparison changed:
- evaluate_allocation changed:
- app.py major UI changed:

## Behavioral Risk

## QA Evidence

## Recommendation

Approve / Request changes / Needs human approval
```

Claude or another model can act as review agent after Codex opens PR.

Review agent must not push changes directly unless assigned.

## 11. Tasks Requiring Human Approval

Jin must approve before agent does any of the following:

- modifies `strategy_score(...)`
- modifies `strategy_comparison(...)`
- modifies `evaluate_allocation(...)`
- changes production sorting
- changes default recommendation
- changes recommendation logic
- writes or overwrites `data/history/` original files
- runs full historical API backfill
- changes `app.py` major UI structure
- deletes files
- force pushes
- rewrites Git history
- merges PR
- deploys app

## 12. Files / Areas Agents Must Not Modify Without Explicit Approval

Forbidden by default:

```text
data/history/*_pre.json
data/history/*_post.json
data/history/my_portfolios/*.json
```

Forbidden functions by default:

```text
strategy_score(...)
strategy_comparison(...)
evaluate_allocation(...)
```

Sensitive by default:

```text
app.py major UI changes
recommendation logic
Portfolio Ranking production sorting
API refresh / full backfill scripts
```

Allowed with normal Issue approval:

```text
docs/*
report-only Markdown files
report-only scripts under scripts/
display-only UI changes explicitly approved in Issue
isolated data/history/backfill/ pilot data
```

## 13. Recommended Agent Commands

Agent should run:

```bash
git status --short
git branch --show-current
python -m py_compile app.py
```

If script changed:

```bash
python -m py_compile scripts/<script>.py
```

If report generated:

```bash
python scripts/<script>.py
```

Agent should not run:

```bash
git reset --hard
git push --force
git rebase -i
rm -rf
```

## 14. Recommended GitHub Labels

```text
type:design
type:implementation
type:qa
area:ui
area:ranking
area:scenario
area:validation
area:data
risk:low
risk:medium
risk:high
needs-approval
approved:app-ui
approved:ranking
approved:data-write
no-business-code
report-only
```

## 15. Example Issue

```md
# [UI] Add Match Betting Score MVP

## Goal

Add a match-level decision card that shows whether the match is worth betting.

## Scope

Allowed:
- Modify `app.py` display layer.
- Update `docs/CHANGELOG.md`.
- Update `docs/QA_REPORT.md`.

Forbidden:
- Do not change sorting.
- Do not change recommendation logic.
- Do not change `strategy_score(...)`.
- Do not change `strategy_comparison(...)`.
- Do not change `evaluate_allocation(...)`.
- Do not modify data files.

## Acceptance Criteria

- [ ] Match Betting Score appears above Portfolio Ranking.
- [ ] Recommended Stake appears above Portfolio Ranking.
- [ ] Portfolio Ranking still sorts by existing score.
- [ ] `app.py` syntax check passes.
- [ ] CHANGELOG and QA report updated.

## Risk Level

MEDIUM
```

## 16. Recommended Workflow For Jin

Daily development:

1. Create or select GitHub Issue.
2. Add acceptance criteria and forbidden scope.
3. Assign to Codex or Claude.
4. Agent creates feature branch.
5. Agent opens PR.
6. GitHub Actions run QA.
7. Review agent posts PR review.
8. Jin reviews diff in GitHub or GitHub Desktop.
9. Jin merges or requests changes.

This removes most GPT/Codex copy-paste because the Issue becomes the shared task contract.

## 17. Final Recommendation

Use GitHub Issues as the planning source of truth and Pull Requests as the execution/audit source of truth.

Codex should implement.

Claude Code should optionally review.

Jin should approve scope, merge, and any high-risk action.

