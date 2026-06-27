# Branch Lifecycle System

This document defines the non-destructive branch lifecycle system for World Cup Analyzer.

## Purpose

The branch lifecycle system reduces branch confusion without deleting, merging, or rewriting any branch automatically.

This system applies to local branches, remote branches, backup branches, recovery branches, and Codex experiment branches.

## Lifecycle Stages

| Stage | Definition | Allowed activity | Merge policy |
| --- | --- | --- | --- |
| `ACTIVE` | Actively used branch or protected stable line. | Receives approved commits or controlled PR promotion. | May merge into `dev-clean` or stable branches only through the approved workflow. |
| `EXPERIMENTAL` | Codex experiment branch for model, UI, ops, risk, or protocol work. | May diverge from `dev-clean` while isolated. | Must not merge without review, validation, and explicit approval. |
| `STALE` | Superseded branch, no activity beyond the review window, or already merged into `dev-clean`. | No new development by default. | May be proposed for archival or deletion after audit. |
| `ARCHIVED` | Read-only backup, freeze, rollback, or recovery reference. | Read-only reference only. | Must not be used for normal development or merged without explicit recovery approval. |

## Stage Rules

### ACTIVE

- `dev-clean` is the active integration branch.
- `main` and `main-clean` are protected stable lines and must not receive direct Codex development.
- ACTIVE branches require clean status before new work starts.
- ACTIVE branches must not absorb experimental work without review.

### EXPERIMENTAL

- EXPERIMENTAL branches may contain unmerged Codex research or task-specific work.
- EXPERIMENTAL branches may diverge from `dev-clean`.
- EXPERIMENTAL branches must be reviewed before merge consideration.
- EXPERIMENTAL branches older than 2-3 Codex-Claude loops without merge must be reviewed and either promoted, marked STALE, or archived.

### STALE

- A branch is STALE when it is superseded, already merged, or has no active owner after the lifecycle review window.
- Stale branches must be marked first, not removed.
- Stale branches may be proposed for cleanup, but no deletion is automatic.
- Stale remote branches require Jin approval before deletion.

### ARCHIVED

- ARCHIVED branches preserve backup, freeze, rollback, or recovery history.
- ARCHIVED branches are read-only unless Jin explicitly approves a recovery operation.
- ARCHIVED branches should not be used as the base for normal feature work.

## Cleanup Rules

- No branch deletion is automatic.
- Codex may only propose deletion candidates.
- Jin must approve deletion of any remote branch.
- Stale branches must be marked or documented before any cleanup action.
- Experimental branches older than 2-3 Codex-Claude loops without merge must be reviewed before continued work.
- Branches with unique commits ahead of `dev-clean` must not be deleted until their diff is reviewed.
- Backup, freeze, rollback, and recovery branches should be preserved unless Jin explicitly approves retirement.
- No force push, history rewrite, or branch recreation is allowed as cleanup.

## Branch Creation Rules

Every new task must declare:

- Branch type: `UI`, `MODEL`, `OPS`, or `RISK`.
- Lifecycle stage: `ACTIVE` or `EXPERIMENTAL`.
- Expected lifetime: `short`, `medium`, or `long`.
- Allowed files.
- Forbidden files.

Default branch routing:

| Task type | Default branch pattern | Default lifecycle stage | Expected lifetime |
| --- | --- | --- | --- |
| `UI-CACHE` | `feature/ui-cache-api/*` or `codex/ui-cache-api-*` | `EXPERIMENTAL` until reviewed | short |
| `MODEL` | `codex/model-design-*` | `EXPERIMENTAL` | medium or long |
| `OPS` | `dev-clean` for tiny docs-only changes, otherwise `codex/ops-*` | `ACTIVE` on `dev-clean`, `EXPERIMENTAL` on feature branch | short |
| `RISK` | `codex/risk-*` | `EXPERIMENTAL` | medium |

## Merge Safety Labels

Use these labels in branch audits:

| Label | Meaning |
| --- | --- |
| `merge-safe: yes` | Branch is already merged into `dev-clean` or is the active integration/stable target. |
| `merge-safe: no` | Branch has unique commits, divergence, protected-role status, or experimental scope requiring review. |
| `safe to delete locally: yes` | Local branch is a cleanup candidate after confirming no worktree depends on it. |
| `safe to delete remote: yes` | Remote branch is a cleanup candidate only after Jin explicitly approves deletion. |

`safe to delete` never means Codex may delete automatically.

## Current Lifecycle Summary

As of 2026-06-28 after `git fetch --all --prune`:

- Total branch refs excluding `origin/HEAD`: 49.
- ACTIVE refs: 6.
- EXPERIMENTAL refs: 22.
- STALE refs: 16.
- ARCHIVED refs: 5.

Detailed classification is recorded in `reports/branch_lifecycle_audit_report.md`.

## High-Risk Branch Families

- `codex/model-design-intelligence-system`: experimental model-design work; must not merge into `dev-clean` without approval.
- `codex/ui-cache-api-*` branches that are ahead of `dev-clean`: contain unmerged task work; review before merge or cleanup.
- `codex/task-graph-*` and `codex/claude-*` branches ahead of `dev-clean`: protocol/automation changes; review before merge.
- `main` / `origin/main`: stable release snapshot currently divergent from `dev-clean`; do not treat as a feature branch.
- `dev` / `origin/dev`: old development branch; stale and divergent.
- `local/dirty-main-eb35538-backup`, `freeze/*`, and rollback branches: archival or recovery refs only.

## Governance Gate

Before any future cleanup action:

1. Re-run branch inventory.
2. Confirm no worktree depends on the target branch.
3. Confirm ahead/behind state relative to `dev-clean`.
4. Confirm whether the branch has a remote counterpart.
5. Record cleanup proposal in a report.
6. Get Jin approval before deleting any remote branch.

## Consolidation Planning Phase

As of the branch consolidation strategy v1 checkpoint:

- The lifecycle system is considered stable enough for consolidation planning.
- The next phase is consolidation planning, not execution.
- No branch deletion is allowed until Jin approves the exact branch list.
- No branch merge is allowed until Jin approves an explicit consolidation plan and merge order.
- Branch consolidation planning must remain governance-only unless a future task explicitly authorizes Git operations.
- Consolidation planning must not modify `app.py`, `modules/`, `data/`, golden JSON, ranking, portfolio, strategy, odds, or backtest logic.

## Execution Gate Binding

Branch lifecycle decisions are now controlled by `docs/EXECUTION_GATE_SYSTEM.md`.

Current gate:

- `Gate 2 - Pre-Execution`.

Current meaning:

- Lifecycle mapping is complete.
- Consolidation planning is complete.
- Final execution plans are allowed.
- Branch merge, archive, deletion, and push remain blocked.

No branch operation may move past Gate 2 unless all Gate 3 entry conditions are satisfied and Jin explicitly approves the exact action list and order.

Hard stop:

- No direct or indirect `dev-clean` modification through merge chains.
- No direct `main-clean` modification.
- No action on model-design, UI-CACHE-API, ops-protocol, or experimental-sandbox branches while high-risk divergence remains unresolved.
- No action if validation, secret scan, golden JSON validation, or workflow stability checks fail.
