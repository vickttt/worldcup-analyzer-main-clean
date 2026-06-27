# Task Graph

This file is the required execution state machine for World Cup Analyzer.

`TASK_GRAPH.md` is the single source of truth for `CURRENT_NODE`, valid next-node selection, and graph-governed Codex-Claude execution.

## Current Pointer

`CURRENT_NODE = NODE 1 - UI-CACHE-API AUDIT`

Current system status:

- State machine restored.
- Current executable node: `NODE 1 - UI-CACHE-API AUDIT`.
- Execution gate: `Gate 2 - Pre-Execution`.
- Branch: `dev-clean`.
- `PORTFOLIO_EXTRACTION`: `BLOCKED`.
- `BACKTEST_READY`: `NO`.

## Nodes

| Node | Name | Purpose | Branch | Status | Next |
| --- | --- | --- | --- | --- | --- |
| NODE 0 | INIT | System initialization and protocol bootstrap | `dev-clean` | `COMPLETED` | NODE 1 |
| NODE 1 | UI-CACHE-API AUDIT | Read-only UI, cache, API, and refresh-safety audit | `dev-clean` or scoped `codex/ui-cache-api-*` | `IN_PROGRESS` | NODE 2 after explicit completion |
| NODE 2 | MODEL-DESIGN ANALYSIS | Risk, model, scoring, and intelligence analysis | isolated model-design branch | `EXPERIMENTAL` | NODE 3 after Jin approval |
| NODE 3 | BRANCH CONSOLIDATION PLANNING | Branch lifecycle mapping and consolidation planning only | `dev-clean` | `COMPLETED` | NODE 4 |
| NODE 4 | EXECUTION GATE DESIGN | Execution gate and hard-stop design only | `dev-clean` | `COMPLETED` | NODE 5 after Jin approval |
| NODE 5 | FIRST REAL EXECUTION PHASE | First approved branch/archive/merge execution phase | approved branch only | `NOT_STARTED` | none |

## Node Details

### NODE 0 - INIT

- Purpose: system initialization.
- Branch: `dev-clean`.
- Status: `COMPLETED`.
- Evidence: `AGENTS.md`, governance docs, and current protocol layer are present.

### NODE 1 - UI-CACHE-API AUDIT

- Purpose: read-only UI, cache, API, and refresh-safety audit.
- Current status: `IN_PROGRESS`.
- Allowed work:
  - Streamlit performance profiling.
  - API-Football refresh flow audit.
  - Cache design analysis.
  - UI rendering optimization planning.
  - Fetch reduction strategy.
  - UI decision clarity analysis.
- Forbidden work:
  - Real API calls without approval.
  - Ranking, portfolio, strategy, odds, model, or backtest logic changes.
  - `data/history` or golden JSON writes.

### NODE 2 - MODEL-DESIGN ANALYSIS

- Purpose: risk, model, scoring, and intelligence analysis.
- Status: `EXPERIMENTAL`.
- Must remain isolated from `dev-clean` unless Jin explicitly approves a merge or promotion.
- Must not change production ranking, portfolio, strategy, odds, or backtest behavior without explicit scope.

### NODE 3 - BRANCH CONSOLIDATION PLANNING

- Purpose: lifecycle mapping and consolidation strategy.
- Status: `COMPLETED`.
- Evidence:
  - `docs/BRANCH_LIFECYCLE_SYSTEM.md`.
  - `reports/branch_lifecycle_audit_report.md`.
  - `reports/branch_consolidation_strategy_v1.md`.

### NODE 4 - EXECUTION GATE DESIGN

- Purpose: execution gating and hard-stop design.
- Status: `COMPLETED`.
- Evidence:
  - `docs/EXECUTION_GATE_SYSTEM.md`.
  - `reports/branch_consolidation_execution_plan_v1.md`.

### NODE 5 - FIRST REAL EXECUTION PHASE

- Purpose: first approved execution phase for branch archive, merge, or cleanup.
- Status: `NOT_STARTED`.
- Entry condition: Jin approval is required.
- Additional entry condition: `docs/EXECUTION_GATE_SYSTEM.md` must allow transition from Gate 2 to Gate 3 and then Gate 4.
- No action may begin while high-risk branch divergence remains unresolved.

## Rules

- `NEXT_NODE` must always come from this file.
- Codex cannot proceed if `docs/TASK_GRAPH.md` is missing or invalid.
- Git history overrides task graph state if a mismatch exists.
- If task graph and Git history disagree, report `SYSTEM_HEALTH = DRIFT` and stop.
- Claude cannot change `docs/TASK_GRAPH.md`; Claude may only recommend a valid next node.
- Codex owns task graph updates when a graph node is actually completed.
- Jin is final authority for `NODE 5` and later execution phases.
- `AUTO_ADVANCE` is allowed only when the next node exists, validation passes, Git status is clean, and the execution gate allows the transition.

## Current Decision

- `NEXT_NODE`: `NODE 1 - UI-CACHE-API AUDIT`.
- `AUTO_ADVANCE`: `NO` until current governance changes are committed and validation state is clean.
- `SYSTEM_HEALTH`: `RESTORED_WITH_DIRTY_WORKTREE`.
