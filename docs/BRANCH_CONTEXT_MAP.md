# Branch Context Map

This document defines branch ownership and chat-context safety rules for World Cup Analyzer.

## Current Branch Roles

| Branch or branch family | Role | Allowed scope | Must not touch |
| --- | --- | --- | --- |
| `dev-clean` | Production development integration branch | Reviewed, validated work ready to become the next stable development baseline | Unapproved experimental model research, unreviewed branch artifacts, accidental data snapshots |
| `codex/model-design-intelligence-system` | Experimental AI/model research | Model intelligence design notes, research scaffolding, isolated planning | Direct integration into `dev-clean`, production ranking behavior, portfolio extraction, backtest enablement without approval |
| `codex/ui-cache-api-*` | UI-CACHE-API feature branches | UI freshness panel, refresh status layer, static cache, controlled API refresh tasks, performance layer work | Model/ranking behavior, portfolio logic, backtest logic, unapproved repeated API calls |
| `codex/protocol-consolidation-agents-md` | OPS / protocol consolidation branch | Workflow, GitHub, Claude review, Codex operating protocol, guardrail documentation | Product behavior, data snapshots, golden JSON, runtime recommendation logic |
| `codex/claude-*` | OPS / Claude-system support branches | Claude review infrastructure, packet validation, API-cost guardrails, state binding rules | Product behavior, unapproved secrets handling, ranking/portfolio/backtest logic |
| `feature/*` | Scoped feature work | Single-task implementation from `dev-clean` unless explicitly stated otherwise | Mixed UI/model/data/backtest changes in one task |
| `backup/*`, `freeze/*`, recovery branches | Historical backup or recovery | Read-only reference unless Jin explicitly approves recovery work | Normal development |
| `main` / `origin/main` | Stable release branch | PR-only promotion from reviewed integration state | Direct Codex development |

## Lifecycle Stage Overlay

All branches must now carry a lifecycle stage from `docs/BRANCH_LIFECYCLE_SYSTEM.md`.

| Branch or branch family | Lifecycle stage | Merge-safe by default | Cleanup posture |
| --- | --- | --- | --- |
| `dev-clean` | `ACTIVE` | Yes | Keep active. |
| `main`, `main-clean`, and remotes | `ACTIVE` protected stable | No direct development | Keep protected. |
| `codex/model-design-*` | `EXPERIMENTAL` | No | Review after 2-3 Codex-Claude loops without merge. |
| `codex/ui-cache-api-*` | `EXPERIMENTAL` until reviewed, `STALE` after merge/supersession | Only if already merged into `dev-clean` | Mark before cleanup. |
| `codex/claude-*`, `codex/task-graph-*` | `EXPERIMENTAL` unless already merged | No unless merged into `dev-clean` | Review protocol diff before merge or cleanup. |
| `feature/*` | `EXPERIMENTAL` until reviewed, `STALE` after merge/supersession | Only if already merged into `dev-clean` | Candidate after audit. |
| `backup/*`, `freeze/*`, rollback, recovery | `ARCHIVED` | No normal merge | Read-only reference. |
| `dev` and other old development branches | `STALE` | No | Review before archive or deletion proposal. |

Deletion is never automatic. Codex may propose cleanup only; Jin must approve remote branch deletion.

## Execution Gate State

Branch consolidation is controlled by `docs/EXECUTION_GATE_SYSTEM.md`.

Current state:

- `Gate 2 - Pre-Execution`.

Allowed now:

- Branch inspection.
- Lifecycle classification.
- Reporting.
- Dependency mapping.
- Risk analysis.
- Execution planning with no action.

Blocked now:

- Branch merge.
- Branch archive action.
- Branch deletion.
- Push.
- Direct or indirect `dev-clean` modification through merge chains.
- Direct `main-clean` modification.
- Action on model-design, active UI-CACHE-API, ops-protocol, or experimental-sandbox branches while high-risk divergence remains unresolved.

## Hard Branch Rules

- `dev-clean` is the only stable development integration branch.
- `codex/model-design-intelligence-system` is experimental only.
- Never merge `codex/model-design-intelligence-system` into `dev-clean` without explicit Jin approval.
- Never assume a Codex chat context matches the active Git branch.
- Every task must explicitly confirm current branch, target branch, and allowed files.
- Every new task must declare branch type, lifecycle stage, and expected lifetime.
- If branch context and working tree state disagree, stop before edits unless the cleanup action is explicitly scoped.

## What Must Never Cross Branches Silently

- `data/history` snapshots
- `data/worldcup2026` data
- golden JSON fixtures
- `app.py` runtime behavior
- modules under `modules/strategy`, `modules/portfolio`, `modules/backtest`, or odds settlement paths
- API keys, `.env` content, Streamlit secrets, or runtime API payloads
- unreviewed experimental model-design docs or generated artifacts

## When To Create A New Branch

Create a new branch when the task:

- changes runtime behavior
- changes UI behavior
- touches model, strategy, ranking, portfolio, odds, or backtest code
- changes API refresh behavior or cache behavior
- adds a new validation tool or report generator
- updates workflow or Claude/Codex operating protocol beyond a small typo fix

Use `codex/` as the default branch prefix unless Jin specifies another branch name.

Default lifecycle routing:

- `UI-CACHE`: `feature/ui-cache-api/*` or `codex/ui-cache-api-*`, lifecycle `EXPERIMENTAL`, short lifetime.
- `MODEL`: `codex/model-design-*`, lifecycle `EXPERIMENTAL`, medium or long lifetime.
- `OPS`: `dev-clean` for tiny docs-only changes, otherwise `codex/ops-*`, lifecycle `ACTIVE` or `EXPERIMENTAL` depending on branch.
- `RISK`: `codex/risk-*`, lifecycle `EXPERIMENTAL`, medium lifetime.

Experimental branches older than 2-3 Codex-Claude loops without merge must be reviewed and either promoted, marked `STALE`, or archived.

## Context Cleanup Procedure

When a chat/context is on the wrong branch:

1. Run `git branch --show-current` and `git status`.
2. Identify whether uncommitted changes exist.
3. If uncommitted files exist on the wrong branch, do not merge.
4. Stash, commit to the explicitly correct branch, or stop and report the divergence.
5. Switch to the target branch only after the wrong branch is clean.
6. Re-read required docs on the target branch before editing.
7. Reconfirm allowed files before writing.

## Current Isolation Note

As of 2026-06-28, local branch analysis showed:

- `dev-clean` at `51245e0` is the merge base for `codex/model-design-intelligence-system`.
- `codex/model-design-intelligence-system` is ahead of `dev-clean` with UI-CACHE-API and model-design commits.
- No automatic merge from `codex/model-design-intelligence-system` to `dev-clean` is approved.
- Untracked `data/history` snapshots found while on the experimental branch were isolated in a stash before returning to `dev-clean`.
