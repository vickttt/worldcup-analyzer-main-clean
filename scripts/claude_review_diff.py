#!/usr/bin/env python3
"""Generate a read-only Claude review for a controlled diff or report."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "reports" / "claude_reviews"
PROMPT_TEMPLATE = ROOT / "docs" / "CLAUDE_REVIEW_PROMPT_TEMPLATE.md"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
SAFETY_EXCLUSIONS = [
    "data/**",
    "reports/golden_output_snapshot_v1.json",
    "reports/golden_output_snapshot_v2.json",
    "reports/golden_risk_contract_v1.json",
    ".env",
    ".env.*",
    "*.env",
]
GIT_PATHSPECS = [
    ".",
    ":!data/**",
    ":!reports/golden_output_snapshot_v1.json",
    ":!reports/golden_output_snapshot_v2.json",
    ":!reports/golden_risk_contract_v1.json",
    ":!.env",
    ":!.env.*",
    ":!*.env",
]


def run_command(args: list[str]) -> str:
    result = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout.strip()
    error = result.stderr.strip()
    if result.returncode != 0:
        joined = " ".join(args)
        raise RuntimeError(f"Command failed ({joined}): {error or output}")
    return output


def git_branch() -> str:
    return run_command(["git", "branch", "--show-current"])


def git_commit() -> str:
    return run_command(["git", "rev-parse", "HEAD"])


def read_prompt_template() -> str:
    if PROMPT_TEMPLATE.exists():
        return PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return "Review the supplied World Cup Analyzer change. Do not write code."


def collect_working_diff() -> tuple[str, str]:
    stat = run_command(["git", "diff", "--stat", "--", *GIT_PATHSPECS])
    diff = run_command(["git", "diff", "--", *GIT_PATHSPECS])
    body = "\n\n".join(part for part in [stat, diff] if part)
    return body or "No working diff found.", "current git working diff"


def collect_last_commit() -> tuple[str, str]:
    stat = run_command(["git", "show", "--stat", "--oneline", "HEAD"])
    diff = run_command(["git", "show", "--", *GIT_PATHSPECS])
    return "\n\n".join(part for part in [stat, diff] if part), "last commit"


def collect_pr_diff(pr_number: int) -> tuple[str, str]:
    diff = run_command(["gh", "pr", "diff", str(pr_number)])
    return diff, f"GitHub PR #{pr_number}"


def collect_file(path: str) -> tuple[str, str]:
    input_path = (ROOT / path).resolve()
    try:
        input_path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("input file must be inside the repository") from exc
    if input_path.name == ".env" or input_path.suffix == ".env":
        raise ValueError("refusing to review local environment secret files")
    text = input_path.read_text(encoding="utf-8")
    return text, str(input_path.relative_to(ROOT))


def collect_input(args: argparse.Namespace) -> tuple[str, str]:
    if args.mode == "working-diff":
        return collect_working_diff()
    if args.mode == "last-commit":
        return collect_last_commit()
    if args.mode == "pr":
        if args.pr_number is None:
            raise ValueError("--pr-number is required for --mode pr")
        return collect_pr_diff(args.pr_number)
    if args.mode == "file":
        if not args.input_file:
            raise ValueError("--input-file is required for --mode file")
        return collect_file(args.input_file)
    raise ValueError(f"unsupported mode: {args.mode}")


def build_prompt(review_input: str, source: str) -> str:
    template = read_prompt_template()
    return f"""{template}

## Review Input Source

{source}

## Review Input

```text
{review_input}
```
"""


def extract_text(message: object) -> str:
    text_parts: list[str] = []
    for block in getattr(message, "content", []):
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text.strip())
    return "\n\n".join(part for part in text_parts if part).strip()


def write_outputs(
    review_text: str,
    metadata: dict[str, object],
    timestamp: str,
) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    markdown_path = OUTPUT_DIR / f"claude_review_{timestamp}.md"
    metadata_path = OUTPUT_DIR / f"claude_review_{timestamp}.json"
    markdown_path.write_text(review_text + "\n", encoding="utf-8")
    metadata["output_markdown_path"] = str(markdown_path.relative_to(ROOT))
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return markdown_path, metadata_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=["working-diff", "last-commit", "file", "pr"],
        default="working-diff",
    )
    parser.add_argument("--input-file")
    parser.add_argument("--pr-number", type=int)
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("CLAUDE_REVIEW_READY: NO_KEY")
        print("Set the Anthropic key in the local shell or ignored .env before running review.")
        return 1

    args = parse_args()
    model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)

    try:
        review_input, source = collect_input(args)
        prompt = build_prompt(review_input, source)
        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=1600,
            messages=[{"role": "user", "content": prompt}],
        )
        review_text = extract_text(message) or "No review text returned."
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        metadata = {
            "timestamp": timestamp,
            "mode": args.mode,
            "model": model,
            "git_branch": git_branch(),
            "git_commit": git_commit(),
            "input_source": source,
            "safety_exclusions_used": SAFETY_EXCLUSIONS,
        }
        markdown_path, metadata_path = write_outputs(review_text, metadata, timestamp)
    except Exception as exc:
        print("CLAUDE_REVIEW_READY: FAILED")
        print(f"Error: {exc.__class__.__name__}: {exc}")
        return 2

    print("CLAUDE_REVIEW_READY: YES")
    print(f"Review: {markdown_path.relative_to(ROOT)}")
    print(f"Metadata: {metadata_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
