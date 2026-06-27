# Codex Branch Context Rules

Codex owns local execution, validation, file edits, and Git hygiene. Codex must keep branch context explicit before every task.

## Stable Integration Rule

- `dev-clean` is the only stable development integration branch.
- `codex/model-design-intelligence-system` is experimental AI/model research only.
- Never merge `codex/model-design-intelligence-system` into `dev-clean` without explicit Jin approval.
- Do not run normal development from an accidental branch context.

## Required Start Check

Before changing files, Codex must confirm:

- current branch
- target branch
- `git status`
- allowed files
- forbidden files
- branch type: `UI`, `MODEL`, `OPS`, or `RISK`
- lifecycle stage: `ACTIVE` or `EXPERIMENTAL`
- expected branch lifetime: `short`, `medium`, or `long`

If the current branch does not match the target branch, Codex must switch only after confirming the working tree is clean or safely isolating uncommitted work.

## Dirty State Rule

If uncommitted files exist on the wrong branch:

- do not merge
- do not carry the files into another branch
- stash them, commit them to the explicitly correct branch, or stop and report the divergence
- never silently move `data/history`, golden JSON, runtime code, or module changes across branch boundaries

## Task Boundary Rule

No Codex chat/context should assume the Git branch. Every task must explicitly confirm:

- current branch
- target branch
- allowed files
- lifecycle stage
- expected lifetime

If the prompt lacks these fields, Codex should infer conservatively from repo docs and `git status`, then state the assumption before edits.

## Branch Lifecycle Rule

Codex must apply `docs/BRANCH_LIFECYCLE_SYSTEM.md` before proposing branch cleanup or starting a new branch.

- `ACTIVE` branches may receive approved work under the current governance rules.
- `EXPERIMENTAL` branches must remain isolated until reviewed.
- `STALE` branches may be proposed for cleanup but must not be deleted automatically.
- `ARCHIVED` branches are read-only references unless Jin approves recovery work.
- Codex may propose deletion candidates, but Jin must approve remote branch deletion.
- Experimental branches older than 2-3 Codex-Claude loops without merge must be reviewed before further work.
- `safe to delete` means cleanup candidate only; it is not permission to delete.

Default branch routing:

- `UI-CACHE`: use `feature/ui-cache-api/*` or `codex/ui-cache-api-*`.
- `MODEL`: use `codex/model-design-*`.
- `OPS`: use `dev-clean` only for tiny docs-only changes; otherwise use a scoped `codex/ops-*` branch.
- `RISK`: use `codex/risk-*`.

## Decision Layer Rule

Codex must apply `docs/DECISION_LAYER_CONTROL_SYSTEM.md` before starting a new node, triggering Claude, or proposing branch execution.

If the system is in `FRAGMENTED` or `CONSOLIDATION MODE`:

- do not start a new node.
- do not trigger Claude.
- do not merge, archive, delete, or push branch operations.
- do not create more analysis reports unless they directly consolidate existing findings.
- update `reports/CONSOLIDATED_SYSTEM_ANALYSIS.md` or Decision Layer governance first.

If analysis output is growing faster than execution readiness, Codex must classify analysis/execution balance as `IMBALANCED` and stop for Decision Layer review.
