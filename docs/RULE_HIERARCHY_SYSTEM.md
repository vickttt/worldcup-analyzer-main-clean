# Rule Hierarchy System

## Historical Governance Notice

This file is a historical classification map only. It is not an active rule
source. `AGENTS.md` is the only active top-level authority for this repository.
All classifications below are subordinate historical context unless `AGENTS.md`
explicitly restores them.

Date: 2026-07-01

Purpose: consolidate discovered governance, loop, execution, and observation rules into one authority hierarchy without deleting or rewriting historical files.

This document is a governance classification map only. It does not change runtime behavior, model logic, UI logic, API logic, data files, golden fixtures, or workflow execution.

## Current Rule State

Repository rule discovery found:

- 112 unique rule-related paths.
- 125 content versions.
- Multiple branch-specific and historical rule variants.
- System state before consolidation: FRAGMENTED BUT DISCOVERABLE.

System state after this classification remains FRAGMENTED until the duplicated and deprecated rule sources are explicitly reconciled in later cleanup work.

## Single Source Of Truth Rule

`AGENTS.md` is the only top-level authority for this repository.

All other governance files must be interpreted as subordinate to `AGENTS.md`. If any lower-level rule conflicts with `AGENTS.md`, the lower-level rule is blocked until Jin approves a reconciliation.

No parallel top-level authority is allowed.

Reports, audit logs, Claude artifacts, workflow outputs, and historical branch documents are evidence. They do not override `AGENTS.md`.

## Rule Hierarchy Tree

### LEVEL 0 - SYSTEM ROOT

| File | Classification | Authority |
| --- | --- | --- |
| `AGENTS.md` | ACTIVE | Single source of truth for agent behavior, branch rules, forbidden paths, risk gates, Claude review boundaries, API safety, and stop conditions. |

### LEVEL 1 - HISTORICAL EXECUTION CONTROL

These files formerly described execution control. They are historical or subordinate only and do not override `AGENTS.md`.

| File | Classification | Authority |
| --- | --- | --- |
| `docs/TASK_GRAPH.md` | DEPRECATED | Historical graph dependency and drift notes only. |
| `docs/EXECUTION_GATE_SYSTEM.md` | DEPRECATED | Historical branch-consolidation gate design only. |
| `docs/DECISION_LAYER_CONTROL_SYSTEM.md` | DEPRECATED | Historical decision-layer design only. |

These files must not be used as active execution rules unless `AGENTS.md` is explicitly updated to restore them.

### LEVEL 2 - DOMAIN RULES

These files constrain domain-specific work. They are active only within their domain and phase.

| File or Rule Family | Classification | Authority |
| --- | --- | --- |
| `docs/UI_CACHE_API_PROTOCOL.md` | SUBORDINATE REFERENCE | Historical UI-CACHE-API phase rules; does not override `AGENTS.md`. |
| `docs/API_REFRESH_SAFETY.md` | SUBORDINATE REFERENCE | API-Football refresh safety reference; does not override `AGENTS.md`. |
| `docs/PRODUCT_PRINCIPLES.md` | SUBORDINATE REFERENCE | Product-level intent and non-runtime decision principles. |
| `docs/TASK_QUEUE.md` | SUBORDINATE REFERENCE | Queued work inventory; not an execution permit by itself. |
| `docs/KNOWN_BUGS.md` | SUBORDINATE REFERENCE | Known issue inventory; not an execution permit by itself. |
| Model-design rules in `AGENTS.md` and model-design governance docs | SUBORDINATE REFERENCE | Model contract context only when explicitly scoped by `AGENTS.md` and the user task. |
| OPS and branch governance docs | SUBORDINATE REFERENCE | Historical GitHub workflow discipline; does not override `AGENTS.md`. |

### LEVEL 3 - HISTORICAL LOOP SYSTEMS

These files define review and agent-loop behavior.

| File | Classification | Authority |
| --- | --- | --- |
| `docs/CODEX_CLAUDE_LOOP.md` | DEPRECATED | Historical loop protocol; superseded by `AGENTS.md`. |
| `docs/CLAUDE_REVIEW_PROMPT_TEMPLATE.md` | DEPRECATED | Historical prompt contract; superseded by `AGENTS.md`. |
| `.github/workflows/claude-review.yml` | MANUAL TOOL | Manual review implementation only, not policy authority. |
| `docs/CODEX_CLAUDE_REVIEW_LOOP.md` | DEPRECATED | Older review-loop lineage. Retained for history only. |
| Numbered workflow or loop copies such as `claude-review 2.yml` | DEPRECATED | Historical duplicates unless explicitly re-promoted. |

### LEVEL 4 - OBSERVATION / REPORTS

These files record findings, validation results, and historical evidence.

| File Family | Classification | Authority |
| --- | --- | --- |
| `reports/*` | OBSERVATION | Evidence, analysis, artifacts, and review outputs. |
| `reports/claude_reviews/*` | OBSERVATION | Claude review packets and artifacts. |
| `docs/CHANGELOG.md` | OBSERVATION | Durable change history. Required reading, not an execution authority. |
| `docs/QA_REPORT.md` | OBSERVATION | Validation and QA history. Required reading, not an execution authority. |
| Audit logs and archived findings | OBSERVATION | Historical evidence only. |

## Active / Deprecated / Observation Classification

### CURRENT ACTIVE AUTHORITY

- `AGENTS.md`

### SUBORDINATE / HISTORICAL REFERENCES

- `docs/UI_CACHE_API_PROTOCOL.md`
- `docs/API_REFRESH_SAFETY.md`
- `docs/PRODUCT_PRINCIPLES.md`
- `docs/GPT_CONTEXT.md`
- `docs/TASK_QUEUE.md`
- `docs/KNOWN_BUGS.md`
- Current non-numbered GitHub workflow and template files.

### DEPRECATED

- `docs/CODEX_CLAUDE_REVIEW_LOOP.md`
- `docs/TASK_GRAPH.md`
- `docs/EXECUTION_GATE_SYSTEM.md`
- `docs/DECISION_LAYER_CONTROL_SYSTEM.md`
- `docs/CODEX_CLAUDE_LOOP.md`
- `docs/CLAUDE_REVIEW_PROMPT_TEMPLATE.md`
- Numbered duplicate governance, workflow, issue-template, PR-template, and hook-plan files.
- Historical workflow variants that are not referenced by `AGENTS.md` or current GitHub Actions usage.
- Branch-specific copies superseded by the current active files.

Deprecated files must not be deleted during this consolidation. They should remain available as history until Jin approves cleanup.

### OBSERVATION

- `reports/*`
- `reports/claude_reviews/*`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`
- Audit reports, branch reports, and downloaded workflow artifacts.

Observation files may recommend actions, but they do not authorize execution by themselves.

## Cross-Layer Conflict Register

### 1. UI vs MODEL Scope Conflict

- Sources: `AGENTS.md`, `docs/TASK_GRAPH.md`, current branch naming, model-design governance files.
- Conflict: `AGENTS.md` identifies the current phase as UI-CACHE-API, while the current task graph and branch context include model-design continuation nodes.
- Rule: do not execute new product work until phase, branch, and task graph scope are aligned.

### 2. TASK_GRAPH vs EXECUTION_GATE Conflict

- Sources: `docs/TASK_GRAPH.md`, `docs/EXECUTION_GATE_SYSTEM.md`, `docs/DECISION_LAYER_CONTROL_SYSTEM.md`.
- Conflict: graph readiness, execution gates, and fragmented-rule state can point to different next actions.
- Rule: if graph and gate state disagree, execution is blocked and consolidation mode wins.

### 3. Loop System Version Conflict

- Sources: `docs/CODEX_CLAUDE_LOOP.md`, `docs/CODEX_CLAUDE_REVIEW_LOOP.md`, historical Claude review artifacts.
- Conflict: active three-round loop protocol coexists with older review-loop variants.
- Rule: `docs/CODEX_CLAUDE_LOOP.md` is primary; `docs/CODEX_CLAUDE_REVIEW_LOOP.md` is deprecated.

### 4. API Policy vs Runtime Behavior Conflict

- Sources: `AGENTS.md`, `docs/API_REFRESH_SAFETY.md`, `docs/UI_CACHE_API_PROTOCOL.md`, legacy runtime/API code paths.
- Conflict: current governance says API-Football is the only keyed API target and Odds API is disabled for this phase, while legacy runtime paths may still exist.
- Rule: legacy API paths must not be treated as approval to call them. Future API work requires explicit scope and safety review.

### 5. Report Authority Conflict

- Sources: `reports/*`, `docs/CHANGELOG.md`, `docs/QA_REPORT.md`, Claude artifacts, `AGENTS.md`.
- Conflict: reports contain recommendations that can look like execution instructions.
- Rule: reports are observation only unless `AGENTS.md`, `TASK_GRAPH`, and active gates permit execution.

## Duplication Map

Top duplication sources identified during repository rule discovery:

1. `docs/CHANGELOG.md` - many branch-specific content versions.
2. `docs/QA_REPORT.md` - many branch-specific content versions.
3. `AGENTS.md` - multiple content versions across active and historical branches.
4. `docs/TASK_GRAPH.md` - multiple graph-state versions across branches.
5. GitHub workflow/template duplicates - numbered copies of `claude-review.yml`, `agent-qa.yml`, issue templates, PR templates, hook plans, and subagent docs.

## Conflict Count

Known conflict groups: 5.

Conflicting source families involved: 8 primary families:

- `AGENTS.md`
- `docs/TASK_GRAPH.md`
- `docs/EXECUTION_GATE_SYSTEM.md`
- `docs/DECISION_LAYER_CONTROL_SYSTEM.md`
- `docs/CODEX_CLAUDE_LOOP.md`
- `docs/CODEX_CLAUDE_REVIEW_LOOP.md`
- UI/API domain rules
- reports and workflow artifacts

## Recommended Cleanup Order

No cleanup action is approved by this document. Recommended order for future Jin-approved cleanup:

1. Confirm `AGENTS.md` as the permanent root authority and add back-references from active subordinate files.
2. Reconcile `TASK_GRAPH`, execution gates, and decision-layer state into one current pointer.
3. Deprecate or archive `docs/CODEX_CLAUDE_REVIEW_LOOP.md` in favor of `docs/CODEX_CLAUDE_LOOP.md`.
4. Classify and quarantine numbered duplicate workflow/template/governance files.
5. Move durable findings from scattered reports into consolidated system analysis.
6. Separate observation reports from execution instructions.
7. Audit API policy/runtime mismatch before any future keyed API refresh work.

## Execution Readiness

System can safely enter execution phase: NO.

Reason: rule authority is now classified, but the repository still has fragmented historical rule sources, phase/node ambiguity, loop-version duplication, and API policy/runtime drift. Execution should remain blocked until Jin approves the next cleanup or reconciliation step.
