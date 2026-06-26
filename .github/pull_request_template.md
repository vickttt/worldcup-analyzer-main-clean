## Summary

- 

## Linked Issue

Closes #

## Changes

- 

## QA

- [ ] Python syntax check passed for changed Python files.
- [ ] `docs/CHANGELOG.md` updated when code or workflow changed.
- [ ] `docs/QA_REPORT.md` updated when code or workflow changed.
- [ ] No API refresh was run unless explicitly approved.
- [ ] No data files were modified unless explicitly approved.

## Safety Check

- [ ] Did not change production sorting.
- [ ] Did not change recommendation logic.
- [ ] Did not change default recommendation.
- [ ] Did not modify `strategy_score(...)`.
- [ ] Did not modify `strategy_comparison(...)`.
- [ ] Did not modify `evaluate_allocation(...)`.
- [ ] Did not modify protected history data.

If this PR intentionally modifies ranking-sensitive functions, include:

`approved:ranking`

If this PR intentionally modifies protected history data, include:

`approved:data-write`

## Manual Review Required

List anything Jin must manually inspect before merge.
