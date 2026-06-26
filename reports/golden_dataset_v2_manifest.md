# Golden Dataset v2 Manifest

This report defines the multi-scenario golden output set used before portfolio/backtest extraction. It is analysis-only and uses existing saved snapshots without recomputation.

## Dataset Selection Rule

- Source roots inspected: `data/history/` and `data/worldcup2026/`.
- Selected snapshots are existing pre-match JSON files under `data/history/`.
- Data files were read only; no `data/history` or `data/worldcup2026` files were written.
- Each selected match has a saved output snapshot sufficient to serialize odds, strategy, portfolio, and decision outputs where available.

## Selected Matches

### 2026_06_21_Tunisia_Japan_pre

- match: Tunisia vs Japan
- source: `data/history/2026_06_21_Tunisia_Japan_pre.json`
- source sha256: `161e299a5464b0b5e07951ed758e1259b4076cc2b4015657093bc02d9dfc8f1e`
- scenario role: high odds mismatch match
- selection reason: Has 58 saved actual_odds items and the largest observed absolute EV lift among candidate snapshots; final recommendation diverges toward Tunisia +1.5 while win market direction favors Japan.
- odds found: True
- actual odds item count: 58
- strategy count: 10
- top strategy: 只买最佳波胆 / display 推荐组合 / score 62 / max loss 300
- final recommendation: Tunisia +1.5
- recommended stake: 300
- participation advice: 仅观察
- probability path: favorite 日本 / main path 日本小胜（1球）

### 2026_06_25_Japan_Sweden_pre

- match: Japan vs Sweden
- source: `data/history/2026_06_25_Japan_Sweden_pre.json`
- source sha256: `072ea635726bfd7ce5044b543cf0d8087b380e1b95683db1b061bbbabd2dfaba`
- scenario role: balanced match (50/50)
- selection reason: Saved market probability centers near Japan 50.9% with low market disagreement and compressed strategy scores.
- odds found: True
- actual odds item count: 0
- strategy count: 12
- top strategy: 让球策略 / display 推荐组合 / score 49 / max loss 1200
- final recommendation: Japan
- recommended stake: 1200
- participation advice: 小仓参与
- probability path: favorite 日本 / main path 平局区间

### 2026_06_25_Ecuador_Germany_pre

- match: Ecuador vs Germany
- source: `data/history/2026_06_25_Ecuador_Germany_pre.json`
- source sha256: `9775cb19df3153669ced752c07a2d80f01cc2847e4bc9b58459a6cadfca17762`
- scenario role: low volatility favorite match
- selection reason: Saved top strategy has low max_loss around 200 with a Germany favorite path and small recommended stake, creating a low-exposure lock case.
- odds found: True
- actual odds item count: 0
- strategy count: 13
- top strategy: 独赢策略 / display 推荐组合 / score 74 / max loss 200
- final recommendation: Ecuador +0.5
- recommended stake: 200
- participation advice: 仅观察
- probability path: favorite 德国 / main path 德国小胜（1球）

### 2026_06_24_Scotland_Brazil_pre

- match: Scotland vs Brazil
- source: `data/history/2026_06_24_Scotland_Brazil_pre.json`
- source sha256: `05a2479eeef95952dfba17d3fe7feb5e5f23e9fff0fd4d0959048ea25bc9e51c`
- scenario role: upset-prone match
- selection reason: Brazil is a strong favorite, but the saved final recommendation is Scotland +1.5 and upset_index is elevated, locking favorite-vs-handicap tension.
- odds found: True
- actual odds item count: 0
- strategy count: 12
- top strategy: 独赢策略 / display 推荐组合 / score 73 / max loss 1100
- final recommendation: Scotland +1.5
- recommended stake: 1100
- participation advice: 小仓参与
- probability path: favorite 巴西 / main path 巴西赢2球

### 2026_06_21_New_Zealand_Egypt_pre

- match: New Zealand vs Egypt
- source: `data/history/2026_06_21_New_Zealand_Egypt_pre.json`
- source sha256: `97b8f865a304e222e432cf87bf5c704d7ac043d4a71c3780ba30c41d16520510`
- scenario role: low liquidity / incomplete odds match
- selection reason: Saved odds_found is false, market comparison data is missing, and final advice is observation/abandonment while strategies still exist.
- odds found: False
- actual odds item count: 0
- strategy count: 9
- top strategy: 只买最佳波胆 / display 推荐组合 / score 44 / max loss 100
- final recommendation: 观察为主
- recommended stake: 100
- participation advice: 放弃
- probability path: favorite 埃及 / main path 埃及小胜（1球）
