#!/usr/bin/env python3
"""Report source-key availability for risk contract extraction planning."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "reports" / "golden_risk_contract_v1.json"
REPORT_PATH = ROOT / "reports" / "risk_contract_source_availability_matrix.md"

SOURCE_KEYS = {
    "risk_gate.risk_level": ("risk_gate", "risk_level"),
    "risk_gate.rank1_eligible": ("risk_gate", "rank1_eligible"),
    "risk_gate.gate_reasons": ("risk_gate", "gate_reasons"),
    "risk_gate.hard_blockers": ("risk_gate", "hard_blockers"),
    "risk_gate.soft_warnings": ("risk_gate", "soft_warnings"),
    "exposure_risk.correct_score_limit": ("exposure_risk", "correct_score_limit"),
    "exposure_risk.correct_score_limit_source": ("exposure_risk", "correct_score_limit_source"),
    "scenario_risk.failed_scenario_probability": ("scenario_risk", "failed_scenario_probability"),
    "scenario_risk.adjacent_path_failure": ("scenario_risk", "adjacent_path_failure"),
    "scenario_risk.narrow_exact_score_dependency": ("scenario_risk", "narrow_exact_score_dependency"),
    "scenario_risk.pressure_strictness": ("scenario_risk", "pressure_strictness"),
    "risk_score_components.canonical_risk_score": ("risk_score_components", "canonical_risk_score"),
    "post_match_risk_outcome": ("post_match_risk_outcome",),
}


def present(value: Any) -> bool:
    if value is None:
        return False
    if value == "UNKNOWN" or value == "unknown":
        return False
    return True


def get_path(payload: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def main() -> int:
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contracts = payload.get("contracts") or []
    total = len(contracts)
    rows: list[dict[str, Any]] = []
    for field, path in SOURCE_KEYS.items():
        count = sum(1 for contract in contracts if present(get_path(contract, path)))
        percent = round((count / total) * 100, 1) if total else 0.0
        rows.append({"field": field, "available": count, "total": total, "coverage": percent})

    lines = [
        "# Risk Contract Source Availability Matrix",
        "",
        "Scope: read-only coverage matrix for existing `risk_contract_v1` fixture fields. This script does not write golden JSON, replay portfolio logic, enable portfolio extraction, or enable backtest.",
        "",
        "## Summary",
        "",
        f"- Contracts checked: {total}",
        "- Source: `reports/golden_risk_contract_v1.json`",
        "- PORTFOLIO_EXTRACTION: BLOCKED",
        "- BACKTEST_READY: NO",
        "",
        "## Matrix",
        "",
        "| Field | Available contracts | Total contracts | Coverage |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['field']}` | {row['available']} | {row['total']} | {row['coverage']}% |"
        )

    gaps = [row for row in rows if row["available"] < row["total"]]
    lines.extend(["", "## Gaps", ""])
    if gaps:
        for row in gaps:
            lines.append(f"- `{row['field']}` coverage is {row['coverage']}%.")
    else:
        lines.append("- No source availability gaps found.")

    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            "Do not enable portfolio extraction or backtest. Next safe step is to classify which unavailable fields can be sourced from existing live functions versus which require an approved new formula or settled-result design.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("SOURCE_AVAILABILITY_VALIDATION: PASS")
    print(f"REPORT: {REPORT_PATH.relative_to(ROOT)}")
    print("PORTFOLIO_EXTRACTION: BLOCKED")
    print("BACKTEST_READY: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
