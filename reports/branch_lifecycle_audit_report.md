# Branch Lifecycle Audit Report

Date: 2026-06-28

Branch: `dev-clean`

Scope: governance-only branch lifecycle classification.

## Summary

- Total branch refs excluding `origin/HEAD`: 49.
- ACTIVE count: 6.
- EXPERIMENTAL count: 22.
- STALE count: 16.
- ARCHIVED count: 5.
- Branch deletion executed: No.
- Branch merge executed: No.
- Product code changed: No.
- `app.py` changed: No.
- `modules/` changed: No.
- `data/` changed: No.
- Golden JSON changed: No.

## Classification Rules Used

- `ACTIVE`: active integration or protected stable branch.
- `EXPERIMENTAL`: branch has unique work or task-specific Codex changes requiring review before merge.
- `STALE`: branch is superseded, already merged into `dev-clean`, or old divergent development context.
- `ARCHIVED`: backup, freeze, rollback, recovery, or dirty-state preservation reference.

`safe to delete` means candidate only. It is not approval to delete. Remote deletion requires Jin approval.

## Branch Classification Table

| Branch ref | Scope | Stage | Purpose | Merge-safe | Safe to delete locally | Safe to delete remote | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `backup/pre-clean-20260626` | local | `ARCHIVED` | Safety backup before cleanup | no | no | no | Read-only backup. |
| `origin/backup/pre-clean-20260626` | remote | `ARCHIVED` | Remote safety backup | no | no | no | Keep unless Jin approves retirement. |
| `dev-clean` | local | `ACTIVE` | Main integration branch | yes | no | no | Current development baseline. |
| `origin/dev-clean` | remote | `ACTIVE` | Remote integration branch | yes | no | no | Tracks active development baseline. |
| `main` | local | `ACTIVE` | Stable release snapshot | no | no | no | Divergent from `dev-clean`; protected role. |
| `origin/main` | remote | `ACTIVE` | Remote stable release snapshot | no | no | no | Do not treat as feature branch. |
| `main-clean` | local | `ACTIVE` | Stable clean baseline | yes | no | no | Merged into `dev-clean`; protected baseline. |
| `origin/main-clean` | remote | `ACTIVE` | Remote stable clean baseline | yes | no | no | Keep protected. |
| `codex/model-design-intelligence-system` | local | `EXPERIMENTAL` | Model intelligence design | no | no | no | Ahead of remote by 1 and ahead of `dev-clean`; keep isolated. |
| `origin/codex/model-design-intelligence-system` | remote | `EXPERIMENTAL` | Remote model intelligence design | no | no | no | Requires Jin approval before merge. |
| `codex/claude-api-cost-audit` | local | `EXPERIMENTAL` | Claude cost audit | no | no | no | Diverged from `dev-clean`; review before merge or cleanup. |
| `origin/codex/claude-api-cost-audit` | remote | `EXPERIMENTAL` | Remote Claude cost audit | no | no | no | Unique commits; not cleanup-safe yet. |
| `codex/claude-state-binding-patch` | local | `EXPERIMENTAL` | Claude state binding patch | no | no | no | Contains `dev-clean` plus unique commits. |
| `origin/codex/claude-state-binding-patch` | remote | `EXPERIMENTAL` | Remote Claude state binding patch | no | no | no | Review before merge. |
| `codex/claude-system-controller-upgrade` | local | `EXPERIMENTAL` | Claude controller upgrade | no | no | no | Contains `dev-clean` plus unique commits. |
| `origin/codex/claude-system-controller-upgrade` | remote | `EXPERIMENTAL` | Remote Claude controller upgrade | no | no | no | Review before merge. |
| `codex/task-graph-initialization` | local | `EXPERIMENTAL` | Task graph initialization | no | no | no | Contains `dev-clean` plus unique commits. |
| `origin/codex/task-graph-initialization` | remote | `EXPERIMENTAL` | Remote task graph initialization | no | no | no | Review before merge. |
| `codex/task-graph-state-patch` | local | `EXPERIMENTAL` | Task graph state patch | no | no | no | Contains `dev-clean` plus unique commits. |
| `origin/codex/task-graph-state-patch` | remote | `EXPERIMENTAL` | Remote task graph state patch | no | no | no | Review before merge. |
| `codex/ui-cache-api-dry-run-refresh-button` | local | `EXPERIMENTAL` | UI-CACHE dry-run refresh button | no | no | no | Contains `dev-clean` plus unique commits. |
| `origin/codex/ui-cache-api-dry-run-refresh-button` | remote | `EXPERIMENTAL` | Remote dry-run refresh button | no | no | no | Review before merge. |
| `codex/ui-cache-api-phase-finalization` | local | `EXPERIMENTAL` | UI-CACHE phase finalization | no | no | no | Contains `dev-clean` plus unique commits. |
| `origin/codex/ui-cache-api-phase-finalization` | remote | `EXPERIMENTAL` | Remote phase finalization | no | no | no | Review before merge. |
| `codex/ui-cache-api-readonly-audit` | local | `EXPERIMENTAL` | UI-CACHE read-only audit | no | no | no | Diverged from `dev-clean`; no upstream set. |
| `origin/codex/ui-cache-api-readonly-audit` | remote | `EXPERIMENTAL` | Remote UI-CACHE read-only audit | no | no | no | Unique commits; review before cleanup. |
| `codex/ui-cache-api-static-cache-layer` | local | `EXPERIMENTAL` | Static cache layer | no | no | no | Contains `dev-clean` plus unique commits. |
| `origin/codex/ui-cache-api-static-cache-layer` | remote | `EXPERIMENTAL` | Remote static cache layer | no | no | no | Review before merge. |
| `codex/ui-cache-api-streamlit-optimization` | local | `EXPERIMENTAL` | Streamlit optimization | no | no | no | Contains `dev-clean` plus unique commits. |
| `origin/codex/ui-cache-api-streamlit-optimization` | remote | `EXPERIMENTAL` | Remote Streamlit optimization | no | no | no | Review before merge. |
| `codex/claude-packet-budget-guard` | local | `STALE` | Merged packet budget guard | yes | yes | yes | Cleanup candidate after audit and approval. |
| `origin/codex/claude-packet-budget-guard` | remote | `STALE` | Remote merged packet budget guard | yes | no | yes | Jin approval required before remote deletion. |
| `codex/protocol-consolidation-agents-md` | local | `STALE` | Merged protocol consolidation | yes | yes | yes | Cleanup candidate after audit and approval. |
| `origin/codex/protocol-consolidation-agents-md` | remote | `STALE` | Remote merged protocol consolidation | yes | no | yes | Jin approval required before remote deletion. |
| `codex/ui-cache-api-api-football-one-time-refresh` | local | `STALE` | Merged API-Football one-time refresh | yes | yes | yes | Cleanup candidate after audit and approval. |
| `origin/codex/ui-cache-api-api-football-one-time-refresh` | remote | `STALE` | Remote merged one-time refresh | yes | no | yes | Jin approval required before remote deletion. |
| `codex/ui-cache-api-api-football-refresh-gate` | local | `STALE` | Merged API-Football readiness gate | yes | yes | yes | Cleanup candidate after audit and approval. |
| `origin/codex/ui-cache-api-api-football-refresh-gate` | remote | `STALE` | Remote merged readiness gate | yes | no | yes | Jin approval required before remote deletion. |
| `codex/ui-cache-api-freshness-panel` | local | `STALE` | Merged freshness panel | yes | yes | yes | Cleanup candidate after audit and approval. |
| `origin/codex/ui-cache-api-freshness-panel` | remote | `STALE` | Remote merged freshness panel | yes | no | yes | Jin approval required before remote deletion. |
| `codex/ui-cache-api-refresh-status-layer` | local | `STALE` | Merged refresh status layer | yes | yes | yes | Cleanup candidate after audit and approval. |
| `origin/codex/ui-cache-api-refresh-status-layer` | remote | `STALE` | Remote merged refresh status layer | yes | no | yes | Jin approval required before remote deletion. |
| `feature/claude-auto-loop-v1` | local | `STALE` | Merged auto-loop experiment | yes | yes | yes | Cleanup candidate after audit and approval. |
| `origin/feature/claude-auto-loop-v1` | remote | `STALE` | Remote merged auto-loop experiment | yes | no | yes | Jin approval required before remote deletion. |
| `dev` | local | `STALE` | Old development branch | no | no | no | Divergent old branch; review before archival decision. |
| `origin/dev` | remote | `STALE` | Remote old development branch | no | no | no | Do not delete until unique commit is reviewed. |
| `freeze/current-dev-20260626-v180-recovery` | local | `ARCHIVED` | Frozen recovery worktree branch | yes | no | no | Remote is gone; keep until recovery workspace is retired. |
| `local/dirty-main-eb35538-backup` | local | `ARCHIVED` | Dirty main backup | no | no | no | Preserve as local backup unless Jin approves cleanup. |
| `失败退回版本` | local | `ARCHIVED` | Rollback branch | yes | no | no | Read-only rollback reference. |

## High-Risk Branches

- `codex/model-design-intelligence-system`: local branch is ahead of remote and ahead of `dev-clean`; model-design work must remain isolated.
- `codex/claude-state-binding-patch`, `codex/claude-system-controller-upgrade`, `codex/task-graph-*`: protocol/controller work ahead of `dev-clean`; review before merge.
- `codex/ui-cache-api-dry-run-refresh-button`, `codex/ui-cache-api-phase-finalization`, `codex/ui-cache-api-static-cache-layer`, `codex/ui-cache-api-streamlit-optimization`: ahead of `dev-clean`; do not cleanup or merge without review.
- `codex/ui-cache-api-readonly-audit`: diverged from `dev-clean` and has no local upstream; inspect before cleanup.
- `main` / `origin/main`: stable release line diverges from `dev-clean`; protected, not feature-like.
- `dev` / `origin/dev`: old divergent branch with one unique commit; inspect before archive or deletion.
- `local/dirty-main-eb35538-backup`: dirty-state preservation branch; do not delete automatically.

## Merge Risk List

- All `EXPERIMENTAL` refs are merge-risk until reviewed.
- `main` and `origin/main` are merge-risk because they are stable release refs and diverge from `dev-clean`.
- `dev` and `origin/dev` are merge-risk because they are stale and divergent.
- `local/dirty-main-eb35538-backup` is merge-risk because it preserves a dirty-state snapshot.
- ARCHIVED rollback/freeze branches must not be normal merge sources.

## Cleanup Recommendations

Do not execute cleanup automatically.

Candidate local cleanup after confirmation that no worktree depends on the branch:

- `codex/claude-packet-budget-guard`
- `codex/protocol-consolidation-agents-md`
- `codex/ui-cache-api-api-football-one-time-refresh`
- `codex/ui-cache-api-api-football-refresh-gate`
- `codex/ui-cache-api-freshness-panel`
- `codex/ui-cache-api-refresh-status-layer`
- `feature/claude-auto-loop-v1`

Candidate remote cleanup only after Jin approval:

- `origin/codex/claude-packet-budget-guard`
- `origin/codex/protocol-consolidation-agents-md`
- `origin/codex/ui-cache-api-api-football-one-time-refresh`
- `origin/codex/ui-cache-api-api-football-refresh-gate`
- `origin/codex/ui-cache-api-freshness-panel`
- `origin/codex/ui-cache-api-refresh-status-layer`
- `origin/feature/claude-auto-loop-v1`

Branches requiring review before any cleanup proposal:

- `codex/model-design-intelligence-system`
- `codex/claude-api-cost-audit`
- `codex/claude-state-binding-patch`
- `codex/claude-system-controller-upgrade`
- `codex/task-graph-initialization`
- `codex/task-graph-state-patch`
- `codex/ui-cache-api-dry-run-refresh-button`
- `codex/ui-cache-api-phase-finalization`
- `codex/ui-cache-api-readonly-audit`
- `codex/ui-cache-api-static-cache-layer`
- `codex/ui-cache-api-streamlit-optimization`
- `dev`
- `main`

## Validation

- `git fetch --all --prune`: pass.
- `git diff --check`: pass.
- `git diff -- app.py`: pass, no diff output.
- `git diff -- modules`: pass, no diff output.
- `git diff -- data`: pass, no diff output.
- `git diff -- reports/golden_output_snapshot_v1.json reports/golden_output_snapshot_v2.json reports/golden_risk_contract_v1.json`: pass, no diff output.
- Protected code/data changes: none.
