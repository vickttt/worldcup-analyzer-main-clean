#!/usr/bin/env bash
set -euo pipefail

echo "GitHub auth:"
gh auth status

echo "Repo:"
gh repo view --json nameWithOwner,defaultBranchRef,url

echo "Recent PRs:"
gh pr list --limit 3

echo "Recent issues:"
gh issue list --limit 3
