## 1. Verdict

PASS

## 2. Scope Check

The change stayed within requested scope. The task was to create a read-only field provenance map for missing `risk_contract_v1` fields without implementing extraction. The packet shows:

- Documentation and validation script only.
- No product runtime code modified.
- No golden JSON files modified.
- Protected files untouched.
- CHANGELOG and QA_REPORT updated as required.

Scope is clean.

## 3. Product Code Safety

Product code impact: none. Runtime logic, ranking, recommendation, odds, strategy, portfolio, data refresh, and backtest logic remain unchanged. The new provenance map is read-only documentation and validation scaffolding. Safe to proceed.

## 4. Secret Safety

No secrets appear in the supplied packet. Fast staged-diff secret check is planned before commit. Status: safe.

## 5. Git / Branch / Worktree Safety

Current branch judgment: appears to be `dev-clean` or a feature branch for risk-contract analysis. No branch confusion detected.

- `main-clean` is protected from direct edits: confirmed.
- Working tree: small, reversible, documentation-focused. No checkpoint needed yet.
- No branch creation or worktree needed for this task.
- Validation passed locally.

Recommendation: **Continue on dev-clean** (or current feature branch). Task is small, docs/validation-only, easy to revert, and does not touch product logic.

## 6. GitHub / Docs Safety

- Commit recommendation: safe to commit after planned secret scan.
- Push recommendation: safe to push to `dev-clean` after commit and final QA validation.
- PR recommendation: hold PR until risk contract extraction/implementation scope is approved by Jin. This task is foundational; merge should wait for next strategic step.
- Safe to keep local only: no. The provenance map is foundational for future extraction tasks; push to `dev-clean` is recommended so Jin and team see the findings.
- GitHub backup needed: yes, before high-risk extraction tasks begin.
- `docs/CHANGELOG.md`: updated. Status: safe.
- `docs/QA_REPORT.md`: updated. Status: safe.

## 7. Token Budget / Context Safety

Review input size: small, appropriately scoped, sanitized, and token-light. Packet format is correct:

- `git diff --stat` equivalent provided implicitly.
- Scoped file list and validation summary.
- No full golden JSON, full modules, or large reports included.
- No unrelated historical context.

Token/API cost risk: acceptable. Context is limited to current task, current packet, gate status, and long-term goals. Next review should use the same scoped packet format.

## 8. Long-Term Goal Alignment

Long-term goal supported: **risk contract and golden validation**.

Why this matters: the provenance map is a prerequisite for safe extraction. By documenting source functions and data availability without implementing extraction, the team gains clarity on feasibility before enabling backtest or portfolio extraction. This reduces implementation risk and supports the golden validation goal.

The proposed next task (source availability matrix) directly extends this goal by validating whether mapped sources have sufficient data across golden fixtures.

## 9. Codex Capability Recommendation

No special capabilities needed for this round. The task was documentation and validation scripting, both completed locally. For the next task (source availability matrix), Codex may benefit from:

- Validation script to scan golden fixtures and map source-key availability.
- Report generation to tabulate coverage.
- Optional local app run or Streamlit inspection if UI clarity is needed (deferred).

## 10. Gate Status

- PORTFOLIO_EXTRACTION: **BLOCKED** (no change; extraction not implemented).
- BACKTEST_READY: **NO** (no change; post-match risk outcome and canonical score remain unresolved).

Both gates remain as required. No evidence in this packet satisfies either gate condition.

## 11. Codex Reply Quality Check

Codex's reply to Jin should include (when provided):

- Current branch.
- Changed files: five files (provenance map, validation script, review packet, CHANGELOG, QA_REPORT).
- Validation results: all local checks passed.
- Claude verdict: PASS.
- Product-code impact: none.
- Secret scan result: pending before commit.
- Gate status: PORTFOLIO_EXTRACTION blocked, BACKTEST_READY no.
- Recommendation: commit, push to dev-clean, hold PR.
- Next task: source availability matrix (read-only, no extraction).

If Codex's final reply includes these fields, quality is sufficient. If any field is missing, mark the next review `PASS_WITH_NOTES`.

## 12. Next Codex Task

**Task Title:** Create source availability matrix across golden fixtures.

**Long-term goal supported:** risk contract and golden validation.

**Why this task matters:** validates whether mapped risk-contract source functions have sufficient data coverage in existing golden fixtures before extraction is attempted. Identifies gaps early.

**Why this task is high leverage:** unblocks extraction feasibility assessment and informs whether golden fixtures need expansion before backtest enablement.

**Allowed files:**

- `reports/risk_contract_source_availability_matrix.md` (new).
- `scripts/validate_source_availability.py` (new or extend existing).
- `docs/CHANGELOG.md` (append).
- `docs/QA_REPORT.md` (append).

**Forbidden files:**

- `app.py`
- `modules/`
- `data/`
- Golden output JSON.
- Product runtime code.

**Validation commands:**

- `python3 -m py_compile scripts/validate_source_availability.py`
- `python3 scripts/validate_source_availability.py`
- `git diff --check`
- Secret scan before commit.

**Expected Codex final report fields:**

- Current branch.
- Changed files.
- Validation results.
- Matrix summary (coverage percentage per source key, per fixture set).
- Gaps identified (if any).
- Recommendation for golden fixture expansion (if needed).
- Gate status: PORTFOLIO_EXTRACTION, BACKTEST_READY (no change).
- Next task recommendation (for Claude review).

## 13. Stop Conditions

Stop Codex before implementation if:

- Claude verdict is `BLOCKED` (not applicable; verdict is PASS).
- `app.py`, `modules/`, `data/`, or golden JSON are modified (not applicable; protected).
- Secrets appear in reports, docs, scripts, or logs (not applicable; scan pending).
- Validation fails (not applicable; all checks passed).
- Secret scan fails (stop and ask Jin).
- Source availability matrix task scope expands to extraction or backtest enablement (stop and ask Jin).
- Next task cannot be parsed safely (not applicable; task is clear).
- Token/cost risk becomes high (not applicable; local validation only).

Proceed to source availability matrix task only after secret scan passes and Jin confirms the provenance map findings are acceptable.
