# GPT Context

## Governance Notice

This file is contextual history only. `AGENTS.md` is the only active system
authority for repository execution rules.

Current active workflow:

- `dev-clean` is the only development branch.
- No automatic branch creation or branch switching.
- Codex is the only execution engine.
- Claude is read-only review only.
- The user is the final decision authority.

## Project

WorldCup Analyzer is a football betting and portfolio analysis project. The project currently needs stronger governance before additional feature work continues.

## Current Governance Goal

The immediate goal is to make the project controllable, auditable, reversible, and suitable for AI-assisted automation.

## Required Read Order For AI Agents

Before starting any development work, read:

1. `AGENTS.md`
2. `docs/PRODUCT_PRINCIPLES.md`
3. `docs/TASK_QUEUE.md`
4. `docs/KNOWN_BUGS.md`
5. `docs/CHANGELOG.md`
6. `docs/QA_REPORT.md`

## Current Git Baseline

- Current active branch model: `dev-clean` only.
- Historical baseline notes below this file must not override `AGENTS.md`.

## Development Rule

Follow `AGENTS.md`: all work happens on `dev-clean`; do not create backup or feature branches unless the user explicitly approves that branch operation.
