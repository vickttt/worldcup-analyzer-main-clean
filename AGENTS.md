# World Cup Analyzer System Kernel

`AGENTS.md` is the only top-level authority file for this repository. All other
docs, reports, workflows, and agent notes are subordinate to this file.

Codex must read this file before every task.

## 1. Decision Core: TPB System

The production decision system is TPB-only.

- TPB is the sole probability source, derived from API-Football 1X2 odds and
  normalized bookmaker consensus.
- `betting_confidence` derives from TPB entropy only.
- `investment_score` derives from TPB plus bookmaker dispersion only.
- `stake` is deterministic from `investment_score` only.
- Coverage is TPB-driven through draw probability, upset probability, and
  favorite-gap thresholds. Handicap data is secondary display only.
- Risk is diagnostic only. It must not block ranking, stake, or recommendation.
- `max_loss = null` means not calculated; `0` means no position; `>0` means
  real exposure.
- `scenario_engine` is observation-only. It may display distributions and
  explanations, but must not influence TPB, score, stake, ranking, coverage,
  risk, or recommendations.

Forbidden in the active decision path:

- EV or ROI.
- hybrid v0.x / hybrid v2.
- legacy `strategy_score`.
- scenario decision influence.
- portfolio optimizer influence.
- risk-gate blocking.
- user-entered odds as a decision signal.
- any secondary probability model.

Decision chain:

```text
API-Football 1X2 odds -> TPB -> betting_confidence -> investment_score -> stake -> UI display
```

## 2. Execution Layer: Git, UI, API

Default execution state:

- Branch: `dev-clean`.
- Mode: TPB-only.
- UI: display-only.
- Scenario: observation-only.
- Loop: Codex executes, Claude reviews read-only, user decides.
- Git: no branch operation unless explicitly requested.

Branch and Git rules:

- Codex must stop if the current branch is not `dev-clean`.
- All work happens directly on `dev-clean`.
- No feature branches and no automatic branch creation or branch switching.
- Branch creation, branch switching, merge, rebase, cherry-pick, push, force
  push, tag creation, branch deletion, history rewrite, stash deletion, and
  destructive cleanup require explicit user approval.
- Commits may include only files scoped by the task.
- Do not mix governance-only changes with product logic changes.
- Prefer fast-forward only when the user explicitly requests a production merge.

UI rules:

- UI code may orchestrate loading, format values, translate labels, and display
  model outputs.
- UI code must not compute or adjust TPB, confidence, investment score, stake,
  ranking, coverage, risk, EV, ROI, or strategy score.

API and secret rules:

- Never print or commit API keys, tokens, `.env` values, or secrets.
- API-Football is the only keyed API provider unless explicitly scoped.
- Real API calls require explicit approval unless the task names the exact
  bounded call.
- No broad refresh loops, all-date pulls, all-league pulls, or repeated API
  refresh loops.
- Runtime outputs must stay ignored unless explicitly approved.

Protected paths and areas:

- `data/`
- `data/history/`
- `data/performance_logs/`
- golden JSON fixtures
- `.env`, `.env.*`, `*.env`
- `.streamlit/secrets.toml`
- generated runtime/cache/log artifacts
- `main-clean`
- branch history
- TPB formulas, API transport, odds settlement, betting strategy, backtest
  behavior, and ranking behavior unless explicitly scoped.

Codex-Claude loop:

1. User assigns task.
2. Codex executes on `dev-clean`, makes scoped changes, validates, and commits
   locally when requested.
3. Codex syncs to GitHub only when required and explicitly allowed.
4. Claude reviews the diff or changed files as a passive audit layer.
5. Codex applies approved review fixes on `dev-clean`, validates, and commits.
6. Codex reports changes, Claude findings, fixes, and final status to the user.

Role boundaries:

- Codex is the only execution engine. It may edit files, run scripts, validate,
  commit, and apply Claude feedback within task scope.
- Claude is read-only. It may review code, logic, risks, and architecture. It
  must not edit files, run commands, create branches, commit, push, merge, or
  trigger automation.
- The user is the final decision authority.
- No additional agents, branches, or parallel workflows are allowed.

## 3. Safety And Conflict Resolution

Rule priority, highest to lowest:

1. TPB System.
2. Protected paths and secrets.
3. Git workflow.
4. UI display-only behavior.
5. Scenario observation.

Conflict rules:

- Higher-priority rules always win.
- Never merge conflicting rules.
- Never partially apply conflicting rules.
- Never use heuristic or "best effort" interpretation.
- Task context cannot bypass TPB, protected paths, or Git rules.
- Any TPB conflict requires immediate stop and report.

Stop conditions:

- Current branch is not `dev-clean`.
- Task requires branch operation without explicit approval.
- A new branch is created.
- Claude attempts to modify code or perform Git/execution actions.
- Codex bypasses a required Claude review step.
- Multiple workflows or parallel agent paths are introduced.
- Task would reintroduce EV, ROI, hybrid, scenario, portfolio, user odds, or
  risk-gate decision influence.
- UI would compute or alter model outputs.
- Protected paths or secrets would be touched without approval.
- An unapproved real API call would be made.
- Destructive Git operation is required.
- Validation fails and the fix is outside scope.
- Unrelated dirty files create commit risk.

Validation defaults:

- Code changes: `python3 -m py_compile app.py modules/*.py scripts/test_portfolio_engine.py`,
  `git diff --check`, and `git status`.
- Governance-only changes: confirm only governance files changed, run
  `git diff --check`, and confirm `git status`.
- UI changes: compile validation plus browser verification only when requested
  or required by the task.

## Codex Execution Loop

1. Check branch is `dev-clean`.
2. Read `AGENTS.md`.
3. Validate task scope, allowed files, forbidden files, and approvals.
4. Execute only allowed operations on `dev-clean`.
5. Run local validation.
6. Use Claude as read-only review when required by task scope.
7. Apply scoped fixes if needed.
8. Report files changed, validations, Claude findings, fixes, protected-path
   status, TPB integrity, scenario isolation, UI display-only status, Git state,
   and unresolved risks.
