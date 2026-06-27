# Task Graph

This file is the required execution state machine for World Cup Analyzer.

`TASK_GRAPH.md` is the single source of truth for `CURRENT_NODE`, valid next-node selection, and graph-governed Codex-Claude execution.

## Current Pointer

`CURRENT_NODE = NODE 2 - MODEL-DESIGN ANALYSIS (READ ONLY)`

Current system status:

- State machine restored.
- Current executable node: `NODE 2 - MODEL-DESIGN ANALYSIS (READ ONLY)` completed; next node is `NODE 3B - MODEL-DESIGN ANALYSIS CONTINUATION (READ ONLY)` and must not auto-execute until Claude loop is explicitly resumed.
- Execution gate: `Gate 2 - Pre-Execution`.
- Branch: `dev-clean`.
- `PORTFOLIO_EXTRACTION`: `BLOCKED`.
- `BACKTEST_READY`: `NO`.

## Nodes

| Node | Name | Purpose | Branch | Status | Next |
| --- | --- | --- | --- | --- | --- |
| NODE 0 | INIT | System initialization and protocol bootstrap | `dev-clean` | `COMPLETED` | NODE 1 |
| NODE 1 | UI-CACHE-API AUDIT | Read-only UI, cache, API, and refresh-safety audit | `dev-clean` or scoped `codex/ui-cache-api-*` | `COMPLETED` | NODE 2 |
| NODE 2 | MODEL-DESIGN ANALYSIS (READ ONLY) | Risk scoring flow mapping, portfolio dependency mapping, and ranking system dependency graph | `codex/model-design/*` | `COMPLETED` | NODE 3A already completed; NODE 3B ready |
| NODE 3A | BRANCH CONSOLIDATION PLANNING | Branch lifecycle mapping and consolidation planning only | `dev-clean` | `COMPLETED` | NODE 3B |
| NODE 3B | MODEL-DESIGN ANALYSIS CONTINUATION (READ ONLY) | Risk-score dependency validation, portfolio construction mapping, ranking signal-flow validation, and scenario engine linkage | `codex/model-design/*` | `READY_NOT_STARTED` | NODE 4 after review |
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
- Current status: `COMPLETED`.
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
- Evidence:
  - `reports/ui_cache_api_audit.md`.
  - `reports/streamlit_load_flow_map.md`.
  - `reports/api_refresh_flow_audit.md`.
  - `reports/cache_opportunity_map.md`.

### NODE 2 - MODEL-DESIGN ANALYSIS (READ ONLY)

- Purpose: read-only risk, model, scoring, portfolio dependency, and ranking dependency analysis.
- Status: `COMPLETED`.
- Required branch family for execution: `codex/model-design/*`.
- Allowed work:
  - risk scoring flow mapping.
  - portfolio dependency mapping.
  - ranking system dependency graph.
  - golden validation dependency mapping.
  - reports-only analysis.
- Prepared reports:
  - `reports/model_design_dependency_map.md`.
  - `reports/risk_score_flow_analysis.md`.
  - `reports/portfolio_pipeline_map.md`.
- Execution reports:
  - `reports/node2_model_flow_map.md`.
  - `reports/node2_model_dependency_graph.md`.
- Forbidden work:
  - model logic changes.
  - ranking logic changes.
  - portfolio logic changes.
  - strategy, odds, or backtest logic changes.
  - `app.py` runtime behavior changes.
  - `modules/` changes.
  - `data/` or `data/history` writes.
  - golden JSON writes.
- Result:
  - model pipeline clarity: `fragmented`.
  - dependency risk level: `high`.
  - hidden coupling severity: `high`.
  - portfolio extraction remains `BLOCKED`.
  - backtest remains `NO`.
- Auto-advance condition: `NO`; do not advance to NODE 3B automatically.

### NODE 3A - BRANCH CONSOLIDATION PLANNING

- Purpose: lifecycle mapping and consolidation strategy.
- Status: `COMPLETED`.
- Evidence:
  - `docs/BRANCH_LIFECYCLE_SYSTEM.md`.
  - `reports/branch_lifecycle_audit_report.md`.
  - `reports/branch_consolidation_strategy_v1.md`.

### NODE 3B - MODEL-DESIGN ANALYSIS CONTINUATION (READ ONLY)

- Purpose: continue model-design read-only analysis without changing runtime behavior.
- Status: `READY_NOT_STARTED`.
- Required branch family for execution: `codex/model-design/*`.
- Allowed work:
  - risk-score dependency validation.
  - portfolio construction mapping.
  - ranking signal-flow validation.
  - scenario engine linkage analysis.
  - reports-only analysis.
- Forbidden work:
  - model logic changes.
  - ranking logic changes.
  - portfolio logic changes.
  - strategy, odds, or backtest logic changes.
  - `app.py` runtime behavior changes.
  - `modules/` changes.
  - `data/` or `data/history` writes.
  - golden JSON writes.
  - branch merge, archive, or deletion.
- Entry condition: explicit loop resume task plus valid protected-path checks.
- Execution status: not executed by this repair.

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
- `AUTO_ADVANCE` is allowed only when the next node exists, validation passes, Git status is clean, branch selection is correct, Claude returns `PASS` with `BRANCH_OK: YES`, and the execution gate allows the transition.

## Current Decision

- `NODE 1 completed`: `YES`.
- `NODE 2 completed`: `YES`.
- `NODE 3A branch consolidation completed`: `YES`.
- `NODE 3B model-design continuation ready`: `YES`, not executed.
- `NEXT_NODE`: `NODE 3B - MODEL-DESIGN ANALYSIS CONTINUATION (READ ONLY)`.
- `AUTO_ADVANCE`: `NO`.
- `SYSTEM_HEALTH`: `OK`.
