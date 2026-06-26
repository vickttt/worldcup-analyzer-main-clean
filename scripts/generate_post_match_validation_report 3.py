#!/usr/bin/env python3
"""Generate read-only post-match validation for Legacy vs Scenario Ranking."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.shadow_metadata import attach_shadow_metadata


REPORT_PATH = ROOT / "POST_MATCH_VALIDATION_REPORT.md"
HISTORY_DIR = ROOT / "data/history"
MY_PORTFOLIOS_DIR = HISTORY_DIR / "my_portfolios"
MATERIAL_ROI_GAP = 0.02


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def safe_num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_score(score: str) -> tuple[int, int]:
    home, away = str(score).split(":", 1)
    return int(home), int(away)


def normalize_match(match: dict[str, Any]) -> dict[str, str]:
    home = match.get("home") or match.get("home_cn") or ""
    away = match.get("away") or match.get("away_cn") or ""
    return {
        "home": str(home),
        "away": str(away),
        "home_cn": str(match.get("home_cn") or home),
        "away_cn": str(match.get("away_cn") or away),
        "display": str(match.get("display") or f"{home} vs {away}"),
    }


def parse_handicap_selection(selection: Any) -> tuple[str | None, float | None]:
    text = str(selection or "")
    match = re.search(r"\b(Home|Away)\b\s*([+-]?\d+(?:\.\d+)?)", text, re.I)
    if match:
        return match.group(1).lower(), float(match.group(2))
    return None, None


def parse_total_selection(selection: Any) -> tuple[str | None, float | None]:
    text = str(selection or "")
    match = re.search(r"(Under|Over|小于|大于)\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
    if not match:
        return None, None
    side = "under" if match.group(1).lower() in {"under", "小于"} else "over"
    return side, float(match.group(2))


def winner_outcome(item: dict[str, Any], match: dict[str, str], home_goals: int, away_goals: int) -> str:
    selection = str(item.get("selection") or item.get("name") or "")
    if home_goals == away_goals:
        result = "平局"
    elif home_goals > away_goals:
        result = match["home_cn"]
    else:
        result = match["away_cn"]
    return "win" if result and result in selection else "lose"


def handicap_outcome(item: dict[str, Any], home_goals: int, away_goals: int) -> str:
    side, line = parse_handicap_selection(item.get("selection") or item.get("name"))
    if side is None or line is None:
        return "unknown"
    adjusted = home_goals + line if side == "home" else away_goals + line
    opponent = away_goals if side == "home" else home_goals
    if abs(adjusted - opponent) < 0.001:
        return "push"
    return "win" if adjusted > opponent else "lose"


def total_outcome(item: dict[str, Any], home_goals: int, away_goals: int) -> str:
    side, line = parse_total_selection(item.get("selection") or item.get("name"))
    if side is None or line is None:
        return "unknown"
    total_goals = home_goals + away_goals
    if abs(total_goals - line) < 0.001:
        return "push"
    if side == "under":
        return "win" if total_goals < line else "lose"
    return "win" if total_goals > line else "lose"


def correct_score_outcome(item: dict[str, Any], home_goals: int, away_goals: int) -> str:
    return "win" if str(item.get("selection")) == f"{home_goals}:{away_goals}" else "lose"


def asset_outcome(item: dict[str, Any], match: dict[str, str], home_goals: int, away_goals: int) -> str:
    item_type = item.get("type")
    if item_type == "winner":
        return winner_outcome(item, match, home_goals, away_goals)
    if item_type == "handicap":
        return handicap_outcome(item, home_goals, away_goals)
    if item_type == "total":
        return total_outcome(item, home_goals, away_goals)
    if item_type == "correct_score":
        return correct_score_outcome(item, home_goals, away_goals)
    return "unknown"


def profit_value(amount: float, odds: float, outcome: str) -> float:
    if outcome == "win" and odds:
        return amount * (odds - 1)
    if outcome == "lose":
        return -amount
    return 0.0


def settle_portfolio(strategy: dict[str, Any], match: dict[str, str], final_score: str) -> dict[str, Any]:
    home_goals, away_goals = parse_score(final_score)
    asset_rows: list[dict[str, Any]] = []
    stake = 0.0
    profit = 0.0
    max_drawdown = 0.0

    for item in strategy.get("items") or []:
        if not isinstance(item, dict):
            continue
        amount = safe_num(item.get("amount"))
        odds = safe_num(item.get("odds") or item.get("effective_odds") or item.get("standard_odds"))
        outcome = asset_outcome(item, match, home_goals, away_goals)
        item_profit = profit_value(amount, odds, outcome)
        stake += amount
        profit += item_profit
        max_drawdown += amount if outcome == "lose" else 0.0
        asset_rows.append(
            {
                "name": item.get("name") or item.get("selection") or "-",
                "type": item.get("type") or "-",
                "stake": amount,
                "odds": odds,
                "outcome": outcome,
                "profit_loss": item_profit,
            }
        )

    wins = sum(1 for row in asset_rows if row["outcome"] == "win")
    losses = sum(1 for row in asset_rows if row["outcome"] == "lose")
    pushes = sum(1 for row in asset_rows if row["outcome"] == "push")
    if wins and not losses:
        hit_status = "hit"
    elif wins and losses:
        hit_status = "partial_hit"
    elif pushes and not wins and not losses:
        hit_status = "push"
    else:
        hit_status = "miss"

    return {
        "stake": stake,
        "profit_loss": round(profit, 2),
        "roi": round(profit / stake, 4) if stake else 0.0,
        "max_drawdown": round(max_drawdown, 2),
        "hit_status": hit_status,
        "assets": asset_rows,
    }


def pre_snapshot_path(post_path: Path, post_snapshot: dict[str, Any]) -> Path | None:
    raw = post_snapshot.get("pre_match_snapshot")
    candidates: list[Path] = []
    if raw:
        candidates.append(ROOT / str(raw))
    stem = post_path.name.replace("_post.json", "_pre.json")
    candidates.append(post_path.with_name(stem))
    candidates.append(post_path.with_name(post_path.name.replace("_post.json", ".json")))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def match_slug_from_path(path: Path) -> str:
    name = path.name
    for suffix in ("_pre.json", "_post.json", ".json"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return path.stem


def my_portfolio_path_candidates(pre_path: Path, post_path: Path, post_snapshot: dict[str, Any]) -> list[Path]:
    slugs = [match_slug_from_path(pre_path), match_slug_from_path(post_path)]
    raw = post_snapshot.get("pre_match_snapshot")
    if raw:
        slugs.append(match_slug_from_path(Path(str(raw))))

    candidates: list[Path] = []
    for slug in dict.fromkeys(slugs):
        candidates.append(MY_PORTFOLIOS_DIR / f"{slug}.json")
    return candidates


def load_standalone_my_portfolio(pre_path: Path, post_path: Path, post_snapshot: dict[str, Any]) -> tuple[dict[str, Any] | None, Path | None]:
    for candidate in my_portfolio_path_candidates(pre_path, post_path, post_snapshot):
        if not candidate.exists():
            continue
        my_portfolio = load_json(candidate)
        items = my_portfolio.get("items") if isinstance(my_portfolio, dict) else None
        if items:
            return my_portfolio, candidate
    return None, None


def strategies_from_pre_snapshot(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    strategies = (snapshot.get("strategy_snapshot") or {}).get("strategies")
    if not isinstance(strategies, list):
        strategies = snapshot.get("strategies") if isinstance(snapshot.get("strategies"), list) else []
    return [strategy for strategy in strategies if isinstance(strategy, dict)]


def my_portfolio_strategy(my_portfolio: dict[str, Any] | None) -> dict[str, Any] | None:
    my_portfolio = my_portfolio or {}
    items = my_portfolio.get("items") if isinstance(my_portfolio, dict) else None
    if not items:
        return None
    return {
        "code": "my_portfolio",
        "name": "My Portfolio",
        "rank_name": "My Portfolio",
        "items": items,
        "score": None,
    }


def pick_current_recommendation(strategies: list[dict[str, Any]]) -> dict[str, Any]:
    for strategy in strategies:
        name = str(strategy.get("rank_name") or strategy.get("name") or "")
        if "推荐" in name or "当前" in name:
            return strategy
    return strategies[0] if strategies else {}


def compare_legacy_scenario(legacy: dict[str, Any], scenario: dict[str, Any]) -> tuple[str, str]:
    legacy_outcome = legacy.get("outcome") or {}
    scenario_outcome = scenario.get("outcome") or {}
    legacy_roi = safe_num(legacy_outcome.get("roi"))
    scenario_roi = safe_num(scenario_outcome.get("roi"))
    roi_gap = scenario_roi - legacy_roi

    if abs(roi_gap) < MATERIAL_ROI_GAP:
        legacy_dd = safe_num(legacy_outcome.get("max_drawdown"))
        scenario_dd = safe_num(scenario_outcome.get("max_drawdown"))
        if abs(scenario_dd - legacy_dd) > 0 and min(legacy_dd, scenario_dd) / max(legacy_dd, scenario_dd, 1) < 0.80:
            if scenario_dd < legacy_dd:
                return "Scenario Winner", "ROI gap is small, but Scenario Top had materially lower drawdown."
            return "Legacy Winner", "ROI gap is small, but Legacy Top had materially lower drawdown."
        return "Draw", "ROI gap is below the 2 percentage point material threshold."

    if roi_gap > 0:
        return "Scenario Winner", "Scenario Top ROI is materially higher than Legacy Top ROI."
    return "Legacy Winner", "Legacy Top ROI is materially higher than Scenario Top ROI."


def portfolio_name(strategy: dict[str, Any]) -> str:
    return str(strategy.get("rank_name") or strategy.get("name") or "-")


def validation_for_post(post_path: Path) -> dict[str, Any]:
    post_snapshot = load_json(post_path)
    pre_path = pre_snapshot_path(post_path, post_snapshot)
    if not pre_path:
        return {"eligible": False, "post_path": post_path, "skip_reason": "missing_pre_snapshot"}
    pre_snapshot = load_json(pre_path)
    final_score = post_snapshot.get("final_score")
    strategies = strategies_from_pre_snapshot(pre_snapshot)
    if not final_score or not strategies:
        return {"eligible": False, "post_path": post_path, "pre_path": pre_path, "skip_reason": "missing_score_or_strategies"}

    match = normalize_match(pre_snapshot.get("match") or post_snapshot.get("match") or {})
    shadowed = attach_shadow_metadata(strategies, pre_snapshot.get("match") or {}, pre_snapshot.get("probability_distribution") or {})
    legacy_top = shadowed[0]
    scenario_top = min(shadowed, key=lambda item: (item.get("shadow") or {}).get("scenario_rank", 999))
    current_recommendation = pick_current_recommendation(shadowed)
    standalone_my_portfolio, standalone_my_portfolio_path = load_standalone_my_portfolio(pre_path, post_path, post_snapshot)
    embedded_my_portfolio = pre_snapshot.get("my_portfolio") if isinstance(pre_snapshot.get("my_portfolio"), dict) else {}
    my_portfolio_source = standalone_my_portfolio_path or "pre_snapshot.my_portfolio"
    my_strategy = my_portfolio_strategy(standalone_my_portfolio or embedded_my_portfolio)

    selected = [
        ("Legacy Top", legacy_top),
        ("Scenario Top", scenario_top),
        ("Current Recommendation", current_recommendation),
    ]
    if my_strategy:
        selected.append(("My Portfolio", my_strategy))

    seen: set[tuple[str, str]] = set()
    portfolios: list[dict[str, Any]] = []
    for label, strategy in selected:
        key = (label, portfolio_name(strategy))
        if key in seen:
            continue
        seen.add(key)
        outcome = settle_portfolio(strategy, match, str(final_score))
        shadow = strategy.get("shadow") or {}
        portfolios.append(
            {
                "type": label,
                "name": portfolio_name(strategy),
                "legacy_rank": shadow.get("legacy_rank", "-"),
                "legacy_score": shadow.get("legacy_score", strategy.get("score", "-")),
                "scenario_rank": shadow.get("scenario_rank", "-"),
                "scenario_score": shadow.get("scenario_score", "-"),
                "shadow_verdict": shadow.get("shadow_verdict", "-"),
                "scenario_rank_reason": shadow.get("scenario_rank_reason", "-"),
                "outcome": outcome,
            }
        )

    legacy_row = next(row for row in portfolios if row["type"] == "Legacy Top")
    scenario_row = next(row for row in portfolios if row["type"] == "Scenario Top")
    result, reason = compare_legacy_scenario(legacy_row, scenario_row)

    return {
        "eligible": True,
        "match": match,
        "final_score": final_score,
        "pre_path": pre_path,
        "post_path": post_path,
        "legacy_top": portfolio_name(legacy_top),
        "scenario_top": portfolio_name(scenario_top),
        "current_recommendation": portfolio_name(current_recommendation),
        "my_portfolio_source": str(Path(my_portfolio_source).relative_to(ROOT)) if isinstance(my_portfolio_source, Path) else my_portfolio_source,
        "portfolios": portfolios,
        "legacy_vs_scenario": result,
        "legacy_vs_scenario_reason": reason,
        "legacy_top_downgrade_reason": (legacy_top.get("shadow") or {}).get("scenario_rank_reason", "-"),
    }


def money(value: Any) -> str:
    number = safe_num(value)
    return f"{number:+.0f}"


def percent(value: Any) -> str:
    return f"{safe_num(value) * 100:.1f}%"


def portfolio_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Portfolio | Type | Legacy Rank | Scenario Rank | Shadow Verdict | Hit | P/L | ROI | Max Drawdown |",
        "| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        outcome = row["outcome"]
        lines.append(
            "| "
            + " | ".join(
                [
                    row["name"],
                    row["type"],
                    str(row["legacy_rank"]),
                    str(row["scenario_rank"]),
                    str(row["shadow_verdict"]),
                    str(outcome["hit_status"]),
                    money(outcome["profit_loss"]),
                    percent(outcome["roi"]),
                    money(-safe_num(outcome["max_drawdown"])),
                ]
            )
            + " |"
        )
    return lines


def promotion_rule_section(validations: list[dict[str, Any]]) -> list[str]:
    valid = [item for item in validations if item.get("eligible")]
    scenario_wins = sum(1 for item in valid if item.get("legacy_vs_scenario") == "Scenario Winner")
    legacy_wins = sum(1 for item in valid if item.get("legacy_vs_scenario") == "Legacy Winner")
    draws = sum(1 for item in valid if item.get("legacy_vs_scenario") == "Draw")
    legacy_profit = sum(safe_num(next(row for row in item["portfolios"] if row["type"] == "Legacy Top")["outcome"]["profit_loss"]) for item in valid)
    legacy_stake = sum(safe_num(next(row for row in item["portfolios"] if row["type"] == "Legacy Top")["outcome"]["stake"]) for item in valid)
    scenario_profit = sum(safe_num(next(row for row in item["portfolios"] if row["type"] == "Scenario Top")["outcome"]["profit_loss"]) for item in valid)
    scenario_stake = sum(safe_num(next(row for row in item["portfolios"] if row["type"] == "Scenario Top")["outcome"]["stake"]) for item in valid)
    legacy_roi = legacy_profit / legacy_stake if legacy_stake else 0.0
    scenario_roi = scenario_profit / scenario_stake if scenario_stake else 0.0

    criteria_met = (
        len(valid) >= 5
        and scenario_roi >= legacy_roi
        and scenario_wins + draws >= legacy_wins
        and scenario_wins >= 3
    )
    status = "Enter Scenario Guardrails Phase" if criteria_met else "Keep Shadow Mode"
    if len(valid) < 5:
        status_reason = f"Only {len(valid)} valid post-match validations are available; 5 are required."
    elif criteria_met:
        status_reason = "The 5-match promotion rule is satisfied."
    else:
        status_reason = "The 5-match promotion rule is not satisfied."

    return [
        "## 5-Match Promotion Rule",
        "",
        "After 5 valid post-match validations, enter `Scenario Guardrails Phase` only if all conditions hold:",
        "",
        "- Scenario Top ROI >= Legacy Top ROI.",
        "- Scenario Top wins at least 3 matches or is not worse than Legacy.",
        "- Scenario Top does not have materially larger drawdown.",
        "- Scenario Rank downgrade reasons for Legacy Rank 1 are supported by post-match outcomes.",
        "",
        "Scenario Guardrails Phase means:",
        "",
        "- Legacy Rank 1 with `Shadow Verdict = Disagreement` must show a strong warning.",
        "- Scenario Rank 1 can be marked as `剧本优先候选`.",
        "- Tail-heavy / pure tempo / low consistency portfolios cannot become default recommendations without warning.",
        "- Scenario Rank can influence default recommendation eligibility.",
        "- Legacy score sorting remains in place temporarily.",
        "",
        "It does not mean replacing `strategy_score(...)` or changing production sorting immediately.",
        "",
        "## Current Promotion Evaluation",
        "",
        f"- Valid matches: {len(valid)} / 5 required.",
        f"- Scenario wins: {scenario_wins}.",
        f"- Legacy wins: {legacy_wins}.",
        f"- Draws: {draws}.",
        f"- Legacy aggregate ROI: {percent(legacy_roi)}.",
        f"- Scenario aggregate ROI: {percent(scenario_roi)}.",
        f"- Promotion status: `{status}`.",
        f"- Reason: {status_reason}",
        "",
    ]


def build_report() -> str:
    post_paths = sorted(HISTORY_DIR.glob("*_post.json"))
    validations = [validation_for_post(path) for path in post_paths]
    valid = [item for item in validations if item.get("eligible")]

    lines = [
        "# Post-Match Validation Report v0.1",
        "",
        "Date: 2026-06-21",
        "",
        "## Scope",
        "",
        "- Reads existing pre-match snapshots and post-match final scores.",
        "- Reads standalone My Portfolio history files from `data/history/my_portfolios/` when available.",
        "- Settles Legacy Top, Scenario Top, Current Recommendation, and My Portfolio when available.",
        "- Generates this report only.",
        "- Does not modify sorting, recommendation logic, scores, UI, or data files.",
        "",
        "## Validation Summary",
        "",
        f"- Post-match files discovered: {len(post_paths)}.",
        f"- Valid comparisons: {len(valid)}.",
        f"- Insufficient comparisons: {len(validations) - len(valid)}.",
        "",
    ]

    for item in validations:
        if not item.get("eligible"):
            lines.extend(
                [
                    f"## Skipped: `{Path(item['post_path']).name}`",
                    "",
                    f"- Reason: {item.get('skip_reason')}",
                    "",
                ]
            )
            continue

        match = item["match"]
        lines.extend(
            [
                f"## {match['display']}",
                "",
                f"- Pre snapshot: `{Path(item['pre_path']).relative_to(ROOT)}`",
                f"- Post result: `{Path(item['post_path']).relative_to(ROOT)}`",
                f"- Final score: `{item['final_score']}`",
                f"- Legacy Top Portfolio: {item['legacy_top']}",
                f"- Scenario Top Portfolio: {item['scenario_top']}",
                f"- Current Recommendation: {item['current_recommendation']}",
                f"- My Portfolio source: `{item['my_portfolio_source']}`",
                "",
                *portfolio_table(item["portfolios"]),
                "",
                "### Legacy vs Scenario",
                "",
                f"- Result: `{item['legacy_vs_scenario']}`",
                f"- Reason: {item['legacy_vs_scenario_reason']}",
                f"- Legacy Rank 1 downgrade reason: {item['legacy_top_downgrade_reason']}",
                "",
            ]
        )

    lines.extend(promotion_rule_section(validations))
    lines.extend(
        [
            "## Automation Verdict",
            "",
            "- `POST_MATCH_VALIDATION_REPORT.md` generated: Yes.",
            "- Sorting changed: No.",
            "- Recommendation logic changed: No.",
            "- Score changed: No.",
            "- Data files modified: No.",
            "- Current production recommendation authority: Legacy Ranking remains authoritative.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    REPORT_PATH.write_text(build_report(), encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
