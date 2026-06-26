# WorldCup Analyzer Development Workflow

## 1. Current Project Structure

- `worldcup-analyzer-main-clean` is the new clean primary development directory.
- The old `worldcup-analyzer` directory is a dirty archive and must not be used for new development.
- `main-clean-local` is only for viewing `origin/main`.
- `dev-clean` is the daily development integration branch.
- `feature/*` branches are used for single-task development.

## 2. Branch Rules

- `main` / `origin/main`: stable release branch. Update only through pull requests.
- `main-clean-local`: local stable view of `origin/main`. Do not develop directly on it.
- `dev-clean`: daily integration branch for normal development.
- `feature/ui-*`: page, layout, report, and reading-experience work.
- `feature/model-*`: algorithms, scoring, scenario logic, and portfolio ranking work.
- `feature/odds-*`: market odds parsing, real user odds, and odds matching work.
- `feature/backtest-*`: backtests, attribution, validation, and audit work.
- `feature/data-*`: API refresh, cache behavior, data schema, and snapshot work.
- `freeze/*`: historical frozen recovery branches. Do not develop directly on them.
- `backup/*`: historical backup branches. Do not develop directly on them.

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

## 4. Single-Task Isolation

- UI tasks must not casually change Portfolio Engine logic.
- Model tasks must not casually change report UI.
- Backtest tasks must not casually change pages.
- Data/API tasks must not casually change algorithms.
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
- Pull requests must pass CI.
- Do not push directly to `main`.
- Claude Review is currently auxiliary and is not a required gate.
- Agent QA is currently auxiliary and is not a required gate.
- One pull request should solve one topic.

## 7. Prohibited Actions

- Do not develop directly on `main`.
- Do not continue development in the old `worldcup-analyzer` dirty archive.
- Do not modify UI, algorithms, data, and backtests in the same Codex task.
- Do not write `.env`, API keys, or secrets into code or Markdown.
- Do not run `git clean`, delete stash entries, or delete branches unless explicitly confirmed.
- Do not overwrite `data/history` snapshots.

## 8. Standard Development Flow

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

## 9. Current Status

- `origin/main` is now the merged v1.81-dev recovery version.
- `dev-clean` was created from `origin/main`.
- The old `worldcup-analyzer` directory remains as a dirty archive.
- `freeze/current-dev-20260626-v180-recovery` remains as a recovery backup.
