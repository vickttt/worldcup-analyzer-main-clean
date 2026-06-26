# Risk Semantics Map

This report maps the observed path from strategy score to risk features, stake size, and portfolio weight. It is read-only modeling, not a new implementation.

## General Transformation Path

```text
strategy inputs -> evaluate_strategy metrics -> strategy_score risk component -> compute_portfolio_score components -> rank/risk gate fields -> decision recommended_stake -> stake_amounts / allocate_strategy_items -> item portfolio weights
```

## Transformation Rules

- `strategy_score -> risk_score`: implicit. Risk appears as `风险控制`, `Risk-Adjusted Value`, `Drawdown / Zero Risk`, `risk_gate.risk_level`, and `correct_score_exposure.stake_share`.
- `risk_score -> stake_size`: not direct. Saved decision stake is driven by `decision.recommended_stake`, which references direction confidence and value rating, not top strategy score alone.
- `stake_size -> portfolio_weight`: decision stake is split by candidate `share`; strategy stake is split by correlation-adjusted weights and correct-score floor rules.
- `portfolio_weight -> ranking`: ranking uses eligibility, risk rank, correct-score exposure penalty, and score.

## Golden v2 Match Traces

### 2026_06_21_Tunisia_Japan_pre

- match: Tunisia vs Japan
- scenario role: high odds mismatch match
- strategy_score: 62 via top strategy `只买最佳波胆`
- implicit risk inputs: max_loss 300, volatility 669.35, concentration 0.00, risk_reward 5.00
- risk component observed: `2`; portfolio metrics present: False
- decision risk context: direction confidence 64 (谨慎参与), disagreement 46 (中分歧), upset 63 (中等爆冷风险)
- stake_size: decision stake 300; saved reason `方向把握 64 分，对应基础仓位 300；赔率价值 C，调整 +0。`
- portfolio_weight: top strategy stake 300; positive combo [('Home +1.5', 'handicap', 300, 0.5976332134078808, 0.08027006751687948)]
- hidden heuristics: risk_gate missing; portfolio score components missing; decision stake not derived directly from strategy score.

### 2026_06_25_Japan_Sweden_pre

- match: Japan vs Sweden
- scenario role: balanced match (50/50)
- strategy_score: 49 via top strategy `让球策略`
- implicit risk inputs: max_loss 1200, volatility 1098.81, concentration 0.00, risk_reward 0.85
- risk component observed: `53`; portfolio metrics present: True
- decision risk context: direction confidence 79 (中等把握), disagreement 21 (低分歧), upset 47 (中等爆冷风险)
- stake_size: decision stake 1200; saved reason `方向把握 79 分，对应基础仓位 900；赔率价值 A，调整 +300。`
- portfolio_weight: top strategy stake 1200; positive combo [('Home -0.5', 'handicap', 700, 0.4476137624861265, 0.0), ('Japan独赢', 'winner', 400, 0.2923862375138735, 0.0), ('波胆 2:1', 'correct_score', 100, 0.0475761346702652, 0.0)]
- hidden heuristics: risk_gate missing; decision stake not derived directly from strategy score.

### 2026_06_25_Ecuador_Germany_pre

- match: Ecuador vs Germany
- scenario role: low volatility favorite match
- strategy_score: 74 via top strategy `独赢策略`
- implicit risk inputs: max_loss 200, volatility 150.96, concentration 0.00, risk_reward 0.60
- risk component observed: `55`; portfolio metrics present: True
- decision risk context: direction confidence 57 (观望), disagreement 0 (低分歧), upset 52 (中等爆冷风险)
- stake_size: decision stake 200; saved reason `方向把握 57 分，对应基础仓位 200；赔率价值 C，调整 +0。`
- portfolio_weight: top strategy stake 200; positive combo [('Home +0.5', 'handicap', 100, 0.44304207119741096, 0.0), ('Germany独赢', 'winner', 100, 0.296957928802589, 0.0)]
- hidden heuristics: risk_gate missing; decision stake not derived directly from strategy score.

### 2026_06_24_Scotland_Brazil_pre

- match: Scotland vs Brazil
- scenario role: upset-prone match
- strategy_score: 73 via top strategy `独赢策略`
- implicit risk inputs: max_loss 1100, volatility 599.58, concentration 0.00, risk_reward 0.30
- risk component observed: `44`; portfolio metrics present: True
- decision risk context: direction confidence 76 (中等把握), disagreement 8 (低分歧), upset 60 (中等爆冷风险)
- stake_size: decision stake 1100; saved reason `方向把握 76 分，对应基础仓位 900；赔率价值 B，调整 +200。`
- portfolio_weight: top strategy stake 1100; positive combo [('Home +1.5', 'handicap', 800, 0.43738019169329073, 0.0), ('Brazil独赢', 'winner', 300, 0.30261980830670926, 0.0)]
- hidden heuristics: risk_gate missing; decision stake not derived directly from strategy score.

### 2026_06_21_New_Zealand_Egypt_pre

- match: New Zealand vs Egypt
- scenario role: low liquidity / incomplete odds match
- strategy_score: 44 via top strategy `只买最佳波胆`
- implicit risk inputs: max_loss 100, volatility 213.01, concentration 0.00, risk_reward 4.90
- risk component observed: `2`; portfolio metrics present: False
- decision risk context: direction confidence 0 (观望), disagreement 0 (低分歧), upset 47 (中等爆冷风险)
- stake_size: decision stake 100; saved reason `方向把握 0 分，对应基础仓位 0；赔率价值 C，调整 +0。`
- portfolio_weight: top strategy stake 100; positive combo [('Home +1.5', 'handicap', 100, 0.7400000000000001, 0.0)]
- hidden heuristics: risk_gate missing; portfolio score components missing; decision stake not derived directly from strategy score.

## Map Decision

The current map is partially observable but not explicit. It is sufficient for manual review, not sufficient for extraction or independent backtest simulation.