# Portfolio Shadow vs Production Diff

This report is a strict read-only comparison. Production behavior is represented by the locked `reports/golden_output_snapshot_v2.json` output, not by re-running the Streamlit runtime.

## Inputs

- golden v2 snapshot sha256: `4fc5e5eeacdf6cbf6c38d8d2a72245a92311f22f271f1c9ce0106c8058c2bb40`
- production reference: saved strategy, portfolio, decision, and allocation fields in golden v2
- shadow reference: `modules/portfolio/shadow.py` read-only replay helpers
- no production code, shadow code, or golden output file was modified during this comparison

## Source Contract Presence

- recommended_total_stake: MATCH / production `app.py::recommended_total_stake` hash `a12b01c30658` / shadow `modules/portfolio/shadow.py::recommended_total_stake` hash `ed7b78792756`
- stake_amounts: MATCH / production `app.py::stake_amounts` hash `f882676470fb` / shadow `modules/portfolio/shadow.py::stake_amounts` hash `6203150841ba`
- strategy_weight: MATCH / production `app.py::strategy_weight` hash `8fe3339f43f8` / shadow `modules/portfolio/shadow.py::strategy_weight` hash `8fe3339f43f8`
- correlation_adjusted_weight: MATCH / production `app.py::correlation_adjusted_weight` hash `66fede1ba39f` / shadow `modules/portfolio/shadow.py::correlation_adjusted_weight` hash `2d9ce0acf3bf`
- allocate_strategy_items: MATCH / production `app.py::allocate_strategy_items` hash `e9b236bc6fc4` / shadow `modules/portfolio/shadow.py::allocate_strategy_items` hash `12dacc4c5681`
- enforce_correct_score_floor: MATCH / production `app.py::enforce_correct_score_floor` hash `2d86d814dafd` / shadow `modules/portfolio/shadow.py::enforce_correct_score_floor` hash `2d86d814dafd`
- recommended_stake_mvp: MATCH / production `modules/strategy/core.py::recommended_stake_mvp` hash `478b2089ec7f` / shadow `modules/portfolio/shadow.py::recommended_stake_mvp` hash `478b2089ec7f`
- strategy_score: MATCH / production `modules/strategy/core.py::strategy_score` hash `0cd42a44266c` / shadow `modules/portfolio/shadow.py::strategy_score` hash `c22f44e0176f`
- rank_key_with_eligibility: MATCH / production `modules/strategy/core.py::rank_key_with_eligibility` hash `32da2dbbc7f4` / shadow `modules/portfolio/shadow.py::rank_key_with_eligibility` hash `32da2dbbc7f4`

## Per-Match Diff

### 2026_06_21_Tunisia_Japan_pre

- match: Tunisia vs Japan
- ranking order: MATCH
- stake allocation: MATCH
- portfolio selection: MATCH
- risk weighting: MATCH
- deviation score: 100 / 100
- production top: 只买最佳波胆 / display 推荐组合 / score 62 / stake 300
- shadow replay stake: 300
- production rank key: `(0, 1, -0.0, 62)`
- shadow rank key: `(0, 1, -0.0, 62)`
- allocation explanation: saved top-strategy active item amounts equal shadow replay amounts.
- risk note: golden v2 lacks full `risk_gate` payload for this top strategy; rank-key comparison uses available fields only.

### 2026_06_25_Japan_Sweden_pre

- match: Japan vs Sweden
- ranking order: MATCH
- stake allocation: MATCH
- portfolio selection: MATCH
- risk weighting: MATCH
- deviation score: 100 / 100
- production top: 让球策略 / display 推荐组合 / score 49 / stake 1200
- shadow replay stake: 1200
- production rank key: `(0, 1, -0.0, 49)`
- shadow rank key: `(0, 1, -0.0, 49)`
- allocation explanation: saved top-strategy active item amounts equal shadow replay amounts.
- risk note: golden v2 lacks full `risk_gate` payload for this top strategy; rank-key comparison uses available fields only.

### 2026_06_25_Ecuador_Germany_pre

- match: Ecuador vs Germany
- ranking order: MATCH
- stake allocation: MATCH
- portfolio selection: MATCH
- risk weighting: MATCH
- deviation score: 100 / 100
- production top: 独赢策略 / display 推荐组合 / score 74 / stake 200
- shadow replay stake: 200
- production rank key: `(0, 1, -0.0, 74)`
- shadow rank key: `(0, 1, -0.0, 74)`
- allocation explanation: saved top-strategy active item amounts equal shadow replay amounts.
- risk note: golden v2 lacks full `risk_gate` payload for this top strategy; rank-key comparison uses available fields only.

### 2026_06_24_Scotland_Brazil_pre

- match: Scotland vs Brazil
- ranking order: MATCH
- stake allocation: MATCH
- portfolio selection: MATCH
- risk weighting: MATCH
- deviation score: 100 / 100
- production top: 独赢策略 / display 推荐组合 / score 73 / stake 1100
- shadow replay stake: 1100
- production rank key: `(0, 1, -0.0, 73)`
- shadow rank key: `(0, 1, -0.0, 73)`
- allocation explanation: saved top-strategy active item amounts equal shadow replay amounts.
- risk note: golden v2 lacks full `risk_gate` payload for this top strategy; rank-key comparison uses available fields only.

### 2026_06_21_New_Zealand_Egypt_pre

- match: New Zealand vs Egypt
- ranking order: MATCH
- stake allocation: MATCH
- portfolio selection: MATCH
- risk weighting: MATCH
- deviation score: 100 / 100
- production top: 只买最佳波胆 / display 推荐组合 / score 44 / stake 100
- shadow replay stake: 100
- production rank key: `(0, 1, -0.0, 44)`
- shadow rank key: `(0, 1, -0.0, 44)`
- allocation explanation: saved top-strategy active item amounts equal shadow replay amounts.
- risk note: golden v2 lacks full `risk_gate` payload for this top strategy; rank-key comparison uses available fields only.

## Gate Summary

- matches checked: 5
- full 100/100 alignment rows: 5
- risk payload coverage gaps: 5
- shadow vs production alignment result: PASS_WITH_COVERAGE_GAP

The available golden fields align exactly. The remaining coverage gap is that golden v2 does not contain full `risk_gate` payloads for all strategies, so deep risk-gate internals are not proven by this gate.