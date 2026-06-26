# Environment GitHub Claude Audit

Date: 2026-06-27
Branch: `dev-clean`
Scope: environment setup only. No product code, ranking logic, portfolio logic, reports data, or history data were modified.

## Repository Safety Check

- Current branch: `dev-clean`
- Tracking: `origin/dev-clean`
- Starting working tree: clean
- Recent commits:
  - `54a51bb tools: add golden risk contract v1 serializer`
  - `dbe7cf3 docs: define canonical risk contract v1`
  - `49f7011 refactor: prepare modular architecture and risk semantics gates`
  - `8be05d0 update docs`
  - `9731bb4 docs(workflow): add merge precheck report`

## Core Tool Check

| Tool | Installed | Required | Version / Path | Purpose | Recommended Install |
| --- | --- | --- | --- | --- | --- |
| `git` | yes | yes | `git version 2.50.1 (Apple Git-155)` at `/usr/bin/git` | Version control | Xcode command line tools or Homebrew |
| `gh` | yes | yes | `gh version 2.95.0` at `/opt/homebrew/bin/gh` | GitHub auth, repo, issue, PR operations | `brew install gh` |
| `python3` | yes | yes | `Python 3.14.3` at `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` | Local scripts and API checks | Python installer or Homebrew |
| `pip3` | yes | yes | `pip 25.3` at `/Library/Frameworks/Python.framework/Versions/3.14/bin/pip3` | Python package install | Bundled with Python |
| `node` | no | no | missing | Optional JavaScript tooling | `brew install node` if needed |
| `npm` | no | no | missing | Optional JavaScript package tooling | Installed with Node |
| `jq` | yes | yes | `jq-1.7.1-apple` at `/usr/bin/jq` | JSON inspection for CLI output | `brew install jq` |
| `curl` | yes | yes | `curl 8.7.1` at `/usr/bin/curl` | HTTP diagnostics | System curl or Homebrew |
| `brew` | yes | yes | `Homebrew 6.0.4` at `/opt/homebrew/bin/brew` | System tool installation | Homebrew installer |
| `code` | no | no | missing | Optional VS Code command-line editor integration | Install shell command from VS Code |
| `claude` | no | no | missing | Optional Claude CLI | Do not install until explicitly approved |
| `codex` | yes | yes | `codex-cli 0.142.2` at `/Applications/Codex.app/Contents/Resources/codex` | Codex local automation | Codex app |

No Homebrew installs were required. `gh` and `jq` were already installed. Node/npm remain optional and were not installed.

## GitHub CLI Check

- GitHub CLI authenticated: yes
- Active GitHub account: `vickttt`
- Git protocol: HTTPS
- Token scopes reported by `gh auth status`: `gist`, `read:org`, `repo`, `workflow`
- Remote URL: `https://github.com/vickttt/worldcup-analyzer-main-clean.git`
- Repo detected: yes
- Current repo: `vickttt/worldcup-analyzer-main-clean`
- Repo URL: `https://github.com/vickttt/worldcup-analyzer-main-clean`
- Default branch: `dev-clean`
- Can read issues: yes
- Can read PRs: yes
- `gh issue list --limit 5`: succeeded, returned no visible rows
- `gh pr list --limit 5`: succeeded, returned no visible rows

## Python Virtual Environment Check

- Existing venv before audit: no
- Created local venv: yes, `.venv`
- `.venv` ignored by Git: yes
- Package install result: success
- Import verification: `python api packages ok`

Installed package versions:

```text
anthropic==0.112.0
pydantic==2.13.4
pydantic_core==2.46.4
python-dotenv==1.2.2
requests==2.34.2
rich==15.0.0
```

Note: `pip freeze` emitted a local cache warning because the user-level pip cache directory was not writable. The install itself succeeded because pip disabled the cache.

## Claude API Readiness

- Claude CLI: missing
- Anthropic Python SDK: installed
- Claude CLI required: no
- `ANTHROPIC_MODEL` override: supported
- Default model: `claude-haiku-4-5-20251001`
- Claude smoke-test script created: yes
- Claude API status: READY
- Smoke-test result with local key available: `CLAUDE_API_READY: YES`

Recommended path: continue using the Python SDK first for controlled Claude API calls. Install a Claude CLI only after explicit approval.

Do not write real keys into repository files, Markdown, GitHub Issues, or PRs.

## Secret Safety

- `.env`: ignored
- `.env.*`: ignored
- `*.env`: added and ignored
- Real API keys written to repo: no
- The Claude smoke test reads only the local process environment and never prints keys.

## Smoke Test Scripts

- `scripts/check_claude_api_connection.py`
  - Reads `ANTHROPIC_API_KEY` from environment.
  - Uses `ANTHROPIC_MODEL` when set, otherwise defaults to `claude-haiku-4-5-20251001`.
  - Sends only the prompt `Reply with OK.` when a key exists.
  - Fails gracefully with `CLAUDE_API_READY: NO_KEY` when no key exists.
  - Does not send project data.

- `scripts/check_github_cli_connection.sh`
  - Runs read-only GitHub checks: auth, repo metadata, recent PRs, recent issues.
  - Does not create issues, PRs, branches, commits, or pushes.

## Validation

- `python3 -m py_compile scripts/check_claude_api_connection.py`: passed
- Updated Claude smoke-test default model from `claude-3-5-haiku-latest` to `claude-3-5-haiku-20241022` after the alias returned 404.
- Updated Claude smoke-test default model from `claude-3-5-haiku-20241022` to `claude-haiku-4-5-20251001` after the dated Haiku 3.5 model returned 404 for the user.
- `source .venv/bin/activate` then `python scripts/check_claude_api_connection.py`: returned `CLAUDE_API_READY: NO_KEY`; no live API request was made because no local key is set.
- Latest key-enabled smoke test status provided for checkpoint: `CLAUDE_API_READY: YES`.
- `bash -n scripts/check_github_cli_connection.sh`: passed
- `.venv/bin/python scripts/check_claude_api_connection.py`: returned `CLAUDE_API_READY: NO_KEY`, expected until a local key is set
- `./scripts/check_github_cli_connection.sh`: passed
- `git diff --check`: passed
- `git diff -- app.py`: no diff
- `git diff -- modules`: no diff
- `git diff -- data`: no diff
- `git diff -- reports`: no diff
- Secret scan for common Anthropic/GitHub token patterns outside `.git` and `.venv`: no matches

## Final Status

- Codex operating GitHub smoothly: yes for authenticated read operations.
- Branch/commit/PR readiness via GitHub CLI: partially ready; auth and repo detection work, but write operations were not tested because this audit is read-only.
- Reading and modifying project files safely: yes; only environment docs, scripts, `.gitignore`, and required QA/changelog docs were touched.
- Calling Claude API through local scripts: ready when `ANTHROPIC_API_KEY` is present in the executing shell.
- Future Codex to GitHub to Claude workflow: ready for the next controlled setup step.
