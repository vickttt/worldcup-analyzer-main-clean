#!/usr/bin/env python3
"""Smoke test for Claude API connectivity.

This script never stores or prints API keys. It reads credentials only from the
local process environment.
"""

from __future__ import annotations

import os

from anthropic import Anthropic


def main() -> int:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("CLAUDE_API_READY: NO_KEY")
        print("Set ANTHROPIC_API_KEY in your local shell before running this check.")
        return 1

    try:
        client = Anthropic()
        message = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
            max_tokens=8,
            messages=[{"role": "user", "content": "Reply with OK."}],
        )
    except Exception as exc:  # pragma: no cover - smoke-test error path
        print("CLAUDE_API_READY: FAILED")
        print(f"Error: {exc.__class__.__name__}: {exc}")
        return 2

    text_parts = []
    for block in message.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text.strip())

    print("CLAUDE_API_READY: YES")
    print("Response:", " ".join(text_parts).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
