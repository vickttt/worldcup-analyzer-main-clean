# World Cup Analyzer System Kernel

`AGENTS.md` is the only top-level authority file for this repository. All other
docs, reports, workflows, and agent notes are subordinate to this file.

Codex must read this file before every task.

## 1. Decision Core: Multi-Layer Betting Intelligence System v1

The production decision system is fixed as Multi-Layer Betting Intelligence
System v1. It must not degrade into TPB-only, multi-model voting, EV trading, or
optimizer-based systems.

System Definition (IMPORTANT):

- The system does not predict match results.
- The system does not search for optimal odds.
- The system does not maximize profit or act as a yield optimizer.
- The system builds a probability market structure explanation system.
- The system builds scenario coverage space.
- The system outputs risk-coverage balance portfolios.
- Final positioning: Market Structure + Scenario Coverage + Probability Anchor
  System.

Philosophy:

- No prediction dominance.
- No EV/ROI dominance.
- No optimizer dominance.
- No hidden scoring authority.
- TPB = anchor only.
- Scenario = decomposition only.
- Market = signal only.

Odds philosophy:

- odds are not true probability.
- odds are market pricing with bookmaker bias.
- odds are noisy market signals.
- The system does not assume an external "true probability" exists. It infers
  market structure from quoted prices and bookmaker consensus.

EV / ROI boundary:

- EV and ROI are excluded because they depend on an assumed true probability.
- This system does not claim to know a true probability independent of market
  pricing.
- The system performs market structure inference, not value-betting
  optimization.

Optimizer boundary:

- Allowed: coverage optimization as explanation, scenario balancing, and risk
  exposure smoothing.
- Forbidden: EV optimizer, ROI optimizer, profit maximization engine, and
  black-box scoring system.

Layer model:

1. Layer 0: Market Data Layer
   - Source: API-Football only unless explicitly scoped.
   - Inputs: 1X2 odds, Asian Handicap, Over/Under, Correct Score, and bookmaker
     market data.
   - Output: raw market data, implied probabilities, and bookmaker consensus.
   - This layer provides data only and never makes decisions.

2. Layer 1: TPB Baseline Layer
   - TPB is the baseline probability anchor derived from API-Football 1X2 odds
     and normalized bookmaker consensus.
   - TPB is a probability normalization anchor and coordinate system.
   - TPB is not a predictive model and not a decision engine.
   - TPB is the only probability baseline anchor. It may not be replaced,
     overridden, or downgraded into an ordinary helper variable.
   - TPB anchors probability interpretation, confidence, investment score, and
     deterministic stake mapping.
   - TPB cannot be overridden by market structure, scenario thinking, user
     input, or any secondary model.
   - TPB does not participate in a ranking override; it supplies baseline
     strength to the system recommendation layer.

3. Layer 2: Market Structure Intelligence Layer
   - Uses API-Football market structure to produce analytical signals:
     Directional Strength, Market Conflict Index, Market Efficiency Score,
     Volatility Index, and Upset Probability.
   - This layer explains the market. It does not independently decide,
     override TPB, alter stake, mutate raw odds, or write user execution data.
   - These signals may be consumed by the System Portfolio Layer as explanatory
     system inputs.
   - Market Structure cannot directly generate final recommendation. It can
     influence System Ranking only through the synthesis layer.

4. Layer 3: Scenario Engine Layer
   - Scenario Engine v1 is the Market Scenario Coverage & Risk Decomposition
     Layer.
   - It uses only API-Football market data, TPB baseline, and Market Structure
     signals.
   - It decomposes probability space into exactly six fixed scenarios:
     S1 Strong Favorite Win, S2 Narrow Favorite Win, S3 Draw, S4 Upset Win,
     S5 Low Scoring Match, and S6 High Variance Match.
   - It may output Scenario Probability Distribution, Scenario Risk Surface,
     Scenario Coverage Map, Scenario Efficiency Score, Scenario-to-Market
     Mapping, and Scenario-to-Portfolio Mapping Explanation.
   - It is the explanatory backbone for System Portfolio coverage narrative.
   - Scenario Engine must not predict exact scores, calculate EV/ROI, optimize
     profit, override TPB, alter stake, influence system ranking, influence
     system recommendation, or use user input.

5. Layer 4: System Portfolio & Ranking Layer
   - The only legal system recommendation chain is:
     TPB baseline + Market Structure -> System Recommendation.
   - System recommendation is a synthesis of TPB baseline strength, market
     structure signals, and Scenario Engine coverage narrative.
   - Allowed system outputs: Main Position, Defensive Position, Tail Risk
     Position, and System Ranking.
   - System Ranking may use TPB baseline strength, Market Conflict Index,
     Directional Strength, Market Efficiency Score, Volatility Index, and Upset
     Probability.
   - System Ranking must not use user input, execution layer signals, EV, ROI,
     or legacy optimizer logic.
   - Stake remains deterministic from the existing investment score unless the
     user explicitly scopes a future stake-model migration.

6. Layer 5: Customer Execution Layer
   - User input is execution behavior only.
   - User odds and positions may be used for execution evaluation, Value Check,
     risk review, and user-vs-system display comparison.
   - Allowed execution classifications include Aligned, Partially Aligned,
     Hedged, Contrarian, and High Risk Exposure.
   - User input must never influence TPB, investment score, stake, coverage,
     system ranking, raw odds, API data, or system recommendation.

7. Model Methodology Transparency Layer
   - This layer explains calculation methods only. It never computes or mutates
     TPB, Market Structure, Scenario, Portfolio, Ranking, Stake, or Execution.
   - It must document Directional Strength, Market Conflict Index, Efficiency
     Score, Volatility Index, Scenario Probability Derivation, Scenario Mapping,
     Coverage Mapping, and Coverage Efficiency.
   - It must prevent black-box scoring, hidden ranking weights, implicit EV
     logic, and optimizer-style reasoning.

Scenario Thinking and Scenario Engine:

- Scenario Thinking is implemented through Scenario Engine v1 and is allowed
  only as probability-space decomposition, risk coverage, and explanation.
- Scenario taxonomy is fixed. Do not dynamically add scenario types.
- Scenario Engine must not enter ranking, override TPB, mutate market structure
  metrics, alter stake, or change system recommendation.

System positioning:

- This is not a pure prediction system and not an EV trading system.
- It is a Market Structure + Probability Anchor + Scenario Explanation System.
- One-line lock:
  TPB defines probability baseline; Market defines structure; Execution defines
  user behavior; System defines recommendation.

Forbidden in the active decision path:

- EV or ROI.
- hybrid v0.x / hybrid v2.
- legacy `strategy_score`.
- legacy portfolio optimizer.
- risk-gate blocking.
- user-entered odds as a system decision signal.
- user-driven ranking.
- scenario shadow or scenario-driven ranking.
- scenario-driven recommendation.
- multi-model voting.
- secondary probability model overriding TPB.

Forbidden ranking paths:

- user input ranking.
- execution layer ranking influence.
- EV ranking.
- ROI ranking.
- portfolio optimizer ranking.

Decision Authority Hierarchy:

1. TPB Baseline Probability (anchor).
2. Market Structure Intelligence (signal layer).
3. Scenario Engine Layer (probability space decomposition and portfolio
   explanation backbone only).
4. System Portfolio Layer (synthesis + ranking).
5. Execution Layer (display/evaluation only).
6. Method Layer (calculation transparency only).

Authority rules:

- TPB cannot be overridden.
- Market Structure cannot override TPB.
- Scenario Engine cannot become a decision engine.
- System Portfolio must be synthesis-based.
- Execution Layer cannot affect any upstream layer.

Allowed report structure:

1. Core Decision Layer: TPB, betting confidence, investment score, and stake.
2. Market Structure Layer: Directional Strength, Conflict Index, Efficiency
   Score, Volatility Index, and Upset Probability.
3. Scenario Engine Layer: scenario probability distribution, risk surface,
   coverage map, scenario-market mapping, scenario-portfolio mapping, and
   coverage efficiency.
4. System Portfolio Layer: main, defensive, and tail positions.
5. System Ranking: system-only ranking.
6. Execution Layer: user portfolio, odds comparison, and evaluation only.
7. Model Explanation Layer: calculation methods, thresholds, scenario
   derivation, coverage logic, and audit guards.

System chain:

```text
API-Football market data
  -> TPB baseline anchor
  -> market structure signal layer
  -> scenario coverage and risk decomposition
  -> system-only recommendation synthesis
  -> methodology transparency
  -> deterministic stake display + UI/report display
```

Customer execution chain:

```text
user execution input -> Value Check / execution evaluation -> UI/report display only
```

System invariants:

- TPB cannot be overridden.
- Market Structure cannot become an optimizer.
- Scenario Engine cannot become an optimizer, EV model, or ranking engine.
- Execution Layer cannot become ranking input.
- Scenario Thinking cannot become a decision engine.
- No layer may become an EV/ROI system.
- No hidden scoring weights, black-box transformations, or optimizer-style
  reasoning are allowed.

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
