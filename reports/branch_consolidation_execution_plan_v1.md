# Branch Consolidation Execution Plan v1

Date: 2026-06-28

Branch: `dev-clean`

Scope: final pre-execution review only.

## Status

- Lifecycle system: complete and stable.
- Phase 1 consolidation planning: complete.
- System health: `complex but stable`.
- Merge actions performed: No.
- Delete actions performed: No.
- Push actions performed: No.
- Product-code changes performed: No.

## Input State Reload

Inputs requested:

- `reports/branch_consolidation_strategy_v1.md`: present and used.
- `reports/branch_lifecycle_audit_report.md`: present and used.
- `reports/branch_consolidation_map_v1.md`: not present in the current reports directory.

Classification consistency result:

- Lifecycle audit and consolidation strategy are consistent.
- Both classify the system as 49 branch refs excluding `origin/HEAD`.
- Both classify the branch system as complex with many EXPERIMENTAL refs.
- Both keep merge and deletion execution blocked pending Jin approval.
- Because `reports/branch_consolidation_map_v1.md` is missing, this plan treats the existing strategy mapping as the authoritative map for this checkpoint.

## Execution Readiness

- System readiness for execution: `NO`.
- System readiness for a Jin approval review: `YES`.
- Safe merge candidates now: none.
- Safe archive candidates now: stale merged branches only, and only as an approved archive action.
- Safe delete candidates later: stale merged branches only, and only after Jin approval.
- High-risk branches: all model-design, ui-cache-api, ops-protocol, and experimental-sandbox candidates.

## 1. Safe To Merge Now

None.

Reason:

- A merge into `dev-clean` is not zero-risk while the workspace still has uncommitted governance files.
- The remaining useful candidate branches belong to model-design, UI-CACHE-API, or ops-protocol families.
- Several high-risk branches contain `app.py` diffs, task graph diffs, or overlapping Claude review artifacts.
- The explicit rule is no merge until Jin approves a consolidation plan and merge order.

## 2. Safe To Archive Now

Do not execute automatically.

These branches are already merged into `dev-clean` and are candidates for archive marking:

- `codex/claude-packet-budget-guard`
- `codex/protocol-consolidation-agents-md`
- `codex/ui-cache-api-api-football-one-time-refresh`
- `codex/ui-cache-api-api-football-refresh-gate`
- `codex/ui-cache-api-freshness-panel`
- `codex/ui-cache-api-refresh-status-layer`
- `feature/claude-auto-loop-v1`

Matching remote refs are also archive candidates, but remote changes require Jin approval:

- `origin/codex/claude-packet-budget-guard`
- `origin/codex/protocol-consolidation-agents-md`
- `origin/codex/ui-cache-api-api-football-one-time-refresh`
- `origin/codex/ui-cache-api-api-football-refresh-gate`
- `origin/codex/ui-cache-api-freshness-panel`
- `origin/codex/ui-cache-api-refresh-status-layer`
- `origin/feature/claude-auto-loop-v1`

Worktree dependency check:

- None of the safe archive candidate branches are currently checked out in a worktree.
- Current worktrees are `dev-clean`, detached `worldcup-analyzer`, `freeze/current-dev-20260626-v180-recovery`, and rollback branch `失败退回版本`.

## 3. Safe To Delete Later

Do not execute.

Local branches that may become deletion candidates after approved archive marking:

- `codex/claude-packet-budget-guard`
- `codex/protocol-consolidation-agents-md`
- `codex/ui-cache-api-api-football-one-time-refresh`
- `codex/ui-cache-api-api-football-refresh-gate`
- `codex/ui-cache-api-freshness-panel`
- `codex/ui-cache-api-refresh-status-layer`
- `feature/claude-auto-loop-v1`

Remote branches that may become deletion candidates only after Jin approval:

- `origin/codex/claude-packet-budget-guard`
- `origin/codex/protocol-consolidation-agents-md`
- `origin/codex/ui-cache-api-api-football-one-time-refresh`
- `origin/codex/ui-cache-api-api-football-refresh-gate`
- `origin/codex/ui-cache-api-freshness-panel`
- `origin/codex/ui-cache-api-refresh-status-layer`
- `origin/feature/claude-auto-loop-v1`

Not delete candidates:

- `backup/pre-clean-20260626`
- `origin/backup/pre-clean-20260626`
- `freeze/current-dev-20260626-v180-recovery`
- `local/dirty-main-eb35538-backup`
- `失败退回版本`
- `dev`
- `origin/dev`
- `main`
- `origin/main`
- `main-clean`
- `origin/main-clean`

## 4. High Risk - Must Not Touch Yet

These branches must not be merged, archived, or deleted in the next execution step:

### Model Design

- `codex/model-design-intelligence-system`
- `origin/codex/model-design-intelligence-system`

Reason:

- Local branch is ahead of remote and ahead of `dev-clean`.
- Contains 28 commits ahead of `dev-clean`.
- Contains `app.py` differences and model-design artifacts.
- Overlaps with UI and ops branches through `AGENTS.md`, `docs/CHANGELOG.md`, `docs/QA_REPORT.md`, and protocol docs.

### UI-CACHE-API

- `codex/ui-cache-api-dry-run-refresh-button`
- `origin/codex/ui-cache-api-dry-run-refresh-button`
- `codex/ui-cache-api-phase-finalization`
- `origin/codex/ui-cache-api-phase-finalization`
- `codex/ui-cache-api-readonly-audit`
- `origin/codex/ui-cache-api-readonly-audit`
- `codex/ui-cache-api-static-cache-layer`
- `origin/codex/ui-cache-api-static-cache-layer`
- `codex/ui-cache-api-streamlit-optimization`
- `origin/codex/ui-cache-api-streamlit-optimization`

Reason:

- Several branches contain `app.py` differences.
- Several branches contain overlapping `docs/TASK_GRAPH.md`, `AGENTS.md`, static-cache, streamlit optimization, and Claude review artifacts.
- UI-CACHE-API branches should first be consolidated into one reviewed UI line, not merged directly into `dev-clean` by branch cleanup.

### Ops Protocol

- `codex/claude-api-cost-audit`
- `origin/codex/claude-api-cost-audit`
- `codex/claude-state-binding-patch`
- `origin/codex/claude-state-binding-patch`
- `codex/claude-system-controller-upgrade`
- `origin/codex/claude-system-controller-upgrade`
- `codex/task-graph-initialization`
- `origin/codex/task-graph-initialization`
- `codex/task-graph-state-patch`
- `origin/codex/task-graph-state-patch`

Reason:

- Some ops branches are docs/report-only, but others overlap with `app.py`, `AGENTS.md`, `docs/TASK_GRAPH.md`, and Claude controller protocol.
- Ops branches need an `ops-protocol` consolidation review before any merge or cleanup.

### Experimental Sandbox / Legacy Divergence

- `dev`
- `origin/dev`
- `main`
- `origin/main`
- `local/dirty-main-eb35538-backup`

Reason:

- `dev` has large historical data and module differences relative to `dev-clean`.
- `main` and `origin/main` are stable release refs, not cleanup targets.
- `local/dirty-main-eb35538-backup` is a dirty-state preservation branch.

## 5. Dependency Safety Check

| Branch family | Divergence from `dev-clean` | Experimental logic | Overlap risk | Decision |
| --- | --- | --- | --- | --- |
| model-design | Significant: 28 commits ahead locally | Yes, model-design artifacts and `app.py` diffs | High: overlaps docs, app, and protocol files | Must not touch yet |
| ui-cache-api active experiments | Significant: 10-24 commits ahead for several branches | Yes, UI/cache/API behavior preparation | High: `app.py`, `TASK_GRAPH`, static cache, Streamlit docs and reports | Must not touch yet |
| ui-cache-api readonly audit | Diverged: 15 behind, 3 ahead | Report-only based on file sample | Medium: audit reports and QA/changelog overlap | Must not touch yet |
| ops-protocol active experiments | Mixed: some ahead only, some diverged | Yes, task graph/controller/protocol behavior | Medium-high: `AGENTS.md`, `TASK_GRAPH`, Claude artifacts | Must not touch yet |
| stale merged branches | Behind only, already merged into `dev-clean` | No active logic | Low | Archive candidates only |
| old `dev` | Severe: 41 behind, 1 ahead with many data/module diffs | Historical mixed work | Critical: data/history, data/worldcup2026, modules | Must not touch yet |
| stable `main` | Diverged as protected release ref | No cleanup logic | Medium: branch-role confusion | Must not touch yet |

## 6. Execution Order

Do not execute until Jin approves.

### Phase A - Archive Safe Branches Only

Allowed only after approval:

- Mark stale merged branch families as archived in governance docs or GitHub branch notes if available.
- Confirm no worktree is attached.
- Confirm no unpushed local work exists.
- Do not delete branches during Phase A.

Candidate families:

- merged Claude packet/protocol branches
- merged UI-CACHE-API freshness/readiness/refresh-status branches
- merged Claude auto-loop feature branch

### Phase B - Merge Only Low-Risk Docs-Only Branches

Current status: no branch is approved for Phase B yet.

Before Phase B can start:

- Inspect each candidate diff against `dev-clean`.
- Confirm no `app.py`, `modules/`, `data/`, or golden JSON changes.
- Confirm Claude review artifacts and `docs/TASK_GRAPH.md` state are consistent.
- Get Jin approval for exact merge order.

Possible future review candidates:

- `codex/claude-api-cost-audit`
- `codex/task-graph-initialization`
- `codex/task-graph-state-patch`

### Phase C - No Action On Model / UI / Ops Branches

No action until separate consolidation plans exist for:

- `model-design`
- `ui-cache-api`
- `ops-protocol`
- `experimental-sandbox`

These branches must stay isolated from `dev-clean`.

## 7. Freeze Rule Confirmation

- `dev-clean` must never be modified indirectly through an unreviewed merge chain.
- `model-design` must remain isolated.
- `ui-cache-api` must remain isolated.
- `ops-protocol` must remain isolated.
- `experimental-sandbox` must remain isolated.
- No cleanup branch may be used as a backdoor path into `dev-clean`.
- No branch deletion, merge, push, force push, or history rewrite may occur without explicit approval.

## 8. Forbidden Actions List

Do not perform:

- Deleting any local branch.
- Deleting any remote branch.
- Merging any branch into `dev-clean`.
- Merging `dev-clean` into any high-risk branch as part of cleanup.
- Pushing any consolidation changes.
- Force pushing or rewriting history.
- Modifying `app.py`.
- Modifying `modules/`.
- Modifying `data/` or `data/history/`.
- Modifying golden JSON.
- Changing ranking, portfolio, strategy, odds, or backtest logic.
- Treating `safe to delete later` as approval to delete.

## 9. Recommended Next Step

STOP and request Jin approval.

Recommended approval question:

- Approve Phase A archive marking only for the stale merged branches listed in this report?

Do not start Phase B or Phase C until Phase A is approved and completed.

## Validation

- `git diff --check`: pass.
- Protected-path diff check for `app.py`: pass, no diff output.
- Protected-path diff check for `modules/`: pass, no diff output.
- Protected-path diff check for `data/`: pass, no diff output.
- Protected-path diff check for golden JSON: pass, no diff output.
