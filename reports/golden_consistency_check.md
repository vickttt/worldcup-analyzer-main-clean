# Golden Consistency Check

This report compares the saved v2 golden outputs across the selected scenarios. It does not recalculate rankings, allocations, strategy scores, or odds.

## Match Coverage

- selected matches: 5
- unique top raw strategy names: 3 (只买最佳波胆, 独赢策略, 让球策略)
- matches with incomplete/missing comparable market data: 2

## Ranking Stability Across Matches

- 2026_06_21_Tunisia_Japan_pre: top `只买最佳波胆` (display `推荐组合`), score 62, score spread 21, final `Tunisia +1.5`.
- 2026_06_25_Japan_Sweden_pre: top `让球策略` (display `推荐组合`), score 49, score spread 11, final `Japan`.
- 2026_06_25_Ecuador_Germany_pre: top `独赢策略` (display `推荐组合`), score 74, score spread 36, final `Ecuador +0.5`.
- 2026_06_24_Scotland_Brazil_pre: top `独赢策略` (display `推荐组合`), score 73, score spread 33, final `Scotland +1.5`.
- 2026_06_21_New_Zealand_Egypt_pre: top `只买最佳波胆` (display `推荐组合`), score 44, score spread 2, final `观察为主`.

Observation: rankings are scenario-sensitive. The display label can normalize different first-ranked strategies to `推荐组合`, so future diff checks must compare raw strategy name, display name, order, score, and item amounts together.

## Strategy Score Variance

- top score min/max: 44 / 74
- top score mean: 60.4
- top score population stdev: 12.21

- 2026_06_21_Tunisia_Japan_pre: score range 41 to 62 with saved top max loss 300.
- 2026_06_25_Japan_Sweden_pre: score range 38 to 49 with saved top max loss 1200.
- 2026_06_25_Ecuador_Germany_pre: score range 38 to 74 with saved top max loss 200.
- 2026_06_24_Scotland_Brazil_pre: score range 40 to 73 with saved top max loss 1100.
- 2026_06_21_New_Zealand_Egypt_pre: score range 42 to 44 with saved top max loss 100.

## Portfolio Allocation Drift

- positive recommendation stake min/max: 100.0 / 1200.0
- positive recommendation stake mean: 580.0

- 2026_06_21_Tunisia_Japan_pre: positive items 1, positive recommendation stake 300.0, decision stake 300.
- 2026_06_25_Japan_Sweden_pre: positive items 3, positive recommendation stake 1200.0, decision stake 1200.
- 2026_06_25_Ecuador_Germany_pre: positive items 2, positive recommendation stake 200.0, decision stake 200.
- 2026_06_24_Scotland_Brazil_pre: positive items 2, positive recommendation stake 1100.0, decision stake 1100.
- 2026_06_21_New_Zealand_Egypt_pre: positive items 1, positive recommendation stake 100.0, decision stake 100.

Observation: allocation exposure varies widely between low-exposure and high-stake recommendation snapshots. Portfolio extraction must lock both item amounts and strategy-level max_loss fields.

## Odds vs Strategy Disagreement Frequency

- saved market disagreement scores: [46, 21, 0, 8, 0]
- medium-or-higher disagreement count: 1
- missing comparable market data count: 2

- 2026_06_21_Tunisia_Japan_pre: disagreement 中分歧 (46), direction confidence 64, upset index 63.
- 2026_06_25_Japan_Sweden_pre: disagreement 低分歧 (21), direction confidence 79, upset index 47.
- 2026_06_25_Ecuador_Germany_pre: disagreement 低分歧 (0), direction confidence 57, upset index 52.
- 2026_06_24_Scotland_Brazil_pre: disagreement 低分歧 (8), direction confidence 76, upset index 60.
- 2026_06_21_New_Zealand_Egypt_pre: disagreement 低分歧 (0), direction confidence 0, upset index 47.

## Consistency Decision

The v2 lock is stronger than v1 because it covers five distinct saved behaviors: high actual-odds divergence, balanced market, low-exposure favorite, upset-prone favorite/handicap tension, and incomplete odds. It is still not a full golden test harness because it serializes outputs but does not yet automate diff assertions.