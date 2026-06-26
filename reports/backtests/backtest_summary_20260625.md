# Backtest Summary 20260625

## Model Version

Current model from saved snapshots when available; current replay script only settles missing saved settlements.

## Data Source

- Primary: `data/history/*_pre.json` and `data/history/*_post.json`
- Secondary: `data/worldcup2026/*/pre_match.json` and `post_match.json`
- My Portfolio: included when present in saved post-match settlement

## Overall PnL

- Tested Matches: 17
- Portfolio Rows: 161
- Total Stake: 144500.0
- Net Profit: -19874.01
- Average ROI: -13.8%
- Win Rate: 43.5%
- Rank #1 Profit Rate: 52.4%
- Best Portfolio Style: Aggressive
- Worst Portfolio Style: System

## Tested Matches

- Switzerland vs Bosnia and Herzegovina
- 南非 vs 韩国
- 厄瓜多尔 vs 库拉索
- 土耳其 vs 巴拉圭
- 巴西 vs 海地
- 德国 vs 科特迪瓦
- 捷克 vs 墨西哥
- 摩洛哥 vs 海地
- 波黑 vs 卡塔尔
- 瑞士 vs 加拿大
- 突尼斯 vs 日本
- 美国 vs 澳大利亚
- 苏格兰 vs 巴西
- 苏格兰 vs 摩洛哥
- 荷兰 vs 瑞典

## Matches Where Rank #1 Failed

- 土耳其 vs 巴拉圭 / 推荐组合 / 0:1 / -100.0
- 土耳其 vs 巴拉圭 / 推荐组合 / 0:1 / -100.0
- 巴西 vs 海地 / 推荐组合 / 3:0 / -100.0
- 厄瓜多尔 vs 库拉索 / 推荐组合 / 0:0 / -1800.0
- 德国 vs 科特迪瓦 / 推荐组合 / 2:1 / -1800.0
- 土耳其 vs 巴拉圭 / 推荐组合 / 0:1 / -1500.0
- 土耳其 vs 巴拉圭 / 推荐组合 / 0:1 / -351.69
- 捷克 vs 墨西哥 / 推荐组合 / 0:3 / -100.0
- 摩洛哥 vs 海地 / 推荐组合 / 4:2 / -94.0
- 南非 vs 韩国 / 推荐组合 / 1:0 / -300.0

## Matches Where My Portfolio Beat System

- 美国 vs 澳大利亚
- 捷克 vs 墨西哥

## Common Failure Patterns

- 组合归零风险触发: 65
- 强队赢但一球偏差导致失败: 34
- 打平路径造成组合失效: 10
- 波胆路径过度集中或比分偏离: 3
- 一般方向或赔率路径失败: 1

## Skipped Matches / Missing Data

- France vs Senegal: missing final score
- England vs Croatia: missing final score
- Portugal vs Democratic Republic of the Congo: missing final score
- 2026_06_18_Canada_Qatar: missing pre or post snapshot
- 巴西 vs 海地: missing saved strategies and settlements
- Scotland vs Morocco: missing saved strategies and settlements
- Turkey vs Paraguay: missing final score
- USA vs Australia: missing final score
- Ecuador vs Curaçao: missing final score
- Türkiye vs Paraguay: missing final score
- United States vs Australia: missing final score
- 2026_06_21_Belgium_Iran: missing pre or post snapshot
- 2026_06_21_Ecuador_Cura_ao: missing pre or post snapshot
- 2026_06_21_New_Zealand_Egypt: missing pre or post snapshot
- 2026_06_21_Spain_Saudi_Arabia: missing pre or post snapshot
- 2026_06_21_Tunisia_Japan: missing pre or post snapshot
- 2026_06_23_Colombia_Democratic_Republic_of_the_Congo: missing pre or post snapshot
- Colombia vs Democratic Republic of the Congo: missing final score
- Czech Republic vs Mexico: missing final score
- 2026_06_25_Cura_ao_Ivory_Coast: missing pre or post snapshot
- Curaçao vs Ivory Coast: missing final score
- 厄瓜多尔 vs 德国: missing final score
- 日本 vs 瑞典: missing final score
- Paraguay vs Australia: missing final score
- 突尼斯 vs 荷兰: missing final score
- 2026_06_25_Turkey_United_States: missing pre or post snapshot
- Turkey vs United States: missing final score

## Recommended Model Fixes

- Do not tune weights from this report alone; first review per-match details.
- Compare third-round matches with Qualification Pressure enabled versus prior saved rankings.
- Check whether Tail Hedge lowers max loss or only adds correct-score noise.
- Check whether Conservative portfolios outperform Aggressive portfolios in draw-acceptable and qualified-favorite matches.
- Add more settled matches before changing Portfolio Score weights.

CSV: `/Users/zijianchen/Documents/Codex/2026-06-14/1-vs-2-polymarket-3-4/worldcup-analyzer/reports/backtests/backtest_results_20260625.csv`
