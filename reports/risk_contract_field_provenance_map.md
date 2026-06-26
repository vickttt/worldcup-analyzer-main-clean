# Risk Contract Field Provenance Map

Date: 2026-06-27

Scope: read-only mapping of missing or incomplete `risk_contract_v1` fields. This report does not recompute rankings, modify runtime logic, change golden JSON, implement extraction, enable portfolio extraction, or enable backtest.

## Summary

- Current serializer source: `scripts/generate_golden_risk_contract_v1.py`.
- Current live risk semantics source: `modules/portfolio_engine.py`.
- Current design source: `reports/canonical_risk_contract_design.md`.
- Current gap source: `reports/risk_feature_extraction_v1.md`.
- Main blocker: existing golden v2 saved strategy rows do not carry full `risk_gate`, correct-score exposure limit, scenario risk internals, canonical risk score, or post-match outcome payloads.

## Provenance Table

| Field | Current status | Likely source | Source file/function/report | Extraction difficulty | Risk level | Needed before portfolio extraction | Needed before backtest | Recommended next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `risk_gate.risk_level` | Missing or `UNKNOWN` when saved strategy lacks full gate payload. | Runtime zero-risk gate result. | `modules/portfolio_engine.py::portfolio_risk_gate`; serialized by `scripts/generate_golden_risk_contract_v1.py::make_contract`. | Medium: requires saving or replaying gate payload with scenario grid context. | High | Yes | Yes | Add a read-only source availability matrix for `strategy.risk_gate.risk_level`. |
| `risk_gate.rank1_eligible` | Null in observed contracts; current live eligibility is stored separately. | Rank #1 eligibility check. | `modules/portfolio_engine.py::rank1_eligibility_check`; `app.py` attaches `result["rank1_eligibility"]`; serializer currently reads `strategy.get("risk_gate")`. | Medium: needs an explicit bridge from `rank1_eligibility` to risk contract. | High | Yes | Yes | Map `rank1_eligibility.rank1_eligible` as likely source before any serializer change. |
| `risk_gate.gate_reasons` | Missing as a canonical list; live gate has `reason` and `failed_paths`. | Gate reason plus eligibility blockers. | `modules/portfolio_engine.py::portfolio_risk_gate`; `modules/portfolio_engine.py::rank1_eligibility_check`. | Medium: requires normalizing strings into stable lists. | High | Yes | Yes | Define list provenance from `risk_gate.reason`, `risk_gate.failed_paths`, and `rank1_eligibility.rank1_blockers`. |
| `risk_gate.hard_blockers` | Empty list in observed contract, not populated from live blockers. | Failed zero-risk gate and Rank #1 blockers. | `modules/portfolio_engine.py::portfolio_risk_gate`; `modules/portfolio_engine.py::rank1_eligibility_check`. | Medium: requires classifying blockers without changing live behavior. | High | Yes | Yes | Create a read-only blocker classification table. |
| `risk_gate.soft_warnings` | Empty list in observed contract, not populated from live warnings. | Non-blocking exposure and display warnings. | `modules/portfolio_engine.py::correct_score_exposure_control`; `modules/report_generator.py::_risk_gate_result`; `app.py` risk display sections. | Medium: warnings are distributed and partly display-oriented. | Medium | Yes | Yes | Identify blocking versus non-blocking warning sources before population. |
| `exposure_risk.correct_score_limit` | Null in observed contracts; serializer sets `correct_score_limit = None`. | Correct-score exposure policy limit. | `modules/portfolio_engine.py::correct_score_exposure_control`; `reports/risk_feature_extraction_v1.md`. | Low-medium: live function returns `limit`, but saved strategies do not carry it. | High | Yes | Yes | Use `correct_score_exposure_control(...).limit` as likely source in future read-only replay. |
| `exposure_risk.correct_score_limit_source` | `"unknown"` in observed contracts. | Portfolio style used to select conservative/default/aggressive limit. | `modules/portfolio_engine.py::correct_score_exposure_control`; portfolio style labels. | Low-medium: source label must be derived consistently from style text. | Medium | Yes | Yes | Define allowed labels: `conservative`, `default`, `aggressive`, `unknown`. |
| `scenario_risk.failed_scenario_probability` | Null in observed contracts. | Failed scenario probability from main/adjacent/tail score-grid rows. | `modules/portfolio_engine.py::portfolio_risk_gate` local `failed_prob`; returned as `failed_probability`. | Medium-high: field exists under a different live name only when gate payload is present. | High | Yes | Yes | Map from `risk_gate.failed_probability` or replay gate read-only with score grid context. |
| `scenario_risk.adjacent_path_failure` | Null in observed contracts. | Adjacent failed probability. | `modules/portfolio_engine.py::portfolio_risk_gate` local `adjacent_failed_prob`; returned as `adjacent_failed_probability`. | Medium-high: field exists under a different live name. | High | Yes | Yes | Map from `risk_gate.adjacent_failed_probability`. |
| `scenario_risk.narrow_exact_score_dependency` | Null in observed contracts. | Correct-score dependency and narrow exact-score blockers. | `modules/portfolio_engine.py::portfolio_risk_gate`; `modules/portfolio_engine.py::correct_score_exposure_control`. | Medium-high: currently encoded as blocker/warning text, not a stable boolean. | High | Yes | Yes | Define a read-only boolean derivation from correct-score stake share, core items, and narrow-path blockers. |
| `scenario_risk.pressure_strictness` | Null in observed contracts. | Match pressure strictness multiplier. | `modules/portfolio_engine.py::_risk_gate_strictness`; distribution `game_behavior`. | Medium: helper is private and currently not serialized. | Medium | Yes | Yes | Record strictness provenance from distribution behavior before exposing it. |
| `risk_score_components.canonical_risk_score` | Null by design; no canonical formula exists. | Not currently defined. Candidate inputs are distributed risk components. | `reports/risk_feature_extraction_v1.md`; `reports/risk_gap_analysis.md`; `modules/strategy/core.py::strategy_score`; `modules/portfolio_engine.py::compute_portfolio_score`. | High: needs separately approved formula design. | High | Yes | Yes | Keep null until Jin approves a formula task; do not infer or backfill now. |
| `post_match_risk_outcome` | Null in pre-match contracts. | Future settled post-match outcome based on result and realized portfolio path. | `reports/canonical_risk_contract_design.md`; post-match validation scripts; `scripts/backtest_attribution.py`. | High: requires settled result linkage and outcome schema. | High | No | Yes | Keep null for pre-match contracts; design a settled-contract report before backtest enablement. |

## Blocking Gates

- `PORTFOLIO_EXTRACTION: BLOCKED`
- `BACKTEST_READY: NO`

## Read-Only Next Step

Create a report-only source availability matrix that checks each golden fixture for the likely source keys listed above, without writing golden JSON and without replaying portfolio logic.
