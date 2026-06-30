# Branch Consolidation Target State

Date: 2026-07-01

Scope: planning only. No branch merge, deletion, archive, rename, runtime change, model change, UI change, API change, data change, or golden fixture change is authorized by this report.

## Target State

### Core Systems

| Branch | Role | Finality |
| --- | --- | --- |
| `dev-clean` | Final integration branch and single source of truth | AUTHORITATIVE |
| `main-clean` | Stable snapshot branch | STABLE ONLY |

### Active Systems

| System | Canonical branch | Target role |
| --- | --- | --- |
| LOOP | `codex/worldcup-loop-enforcement` | Canonical temporary loop-system workspace until approved merge into `dev-clean`. |
| MODEL | `codex/model-design-intelligence-system` | Canonical temporary model-system workspace until approved merge into `dev-clean`. |
| UI | `codex/ui-cache-api-streamlit-optimization` | Canonical temporary UI-system workspace until approved merge into `dev-clean`. |
| OPS | `codex/claude-system-controller-upgrade` | Canonical temporary ops-system workspace until approved merge into `dev-clean`. |
| TASK | `dev-clean` | `AGENTS.md` and `docs/TASK_GRAPH.md` on `dev-clean` only. |

### Legacy

All non-core, non-canonical branches become legacy candidates after their useful content is confirmed merged, superseded, or intentionally discarded by Jin.

Legacy status does not mean deletion. It means the branch is not authoritative and should not drive new work.

## Merge Rules

No merge is authorized by this document.

### Branches That Can Be Considered For Future Merge Into `dev-clean`

Only after Jin approval, clean validation, protected-path checks, and conflict review:

- `codex/worldcup-loop-enforcement`
- `codex/model-design-intelligence-system`
- `codex/ui-cache-api-streamlit-optimization`
- `codex/claude-system-controller-upgrade`

### Branches That Must Never Be Merged Without Explicit Re-Approval

- `main`
- `dev`
- `backup/pre-clean-20260626`
- `freeze/current-dev-20260626-v180-recovery`
- `local/dirty-main-eb35538-backup`
- `失败退回版本`
- Any branch with unknown runtime, data, golden JSON, ranking, portfolio, strategy, odds, or backtest changes.
- Any branch that conflicts with current `dev-clean` governance.

### Branches That Should Be Treated As Superseded Unless Proven Otherwise

- `feature/claude-auto-loop-v1`
- `codex/loops`
- `codex/claude-packet-budget-guard`
- `codex/protocol-consolidation-agents-md`
- `codex/task-graph-initialization`
- `codex/task-graph-state-patch`
- older `codex/ui-cache-api-*` sequence branches already represented by the canonical UI branch or `dev-clean`.

## Merge Order Priority

Recommended future order, if Jin approves Phase 2 execution:

1. TASK baseline on `dev-clean`: confirm `AGENTS.md`, `docs/TASK_GRAPH.md`, execution gates, and rule hierarchy are consistent.
2. OPS system: merge or reconcile `codex/claude-system-controller-upgrade` if it contains only governance/tooling improvements.
3. LOOP system: merge or reconcile `codex/worldcup-loop-enforcement` after OPS stability is confirmed.
4. UI system: merge or reconcile `codex/ui-cache-api-streamlit-optimization` after loop/governance rules are stable.
5. MODEL system: merge or reconcile `codex/model-design-intelligence-system` last, because model governance can affect future execution scope.

This order keeps branch authority, review automation, UI/runtime boundaries, and model rules from being mixed prematurely.

## Archive Rules

Archive means logical classification only unless Jin later approves a real archive branch, tag, or deletion action.

### Must Keep Active

- `dev-clean`
- `main-clean`
- `codex/worldcup-loop-enforcement`
- `codex/model-design-intelligence-system`
- `codex/ui-cache-api-streamlit-optimization`
- `codex/claude-system-controller-upgrade`

### Safe To Archive After Verification

- `feature/claude-auto-loop-v1`
- `codex/loops`
- `codex/claude-packet-budget-guard`
- `codex/protocol-consolidation-agents-md`
- `codex/task-graph-initialization`
- `codex/task-graph-state-patch`
- `codex/ui-cache-api-freshness-panel`
- `codex/ui-cache-api-refresh-status-layer`
- `codex/ui-cache-api-api-football-refresh-gate`
- `codex/ui-cache-api-api-football-one-time-refresh`
- `codex/ui-cache-api-dry-run-refresh-button`
- `codex/ui-cache-api-static-cache-layer`
- `codex/ui-cache-api-phase-finalization`
- `codex/ui-cache-api-readonly-audit`
- `codex/ui-cache-api-clean-restart`

### Risky - Do Not Touch

- `main`
- `dev`
- `backup/pre-clean-20260626`
- `freeze/current-dev-20260626-v180-recovery`
- `local/dirty-main-eb35538-backup`
- `失败退回版本`
- `fix/loop-test-run`
- `fix/worldcup-launcher-round-3`
- `codex/match-data-debug-ivory-norway`
- `codex/claude-network-retry-stabilization`
- `codex/ui-api-control-stabilization`
- `codex/model-design-match-context-engine`
- `codex/model-design-intelligence-phase-start`

Risky branches need separate inspection before any archive, merge, or discard decision.

## Delete Policy

Deletion is not allowed in Phase 2 preparation.

Future deletion may be considered only when all conditions are met:

- Jin explicitly approves deletion by branch name.
- The branch is confirmed merged into `dev-clean`, superseded, or intentionally abandoned.
- No unique product, data, governance, review artifact, or audit content remains only on that branch.
- Protected-path diff against `dev-clean` is reviewed.
- Secret scan passes for branch-specific content.
- Remote and local branch delete commands are listed for approval before execution.
- A rollback reference is available through Git history or an approved archive tag.

No branch may be deleted only because it appears stale by name.

## Risk Matrix

| System | Merge risk | Conflict risk | Dependency risk | Notes |
| --- | --- | --- | --- | --- |
| LOOP | MEDIUM | MEDIUM | HIGH | Interacts with Claude/GitHub review process and may affect autonomous workflow behavior. |
| MODEL | HIGH | MEDIUM | HIGH | Can influence future model execution scope and risk gates; merge late after governance alignment. |
| UI | MEDIUM | HIGH | MEDIUM | May overlap with app/runtime behavior; protected-path checks are mandatory. |
| OPS | MEDIUM | MEDIUM | MEDIUM | Tooling/workflow changes can trigger CI behavior; confirm no workflow auto-trigger side effects. |
| TASK | HIGH | HIGH | HIGH | `AGENTS.md` and `TASK_GRAPH.md` define authority; conflicts block execution. |

## Execution Readiness

Readiness for execution: NO.

Merge plan completeness: PARTIAL.

Risk summary:

- Canonical branches are identified.
- Merge order is defined.
- Archive/delete rules are defined.
- Execution is not ready because each canonical branch still needs fresh diff review against current `dev-clean`.
- `dev-clean` remains the only final source of truth.

Recommended next step: WAIT FOR APPROVAL.
