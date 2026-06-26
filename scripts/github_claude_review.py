#!/usr/bin/env python3
"""Run GitHub-mediated Claude review on a sanitized review packet."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from anthropic import Anthropic


ROOT = Path(__file__).resolve().parents[1]
PROMPT_TEMPLATE = ROOT / "docs" / "CLAUDE_REVIEW_PROMPT_TEMPLATE.md"
OUTPUT_DIR = ROOT / "reports" / "claude_reviews"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
ALLOWED_PACKET_RE = re.compile(r"^reports/claude_reviews/[^/]+_packet\.md$")
FORBIDDEN_PREFIXES = ("data/", "modules/")
FORBIDDEN_EXACT = {
    "app.py",
    ".env",
    "reports/golden_output_snapshot_v1.json",
    "reports/golden_output_snapshot_v2.json",
    "reports/golden_risk_contract_v1.json",
}


def relative_repo_path(path_text: str) -> Path:
    candidate = (ROOT / path_text).resolve()
    try:
        relative = candidate.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("input file must be inside repository") from exc
    relative_text = relative.as_posix()
    if not ALLOWED_PACKET_RE.fullmatch(relative_text):
        raise ValueError("input file must match reports/claude_reviews/*_packet.md")
    if relative_text in FORBIDDEN_EXACT or relative.name.startswith(".env") or relative.name.endswith(".env"):
        raise ValueError("refusing forbidden or secret input path")
    if any(relative_text.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        raise ValueError("refusing product or data input path")
    if not candidate.is_file():
        raise FileNotFoundError(relative_text)
    return relative


def read_text(path: Path) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def build_prompt(packet_text: str, source: str) -> str:
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return (
        f"{template}\n\n"
        "## Review Input Source\n\n"
        f"{source}\n\n"
        "## Current Sanitized Review Packet\n\n"
        f"{packet_text}\n"
    )


def extract_text(message: Any) -> str:
    text_parts: list[str] = []
    for block in getattr(message, "content", []):
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text.strip())
    return "\n\n".join(part for part in text_parts if part).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", required=True)
    parser.add_argument("--round", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("missing required GitHub Actions secret")

    round_text = str(args.round).strip()
    if not round_text.isdigit():
        raise ValueError("--round must be numeric")

    input_path = relative_repo_path(args.input_file)
    packet_text = read_text(input_path)
    prompt = build_prompt(packet_text, input_path.as_posix())
    model = os.getenv("ANTHROPIC_MODEL") or DEFAULT_MODEL

    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=2400,
        messages=[{"role": "user", "content": prompt}],
    )
    review_text = extract_text(message) or "No review text returned."

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    markdown_path = OUTPUT_DIR / f"round_{round_text}_claude_review.md"
    metadata_path = OUTPUT_DIR / f"round_{round_text}_claude_review.json"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    metadata = {
        "timestamp": timestamp,
        "round": int(round_text),
        "input_file": input_path.as_posix(),
        "model": model,
        "review_markdown": markdown_path.relative_to(ROOT).as_posix(),
        "reviewer": "github-actions-claude",
        "output_mode": "artifact-only",
    }

    markdown_path.write_text(review_text.rstrip() + "\n", encoding="utf-8")
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"review_markdown={markdown_path.relative_to(ROOT).as_posix()}")
    print(f"review_metadata={metadata_path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
