#!/usr/bin/env python3
"""Prepare a sanitized packet for a manual, read-only Claude review.

This tool is manually triggered or explicitly authorized only. It does not call
Claude APIs, create branches, open pull requests, commit, push, merge, or act as
an entrypoint for the old automatic review loop. Generated packets may only
support a lightweight, single-round, read-only Claude review under AGENTS.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "reports" / "claude_reviews"
FORBIDDEN_TEXT_MARKERS = [
    "diff --git",
    "-----BEGIN",
]


def reject_unsafe_text(label: str, text: str) -> None:
    lowered = text.lower()
    if "sk-ant" in text or "ghp_" in text or "github_pat_" in text:
        raise ValueError(f"{label} appears to contain a token-like value")
    if "anthropic_api_key" in lowered:
        raise ValueError(f"{label} references a secret environment variable")
    for marker in FORBIDDEN_TEXT_MARKERS:
        if marker in text:
            raise ValueError(f"{label} appears to contain raw diff or key material")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round", required=True, type=int)
    parser.add_argument("--task-title", required=True)
    parser.add_argument("--changed-files-summary", required=True)
    parser.add_argument("--validation-summary", required=True)
    parser.add_argument("--gate-status", required=True)
    parser.add_argument("--proposed-next-task", required=True)
    parser.add_argument("--product-code-impact", default="Product code modified: no.")
    parser.add_argument("--protected-files-status", default="Protected path diff checks returned no output.")
    parser.add_argument("--secret-scan-result", default="No real secrets found.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.round < 1:
        raise ValueError("--round must be positive")

    fields = {
        "task title": args.task_title,
        "changed files summary": args.changed_files_summary,
        "validation summary": args.validation_summary,
        "gate status": args.gate_status,
        "proposed next task": args.proposed_next_task,
        "product code impact": args.product_code_impact,
        "protected files status": args.protected_files_status,
        "secret scan result": args.secret_scan_result,
    }
    for label, text in fields.items():
        reject_unsafe_text(label, text)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"round_{args.round}_review_packet.md"
    packet = f"""# Round {args.round} Sanitized Review Packet

## 1. Task Summary

{args.task_title}

## 2. Files Changed

{args.changed_files_summary}

## 3. Product Code Impact

{args.product_code_impact}

## 4. Protected Files Status

{args.protected_files_status}

## 5. Validation Summary

{args.validation_summary}

## 6. Secret Scan Result

{args.secret_scan_result}

## 7. Current Gates

{args.gate_status}

## 8. Proposed Next Safe Codex Task

{args.proposed_next_task}
"""
    output_path.write_text(packet, encoding="utf-8")
    print(output_path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
