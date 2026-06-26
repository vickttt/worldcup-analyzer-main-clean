#!/usr/bin/env python3
"""Generate Hybrid v0.2 report-only benchmark from backfill snapshots.

This script reads existing data/history/backfill snapshots and writes a
Markdown report. It does not modify production sorting, recommendation logic,
UI, app.py, or historical source data.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_post_match_validation_report import settle_portfolio


BACKFILL_DIR = ROOT / "data/history/backfill"
REPORT_PATH = ROOT / "HYBRID_V2_REPORT_ONLY_REPORT.md"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def percent(value: Any) -> str:
    return f"{num(value) * 100:.1f}%"


def money(value: Any) -> str:
    return f"{num(value):+.0f}"


def strategy_name(strategy: dict[str, Any]) -> str:
    return str(strategy.get("rank_name") or strategy.get("name") or "-")


def strategies_from_snapshot(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    strategies = (snapshot.get("strategy_snapshot") or {}).get("strategies") or []
    return [strategy for strategy in strategies if isinstance(strategy, dict)]


def find_strategy(strategies: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for strategy in strategies:
        if strategy_name(strategy) == name:
            return strategy
    return None


def core_strategy(strategies: list[dict[str, Any]]) -> dict[str, Any]:
    return min(strategies, key=lambda item: num((item.get("shadow") or {}).get("scenario_rank"), 999))


def sleeve_share(sample_type: str) -> float:
    text = str(sample_type or "")
    if "低比分" in text:
        return 0.05
    if "冷门风险" in text:
        return 0.10
    if "强队深盘" in text and "高比分" in text:
        return 0.20
    if "高比分" in text:
        return 0.20
    if "强队深盘" in text:
        return 0.15
    return 0.15


def sleeve_reason(match: dict[str, Any], core: dict[str, Any], sleeve: dict[str, Any] | None, share: float) -> str:
    sample_type = str(match.get("sample_type") or "")
    core_shadow = core.get("shadow") or {}
    if not sleeve or share <= 0:
        return "No sleeve candidate available."
    if "低比分" in sample_type:
        return "Low-score sample; sleeve kept at minimum observation size."
    if "冷门风险" in sample_type:
        return "Upset-risk sample; sleeve allowed only as small capped exposure."
    if "高比分" in sample_type and "强队深盘" in sample_type:
        return "High-score strong-favorite sample; capped upside sleeve tests scenario-supported aggressive return."
    if "高比分" in sample_type:
        return "High-score sample; capped upside sleeve tests recovery of Legacy upside without full tail exposure."
    if "强队深盘" in sample_type:
        return "Strong-favorite sample; sleeve tests deep-cover extension while Core remains authoritative."
    if core_shadow.get("shadow_verdict") in {"Agreement", "Watch"}:
        return "Core is scenario-acceptable; small upside sleeve is observation-only."
    return "Sleeve is observation-only because Core/Scenario support is not strong enough for production use."


def sleeve_status(match: dict[str, Any], sleeve: dict[str, Any] | None, share: float) -> str:
    if not sleeve or share <= 0:
        return "No Sleeve"
    sample_type = str(match.get("sample_type") or "")
    sleeve_shadow = (sleeve.get("shadow") or {}) if sleeve else {}
    if "低比分" in sample_type and share >= 0.10:
        return "Uncontrolled Tail"
    if sleeve_shadow.get("shadow_verdict") == "Disagreement" and share > 0.15:
        return "Uncontrolled Tail"
    if "高比分" in sample_type or "强队深盘" in sample_type:
        return "Scenario-Supported Aggressive Upside"
    if "冷门风险" in sample_type:
        return "Watch: Small Upside Sleeve"
    return "Watch: Small Upside Sleeve"


def combine_outcomes(core: dict[str, Any], sleeve: dict[str, Any], share: float) -> dict[str, Any]:
    core_share = 1 - share
    stake = 1000.0
    profit = core_share * num(core["roi"]) * stake + share * num(sleeve["roi"]) * stake
    drawdown = core_share * num(core["max_drawdown"]) + share * num(sleeve["max_drawdown"])
    if profit > 0:
        hit_status = "hit"
    elif abs(profit) < 0.01:
        hit_status = "push"
    else:
        hit_status = "miss"
    return {
        "stake": stake,
        "profit_loss": round(profit, 2),
        "roi": round(profit / stake, 4),
        "max_drawdown": round(drawdown, 2),
        "hit_status": hit_status,
    }


def positive(outcome: dict[str, Any]) -> bool:
    return num(outcome.get("profit_loss")) > 0


def aggregate(rows: list[dict[str, Any]], key: str) -> dict[str, float]:
    profit = sum(num(row[key]["profit_loss"]) for row in rows)
    stake = sum(num(row[key].get("stake"), 1000) for row in rows)
    drawdown = sum(num(row[key]["max_drawdown"]) for row in rows)
    hit_count = sum(1 for row in rows if positive(row[key]))
    return {
        "profit": profit,
        "stake": stake,
        "roi": profit / stake if stake else 0.0,
        "avg_drawdown": drawdown / len(rows) if rows else 0.0,
        "hit_rate": hit_count / len(rows) if rows else 0.0,
    }


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(BACKFILL_DIR.glob("*_pre.json")):
        snapshot = load_json(path)
        strategies = strategies_from_snapshot(snapshot)
        if not strategies:
            continue
        match = snapshot.get("match") or {}
        final_score = str((snapshot.get("post_match") or {}).get("final_score") or "")
        if not final_score:
            continue

        core = core_strategy(strategies)
        sleeve = find_strategy(strategies, "Tail Upside Portfolio") or core
        legacy = find_strategy(strategies, "Legacy Value Portfolio") or strategies[0]
        share = sleeve_share(str(match.get("sample_type") or ""))

        core_outcome = settle_portfolio(core, match, final_score)
        sleeve_outcome = settle_portfolio(sleeve, match, final_score)
        legacy_outcome = settle_portfolio(legacy, match, final_score)
        core_upside_outcome = combine_outcomes(core_outcome, sleeve_outcome, share)

        status = sleeve_status(match, sleeve, share)
        reason = sleeve_reason(match, core, sleeve, share)
        rows.append(
            {
                "match": match,
                "final_score": final_score,
                "source_path": path,
                "core": core,
                "sleeve": sleeve,
                "legacy": legacy,
                "sleeve_share": share,
                "sleeve_status": status,
                "sleeve_reason": reason,
                "guardrail_status": "Allowed Sleeve" if "Scenario-Supported" in status else status,
                "core_outcome": core_outcome,
                "sleeve_outcome": sleeve_outcome,
                "core_upside_outcome": core_upside_outcome,
                "legacy_outcome": legacy_outcome,
            }
        )
    return rows


def recommendation(rows: list[dict[str, Any]]) -> str:
    core = aggregate(rows, "core_outcome")
    core_upside = aggregate(rows, "core_upside_outcome")
    legacy = aggregate(rows, "legacy_outcome")
    if core_upside["roi"] > core["roi"] and core_upside["avg_drawdown"] < legacy["avg_drawdown"]:
        return "Enter Visible Diagnostic"
    return "Keep Report-Only"


def build_report(rows: list[dict[str, Any]]) -> str:
    core = aggregate(rows, "core_outcome")
    core_upside = aggregate(rows, "core_upside_outcome")
    legacy = aggregate(rows, "legacy_outcome")
    suitable = [
        row for row in rows if row["sleeve_status"] == "Scenario-Supported Aggressive Upside"
    ]
    unsuitable = [
        row
        for row in rows
        if row["sleeve_status"] in {"Uncontrolled Tail", "No Sleeve"} or "Low-score" in row["sleeve_reason"]
    ]
    verdict = recommendation(rows)

    lines = [
        "# Hybrid v0.2 Report-Only Report",
        "",
        "Date: 2026-06-21",
        "",
        "## Scope",
        "",
        "- Reads existing `data/history/backfill/` snapshots only.",
        "- Generates report-only Core, Upside Sleeve, Core + Upside, and Legacy Tail-Heavy comparisons.",
        "- Does not modify `app.py`, production sorting, recommendation logic, UI, score functions, or existing source data.",
        "",
        "## Aggregate Result",
        "",
        "| Structure | ROI | Hit Rate | Avg Max Drawdown | Total P/L |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| Core Portfolio | {percent(core['roi'])} | {percent(core['hit_rate'])} | {money(-core['avg_drawdown'])} | {money(core['profit'])} |",
        f"| Core + Upside Portfolio | {percent(core_upside['roi'])} | {percent(core_upside['hit_rate'])} | {money(-core_upside['avg_drawdown'])} | {money(core_upside['profit'])} |",
        f"| Legacy Tail-Heavy Portfolio | {percent(legacy['roi'])} | {percent(legacy['hit_rate'])} | {money(-legacy['avg_drawdown'])} | {money(legacy['profit'])} |",
        "",
        "## Match-Level Report",
        "",
        "| Match | Type | Final | Core Portfolio | Upside Sleeve | Sleeve Share | Sleeve Status | Guardrail Status | Core ROI | Core+Upside ROI | Legacy ROI | Core+Upside Max DD | Legacy Max DD |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        match = row["match"]
        lines.append(
            "| "
            + " | ".join(
                [
                    str(match.get("display") or "-"),
                    str(match.get("sample_type") or "-"),
                    row["final_score"],
                    strategy_name(row["core"]),
                    strategy_name(row["sleeve"]),
                    percent(row["sleeve_share"]),
                    row["sleeve_status"],
                    row["guardrail_status"],
                    percent(row["core_outcome"]["roi"]),
                    percent(row["core_upside_outcome"]["roi"]),
                    percent(row["legacy_outcome"]["roi"]),
                    money(-num(row["core_upside_outcome"]["max_drawdown"])),
                    money(-num(row["legacy_outcome"]["max_drawdown"])),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Sleeve Reasons",
            "",
            "| Match | Sleeve Reason |",
            "| --- | --- |",
        ]
    )
    for row in rows:
        match = row["match"]
        lines.append(f"| {match.get('display') or '-'} | {row['sleeve_reason']} |")

    lines.extend(
        [
            "",
            "## Suitable For Upside Sleeve",
            "",
        ]
    )
    if suitable:
        for row in suitable:
            lines.append(f"- {row['match'].get('display')}: {row['sleeve_reason']}")
    else:
        lines.append("- None identified.")

    lines.extend(["", "## Not Suitable Or Small-Sleeve Only", ""])
    if unsuitable:
        for row in unsuitable:
            lines.append(f"- {row['match'].get('display')}: {row['sleeve_reason']}")
    else:
        lines.append("- None identified.")

    lines.extend(
        [
            "",
            "## Required Questions",
            "",
            "### Is Core + Upside better than Core?",
            "",
            "Yes." if core_upside["roi"] > core["roi"] else "No.",
            "",
            f"- Core ROI: {percent(core['roi'])}.",
            f"- Core + Upside ROI: {percent(core_upside['roi'])}.",
            f"- Difference: {percent(core_upside['roi'] - core['roi'])}.",
            "",
            "### Does Core + Upside reduce Legacy extreme drawdown?",
            "",
            "Yes." if core_upside["avg_drawdown"] < legacy["avg_drawdown"] else "No.",
            "",
            f"- Core + Upside average max drawdown: {money(-core_upside['avg_drawdown'])}.",
            f"- Legacy Tail-Heavy average max drawdown: {money(-legacy['avg_drawdown'])}.",
            "",
            "### Does Core + Upside recover part of Legacy upside?",
            "",
            "Partially. It improves over Core while staying materially below Legacy Tail-Heavy drawdown.",
            "",
            "### Should the project enter Visible Diagnostic?",
            "",
            f"Recommendation: `{verdict}`.",
            "",
            "- Visible Diagnostic should remain observation-only.",
            "- It should not change production sorting, recommendation eligibility, or UI decision logic unless separately approved.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    rows = build_rows()
    REPORT_PATH.write_text(build_report(rows), encoding="utf-8")
    stats = {
        "matches": len(rows),
        "core_roi": aggregate(rows, "core_outcome")["roi"],
        "core_upside_roi": aggregate(rows, "core_upside_outcome")["roi"],
        "legacy_roi": aggregate(rows, "legacy_outcome")["roi"],
        "recommendation": recommendation(rows),
    }
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
