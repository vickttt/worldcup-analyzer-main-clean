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

## 3. Multi-Layer Betting Intelligence Architecture v2

Claude must check whether the change preserves this active system model:

API-Football market data -> TPB baseline anchor -> market structure signal layer
-> scenario-weighted coverage and risk decomposition -> system-only bounded recommendation synthesis
-> UI/report display

Claude must verify:

- The system is framed as Market Structure + Scenario-Weighted Bounded
  Optimization + Probability Anchor System, not a prediction model,
  optimal-odds finder, EV/ROI system, ML system, or profit maximization engine.
- TPB is not the sole system anymore, but it is still the single probability
  baseline anchor.
- TPB is a probability normalization anchor / coordinate system, not a
  predictive model or decision engine.
- odds are treated as biased and noisy market pricing, not true probability.
- TPB is not overridden, replaced, downgraded, or mutated by market structure,
  scenario thinking, user input, or secondary models.
- Market Structure Intelligence exists as a signal layer that explains market
  structure and does not directly generate final recommendation.
- Market Structure Intelligence does not override TPB, independently decide, or
  alter stake.
- Scenario Engine v2 exists as a bounded scenario-weighted coverage and risk
  decomposition layer.
- Scenario Engine uses the fixed six-scenario taxonomy only: S1 Strong Favorite
  Win, S2 Narrow Favorite Win, S3 Draw, S4 Upset Win, S5 Low Scoring Match, and
  S6 High Variance Match.
- Scenario Engine does not predict exact scores, calculate EV/ROI, optimize
  profit, run ML training, use black-box optimization, override TPB, alter
  stake, or use user input.
- Scenario weights are normalized, explainable, deterministic, and bounded.
- Scenario Engine may influence System Portfolio and System Ranking only
  through bounded Scenario Weights.
- Scenario Engine is integrated into the System Portfolio flow as the bounded
  scenario-weighted coverage backbone.
- Scenario Engine is not an isolated UI module.
- System Recommendation is based only on TPB baseline plus market structure
  signals plus bounded Scenario Weights.
- System Portfolio is synthesis-based and owns final system recommendation and
  system-only ranking.
- Model Methodology Transparency Layer exists and explains Market Structure,
  Scenario, Coverage, and Ranking basis without computing model outputs.
- A unified FINAL DECISION SUMMARY / FINAL DECISION BLOCK exists as the single
  decision-entry view for TPB, Market, Scenario, Portfolio, and Ranking.
- Customer Execution Layer is display-only/evaluation-only and isolated.
- Stake remains deterministic from the current investment-score mapping unless a
  future task explicitly scopes stake-model migration.
- The system does not degrade into TPB-only, multi-model voting, EV trading,
  ROI trading, profit maximization, ML training, or black-box optimizer behavior.

## 4. Required Architecture Boundaries

Claude must validate:

- Market structure signals do not mutate TPB or raw API odds.
- Execution layer/user odds do not influence TPB, investment score, stake,
  coverage, system ranking, or system recommendation.
- System Ranking uses only TPB baseline strength, Market Conflict Index,
  Directional Strength, Market Efficiency Score, Volatility Index, Upset
  Probability, and normalized Scenario Weights.
- Execution Layer does not affect any upstream layer.
- Scenario Thinking is bounded and can influence system-only ranking through
  explainable Scenario Weights; it still does not override TPB, mutate stake, or
  use user input.
- Scenario Coverage Map and Coverage Efficiency v2 are bounded coverage
  diagnostics used for portfolio synthesis, not EV/ROI/profit scores.
- Scenario-to-Portfolio Mapping Explanation is present and explains Main,
  Defensive, and Tail coverage with traceable scenario weights.
- System Portfolio explicitly references scenario coverage.
- Market Structure metrics are explainable.
- Scenario Engine calculation transparency exists.
- No hidden scoring weights exist.
- No EV-like transformation is hidden in Scenario Engine.
- No EV/ROI/profit optimizer or ML logic is embedded in Coverage Engine.
- EV/ROI reasoning is not used as an explanation shortcut.
- Coverage optimization, scenario balancing, and risk exposure smoothing remain
  bounded heuristic coverage logic and do not become profit optimization.
- UI/report output does not remain fragmented in a way that creates competing
  decision-entry views.
- Execution Layer is separate from the final decision block.
- No hidden ranking contamination exists from user input or execution-layer
  fields.
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
- unbounded scenario-driven recommendation
- risk-gate blocking
- user odds as a system decision signal
- user-driven system ranking
- execution layer ranking influence
- multi-model voting
- secondary probability model overriding TPB
- ML training or learned scenario weights
- black-box coverage optimizer
- UI-side hidden score, stake, or ranking adjustment

## 6. UI / Report Semantics

Claude must check whether user-facing labels clearly distinguish:

- TPB baseline output
- market structure intelligence
- system portfolio recommendation
- system-only portfolio ranking
- customer execution review
- Value Check / price comparison
- scenario thinking as bounded scenario-weighted coverage logic
- scenario probability distribution, risk surface, coverage map, and coverage
  efficiency as bounded analysis inputs
- Scenario Optimization Layer v2 with scenario weights, coverage mapping,
  optimized portfolio selection, risk distribution surface, and Coverage
  Efficiency Score v2
- scenario-to-portfolio mapping as portfolio explanation narrative
- model methodology transparency as explanation-only
- unified final decision summary as the only decision-entry view
- Polymarket read-only comparison
- risk and max_loss diagnostic-only information

## 7. Git / Workflow Safety

Claude must check:

- no branch creation
- no pull request default workflow
- no automatic Claude loop
- no push or pull_request Claude trigger
- workflow_dispatch review only when explicitly authorized for that run
- no second review round unless the user explicitly approves
- the review is tied to a specific commit range or sanitized packet
- Codex did not treat CI as a substitute for Claude Review
- Codex did not mark a committed task complete before Claude returned a verdict
- no merge, production-ready declaration, or next-task continuation occurs while
  review state is PENDING_REVIEW, IN_REVIEW, or NEEDS_CHANGES

## 8. Decoupled Review Request System

Claude Review is a required architecture validation state after every Codex
commit, but it is not assumed to run automatically.

Claude must validate:

- Codex marked committed work as `REVIEW REQUIRED` / `PENDING_REVIEW`.
- The review request was explicitly triggered or explicitly reported as pending.
- Review was not assumed automatically from commit creation, CI success, or push
  completion.
- Claude Review remains read-only.
- The review uses an approved path: commit_range, packet_path, manual
  workflow_dispatch, or explicitly authorized workflow_dispatch Claude API
  review.
- The review is tied to a concrete commit_range or sanitized packet.
- No old multi-round auto-loop is assumed in the system design.
- Ordinary CI is present only as syntax, import, unit-test, smoke-test, command
  validation, or sanitized packet artifact generation.
- Workflow-based Claude API review, if used, was explicitly authorized and used
  only the sanitized packet as model input.
- CI is not used as a replacement for architecture review.
- Low-risk, governance-only, or documentation-only commits are not exempt from
  Claude Review.
- Commit does not equal completed task.
- Only APPROVED review state means the committed task is complete.
- If Claude Review cannot run or cannot return a verdict, review state remains
  PENDING_REVIEW or NEEDS_CHANGES.

Review State Machine:

- PENDING_REVIEW: review requested but not started.
- IN_REVIEW: review running or waiting for verdict.
- APPROVED: Claude returned PASS or PASS_WITH_POLISH without a blocking fix.
- NEEDS_CHANGES: Claude returned NEEDS_CHANGES/BLOCKED, failed, or identified a
  required fix.

CI vs Claude Review boundary:

- CI checks syntax, imports, tests, and basic execution correctness.
- Claude checks architecture integrity, TPB baseline boundaries, market
  structure boundaries, Scenario Engine isolation, EV/ROI violations, ranking
  contamination, execution-layer isolation, API/data safety, and governance
  compliance.
- Both are mandatory after a commit. Neither replaces the other. Review remains
  an independent request state, not an automatic commit hook.

## 9. API / Secret / Data Safety

Claude must flag:

- secrets in packet
- .env exposure
- API keys
- runtime logs
- data/performance_logs
- real API calls introduced into tests
- pytest collecting manual API diagnostics
- CI or smoke tests depending on TPB-only assumptions
- legacy ranking imports or optimizer imports in active core paths

## 10. Output Format

Claude must output:

VERDICT: PASS / PASS_WITH_POLISH / NEEDS_CHANGES / BLOCKED

ACTIVE_DECISION_PATH_RISK: YES / NO

REVIEW_STATE: PENDING_REVIEW / IN_REVIEW / APPROVED / NEEDS_CHANGES

MUST_FIX:

POLISH:

EVIDENCE:

FINAL_RECOMMENDATION:
