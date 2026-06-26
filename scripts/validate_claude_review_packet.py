#!/usr/bin/env python3
"""Validate a sanitized Claude review packet before GitHub-mediated review."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = ROOT / "reports" / "claude_reviews"
REPORT_PATH = PACKET_DIR / "packet_validation_report.md"
MAX_PACKET_BYTES = 20 * 1024

REQUIRED_SECTIONS = [
    "Task",
    "Changed files",
    "Product code impact",
    "Protected files",
    "Validation",
    "Secret scan",
    "Gate status",
    "Proposed next task",
]

FORBIDDEN_PATTERNS = [
    ("anthropic_api_key_reference", re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE)),
    ("anthropic_token_prefix", re.compile(r"sk-ant", re.IGNORECASE)),
    ("github_classic_token_prefix", re.compile(r"ghp_", re.IGNORECASE)),
    ("github_fine_grained_token_prefix", re.compile(r"github_pat_", re.IGNORECASE)),
    ("env_assignment", re.compile(r"^[A-Z0-9_]*KEY\s*=", re.MULTILINE)),
    ("raw_git_diff", re.compile(r"^diff --git ", re.MULTILINE)),
    ("patch_block", re.compile(r"```(?:diff|patch)?\s*$", re.IGNORECASE | re.MULTILINE)),
    ("full_app_marker", re.compile(r"(?m)^#\s*app\.py\s*$|^import streamlit\b")),
    ("module_path_dump", re.compile(r"(?m)^(?:modules/|###\s+modules/)")),
    ("data_history_content", re.compile(r"data/history/|\"history\"\\s*:", re.IGNORECASE)),
    ("golden_json_content", re.compile(r"\"risk_contract_v1\"\s*:|\"contracts\"\s*:\s*\[", re.IGNORECASE)),
]


@dataclass
class ValidationResult:
    packet_path: str
    exists: bool
    under_review_dir: bool
    filename_ok: bool
    size_bytes: int
    size_ok: bool
    missing_sections: list[str]
    forbidden_findings: list[str]
    gate_fields_found: list[str]
    raw_diff_jin_approved: bool

    @property
    def passed(self) -> bool:
        return (
            self.exists
            and self.under_review_dir
            and self.filename_ok
            and self.size_ok
            and not self.missing_sections
            and not self.forbidden_findings
            and {"PORTFOLIO_EXTRACTION", "BACKTEST_READY"}.issubset(set(self.gate_fields_found))
        )


def relative_repo_path(path_text: str) -> tuple[Path, str]:
    candidate = (ROOT / path_text).resolve()
    try:
        relative = candidate.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("packet path must be inside this repository") from exc
    return candidate, relative.as_posix()


def section_present(text: str, section: str) -> bool:
    pattern = re.compile(rf"^#+\s*(?:\d+\.\s*)?{re.escape(section)}\b", re.IGNORECASE | re.MULTILINE)
    return bool(pattern.search(text))


def validate_packet(path_text: str) -> ValidationResult:
    packet_path, relative_text = relative_repo_path(path_text)
    exists = packet_path.is_file()
    under_review_dir = False
    try:
        packet_path.relative_to(PACKET_DIR.resolve())
        under_review_dir = True
    except ValueError:
        under_review_dir = False

    filename_ok = relative_text.startswith("reports/claude_reviews/") and relative_text.endswith("_review_packet.md")
    size_bytes = packet_path.stat().st_size if exists else 0
    size_ok = exists and size_bytes <= MAX_PACKET_BYTES
    text = packet_path.read_text(encoding="utf-8") if exists else ""

    missing_sections = [section for section in REQUIRED_SECTIONS if not section_present(text, section)]
    raw_diff_jin_approved = "JIN_APPROVED_RAW_DIFF: YES" in text
    forbidden_findings: list[str] = []
    for name, pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            if name == "raw_git_diff" and raw_diff_jin_approved:
                continue
            forbidden_findings.append(name)

    gate_fields_found = [
        gate for gate in ("PORTFOLIO_EXTRACTION", "BACKTEST_READY") if re.search(rf"\b{gate}\b", text)
    ]

    return ValidationResult(
        packet_path=relative_text,
        exists=exists,
        under_review_dir=under_review_dir,
        filename_ok=filename_ok,
        size_bytes=size_bytes,
        size_ok=size_ok,
        missing_sections=missing_sections,
        forbidden_findings=forbidden_findings,
        gate_fields_found=gate_fields_found,
        raw_diff_jin_approved=raw_diff_jin_approved,
    )


def write_report(result: ValidationResult) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pass_text = "PASS" if result.passed else "FAIL"
    safe_text = "YES" if result.passed else "NO"
    missing = "\n".join(f"- {section}" for section in result.missing_sections) or "- none"
    findings = "\n".join(f"- {finding}" for finding in result.forbidden_findings) or "- none"
    gates = "\n".join(f"- {gate}" for gate in result.gate_fields_found) or "- none"

    report = f"""# Claude Review Packet Validation Report

## Packet

- Path: `{result.packet_path}`
- Exists: {'yes' if result.exists else 'no'}
- Under `reports/claude_reviews/`: {'yes' if result.under_review_dir else 'no'}
- Filename ends with `_review_packet.md`: {'yes' if result.filename_ok else 'no'}

## Result

- Validation result: {pass_text}
- SAFE_FOR_CLAUDE_REVIEW: {safe_text}

## Size

- Size bytes: {result.size_bytes}
- Maximum bytes: {MAX_PACKET_BYTES}
- Size result: {'PASS' if result.size_ok else 'FAIL'}

## Missing Sections

{missing}

## Forbidden Pattern Findings

{findings}

## Gate Fields Found

{gates}

## Raw Diff Status

- Raw full git diff found without Jin approval: {'no' if 'raw_git_diff' not in result.forbidden_findings else 'yes'}
- Jin-approved raw diff marker present: {'yes' if result.raw_diff_jin_approved else 'no'}

## Recommendation

- SAFE_FOR_CLAUDE_REVIEW: {safe_text}
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet_file", help="Path to reports/claude_reviews/*_review_packet.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_packet(args.packet_file)
    write_report(result)
    print(f"CLAUDE_REVIEW_PACKET_VALIDATION: {'PASS' if result.passed else 'FAIL'}")
    print(f"SAFE_FOR_CLAUDE_REVIEW: {'YES' if result.passed else 'NO'}")
    print(f"REPORT: {REPORT_PATH.relative_to(ROOT).as_posix()}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
