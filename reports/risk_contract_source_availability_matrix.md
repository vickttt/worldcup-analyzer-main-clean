# Risk Contract Source Availability Matrix

Scope: read-only coverage matrix for existing `risk_contract_v1` fixture fields. This script does not write golden JSON, replay portfolio logic, enable portfolio extraction, or enable backtest.

## Summary

- Contracts checked: 10
- Source: `reports/golden_risk_contract_v1.json`
- PORTFOLIO_EXTRACTION: BLOCKED
- BACKTEST_READY: NO

## Matrix

| Field | Available contracts | Total contracts | Coverage |
| --- | ---: | ---: | ---: |
| `risk_gate.risk_level` | 0 | 10 | 0.0% |
| `risk_gate.rank1_eligible` | 0 | 10 | 0.0% |
| `risk_gate.gate_reasons` | 10 | 10 | 100.0% |
| `risk_gate.hard_blockers` | 10 | 10 | 100.0% |
| `risk_gate.soft_warnings` | 10 | 10 | 100.0% |
| `exposure_risk.correct_score_limit` | 0 | 10 | 0.0% |
| `exposure_risk.correct_score_limit_source` | 0 | 10 | 0.0% |
| `scenario_risk.failed_scenario_probability` | 0 | 10 | 0.0% |
| `scenario_risk.adjacent_path_failure` | 0 | 10 | 0.0% |
| `scenario_risk.narrow_exact_score_dependency` | 0 | 10 | 0.0% |
| `scenario_risk.pressure_strictness` | 0 | 10 | 0.0% |
| `risk_score_components.canonical_risk_score` | 0 | 10 | 0.0% |
| `post_match_risk_outcome` | 0 | 10 | 0.0% |

## Gaps

- `risk_gate.risk_level` coverage is 0.0%.
- `risk_gate.rank1_eligible` coverage is 0.0%.
- `exposure_risk.correct_score_limit` coverage is 0.0%.
- `exposure_risk.correct_score_limit_source` coverage is 0.0%.
- `scenario_risk.failed_scenario_probability` coverage is 0.0%.
- `scenario_risk.adjacent_path_failure` coverage is 0.0%.
- `scenario_risk.narrow_exact_score_dependency` coverage is 0.0%.
- `scenario_risk.pressure_strictness` coverage is 0.0%.
- `risk_score_components.canonical_risk_score` coverage is 0.0%.
- `post_match_risk_outcome` coverage is 0.0%.

## Recommendation

Do not enable portfolio extraction or backtest. Next safe step is to classify which unavailable fields can be sourced from existing live functions versus which require an approved new formula or settled-result design.
