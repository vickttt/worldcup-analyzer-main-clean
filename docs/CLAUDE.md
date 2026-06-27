# Claude Branch Context Rules

Claude is review-only in this repository. Claude must not create branches, switch branches, merge branches, commit, push, or modify files.

## Stable Integration Rule

- `dev-clean` is the only stable development integration branch.
- `codex/model-design-intelligence-system` is experimental AI/model research only.
- Never merge `codex/model-design-intelligence-system` into `dev-clean` without explicit Jin approval.
- Do not treat experimental branch context as valid for `dev-clean` tasks.

## Context Verification Rule

No Claude review packet or chat context may assume the active Git branch.

Every task packet must state:

- current branch
- target branch
- allowed files
- forbidden files
- branch type: `UI`, `MODEL`, `OPS`, or `RISK`
- lifecycle stage: `ACTIVE` or `EXPERIMENTAL`
- expected branch lifetime: `short`, `medium`, or `long`
- whether runtime code, `data/history`, golden JSON, portfolio extraction, or backtest enablement are in scope

If branch context is missing or mismatched, Claude should return a blocking finding and ask Codex to confirm branch alignment before proceeding.

## Cross-Branch Safety

- Do not recommend merging experimental model-design work into `dev-clean` unless Jin explicitly requested that merge.
- Do not recommend copying unreviewed files from experimental branches into `dev-clean`.
- Do not infer that a file existing on one branch exists on another branch.
- Treat uncommitted files on the wrong branch as contamination risk until Codex stashes, commits to the correct branch, or reports the divergence.

## Branch Lifecycle Review Rule

Claude must apply `docs/BRANCH_LIFECYCLE_SYSTEM.md` when reviewing branch cleanup, task routing, or merge-readiness packets.

- `ACTIVE` branches may continue only when validation and protected-path checks pass.
- `EXPERIMENTAL` branches must not be marked merge-ready unless the packet proves review, validation, and scope safety.
- `STALE` branches may be recommended for cleanup review, but Claude must not recommend automatic deletion.
- `ARCHIVED` branches are read-only references and must not be proposed as normal development bases.
- Experimental branches older than 2-3 Codex-Claude loops without merge should trigger a review recommendation.
- Remote deletion always requires Jin approval; Claude must not phrase remote deletion as an agent-owned action.

If a packet claims a branch is `merge-safe`, Claude should verify whether it is already merged into `dev-clean`, protected as a stable branch, or still contains unique commits.
