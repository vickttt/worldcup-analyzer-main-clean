# World Cup Analyzer Agent Protocol

This file is the top-level operating protocol for Codex and other AI agents working in this repository. Future task prompts may say: "Read AGENTS.md and continue the next UI-CACHE-API task under the project protocol."

## Project Identity

- Project: World Cup Analyzer.
- Purpose: football betting, market, portfolio, and refresh-safety analysis with auditable recommendations.
- Main development branch: `dev-clean`.
- Stable branch: `main-clean`.
- Current phase: `UI-CACHE-API`.
- Current keyed API target for refresh work: API-Football only.
- External odds providers are disabled; API-Football is the active odds provider.
- Polymarket is public-only and not part of current API refresh tasks unless explicitly scoped.
- WorldCup2026 schedule API is public and separate from keyed API-Football refresh work.

## Roles

- ChatGPT/Jin: product architecture, task approval, final merge/scope authority.
- Codex: development, validation, local execution, Git hygiene, and report generation.
- Claude: review-only safety reviewer through controlled packets; Claude must not write code or patches.
- GitHub: version record, branch backup, Actions-mediated Claude review artifacts.
- GitHub Desktop: optional human-facing commit, sync, and rollback surface.

## Required Reading

Before work starts, read:

1. `AGENTS.md`.
2. `docs/GPT_CONTEXT.md`.
3. `docs/PRODUCT_PRINCIPLES.md`.
4. `docs/TASK_QUEUE.md`.
5. `docs/KNOWN_BUGS.md`.
6. `docs/QA_REPORT.md`.
7. `docs/CHANGELOG.md`.

For current UI-CACHE-API work, also read:

- `docs/UI_CACHE_API_PROTOCOL.md`.
- `docs/API_REFRESH_SAFETY.md`.
- `docs/CODEX_CLAUDE_LOOP.md`.
- `docs/TASK_GRAPH.md`.

## Task Graph Dependency

`docs/TASK_GRAPH.md` is the required execution state machine for graph-governed work.

- The system cannot resolve `NEXT_NODE` without `docs/TASK_GRAPH.md`.
- Codex must stop if `docs/TASK_GRAPH.md` is missing, invalid, or inconsistent with Git history.
- `CURRENT_NODE` must come from `docs/TASK_GRAPH.md`.
- Claude may recommend the next node, but Claude must not edit `docs/TASK_GRAPH.md`.
- Codex owns task graph updates after a node is actually completed.
- Git history overrides task graph state when a mismatch exists; mismatch means `SYSTEM_HEALTH: DRIFT` and auto-advance is blocked.
- Jin is final authority for `NODE 5` and later real execution phases.

## Branch Rules

- Never directly modify `main-clean`.
- Every implementation task starts from clean, up-to-date `dev-clean`.
- Use a feature branch for each implementation or protocol task.
- Normal feature branch prefix: `codex/`.
- After validation and Claude review, consolidate completed branches into `dev-clean` with fast-forward if possible.
- Consolidation merges of already-reviewed branches do not require Claude unless a conflict, unexpected diff, failed validation, or scope uncertainty appears.
- Do not force push.
- Do not rewrite Git history.
- Do not delete files unless the user explicitly approves.

## Forbidden Paths And Areas

Unless the task explicitly scopes them and a human approves, do not modify:

- `main-clean`.
- `app.py` product behavior.
- `modules/ranking`.
- `modules/portfolio`.
- `modules/strategy`.
- `modules/backtest`.
- `data/`.
- `data/history/`.
- Golden JSON fixtures.
- Ranking logic.
- Portfolio logic.
- Strategy logic.
- Odds calculation or settlement logic.
- Backtest enablement.
- Recommendation outputs.
- `.env`, `.env.*`, `*.env`.
- `.streamlit/secrets.toml`.

Docs/protocol tasks must not modify product code, `app.py`, modules, data, or golden JSON.

## Risk Gates

These gates remain locked unless a future task explicitly satisfies and documents the unlock criteria:

- `PORTFOLIO_EXTRACTION: BLOCKED`.
- `BACKTEST_READY: NO`.

Claude and Codex must keep these gates blocked unless the supplied current-task evidence explicitly proves readiness.

## UI-CACHE-API Current Phase Route

Current route:

1. Data Freshness / Refresh Status panel.
2. Refresh status layer.
3. API-Football key readiness gate.
4. Controlled one-time API-Football refresh.
5. Dry-run refresh button.
6. Refresh log viewer.
7. Static metadata cache.
8. Streamlit loading optimization.

Known completed checkpoint:

- Task 5 completed on branch `codex/ui-cache-api-api-football-one-time-refresh`.
- Final head: `7f447bbad9e70caaf9b0779bf214e0f6f26f21cd`.
- It performed exactly one API-Football call: `GET /fixtures?id=1489393`.
- It wrote ignored runtime artifacts plus tracked reports/docs/scripts.
- It passed Claude Round 14 with verdict `PASS`.

Do not auto-proceed to any task that performs another real API call.

## API And Secret Policy

- Never print `.env`.
- Never print API key values.
- Only display key present/missing state.
- `.env` must be ignored.
- `.streamlit/secrets.toml` must be ignored if used.
- `.runtime/` must be ignored.
- API-Football is the only keyed API target in the current phase.
- `API_FOOTBALL_KEY` is required for live API-Football odds refresh for the current phase.
- API-Football is disabled for the current phase.
- Polymarket is public-only and not part of API refresh work unless explicitly scoped.
- A real API refresh must be one-time, bounded, logged, and explicitly approved.
- No repeated refresh loops.
- Runtime output goes to ignored paths unless explicitly approved.
- Tracked sample JSON must be stable and must not contain runtime timestamps or secrets.

See `docs/API_REFRESH_SAFETY.md` for the detailed refresh policy.

## Codex-Claude Review Loop

- Round 1 Claude review is required for normal development tasks.
- Up to 3 Claude review rounds total.
- Stop early if Claude returns `PASS` or no material findings.
- If Claude finds a material issue, Codex fixes only safe scoped items, validates, commits, pushes, and runs the next round.
- Do not continue beyond 3 rounds without human approval.
- Claude reviews only; Claude must not write code or patches.
- Use sanitized packets under `reports/claude_reviews/`.
- Run the packet budget guard before Claude review.
- Store Claude artifacts under `reports/claude_reviews/`.

## Report Consolidation Rule

After every Codex-Claude loop or graph-governed analysis cycle, Codex must run a report consolidation step.

The consolidation step must:

- update `reports/CONSOLIDATED_SYSTEM_ANALYSIS.md`.
- merge durable UI, MODEL, API, CACHE, OPS, risk, portfolio, and branch-governance findings into one structured summary.
- avoid duplicating the same finding across node reports.
- identify unresolved overlaps between UI, MODEL, and OPS domains.
- confirm whether the system is still in analysis/planning or has explicit approval to enter execution.

Claude must detect report fragmentation and include `REPORT_CONSOLIDATION_REQUIRED: YES/NO` in graph-governed review output.

If report fragmentation is detected, Codex must consolidate reports before continuing to another node.

## Decision Layer Control

`docs/DECISION_LAYER_CONTROL_SYSTEM.md` controls whether the system should continue analysis, consolidate, request execution readiness review, or remain execution-locked.

Decision Layer states:

- `ANALYSIS MODE`: read-only analysis is allowed.
- `CONSOLIDATION MODE`: only report consolidation and overlap reduction are allowed.
- `EXECUTION READY MODE`: exact action list may be prepared for Jin approval.
- `EXECUTION LOCKED MODE`: no execution, merge, branch archive, deletion, or product change is allowed.

If `SYSTEM_HEALTH` is `FRAGMENTED`, Codex must not start a new node, trigger Claude, merge branches, delete branches, or perform branch operations. Codex may only consolidate reports and update governance state.

If analysis output grows faster than execution readiness, Codex must stop and run Decision Layer review before adding more reports or proposing execution.

Claude is usually not required for:

- Pure local operations such as opening a page, checking a port, stopping Streamlit, or confirming localhost.
- Read-only checks that do not modify files, commit, or push.
- Fast-forward or safe merge into `dev-clean` after a branch already passed Claude.
- Tiny runtime/log cleanup where Claude cost exceeds benefit.
- Emergency cleanup to restore clean Git state, with later review if needed.

See `docs/CODEX_CLAUDE_LOOP.md` for the detailed loop.

## Autonomous Progression Rule

Within the current phase goal and forbidden boundaries, Codex may continue from one completed task to the next logical low-risk task recommended by Claude only when all conditions are met:

- Claude returns `PASS` or no material findings.
- Claude recommends exactly one next task.
- The next task is low-risk or medium-low-risk.
- The next task stays inside the current phase.
- No additional real API call is required.
- No secret value is exposed.
- No `data/history` or golden JSON mutation is required.
- No ranking, portfolio, strategy, odds, or backtest logic is touched.
- Git status is clean.
- Validation passes.
- Packet budget guard passes.

Stop for human checkpoint after:

- Maximum 3 autonomous tasks.
- Maximum 3 Claude review rounds.
- Any material risk.
- Conflict.
- Failed validation.
- Secret/API uncertainty.
- Scope expansion.
- Claude/Codex disagreement.

## Stop Conditions

Stop and ask for human approval if the task involves:

- A real API call without explicit approval.
- Secret or `.env` handling beyond presence check.
- `data/history` write.
- Golden JSON write.
- Ranking, portfolio, strategy, odds, or backtest logic.
- Portfolio extraction.
- Backtest enablement.
- Direct `main-clean` modification.
- Cross-phase move from `UI-CACHE-API` to `MODEL-UPGRADE`.
- Validation failure.
- Merge conflict.
- Unexpected dirty Git state.
- Any suspected secret exposure.

## Validation Checklist

General checks:

- Confirm current branch and `git status`.
- Confirm `dev-clean` sync before new branch work.
- Run `git diff --check`.
- Run `py_compile` for touched Python files.
- Run packet budget guard before Claude review.
- Run secret-shaped token scan on changed files.
- Run protected-path diff check.
- Confirm `.env` and `.runtime/` are ignored and not staged.

Task-specific checks:

- Dry-run churn test.
- Streamlit local smoke test at `http://localhost:8501` for UI tasks.
- API refresh gate report before any real API call.
- Confirm API call count.
- Confirm files written and whether tracked/ignored.
- Confirm `data/history` and golden JSON untouched.

## Checkpoint Summary Format

Every autonomous checkpoint or final response should include:

- Completed tasks.
- Branches.
- Commits.
- Claude verdicts.
- Files changed.
- Validations run.
- API calls performed.
- Secret safety.
- Protected paths.
- Unresolved risks.
- Recommended next task.
- Whether human approval is needed.
