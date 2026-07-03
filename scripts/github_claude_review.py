#!/usr/bin/env python3
"""Manual, read-only GitHub/Claude review runner for one sanitized packet.

This tool must be manually triggered or explicitly authorized. It must not
modify code, create branches, open pull requests, commit, push, merge, or act
as an entrypoint for the old Issue -> Branch -> PR workflow. Use it only as a
single-round review tool in the lightweight Codex-Claude loop.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from anthropic import Anthropic, APIConnectionError, APITimeoutError
except ImportError:  # pragma: no cover - GitHub Actions installs anthropic before running this script.
    Anthropic = None

    class APIConnectionError(Exception):
        pass

    class APITimeoutError(Exception):
        pass

try:
    import httpx
except ImportError:  # pragma: no cover - dependency is installed with anthropic in GitHub Actions.
    httpx = None


ROOT = Path(__file__).resolve().parents[1]
PROMPT_TEMPLATE = ROOT / "docs" / "CLAUDE_REVIEW_PROMPT_TEMPLATE.md"
OUTPUT_DIR = ROOT / "reports" / "claude_reviews"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_TIMEOUT_SECONDS = 90.0
DEFAULT_MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = (2, 5, 10)
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


def parse_positive_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")
    return value


def parse_positive_float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")
    return value


def is_retryable_network_error(error: BaseException) -> bool:
    retryable_types: tuple[type[BaseException], ...] = (APITimeoutError, APIConnectionError)
    if httpx is not None:
        retryable_types = retryable_types + (httpx.ConnectTimeout, httpx.TransportError)
    if isinstance(error, retryable_types):
        return True
    text = str(error).lower()
    return any(
        phrase in text
        for phrase in (
            "handshake operation timed out",
            "connecttimeout",
            "connection timed out",
            "tls",
            "temporary failure",
            "network is unreachable",
            "connection reset",
        )
    )


def write_review_artifacts(
    round_text: str,
    input_path: Path,
    model: str,
    review_text: str,
    metadata_extra: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
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
    if metadata_extra:
        metadata.update(metadata_extra)

    markdown_path.write_text(review_text.rstrip() + "\n", encoding="utf-8")
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return markdown_path, metadata_path


def network_unstable_review(error: BaseException, attempts: int, timeout_seconds: float) -> str:
    return (
        "## 1. Verdict\n\n"
        "NETWORK_UNSTABLE\n\n"
        "## 2. Scope Check\n\n"
        "Claude review could not be completed because the Anthropic API network call did not complete after retry.\n\n"
        "## 3. Product Code Safety\n\n"
        "Not reviewed by Claude. Codex must rely only on local validation until a review succeeds.\n\n"
        "## 4. Secret Safety\n\n"
        "No secret value is included in this artifact.\n\n"
        "## 5. Git / Branch / Worktree Safety\n\n"
        "AUTO_ADVANCE: NO\n\n"
        "## 6. GitHub / Docs Safety\n\n"
        "Do not treat this artifact as PASS or PASS_WITH_NOTES.\n\n"
        "## 7. Token Budget / Context Safety\n\n"
        "The sanitized packet was accepted by the review runner, but the external Claude call failed.\n\n"
        "## 8. Long-Term Goal Alignment\n\n"
        "GitHub workflow reliability remains the relevant goal.\n\n"
        "## 9. Codex Capability Recommendation\n\n"
        "Retry the Claude review later only after explicit user approval.\n\n"
        "## 10. Gate Status\n\n"
        "PORTFOLIO_EXTRACTION: BLOCKED\n\n"
        "BACKTEST_READY: NO\n\n"
        "## 11. Codex Reply Quality Check\n\n"
        "Codex must report the network failure explicitly.\n\n"
        "## 12. Next Codex Task\n\n"
        "NEXT_ACTION: manual single-round Claude review retry after user approval\n\n"
        "SYSTEM_HEALTH: BLOCKED\n\n"
        "## 13. Stop Conditions\n\n"
        f"Claude API network call failed after {attempts} attempt(s) with timeout {timeout_seconds:g}s. "
        f"Final error type: {type(error).__name__}."
    )


def request_claude_review(
    api_key: str,
    model: str,
    prompt: str,
    max_attempts: int,
    timeout_seconds: float,
) -> tuple[Any | None, BaseException | None, int]:
    if Anthropic is None:
        raise RuntimeError("missing required Python package: anthropic")
    client = Anthropic(api_key=api_key, timeout=timeout_seconds, max_retries=0)
    last_error: BaseException | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            message = client.messages.create(
                model=model,
                max_tokens=2400,
                messages=[{"role": "user", "content": prompt}],
            )
            return message, None, attempt
        except Exception as error:
            if not is_retryable_network_error(error):
                raise
            last_error = error
            if attempt >= max_attempts:
                return None, last_error, attempt
            backoff = RETRY_BACKOFF_SECONDS[min(attempt - 1, len(RETRY_BACKOFF_SECONDS) - 1)]
            print(
                f"Claude review network attempt {attempt}/{max_attempts} failed with "
                f"{type(error).__name__}; retrying in {backoff}s.",
                flush=True,
            )
            time.sleep(backoff)
    return None, last_error, max_attempts


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
    timeout_seconds = parse_positive_float_env("CLAUDE_REVIEW_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
    max_attempts = min(parse_positive_int_env("CLAUDE_REVIEW_MAX_ATTEMPTS", DEFAULT_MAX_ATTEMPTS), 3)

    message, network_error, attempts = request_claude_review(
        api_key=api_key,
        model=model,
        prompt=prompt,
        max_attempts=max_attempts,
        timeout_seconds=timeout_seconds,
    )
    if network_error is not None:
        review_text = network_unstable_review(network_error, attempts, timeout_seconds)
        markdown_path, metadata_path = write_review_artifacts(
            round_text,
            input_path,
            model,
            review_text,
            {
                "attempts": attempts,
                "network_error_type": type(network_error).__name__,
                "review_status": "NETWORK_UNSTABLE",
                "timeout_seconds": timeout_seconds,
            },
        )
        print("review_status=NETWORK_UNSTABLE")
        print(f"review_markdown={markdown_path.relative_to(ROOT).as_posix()}")
        print(f"review_metadata={metadata_path.relative_to(ROOT).as_posix()}")
        return 0

    review_text = extract_text(message) or "No review text returned."
    markdown_path, metadata_path = write_review_artifacts(
        round_text,
        input_path,
        model,
        review_text,
        {
            "attempts": attempts,
            "review_status": "COMPLETED",
            "timeout_seconds": timeout_seconds,
        },
    )
    print(f"review_markdown={markdown_path.relative_to(ROOT).as_posix()}")
    print(f"review_metadata={metadata_path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
