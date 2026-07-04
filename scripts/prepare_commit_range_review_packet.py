#!/usr/bin/env python3
"""Prepare a sanitized packet from a git commit range for Claude review.

This helper only prepares sanitized review input. It does not call Claude APIs,
create branches, open pull requests, commit, push, merge, or trigger any
workflow. It reads git metadata and selected safe text snippets, then writes one
packet under the system temp directory or RUNNER_TEMP for the current runner
workspace.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.getenv("RUNNER_TEMP") or tempfile.gettempdir()) / "worldcup2026_review_packets"
RUBRIC_PATH = ROOT / "reports" / "claude_reviews" / "CLAUDE_REVIEW_RUBRIC.md"
MAX_PACKET_BYTES = 48 * 1024
MAX_SNIPPET_LINES_PER_FILE = 80
CONTEXT_LINES = 4
COMMIT_RANGE_RE = re.compile(r"^[A-Za-z0-9._/\-^~]+\.\.[A-Za-z0-9._/\-^~]+$")
SECRET_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}", re.IGNORECASE),
    re.compile(r"ghp_[A-Za-z0-9]{20,}", re.IGNORECASE),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}", re.IGNORECASE),
    re.compile(r"(?m)^\s*[A-Z0-9_]*KEY\s*=\s*['\"]?[A-Za-z0-9_./+=:-]{16,}['\"]?\s*$"),
    re.compile(r"(?m)^\s*[A-Z0-9_]*TOKEN\s*=\s*['\"]?[A-Za-z0-9_./+=:-]{16,}['\"]?\s*$"),
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


def resolve_commit(expr: str) -> str:
    return run_git(["rev-parse", "--verify", f"{expr}^{{commit}}"])


def current_head() -> str:
    return resolve_commit("HEAD")


def current_head_parent() -> str:
    return resolve_commit("HEAD^")


def head_bound_commit_range(raw_commit_range: str | None) -> tuple[str, str]:
    head = current_head()
    parent = current_head_parent()
    normalized = f"{head}^..{head}"
    if not raw_commit_range:
        return normalized, head

    if not COMMIT_RANGE_RE.fullmatch(raw_commit_range):
        raise ValueError("commit range must look like base..head and contain no whitespace")
    left_expr, right_expr = raw_commit_range.split("..", 1)
    if resolve_commit(right_expr) != head:
        raise ValueError("commit range head must resolve to current git HEAD")
    if resolve_commit(left_expr) != parent:
        raise ValueError("commit range base must resolve to current git HEAD parent")
    return normalized, head


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
    run_git(["rev-list", "--count", commit_range])


def read_rubric() -> str:
    if not RUBRIC_PATH.is_file():
        raise FileNotFoundError("missing reports/claude_reviews/CLAUDE_REVIEW_RUBRIC.md")
    rubric = sanitize_text(RUBRIC_PATH.read_text(encoding="utf-8"))
    reject_secret_like_text("Claude review rubric", rubric)
    if "CLAUDE_REVIEW_RUBRIC" not in rubric:
        raise ValueError("rubric file must contain CLAUDE_REVIEW_RUBRIC marker")
    return rubric.strip()


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
    head = current_head()
    rubric = read_rubric()
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

    packet = f"""# Embedded Claude Review Rubric

{rubric}

# Commit Range Rule

Git range A..B excludes commit A and includes commits after A through B.

To include commit A itself, use A^..B.

If the user says "include commit A through B", Codex must convert the range to A^..B.

If the user gives raw A..B, Codex must report that A itself is excluded.

Current raw commit range: `{commit_range}`

# HEAD Binding

Current git HEAD used for packet generation: `{head}`

Normalized packet range: `{commit_range}`

This packet is freshly generated from the current git HEAD. Cached packet files, previous workflow artifacts, and user-supplied stale commit ranges are not used.

# Task

Prepare a structured, sanitized packet for architecture review of this git commit range.

The packet is generated before review and may be used in either mode:

- Packet artifact mode: upload this sanitized packet as a GitHub Actions artifact without AI inference.
- Authorized Claude API review mode: after explicit user authorization for that workflow_dispatch run, send only this sanitized packet to Claude API and upload the read-only verdict artifact.

Any manual reviewer must review only the sanitized commit-range summary and snippets below. The reviewer must not write patches, modify code, create branches, open pull requests, merge, rebase, trigger workflows, or request an automatic second review round.

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

# System architecture summary

## TPB summary

TPB is the baseline probability anchor derived from API-Football 1X2 odds and normalized bookmaker consensus. TPB anchors probability interpretation, investment score, deterministic stake mapping, and UI/report display. TPB must not be replaced, overridden, mutated by user input, or converted into an EV/ROI model.

## Market structure summary

Market Structure uses API-Football market structure to produce bounded analytical signals such as Directional Strength, Market Conflict, Efficiency, Volatility, and Upset Probability. These signals explain market structure and may be consumed by system synthesis, but they must not override TPB, mutate raw odds, or act as profit optimization.

## Scenario summary

Scenario Engine decomposes probability space into the fixed S1-S6 scenario taxonomy and may produce bounded deterministic scenario weights, risk surface, coverage map, and scenario-to-portfolio mapping. Scenario weights may influence System Portfolio and Ranking only through explainable bounded heuristics. Scenario must not use user input, predict exact scores, calculate EV/ROI, or become a black-box optimizer.

## Portfolio summary

System Portfolio is a coverage and synthesis layer based on TPB baseline, Market Structure signals, and bounded Scenario weights. It may express main, defensive, and high-variance coverage structures. It must not use user odds, execution behavior, EV/ROI, or legacy optimizer logic.

## Ranking summary

System Ranking is system-only ordering of model-generated betting structures. It may use TPB baseline strength, market structure signals, and bounded scenario weights. It must not use user input, execution-layer data, EV/ROI ranking, profit optimization, or black-box scoring.

## Execution layer summary

Customer Execution Layer is display/evaluation only. User positions and odds may be used for Value Check, execution evaluation, and user-vs-system comparison. User input must never influence TPB, investment score, stake, coverage, system ranking, raw odds, API data, or system recommendation.

# Product code impact

Review whether the changed files preserve the current Multi-Layer Betting Intelligence System v2 architecture and whether any active decision path risk is visible from the summarized changes and snippets.

Expected system chain:

API-Football market data -> TPB baseline anchor -> Market Structure signal layer -> bounded Scenario weighting -> System Portfolio synthesis -> System Ranking -> deterministic stake display + UI/report display.

Expected constraints:

- No EV or ROI should influence decision output.
- No hybrid, scenario shadow, legacy optimizer, or risk-gate blocking path should influence output.
- Scenario weights must remain bounded, deterministic, explainable, and traceable to TPB and Market Structure.
- User execution input must never influence TPB, investment score, stake, coverage, system ranking, raw odds, API data, or system recommendation.
- Polymarket and user odds must remain read-only / display / comparison layers.
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

Packet mode: sanitized review input only.

Branch mode: dev-clean only. No branch creation, pull request, merge, rebase, or old multi-round Claude loop.

# Proposed next task

No automatic next task should execute from this review.

Claude should classify any finding as:

- MUST_FIX: active decision path, CI safety, secret safety, or workflow authority risk.
- POLISH: wording, label clarity, or documentation improvement only.
- NO_ACTION: acceptable as-is.

Review questions:

1. Does the commit range preserve the Multi-Layer Betting Intelligence System v2 boundaries?
2. Does TPB remain the probability anchor without being overridden by Market, Scenario, Portfolio, Ranking, or Execution?
3. Are Scenario weights bounded, deterministic, explainable, and free of EV/ROI/profit optimization behavior?
4. Is System Ranking free of user input, execution-layer data, EV/ROI, and black-box optimizer influence?
5. Is Customer Execution isolated from TPB, investment score, stake, coverage, ranking, raw odds, API data, and recommendation?
6. If workflow Claude API review mode is used, was it explicitly authorized, limited to this sanitized packet, and free of secrets/runtime data?
7. Is there any secret, data, runtime artifact, or protected-path exposure risk?
8. Is there any active decision path risk?

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
    parser.add_argument(
        "--commit-range",
        required=False,
        default="",
        help="Optional guard range. If provided, it must resolve to current HEAD^..HEAD.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    commit_range, head = head_bound_commit_range(args.commit_range.strip())
    validate_commit_range(commit_range)
    packet = build_packet(commit_range)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"commit_range_{head[:7]}_review_packet.md"
    output_path.write_text(packet, encoding="utf-8")
    print(output_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
