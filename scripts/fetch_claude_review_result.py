#!/usr/bin/env python3
"""Manually fetch an explicitly authorized Claude review artifact/result.

This tool must not trigger GitHub Actions or Claude review. It must not create
branches, open pull requests, commit, push, merge, or act as an entrypoint for
the old GitHub-mediated review loop. Use it only to retrieve an existing result
after the user explicitly authorizes that review path.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "reports" / "claude_reviews"


def run_command(args: list[str]) -> str:
    result = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round", required=True, type=int)
    parser.add_argument("--run-id", help="GitHub Actions run id. If omitted, latest claude-review.yml run is used.")
    return parser.parse_args()


def latest_run_id() -> str:
    output = run_command(
        [
            "gh",
            "run",
            "list",
            "--workflow",
            "claude-review.yml",
            "--limit",
            "1",
            "--json",
            "databaseId",
            "--jq",
            ".[0].databaseId",
        ]
    )
    if not output:
        raise RuntimeError("no claude-review.yml workflow runs found")
    return output


def main() -> int:
    args = parse_args()
    if args.round < 1:
        raise ValueError("--round must be positive")
    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI is required. Manual fallback: download the artifact from the workflow run page.")

    run_id = args.run_id or latest_run_id()
    artifact_name = f"claude-review-round-{args.round}"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_command(["gh", "run", "download", run_id, "--name", artifact_name, "--dir", str(OUTPUT_DIR)])
    print(f"Downloaded {artifact_name} from run {run_id} into {OUTPUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
