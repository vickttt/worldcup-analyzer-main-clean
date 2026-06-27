# Task

Review the protocol consolidation task for World Cup Analyzer.

Claude should review only and must not write code. This is a docs/protocol task that consolidates repeated operating rules into project-level documents.

# Changed files

- `AGENTS.md`
- `docs/CODEX_CLAUDE_LOOP.md`
- `docs/UI_CACHE_API_PROTOCOL.md`
- `docs/API_REFRESH_SAFETY.md`
- `docs/CHANGELOG.md`
- `docs/QA_REPORT.md`
- `reports/claude_reviews/round_15_review_packet.md`

# Scope

- Product code changed: no.
- `app.py` changed: no.
- `modules/` changed: no.
- `data/` changed: no.
- Golden JSON changed: no.
- Real API refresh performed: no.
- Secrets printed: no.
- `main-clean` modified: no.

# Product code impact

- None.
- This task changes only project protocol documentation, changelog/QA notes, and this Claude review packet.
- No runtime behavior, UI behavior, API behavior, cache behavior, recommendation output, ranking, portfolio, strategy, odds, backtest, data, or golden fixture behavior was changed.

# Protocol content added

- `AGENTS.md` now defines project identity, branch rules, forbidden paths, risk gates, Codex-Claude review loop, autonomous progression rule, stop conditions, validation checklist, API/secret policy, UI-CACHE-API route, and checkpoint summary format.
- `docs/CODEX_CLAUDE_LOOP.md` defines Codex, Claude, and ChatGPT/Jin roles; review round rules; max 3 Claude rounds; PASS early-stop; material finding handling; packet budget guard; artifact handling; and when Claude is not required.
- `docs/UI_CACHE_API_PROTOCOL.md` defines the current UI-CACHE-API phase route, completed tasks, forbidden areas, API-Football-only policy, runtime/cache file policy, `.runtime/` behavior, sample JSON behavior, and local Streamlit 8501 testing protocol.
- `docs/API_REFRESH_SAFETY.md` defines no-secret-printing rules, ignored secret files, API-Football-only policy, Odds API disabled policy, no repeated refresh loops, one-time bounded refresh gate, runtime status path, tracked sample path, no `data/history` mutation, no golden JSON mutation, API call logging, and failure-safe behavior.

# Task 5 context included

- Task 5 completed successfully on branch `codex/ui-cache-api-api-football-one-time-refresh`.
- Final head: `7f447bbad9e70caaf9b0779bf214e0f6f26f21cd`.
- It performed exactly one API-Football call to `GET /fixtures?id=1489393`.
- It wrote only ignored runtime artifacts plus tracked reports/docs/scripts.
- It passed Claude Round 14 with verdict `PASS`.

# Secret scan

- No secret values are intentionally included.
- Changed docs contain only key names and present/missing policy, not key values.
- `.env` and `.runtime/` are not part of the changed files.
- Secret-shaped token scan on changed files: pass, no matches.

# Protected files

- `app.py` untouched.
- `modules/` untouched.
- `data/` untouched.
- Golden JSON untouched.
- Ranking, portfolio, strategy, odds, and backtest logic untouched.

# Validation

- `git diff --check`: pass.
- Secret-shaped token scan on changed files: pass, no matches.
- Protected-path diff check for `app.py`, `modules`, `data`, and golden JSON: pass.
- Python compile: not required because no Python files were touched.
- `python3 scripts/validate_claude_review_packet.py reports/claude_reviews/round_15_review_packet.md`: pass, estimated `$0.007110`.

# Gate status

- PORTFOLIO_EXTRACTION: BLOCKED.
- BACKTEST_READY: NO.
- Current phase: UI-CACHE-API.
- API provider policy: API-Football only for keyed refresh work.
- Real API refresh for this protocol task: not performed.

# Proposed next task

Consolidate this protocol branch into `dev-clean` after validation and Claude PASS. This next task should be a fast-forward or safe merge only, require no product code changes, no real API call, no secret handling beyond status checks, and no protected-path changes.

# Questions for Claude

- Do the protocol docs correctly reduce repeated task prompts without weakening safety gates?
- Are branch rules and `main-clean` protection clear?
- Are forbidden paths and stop conditions complete enough?
- Is the Codex-Claude loop consistent with the current GitHub Actions packet review workflow?
- Are autonomous progression rules narrow enough?
- Is API refresh safety clear for API-Football-only work?
- Does the UI-CACHE-API route correctly reflect completed Task 5 and the next expected tasks?
- Is the proposed next task low-risk and safe for Codex to perform after PASS?
