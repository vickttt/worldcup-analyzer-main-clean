#!/usr/bin/env python3
"""Classify mapped risk contract fields by readiness category."""

from __future__ import annotations

from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "field_readiness_classification.md"

FIELD_CATEGORIES = {
    "risk_gate.risk_level": "requires read-only live-function replay",
    "risk_gate.rank1_eligible": "requires read-only live-function replay",
    "risk_gate.gate_reasons": "requires read-only live-function replay",
    "risk_gate.hard_blockers": "requires read-only live-function replay",
    "risk_gate.soft_warnings": "requires read-only live-function replay",
    "exposure_risk.correct_score_limit": "requires read-only live-function replay",
    "exposure_risk.correct_score_limit_source": "requires read-only live-function replay",
    "scenario_risk.failed_scenario_probability": "requires read-only live-function replay",
    "scenario_risk.adjacent_path_failure": "requires read-only live-function replay",
    "scenario_risk.narrow_exact_score_dependency": "requires read-only live-function replay",
    "scenario_risk.pressure_strictness": "requires read-only live-function replay",
    "risk_score_components.canonical_risk_score": "requires approved new formula",
    "post_match_risk_outcome": "requires settled post-match design",
}


def main() -> int:
    counts = Counter(FIELD_CATEGORIES.values())
    lines = [
        "# Field Readiness Classification",
        "",
        "Scope: report-only classification of mapped missing risk contract fields. This script does not modify runtime logic, replay portfolio logic, write golden JSON, enable portfolio extraction, or enable backtest.",
        "",
        "## Gate Status",
        "",
        "- PORTFOLIO_EXTRACTION: BLOCKED",
        "- BACKTEST_READY: NO",
        "",
        "## Category Counts",
        "",
        "| Category | Field count |",
        "| --- | ---: |",
    ]
    for category, count in sorted(counts.items()):
        lines.append(f"| {category} | {count} |")

    lines.extend(["", "## Field Classification", "", "| Field | Readiness category | Reason |", "| --- | --- | --- |"])
    for field, category in FIELD_CATEGORIES.items():
        if category == "requires read-only live-function replay":
            reason = "Existing serialized contracts do not carry the stable value, but current runtime/report sources identify likely provenance."
        elif category == "requires approved new formula":
            reason = "No canonical risk score formula is approved; keep null until Jin approves a formula task."
        else:
            reason = "Pre-match contracts cannot settle realized risk outcome; requires post-match design."
        lines.append(f"| `{field}` | {category} | {reason} |")

    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            "Next safe step is a Jin-reviewed design task for read-only replay boundaries. Do not implement extraction, backtest, or a canonical risk score formula yet.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("FIELD_READINESS_CLASSIFICATION: PASS")
    print(f"REPORT: {REPORT_PATH.relative_to(ROOT)}")
    print("PORTFOLIO_EXTRACTION: BLOCKED")
    print("BACKTEST_READY: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
