# DEPRECATED — HISTORICAL REFERENCE ONLY

This document is no longer an active workflow authority.
The current active repository rules are defined only in AGENTS.md.

Current active workflow:
- dev-clean is the only development branch
- no automatic branch creation or branch switching
- Codex is the only execution engine
- Claude is read-only review only
- the user is the final decision authority
- no parallel agent workflows are allowed
- old Issue -> Branch -> PR, Supervisor-driven branch workflows, and multi-agent automation loops must not be followed unless explicitly re-approved by the user

Do not use this document as execution guidance unless AGENTS.md is explicitly updated to restore it.

# Codex-Claude Loop

This document is the concise operating protocol for Codex-Claude collaboration in World Cup Analyzer.

## Roles

- Codex implements scoped tasks, runs local validation, manages Git, prepares sanitized review packets, reads Claude feedback, and applies safe fixes.
- Claude reviews only. Claude must not write code, produce patches, create branches, manage worktrees, commit, push, merge, or modify files.
- ChatGPT/Jin owns product direction, scope approval, risky decisions, final approvals, and merges into protected branches.
- GitHub stores branch history and runs the GitHub Actions Claude review workflow.

## Review Rounds

- Round 1 Claude review is required for normal development tasks.
- Maximum 3 Claude rounds per task.
- Stop early when Claude returns `PASS` or no material findings.
- If Claude returns material findings, Codex may make only safe scoped fixes, rerun validation, commit, push, and run the next round.
- Do not continue beyond 3 rounds without human approval.
- Claude output should include verdict, material findings, safe fixes required, exactly one recommended next task, risk level, and whether Codex may proceed automatically.

## Packet Budget Guard

- Claude review uses sanitized packets under `reports/claude_reviews/`.
- Run `python3 scripts/validate_claude_review_packet.py <packet>` before each Claude review.
- The packet must stay small and must not include raw full diffs, full `app.py`, full `modules/`, full `data/history`, full golden JSON, secrets, large reports, or repository dumps unless Jin explicitly approves.
- If the packet guard fails, fix the packet before review.

## GitHub Actions Review

- Preferred workflow: `.github/workflows/claude-review.yml`.
- Use a sanitized packet path like `reports/claude_reviews/round_<n>_review_packet.md`.
- Claude artifacts are downloaded or stored under `reports/claude_reviews/`.
- Artifact files should be committed when they are part of the task record.
- GitHub Actions uses repository secret `ANTHROPIC_API_KEY`; do not place this key in files, logs, issues, PRs, reports, or command output.

## Material Finding Handling

Material findings include:

- Secret exposure or unsafe secret handling.
- Unbounded or repeated API calls.
- Forbidden path changes.
- `data/history` mutation without approval.
- Golden JSON mutation without approval.
- Ranking, portfolio, strategy, odds, or backtest logic changes outside scope.
- UI or report wording that overclaims freshness, refresh coverage, or recommendation safety.
- Validation failure.
- Branch confusion or unexpected dirty state.

Codex response to material findings:

1. Stop any further scope expansion.
2. Apply only safe scoped report/doc/code fixes allowed by the task.
3. Rerun relevant validation.
4. Commit and push fixes.
5. Run the next Claude round, up to the 3-round maximum.

## When Claude Is Not Required

Claude is usually not required for:

- Pure local operations: open web page, check port, stop Streamlit, confirm localhost.
- Read-only checks that do not modify files, commit, or push.
- Fast-forward or safe merge into `dev-clean` after a branch already passed Claude.
- Tiny runtime/log cleanup where Claude cost exceeds benefit.
- Emergency cleanup to restore clean Git state, with later review if needed.

Claude is required for normal implementation tasks, product-facing UI changes, API/cache behavior changes, workflow protocol changes, and changes that will be used as future agent operating rules.

## Autonomous Progression

Codex may automatically continue to exactly one next task only when:

- Claude returns `PASS` or no material findings.
- Claude recommends exactly one next task.
- The next task is low-risk or medium-low-risk.
- The next task stays inside the current phase.
- No additional real API call is required.
- No secret value is exposed.
- No `data/history` or golden JSON mutation is required.
- No ranking, portfolio, strategy, odds, or backtest logic is touched.
- Git status is clean.
- Validation passes.
- Packet budget guard passes.

Codex must stop for human checkpoint after maximum 3 autonomous tasks, maximum 3 Claude rounds, any material risk, conflict, failed validation, secret/API uncertainty, scope expansion, or Claude/Codex disagreement.

## Required Review Packet Shape

A review packet should include:

- Task name and scope.
- Changed files.
- Product-code impact.
- Protected-path status.
- API and secret safety.
- Validation summary.
- Gate status.
- Proposed next task.
- Specific questions for Claude.

## Artifact Handling

- Commit sanitized packets when used for review.
- Download and commit Claude review artifacts when they are part of the task checkpoint.
- Record Claude verdict and material findings in `docs/QA_REPORT.md`.
- Record high-level completed work in `docs/CHANGELOG.md`.
- Do not commit `.env`, `.runtime/`, Streamlit secrets, raw API payloads, or generated runtime logs.
