# Decision Layer Control System

Date: 2026-06-28
Status: active governance control layer.

## Purpose

The Decision Layer controls when World Cup Analyzer should stop analysis, consolidate knowledge, or request approval for execution. It exists to prevent analysis from expanding faster than execution readiness.

This is not an execution system. It does not authorize merges, branch deletion, model changes, UI changes, portfolio extraction, or backtest enablement.

## 1. System State Problem

The current system is analysis-heavy:

- UI-CACHE-API reports exist.
- MODEL-DESIGN reports exist.
- branch lifecycle and execution-gate reports exist.
- consolidated analysis now exists.
- execution is paused by design.

Risk:

- analysis can expand faster than execution.
- reports can accumulate without decision pressure.
- duplicated findings can hide the true next action.
- the system lacks an execution pressure regulator.

## 2. Decision Layer Role

Decision Layer controls when to:

- stop analysis.
- consolidate reports.
- merge knowledge into a single system understanding.
- decide whether execution is still locked.
- decide whether a future task may request execution readiness review.

The Decision Layer sits above task reports and below Jin approval.

```text
TASK_GRAPH
  -> node reports
  -> report consolidation
  -> Decision Layer
  -> execution gate readiness
  -> Jin approval
  -> controlled execution only if all gates pass
```

## 3. Decision States

| State | Meaning | Allowed work | Blocked work |
| --- | --- | --- | --- |
| `ANALYSIS MODE` | Current system is still collecting evidence | read-only analysis, report writing | execution, merge, deletion, product changes |
| `CONSOLIDATION MODE` | Reports are fragmented or overlapping | update `reports/CONSOLIDATED_SYSTEM_ANALYSIS.md`, reduce duplication | new node execution, Claude loop triggering, branch operations |
| `EXECUTION READY MODE` | Evidence is consolidated and all readiness thresholds are met | request Jin approval for exact action list | execution without approval |
| `EXECUTION LOCKED MODE` | Any blocker remains unresolved | stop, report blocker, request decision | merge, archive, deletion, product changes |

Current state:

- `CONSOLIDATION MODE` after report fragmentation is detected.
- `EXECUTION LOCKED MODE` for branch execution, portfolio extraction, and backtest enablement.

## 4. Execution Threshold Rule

The system may enter `EXECUTION READY MODE` only when all conditions are true:

- report consolidation completed.
- fragmentation level is `LOW`.
- Claude stability is `PASS` for 3 consecutive relevant review cycles.
- no unresolved branch conflicts exist.
- no unreviewed model, UI, ops, data, golden JSON, ranking, portfolio, strategy, odds, or backtest risk remains in the execution set.
- validation and secret scans pass.
- Jin approval is present for the exact action list.

If any condition fails, execution remains locked.

## 5. Fragmented Stop Condition

If the system enters `FRAGMENTED` state:

- no new NODE execution.
- only consolidation is allowed.
- no Claude loop triggering.
- no branch operations.
- no execution-readiness promotion.

Required action:

1. Update `reports/CONSOLIDATED_SYSTEM_ANALYSIS.md`.
2. Identify duplicated or overlapping findings.
3. Mark unresolved overlaps.
4. Return to Decision Layer review.

## 6. Analysis To Execution Ratio Control

The system must enforce analysis-to-execution balance.

If analysis output grows while execution remains locked:

- force stop.
- require Decision Layer review.
- consolidate reports before adding new reports.
- do not create a new node unless Jin approves the purpose and scope.

Balance classification:

| Ratio state | Meaning | Required action |
| --- | --- | --- |
| `OK` | analysis outputs are consolidated and directly support a decision | continue planning or request approval |
| `IMBALANCED` | reports are expanding without executable decision | stop and review Decision Layer |
| `FRAGMENTED` | findings are duplicated or scattered | consolidation only |

## 7. Current Decision

- System state: `STABLE` for governance, `CONSOLIDATION MODE` for analysis.
- Analysis/execution balance: `IMBALANCED` until Decision Layer review is committed and accepted.
- NODE progression allowed: No.
- Next required action: decision layer stabilization only.

## 8. Locked Gates

These gates remain unchanged:

- `PORTFOLIO_EXTRACTION: BLOCKED`.
- `BACKTEST_READY: NO`.
- Branch execution: locked until execution threshold rule is satisfied and Jin approves.
