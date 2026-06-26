# Field Readiness Classification

Scope: report-only classification of mapped missing risk contract fields. This script does not modify runtime logic, replay portfolio logic, write golden JSON, enable portfolio extraction, or enable backtest.

## Gate Status

- PORTFOLIO_EXTRACTION: BLOCKED
- BACKTEST_READY: NO

## Category Counts

| Category | Field count |
| --- | ---: |
| requires approved new formula | 1 |
| requires read-only live-function replay | 11 |
| requires settled post-match design | 1 |

## Field Classification

| Field | Readiness category | Reason |
| --- | --- | --- |
| `risk_gate.risk_level` | requires read-only live-function replay | Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance. |
| `risk_gate.rank1_eligible` | requires read-only live-function replay | Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance. |
| `risk_gate.gate_reasons` | requires read-only live-function replay | Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance. |
| `risk_gate.hard_blockers` | requires read-only live-function replay | Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance. |
| `risk_gate.soft_warnings` | requires read-only live-function replay | Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance. |
| `exposure_risk.correct_score_limit` | requires read-only live-function replay | Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance. |
| `exposure_risk.correct_score_limit_source` | requires read-only live-function replay | Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance. |
| `scenario_risk.failed_scenario_probability` | requires read-only live-function replay | Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance. |
| `scenario_risk.adjacent_path_failure` | requires read-only live-function replay | Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance. |
| `scenario_risk.narrow_exact_score_dependency` | requires read-only live-function replay | Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance. |
| `scenario_risk.pressure_strictness` | requires read-only live-function replay | Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance. |
| `risk_score_components.canonical_risk_score` | requires approved new formula | No canonical risk score formula is approved; keep null until Jin approves a formula task. |
| `post_match_risk_outcome` | requires settled post-match design | Pre-match contracts cannot settle realized risk outcome; requires post-match design. |

## Recommendation

Next safe step is a Jin-reviewed design task for read-only replay boundaries. Do not implement extraction, backtest, or a canonical risk score formula yet.
