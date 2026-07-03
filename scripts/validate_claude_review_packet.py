#!/usr/bin/env python3
"""Validate a sanitized Claude review packet with static local checks only.

This tool does not call Claude APIs, create branches, open pull requests,
commit, push, merge, or define workflow authority. It only checks whether a
packet is suitable for a lightweight, single-round, read-only Claude review
under AGENTS.md.
"""

from __future__ import annotations

import argparse
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = ROOT / "reports" / "claude_reviews"
REPORT_PATH = PACKET_DIR / "packet_validation_report.md"
MAX_PACKET_BYTES = 20 * 1024
DEFAULT_MODEL_CLASS = "haiku"
DEFAULT_EXPECTED_OUTPUT_TOKENS = 1200
DEFAULT_MAX_ESTIMATED_COST_USD = 0.20
LARGE_PACKET_INPUT_TOKEN_WARNING = 10_000
PLANNING_BUDGET_USD = 20.00

MODEL_PRICING_USD_PER_MILLION = {
    "haiku": {
        "input": 1.00,
        "output": 5.00,
    },
    "sonnet": {
        "input": 3.00,
        "output": 15.00,
    },
}

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
class BudgetEstimate:
    character_count: int
    estimated_input_tokens: int
    expected_output_tokens: int
    model_class: str
    input_price_per_million: float
    output_price_per_million: float
    estimated_input_cost_usd: float
    estimated_output_cost_usd: float
    estimated_total_cost_usd: float
    threshold_usd: float
    override_used: bool
    config_findings: list[str]

    @property
    def over_budget(self) -> bool:
        return self.estimated_total_cost_usd > self.threshold_usd

    @property
    def large_packet_warning(self) -> bool:
        return self.estimated_input_tokens > LARGE_PACKET_INPUT_TOKEN_WARNING

    @property
    def budget_passed(self) -> bool:
        return not self.config_findings and (not self.over_budget or self.override_used)

    @property
    def status_text(self) -> str:
        if self.config_findings:
            return "FAIL"
        if not self.over_budget:
            return "PASS"
        if self.override_used:
            return "OVERRIDE_PASS"
        return "FAIL"


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
    budget: BudgetEstimate

    @property
    def passed(self) -> bool:
        return (
            self.exists
            and self.under_review_dir
            and self.filename_ok
            and self.size_ok
            and not self.missing_sections
            and not self.forbidden_findings
            and self.budget.budget_passed
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


def parse_positive_int_env(name: str, default: int, findings: list[str]) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        return default
    try:
        value = int(raw_value)
    except ValueError:
        findings.append(f"{name} must be an integer")
        return default
    if value <= 0:
        findings.append(f"{name} must be greater than 0")
        return default
    return value


def parse_positive_float_env(name: str, default: float, findings: list[str]) -> float:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        return default
    try:
        value = float(raw_value)
    except ValueError:
        findings.append(f"{name} must be a number")
        return default
    if value <= 0:
        findings.append(f"{name} must be greater than 0")
        return default
    return value


def normalize_model_class(findings: list[str]) -> str:
    model_class = (os.getenv("CLAUDE_REVIEW_MODEL_CLASS") or DEFAULT_MODEL_CLASS).strip().lower()
    if model_class not in MODEL_PRICING_USD_PER_MILLION:
        findings.append(
            "CLAUDE_REVIEW_MODEL_CLASS must be one of: "
            + ", ".join(sorted(MODEL_PRICING_USD_PER_MILLION))
        )
        return DEFAULT_MODEL_CLASS
    return model_class


def estimate_budget(text: str, size_bytes: int) -> BudgetEstimate:
    findings: list[str] = []
    model_class = normalize_model_class(findings)
    expected_output_tokens = parse_positive_int_env(
        "CLAUDE_REVIEW_EXPECTED_OUTPUT_TOKENS",
        DEFAULT_EXPECTED_OUTPUT_TOKENS,
        findings,
    )
    threshold_usd = parse_positive_float_env(
        "CLAUDE_REVIEW_MAX_ESTIMATED_COST_USD",
        DEFAULT_MAX_ESTIMATED_COST_USD,
        findings,
    )
    override_used = os.getenv("ALLOW_CLAUDE_REVIEW_OVER_BUDGET") == "1"
    character_count = len(text)
    estimated_input_tokens = math.ceil(max(character_count, size_bytes) / 4)
    pricing = MODEL_PRICING_USD_PER_MILLION[model_class]
    estimated_input_cost_usd = estimated_input_tokens / 1_000_000 * pricing["input"]
    estimated_output_cost_usd = expected_output_tokens / 1_000_000 * pricing["output"]
    estimated_total_cost_usd = estimated_input_cost_usd + estimated_output_cost_usd

    return BudgetEstimate(
        character_count=character_count,
        estimated_input_tokens=estimated_input_tokens,
        expected_output_tokens=expected_output_tokens,
        model_class=model_class,
        input_price_per_million=pricing["input"],
        output_price_per_million=pricing["output"],
        estimated_input_cost_usd=estimated_input_cost_usd,
        estimated_output_cost_usd=estimated_output_cost_usd,
        estimated_total_cost_usd=estimated_total_cost_usd,
        threshold_usd=threshold_usd,
        override_used=override_used,
        config_findings=findings,
    )


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
    budget = estimate_budget(text, size_bytes)

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
        budget=budget,
    )


def write_report(result: ValidationResult) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pass_text = "PASS" if result.passed else "FAIL"
    safe_text = "YES" if result.passed else "NO"
    missing = "\n".join(f"- {section}" for section in result.missing_sections) or "- none"
    findings = "\n".join(f"- {finding}" for finding in result.forbidden_findings) or "- none"
    gates = "\n".join(f"- {gate}" for gate in result.gate_fields_found) or "- none"
    config_findings = "\n".join(f"- {finding}" for finding in result.budget.config_findings) or "- none"
    large_packet_warning = (
        "yes, reduce packet size or summarize before review" if result.budget.large_packet_warning else "no"
    )
    over_budget_action = (
        "Reduce packet size, send summaries/diffs only, use Haiku for docs/report review, "
        "or set ALLOW_CLAUDE_REVIEW_OVER_BUDGET=1 only after Jin-approved exception."
    )

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

## Cost Budget Estimate

- Packet character count: {result.budget.character_count}
- Estimated input tokens: {result.budget.estimated_input_tokens}
- Expected output tokens: {result.budget.expected_output_tokens}
- Assumed model class: {result.budget.model_class}
- Input price per 1M tokens: ${result.budget.input_price_per_million:.2f}
- Output price per 1M tokens: ${result.budget.output_price_per_million:.2f}
- Estimated input cost: ${result.budget.estimated_input_cost_usd:.6f}
- Estimated output cost: ${result.budget.estimated_output_cost_usd:.6f}
- Estimated cost per round: ${result.budget.estimated_total_cost_usd:.6f}
- Per-round threshold: ${result.budget.threshold_usd:.2f}
- Budget status: {result.budget.status_text}
- Override used: {'yes' if result.budget.override_used else 'no'}
- Large packet warning: {large_packet_warning}
- Reminder: $0.20 is the per-round guardrail. $20 is the total planning budget.

## Cost Policy

- Haiku is default for docs/report-only review.
- Sonnet should be reserved for product-code or high-risk API/cache/security changes.
- Do not send full repo, full data files, golden JSON, old logs, or full prior Claude artifacts.
- Round 2/3 should send only incremental diff or a short previous findings checklist.

## Budget Configuration Findings

{config_findings}

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
- Budget action: {'none' if result.budget.budget_passed else over_budget_action}
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
    print(f"ESTIMATED_INPUT_TOKENS: {result.budget.estimated_input_tokens}")
    print(f"EXPECTED_OUTPUT_TOKENS: {result.budget.expected_output_tokens}")
    print(f"ASSUMED_MODEL_CLASS: {result.budget.model_class}")
    print(f"ESTIMATED_COST_PER_ROUND_USD: {result.budget.estimated_total_cost_usd:.6f}")
    print(f"CLAUDE_REVIEW_COST_BUDGET: {result.budget.status_text}")
    if not result.budget.budget_passed:
        print("BUDGET_ACTION: reduce packet size, send summaries/diffs only, or use explicit approved override")
    print(f"REPORT: {REPORT_PATH.relative_to(ROOT).as_posix()}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
