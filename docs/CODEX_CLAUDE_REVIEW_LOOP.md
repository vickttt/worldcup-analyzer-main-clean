# Codex Claude Review Loop

Date: 2026-06-27

## Purpose

This protocol lets Codex perform scoped implementation work while Claude reviews controlled diffs or reports. Claude is a strategic reviewer only. Codex remains the implementation agent.

## Long-Term Goals

Claude should evaluate whether each recommended next Codex task advances at least one long-term project goal:

- Model quality.
- Calculation architecture.
- Football-API refresh safety and efficiency.
- App open speed.
- Cache design.
- UI decision clarity.
- Risk contract and golden validation.
- GitHub workflow reliability.
- Engineering safety.

## GitHub Hygiene

- `dev-clean` is the normal development branch for small docs, reports, and script-only work.
- `main-clean` is stable and protected from direct edits.
- Direct `main-clean` edits are forbidden.
- Large, risky, or product-facing work needs a feature branch before implementation.
- Parallel UI, model, API, portfolio, or refactor streams should use a separate worktree.
- Checkpoint commit and push are recommended at phase boundaries after validation passes.
- Claude may recommend preparing a PR only when a change is stable, validated, and scoped.
- Claude must not recommend merge into `main-clean`; Jin remains the final approver.

## Worktree Decision Policy

- No worktree is needed for small docs, scripts, or reports that are easy to revert.
- A feature branch is recommended for product runtime code, UI, model, API refresh, cache, portfolio, backtest, ranking, or multi-file behavior changes.
- A worktree is recommended for parallel UI/model/API/portfolio work, risky product refactors, or multi-round work where the current workspace must remain stable.
- A checkpoint commit and push are recommended when several files changed, new infrastructure works, validation passed, or a new major phase is about to start.

## Three-Round Loop

Codex may auto-run at most 3 rounds before stopping for Jin review. This cap reduces drift risk, low-value task chains, and token/API cost.

## Round 1

- Codex performs a small scoped task.
- Codex runs validation.
- Codex generates a controlled diff or report.
- Claude reviews the supplied material.
- Claude outputs one recommended next Codex task with long-term goal alignment.

## Round 2

- Codex implements only the recommended task if it is safe and scoped.
- Codex runs validation.
- Claude reviews again.

## Round 3

- Codex creates a final consolidation summary.
- Jin decides whether to commit, open a PR, or merge.

## Rules

- Claude never edits files.
- Claude never writes code.
- Claude never applies patches.
- Claude only reviews controlled inputs and recommends one next Codex task.
- Claude is stateless by default.
- Each Claude review relies only on the current review packet, not prior conversation memory, prior Claude replies, or long historical context.
- If context is insufficient, Claude requests a smaller targeted packet instead of inferring from old context.
- Claude must not create or manage branches, worktrees, or conversations itself.
- Codex is responsible for Git operations.
- Default Claude review mode is sanitized file-mode review packet.
- Auto-loop rounds should pass only small review packets to Claude.
- `working-diff` mode is optional and should not be used when environment data-exposure policy blocks external diff review.
- Raw working diffs require Jin approval before being sent to Claude.
- Claude explains which long-term project goal the next task supports.
- Claude prefers small, reversible, high-leverage tasks.
- Codex remains the implementation agent.
- Codex never blindly follows unsafe Claude suggestions.
- Jin remains the final approver for commits, PRs, merges, and scope expansion.
- Jin approves before PR merge.
- No product logic changes unless explicitly scoped.
- No secrets are sent to Claude, GitHub, reports, or docs.
- Do not send full history snapshots unless explicitly approved.
- Do not ask Claude to review full `data/history`, full `app.py`, full `modules/`, full golden JSON, long historical changelogs, full repository dumps, or large reports unless Jin explicitly approves.
- Keep review inputs token-light by default.
- Claude output should be concise, target 1000-2000 tokens, avoid long essays, and include one next Codex task only.
- Claude must focus only on the current task, current diff/report, current gate status, and long-term project goals.
- Claude must not overfit to old docs or unrelated historical reports.
- Portfolio extraction remains blocked until the required gates are satisfied.
- Backtest enablement remains disabled until the required gates are satisfied.
- Claude must keep `PORTFOLIO_EXTRACTION` as `BLOCKED` and `BACKTEST_READY` as `NO` unless supplied evidence explicitly satisfies those gates.
- Claude reviews Git, branch, worktree, GitHub, docs, QA, and Codex final reply quality as part of every loop round.
- Codex checks the branch, changed files, validation, Claude verdict, next task, and whether commit/push/worktree/PR is needed before continuing.
- Claude may suggest Codex capabilities as optional implementation hints, but must not demand tools unavailable in the current environment.

Claude may only recommend these branch and GitHub actions:

- Continue on current branch.
- Create feature branch.
- Create worktree.
- Checkpoint commit and push.
- Open PR after Jin approval.

## External Review Policy

If the environment blocks external review of repository-derived content:

- Do not retry automatically.
- Do not work around the policy.
- Do not send raw diff.
- Do not send sanitized packet.
- Record the block in `reports/`.
- Continue with local Codex-only validation.
- Ask Jin whether to use manual review or another approved review path.

Default review hierarchy:

1. Local validation first.
2. Sanitized review packet.
3. External Claude API review only if policy allows.
4. Manual Jin-approved review if external review is blocked.

## GitHub-Mediated Claude Review

When direct Codex-to-Claude review of repository-derived content is blocked, the default approved architecture is GitHub-mediated review:

1. Codex creates a sanitized packet at `reports/claude_reviews/round_<n>_review_packet.md`.
2. Codex commits and pushes the packet to the active feature branch after Jin approves the checkpoint.
3. Push to `dev-clean` auto-triggers `.github/workflows/claude-review.yml` when a sanitized review packet is added or changed.
4. GitHub Actions detects the latest changed `reports/claude_reviews/*_review_packet.md` file and sends only that packet to Claude.
5. GitHub Actions calls Claude with `secrets.ANTHROPIC_API_KEY`.
6. GitHub Actions uploads artifact `claude-review-round-<n>`.
7. The artifact contains `round_<n>_claude_review.md` and `round_<n>_claude_review.json`.
8. Codex fetches the artifact with `scripts/fetch_claude_review_result.py` or Jin downloads it manually from GitHub.
9. Codex reads the review output, extracts one next Codex task, validates safety, and continues only if the verdict is `PASS` or `PASS_WITH_NOTES`.

`workflow_dispatch` remains available as a manual fallback. Codex must not use `gh workflow run` unless Jin explicitly asks. The auto-trigger reviews sanitized packets only, never raw diffs.

Version 1 is artifact-only. The workflow must not auto-commit review output back to the branch.

Required GitHub secret:

- Name: `ANTHROPIC_API_KEY`
- Location: GitHub repository settings, Secrets and variables, Actions, New repository secret.

Do not paste the key into files, issues, PRs, reports, or local command output.
Do not manually trigger the workflow until Jin confirms the repository secret is added and explicitly asks for manual dispatch.

## Codex Capability Suggestions

Claude may recommend Codex use available capabilities when helpful:

- Codex agent mode for longer scoped tasks.
- GitHub CLI for issues, branches, PRs, and branch checks.
- Feature branch or worktree split.
- Browser or computer-use to inspect local Streamlit UI.
- Local app run or page-load check.
- Cache or performance profiling.
- Validation scripts.
- Automated report generation.
- Claude review script for checkpoint review.

Capability suggestions are optional implementation hints. Codex decides what is actually available and safe.

## App, Browser, UI, And API Policy

Claude may recommend browser or computer-use only for UI or speed tasks, such as:

- Local Streamlit page opens successfully.
- Page load speed is acceptable.
- UI sections are readable.
- Cache changes improve responsiveness.
- Football-api refresh button behavior is clear.

Browser and computer-use must not be used for secrets, API keys, or private credential pages.

Claude may recommend Codex call other apps or APIs only if:

- The task explicitly requires it.
- Credentials are already safely configured.
- No secrets are printed.
- Outputs are saved into approved report paths.
- Jin approval is required for paid or high-volume API usage.

## Guarded Auto-Run Mode

Codex may run up to 3 guarded rounds automatically only when all of these rules hold:

1. Each round is small, reversible, and scoped.
2. The first auto-run experiment is restricted to docs, scripts, and Claude review reports.
3. Claude reviews each round and recommends exactly one next Codex task.
4. Codex continues automatically only after Claude returns `PASS` or `PASS_WITH_NOTES`.
5. Codex stops immediately after Claude returns `BLOCKED`.
6. Codex writes a report after every round.
7. After 3 rounds, Codex stops and asks Jin for approval.

Allowed files for the first auto-run experiment:

- `docs/`
- `scripts/`
- `reports/claude_reviews/`
- `reports/*validation*.md`
- `reports/*contract*.md`

Forbidden files:

- `app.py`
- `modules/`
- `data/`
- `reports/golden_output_snapshot_v1.json`
- `reports/golden_output_snapshot_v2.json`
- `reports/golden_risk_contract_v1.json`
- `.env`
- `.env.*`
- `*.env`

Stop immediately if any of these occur:

- `app.py` changes unexpectedly.
- `modules/` changes unexpectedly.
- `data/` changes.
- Golden output JSON changes.
- `.env` or secrets appear outside ignored local files.
- Claude suggests portfolio extraction.
- Claude suggests backtest enablement.
- Claude suggests direct `main-clean` edits.
- Claude suggests merge, PR, or push without Jin approval.
- Claude suggests reviewing large files without Jin approval.
- The task becomes ambiguous.
- Validation fails.
- Secret scan fails.
- The next task cannot be parsed safely.
- Token or cost risk becomes high.

The auto-run driver records per-round artifacts:

- `reports/claude_reviews/round_<n>_review.md`
- `reports/claude_reviews/round_<n>_next_codex_task.md`
- `reports/claude_reviews/round_<n>_metadata.json`
- `reports/claude_reviews/round_<n>_codex_execution_summary.md`

The final auto-run summary should be:

- `reports/claude_reviews/three_round_auto_loop_summary.md`

The summary must include branch, rounds completed, files changed by round, validation by round, Claude verdict by round, stop condition, gate status, commit recommendation, push recommendation, PR recommendation, and whether a worktree is recommended for the next phase.

## Allowed Review Inputs

- Sanitized review packet.
- Current working diff with protected paths excluded.
- Last commit diff with protected paths excluded.
- A selected PR diff.
- A selected short report or test input file.
- Small excerpts from large files only when the excerpt is explicitly scoped.
- `git diff --stat`.
- Scoped git diff.
- Validation summaries.

## Forbidden Review Inputs Without Jin Approval

- Full `app.py`.
- Full `modules/`.
- Full `data/history`.
- Full golden JSON.
- Full repository dump.
- Long historical changelog.
- Large reports.

## Default Exclusions

- `data/**`
- `reports/golden_output_snapshot_v1.json`
- `reports/golden_output_snapshot_v2.json`
- `reports/golden_risk_contract_v1.json`
- `.env`
- `.env.*`
- `*.env`

## Operator Checklist

- Confirm local secret files are ignored.
- Confirm the Claude smoke test is ready.
- Confirm the current branch is correct for the task.
- Run the review script in the selected mode.
- Review the generated Markdown and metadata.
- Execute only safe, scoped next tasks.

## Three-Round GitHub Discipline

Each round must include:

- Branch check.
- Changed file summary.
- Validation.
- Claude review.
- Commit/push recommendation.
- Next Codex task.

Codex's final response to Jin must briefly summarize:

- Branch.
- Modified files.
- Created files.
- Deleted files, if any.
- Validation results.
- Claude review verdict.
- Secret scan result, when relevant.
- Product-code impact.
- Data/history impact.
- Gate status.
- Commit hash, if committed.
- Push status, if pushed.
- PR link or number, if opened.
- Next recommended action.
- Whether commit, push, worktree, PR, or GitHub backup is needed.
