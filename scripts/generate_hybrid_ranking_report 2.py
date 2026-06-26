#!/usr/bin/env python3
"""Generate read-only Hybrid Ranking report from saved history snapshots."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.shadow_metadata import attach_shadow_metadata


HISTORY_DIR = ROOT / "data/history"
REPORT_PATH = ROOT / "HYBRID_RANKING_REPORT.md"


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


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def strategies_from_snapshot(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    strategies = (snapshot.get("strategy_snapshot") or {}).get("strategies")
    if not isinstance(strategies, list):
        strategies = snapshot.get("strategies") if isinstance(snapshot.get("strategies"), list) else []
    return [strategy for strategy in strategies if isinstance(strategy, dict)]


def match_display(snapshot: dict[str, Any], fallback: str) -> str:
    match = snapshot.get("match") if isinstance(snapshot.get("match"), dict) else {}
    return str(match.get("display") or match.get("display_name") or fallback)


def role_exposure(strategy: dict[str, Any]) -> dict[str, float]:
    style = strategy.get("portfolio_style") or {}
    exposure = style.get("role_exposure") or {}
    if not isinstance(exposure, dict):
        return {}
    return {str(key): num(value) for key, value in exposure.items()}


def tail_exposure(strategy: dict[str, Any]) -> float:
    style = strategy.get("portfolio_style") or {}
    tail = num(style.get("tail_share"))
    if tail:
        return tail
    return role_exposure(strategy).get("尾部资产", 0.0)


def tempo_exposure(strategy: dict[str, Any]) -> float:
    style = strategy.get("portfolio_style") or {}
    tempo = num(style.get("tempo_share"))
    if tempo:
        return tempo
    return role_exposure(strategy).get("节奏资产", 0.0)


def direction_exposure(strategy: dict[str, Any]) -> float:
    return role_exposure(strategy).get("方向资产", 0.0)


def return_exposure(strategy: dict[str, Any]) -> float:
    style = strategy.get("portfolio_style") or {}
    return num(style.get("return_share")) or role_exposure(strategy).get("收益资产", 0.0)


def insurance_exposure(strategy: dict[str, Any]) -> float:
    style = strategy.get("portfolio_style") or {}
    return num(style.get("insurance_share")) or role_exposure(strategy).get("保险资产", 0.0)


def value_score(strategy: dict[str, Any]) -> float:
    legacy_score = clamp(num(strategy.get("score")))
    expected_yield = num(strategy.get("expected_yield") or strategy.get("capital_efficiency"))
    sharpe = num(strategy.get("sharpe_ratio"))
    ev_component = clamp(50 + expected_yield * 180)
    roi_component = clamp(50 + num(strategy.get("capital_efficiency"), expected_yield) * 180)
    sharpe_component = clamp(50 + sharpe * 120)
    return round(legacy_score * 0.35 + ev_component * 0.25 + roi_component * 0.20 + sharpe_component * 0.20, 1)


def scenario_consistency_score(strategy: dict[str, Any]) -> float:
    consistency = strategy.get("consistency_score")
    if consistency is not None:
        value = num(consistency)
        return round(clamp(value * 100 if value <= 1 else value), 1)
    shadow = strategy.get("shadow") or {}
    return round(clamp(num(shadow.get("scenario_score"), 70.0)), 1)


def scenario_rank_bonus(strategy: dict[str, Any]) -> float:
    shadow = strategy.get("shadow") or {}
    rank = int(num(shadow.get("scenario_rank"), 99))
    if rank == 1:
        return 10.0
    if rank == 2:
        return 6.0
    if rank == 3:
        return 3.0
    return 0.0


def shadow_verdict_adjustment(strategy: dict[str, Any]) -> float:
    verdict = str((strategy.get("shadow") or {}).get("shadow_verdict") or "")
    return {
        "Agreement": 5.0,
        "Watch": 1.0,
        "Disagreement": -8.0,
        "Blocker Candidate": -20.0,
    }.get(verdict, 0.0)


def coverage_score(strategy: dict[str, Any]) -> float:
    main_coverage = max(num(strategy.get("coverage")), direction_exposure(strategy), return_exposure(strategy))
    insurance = insurance_exposure(strategy)
    return round(clamp(main_coverage * 100) * 0.60 + clamp(insurance * 100) * 0.40, 1)


def max_loss_penalty(strategy: dict[str, Any]) -> float:
    max_loss = abs(num(strategy.get("max_loss")))
    stake = sum(num(item.get("amount")) for item in strategy.get("items") or [] if isinstance(item, dict))
    if not stake:
        return 0.0
    loss_ratio = max_loss / stake
    if loss_ratio > 1.0:
        return 10.0
    if loss_ratio > 0.75:
        return 6.0
    if loss_ratio > 0.50:
        return 3.0
    return 0.0


def tail_tempo_penalty(strategy: dict[str, Any]) -> float:
    tail = tail_exposure(strategy)
    tempo = tempo_exposure(strategy)
    direction = direction_exposure(strategy)
    penalty = 0.0
    if tail > 0.35:
        penalty += 22.0
    elif tail > 0.20:
        penalty += 12.0
    elif tail > 0.15:
        penalty += 6.0
    if tempo > 0.55 and direction < 0.20:
        penalty += 14.0
    return penalty


def guardrail_status(strategy: dict[str, Any], hybrid_score: float) -> tuple[str, list[str]]:
    flags: list[str] = []
    shadow = strategy.get("shadow") or {}
    verdict = str(shadow.get("shadow_verdict") or "-")
    consistency = scenario_consistency_score(strategy)
    tail = tail_exposure(strategy)
    tempo = tempo_exposure(strategy)
    direction = direction_exposure(strategy)

    if verdict == "Blocker Candidate":
        flags.append("Blocker Candidate")
    if verdict == "Disagreement":
        flags.append("Shadow Disagreement")
    if consistency < 60:
        flags.append("Low scenario consistency")
    elif consistency < 75:
        flags.append("Scenario consistency warning")
    if tail > 0.35:
        flags.append("Tail-heavy")
    elif tail > 0.20:
        flags.append("Elevated tail exposure")
    if tempo > 0.55 and direction < 0.20:
        flags.append("Pure tempo risk")
    if verdict == "Disagreement" and hybrid_score < 85:
        flags.append("Not default-eligible without explanation")

    if any(flag in flags for flag in ("Blocker Candidate", "Tail-heavy", "Low scenario consistency")):
        return "Blocked", flags
    if flags:
        return "Watch", flags
    return "Eligible", flags


def hybrid_reason(strategy: dict[str, Any], status: str, flags: list[str]) -> str:
    shadow = strategy.get("shadow") or {}
    if status == "Blocked":
        return "Guardrails block this portfolio from default ranking leadership: " + ", ".join(flags)
    if status == "Watch":
        return "Hybrid rank keeps this portfolio under observation because: " + ", ".join(flags)
    if int(num(shadow.get("scenario_rank"), 99)) == 1:
        return "Hybrid rank rewards Scenario Rank 1 with acceptable value and risk controls."
    return "Hybrid rank balances legacy value metrics with scenario consistency and controlled downside."


def attach_hybrid_metadata(strategies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[tuple[float, int, dict[str, Any]]] = []
    for strategy in strategies:
        value_layer = value_score(strategy) * 0.30
        scenario_layer = scenario_consistency_score(strategy) * 0.15 + scenario_rank_bonus(strategy) + shadow_verdict_adjustment(strategy)
        coverage_layer = coverage_score(strategy) * 0.20
        stability_layer = clamp(100 - max_loss_penalty(strategy) * 10) * 0.10
        penalty = tail_tempo_penalty(strategy) + max_loss_penalty(strategy)
        hybrid_score = round(clamp(value_layer + scenario_layer + coverage_layer + stability_layer - penalty), 1)
        status, flags = guardrail_status(strategy, hybrid_score)
        strategy["hybrid"] = {
            "hybrid_score": hybrid_score,
            "guardrail_status": status,
            "guardrail_flags": flags,
            "hybrid_rank_reason": hybrid_reason(strategy, status, flags),
        }
        rows.append((hybrid_score, int(num((strategy.get("shadow") or {}).get("legacy_rank"), 999)), strategy))

    ordered = sorted(rows, key=lambda row: (-row[0], row[1]))
    for hybrid_rank, (_score, _legacy_rank, strategy) in enumerate(ordered, start=1):
        strategy["hybrid"]["hybrid_rank"] = hybrid_rank
    return strategies


def money(value: Any) -> str:
    return f"{num(value):.0f}"


def score(value: Any) -> str:
    return f"{num(value):.1f}"


def strategy_name(strategy: dict[str, Any]) -> str:
    return str(strategy.get("rank_name") or strategy.get("name") or "-")


def table_rows(strategies: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Guardrail Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for strategy in sorted(strategies, key=lambda item: int(num((item.get("hybrid") or {}).get("hybrid_rank"), 999))):
        shadow = strategy.get("shadow") or {}
        hybrid = strategy.get("hybrid") or {}
        lines.append(
            "| "
            + " | ".join(
                [
                    strategy_name(strategy),
                    str(shadow.get("legacy_rank", "-")),
                    str(shadow.get("scenario_rank", "-")),
                    str(hybrid.get("hybrid_rank", "-")),
                    score(shadow.get("legacy_score")),
                    score(hybrid.get("hybrid_score")),
                    str(hybrid.get("guardrail_status", "-")),
                ]
            )
            + " |"
        )
    return lines


def report_for_snapshot(path: Path) -> tuple[list[str], dict[str, Any] | None]:
    snapshot = load_json(path)
    raw_strategies = strategies_from_snapshot(snapshot)
    if not raw_strategies:
        return [], None
    strategies = attach_shadow_metadata(raw_strategies, snapshot.get("match") or {}, snapshot.get("probability_distribution") or {})
    strategies = attach_hybrid_metadata(strategies)

    legacy_top = min(strategies, key=lambda item: int(num((item.get("shadow") or {}).get("legacy_rank"), 999)))
    scenario_top = min(strategies, key=lambda item: int(num((item.get("shadow") or {}).get("scenario_rank"), 999)))
    hybrid_top = min(strategies, key=lambda item: int(num((item.get("hybrid") or {}).get("hybrid_rank"), 999)))
    display = match_display(snapshot, path.stem)

    section = [
        f"## {display}",
        "",
        f"- Source snapshot: `{path.relative_to(ROOT)}`",
        f"- Strategy count: {len(strategies)}",
        f"- Legacy Top: {strategy_name(legacy_top)}",
        f"- Scenario Top: {strategy_name(scenario_top)}",
        f"- Hybrid Top: {strategy_name(hybrid_top)}",
        f"- Hybrid Top Guardrail Status: {(hybrid_top.get('hybrid') or {}).get('guardrail_status', '-')}",
        "",
        *table_rows(strategies),
        "",
        "### Hybrid Top Reason",
        "",
        f"- {(hybrid_top.get('hybrid') or {}).get('hybrid_rank_reason', '-')}",
        "",
        "### Legacy vs Scenario vs Hybrid",
        "",
        f"- Legacy Top == Scenario Top: {'Yes' if strategy_name(legacy_top) == strategy_name(scenario_top) else 'No'}",
        f"- Legacy Top == Hybrid Top: {'Yes' if strategy_name(legacy_top) == strategy_name(hybrid_top) else 'No'}",
        f"- Scenario Top == Hybrid Top: {'Yes' if strategy_name(scenario_top) == strategy_name(hybrid_top) else 'No'}",
        "",
    ]
    summary = {
        "match": display,
        "legacy_top": strategy_name(legacy_top),
        "scenario_top": strategy_name(scenario_top),
        "hybrid_top": strategy_name(hybrid_top),
        "hybrid_status": (hybrid_top.get("hybrid") or {}).get("guardrail_status", "-"),
    }
    return section, summary


def snapshot_paths() -> list[Path]:
    paths = sorted(HISTORY_DIR.glob("*_pre.json"))
    paths.extend(
        path
        for path in sorted(HISTORY_DIR.glob("*.json"))
        if not path.name.endswith("_pre.json")
        and not path.name.endswith("_post.json")
        and path.name not in {"portfolio_performance.json", "style_performance.json"}
    )
    return paths


def build_report() -> str:
    lines = [
        "# Hybrid Ranking Report v0.1",
        "",
        "## Scope",
        "",
        "- Phase A only: Hybrid Report Only.",
        "- Reads saved history snapshots from `data/history/`.",
        "- Reuses `attach_shadow_metadata(...)` to derive Scenario Rank and Shadow Verdict in memory.",
        "- Computes `strategy[\"hybrid\"]` in memory for reporting only.",
        "- Writes only `HYBRID_RANKING_REPORT.md`.",
        "- Does not modify `app.py`, UI, production sorting, recommendation logic, score functions, or data files.",
        "",
        "## Hybrid Score v0.1 Inputs",
        "",
        "- Legacy Score / expected yield / ROI proxy / Sharpe.",
        "- Scenario Rank.",
        "- Shadow Verdict.",
        "- Scenario Consistency Score.",
        "- Max Loss.",
        "- Tail exposure and pure tempo penalty when available.",
        "- Main Scenario Coverage and Secondary Insurance Coverage proxies from existing strategy fields.",
        "",
        "## Cross-Match Summary",
        "",
        "| Match | Legacy Top | Scenario Top | Hybrid Top | Hybrid Guardrail Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    sections: list[list[str]] = []
    summaries: list[dict[str, Any]] = []
    skipped = 0
    for path in snapshot_paths():
        section, summary = report_for_snapshot(path)
        if summary is None:
            skipped += 1
            continue
        sections.append(section)
        summaries.append(summary)
        lines.append(
            "| "
            + " | ".join(
                [
                    str(summary["match"]),
                    str(summary["legacy_top"]),
                    str(summary["scenario_top"]),
                    str(summary["hybrid_top"]),
                    str(summary["hybrid_status"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Summary Metrics",
            "",
            f"- Snapshots scanned: {len(snapshot_paths())}.",
            f"- Snapshots with strategies: {len(summaries)}.",
            f"- Snapshots skipped because strategies were missing: {skipped}.",
            f"- Legacy Top differs from Hybrid Top: {sum(1 for item in summaries if item['legacy_top'] != item['hybrid_top'])}.",
            f"- Scenario Top differs from Hybrid Top: {sum(1 for item in summaries if item['scenario_top'] != item['hybrid_top'])}.",
            "",
            "## Match Details",
            "",
        ]
    )
    for section in sections:
        lines.extend(section)

    lines.extend(
        [
            "## Automation Verdict",
            "",
            "- `HYBRID_RANKING_REPORT.md` generated: Yes.",
            "- Sorting changed: No.",
            "- Recommendation logic changed: No.",
            "- UI changed: No.",
            "- Data files changed: No.",
            "- Production authority changed: No.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    REPORT_PATH.write_text(build_report(), encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
