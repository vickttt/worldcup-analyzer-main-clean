#!/usr/bin/env python3
"""Static guard for the locked Claude Review loop.

This script does not call GitHub, Claude, Anthropic, or any external service.
It only checks repository text files so CI can catch accidental workflow or
governance drift before a bad loop shape is merged into dev-clean.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_WORKFLOW = ROOT / ".github" / "workflows" / "claude-review.yml"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
AGENTS = ROOT / "AGENTS.md"
RUBRIC = ROOT / "reports" / "claude_reviews" / "CLAUDE_REVIEW_RUBRIC.md"
PROMPT_TEMPLATE = ROOT / "docs" / "CLAUDE_REVIEW_PROMPT_TEMPLATE.md"


def read(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing {label}: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"forbidden {label}: {needle}")


def verify_claude_workflow(text: str) -> None:
    require(text, "push:", "push trigger")
    require(text, "branches:", "branch filter")
    require(text, "- dev-clean", "dev-clean push trigger")
    require(text, "workflow_dispatch:", "manual workflow_dispatch trigger")
    forbid(text, "pull_request:", "pull_request Claude review trigger")

    require(text, 'packet_mode="commit_range"', "commit range packet mode")
    require(text, '${{ github.event_name }}', "event-name branch selection")
    require(text, '== "push"', "push event condition")
    require(text, 'commit_range=""', "push HEAD-bound default range")
    require(text, 'artifact_round="${{ github.run_number }}"', "numeric push artifact round")
    require(text, 'execute_claude_review="true"', "push-triggered Claude review")
    require(text, "artifact_round must be numeric", "numeric round validation")

    require(
        text,
        "scripts/prepare_commit_range_review_packet.py",
        "sanitized packet generation",
    )
    require(text, "Generated packet is not bound to current HEAD", "HEAD binding guard")
    require(text, "claude-review-packet-round-", "packet artifact upload")
    require(text, "python -m pip install anthropic", "Claude SDK install")
    require(text, "scripts/github_claude_review.py", "Claude review runner")
    require(text, "ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}", "GitHub secret source")
    require(text, "claude-review-result-round-", "Claude verdict artifact upload")

    for forbidden in (
        "git push",
        "git commit",
        "gh pr",
        "gh workflow run",
        "create-pull-request",
    ):
        forbid(text, forbidden, "workflow mutation command")


def verify_ci_workflow(text: str) -> None:
    require(
        text,
        "python scripts/verify_claude_review_loop.py",
        "CI Claude Review loop guard step",
    )


def verify_agents(text: str) -> None:
    require(text, "Claude Review Loop Lock:", "AGENTS loop lock section")
    require(text, "Codex commit -> push dev-clean -> GitHub Actions", "locked flow")
    require(text, "sanitized HEAD^..HEAD", "HEAD-bound packet invariant")
    require(text, "must not trigger Claude API review", "pull_request ban")
    require(text, "ANTHROPIC_API_KEY", "secret source invariant")
    require(text, "change reasoning quality", "Claude change reasoning responsibility")
    require(text, "correctness, necessity, and simplicity", "correctness and necessity review scope")
    require(
        text,
        "scripts/verify_claude_review_loop.py",
        "guard script governance reference",
    )


def verify_change_reasoning_review(text: str, label: str) -> None:
    require(text, "Change Reasoning Assessment", f"{label} change reasoning section")
    require(text, "Over-Engineering Risk", f"{label} over-engineering check")
    require(text, "Redundant Abstraction", f"{label} redundant abstraction check")
    require(text, "Long-Term Architecture Fit", f"{label} architecture fit check")
    require(text, "Maintainability / Explainability Impact", f"{label} maintainability check")


def main() -> int:
    verify_claude_workflow(read(CLAUDE_WORKFLOW))
    verify_ci_workflow(read(CI_WORKFLOW))
    verify_agents(read(AGENTS))
    verify_change_reasoning_review(read(RUBRIC), "rubric")
    verify_change_reasoning_review(read(PROMPT_TEMPLATE), "prompt template")
    print("Claude Review loop guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
