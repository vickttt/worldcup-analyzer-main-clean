# Task

Perform a single-round, read-only Claude Review smoke test for the lightweight Codex-Claude loop on dev-clean.

Review only the recent TPB-only markdown report semantics and CI health changes listed below. Claude must not propose code patches, must not modify files, and must not start a second review round.

# Changed files

Target commits under review:

- 850c506: Align markdown match reports with TPB-only semantics.
- 4548324: Update portfolio engine smoke test for TPB-only architecture.
- 48dd13c: Prevent legacy API diagnostic script from failing CI pytest collection.

Target files under review:

- report generator file: markdown match report output semantics.
- portfolio engine smoke test file: TPB-only interface smoke test.
- manual API check script: manual-only API-Football diagnostic script.
- CI workflow file: ordinary push and pull request CI.
- Claude Review workflow file: manual review workflow.

Summarized changes:

- Markdown report output was updated to use TPB-only labels: 盘口观察, TPB 概率标签, TPB 覆盖说明, 比赛投资分, 推荐金额, 结果分布观察, and Polymarket 只读对比层.
- Report output now includes a recommended stake field when available. If no stake field exists, it says 推荐金额：未计算 and states that stake is mapped from 比赛投资分.
- Result distribution and Polymarket sections are labeled as observation-only and not part of TPB, 比赛投资分, or 推荐金额.
- The old large portfolio/scenario test script was replaced by a small smoke test for the current TPB-only public contract: score_layer, execution_layer, explanation_layer, TPB probabilities, entropy-derived confidence, investment score, deterministic stake mapping, TPB coverage explanation, and disabled legacy stubs.
- The old API diagnostic script was renamed from a pytest-collectable test name to a manual-only API check name. It now imports the API key loader from the current centralized API client and states that real API diagnostics require explicit user authorization.
- CI remains a normal push and pull request workflow. It compiles selected Python files, runs the TPB-only portfolio smoke test, and then runs pytest.
- Claude Review remains a manual workflow_dispatch workflow. It checks out dev-clean, reads one sanitized packet path, calls Claude once, and uploads a review artifact.

# Product code impact

Product decision logic was not intentionally changed by these commits.

Expected unchanged decision chain:

API-Football 1X2 odds -> TPB -> betting_confidence -> investment_score -> stake -> UI/report display.

Expected unchanged constraints:

- No EV or ROI should influence decision output.
- No hybrid system should influence decision output.
- No scenario ranking or scenario shadow output should influence score, stake, ranking, or risk.
- No risk gate should block TPB recommendations.
- Polymarket remains read-only comparison or observation, not a replacement source.
- Manual API diagnostics must not run in CI or pytest collection.

# Protected files

Protected areas not intentionally changed in these commits:

- AGENTS.md was not modified.
- app.py was not modified by this review scope.
- TPB formulas were not modified by this review scope.
- stake mapping was not modified by this review scope.
- coverage calculation was not modified by this review scope.
- API transport logic was not modified by this review scope.
- runtime logs and performance logs are excluded from this packet and from the commit.

# Validation

Local validation already performed by Codex before this smoke test:

- Python compile passed for app.py, project modules, the TPB portfolio smoke test, and the manual API check script.
- TPB-only portfolio smoke test passed locally.
- git diff whitespace check passed.
- GitHub CI passed after the manual API check script was removed from pytest auto-collection.
- Current dev-clean is synchronized with origin/dev-clean before this packet-only commit.

# Secret scan

This packet includes only summaries and short descriptions.

It does not include:

- secret values
- local environment files
- API key values
- runtime logs
- performance logs
- data cache content
- full repository content
- raw patch blocks

# Gate status

PORTFOLIO_EXTRACTION: BLOCKED.

BACKTEST_READY: NO.

Claude Review mode: read-only, single round only.

Branch mode: dev-clean only. No branch creation, pull request, merge, rebase, or old multi-round Claude loop.

# Proposed next task

No automatic next task should be executed from this review.

Claude should answer only these review questions:

1. Does the markdown report output now match TPB-only semantics?
2. Are any user-visible labels still likely to imply Legacy Ranking, Scenario Shadow, EV, ROI, hybrid, risk gate, or portfolio optimizer decision logic?
3. Are these labels clear enough: 盘口观察, TPB 概率标签, TPB 覆盖说明, 比赛投资分, 推荐金额, 结果分布观察, Polymarket 只读对比层?
4. Is TPB 概率标签：- a user-understanding risk that should be changed to a clearer null state?
5. Should 执行模式：TPB确定性 be changed to 执行模式：TPB 确定性 for readability?
6. Is the portfolio smoke test limited to the TPB-only contract without restoring old scenario, EV, ROI, risk gate, or portfolio optimizer logic?
7. Is the manual API check script safely outside pytest collection and explicit enough that it must not run without user authorization?
8. Is the CI workflow appropriate as ordinary CI?
9. Is the Claude Review workflow still a manual, read-only Claude review path?
10. Is there any active decision path risk in the reviewed changes?

If Claude finds issues, classify them as:

- MUST_FIX: active decision path or CI safety risk.
- POLISH: wording or clarity improvement only.
- NO_ACTION: acceptable as-is.
