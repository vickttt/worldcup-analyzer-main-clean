# NODE 2 Model Dependency Graph

Date: 2026-06-28
Node: `NODE 2 - MODEL-DESIGN ANALYSIS (READ ONLY)`
Scope: static dependency analysis only.

## Modules Involved

| Module or file | Role in model layer | Risk level |
| --- | --- | --- |
| `app.py` | detail-page orchestration, portfolio seed, allocation optimizer, snapshot persistence, UI rendering | high |
| `modules/decision_engine.py` | direction confidence, upset risk, participation advice, stake guidance | high |
| `modules/result_distribution.py` | match result path distribution and scenario signals | medium |
| `modules/strategy/core.py` | strategy score, match betting score, stake display mapping, ranking key | high |
| `modules/portfolio_engine.py` | portfolio generation, portfolio scoring, risk gate, rank-1 eligibility, match investment score | high |
| `modules/probability_model.py` | probability blending | medium |
| `modules/score_model.py` | score recommendations | medium |
| `modules/value_model.py` | value analysis | medium |
| `modules/user_odds.py` | actual odds slots and recommendation slots | high |
| `modules/odds.core.py` | market pricing helpers after Phase 1 extraction | medium |
| `modules/portfolio/shadow.py` | shadow portfolio observation only, not runtime-wired | medium |

## Main Call Chain

```text
app.py::render_analysis_page
  -> fetch_match_data / fetch_odds / fetch_polymarket
  -> combine_probabilities
  -> recommend_scores
  -> rate_opportunity
  -> analyze_value
  -> build_betting_opinion
  -> build_match_context
  -> build_result_distribution
  -> build_decision_engine
  -> recommendation_combo
  -> recommended_total_stake
  -> stake_amounts
  -> strategy_comparison
  -> compute_portfolio_score
  -> portfolio_risk_gate
  -> rank1_eligibility_check
  -> rank_key_with_eligibility
  -> render_portfolio_ranking
  -> save_match_snapshot
```

## Dependency On `data/history`

The model layer has a direct historical snapshot dependency through `app.py` and report/backtest scripts:

- `app.py` writes pre-match snapshots containing odds, API context, Polymarket, actual odds, recommendation combo, strategy snapshot, decision, distribution, and betting opinion.
- post-match analysis reads those snapshots and compares strategy output to final results.
- existing backtest/report scripts read `data/history/*_pre.json`, `data/history/*_post.json`, and backfill snapshots.
- golden v2 and risk contract reports reference selected `data/history` pre-match snapshots.

Risk: high for extraction. Snapshot schema stability is part of the product contract, even when the code path looks internal.

## Dependency On Golden JSON

Golden validation currently depends on:

- `reports/golden_output_snapshot_v1.json`.
- `reports/golden_output_snapshot_v2.json`.
- `reports/golden_risk_contract_v1.json`.
- `reports/golden_risk_contract_v1_validation_report.md`.
- shadow and assertion-gate reports.

Risk: medium-high. Golden files protect observable behavior, but they do not yet define a canonical risk score or guarantee full risk-gate payload coverage.

## Dependency On UI Layer

Hidden UI coupling is high:

- `app.py` owns Streamlit state, detail-page orchestration, model execution order, portfolio construction, snapshot persistence, and rendering.
- model outputs are assembled close to `st.*` calls and `st.session_state`.
- recommendation outputs are saved after UI page execution, not from an isolated model service.
- `render_portfolio_ranking(...)` is both display surface and final ranking consumer.

The model layer cannot yet be treated as UI-independent.

## Dependency On API Refresh Layer

Hidden API coupling is medium:

- `build_decision_engine(...)` consumes `api_football_data`.
- `build_match_context(...)` consumes API-Football context.
- portfolio scoring uses `distribution.game_behavior`, which depends on match context.
- `compute_match_investment_score(...)` includes API quality and data timing concepts in its score components.

The Odds API remains disabled for the current UI-CACHE-API phase, but model logic still consumes odds-like payloads and API-Football context if available.

## Dependency On Cache Layer

Hidden cache coupling is medium:

- detail page uses cached/fetched odds and API-Football data before model execution.
- data freshness context is built after snapshot save.
- `data/history` snapshots become both cache-like persistence and golden/backtest inputs.
- cache status appears in UI and audit reports, but not as a first-class model input contract.

## Implicit State Dependencies

| State | Source | Why it matters |
| --- | --- | --- |
| `st.session_state.selected_fixture` | `app.py` | controls fixture, page, refresh state, and snapshot identity |
| local DB/cache flags | schedule and odds clients | changes whether data is fetched or read from cache |
| user odds files | `modules/user_odds.py`, history paths | influence recommendation slots and portfolio pricing |
| snapshot files | `data/history` | feed post-match audit, reports, backtest, golden validation |
| distribution payload shape | result distribution and portfolio engine | controls scenario path risk, coverage, and ranking |
| strategy dictionary fields | strategy/portfolio/app handoff | no typed boundary; missing fields change ranking behavior |

## Portfolio And Risk Contract Link

Portfolio is built from model outputs in this order:

1. market and context data produce probability and result distribution.
2. decision engine produces participation and stake guidance.
3. recommendation combo produces candidate betting items and shares.
4. app-local stake mapping converts shares into amounts.
5. portfolio engine generates candidate styles and pressure templates.
6. scoring/risk gates evaluate candidates.
7. ranking key uses eligibility, risk level, exposure, and score.

Missing contract:

- canonical `risk_score`.
- stable `RiskAssessment` payload.
- stable `PortfolioCandidate` payload.
- explicit distinction between display stake and allocation stake.
- complete golden coverage for risk gate, rank eligibility, and score-grid contracts.

## Why Portfolio Extraction Is Still Blocked

- `app.py` still owns allocation optimizer and snapshot assembly.
- portfolio candidate payloads are implicit dictionaries.
- risk gate and ranking depend on score-grid shape and distribution metadata.
- UI rendering consumes ranking payloads directly.
- golden v2 protects outputs but not all intermediate risk semantics.
- backtest scripts depend on historical snapshot schema produced by `app.py`.

## Risk Identification

| Coupling | Severity | Reason |
| --- | --- | --- |
| UI layer coupling | high | model execution and rendering share `app.py` and Streamlit state |
| API refresh coupling | medium | API-Football context changes match context, decision, and data quality |
| cache coupling | medium | cache/source status affects payload availability and freshness interpretation |
| implicit state coupling | high | dict fields and snapshot schema drive behavior without a typed contract |
| golden validation coupling | medium-high | golden outputs exist, but intermediate risk contract coverage is partial |

## Readiness Decision

- Model pipeline clarity: `fragmented`.
- Dependency risk level: `high`.
- Hidden coupling severity: `high`.
- Readiness for NODE 3: `NO`, unless NODE 3 is treated strictly as planning-only and Jin explicitly approves.
- Safe to continue auto-advance: `NO`.
