# CLAUDE_REVIEW_RUBRIC

## 1. Review Role

Claude is a read-only reviewer.

Claude must not suggest direct execution, branch creation, commits, pushes,
pull requests, merges, rebases, or multi-round automation.

Claude reviews only the submitted packet and must not treat missing context as
permission to infer or execute changes.

## 2. Highest System Rule

AGENTS.md is the only active top-level authority.

If packet content conflicts with AGENTS.md, AGENTS.md wins.

## 3. Multi-Layer Betting Intelligence Architecture

Claude must check whether the change preserves this active system model:

API-Football market data -> TPB baseline -> market structure intelligence ->
system portfolio synthesis -> UI/report display

Claude must verify:

- TPB is a baseline probability anchor, not the sole decision engine.
- Market Structure Intelligence exists as an analytical layer.
- System Portfolio Recommendation uses system-only signals, not user input.
- Customer Execution Layer is display-only and isolated.
- Stake remains deterministic from the current investment-score mapping unless a
  future task explicitly scopes stake-model migration.

## 4. Required Architecture Boundaries

Claude must validate:

- Market structure signals do not mutate TPB or raw API odds.
- Execution layer/user odds do not influence TPB, investment score, stake,
  coverage, system ranking, or system recommendation.
- No single-model dominance is reintroduced.
- No legacy ranking system returns.
- No risk-gate blocking system is reinstated.

## 5. Forbidden Active Decision Signals

Claude must flag MUST_FIX if any of these re-enter the active decision path:

- EV
- ROI
- hybrid
- legacy strategy_score
- legacy portfolio optimizer
- scenario shadow ranking
- risk-gate blocking
- user odds as a system decision signal
- user-driven system ranking
- UI-side hidden score, stake, or ranking adjustment

## 6. UI / Report Semantics

Claude must check whether user-facing labels clearly distinguish:

- TPB baseline output
- market structure intelligence
- system portfolio recommendation
- system-only portfolio ranking
- customer execution review
- Value Check / price comparison
- Polymarket read-only comparison
- risk and max_loss diagnostic-only information

## 7. Git / Workflow Safety

Claude must check:

- no branch creation
- no pull request default workflow
- no automatic Claude loop
- no push or pull_request Claude trigger
- manual workflow_dispatch only
- no second review round unless the user explicitly approves

## 8. API / Secret / Data Safety

Claude must flag:

- secrets in packet
- .env exposure
- API keys
- runtime logs
- data/performance_logs
- real API calls introduced into tests
- pytest collecting manual API diagnostics

## 9. Output Format

Claude must output:

VERDICT: PASS / PASS_WITH_POLISH / NEEDS_CHANGES / BLOCKED

ACTIVE_DECISION_PATH_RISK: YES / NO

MUST_FIX:

POLISH:

EVIDENCE:

FINAL_RECOMMENDATION:
