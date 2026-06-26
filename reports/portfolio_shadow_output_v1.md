# Portfolio Shadow Output v1

This report uses `modules/portfolio/shadow.py` to observe saved golden v2 portfolio behavior. The shadow module is not imported by runtime code.

## Generation Rule

- Input: `reports/golden_output_snapshot_v2.json`.
- Data files under `data/` were not written.
- Existing production logic was not modified or imported into `app.py`.
- Shadow allocation replay is observational and compares against saved golden output amounts.

## 2026_06_21_Tunisia_Japan_pre

- match: Tunisia vs Japan
- scenario role: high odds mismatch match
- final recommendation: Tunisia +1.5
- decision stake: 300
- positive combo stake: 300
- top strategy: 只买最佳波胆 / display 推荐组合 / score 62 / max loss 300
- top strategy saved stake: 300
- stake alignment: combo delta 0, top strategy delta 0

### Stake Distribution By Type

- correct_score: 300

### Top Strategy Items

- 波胆 0:1 / correct_score / amount 300 / path consistency 0.99 / weight 3.03

### Shadow Replay Against Saved Top Strategy

- 波胆 0:1 / correct_score: saved 300, shadow replay 300, delta 0

### Ranking To Capital Mapping

- rank 1: 只买最佳波胆 / display 推荐组合 / score 62 / stake 300 / max loss 300 / risk - / CS share -
- rank 2: 独赢策略 / display 第2组合 / score 60 / stake 300 / max loss 300 / risk - / CS share -
- rank 3: 赔率分布优化器 / display 第3组合 / score 60 / stake 300 / max loss 300 / risk - / CS share -
- rank 4: 让球策略 / display 第4组合 / score 59 / stake 300 / max loss 300 / risk - / CS share -
- rank 5: 独赢 + 让球 / display 第5组合 / score 58 / stake 300 / max loss 155 / risk - / CS share -
- rank 6: 让球 + 波胆 / display 第6组合 / score 58 / stake 300 / max loss 300 / risk - / CS share -
- rank 7: 独赢 + 波胆 / display 第7组合 / score 57 / stake 300 / max loss 300 / risk - / CS share -
- rank 8: 当前推荐组合 / display 第8组合 / score 41 / stake 300 / max loss 300 / risk - / CS share -

## 2026_06_25_Japan_Sweden_pre

- match: Japan vs Sweden
- scenario role: balanced match (50/50)
- final recommendation: Japan
- decision stake: 1200
- positive combo stake: 1200
- top strategy: 让球策略 / display 推荐组合 / score 49 / max loss 1200
- top strategy saved stake: 1200
- stake alignment: combo delta 0, top strategy delta 0

### Stake Distribution By Type

- handicap: 1200

### Top Strategy Items

- Home -0.5 / handicap / amount 1200 / path consistency 0.88 / weight 2.38

### Shadow Replay Against Saved Top Strategy

- Home -0.5 / handicap: saved 1200, shadow replay 1200, delta 0

### Ranking To Capital Mapping

- rank 1: 让球策略 / display 推荐组合 / score 49 / stake 1200 / max loss 1200 / risk - / CS share -
- rank 2: 独赢 + 让球 / display 第2组合 / score 48 / stake 1200 / max loss 1200 / risk - / CS share -
- rank 3: 让球 + 波胆 / display 第3组合 / score 48 / stake 1200 / max loss 1200 / risk - / CS share -
- rank 4: Conservative Portfolio / display 第4组合 / score 48 / stake 1200 / max loss 1200 / risk - / CS share -
- rank 5: 独赢策略 / display 第5组合 / score 47 / stake 1200 / max loss 1200 / risk - / CS share -
- rank 6: 独赢 + 波胆 / display 第6组合 / score 46 / stake 1200 / max loss 1200 / risk - / CS share -
- rank 7: 当前推荐组合 / display 第7组合 / score 44 / stake 1200 / max loss 1200 / risk - / CS share -
- rank 8: 只买最佳波胆 / display 第8组合 / score 40 / stake 1200 / max loss 1200 / risk - / CS share -

## 2026_06_25_Ecuador_Germany_pre

- match: Ecuador vs Germany
- scenario role: low volatility favorite match
- final recommendation: Ecuador +0.5
- decision stake: 200
- positive combo stake: 200
- top strategy: 独赢策略 / display 推荐组合 / score 74 / max loss 200
- top strategy saved stake: 200
- stake alignment: combo delta 0, top strategy delta 0

### Stake Distribution By Type

- winner: 200

### Top Strategy Items

- Germany独赢 / winner / amount 200 / path consistency 0.88 / weight 2.24

### Shadow Replay Against Saved Top Strategy

- Germany独赢 / winner: saved 200, shadow replay 200, delta 0

### Ranking To Capital Mapping

- rank 1: 独赢策略 / display 推荐组合 / score 74 / stake 200 / max loss 200 / risk - / CS share -
- rank 2: 独赢 + 波胆 / display 第2组合 / score 45 / stake 200 / max loss 200 / risk - / CS share -
- rank 3: 双波胆组合 / display 第3组合 / score 44 / stake 200 / max loss 200 / risk - / CS share -
- rank 4: 独赢 + 让球 / display 第4组合 / score 44 / stake 200 / max loss 40 / risk - / CS share -
- rank 5: 主路径波胆组合 / display 第5组合 / score 44 / stake 200 / max loss 200 / risk - / CS share -
- rank 6: Conservative Portfolio / display 第6组合 / score 44 / stake 200 / max loss 40 / risk - / CS share -
- rank 7: 让球 + 波胆 / display 第7组合 / score 43 / stake 200 / max loss 200 / risk - / CS share -
- rank 8: Tail Hedge Portfolio / display 第8组合 / score 42 / stake 200 / max loss 200 / risk - / CS share -

## 2026_06_24_Scotland_Brazil_pre

- match: Scotland vs Brazil
- scenario role: upset-prone match
- final recommendation: Scotland +1.5
- decision stake: 1100
- positive combo stake: 1100
- top strategy: 独赢策略 / display 推荐组合 / score 73 / max loss 1100
- top strategy saved stake: 1100
- stake alignment: combo delta 0, top strategy delta 0

### Stake Distribution By Type

- winner: 1100

### Top Strategy Items

- Brazil独赢 / winner / amount 1100 / path consistency 0.88 / weight 2.31

### Shadow Replay Against Saved Top Strategy

- Brazil独赢 / winner: saved 1100, shadow replay 1100, delta 0

### Ranking To Capital Mapping

- rank 1: 独赢策略 / display 推荐组合 / score 73 / stake 1100 / max loss 1100 / risk - / CS share -
- rank 2: Conservative Portfolio / display 第2组合 / score 53 / stake 1100 / max loss 710 / risk - / CS share -
- rank 3: 让球 + 波胆 / display 第3组合 / score 52 / stake 1100 / max loss 1100 / risk - / CS share -
- rank 4: 主路径波胆组合 / display 第4组合 / score 51 / stake 1100 / max loss 1100 / risk - / CS share -
- rank 5: Aggressive Portfolio / display 第5组合 / score 51 / stake 1100 / max loss 1100 / risk - / CS share -
- rank 6: 当前推荐组合 / display 第6组合 / score 50 / stake 1100 / max loss 840 / risk - / CS share -
- rank 7: Tail Hedge Portfolio / display 第7组合 / score 50 / stake 1100 / max loss 1100 / risk - / CS share -
- rank 8: 独赢 + 波胆 / display 第8组合 / score 47 / stake 1100 / max loss 1100 / risk - / CS share -

## 2026_06_21_New_Zealand_Egypt_pre

- match: New Zealand vs Egypt
- scenario role: low liquidity / incomplete odds match
- final recommendation: 观察为主
- decision stake: 100
- positive combo stake: 100
- top strategy: 只买最佳波胆 / display 推荐组合 / score 44 / max loss 100
- top strategy saved stake: 100
- stake alignment: combo delta 0, top strategy delta 0

### Stake Distribution By Type

- correct_score: 100

### Top Strategy Items

- 波胆 0:1 / correct_score / amount 100 / path consistency 0.87 / weight 1.55

### Shadow Replay Against Saved Top Strategy

- 波胆 0:1 / correct_score: saved 100, shadow replay 100, delta 0

### Ranking To Capital Mapping

- rank 1: 只买最佳波胆 / display 推荐组合 / score 44 / stake 100 / max loss 100 / risk - / CS share -
- rank 2: 双波胆组合 / display 第2组合 / score 44 / stake 100 / max loss 100 / risk - / CS share -
- rank 3: 独赢 + 波胆 / display 第3组合 / score 44 / stake 100 / max loss 100 / risk - / CS share -
- rank 4: 主路径波胆组合 / display 第4组合 / score 44 / stake 100 / max loss 100 / risk - / CS share -
- rank 5: 赔率分布优化器 / display 第5组合 / score 44 / stake 100 / max loss 100 / risk - / CS share -
- rank 6: 当前推荐组合 / display 第6组合 / score 42 / stake 100 / max loss 100 / risk - / CS share -
- rank 7: 让球策略 / display 第7组合 / score 42 / stake 100 / max loss 100 / risk - / CS share -
- rank 8: 独赢 + 让球 / display 第8组合 / score 42 / stake 100 / max loss 100 / risk - / CS share -
