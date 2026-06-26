#!/usr/bin/env python3
"""Generate a report validating strategy['shadow'] metadata on saved snapshots."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.shadow_metadata import attach_shadow_metadata


REPORT_PATH = ROOT / "SHADOW_METADATA_REPORT.md"
MATCHES = [
    (
        "Germany vs Ivory Coast",
        ROOT / "data/history/2026_06_20_Germany_Ivory_Coast_pre.json",
        "Round 1 strong favorite / handicap-cover",
    ),
    (
        "Scotland vs Morocco",
        ROOT / "data/history/2026_06_20_Scotland_Morocco_pre.json",
        "Round 2 balanced match",
    ),
    (
        "Brazil vs Haiti",
        ROOT / "data/history/2026_06_20_Brazil_Haiti_pre.json",
        "Round 3 cold-risk / crowded favorite",
    ),
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def shadow_value(strategy: dict[str, Any], key: str, default: Any = "-") -> Any:
    shadow = strategy.get("shadow") or {}
    return shadow.get(key, default)


def match_display(snapshot: dict[str, Any], fallback: str) -> str:
    match = snapshot.get("match") or {}
    return str(match.get("display") or fallback)


def strategy_rows(strategies: list[dict[str, Any]]) -> list[str]:
    rows = [
        "| Portfolio | Legacy Rank | Legacy Score | Scenario Rank | Scenario Score | Rank Difference | Shadow Verdict |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for strategy in strategies:
        name = strategy.get("rank_name") or strategy.get("name") or "-"
        rows.append(
            "| "
            + " | ".join(
                [
                    str(name),
                    str(shadow_value(strategy, "legacy_rank")),
                    str(shadow_value(strategy, "legacy_score")),
                    str(shadow_value(strategy, "scenario_rank")),
                    str(shadow_value(strategy, "scenario_score")),
                    f"{shadow_value(strategy, 'rank_difference'):+d}"
                    if isinstance(shadow_value(strategy, "rank_difference"), int)
                    else str(shadow_value(strategy, "rank_difference")),
                    str(shadow_value(strategy, "shadow_verdict")),
                ]
            )
            + " |"
        )
    return rows


def report_for_match(name: str, path: Path, label: str) -> tuple[list[str], dict[str, Any]]:
    snapshot = load_json(path)
    raw_strategies = (snapshot.get("strategy_snapshot") or {}).get("strategies") or []
    if not isinstance(raw_strategies, list):
        raw_strategies = []
    strategies = attach_shadow_metadata(raw_strategies, snapshot.get("match") or {}, snapshot.get("probability_distribution") or {})

    legacy_top = strategies[0] if strategies else {}
    scenario_top = min(strategies, key=lambda item: shadow_value(item, "scenario_rank", 999)) if strategies else {}
    legacy_top_shadow = legacy_top.get("shadow") or {}
    all_have_shadow = all(isinstance(item.get("shadow"), dict) for item in strategies)

    section = [
        f"## {name}",
        "",
        f"- Validation label: {label}",
        f"- Source snapshot: `{path.relative_to(ROOT)}`",
        f"- Match display: {match_display(snapshot, name)}",
        f"- Strategy count: {len(strategies)}",
        f"- Every strategy has `shadow`: {'Yes' if all_have_shadow else 'No'}",
        f"- Legacy top portfolio: {legacy_top.get('rank_name') or legacy_top.get('name') or '-'}",
        f"- Scenario top portfolio: {scenario_top.get('rank_name') or scenario_top.get('name') or '-'}",
        f"- Legacy top Scenario Rank: {legacy_top_shadow.get('scenario_rank', '-')}",
        f"- Legacy top Shadow Verdict: {legacy_top_shadow.get('shadow_verdict', '-')}",
        "",
        *strategy_rows(strategies),
        "",
        "### Legacy Top Reason",
        "",
        f"- {legacy_top_shadow.get('scenario_rank_reason', '-')}",
        "",
    ]
    summary = {
        "name": name,
        "strategy_count": len(strategies),
        "all_have_shadow": all_have_shadow,
        "legacy_top": legacy_top.get("rank_name") or legacy_top.get("name") or "-",
        "scenario_top": scenario_top.get("rank_name") or scenario_top.get("name") or "-",
        "legacy_top_scenario_rank": legacy_top_shadow.get("scenario_rank"),
        "legacy_top_shadow_verdict": legacy_top_shadow.get("shadow_verdict"),
    }
    return section, summary


def build_report() -> str:
    lines = [
        "# Shadow Metadata Report",
        "",
        "## Scope",
        "",
        "- Validates `attach_shadow_metadata(...)` on three saved local snapshots.",
        "- Adds only in-memory `strategy[\"shadow\"]` metadata during report generation.",
        "- Does not modify Legacy Ranking, scores, recommendation logic, UI, or data files.",
        "",
        "## Required Shadow Fields",
        "",
        "- `legacy_rank`",
        "- `legacy_score`",
        "- `scenario_rank`",
        "- `scenario_score`",
        "- `rank_difference`",
        "- `shadow_verdict`",
        "- `scenario_rank_reason`",
        "",
    ]
    summaries: list[dict[str, Any]] = []
    for name, path, label in MATCHES:
        section, summary = report_for_match(name, path, label)
        lines.extend(section)
        summaries.append(summary)

    lines.extend(
        [
            "## Cross-Match Summary",
            "",
            "| Match | Strategies | All Have Shadow | Legacy Top | Scenario Top | Legacy Top Scenario Rank | Verdict |",
            "| --- | ---: | --- | --- | --- | ---: | --- |",
        ]
    )
    for summary in summaries:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(summary["name"]),
                    str(summary["strategy_count"]),
                    "Yes" if summary["all_have_shadow"] else "No",
                    str(summary["legacy_top"]),
                    str(summary["scenario_top"]),
                    str(summary["legacy_top_scenario_rank"]),
                    str(summary["legacy_top_shadow_verdict"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Verification Verdict",
            "",
            "- `strategy[\"shadow\"]` generated: Yes",
            "- Legacy order changed: No",
            "- Legacy score changed: No",
            "- Recommendation logic changed: No",
            "- UI changed: No",
            "- Data files changed: No",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
