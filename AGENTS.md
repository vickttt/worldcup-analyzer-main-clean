# World Cup Analyzer System Kernel

`AGENTS.md` is the only top-level authority file for this repository. All other
docs, reports, workflows, and agent notes are subordinate to this file.

Codex must read this file before every task.

## 1. Decision Core: Multi-Layer Betting Intelligence System v2

The production decision system is fixed as Multi-Layer Betting Intelligence
System v2. It is a bounded scenario-weighted optimization system. It must not
degrade into TPB-only, multi-model voting, EV trading, ROI trading, profit
maximization, ML training, or black-box optimizer systems.

System Definition (IMPORTANT):

- The system does not predict match results.
- The system does not search for optimal odds.
- The system does not maximize profit or act as a yield optimizer.
- The system builds a probability market structure inference system.
- The system builds scenario coverage and scenario-weighted synthesis space.
- The system outputs bounded risk-coverage balance portfolios.
- Final positioning: Market Structure + Scenario-Weighted Bounded Optimization
  + Probability Anchor System.
- Final UI positioning: One Decision View System.

Philosophy:

- No prediction dominance.
- No EV/ROI dominance.
- No profit optimizer dominance.
- No hidden scoring authority.
- TPB = anchor only.
- Scenario = bounded weighted signal only.
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

- Allowed: bounded heuristic coverage optimization, scenario weighting,
  scenario balancing, and risk exposure smoothing.
- Allowed optimization must maximize scenario coverage, probability alignment,
  and risk balance while minimizing tail exposure, conflict exposure, and
  redundancy.
- Forbidden: EV optimizer, ROI optimizer, profit maximization engine, ML
  training system, and black-box scoring system.

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
   - Scenario Engine v2 is the Scenario-Weighted Coverage & Risk Decomposition
     Layer.
   - It uses only API-Football market data, TPB baseline, and Market Structure
     signals.
   - It decomposes probability space into exactly six fixed scenarios:
     S1 Strong Favorite Win, S2 Narrow Favorite Win, S3 Draw, S4 Upset Win,
     S5 Low Scoring Match, and S6 High Variance Match.
   - It may output Scenario Probability Distribution, Scenario Risk Surface,
     Scenario Coverage Map, Scenario Efficiency Score, Scenario-to-Market
     Mapping, Scenario-to-Portfolio Mapping Explanation, and normalized
     Scenario Weights.
   - It is the bounded weighted signal backbone for System Portfolio coverage
     narrative and ranking synthesis.
   - Scenario Engine may influence System Portfolio Layer and System Ranking
     only through explainable, deterministic, bounded heuristic scenario
     weights.
   - Scenario Engine must not predict exact scores, calculate EV/ROI, optimize
     profit, perform ML training, use black-box optimization, override TPB,
     alter stake, mutate raw odds, or use user input.

5. Layer 4: System Portfolio & Ranking Layer
   - The only legal system recommendation chain is:
     TPB baseline + Market Structure + bounded Scenario Weights -> System
     Recommendation.
   - System recommendation is a synthesis of TPB baseline strength, market
     structure signals, and bounded Scenario Engine coverage weights.
   - Allowed system outputs: Main Position, Defensive Position, Tail Risk
     Position, and System Ranking.
   - System Ranking may use TPB baseline strength, Market Conflict Index,
     Directional Strength, Market Efficiency Score, Volatility Index, and Upset
     Probability, plus normalized Scenario Weights.
   - System Ranking must not use user input, execution layer signals, EV, ROI,
     profit optimization, ML training, black-box optimization, or legacy
     optimizer logic.
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
     logic, and EV/ROI/profit optimizer reasoning.

Scenario Thinking and Scenario Engine:

- Scenario Thinking is implemented through Scenario Engine v2 and is allowed as
  probability-space decomposition, bounded scenario weighting, risk coverage,
  and coverage optimization.
- Scenario taxonomy is fixed. Do not dynamically add scenario types.
- Scenario Engine may influence System Ranking and System Portfolio only through
  bounded, deterministic, explainable Scenario Weights.
- Scenario Engine must not override TPB, mutate market structure metrics, alter
  stake, use user input, calculate EV/ROI, maximize profit, or become a
  black-box optimizer.

Bounded Influence Rule:

- Scenario Engine cannot override TPB.
- Scenario Engine cannot act as an EV/ROI/profit optimizer.
- Scenario Engine can only provide weighted scenario signals to the System
  Portfolio Layer.
- Scenario influence must be explainable, deterministic, bounded, and
  heuristic.
- Scenario influence must be traceable to TPB baseline, Market Structure
  signals, Volatility Index, and Upset Probability.
- Scenario influence must not depend on user input, user odds, historical
  returns, profit targets, or black-box learned weights.

Scenario Weighting Permission:

- Normalized scenario weights may influence System Ranking under bounded
  constraints.
- Normalized scenario weights may influence System Portfolio construction under
  bounded constraints.
- Normalized scenario weights may influence coverage optimization under bounded
  constraints.
- Scenario weights must not create EV optimization, ROI optimization, profit
  maximization, ML training behavior, or hidden scoring authority.

System positioning:

- This is not a pure prediction system and not an EV trading system.
- It is a Market Structure + Probability Anchor + Scenario-Weighted Bounded
  Optimization System.
- One-line lock:
  TPB defines probability baseline; Market defines structure; Scenario defines
  bounded weights; Execution defines user behavior; System defines
  recommendation.

Forbidden in the active decision path:

- EV or ROI.
- hybrid v0.x / hybrid v2.
- legacy `strategy_score`.
- legacy portfolio optimizer.
- risk-gate blocking.
- user-entered odds as a system decision signal.
- user-driven ranking.
- scenario shadow.
- unbounded scenario-driven ranking or recommendation.
- multi-model voting.
- secondary probability model overriding TPB.

Forbidden ranking paths:

- user input ranking.
- execution layer ranking influence.
- EV ranking.
- ROI ranking.
- profit optimizer ranking.
- black-box optimizer ranking.
- user-driven scenario ranking override.

Decision Authority Hierarchy:

1. TPB Baseline Probability (anchor).
2. Market Structure Intelligence (signal layer).
3. Scenario Engine Layer (probability space decomposition and bounded scenario
   weighting).
4. System Portfolio Layer (synthesis + ranking).
5. Execution Layer (display/evaluation only).
6. Method Layer (calculation transparency only).

Authority rules:

- TPB cannot be overridden.
- Market Structure cannot override TPB.
- Scenario Engine cannot override TPB or become an EV/ROI/profit optimizer.
- Scenario Engine may influence System Portfolio and Ranking only through
  bounded, deterministic, explainable Scenario Weights.
- System Portfolio must be synthesis-based.
- Execution Layer cannot affect any upstream layer.

Decision Flow Lock Rule:

- The system must follow this interpretation order:
  TPB -> Market -> Scenario -> Portfolio -> Ranking -> Execution.
- UI/report output must converge TPB, Market, Scenario, Portfolio, and Ranking
  into one unified decision block.
- Execution remains a separate layer and must not appear inside the final
  decision block.
- The final decision block is the only decision-entry view. It is a summary of
  existing model outputs, not a new model and not a new calculation layer.

Allowed report structure:

0. FINAL DECISION BLOCK: TPB Summary, Market Structure Summary, Scenario
   Summary, Portfolio Recommendation, and System Ranking.
1. Core Decision Layer: TPB, betting confidence, investment score, and stake.
2. Market Structure Layer: Directional Strength, Conflict Index, Efficiency
   Score, Volatility Index, and Upset Probability.
3. Scenario Engine Layer: scenario probability distribution, risk surface,
   coverage map, scenario-market mapping, scenario-portfolio mapping, and
   coverage efficiency.
3a. Scenario Optimization Layer v2: normalized scenario weights, bounded
   coverage optimization objective, scenario-to-leg coverage contribution,
   scenario dependency, risk exposure, redundancy, and Coverage Efficiency v2.
4. System Portfolio Layer: main, defensive, and tail positions.
5. System Ranking: scenario-weighted system-only ranking.
6. Execution Layer: user portfolio, odds comparison, and evaluation only.
7. Model Explanation Layer: calculation methods, thresholds, scenario
   derivation, coverage logic, and audit guards.

System chain:

```text
API-Football market data
  -> TPB baseline anchor
  -> market structure signal layer
  -> scenario-weighted coverage and risk decomposition
  -> system-only bounded recommendation synthesis
  -> methodology transparency
  -> deterministic stake display + UI/report display
```

Customer execution chain:

```text
user execution input -> Value Check / execution evaluation -> UI/report display only
```

System invariants:

- TPB cannot be overridden.
- Market Structure cannot become an EV/ROI/profit optimizer.
- Scenario Engine cannot become an EV model, ROI model, profit optimizer, ML
  training system, or black-box optimizer.
- Scenario Engine can influence System Ranking only through bounded,
  deterministic, explainable Scenario Weights.
- Execution Layer cannot become ranking input.
- Scenario Thinking cannot become an unbounded decision engine.
- No layer may become an EV/ROI system.
- No hidden scoring weights, black-box transformations, EV/ROI/profit optimizer
  reasoning, or ML training behavior are allowed.
- Not multiple systems: one unified decision flow, one interpretation layer, and
  one separate execution layer.

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
2. Codex executes on `dev-clean` with scoped changes only.
3. Codex runs required local validation.
4. Codex commits changes when the task requires or authorizes a commit.
5. Codex marks `REVIEW REQUIRED` after every commit.
6. Codex may stop at Local Complete with Review Pending if the user has not
   requested remote sync or review execution.
7. Codex pushes only when explicitly allowed by the user.
8. Claude Review may be requested as an independent step. GitHub Actions may
   only prepare/upload sanitized review packet artifacts; it must not call any
   external AI API.
9. Claude performs read-only review manually/chat-based from the artifact or
   packet content and returns a verdict.
10. Codex applies approved review fixes if needed on `dev-clean`, validates, and
   commits the fix.
11. Every fix commit returns to `REVIEW REQUIRED`.
12. Codex reports local completion, review state, remote sync state, and any
    unresolved risks. Production-ready status requires APPROVED review.

Git / Review State Machine:

- `LOCAL_COMPLETE`: commit complete, required local validation complete, and
  working tree clean. This is a valid stopping state for local development.
- `PENDING_REVIEW`: commit complete and Claude Review not yet completed. This
  state records architecture review debt; it does not require push and does not
  block unrelated local development unless the user requests production-ready
  status, merge, release, or review closure.
- `REMOTE_SYNC`: commit has been pushed to `origin/dev-clean` for remote backup,
  CI, or GitHub Actions review. Remote sync is optional and requires explicit
  user approval.

State output standard:

- `Local Complete`: `YES` when commit, local validation, and clean worktree are
  confirmed.
- `Review State`: `PENDING_REVIEW`, `IN_REVIEW`, `APPROVED`, or
  `NEEDS_CHANGES`.
- `Remote Sync`: `YES` only after push to `origin/dev-clean` succeeds.
- `Push Required`: always `OPTIONAL`, never `REQUIRED`, unless a user explicitly
  scopes a remote workflow that needs pushed commits.

Decoupled Review Request System:

- Claude Review is required after every Codex commit, but review is not an
  automatic side effect of commit creation.
- Codex must request Claude Review after every commit.
- Codex must mark committed work as `REVIEW REQUIRED` / `PENDING_REVIEW` until
  a manual/chat-based review is independently completed.
- Commit plus local validation can be `LOCAL_COMPLETE`.
- Commit does not equal `APPROVED` review.
- CI does not replace Claude Review.
- Review is not assumed to have run.
- Claude Review is read-only but required as a separate architecture validation
  state.
- Codex must not skip review for governance-only, documentation-only, or
  "low-risk" commits.
- Codex may continue local development while review is pending when the user
  assigns another local task, but must not report production-ready status, merge,
  release, or review closure while review is pending.
- Push is optional remote sync, not a required validation step.
- Claude Review does not inherently depend on push. It may use local
  `commit_range` packets, packet review, or remote `workflow_dispatch` packet
  artifacts when authorized.
- Remote `workflow_dispatch` is artifact-only. It may generate or collect a
  sanitized packet and upload it as a GitHub Actions artifact, but it must not
  call Claude, Anthropic, or any external AI API from CI.
- AI review is external and manual only. CI is never allowed to execute AI
  inference.
- CI may build, test, generate sanitized review packets, and upload artifacts.
  CI must not perform model-based review, automated AI evaluation, or external
  LLM inference.
- Claude Review is performed only by manual/chat-based analysis of the
  downloaded artifact or copied packet content.
- If review cannot be requested or triggered because workflow, Claude, token
  authorization, local dependency, or user approval is missing, Codex must
  report:
  `REVIEW REQUIRED: PENDING_REVIEW`.
- If Claude Review fails, returns NEEDS_CHANGES/BLOCKED, or cannot produce a
  verdict, Codex must report the task as incomplete until the user authorizes a
  scoped fix or explicitly stops the task.

Review State Machine:

- `PENDING_REVIEW`: Codex has committed changes and requested review, but
  Claude Review has not started.
- `IN_REVIEW`: Claude Review is actively running or waiting for a verdict.
- `APPROVED`: Claude Review returned PASS or PASS_WITH_POLISH with no required
  blocking fix. Only APPROVED means the committed task is complete.
- `NEEDS_CHANGES`: Claude Review returned NEEDS_CHANGES/BLOCKED, failed to
  produce a verdict, or identified a required fix.

Review System Rule (locked artifact-only flow):

- CI only generates artifacts.
- CI does not execute AI review.
- Claude Review is manual/chat-based only.
- No workflow-based AI execution is allowed.
- No external AI API calls are allowed from CI.
- GitHub Actions may run tests, generate sanitized review packets, and upload
  packet artifacts only.

Review request methods:

- Local `commit_range` packet generation for committed repository changes.
- Local `packet_path` / packet-based review for sanitized review packets.
- Manual `workflow_dispatch` through the Claude Review GitHub Actions workflow
  when remote sync is explicitly authorized, limited to packet/artifact
  generation and upload only.
- Manual/chat-based Claude Review from the downloaded artifact or copied packet
  content. CI must not execute the Claude review itself.

CI vs Claude Review:

- CI checks syntax, imports, unit tests, smoke tests, and basic command
  correctness.
- GitHub Actions may generate sanitized review packets and upload artifacts for
  manual review, but it must not execute external AI inference.
- Claude Review checks architecture validation, TPB baseline integrity, market
  structure boundaries, Scenario Engine isolation, EV/ROI violation detection,
  ranking contamination, execution-layer isolation, and governance compliance.
- CI and Claude Review are both mandatory after a commit. Neither replaces the
  other, but Claude Review remains a decoupled request state rather than an
  automatic commit hook.

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
- A commit has been created but Codex has not marked `REVIEW REQUIRED` /
  `PENDING_REVIEW`.
- Codex attempts to mark a committed task complete using CI only.
- Codex attempts to merge, release, or declare production readiness while review
  state is PENDING_REVIEW, IN_REVIEW, or NEEDS_CHANGES.
- Codex reports push as required when the user has not explicitly requested
  remote sync, CI, or GitHub Actions review.
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
- After any commit, mark `REVIEW REQUIRED` and report the current review state.
  Request Claude Review using an authorized review method when scoped or
  approved. If review cannot be triggered yet, report
  `REVIEW REQUIRED: PENDING_REVIEW` and `Push Required: OPTIONAL`.

## Codex Execution Loop

1. Check branch is `dev-clean`.
2. Read `AGENTS.md`.
3. Validate task scope, allowed files, forbidden files, and approvals.
4. Execute only allowed operations on `dev-clean`.
5. Run local validation.
6. Commit when the task requires or authorizes a commit.
7. Mark `REVIEW REQUIRED` / `PENDING_REVIEW` after every commit.
8. Report `LOCAL_COMPLETE` when commit, validation, and clean worktree are
   confirmed.
9. Request Claude Review as an independent step when scoped or approved.
10. Push only when explicitly approved as optional remote sync.
11. Apply scoped fixes if needed, then repeat validation, commit, and review
   request for the fix.
12. Report files changed, validations, Claude findings, fixes, protected-path
   status, TPB baseline integrity, market-structure integrity, customer
   execution isolation, UI status, Git state, review state, Remote Sync, Push
   Required, and
   unresolved risks.
