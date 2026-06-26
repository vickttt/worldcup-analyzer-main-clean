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
- Claude API smoke test status: READY when `ANTHROPIC_API_KEY` is present in the executing shell.
- Default Claude smoke-test model: `claude-haiku-4-5-20251001`.
- `ANTHROPIC_MODEL` can override the default model for future compatibility.

Credential rules:

- Do not commit API keys, tokens, passwords, or local secret files.
- Do not write real keys into code, Markdown, GitHub Issues, or PRs.
- Keep secret values local to the terminal, shell profile, or a gitignored local environment file.

## Safe Communication Model

- Codex modifies files locally inside the repo.
- Codex works from `dev-clean` or a dedicated feature branch for larger changes.
- GitHub Issues define task scope and forbidden files.
- Pull Requests become the review and approval layer before merge.
- Claude API reviews only controlled inputs such as diffs, audit reports, or explicitly selected files.
- Claude output is saved to reports only after secret scanning and scope checks.
- No secrets are sent to GitHub or committed to the repository.
- Claude CLI remains optional; the Python SDK is the default controlled integration path.

## Future Automation

1. Add a local script that sends a PR diff or selected report to Claude for review.
2. Save Claude review output into a controlled report path.
3. Add an optional GitHub comment posting script after manual approval.
4. Keep merge decisions manual.
5. Keep `data/history`, ranking logic, portfolio logic, and recommendation logic protected unless a task explicitly authorizes changes.

## Next Gate

- Build a read-only Claude review script for PR diffs or selected reports.
- Keep the script local-first, credential-safe, and explicit about which project context is sent.
- Do not enable portfolio extraction or backtest automation in this step.
