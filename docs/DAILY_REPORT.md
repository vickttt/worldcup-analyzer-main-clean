# Daily Report

## 2026-06-26

## 项目状态

- Branch: `dev`
- Main branch risk: Low. 当前没有在 `main` 开发。
- Uncommitted files: Yes.
- Business code changed in working tree: Yes. 当前未提交变更包含 `app.py`、大量 `modules/`、`scripts/`、`data/`、报告与启动脚本。
- Current phase: High-risk commit hygiene and recovery.
- Automation status: GitHub Issue / PR workflow、Agent QA、branch protection、mock Claude Review、Real Claude Integration Plan 均已进入体系化阶段；但当前工作区状态不适合继续自动开发。
- Recommendation authority: 暂停继续开发新功能，优先恢复可审计、可提交、可回滚的工作区状态。

## 风险评分

- Risk score: `94 / 100`

Reason:

- Positive: 当前分支是 `dev`，没有在 `main` 直接开发。
- Positive: 项目治理、Agent workflow、Claude Review 接入方案和 QA 规则已有基础。
- Positive: 本次 Supervisor 检查只更新日报，没有创建分支、提交、push 或删除文件。
- Risk: 工作区存在大量未提交文件，覆盖业务代码、API/赔率客户端、数据刷新脚本、回测脚本、历史数据、运行日志、报告和启动脚本。
- Risk: 未提交变更包含 `app.py` 和多个核心 `modules/`，已超出单一任务可审计范围。
- Risk: 存在大量新增 `data/history/*_pre.json`、`data/history/*_post.json`、`data/history/my_portfolios/*.json`、`data/worldcup2026/*`，必须区分真实历史输入、刷新产物、运行缓存和可提交数据。
- Risk: `data/performance_logs/app_performance.jsonl` 已修改，明确不应进入正常 commit。
- Risk: `docs/CHANGELOG.md` 和 `docs/QA_REPORT.md` 最近同步记录仍停留在 2026-06-22，未覆盖当前 2026-06-24 至 2026-06-26 的大量变更。
- Risk: `docs/TASK_QUEUE.md` 仍以 Agent automation / commit hygiene 为主，但没有明确反映当前新增算法、回测、数据刷新、Real Claude 接入等多条并行工作线。
- Risk: 根目录存在 `QA_REPORT.md`、`REAL_CLAUDE_INTEGRATION_PLAN.md`、`STARTUP_RECOVERY.md`、`START_APP.command` 等未提交文件，需要确认是否属于当前可提交范围。

## 当前优先任务

- Current priority: Stop feature development and perform commit hygiene.
- Immediate next step: 生成一次完整的工作区分组提交计划，明确哪些文件应提交、哪些文件必须排除、哪些文件需要用户确认。
- Recommended focus: 先处理版本审计和提交边界，再继续 Real Claude report-only、算法回测、UI 或数据刷新。
- Current rule: 在清理完成前，不应继续修改 `app.py`、`modules/`、`scripts/`、生产排序、推荐逻辑或 `data/history`。

## 已知问题

- 推荐组合存在剧本冲突。
- Over3.5 与 1:0 可能同时出现。
- 缺少主剧本/次剧本/冷门剧本结构。
- Portfolio Ranking 过度依赖 EV/ROI/Sharpe。
- 用户组合缺少自动排名。
- UI 决策效率不够高。
- 当前工作区存在多主题混杂变更，版本审计风险极高。
- 数据刷新产物、历史数据、性能日志、业务代码和治理文档尚未拆分提交。

## 检查结果

- 是否在 `main` 开发: No. 当前分支是 `dev`。
- 是否存在未提交修改: Yes.
- CHANGELOG 是否同步: No. `docs/CHANGELOG.md` 未覆盖当前大量 2026-06-24 至 2026-06-26 变更。
- QA_REPORT 是否同步: No. `docs/QA_REPORT.md` 未覆盖当前工作区风险、真实 Claude 接入方案和新增算法/回测/data 刷新工作。
- TASK_QUEUE 是否同步: Partially. 仍强调 automation / commit hygiene，但需要补充当前实际最高优先级：工作区恢复与提交拆分。

Current uncommitted risk buckets:

- Business / product code changed:
  - `app.py`
  - `modules/betting_opinion.py`
  - `modules/market_utils.py`
  - `modules/odds_client.py`
  - `modules/polymarket_client.py`
  - `modules/pregame_content.py`
  - `modules/report_generator.py`
  - `modules/result_distribution.py`
  - `modules/schedule_client.py`
  - `modules/team_resolver.py`
  - `modules/the_odds_client.py`
  - `modules/user_odds.py`
  - `modules/weather_client.py`
  - `modules/worldcup_db.py`
  - `modules/game_behavior_engine.py`
  - `modules/portfolio_engine.py`

- Scripts changed or added:
  - `scripts/refresh_match_prematch_snapshot.py`
  - `scripts/update_gpt_context.py`
  - `scripts/backtest_attribution.py`
  - `scripts/backtest_portfolio_engine.py`
  - `scripts/run_streamlit_8502.sh`
  - `scripts/start_streamlit_8502.command`
  - `scripts/test_portfolio_engine.py`
  - `scripts/validate_report_exports.py`

- Data / generated outputs:
  - `data/history/portfolio_performance.json`
  - `data/history/style_performance.json`
  - `data/history/*_pre.json`
  - `data/history/*_post.json`
  - `data/history/my_portfolios/*.json`
  - `data/worldcup2026/*`
  - `data/fetch_logs/*`
  - `data/team_aliases.yaml`
  - `data/worldcup2026/index.json`

- Reports and docs:
  - `REAL_CLAUDE_INTEGRATION_PLAN.md`
  - `STARTUP_RECOVERY.md`
  - `docs/GAME_BEHAVIOR_MODEL.md`
  - `docs/MODEL_ALGORITHM.md`
  - `reports/backtests/*`
  - `reports/validation/*`
  - `CHANGELOG.md`
  - `GPT_CONTEXT.md`
  - `LATEST.md`
  - `QA_REPORT.md`

- Do not include in normal commits:
  - `data/performance_logs/app_performance.jsonl`
  - local cache files if any appear later
  - secrets / `.env`

## 项目状态摘要

```text
当前不是继续开发阶段，而是高风险工作区恢复阶段；必须先把多主题变更拆分、审计、确认提交边界，才能继续 Agent 自动化或产品开发。
```

## 建议下一步

- 立即执行一次 `Commit Hygiene Recovery Report`，按主题列出可提交组、需用户确认组、禁止提交组。
- 优先保护当前工作：不要删除文件，不要 reset，不要 force push。
- 第一组建议只处理纯文档/治理文件，例如 Real Claude Integration Plan；不要混入业务代码或 data。
- 第二组再单独审查业务代码：`app.py`、`modules/`、`scripts/` 是否属于同一功能目标，是否有 QA 和 changelog 对应记录。
- 第三组单独处理 data：区分赛前快照、赛后结果、my_portfolio、fetch logs、performance logs。
- 在提交拆分完成前，暂停新的功能开发、API 刷新、回测扩展和 UI 改动。
