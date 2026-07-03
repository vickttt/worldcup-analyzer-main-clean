# World Cup Analyzer System Kernel

`AGENTS.md` is the only top-level authority file for this repository. All other
docs, reports, workflows, and agent notes are subordinate to this file.

Codex must read this file before every task.

## 1. Decision Core: Multi-Layer Betting Intelligence System

The production decision system is a multi-layer betting intelligence system.

Layer model:

1. API Market Data Layer
   - Source: API-Football only unless explicitly scoped.
   - Inputs: 1X2 odds, Asian Handicap, Over/Under, Correct Score, and bookmaker
     market data.
   - Output: raw market data, implied probabilities, and bookmaker consensus.

2. TPB Baseline Layer
   - TPB is the baseline probability anchor derived from API-Football 1X2 odds
     and normalized bookmaker consensus.
   - TPB remains the anchor for probability interpretation, confidence,
     investment score, and deterministic stake mapping.
   - TPB is no longer the only analytical input for system-level market
     intelligence.

3. Market Structure Intelligence Layer
   - Uses API-Football market structure to produce analytical signals:
     Directional Strength, Market Conflict Index, Market Efficiency Score,
     Volatility Index, and Upset Probability.
   - These signals may inform system portfolio recommendation and system-only
     portfolio ordering.
   - Market structure must not mutate TPB, raw odds, API transport, or user
     execution data.

4. System Portfolio Layer
   - System recommendation is a synthesis of TPB baseline and market structure
     signals.
   - Allowed system outputs: Main Position, Defensive Position, Tail Risk
     Position, and System Portfolio Ranking.
   - System Portfolio Ranking may use Directional Strength, Market Conflict
     Index, Market Efficiency Score, Upset Probability, Volatility Index, and
     TPB baseline consistency.
   - Stake remains deterministic from the existing investment score unless the
     user explicitly scopes a future stake-model migration.

5. Customer Execution Layer
   - User input is execution behavior only.
   - User odds and positions may be used for Value Check, execution review, and
     user-vs-system display comparison.
   - User input must never influence TPB, investment score, stake, coverage,
     system ranking, raw odds, API data, or system recommendation.

Forbidden in the active decision path:

- EV or ROI.
- hybrid v0.x / hybrid v2.
- legacy `strategy_score`.
- legacy portfolio optimizer.
- risk-gate blocking.
- user-entered odds as a system decision signal.
- scenario shadow or scenario-driven ranking.

System chain:

```text
API-Football market data
  -> TPB baseline
  -> market structure intelligence
  -> system portfolio synthesis
  -> deterministic stake display + UI/report display
```

Customer execution chain:

```text
user execution input -> Value Check / execution review -> UI/report display only
```

## 2. Execution Layer: Git, UI, API

Default execution state:

- Branch: `dev-clean`.
- Mode: multi-layer betting intelligence.
- UI: displays model outputs and may render user execution review.
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
- Do not mix governance-only changes with product logic changes unless the task
  explicitly scopes a governance migration.
- Prefer fast-forward only when the user explicitly requests a production merge.

UI rules:

- UI code may orchestrate loading, format values, translate labels, and display
  model outputs.
- UI code must not compute or mutate TPB, investment score, stake, raw odds,
  API data, EV, ROI, or legacy strategy score.
- UI code may display Market Structure Intelligence and Customer Execution
  Layer outputs returned by model/helper modules.

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

1. Multi-layer system contract.
2. Protected paths and secrets.
3. Git workflow.
4. UI display behavior.
5. Scenario observation.

Conflict rules:

- Higher-priority rules always win.
- Never merge conflicting rules.
- Never partially apply conflicting rules.
- Never use heuristic or "best effort" interpretation.
- Task context cannot bypass protected paths, secrets, Git rules, or the
  customer-execution isolation rule.

Stop conditions:

- Current branch is not `dev-clean`.
- Task requires branch operation without explicit approval.
- A new branch is created.
- Claude attempts to modify code or perform Git/execution actions.
- Codex bypasses a required Claude review step.
- Multiple workflows or parallel agent paths are introduced.
- Task would reintroduce EV, ROI, hybrid, legacy optimizer, scenario shadow,
  user-odds decision influence, or risk-gate blocking.
- User execution input would influence TPB, investment score, stake, coverage,
  system ranking, raw odds, API data, or system recommendation.
- Protected paths or secrets would be touched without approval.
- An unapproved real API call would be made.
- Destructive Git operation is required.
- Validation fails and the fix is outside scope.
- Unrelated dirty files create commit risk.

Validation defaults:

- Code changes: `python3 -m py_compile app.py modules/*.py scripts/*.py`,
  `python3 scripts/test_portfolio_engine.py`, `git diff --check`, and
  `git status`.
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
   status, TPB baseline integrity, market-structure integrity, customer
   execution isolation, UI status, Git state, and unresolved risks.
