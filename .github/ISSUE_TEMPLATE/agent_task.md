---
name: Agent Task
about: Issue-driven task for Codex / Claude agents
title: "[Area] Short action-oriented task"
labels: ["agent-task"]
assignees: ""
---

## Goal

Describe the concrete outcome this task should produce.

## Background

Explain why this task matters and link related reports, plans, screenshots, or prior PRs.

## Scope

List the exact work the agent should perform.

## Allowed Changes

- 

## Forbidden Changes

- Do not modify production ranking unless explicitly approved.
- Do not modify recommendation logic unless explicitly approved.
- Do not modify `strategy_score(...)`, `strategy_comparison(...)`, or `evaluate_allocation(...)` unless explicitly approved with `approved:ranking`.
- Do not modify `data/history/*_pre.json`, `data/history/*_post.json`, or `data/history/my_portfolios/*.json` unless explicitly approved with `approved:data-write`.
- Do not delete files unless Jin explicitly approves.
- Do not force push or rewrite Git history.

## Required Inputs

- 

## Required Outputs

- 

## Acceptance Criteria

- 

## QA Requirements

- Update `docs/CHANGELOG.md` for any code or workflow change.
- Update `docs/QA_REPORT.md` for any code or workflow change.
- Run Python syntax checks when Python files are changed.
- State whether sorting, recommendation logic, UI, and data files changed.

## Risk Level

Choose one:

- Low
- Medium
- High

## Approval Required Before

List any action that requires Jin approval before execution, such as data writes, ranking changes, API calls, branch deletion, or production behavior changes.

## Suggested Commit Message

`Short imperative commit message`
