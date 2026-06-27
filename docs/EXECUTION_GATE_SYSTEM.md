# Execution Gate System

This document defines the hard-stop execution gates for branch consolidation, merging, archiving, and deletion.

The current system state is `Gate 2 - Pre-Execution`.

Decision Layer status:

- Decision Layer document: `docs/DECISION_LAYER_CONTROL_SYSTEM.md`.
- Current decision mode: `CONSOLIDATION MODE`.
- Execution remains locked until Decision Layer threshold rules are satisfied.

## Purpose

The execution gate system prevents branch cleanup from becoming an accidental merge, deletion, push, or production behavior change.

No branch consolidation action is allowed unless the current gate explicitly permits it and all entry conditions are satisfied.

## Gate Overview

| Gate | Name | Allowed | Blocked |
| --- | --- | --- | --- |
| Gate 0 | Observation | Read-only inspection and analysis | File changes, branch changes, merge, archive, deletion, push |
| Gate 1 | Planning | Lifecycle mapping and consolidation strategy documents | Merge, archive, deletion, push |
| Gate 2 | Pre-Execution | Execution plans and safety reviews | Merge, archive, deletion, push |
| Gate 3 | Controlled Execution Approval | Final readiness verification after all entry conditions pass | Execution until Jin explicitly approves |
| Gate 4 | Execution | Limited approved merge or controlled archive actions | Direct `main-clean` modification, unapproved deletion, high-risk branches |
| Gate 5 | Stable System | Simplified branch structure and reduced experimental noise | Reintroducing unmanaged experimental branch noise |

## Gate 0 - Observation

Allowed:

- Branch inspection.
- Worktree inspection.
- Remote inspection.
- Lifecycle evidence gathering.
- Read-only dependency mapping.
- Read-only risk analysis.

Blocked:

- File modifications.
- Branch switching that carries dirty work.
- Merge.
- Archive marking.
- Branch deletion.
- Push.

## Gate 1 - Planning

Allowed:

- Lifecycle mapping.
- Consolidation strategy.
- Branch role classification.
- Merge-candidate analysis.
- Archive-candidate analysis.
- Deletion-candidate analysis.

Blocked:

- Merge execution.
- Archive execution.
- Deletion execution.
- Push.
- Any product-code change.

## Gate 2 - Pre-Execution

Current state: `ACTIVE`.

Allowed:

- Execution plan documents.
- Safety reviews.
- High-risk branch classification.
- Freeze-rule confirmation.
- Approval request preparation.

Blocked:

- Branch merge.
- Branch archive action.
- Branch deletion.
- Push.
- Direct or indirect modification to `dev-clean` through merge chains.
- Any modification to `app.py`, `modules/`, `data/`, golden JSON, ranking, portfolio, strategy, odds, model, UI, or backtest logic.

## Gate 3 - Controlled Execution Approval

Gate 3 is future-only.

Gate 3 may be entered only when all conditions are true:

- Decision Layer state is `EXECUTION READY MODE`.
- Report consolidation is complete and fragmentation level is `LOW`.
- Claude verdict stability is at least 3 consecutive PASS rounds.
- No high-risk branch divergence remains unresolved.
- All validation pipelines are green.
- No unreviewed experimental branch touches core systems.
- No unreviewed model, portfolio, strategy, odds, ranking, UI, API refresh, data, golden JSON, or backtest changes remain in the execution set.
- Jin explicitly approves the exact action list and order.

Gate 3 does not itself execute anything. It authorizes only a controlled transition to Gate 4.

## Gate 4 - Execution

Gate 4 is future-only.

Allowed only after Gate 3 approval:

- Limited approved merge actions.
- Controlled archive marking.
- Approved local branch deletion when explicitly listed.
- Approved remote branch deletion only when Jin explicitly authorizes the remote ref.

Blocked:

- Direct `main-clean` modification.
- Force push.
- History rewrite.
- Broad branch cleanup.
- Unlisted branch operations.
- Any action outside the approved execution order.
- Any action touching high-risk model-design, UI-CACHE-API, ops-protocol, or experimental-sandbox branches without separate approval.

## Gate 5 - Stable System

Gate 5 is reached only after an approved execution pass produces:

- Simplified branch structure.
- Reduced experimental noise.
- Consolidated branch roles.
- Clean `dev-clean`.
- Protected `main-clean`.
- No unresolved high-risk branch ambiguity.
- Recorded final validation.

## Entry Conditions For Execution

Execution is allowed only when every condition is satisfied:

- `dev-clean` is stable.
- No open high-risk experimental branches are included in the action set.
- Claude review system is stable for at least 3 cycles.
- No unreviewed model changes exist in the action set.
- No unreviewed portfolio changes exist in the action set.
- No unreviewed backtest changes exist in the action set.
- No unreviewed ranking, strategy, odds, UI, API refresh, data, or golden JSON changes exist in the action set.
- All validation tiers pass.
- Secret scan passes.
- Golden JSON validation passes.
- Jin explicitly approves the exact action list.

## Hard Block Rules

Execution is forbidden if any condition is true:

- `model-design` contains unmerged experimental logic.
- `ui-cache-api` contains unstable API behavior.
- Any risk contract, portfolio logic, or portfolio extraction gate is incomplete.
- `PORTFOLIO_EXTRACTION` remains `BLOCKED` for a task that would touch portfolio behavior.
- `BACKTEST_READY` remains `NO` for a task that would touch backtest behavior.
- Golden JSON validation fails.
- Secret scan fails.
- Workflow instability exists.
- Decision Layer state is `ANALYSIS MODE`, `CONSOLIDATION MODE`, or `EXECUTION LOCKED MODE`.
- `SYSTEM_HEALTH` is `FRAGMENTED`.
- Analysis/execution balance is `IMBALANCED`.
- A high-risk branch still has unresolved divergence from `dev-clean`.
- A branch operation could indirectly modify `dev-clean` through an unreviewed merge chain.
- Jin has not explicitly approved the exact operation.

## Safe Operations Allowed At All Times

These actions remain allowed in Gates 0-2:

- Branch inspection.
- Lifecycle classification.
- Reporting.
- Dependency mapping.
- Risk analysis.
- Execution planning with no action.

These safe operations must not mutate branches, push, merge, delete, or change product behavior.

## Current Decision

- System state: `PRE-EXECUTION`.
- Execution readiness: `NO`.
- Merge/delete readiness: `NO`.
- Next safe step: request Jin approval for a specific Gate 3 readiness review, or continue read-only planning.
