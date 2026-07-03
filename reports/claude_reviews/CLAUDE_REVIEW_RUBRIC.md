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

## 3. Multi-Layer Betting Intelligence Architecture v1

Claude must check whether the change preserves this active system model:

API-Football market data -> TPB baseline anchor -> market structure signal layer
-> scenario coverage and risk decomposition -> system-only recommendation synthesis
-> UI/report display

Claude must verify:

- The system is framed as Market Structure + Scenario Coverage + Probability
  Anchor System, not a prediction model, optimal-odds finder, or profit
  maximization engine.
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
- Scenario Engine v1 exists only as Market Scenario Coverage & Risk
  Decomposition Layer.
- Scenario Engine uses the fixed six-scenario taxonomy only: S1 Strong Favorite
  Win, S2 Narrow Favorite Win, S3 Draw, S4 Upset Win, S5 Low Scoring Match, and
  S6 High Variance Match.
- Scenario Engine does not predict exact scores, calculate EV/ROI, optimize
  profit, influence ranking, influence recommendation, or use user input.
- Scenario Engine is integrated into the System Portfolio explanation flow as
  the portfolio coverage narrative backbone.
- Scenario Engine is not an isolated UI module.
- System Recommendation is based only on TPB baseline plus market structure
  signals plus Scenario Engine coverage narrative.
- System Portfolio is synthesis-based and owns final system recommendation and
  system-only ranking.
- Model Methodology Transparency Layer exists and explains Market Structure,
  Scenario, Coverage, and Ranking basis without computing model outputs.
- A unified FINAL DECISION SUMMARY / FINAL DECISION BLOCK exists as the single
  decision-entry view for TPB, Market, Scenario, Portfolio, and Ranking.
- Customer Execution Layer is display-only/evaluation-only and isolated.
- Stake remains deterministic from the current investment-score mapping unless a
  future task explicitly scopes stake-model migration.
- The system does not degrade into TPB-only, multi-model voting, EV trading, or
  optimizer-based behavior.

## 4. Required Architecture Boundaries

Claude must validate:

- Market structure signals do not mutate TPB or raw API odds.
- Execution layer/user odds do not influence TPB, investment score, stake,
  coverage, system ranking, or system recommendation.
- System Ranking uses only TPB baseline strength, Market Conflict Index,
  Directional Strength, Market Efficiency Score, Volatility Index, and Upset
  Probability.
- Execution Layer does not affect any upstream layer.
- Scenario Thinking is explanation-only and does not enter ranking, TPB, stake,
  or system recommendation.
- Scenario Coverage Map and Scenario Efficiency Score are coverage diagnostics
  only, not recommendation scores.
- Scenario-to-Portfolio Mapping Explanation is present and explains Main,
  Defensive, and Tail coverage without driving ranking.
- System Portfolio explicitly references scenario coverage.
- Market Structure metrics are explainable.
- Scenario Engine calculation transparency exists.
- No hidden scoring weights exist.
- No EV-like transformation is hidden in Scenario Engine.
- No optimizer logic is embedded in Coverage Engine.
- EV/ROI reasoning is not used as an explanation shortcut.
- Coverage optimization, scenario balancing, and risk exposure smoothing are
  explanation-only and do not become profit optimization.
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
- scenario-driven recommendation
- risk-gate blocking
- user odds as a system decision signal
- user-driven system ranking
- execution layer ranking influence
- multi-model voting
- secondary probability model overriding TPB
- UI-side hidden score, stake, or ranking adjustment

## 6. UI / Report Semantics

Claude must check whether user-facing labels clearly distinguish:

- TPB baseline output
- market structure intelligence
- system portfolio recommendation
- system-only portfolio ranking
- customer execution review
- Value Check / price comparison
- scenario thinking as explanation-only
- scenario probability distribution, risk surface, coverage map, and coverage
  efficiency as analysis-only
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
- CI or smoke tests depending on TPB-only assumptions
- legacy ranking imports or optimizer imports in active core paths

## 9. Output Format

Claude must output:

VERDICT: PASS / PASS_WITH_POLISH / NEEDS_CHANGES / BLOCKED

ACTIVE_DECISION_PATH_RISK: YES / NO

MUST_FIX:

POLISH:

EVIDENCE:

FINAL_RECOMMENDATION:
