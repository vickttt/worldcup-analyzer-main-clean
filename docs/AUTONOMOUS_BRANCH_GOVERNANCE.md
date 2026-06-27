# Autonomous Branch Governance

This document defines how Codex may self-manage branches while preserving the World Cup Analyzer safety model.

## Purpose

Codex may choose and use branches for scoped work, but branch choice must be deterministic, documented, and reviewable. Branch autonomy does not grant permission to merge, delete, force push, rewrite history, or bypass `TASK_GRAPH.md`.

## Branch Types

| Branch family | Classification | Allowed use | Merge posture |
| --- | --- | --- | --- |
| `dev-clean` | integration only | stable reviewed integration work | receives validated changes only |
| `feature/*` | single-task execution | narrow task branches when no domain-specific prefix fits | review required before merge |
| `codex/ui-cache-api/*` | UI/cache/API work only | UI loading, cache planning, refresh safety, public/keyed API readiness analysis | merge only after validation and review |
| `codex/model-design/*` | model/risk work only | read-only model analysis, risk contract design, scoring dependency maps | isolated until Jin approves promotion |
| `codex/ops/*` | workflow/governance only | branch governance, CI planning, protocol docs, Claude loop rules | merge only when docs-only and validated |
| `experimental/*` | disposable sandbox only | short-lived experiments that may diverge | never merge without explicit review and Jin approval |

## Pre-Execution Branch Decision

Before execution, Codex must classify the task and select the branch family:

| Task content | Required branch family | Notes |
| --- | --- | --- |
| UI, cache, refresh status, API flow, Streamlit load flow | `codex/ui-cache-api/*` | no real API call unless explicitly approved |
| MODEL, risk, scoring, ranking dependency analysis | `codex/model-design/*` | read-only unless a future task explicitly unlocks implementation |
| OPS, GitHub, branch rules, workflow, Claude loop, governance docs | `codex/ops/*` or `dev-clean` for docs-only checkpoints | must not alter product behavior |
| Mixed UI plus MODEL plus OPS scope | stop and request split | do not self-merge domains |

If the task is mixed, ambiguous, or crosses a protected area, Codex must stop and request a split or explicit Jin approval.

## Required Branch Packet

Each graph-governed task should declare:

- current branch.
- intended branch family.
- task type: `UI`, `MODEL`, `OPS`, `RISK`, or `MIXED`.
- lifecycle stage: `ACTIVE`, `EXPERIMENTAL`, `STALE`, or `ARCHIVED`.
- expected lifetime: `short`, `medium`, or `long`.
- allowed files.
- forbidden files.
- whether product code, `data/history`, golden JSON, ranking, portfolio, strategy, odds, or backtest logic are in scope.
- whether a real API call, workflow trigger, merge, archive, or deletion is in scope.

## Lifecycle Rules

- `experimental/*` branches expire after 3 Codex-Claude rounds unless Jin extends them.
- Stale branches must be marked or reported first, not deleted.
- Remote deletion requires Jin approval.
- Local deletion also requires explicit user approval when the branch has unique commits or unclear purpose.
- `ARCHIVED` branches are read-only references.
- Claude may recommend cleanup review, but must not authorize deletion.

## dev-clean Protection

- `dev-clean` is an integration branch, not an experiment branch.
- Codex must not place direct experimental commits on `dev-clean`.
- `dev-clean` may receive only validated, reviewed, stable changes.
- Model-design work must remain isolated until the task graph, Claude review, validation, and Jin approval allow promotion.
- UI-CACHE-API work must not contaminate model/risk branches.
- OPS/governance changes must not carry product-code diffs.

## Cross-Domain Contamination Rules

Codex must stop if a diff contains unexpected files for the selected domain:

- UI branch with model, ranking, portfolio, strategy, odds, backtest, data, or golden JSON changes.
- MODEL branch with UI runtime changes, refresh behavior changes, data writes, or golden JSON changes.
- OPS branch with `app.py`, `modules/`, `data/`, or golden JSON changes.
- Any branch with secret values or local config committed.

## Validation Requirements

Minimum checks before reporting completion:

- `git diff --check`.
- protected-path diff check for the task scope.
- secret-shaped token scan on changed docs/reports when governance files are touched.
- `py_compile` for touched Python files, if any.
- task graph consistency check when `docs/TASK_GRAPH.md` is touched.

## Authority

- Codex may choose branches under this document.
- Claude validates branch selection and contamination risk.
- `docs/TASK_GRAPH.md` remains the state-machine source of truth.
- Git history overrides stale task graph state.
- Jin is the final authority for NODE 5 and any merge, archive, or deletion execution.
