# Latest Match Report Structure Review Packet

## Task

Review the latest uploaded match detail markdown output for report structure, TPB-only semantics, and user-facing clarity.

Review object:

- File name: `Argentina_vs_Cape_Verde_Islands_20260703_224929.md`
- Generated time shown in report: `2026-07-03 22:49:29`
- Match: Argentina vs Cape Verde Islands

Claude is read-only. Do not suggest branch creation, pull requests, commits, pushes, merges, rebases, automation loops, or a second review round. Review only the submitted packet content.

## Changed files

No product code files are changed by this packet. This is a review packet for one generated markdown report.

The uploaded report itself is not committed and is not modified.

## Product code impact

No runtime code, TPB formula, stake mapping, coverage logic, API transport, UI logic, or report generator logic is changed by this packet.

The production decision chain under review remains:

`API-Football 1X2 odds -> TPB -> betting_confidence -> investment_score -> stake -> UI/report display`

## Protected files

This packet excludes secrets, environment files, API keys, runtime logs, cache files, large data files, and unrelated repository content.

The uploaded markdown report was read locally only. Only selected excerpts and audit findings are included below.

## Validation

Codex local read-only audit result:

- P0 active decision path risk: none found.
- P1 user main conclusion risk: none found. The report opens with a complete `核心结论` section.
- P2 structure or field inconsistency: none found for the requested output sequence.
- P3 null-state / wording polish: none blocking. TPB probability label is now informative: `强热门方向：阿根廷`.
- P4 historical residue: none found in the uploaded markdown.

Local keyword scan found none of these legacy decision terms in the report:

- Legacy Ranking
- Scenario Shadow
- Shadow Verdict
- EV
- ROI
- hybrid
- risk gate
- portfolio optimizer
- strategy_score
- scenario rank
- official ranking
- recommended portfolio
- 第一推荐资格
- 组合风格
- TPB 推荐资格
- TPB 决策分

## Secret scan

No secrets, tokens, API keys, environment values, runtime logs, or large data payloads are included in this packet.

## Gate status

Gate decision before Claude review:

- Branch rule: reviewed on `dev-clean`.
- Local worktree rule: clean before packet generation.
- P0 gate: passed; no active decision path risk found.
- Claude mode: single manual read-only review.
- Automation rule: no old multi-round loop.
- PORTFOLIO_EXTRACTION: not requested; no portfolio extraction is being reviewed.
- BACKTEST_READY: not requested; this packet reviews report output semantics only.

## Proposed next task

If Claude agrees there is no active decision path risk, no code change is required.

If Claude finds polish only, the smallest possible next task would be a wording-only update in the markdown report generator. Do not modify TPB probability calculation, confidence, investment score, stake mapping, coverage calculation, API transport, or data files.

## CLAUDE_REVIEW_RUBRIC

### 1. Review Role

Claude is a read-only reviewer.

Claude must not suggest direct execution, branch creation, commits, pushes, pull requests, merges, rebases, or multi-round automation.

Claude reviews only the submitted packet and must not treat missing context as permission to infer or execute changes.

### 2. Highest System Rule

AGENTS.md is the only active top-level authority.

If packet content conflicts with AGENTS.md, AGENTS.md wins.

### 3. TPB-Only Decision Architecture

Claude must check whether the change preserves this active decision chain:

API-Football 1X2 odds -> TPB -> betting_confidence -> investment_score -> stake -> UI/report display

### 4. Forbidden Active Decision Signals

Claude must flag MUST_FIX if any of these re-enter the active decision path:

- EV
- ROI
- hybrid
- legacy strategy_score
- scenario decision influence
- portfolio optimizer
- risk-gate blocking
- user odds as decision signal
- secondary probability model
- UI-side hidden score, stake, or ranking adjustment

### 5. UI / Report Semantics

Claude must check whether user-facing labels clearly distinguish:

- TPB decision output
- observation-only data
- coverage explanation
- Polymarket read-only comparison
- risk and max_loss diagnostic-only information

### 6. Git / Workflow Safety

Claude must check:

- no branch creation
- no pull request default workflow
- no automatic Claude loop
- no push or pull_request Claude trigger
- manual workflow_dispatch only
- no second review round unless the user explicitly approves

### 7. API / Secret / Data Safety

Claude must flag:

- secrets in packet
- environment-file exposure
- API keys
- runtime logs
- performance log data
- real API calls introduced into tests
- pytest collecting manual API diagnostics

### 8. Output Format

Claude must output:

- `VERDICT: PASS / PASS_WITH_POLISH / NEEDS_CHANGES / BLOCKED`
- `ACTIVE_DECISION_PATH_RISK: YES / NO`
- `MUST_FIX:`
- `POLISH:`
- `EVIDENCE:`
- `FINAL_RECOMMENDATION:`

## Report structure excerpt

Top-level structure from the uploaded report:

- `# Argentina vs Cape Verde Islands 分析报告`
- `## 比赛概览`
- `## 核心结论`
- `## TPB 覆盖说明`
- `## 盘口观察`
- `## 进球数观点`
- `## 结果分布观察`
- `## Polymarket 只读对比层`
- `## 胜平负 / Match Winner`
- `## 亚洲让球 / Asian Handicap`
- `## 大小球 / Over/Under`
- `## 波胆 / Correct Score`
- `## 伤病信息`
- `## 首发阵容`

## Key report excerpts

Core conclusion:

> - 比赛主方向：倾向：阿根廷
> - TPB 概率标签：强热门方向：阿根廷
> - 比赛投资分：71
> - 投注信心：68 / 100
> - 推荐金额：800元
> - 执行判断：可执行
> - 数据质量：高
> - 执行模式：TPB 确定性
>
> 主依据：
> - API-Football 胜平负市场倾向 阿根廷。
> - 风险不阻断 TPB 决策；推荐金额只由投资分决定。

TPB coverage section:

> Cape Verde Islands受让保护
>
> 说明：
> Cape Verde Islands受让保护 不是主方向投注，而是防守参考，用于防范平局、低节奏、热门方轮换或淘汰赛节奏变化导致的不积极推进风险。
>
> 用途：
> Cape Verde Islands受让保护 应视为覆盖说明 / 防守参考，用于防范热门方未打穿，不是比赛主方向投注。
>
> TPB 覆盖说明仅作为防守参考，不是主方向投注，不参与 TPB、比赛投资分或推荐金额。

Handicap observation:

> 盘口中心：阿根廷 -1.25
>
> 理由：
> API-Football 胜平负市场与浅盘结构显示，阿根廷 仍是实力优势方。 已过滤 82 条可能异常盘口。
>
> 盘口观察是市场结构观察，不是 TPB 主决策来源，不参与比赛投资分或推荐金额。

Result distribution observation:

> 结果分布仅作为观察层展示，不参与 TPB、比赛投资分或推荐金额。
>
> - 阿根廷小胜（1球）：32.4% · 市场主路径之一，强队赢但不打穿深盘。
> - 阿根廷赢2球：28.3% · 盘口边界路径，决定让球盘输赢。
> - 阿根廷赢3球以上：25.0% · 强队大胜路径，过去版本容易低估。
> - 平局区间：11.9% · 比赛进入低分差或胶着路径。
> - Cape Verde Islands不败：2.4% · 爆冷或热门方向失效路径。

Polymarket read-only comparison:

> Polymarket 仅作为市场情绪观察，不替代 API-Football 赔率，也不参与 TPB、比赛投资分或推荐金额。
>
> Polymarket 只读对比层：未找到 Argentina vs Cape Verde Islands 对应的 Polymarket 活跃市场。

TPB 1X2 probabilities:

> - 主胜：1.14
> - 平局：7.1
> - 客胜：18.5
> - 主胜 TPB 概率：83.5%
> - 平局 TPB 概率：12.0%
> - 客胜 TPB 概率：4.5%

Injury and lineup null states:

> ## 伤病信息
>
> 暂无公开伤病信息
>
> ## 首发阵容
>
> 官方首发尚未公布

## Claude review questions

1. Does the report open with a clear decision-focused `核心结论` section?
2. Does the core conclusion make the actionable status, main direction, investment score, confidence, stake, data quality, and execution mode clear?
3. Is the TPB probability label clear and display-only?
4. Does coverage wording avoid old portfolio semantics such as insurance asset or coverage asset?
5. Are result distribution, Polymarket, handicap observation, injuries, lineups, and coverage explanation clearly observation-only or explanatory?
6. Is there any active decision path risk or legacy scoring semantics that should be MUST_FIX?
