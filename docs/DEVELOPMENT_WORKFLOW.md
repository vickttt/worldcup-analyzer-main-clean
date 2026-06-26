# WorldCup Analyzer Development Workflow

## 1. Project Directory Rules

- `worldcup-analyzer-main-clean` is the new clean primary development directory.
- The old `worldcup-analyzer` directory is a dirty archive and must not be used for new development.
- `main-clean-local` is only for viewing `origin/main`.
- `dev-clean` is the daily development integration branch.
- `feature/*` branches are used for single-task development.

## 2. Branch Rules

- `main` / `origin/main`: stable release branch. Update only through pull requests.
- `main-clean-local`: local stable view of `origin/main`. Do not develop directly on it.
- `dev-clean`: daily integration branch for normal development.
- `feature/*`: single-purpose branches created from `dev-clean` unless the task explicitly says otherwise.
- Large feature work must use a dedicated `feature/*` branch or worktree, then merge back through `dev-clean` before release promotion.
- `freeze/*`: historical frozen recovery branches. Do not develop directly on them.
- `backup/*`: historical backup branches. Do not develop directly on them.

### Feature Branch Categories

- `feature/ui-*`: page, layout, report, and reading-experience work.
- `feature/model-*`: algorithms, scoring, scenario logic, and portfolio ranking work.
- `feature/odds-*`: market odds parsing, real user odds, and odds matching work.
- `feature/backtest-*`: backtests, attribution, validation, and audit work.
- `feature/data-*`: API refresh, cache behavior, data schema, and snapshot work.

## 3. Codex Task Rules

Every Codex task must state:

- Current branch.
- Files allowed to change in this task.
- Files forbidden to change in this task.
- Whether Portfolio Score weights may change.
- Whether `data/history` may change.
- Whether `.github/workflows` may change.
- Whether new APIs may be added.
- Whether `pytest` must be run.
- Every completed modification must update `docs/CHANGELOG.md` and `docs/QA_REPORT.md`.

## 4. Single-Task Isolation

- UI tasks must not change Portfolio Engine logic unless explicitly approved.
- Model tasks must not change report UI unless explicitly approved.
- Odds/market tasks must not change UI, model scoring, backtests, or historical data unless explicitly approved.
- Backtest tasks must not change pages, model defaults, or data refresh behavior unless explicitly approved.
- Data/API tasks must not change algorithms, UI, or backtest assumptions unless explicitly approved.
- One task should have one owner area and one clear acceptance target.

## 5. Commit Rules

Use scoped commit messages:

- `feat(report): ...`
- `fix(odds): ...`
- `feat(model): ...`
- `test(backtest): ...`
- `docs(workflow): ...`
- `ci(actions): ...`

## 6. Pull Request Rules

- `main` must be updated only through pull requests.
- Do not push directly to `main`.
- CI is a required check before merging into `main`.
- Claude Review is currently auxiliary and is not a required gate.
- Agent QA is currently auxiliary and is not a required gate.
- One pull request should solve one topic.

## 7. Secrets And Environment Safety

- Do not write API keys, tokens, passwords, `.env` values, or other secrets into code.
- Do not write API keys, tokens, passwords, `.env` values, or other secrets into Markdown.
- Use local environment variables or ignored local files for secrets.
- `.env` and local environment variants must remain ignored by `.gitignore`.
- Do not paste secrets into changelogs, QA reports, task notes, or issue/PR templates.

## 8. Completion Report Rules

Every completed task must output:

- Modified files.
- Test/check results.
- Whether Portfolio Score was affected.
- Whether `data/history` was affected.
- Whether any data refresh, API pull, or report generation touched protected data.
- Any skipped checks and the reason they were skipped.

## 9. Prohibited Actions

- Do not develop directly on `main`.
- Do not continue development in the old `worldcup-analyzer` dirty archive.
- Do not modify UI, algorithms, data, and backtests in the same Codex task.
- Do not write `.env`, API keys, or secrets into code or Markdown.
- Do not run `git clean`, delete stash entries, or delete branches unless explicitly confirmed.
- Do not overwrite `data/history` snapshots.

## 10. Standard Development Flow

```bash
git switch dev-clean
git pull
git switch -c feature/report-readability
# make the scoped change
# run required checks
git commit -m "feat(report): improve report readability"
git push -u origin feature/report-readability
# open PR to dev-clean or main, depending on release scope
```

## 11. Current Status

- `origin/main` is now the merged v1.81-dev recovery version.
- `dev-clean` was created from `origin/main`.
- The old `worldcup-analyzer` directory remains as a dirty archive.
- `freeze/current-dev-20260626-v180-recovery` remains as a recovery backup.
