# Branch Consolidation Strategy v1

Date: 2026-06-28

Branch: `dev-clean`

Scope: non-destructive consolidation planning only.

## Executive Summary

- Branch system health: `complex`.
- Consolidation risk level: `medium-high`.
- Ready for simplification phase: `YES`, but only for planning and review.
- Ready for deletion execution: `NO`.
- Ready for merge execution: `NO`.

The branch lifecycle system is stable enough to guide simplification, but the repository still has many experimental branches with unique commits. The next phase must remain consolidation planning, not execution.

## Source Inputs

- `reports/branch_lifecycle_audit_report.md`
- `docs/BRANCH_LIFECYCLE_SYSTEM.md`
- `git branch -a`

## Branch Mapping

| Branch ref | Lifecycle stage | Role | Risk | Merge candidate |
| --- | --- | --- | --- | --- |
| `dev-clean` | `ACTIVE` | Main integration branch | low | no |
| `origin/dev-clean` | `ACTIVE` | Remote integration branch | low | no |
| `main` | `ACTIVE` | Stable release snapshot | medium | no |
| `origin/main` | `ACTIVE` | Remote stable release snapshot | medium | no |
| `main-clean` | `ACTIVE` | Stable clean baseline | low | no |
| `origin/main-clean` | `ACTIVE` | Remote stable clean baseline | low | no |
| `codex/model-design-intelligence-system` | `EXPERIMENTAL` | Model intelligence design | high | yes, after review |
| `origin/codex/model-design-intelligence-system` | `EXPERIMENTAL` | Remote model intelligence design | high | yes, after review |
| `codex/claude-api-cost-audit` | `EXPERIMENTAL` | Claude cost audit | medium | maybe |
| `origin/codex/claude-api-cost-audit` | `EXPERIMENTAL` | Remote Claude cost audit | medium | maybe |
| `codex/claude-state-binding-patch` | `EXPERIMENTAL` | Claude state binding patch | medium | yes, after review |
| `origin/codex/claude-state-binding-patch` | `EXPERIMENTAL` | Remote Claude state binding patch | medium | yes, after review |
| `codex/claude-system-controller-upgrade` | `EXPERIMENTAL` | Claude controller upgrade | medium | yes, after review |
| `origin/codex/claude-system-controller-upgrade` | `EXPERIMENTAL` | Remote Claude controller upgrade | medium | yes, after review |
| `codex/task-graph-initialization` | `EXPERIMENTAL` | Task graph initialization | medium | yes, after review |
| `origin/codex/task-graph-initialization` | `EXPERIMENTAL` | Remote task graph initialization | medium | yes, after review |
| `codex/task-graph-state-patch` | `EXPERIMENTAL` | Task graph state patch | medium | yes, after review |
| `origin/codex/task-graph-state-patch` | `EXPERIMENTAL` | Remote task graph state patch | medium | yes, after review |
| `codex/ui-cache-api-dry-run-refresh-button` | `EXPERIMENTAL` | UI-CACHE dry-run refresh button | high | yes, after review |
| `origin/codex/ui-cache-api-dry-run-refresh-button` | `EXPERIMENTAL` | Remote dry-run refresh button | high | yes, after review |
| `codex/ui-cache-api-phase-finalization` | `EXPERIMENTAL` | UI-CACHE phase finalization | high | yes, after review |
| `origin/codex/ui-cache-api-phase-finalization` | `EXPERIMENTAL` | Remote phase finalization | high | yes, after review |
| `codex/ui-cache-api-readonly-audit` | `EXPERIMENTAL` | UI-CACHE read-only audit | medium | maybe |
| `origin/codex/ui-cache-api-readonly-audit` | `EXPERIMENTAL` | Remote UI-CACHE read-only audit | medium | maybe |
| `codex/ui-cache-api-static-cache-layer` | `EXPERIMENTAL` | Static cache layer | high | yes, after review |
| `origin/codex/ui-cache-api-static-cache-layer` | `EXPERIMENTAL` | Remote static cache layer | high | yes, after review |
| `codex/ui-cache-api-streamlit-optimization` | `EXPERIMENTAL` | Streamlit optimization | high | yes, after review |
| `origin/codex/ui-cache-api-streamlit-optimization` | `EXPERIMENTAL` | Remote Streamlit optimization | high | yes, after review |
| `codex/claude-packet-budget-guard` | `STALE` | Merged packet budget guard | low | no |
| `origin/codex/claude-packet-budget-guard` | `STALE` | Remote merged packet budget guard | low | no |
| `codex/protocol-consolidation-agents-md` | `STALE` | Merged protocol consolidation | low | no |
| `origin/codex/protocol-consolidation-agents-md` | `STALE` | Remote merged protocol consolidation | low | no |
| `codex/ui-cache-api-api-football-one-time-refresh` | `STALE` | Merged API-Football one-time refresh | low | no |
| `origin/codex/ui-cache-api-api-football-one-time-refresh` | `STALE` | Remote merged one-time refresh | low | no |
| `codex/ui-cache-api-api-football-refresh-gate` | `STALE` | Merged API-Football readiness gate | low | no |
| `origin/codex/ui-cache-api-api-football-refresh-gate` | `STALE` | Remote merged readiness gate | low | no |
| `codex/ui-cache-api-freshness-panel` | `STALE` | Merged freshness panel | low | no |
| `origin/codex/ui-cache-api-freshness-panel` | `STALE` | Remote merged freshness panel | low | no |
| `codex/ui-cache-api-refresh-status-layer` | `STALE` | Merged refresh status layer | low | no |
| `origin/codex/ui-cache-api-refresh-status-layer` | `STALE` | Remote merged refresh status layer | low | no |
| `feature/claude-auto-loop-v1` | `STALE` | Merged auto-loop experiment | low | no |
| `origin/feature/claude-auto-loop-v1` | `STALE` | Remote merged auto-loop experiment | low | no |
| `dev` | `STALE` | Old development branch | medium | no |
| `origin/dev` | `STALE` | Remote old development branch | medium | no |
| `backup/pre-clean-20260626` | `ARCHIVED` | Safety backup | low | no |
| `origin/backup/pre-clean-20260626` | `ARCHIVED` | Remote safety backup | low | no |
| `freeze/current-dev-20260626-v180-recovery` | `ARCHIVED` | Frozen recovery worktree branch | low | no |
| `local/dirty-main-eb35538-backup` | `ARCHIVED` | Dirty main backup | medium | no |
| `失败退回版本` | `ARCHIVED` | Rollback branch | low | no |

## System Overcomplexity Findings

### Duplicated Experimental Families

- UI-CACHE-API has many task-level branches that should converge into one reviewed `ui-cache-api` line or become stale after integration.
- Claude/protocol branches are split across cost audit, packet guard, state binding, system controller, and task graph work.
- Model-design currently has one named branch, but it is isolated and ahead of remote locally.

### Branches That Should Eventually Merge Into `dev-clean`

Only after review, validation, and explicit consolidation approval:

- `codex/model-design-intelligence-system`
- `codex/claude-state-binding-patch`
- `codex/claude-system-controller-upgrade`
- `codex/task-graph-initialization`
- `codex/task-graph-state-patch`
- `codex/ui-cache-api-dry-run-refresh-button`
- `codex/ui-cache-api-phase-finalization`
- `codex/ui-cache-api-static-cache-layer`
- `codex/ui-cache-api-streamlit-optimization`

Maybe-merge branches requiring diff inspection first:

- `codex/claude-api-cost-audit`
- `codex/ui-cache-api-readonly-audit`

### Obsolete But Still Present

- `codex/claude-packet-budget-guard`
- `codex/protocol-consolidation-agents-md`
- `codex/ui-cache-api-api-football-one-time-refresh`
- `codex/ui-cache-api-api-football-refresh-gate`
- `codex/ui-cache-api-freshness-panel`
- `codex/ui-cache-api-refresh-status-layer`
- `feature/claude-auto-loop-v1`
- matching remote refs for the same merged branches

These should be treated as cleanup candidates, not deletion targets yet.

### Lifecycle Rule Violations Or Pressure Points

- Several EXPERIMENTAL branches have exceeded the intended short lifetime for task branches and should be reviewed under the 2-3 Codex-Claude loop timeout rule.
- `dev` remains a stale divergent branch with a remote counterpart, which creates naming confusion against `dev-clean`.
- `main` and `main-clean` both exist as stable lines; this is manageable but needs explicit human policy to avoid accidental promotion paths.
- `freeze/current-dev-20260626-v180-recovery` is attached to a prunable worktree and should remain archived until Jin approves worktree cleanup.
- Local `codex/model-design-intelligence-system` is ahead of its remote counterpart, so it must not be used as a cleanup candidate.

## Target Final Branch Set

Ideal branch set after future approved consolidation:

| Target branch | Purpose |
| --- | --- |
| `dev-clean` | Active integration branch for reviewed work. |
| `model-design` or `codex/model-design-intelligence-system` | Single consolidated model design line. |
| `ui-cache-api` or `codex/ui-cache-api` | Single consolidated UI-CACHE-API line. |
| `ops-protocol` or `codex/ops-protocol` | Single consolidated protocol and agent governance line. |
| `experimental-sandbox` or `codex/experimental-sandbox` | Explicit place for disposable experiments. |
| `main-clean` | Protected stable clean baseline. |

`main` should be clarified by Jin as either the external release branch or retired in favor of `main-clean`; no action is proposed here.

## Proposed Merge List

Do not execute.

Review and consider merging into the proper consolidated line first, then into `dev-clean` only after approval:

- `codex/model-design-intelligence-system` -> `model-design`
- `codex/claude-state-binding-patch` -> `ops-protocol`
- `codex/claude-system-controller-upgrade` -> `ops-protocol`
- `codex/task-graph-initialization` -> `ops-protocol`
- `codex/task-graph-state-patch` -> `ops-protocol`
- `codex/ui-cache-api-dry-run-refresh-button` -> `ui-cache-api`
- `codex/ui-cache-api-phase-finalization` -> `ui-cache-api`
- `codex/ui-cache-api-static-cache-layer` -> `ui-cache-api`
- `codex/ui-cache-api-streamlit-optimization` -> `ui-cache-api`

Review before deciding merge/archive:

- `codex/claude-api-cost-audit`
- `codex/ui-cache-api-readonly-audit`

## Proposed Archive List

Do not execute.

- `backup/pre-clean-20260626`
- `origin/backup/pre-clean-20260626`
- `freeze/current-dev-20260626-v180-recovery`
- `local/dirty-main-eb35538-backup`
- `失败退回版本`
- `dev`
- `origin/dev`

## Eventual Deletion Candidate List

Do not execute.

Local candidates after confirming no active worktree depends on them:

- `codex/claude-packet-budget-guard`
- `codex/protocol-consolidation-agents-md`
- `codex/ui-cache-api-api-football-one-time-refresh`
- `codex/ui-cache-api-api-football-refresh-gate`
- `codex/ui-cache-api-freshness-panel`
- `codex/ui-cache-api-refresh-status-layer`
- `feature/claude-auto-loop-v1`

Remote candidates after Jin approval:

- `origin/codex/claude-packet-budget-guard`
- `origin/codex/protocol-consolidation-agents-md`
- `origin/codex/ui-cache-api-api-football-one-time-refresh`
- `origin/codex/ui-cache-api-api-football-refresh-gate`
- `origin/codex/ui-cache-api-freshness-panel`
- `origin/codex/ui-cache-api-refresh-status-layer`
- `origin/feature/claude-auto-loop-v1`

## Next Phase Rules

- Lifecycle system is now stable.
- Next phase is consolidation planning, not execution.
- No branch deletion until Jin approval.
- No branch merge until explicit consolidation plan approval.
- No direct changes to `main-clean`.
- No force push or history rewrite.
- No product-code, data, or golden JSON changes as part of consolidation planning.

## Recommended Next Step

Prepare a review packet that compares the unique commits in each EXPERIMENTAL branch family against `dev-clean`, grouped by target consolidated line:

- `model-design`
- `ui-cache-api`
- `ops-protocol`

This should remain read-only until Jin approves a specific merge order.
