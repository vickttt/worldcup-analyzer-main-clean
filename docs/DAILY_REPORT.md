# Daily Report

## 2026-06-21

## 项目状态

- Branch: `dev`
- Main branch risk: Low. 当前没有在 `main` 开发。
- Uncommitted files: Yes.
- Business code changed: No `app.py` / recommendation logic / Portfolio Ranking sort diff detected in the current Supervisor scan.
- Current phase: Validation -> Scenario Guardrails preparation.
- Shadow Mode status: Active, with Hybrid Ranking report-only validation added.
- Recommendation authority: Legacy remains production authority, but standalone Legacy is no longer considered sufficient.
- Post-Match Validation progress: `12 / 5`.
- Current promotion status: `Enter Scenario Guardrails Phase`.
- Latest capability check: API-Football can return candidate historical odds by `date + league + season + bet`, but each row must pass `update < kickoff` before it is valid for strict pre-match backtest.

## 风险评分

- Risk score: `74 / 100`

Reason:

- Positive: 当前分支是 `dev`，没有在 `main` 直接开发。
- Positive: Post-Match Validation 已达到 12 个有效验证，超过 5-Match Promotion Rule。
- Positive: `docs/CHANGELOG.md` 和 `docs/QA_REPORT.md` 已同步到 Hybrid Ranking Report v0.1。
- Positive: 当前检查未发现 `app.py`、`strategy_score(...)`、`evaluate_allocation(...)`、`strategy_comparison(...)`、UI 或生产排序逻辑被修改。
- Risk: 工作区存在大量未提交文件，需要按主题拆分 commit。
- Risk: 存在 `data/performance_logs/app_performance.jsonl` 和多份历史 `data/` 未提交文件，不应混入设计/脚本类 commit。
- Risk: 最新 `API_FOOTBALL_HISTORICAL_ODDS_CHECK.md` 尚未同步到 `docs/CHANGELOG.md` 和 `docs/QA_REPORT.md`。
- Risk: `docs/TASK_QUEUE.md` 仍停留在早期 P0-P5 队列，未反映当前 Guardrails / Hybrid / Backfill Benchmark 阶段。
- Risk: Scenario ROI 仍为负，虽然明显优于 Legacy ROI；不能直接全量替换排序。

## 当前优先任务

- Current priority: Hybrid Ranking and historical odds benchmark readiness.
- Immediate milestone: Design a safe World Cup odds backfill pipeline after confirming historical odds quality rules.
- Current rule: Do not change production sorting until Hybrid Ranking has report-only benchmark evidence.
- Current guardrail: Legacy Rank 1 with `Shadow Verdict = Disagreement` should not remain unchallenged in future UI/eligibility work.

## 已知问题

- 推荐组合存在剧本冲突。
- Over3.5 与 1:0 可能同时出现。
- 缺少主剧本/次剧本/冷门剧本结构。
- Portfolio Ranking 过度依赖 EV/ROI/Sharpe。
- 用户组合缺少自动排名。
- UI 决策效率不够高。
- Historical odds backfill 不能默认当作真实赛前赔率，必须验证 `odds update timestamp < kickoff timestamp`。
- 当前 `TASK_QUEUE` 未同步最新阶段。

## 检查结果

- 是否在 `main` 开发: No. 当前分支是 `dev`。
- 是否存在未提交修改: Yes.
- CHANGELOG 是否同步: Partially. 已同步 Hybrid Ranking Report v0.1；尚未记录 API-Football Historical Odds Check。
- QA_REPORT 是否同步: Partially. 已同步 Hybrid Ranking Report v0.1；尚未记录 API-Football Historical Odds Check。
- TASK_QUEUE 是否同步: No. 仍是早期 P0-P5 队列，没有反映当前 Guardrails / Hybrid / Historical Backfill Benchmark。

Current uncommitted risk buckets:

- Commit-ready / current work candidates:
  - `API_FOOTBALL_HISTORICAL_ODDS_CHECK.md`
  - `HYBRID_RANKING_REPORT.md`
  - `scripts/generate_hybrid_ranking_report.py`
  - `docs/CHANGELOG.md`
  - `docs/QA_REPORT.md`
- Design docs that should be committed separately:
  - `HYBRID_RANKING_REPLACEMENT_PLAN.md`
  - `OPERATIONAL_DASHBOARD_V1.md`
  - `OPERATIONAL_WORKFLOW_V1.md`
  - `POST_MATCH_VALIDATION_V1.md`
  - `PRODUCT_REVIEW_V1.md`
  - `MY_PORTFOLIO_VALIDATION_CHECK.md`
- Do not include in unrelated commits:
  - `data/performance_logs/app_performance.jsonl`
  - untracked `data/history/*_pre.json`
  - untracked `data/history/my_portfolios/*.json`

## 验证指标

- Valid post-match validations: 12.
- Legacy Wins: 3.
- Scenario Wins: 3.
- Draws: 6.
- Legacy ROI: -40.8%.
- Scenario ROI: -2.1%.
- Promotion Status: `Enter Scenario Guardrails Phase`.
- Hybrid Report v0.1:
  - Snapshots scanned: 19.
  - Snapshots with strategies: 17.
  - Legacy Top differs from Hybrid Top: 10.
  - Scenario Top differs from Hybrid Top: 9.

## 项目状态摘要

```text
Scenario Layer 已经通过 12 场验证进入 Guardrails 阶段；下一步应验证 Hybrid Ranking，而不是继续单独依赖 Legacy Ranking。
```

## 建议下一步

- 先把当前工作区按主题拆分提交，避免 data/log 与设计/脚本混在一起。
- 补充 `docs/CHANGELOG.md` 和 `docs/QA_REPORT.md`，记录 `API_FOOTBALL_HISTORICAL_ODDS_CHECK.md`。
- 更新 `docs/TASK_QUEUE.md`，加入当前阶段:
  - `P0 Commit hygiene and governance sync`
  - `P1 Historical odds backfill plan`
  - `P2 Hybrid Ranking benchmark`
  - `P3 Scenario Guardrails UI / eligibility design`
- 下一项开发前仍不要修改 `strategy_score(...)`、`strategy_comparison(...)`、`evaluate_allocation(...)` 或生产排序。

