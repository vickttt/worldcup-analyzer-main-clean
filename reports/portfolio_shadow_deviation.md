# Portfolio Shadow Deviation

This report compares saved strategy ranking, saved capital allocation, and shadow replay allocation across the golden v2 matches. It is observation-only.

## Scenario Deviations

### 2026_06_21_Tunisia_Japan_pre

- match: Tunisia vs Japan
- top ranked strategy: 只买最佳波胆 / score 62 / saved stake 300
- highest capital strategy: rank 1 只买最佳波胆 / stake 300
- strategy ranking vs capital: aligned
- expected decision stake vs positive combo delta: 0
- expected decision stake vs top strategy delta: 0
- saved-vs-shadow replay absolute delta: 0

### 2026_06_25_Japan_Sweden_pre

- match: Japan vs Sweden
- top ranked strategy: 让球策略 / score 49 / saved stake 1200
- highest capital strategy: rank 1 让球策略 / stake 1200
- strategy ranking vs capital: aligned
- expected decision stake vs positive combo delta: 0
- expected decision stake vs top strategy delta: 0
- saved-vs-shadow replay absolute delta: 0

### 2026_06_25_Ecuador_Germany_pre

- match: Ecuador vs Germany
- top ranked strategy: 独赢策略 / score 74 / saved stake 200
- highest capital strategy: rank 1 独赢策略 / stake 200
- strategy ranking vs capital: aligned
- expected decision stake vs positive combo delta: 0
- expected decision stake vs top strategy delta: 0
- saved-vs-shadow replay absolute delta: 0

### 2026_06_24_Scotland_Brazil_pre

- match: Scotland vs Brazil
- top ranked strategy: 独赢策略 / score 73 / saved stake 1100
- highest capital strategy: rank 1 独赢策略 / stake 1100
- strategy ranking vs capital: aligned
- expected decision stake vs positive combo delta: 0
- expected decision stake vs top strategy delta: 0
- saved-vs-shadow replay absolute delta: 0

### 2026_06_21_New_Zealand_Egypt_pre

- match: New Zealand vs Egypt
- top ranked strategy: 只买最佳波胆 / score 44 / saved stake 100
- highest capital strategy: rank 1 只买最佳波胆 / stake 100
- strategy ranking vs capital: aligned
- expected decision stake vs positive combo delta: 0
- expected decision stake vs top strategy delta: 0
- saved-vs-shadow replay absolute delta: 0

## Cross-Scenario Consistency

- scenarios checked: 5
- scenarios with exact saved/replay match: 5
- scenarios with top strategy stake equal to decision stake: 5
- scenarios with positive combo stake equal to decision stake: 5

## Interpretation

- Strategy ranking and capital allocation are related but not identical: a first-ranked strategy can have a different internal stake profile than the positive recommendation combo.
- Display names normalize the first ranked strategy to `推荐组合`; raw strategy names must remain part of any future diff gate.
- Shadow replay is strongest when the saved strategy has one or two active items. Multi-item strategies remain sensitive to hidden app-level helper contracts such as exact bet correlation, role scoring, and generated item pools.
- No deviation in this report changes current behavior; it only identifies where extraction could drift.