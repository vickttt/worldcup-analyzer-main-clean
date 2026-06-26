# Risk Consistency Check

This report checks whether observed risk-related inputs consistently produce stake and allocation behavior across golden v2. It does not modify any code.

## Rule Results

| Rule | Result | Evidence |
| --- | --- | --- |
| Same strategy score always produces same stake | INCONCLUSIVE | No duplicate top strategy scores exist across golden v2; observed score-to-stake is not monotonic. |
| Higher top strategy score means higher stake | INCONSISTENT | Score 74 has stake 200, while score 49 has stake 1200. |
| Direction confidence drives saved decision stake | PARTIALLY CONSISTENT | Saved stake reasons cite direction confidence and value rating; confidence 79 -> 1200, 76 -> 1100, 64 -> 300, 57 -> 200, 0 -> 100. Value adjustment prevents a pure one-variable rule. |
| Same risk input always produces same stake | INCONCLUSIVE | Golden v2 lacks duplicate identical risk-input tuples and lacks full risk_gate payloads. |
| Odds volatility affects risk | PARTIALLY CONSISTENT | `volatility` affects evaluate_strategy and compute_portfolio_score when portfolio metrics exist, but some golden rows lack portfolio score components. |
| Strategy disagreement changes risk | PARTIALLY CONSISTENT | Shadow verdict has explicit penalties in match_betting_score, but golden v2 does not include enough shadow/risk payload to prove the path per match. |
| Market disagreement directly changes stake | INCONSISTENT | Disagreement 46 has stake 300, disagreement 21 has stake 1200, disagreement 0 has stakes 200 and 100. |
| Allocation equals decision stake | CONSISTENT | All five golden v2 scenarios have positive combo stake and top strategy stake equal to decision stake in prior shadow assertion reports. |
| Risk gate controls Rank #1 eligibility | INCONCLUSIVE | `rank_key_with_eligibility` supports this, but golden v2 lacks `risk_gate` payloads for top strategies. |

## Observed Pairs

- strategy_score -> decision_stake: [(62, 300), (49, 1200), (74, 200), (73, 1100), (44, 100)]
- direction_confidence -> decision_stake: [(64, 300), (79, 1200), (57, 200), (76, 1100), (0, 100)]
- market_disagreement -> decision_stake: [(46, 300), (21, 1200), (0, 200), (8, 1100), (0, 100)]
- volatility available for 5 / 5 matches.

## Consistency Decision

Risk semantics are not consistently represented by a single field. Some local functions are deterministic, but end-to-end risk-to-stake behavior is only partially consistent and not fully assertable from golden v2.