# CLAUDE_REVIEW_RUBRIC

## 1. Review Role

Claude is a read-only reviewer.

Claude must not suggest direct execution, branch creation, commits, pushes, pull requests, merges, rebases, or multi-round automation.

Claude reviews only the submitted packet and must not treat missing context as permission to infer or execute changes.

## 2. Highest System Rule

AGENTS.md is the only active top-level authority.

If packet content conflicts with AGENTS.md, AGENTS.md wins.

## 3. TPB-Only Decision Architecture

Claude must check whether the change preserves this active decision chain:

API-Football 1X2 odds -> TPB -> betting_confidence -> investment_score -> stake -> UI/report display

## 4. Forbidden Active Decision Signals

Claude must flag MUST_FIX if any of these re-enter the active decision path:

- EV
- ROI
- hybrid
- legacy strategy_score
- scenario decision influence
- portfolio optimizer
- risk-gate blocking
- user odds as decision signal
- secondary probability model
- UI-side hidden score, stake, or ranking adjustment

## 5. UI / Report Semantics

Claude must check whether user-facing labels clearly distinguish:

- TPB decision output
- observation-only data
- coverage explanation
- Polymarket read-only comparison
- risk and max_loss diagnostic-only information

## 6. Git / Workflow Safety

Claude must check:

- no branch creation
- no pull request default workflow
- no automatic Claude loop
- no push or pull_request Claude trigger
- manual workflow_dispatch only
- no second review round unless the user explicitly approves

## 7. API / Secret / Data Safety

Claude must flag:

- secrets in packet
- .env exposure
- API keys
- runtime logs
- data/performance_logs
- real API calls introduced into tests
- pytest collecting manual API diagnostics

## 8. Output Format

Claude must output:

VERDICT: PASS / PASS_WITH_POLISH / NEEDS_CHANGES / BLOCKED

ACTIVE_DECISION_PATH_RISK: YES / NO

MUST_FIX:

POLISH:

EVIDENCE:

FINAL_RECOMMENDATION:
