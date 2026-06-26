# Golden Assertion Gate v1

This gate validates consistency across the locked production snapshot, the shadow replay, and the existing golden v2 reference. It does not recompute app output or modify code.

## Gate Inputs

- golden v2 snapshot: `reports/golden_output_snapshot_v2.json`
- golden v2 sha256: `4fc5e5eeacdf6cbf6c38d8d2a72245a92311f22f271f1c9ce0106c8058c2bb40`
- production reference: saved output inside golden v2
- shadow reference: read-only replay from `modules/portfolio/shadow.py`

## Assertions

### 2026_06_21_Tunisia_Japan_pre

- match: Tunisia vs Japan
- ranking stability: MATCH
- selection stability: MATCH
- allocation stability: MATCH
- risk weighting stability: MATCH
- gate row result: PASS_WITH_RISK_PAYLOAD_GAP

### 2026_06_25_Japan_Sweden_pre

- match: Japan vs Sweden
- ranking stability: MATCH
- selection stability: MATCH
- allocation stability: MATCH
- risk weighting stability: MATCH
- gate row result: PASS_WITH_RISK_PAYLOAD_GAP

### 2026_06_25_Ecuador_Germany_pre

- match: Ecuador vs Germany
- ranking stability: MATCH
- selection stability: MATCH
- allocation stability: MATCH
- risk weighting stability: MATCH
- gate row result: PASS_WITH_RISK_PAYLOAD_GAP

### 2026_06_24_Scotland_Brazil_pre

- match: Scotland vs Brazil
- ranking stability: MATCH
- selection stability: MATCH
- allocation stability: MATCH
- risk weighting stability: MATCH
- gate row result: PASS_WITH_RISK_PAYLOAD_GAP

### 2026_06_21_New_Zealand_Egypt_pre

- match: New Zealand vs Egypt
- ranking stability: MATCH
- selection stability: MATCH
- allocation stability: MATCH
- risk weighting stability: MATCH
- gate row result: PASS_WITH_RISK_PAYLOAD_GAP

## Gate Decision

- ranking stability across all scenarios: MATCH
- selection stability across all scenarios: MATCH
- allocation stability across all scenarios: MATCH
- risk weighting stability across available fields: MATCH
- golden assertion gate: PASS_WITH_COVERAGE_GAP

## Extraction Implication

Portfolio extraction remains blocked. The gate proves saved-output alignment for golden v2, but it does not yet prove full production recomputation or post-match/backtest settlement behavior.