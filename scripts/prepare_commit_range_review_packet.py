#!/usr/bin/env python3
"""Prepare a sanitized packet from a git commit range for manual Claude review.

This helper is for the manual GitHub Actions Claude Review workflow only. It
does not call Claude APIs, create branches, open pull requests, commit, push,
merge, or trigger any workflow. It reads git metadata and selected safe text
snippets, then writes one packet under reports/claude_reviews for the current
runner workspace.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "reports" / "claude_reviews"
OUTPUT_PATH = OUTPUT_DIR / "commit_range_review_packet.md"
MAX_PACKET_BYTES = 20 * 1024
MAX_SNIPPET_LINES_PER_FILE = 80
CONTEXT_LINES = 4
COMMIT_RANGE_RE = re.compile(r"^[A-Za-z0-9._/\-^~]+\.\.[A-Za-z0-9._/\-^~]+$")
SECRET_PATTERNS = [
    re.compile(r"sk-ant", re.IGNORECASE),
    re.compile(r"ghp_", re.IGNORECASE),
    re.compile(r"github_pat_", re.IGNORECASE),
    re.compile(r"(?m)^[A-Z0-9_]*KEY\s*="),
    re.compile(r"(?m)^[A-Z0-9_]*TOKEN\s*="),
]
FORBIDDEN_PATH_PREFIXES = (
    ".env",
    ".runtime/",
    ".streamlit/",
    "data/",
    "logs/",
)
FORBIDDEN_PATH_PARTS = (
    "/.env",
    "/data/performance_logs/",
    "/__pycache__/",
)
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
}
SNIPPET_KEYWORDS = (
    "TPB",
    "概率标签",
    "覆盖说明",
    "盘口观察",
    "比赛投资分",
    "推荐金额",
    "结果分布观察",
    "Polymarket",
    "workflow_dispatch",
    "review_mode",
    "commit_range",
    "pytest",
    "manual",
    "API-Football",
    "score_layer",
    "execution_layer",
    "explanation_layer",
    "portfolio_risk_gate",
    "rank1_eligibility_check",
    "load_api_key",
)
REDACTIONS = {
    "ANTHROPIC_API_KEY": "ANTHROPIC_SECRET_NAME",
    "API_FOOTBALL_KEY": "API_FOOTBALL_SECRET_NAME",
}


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def sanitize_text(text: str) -> str:
    sanitized = text
    for needle, replacement in REDACTIONS.items():
        sanitized = sanitized.replace(needle, replacement)
    return sanitized


def indent_block(text: str) -> str:
    if not text.strip():
        return "    none"
    return "\n".join(f"    {line}" for line in text.splitlines())


def reject_secret_like_text(label: str, text: str) -> None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise ValueError(f"{label} appears to contain secret-like text")


def validate_commit_range(commit_range: str) -> None:
    if not COMMIT_RANGE_RE.fullmatch(commit_range):
        raise ValueError("commit range must look like base..head and contain no whitespace")
    run_git(["rev-list", "--count", commit_range])


def parse_changed_paths(name_status_text: str) -> list[str]:
    paths: list[str] = []
    for line in name_status_text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("D"):
            paths.append(parts[-1])
        elif status.startswith("R") and len(parts) >= 3:
            paths.append(parts[-1])
        elif len(parts) >= 2:
            paths.append(parts[-1])
    return sorted(dict.fromkeys(paths))


def path_is_forbidden(path: str) -> bool:
    if any(path.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
        return True
    return any(part in f"/{path}" for part in FORBIDDEN_PATH_PARTS)


def should_include_snippet(path: str) -> bool:
    if path_is_forbidden(path):
        return False
    file_path = ROOT / path
    if not file_path.is_file():
        return False
    if file_path.suffix not in TEXT_SUFFIXES:
        return False
    if file_path.stat().st_size > 24 * 1024:
        return False
    return True


def selected_snippet(path: str) -> str:
    file_path = ROOT / path
    text = sanitize_text(file_path.read_text(encoding="utf-8", errors="replace"))
    reject_secret_like_text(path, text)
    lines = text.splitlines()
    selected_indexes: set[int] = set()
    for index, line in enumerate(lines):
        if any(keyword in line for keyword in SNIPPET_KEYWORDS):
            start = max(0, index - CONTEXT_LINES)
            end = min(len(lines), index + CONTEXT_LINES + 1)
            selected_indexes.update(range(start, end))

    if not selected_indexes:
        selected_indexes.update(range(min(len(lines), 20)))

    ordered_indexes = sorted(selected_indexes)[:MAX_SNIPPET_LINES_PER_FILE]
    rendered: list[str] = []
    previous_index = None
    for index in ordered_indexes:
        if previous_index is not None and index != previous_index + 1:
            rendered.append("...")
        rendered.append(f"{index + 1}: {lines[index]}")
        previous_index = index
    return "\n".join(rendered)


def build_packet(commit_range: str) -> str:
    commit_log = sanitize_text(run_git(["log", "--oneline", commit_range]))
    name_status = sanitize_text(run_git(["diff", "--name-status", commit_range]))
    stat = sanitize_text(run_git(["diff", "--stat", commit_range]))
    changed_paths = parse_changed_paths(name_status)

    snippet_sections: list[str] = []
    skipped_paths: list[str] = []
    for path in changed_paths:
        if should_include_snippet(path):
            snippet = selected_snippet(path)
            snippet_sections.append(f"## Snippet for {path}\n\n{indent_block(snippet)}")
        else:
            skipped_paths.append(path)

    changed_files = "\n".join(f"- {path}" for path in changed_paths) or "- none"
    skipped = "\n".join(f"- {path}" for path in skipped_paths) or "- none"
    snippets = "\n\n".join(snippet_sections) or "No text snippets selected."

    packet = f"""# Task

Perform a single-round, read-only Claude Review for a git commit range generated inside the manual workflow_dispatch runner.

Claude must review only the sanitized commit-range summary and snippets below. Claude must not write patches, modify code, create branches, open pull requests, merge, rebase, trigger workflows, or request a second review round.

# Changed files

Commit range: `{commit_range}`

Commit log:

{indent_block(commit_log)}

Changed file list:

{changed_files}

Diff stat:

{indent_block(stat)}

Skipped from snippets because the path is protected, missing, binary, unsupported, or too large:

{skipped}

# Product code impact

Review whether the changed files preserve the current TPB-only architecture and whether any active decision path risk is visible from the summarized changes and snippets.

Expected decision chain:

API-Football 1X2 odds -> TPB -> betting_confidence -> investment_score -> stake -> UI/report display.

Expected constraints:

- No EV or ROI should influence decision output.
- No hybrid system should influence decision output.
- No scenario ranking or scenario shadow output should influence score, stake, ranking, or risk.
- No risk gate should block TPB recommendations.
- Polymarket must remain read-only comparison or observation.
- Manual API diagnostics must not run in CI or pytest collection.

# Protected files

The packet generator excludes secret and runtime paths, including .env files, .streamlit secrets, data, data/performance_logs, logs, and runtime output.

This packet contains no runtime logs, performance logs, data cache content, API key values, or raw patch blocks.

# Validation

This packet was generated by scripts/prepare_commit_range_review_packet.py using local git metadata in the GitHub Actions runner.

Claude should review the snippets for semantic and workflow risk only. Claude should not treat omitted protected paths as reviewed code.

# Secret scan

The packet generator redacts known secret environment variable names and rejects token-like text before writing this packet.

No API key values, GitHub tokens, Anthropic tokens, .env content, or runtime logs should be present.

# Gate status

PORTFOLIO_EXTRACTION: BLOCKED.

BACKTEST_READY: NO.

Claude Review mode: read-only, single round only.

Branch mode: dev-clean only. No branch creation, pull request, merge, rebase, or old multi-round Claude loop.

# Proposed next task

No automatic next task should execute from this review.

Claude should classify any finding as:

- MUST_FIX: active decision path, CI safety, secret safety, or workflow authority risk.
- POLISH: wording, label clarity, or documentation improvement only.
- NO_ACTION: acceptable as-is.

Review questions:

1. Does the commit range preserve TPB-only decision semantics?
2. Is any legacy EV, ROI, hybrid, scenario shadow, risk gate, or portfolio optimizer influence visible?
3. Are workflow changes still manual-only and compatible with the lightweight Codex-Claude loop?
4. Is there any secret, data, or runtime artifact exposure risk?
5. Is there any active decision path risk?

# Selected file snippets

{snippets}
"""
    reject_secret_like_text("generated packet", packet)
    encoded = packet.encode("utf-8")
    if len(encoded) > MAX_PACKET_BYTES:
        raise ValueError(f"generated packet exceeds {MAX_PACKET_BYTES} bytes")
    return packet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit-range", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    commit_range = args.commit_range.strip()
    validate_commit_range(commit_range)
    packet = build_packet(commit_range)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(packet, encoding="utf-8")
    print(OUTPUT_PATH.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
