# GitHub Claude Codex Setup Plan

Date: 2026-06-27
Scope: safe environment workflow for Codex, GitHub CLI, and Claude API integration.

## Required Tools

- `git`: version control and branch safety.
- `gh`: GitHub authentication, issue reading, PR reading, and future PR creation.
- `python3`: local automation scripts.
- Project `.venv`: isolated Python dependencies.
- Anthropic Python SDK: controlled Claude API calls from local scripts.
- `jq`: JSON inspection for CLI outputs.
- `curl`: HTTP diagnostics.
- `node` and `npm`: optional, only needed if a future approved workflow requires JavaScript tooling.

## Required Credentials

- GitHub CLI auth through `gh auth login`.
- Local Anthropic API key in the shell environment.
- Optional local `.env` file for the Anthropic key, kept gitignored and never committed.
- Claude API smoke test status: READY when `ANTHROPIC_API_KEY` is present in the executing shell.
- Default Claude smoke-test model: `claude-haiku-4-5-20251001`.
- `ANTHROPIC_MODEL` can override the default model for future compatibility.

Credential rules:

- Do not commit API keys, tokens, passwords, or local secret files.
- Do not write real keys into code, Markdown, GitHub Issues, or PRs.
- Keep secret values local to the terminal, shell profile, or a gitignored local environment file.
- Do not print, inspect, or copy local `.env` contents during validation.

## Safe Communication Model

- Codex modifies files locally inside the repo.
- Codex works from `dev-clean` or a dedicated feature branch for larger changes.
- GitHub Issues define task scope and forbidden files.
- Pull Requests become the review and approval layer before merge.
- Claude API reviews only controlled inputs such as diffs, audit reports, or explicitly selected files.
- Claude output is saved to reports only after secret scanning and scope checks.
- No secrets are sent to GitHub or committed to the repository.
- Claude CLI remains optional; the Python SDK is the default controlled integration path.
- Local scripts may load gitignored `.env` values with `python-dotenv`, but generated reports must never include secret values.
- Direct Codex-to-Claude review of repository-derived content may be blocked by local environment data-exposure policy.
- When direct review is blocked, use GitHub-mediated Claude review with sanitized packets and GitHub Actions secrets.

## GitHub-Mediated Claude Review

Default flow for review-loop automation:

1. Codex creates `reports/claude_reviews/round_<n>_review_packet.md`.
2. Codex commits and pushes the packet to the active branch only after Jin approves the checkpoint.
3. Jin adds GitHub Actions repository secret `ANTHROPIC_API_KEY`.
4. Push to `dev-clean` auto-triggers `.github/workflows/claude-review.yml` when a sanitized review packet is added or changed.
5. GitHub Actions detects the latest changed `reports/claude_reviews/*_review_packet.md` file and reads only that sanitized packet path.
6. GitHub Actions calls Claude using `secrets.ANTHROPIC_API_KEY`.
7. GitHub Actions uploads artifact `claude-review-round-<n>`.
8. Codex fetches the artifact with `scripts/fetch_claude_review_result.py`, or Jin downloads it manually.

`workflow_dispatch` remains available as a manual fallback. Jin does not need to manually run the workflow each round after a packet is committed and pushed to `dev-clean`. Codex should create and validate the packet, commit and push, then inspect the automatically created GitHub Actions run. Codex must not use `gh workflow run` unless Jin explicitly asks.

Version 1 is artifact-only:

- No auto-commit from workflow.
- No write permission granted to workflow.
- No raw diff review by default.
- Auto-trigger reviews sanitized packets only, not raw diffs.
- No secret values in code, docs, reports, issues, PR text, or logs.

Manual setup for Jin:

- Open GitHub repository settings.
- Go to Secrets and variables, Actions.
- Add a new repository secret named `ANTHROPIC_API_KEY`.
- Paste the key only into the GitHub secret value field.
- Do not paste the key into any file, issue, pull request, report, or chat transcript.

Do not manually trigger the workflow until Jin confirms the secret is added and explicitly asks for manual dispatch.

## Future Automation

1. Add a local script that sends a PR diff or selected report to Claude for review.
2. Save Claude review output into a controlled report path.
3. Add an optional GitHub comment posting script after manual approval.
4. Keep merge decisions manual.
5. Keep `data/history`, ranking logic, portfolio logic, and recommendation logic protected unless a task explicitly authorizes changes.

## Next Gate

- Use the read-only Claude review script for PR diffs or selected reports.
- Keep review inputs local-first, credential-safe, and explicit about which project context is sent.
- Do not enable portfolio extraction or backtest automation in this step.
