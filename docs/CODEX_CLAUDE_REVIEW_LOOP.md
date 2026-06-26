# Codex Claude Review Loop

Date: 2026-06-27

## Purpose

This protocol lets Codex perform scoped implementation work while Claude reviews controlled diffs or reports. Claude is a reviewer only. Codex remains the implementation agent.

## Five-Round Loop

## Round 1

- Codex performs a small scoped task.
- Codex runs validation.
- Codex generates a controlled diff or report.
- Claude reviews the supplied material.
- Claude outputs one recommended next Codex task.

## Round 2

- Codex implements only the recommended task if it is safe and scoped.
- Codex runs validation.
- Claude reviews again.

## Round 3

- Repeat the same review-gated workflow.
- Keep tasks small, reversible, and documented.

## Round 4

- Repeat the same review-gated workflow.
- Stop if Claude recommends unsafe scope expansion or touches forbidden files.

## Round 5

- Codex creates a final consolidation summary.
- Jin decides whether to commit, open a PR, or merge.

## Rules

- Claude never edits files.
- Claude never writes code.
- Claude never applies patches.
- Codex never blindly follows unsafe Claude suggestions.
- Jin approves before PR merge.
- No product logic changes unless explicitly scoped.
- No secrets are sent to Claude, GitHub, reports, or docs.
- Do not send full history snapshots unless explicitly approved.
- Portfolio extraction remains blocked until the required gates are satisfied.
- Backtest enablement remains disabled until the required gates are satisfied.

## Allowed Review Inputs

- Current working diff with protected paths excluded.
- Last commit diff with protected paths excluded.
- A selected PR diff.
- A selected short report or test input file.

## Default Exclusions

- `data/**`
- `reports/golden_output_snapshot_v1.json`
- `reports/golden_output_snapshot_v2.json`
- `reports/golden_risk_contract_v1.json`
- `.env`
- `.env.*`
- `*.env`

## Operator Checklist

- Confirm local secret files are ignored.
- Confirm the Claude smoke test is ready.
- Run the review script in the selected mode.
- Review the generated Markdown and metadata.
- Execute only safe, scoped next tasks.
