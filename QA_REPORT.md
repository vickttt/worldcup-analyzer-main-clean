# QA Report

Updated: 2026-06-25 18:20 CST

## Report Readability Small Fix 验收

Overall Status: PASS

本轮未调整 Portfolio Score 权重，未新增 API，未重构 Portfolio Engine。修复范围限定在报告解释层、盘口展示可读性和导出校验。

## Report Readability Verification Summary

- 推荐组合导出不再显示 `推荐组合：推荐组合` 占位。
- 组合摘要显示真实组合名称、核心投注、组合风格、综合评分、风险门槛结果、风险等级、第一推荐资格和通过/阻碍原因。
- 风险门槛结果与风险等级已经拆分显示。
- 亚洲让球导出将 Home/Away 映射为真实球队名称。
- 亚洲让球和大小球导出采用“核心摘要 → 主流盘口附近 → 完整明细折叠”的结构。
- 数据质量提示新增用户真实赔率状态。
- 六场验证报告生成：`reports/validation/report_readability_validation_20260625.md`。

## Report Readability Test Output

```text
.venv/bin/python -m py_compile app.py modules/portfolio_engine.py modules/game_behavior_engine.py modules/user_odds.py modules/market_utils.py modules/betting_opinion.py modules/report_generator.py
Result: passed, no output.

.venv/bin/python scripts/validate_report_exports.py
Turkey vs United States: PASS
Ecuador vs Germany: PASS
Curaçao vs Ivory Coast: PASS
Japan vs Sweden: PASS
Tunisia vs Netherlands: PASS
Paraguay vs Australia: PASS

.venv/bin/python scripts/test_portfolio_engine.py
portfolio_engine tests passed

.venv/bin/python -m pytest
23 passed
```

## Qualification Pressure Engine v1 验收

Overall Status: PASS / PARTIAL

本轮完成最小可用版：第三轮小组赛出线压力已进入 Scenario Engine、Coverage Engine、Match Investment Score 与 Portfolio Ranking。当前仍是人工 seed + 规则引擎，尚未完整自动计算所有小组实时出线概率。

## Qualification Verification Summary

- Python 编译检查通过。
- `qualification_context_2026_06_24.json` JSON 校验通过。
- Portfolio Engine 回归测试通过。
- `pytest` 运行通过，17 个测试全部通过。

## Qualification Requirement Matrix

| 验收项 | 结果 | 证据 | 说明 |
| --- | --- | --- | --- |
| Qualification Pressure Score | PASS | `modules/game_behavior_engine.py`, `data/worldcup2026/qualification_context_2026_06_24.json` | 已支持 0-5 分：已出局/无战意、已出线轮换、平局可接受、必须不败、必须赢、必须大胜。 |
| Match Pressure Type | PASS | `modules/game_behavior_engine.py` | 已分类 qualified_favorite_vs_must_win_underdog、both_draw_acceptable、direct_second_place_battle、must_win_vs_must_win、qualified_vs_qualified、favorite_must_win、dead_rubber_or_low_motivation。 |
| Behavior Adjustments | PASS | `modules/game_behavior_engine.py` | 输出 deep_handicap、small_win、underdog_goal、draw、over/under、late_volatility、rotation、tempo、chaos 等结构化因子。 |
| Scenario / Coverage 接入 | PASS | `modules/result_distribution.py`, `modules/portfolio_engine.py` | 结果分布和 score grid 会按出线压力重新加权。 |
| Match Investment Score 接入 | PASS | `modules/portfolio_engine.py` | External Risk 和 Data Quality / Timing 已纳入 qualification context。 |
| Portfolio Ranking Pressure Fit | PASS | `modules/portfolio_engine.py`, `app.py` | 排行表新增 Pressure Fit，组合详情展示适配原因和缺失覆盖。 |
| Core Decision UI | PASS | `app.py` | Core Decision 页面新增 Qualification & Game Behavior 区域。 |
| 自动出线概率计算 | PARTIAL | `data/worldcup2026/qualification_context_2026_06_24.json` | 当前先用人工 seed，后续再从 API-Football standings 自动化。 |

## Qualification Test Output

Compile:

```text
.venv/bin/python -m py_compile app.py modules/portfolio_engine.py modules/user_odds.py modules/game_behavior_engine.py modules/result_distribution.py
```

Result: passed, no output.

Regression:

```text
.venv/bin/python scripts/test_portfolio_engine.py
portfolio_engine tests passed
```

Pytest:

```text
.venv/bin/python -m pytest
============================= test session starts ==============================
collected 17 items
scripts/test_portfolio_engine.py .................                       [100%]
============================== 17 passed in 0.14s ==============================
```

## Qualification Sample Cases

| Match | Pressure Type | Expected Adjustment |
| --- | --- | --- |
| Ecuador vs Germany | qualified_favorite_vs_must_win_underdog | 德国深盘风险上升，德国小胜和厄瓜多尔进球尾部上升。 |
| Switzerland vs Canada | both_draw_acceptable | 平局和小球权重上升，大胜路径下降。 |
| Bosnia and Herzegovina vs Qatar | must_win_vs_must_win | 平局价值下降，后期开放和混乱路径上升。 |
| Morocco vs Haiti | favorite_must_win | 摩洛哥方向保留，但 2:0 / 3:0 / 3:1 优先于极端大胜。 |
| Japan vs Sweden | direct_second_place_battle | 前期谨慎、平局/窄比分和瑞典进球尾部更重要。 |
| Panama vs England | favorite_must_win | 英格兰方向保留，但深盘不自动强化。 |

## Model Documentation and Backtest Framework 验收

Overall Status: PASS / PARTIAL

本轮暂停调参，完成当前模型文档化和第一版历史回测入口。回测框架能扫描历史 pre/post 快照、输出 CSV 和 Markdown 报告。当前仍为 PARTIAL，因为脚本优先复用已保存 settlement；缺少完整 pre/post 或缺少保存策略的比赛会跳过，不会编造数据。

## Backtest Verification Summary

- `docs/MODEL_ALGORITHM.md` 已创建，覆盖输入、数据源、盘口解析、分盘结算、用户赔率、Coverage、Portfolio Score、Ranking、My Portfolio、赛后结算和局限。
- `docs/GAME_BEHAVIOR_MODEL.md` 已创建，并明确当前状态为 IMPLEMENTED / PARTIAL。
- `scripts/backtest_portfolio_engine.py` 已创建，可运行并输出报告。
- `reports/backtests/backtest_summary_20260625.md` 已生成。
- `reports/backtests/backtest_results_20260625.csv` 已生成。

## Backtest Requirement Matrix

| 验收项 | 结果 | 证据 | 说明 |
| --- | --- | --- | --- |
| 模型算法文档 | PASS | `docs/MODEL_ALGORITHM.md` | 已写明 Portfolio Ranking 真实流程和权重。 |
| Match Investment Score 权重核对 | PASS | `docs/MODEL_ALGORITHM.md`, `modules/portfolio_engine.py` | 20/25/20/20/10/5 与代码一致。 |
| Game Behavior 文档 | PASS | `docs/GAME_BEHAVIOR_MODEL.md` | 明确 IMPLEMENTED / PARTIAL，没有误报全自动完成。 |
| 回测脚本 | PASS | `scripts/backtest_portfolio_engine.py` | 可扫描历史快照并输出报告。 |
| 不覆盖历史 snapshot | PASS | 脚本只读 `data/history` / `data/worldcup2026`，只写 `reports/backtests` | 没有写回历史快照。 |
| 不新增 API 数据源 | PASS | 本轮只读本地文件 | 没有网络抓取。 |
| 不调参 | PASS | 未改 Portfolio Score 权重 | 只文档化和回测。 |
| 初始回测报告 | PASS | `reports/backtests/backtest_summary_20260625.md` | 扫描 17 场、161 条组合结果。 |
| 缺数据记录 | PASS | 回测报告 Skipped Matches | 缺 pre/post、缺 final score、缺 strategy 的比赛均记录原因。 |

## Backtest Output

```text
.venv/bin/python scripts/backtest_portfolio_engine.py
Backtest matches: 17
Portfolio rows: 161
Overall ROI: -13.8%
Report: reports/backtests/backtest_summary_20260625.md
CSV: reports/backtests/backtest_results_20260625.csv
```

## Backtest Initial Findings

- Aggregate ROI in available replay sample: -13.8%.
- Portfolio-row win rate: 43.5%.
- Rank #1 profit rate: 52.4%.
- Detected failure patterns:
  - 组合归零风险触发: 65
  - 强队赢但一球偏差导致失败: 34
  - 打平路径造成组合失效: 10
  - 波胆路径过度集中或比分偏离: 3

Conclusion: do not tune immediately. Review the backtest report and per-match failures first.

## Backtest Attribution Review 验收

Overall Status: PASS / PARTIAL

本轮只做归因审计，不调参、不新增模型、不新增数据源。归因脚本读取 `backtest_summary_20260625.md` 和 `backtest_results_20260625.csv`，并结合历史 post snapshot 中的组合审计信息生成 Markdown 与 CSV。

## Attribution Verification Summary

- `scripts/backtest_attribution.py` 已创建。
- `reports/backtests/backtest_attribution_20260625.md` 已生成。
- `reports/backtests/backtest_attribution_20260625.csv` 已生成。
- Attribution rows: 161。
- Rank #1 failures: 10。
- 本轮未修改 Portfolio Score 权重。

## Attribution Requirement Matrix

| 验收项 | 结果 | 证据 | 说明 |
| --- | --- | --- | --- |
| 读取 summary / CSV | PASS | `scripts/backtest_attribution.py` | 读取既有回测结果，不重新抓 API。 |
| Portfolio style 统计 | PASS | `backtest_attribution_20260625.md` | 输出 stake、profit、ROI、win rate、max loss、best/worst match。 |
| Rank #1 失败审计 | PASS | `backtest_attribution_20260625.md` | 列出 Rank #1 亏损行和 failure pattern。 |
| 强队不穿盘审计 | PASS / PARTIAL | `backtest_attribution_20260625.md` | 已输出相关失败；部分历史行缺少具体盘口 detail，handicap_depth 可能为空。 |
| 弱队进球尾部审计 | PASS | `backtest_attribution_20260625.md` | 输出 clean-sheet 被破坏场景。 |
| 平局路径审计 | PASS | `backtest_attribution_20260625.md` | 输出 draw-path missed 场景。 |
| Qualification Pressure 审计 | PARTIAL | `backtest_attribution_20260625.md` | 多数历史 snapshot 生成早于 pressure metadata，因此 pressure type 为 unknown。 |
| My Portfolio vs System | PASS | `backtest_attribution_20260625.md` | 输出用户组合和系统首选对比。 |
| 不调参 | PASS | 文件 diff | 未改 Portfolio Score 权重或推荐逻辑。 |

## Attribution Output

```text
.venv/bin/python scripts/backtest_attribution.py
Attribution rows: 161
Rank #1 failures: 10
Top failure patterns:
- low_odds_false_safety: 65
- correct_score_over_concentrated: 42
- market_direction_wrong: 38
- underdog_goal_broke_clean_sheet: 20
- draw_path_missed: 10
- over_under_wrong: 3
Best style: Aggressive (-351)
Worst style: System (-15297)
```

Conclusion: next round should review failure rows before tuning. Do not change Portfolio Score weights from aggregate ROI alone.

## 本轮验收审计

Overall Status: PARTIAL

本轮继续修复上一次验收报告中的 PARTIAL 项。结论是：关键阻塞项已经推进到可验证状态；Match Investment Score、Coverage Efficiency、用户真实赔率 A/B Ranking、系统推荐组合最多4个波胆已经达到 PASS。Coverage Engine 概率校准和 Directional Odds Value 噪音过滤仍属于最小可用版，保留 PARTIAL。

## Verification Summary

- Python 编译检查通过。
- Portfolio Engine 回归测试通过。
- 本地网页服务可访问：`http://localhost:8502/` 返回 `HTTP/1.1 200 OK`。
- `pytest` 已安装并运行通过。

## Requirement Matrix

| 验收项 | 结果 | 证据 | 说明 |
| --- | --- | --- | --- |
| Match Investment Score | PASS | `modules/portfolio_engine.py:690`, `app.py:5104` | 明确使用 20/25/20/20/10/5 权重，Polymarket、API盘口完整度、用户真实赔率均进入 Data Quality / Timing。 |
| 亚洲让球分数盘解析 | PASS | `modules/portfolio_engine.py:37`, `scripts/test_portfolio_engine.py` | 已覆盖 `-1/2`, `-0.5/1`, `-1/1.5`, `-1.5/2`, `-2/2.5`, `-2.5/3` 及正数方向。 |
| 分盘结算 | PASS | `modules/portfolio_engine.py:91`, `scripts/test_portfolio_engine.py` | `-1/1.5`, `-2.5/3`, `+2/2.5` 按拆腿结算，测试通过。 |
| bet_id 去重 | PASS | `modules/portfolio_engine.py:141`, `modules/portfolio_engine.py:161` | 同一盘口不同写法归一成同一 bet_id；本轮修复后重复投注会合并角色标签。 |
| portfolio 去重 | PASS | `modules/portfolio_engine.py:186`, `app.py:4744` | 组合按归一后的投注集合去重，不再因角色标签或盘口写法重复。 |
| Directional Odds Value 噪音过滤 | PARTIAL | `modules/portfolio_engine.py:485` | 已输出 price edge、scenario alignment、plausibility、market support、noise penalty、weighted edge；反向剧本不再拉高主方向价值。但仍未接入盘口流动性。 |
| Coverage Engine | PARTIAL | `modules/portfolio_engine.py:250`, `modules/portfolio_engine.py:368` | 已加入 raw implied probability、devig probability、handicap alignment、total alignment、final scenario weight；仍是最小校准版。 |
| Coverage Efficiency | PASS | `modules/portfolio_engine.py:561` | 已输出 base/new EV、ROI、max loss、zero risk、one-goal risk、coverage gain、stake cost、penalty 和 recommendation。 |
| 新 Portfolio Score | PASS | `modules/portfolio_engine.py:548`, `app.py:3279` | 最终排行使用统一评分组件，分数不再全部为 100。 |
| Portfolio Ranking UI | PASS | `app.py:4826` | 已包含组合名称、主剧本、让球资产、大小球资产、波胆资产、EV、ROI、最大亏损、剧本一致性、综合评分等列。 |
| 用户组合与系统组合同规则评分 | PASS | `app.py:5171`, `app.py:5293` | `我的组合` 通过 `evaluate_strategy` 进入同一个排序列表。 |
| 波胆最多 4 个 | PASS | `app.py:2888`, `modules/portfolio_engine.py:614`, `scripts/test_portfolio_engine.py` | Conservative / Main Scenario / Aggressive / Tail Hedge 均通过测试，系统推荐组合最多4个波胆；用户组合超过4个只扣 Simplicity。 |
| 实际用户赔率影响排序 | PASS | `scripts/test_portfolio_engine.py` | A/B 测试证明主方向赔率变好会改变排名；极端噪音赔率不会误导主推荐。 |

## Bugs Found

1. `compute_match_investment_score` 缺少 Polymarket / API完整度 / 用户赔率的数据质量权重。
2. `compute_coverage_efficiency` 缺少 EV/ROI/max loss/zero risk 增量。
3. 弱队简称如 `Saudi win` 没有被识别为反向剧本噪音。
4. `pytest` 此前未安装；本轮已安装并加入 `requirements-dev.txt`。

## Fixes Applied

- `Match Investment Score` 加入固定权重：Market Clarity 20%、Scenario Clarity 25%、Directional Odds Value 20%、Coverage Quality 20%、External Risk 10%、Data Quality / Timing 5%。
- Data Quality / Timing 显式纳入 Polymarket 完整性、API赔率完整性、用户真实赔率输入情况和数据时点。
- `Coverage Efficiency` 补齐 EV/ROI/max loss/zero risk/coverage/penalty/recommendation 完整输出。
- `Coverage Efficiency` 支持 `Replace`，用于识别更浅让球盘替代深盘的保险价值。
- `Directional Odds Value` 增加 price edge、scenario alignment、plausibility、market support、noise penalty 和 weighted edge 明细。
- 弱队独赢或反向波胆高赔率会被标记为 Noise，不再拉高主方向价值。
- `build_score_scenario_grid` 增加去水概率、盘口一致性、大小球一致性与最终场景权重字段。
- 回归测试新增 Coverage Efficiency 三案例、用户赔率 A/B Ranking、系统组合波胆数量扫描、Match Investment Score 数据质量验证。

## Test Output

Compile:

```text
.venv/bin/python -m py_compile app.py modules/portfolio_engine.py modules/user_odds.py
```

Result: passed, no output.

Regression:

```text
.venv/bin/python scripts/test_portfolio_engine.py
Coverage Efficiency Cases
Spain deep handicap insurance {'recommendation': 'Replace', 'ev_delta': 77.62, 'roi_delta': 0.0076, 'zero_risk_delta': 0.0, 'one_goal_reduction': 0, 'score': 100}
Germany one-goal tolerance {'recommendation': 'Replace', 'ev_delta': 122.56, 'roi_delta': -0.0519, 'zero_risk_delta': 0.0, 'one_goal_reduction': 0, 'score': 78}
Noise correct score {'recommendation': 'Do Not Add', 'ev_delta': 80.34, 'roi_delta': 0.0419, 'zero_risk_delta': -0.0225, 'one_goal_reduction': 0, 'score': 0}

A/B Ranking Cases
Before: [('Conservative Portfolio', 59), ('Main Scenario Portfolio', 58)]
After: [('Main Scenario Portfolio', 63), ('Conservative Portfolio', 59)]
Noise: 41 0 ['2:3: 偏离主剧本，作为噪音价值剔除', 'Saudi win: 偏离主剧本，作为噪音价值剔除']

Correct Score Count Scan
Conservative Portfolio 2 PASS
Main Scenario Portfolio 4 PASS
Aggressive Portfolio 4 PASS
Tail Hedge Portfolio 4 PASS

Match Investment Score
Complete: {'score': 71, 'rating': '可小仓参与', ... 'Data Quality / Timing': 97}
Incomplete: {'score': 69, 'rating': '可小仓参与', ... 'Data Quality / Timing': 60}
portfolio_engine tests passed
```

Pytest:

```text
.venv/bin/python -m pytest
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/zijianchen/Documents/Codex/2026-06-14/1-vs-2-polymarket-3-4/worldcup-analyzer
collected 9 items

scripts/test_portfolio_engine.py .........                               [100%]

============================== 9 passed in 0.22s ===============================
```

Local Web:

```text
curl -I http://localhost:8502/
HTTP/1.1 200 OK
```

## Settlement Samples

| 输入 | 比分 | 结果 |
| --- | --- | --- |
| Home -1/1.5, odds 2.05, stake 100 | 2:0 | +105 |
| Home -1/1.5, odds 2.05, stake 100 | 1:0 | -50 |
| Home -1/1.5, odds 2.05, stake 100 | 0:0 | -100 |
| Home -2.5/3, odds 2.01, stake 100 | 4:0 | +101 |
| Home -2.5/3, odds 2.01, stake 100 | 3:0 | +50.5 |
| Home -2.5/3, odds 2.01, stake 100 | 2:0 | -100 |
| Away +2/2.5, odds 1.90, stake 100 | 2:0 | +45 |
| Away +2/2.5, odds 1.90, stake 100 | 3:0 | -100 |

## Example Ranking

Synthetic Spain vs Saudi Arabia test:

| Portfolio | Score | EV | Main | Adjacent | Zero Risk |
| --- | ---: | ---: | ---: | ---: | ---: |
| Tail Hedge Portfolio | 81 | +37.1% | 100% | 100% | 0% |
| Conservative Portfolio | 75 | +48.7% | 100% | 63% | 18% |
| Main Scenario Portfolio | 70 | +40.3% | 100% | 31% | 34% |
| Aggressive Portfolio | 70 | +28.3% | 100% | 31% | 34% |

Directional Odds Value sample:

```text
Spain 3:0: 主方向权重后价差 -8.0%
Spain -2.5: 主方向权重后价差 +6.0%
Saudi 2:3: 偏离主剧本，作为噪音价值剔除
```

## Remaining Risks

1. Coverage Engine 仍是最小可用校准版，未来需要更严谨的盘口联合概率模型。
2. Directional Odds Value 噪音过滤仍是启发式，未来可加入盘口流动性、博彩公司数量和价格稳定性。
3. 用户手动输入超过 4 个波胆时，目前是扣 Simplicity，不是阻断。
4. `pytest` 已配置为开发测试依赖；后续仍需继续增加更多真实比赛回归用例。

## Files Updated By This Audit

- `modules/portfolio_engine.py`
- `scripts/test_portfolio_engine.py`
- `QA_REPORT.md`
- `CHANGELOG.md`
- `GPT_CONTEXT.md`
- `LATEST.md`

---

## Constraint Layer QA - 2026-06-25

### Scope

This QA pass validates risk constraints and portfolio generation rules. It does not validate Portfolio Score weight tuning because weights were intentionally kept unchanged.

### Changes Checked

- `portfolio_risk_gate`
- `correct_score_exposure_control`
- `generate_portfolio_templates_by_pressure`
- `rank1_eligibility_check`
- `compute_portfolio_marginal_utility`

### Requirement Matrix

| Requirement | Status | Notes |
| --- | --- | --- |
| Portfolio Score weights unchanged | PASS | Existing 15/20/20/15/10/10/10 weights were not modified. |
| Zero Risk upgraded to hard Rank #1 gate | PASS | Failed gate portfolios can display but cannot be official Rank #1 unless all fail. |
| Correct Score cannot dominate main recommendation | PASS | Stake-share limits and dependency checks are active. |
| Qualification Pressure changes portfolio generation | PASS | Pressure templates are added for key pressure types. |
| Rank #1 eligibility beyond raw score | PASS | Risk gate, exposure, pressure fit, coverage and noise blockers are checked. |
| Coverage Efficiency supports structural replacement review | PASS | Marginal utility rows compare deep-to-shallow and clean-sheet-to-underdog-goal variants. |
| Before / after backtest comparison | PASS / PARTIAL | Report generated; historical aggregate unchanged because saved portfolios were not regenerated. |

### Test Output

```text
.venv/bin/python -m py_compile app.py modules/portfolio_engine.py modules/game_behavior_engine.py modules/user_odds.py
passed

.venv/bin/python scripts/test_portfolio_engine.py
portfolio_engine tests passed

.venv/bin/python -m pytest
21 passed in 0.25s

.venv/bin/python scripts/backtest_portfolio_engine.py
Backtest matches: 17
Portfolio rows: 161
Overall ROI: -13.8%

.venv/bin/python scripts/backtest_attribution.py
Rank #1 failures: 10
Top failure patterns:
- low_odds_false_safety: 65
- correct_score_over_concentrated: 42
- market_direction_wrong: 38
```

### Constraint Comparison

- Report: `reports/backtests/backtest_constraint_comparison_20260625.md`
- CSV: `reports/backtests/backtest_constraint_comparison_20260625.csv`

### Remaining Risks

1. Current backtest does not fully replay newly generated portfolios from raw odds, so aggregate ROI remains unchanged.
2. Some historical pressure metadata is missing, so pressure-template benefit must be validated on future saved matches.
3. Constraint thresholds are now structural rules, but still need post-match replay validation before any scoring-weight tuning.

---

## Report Explanation Layer QA - 2026-06-25

### Scope

This QA pass validates the Turkey vs United States Markdown report explanation layer. It does not tune Portfolio Score weights, add APIs, or regenerate historical snapshots.

### Requirement Matrix

| Requirement | Status | Notes |
| --- | --- | --- |
| Match Overview no longer exports `- vs -` | PASS | New report shows `Turkey vs United States`. |
| Match Direction separated from coverage assets | PASS | United States is Match Direction; Turkey +0.5 is Coverage / Insurance Candidate. |
| Asian Handicap center filters outliers | PASS | Report flags 73 possible outlier handicap rows and centers around United States -0.5 / -0.25. |
| Total Center avoids mechanical Lean Over 2.5 | PASS | Report shows Total Center `2.5-2.75`. |
| Value Analysis scope is winner market only | PASS | Report section is titled Winner Market Value. |
| Confidence split | PASS | Report shows Market Direction Confidence, Betting Confidence, and Data Quality. |
| Data Quality Notes | PASS | Missing lineups, handicap outliers, Polymarket scope, and injury ambiguity are listed. |

### Test Output

```text
.venv/bin/python -m py_compile app.py modules/portfolio_engine.py modules/game_behavior_engine.py modules/user_odds.py modules/market_utils.py modules/betting_opinion.py modules/report_generator.py
passed

.venv/bin/python scripts/test_portfolio_engine.py
portfolio_engine tests passed

.venv/bin/python -m pytest
23 passed in 0.25s
```

### Exported Report

- `outputs/reports/Turkey_vs_United_States_20260625_222539.md`

---

## Global Report Export QA - 2026-06-25

### Scope

This QA pass validates that Betting Opinion v2, fixture metadata, Chinese labels, handicap-center detection, total-center detection, winner-market-scoped Value Analysis, confidence split, Data Quality Notes, and Portfolio Eligibility wording are global across selected June 25 matches.

### Matches Checked

- Turkey vs United States
- Ecuador vs Germany
- Curaçao vs Ivory Coast
- Japan vs Sweden
- Tunisia vs Netherlands
- Paraguay vs Australia

### Validation Report

- `reports/validation/report_export_validation_20260625.md`

### Requirement Matrix

| Requirement | Status | Notes |
| --- | --- | --- |
| Betting Opinion v2 global | PASS | All six generated reports contain 比赛主方向 / 让球盘口方向 / 覆盖 / 保险候选 / 进球数观点 / 比赛投资价值. |
| Chinese user-facing labels | PASS | Report sections and Portfolio Ranking columns now use Chinese user-facing names. |
| Fixture metadata complete | PASS | Six-match validation passed overview checks for teams, competition, stage, kickoff, and venue. |
| Handicap center global | PASS | Six matches produced handicap centers and coverage candidates; same-sign favorite handicap rows are normalized for center detection. |
| Total center global | PASS | Six matches produced total-center ranges instead of mechanical Lean Over 2.5. |
| Winner Market Value scope | PASS | Value Analysis is scoped to 胜平负市场价值. |
| Confidence split | PASS | Reports show 市场方向置信度 / 投注信心 / 数据质量. |
| Data Quality Notes | PASS | Reports include 数据质量提示. |
| Portfolio Eligibility wording | PASS | Reports no longer use "Available in Portfolio Ranking details"; page export passes actual top strategy when generated through Streamlit. |

### Test Output

```text
.venv/bin/python -m py_compile app.py modules/portfolio_engine.py modules/game_behavior_engine.py modules/user_odds.py modules/market_utils.py modules/betting_opinion.py modules/report_generator.py modules/worldcup_db.py scripts/validate_report_exports.py
passed

.venv/bin/python scripts/test_portfolio_engine.py
portfolio_engine tests passed

.venv/bin/python -m pytest
23 passed in 0.16s

.venv/bin/python scripts/validate_report_exports.py
All six validation rows PASS; report saved to reports/validation/report_export_validation_20260625.md
```
