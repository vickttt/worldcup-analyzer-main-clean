#!/usr/bin/env python3
# DEPRECATED — LEGACY MULTI-ROUND CLAUDE LOOP
# Current active loop is defined in AGENTS.md.
# This script must not be used as the default execution path.
# Do not run it unless the user explicitly re-approves legacy multi-round automation.
# For current workflow, Claude review must be read-only, manual or explicitly requested,
# and Codex remains the only execution engine.
"""Run one safe round of the Codex-Claude review loop."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "reports" / "claude_reviews"


def run_review(args: argparse.Namespace) -> None:
    command = [
        "python",
        "scripts/claude_review_diff.py",
        "--mode",
        args.input_mode,
    ]
    if args.input_file:
        command.extend(["--input-file", args.input_file])
    if args.pr_number is not None:
        command.extend(["--pr-number", str(args.pr_number)])

    subprocess.run(command, cwd=ROOT, check=True)


def latest_review_files() -> tuple[Path, Path]:
    reviews = sorted(OUTPUT_DIR.glob("claude_review_*.md"), key=lambda path: path.stat().st_mtime)
    metadata = sorted(OUTPUT_DIR.glob("claude_review_*.json"), key=lambda path: path.stat().st_mtime)
    if not reviews or not metadata:
        raise FileNotFoundError("no Claude review artifacts found")
    return reviews[-1], metadata[-1]


def write_round_files(round_number: int, review_path: Path, metadata_path: Path) -> tuple[Path, Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    review_text = review_path.read_text(encoding="utf-8")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    round_review = OUTPUT_DIR / f"round_{round_number}_review.md"
    round_task = OUTPUT_DIR / f"round_{round_number}_next_codex_task.md"
    round_metadata = OUTPUT_DIR / f"round_{round_number}_metadata.json"

    round_review.write_text(review_text, encoding="utf-8")
    round_task.write_text(
        "# Next Codex Task\n\n"
        "Review the Claude output in the matching round review file. "
        "Implement only a safe, scoped task after Jin approval when required.\n",
        encoding="utf-8",
    )
    metadata["round"] = round_number
    metadata["round_review_path"] = str(round_review.relative_to(ROOT))
    metadata["round_next_task_path"] = str(round_task.relative_to(ROOT))
    round_metadata.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return round_review, round_task, round_metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round", type=int, required=True, choices=range(1, 6))
    parser.add_argument(
        "--input-mode",
        choices=["working-diff", "last-commit", "file", "pr"],
        required=True,
    )
    parser.add_argument("--input-file")
    parser.add_argument("--pr-number", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_review(args)
    review_path, metadata_path = latest_review_files()
    round_review, round_task, round_metadata = write_round_files(args.round, review_path, metadata_path)
    print(f"Round review: {round_review.relative_to(ROOT)}")
    print(f"Next task: {round_task.relative_to(ROOT)}")
    print(f"Round metadata: {round_metadata.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
