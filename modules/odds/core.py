"""Odds and market calculation helpers extracted from app.py.

This module is a pure move refactor target; function bodies are intentionally unchanged.
"""

import re

from modules.portfolio_engine import normalize_handicap_line, settle_asian_handicap
from modules.user_odds import build_market_candidates, candidate_with_actual


def fmt_odds(value):
    if value is None:
        return "-"
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return str(value)

def market_odds_overview_rows(combo):
    rows = []
    for item in combo:
        if item.get("type") in {"empty"}:
            continue
        actual = item.get("actual_odds")
        market = item.get("standard_odds")
        if actual is None or market is None:
            status = "⚪ 未输入实际赔率"
        elif actual > market:
            status = "🟢 实际赔率更优"
        elif actual < market:
            status = "🔴 实际赔率偏低"
        else:
            status = "⚪ 与市场一致"
        rows.append({
            "投注": item.get("name", "-"),
            "实际赔率": fmt_odds(actual),
            "市场赔率": fmt_odds(market),
            "差异": f"{(item.get('edge') or 0) * 100:+.1f}%" if item.get("edge") is not None else "-",
            "EV提升": f"{(item.get('ev_lift') or 0) * 100:+.1f}%" if item.get("ev_lift") is not None else "-",
            "_ev_lift": item.get("ev_lift") if item.get("ev_lift") is not None else -999,
            "状态": status,
        })
    return rows

def actual_odds_completeness(combo):
    candidates = [item for item in combo if item.get("type") != "empty"]
    if not candidates:
        return {"entered": 0, "total": 0, "ratio": 0, "missing": []}
    entered = [item for item in candidates if item.get("actual_odds")]
    missing = [item.get("name", "-") for item in candidates if not item.get("actual_odds")]
    return {
        "entered": len(entered),
        "total": len(candidates),
        "ratio": len(entered) / len(candidates),
        "missing": missing,
    }

def actual_odds_completeness_for_match(match, odds, api_football_data, actual_odds, fallback_combo):
    raw_candidates = build_market_candidates(match, odds, api_football_data)
    if not raw_candidates:
        return actual_odds_completeness(fallback_combo)

    required = []
    seen = set()
    for candidate in raw_candidates:
        key = (candidate.get("type"), candidate.get("slot"))
        if candidate.get("type") == "total":
            key = ("total", "主大小球")
            if key in seen:
                continue
            total_candidates = [
                candidate_with_actual(item, actual_odds)
                for item in raw_candidates
                if item.get("type") == "total"
            ]
            matched_total = next((item for item in total_candidates if item.get("actual_odds")), None)
            required.append(matched_total or {**candidate, "name": "大小球主盘口", "actual_odds": None})
            seen.add(key)
            continue
        if key in seen:
            continue
        seen.add(key)
        required.append(candidate_with_actual(candidate, actual_odds))

    entered = [item for item in required if item.get("actual_odds")]
    missing = [item.get("name", "-") for item in required if not item.get("actual_odds")]
    return {
        "entered": len(entered),
        "total": len(required),
        "ratio": len(entered) / len(required) if required else 0,
        "missing": missing,
    }

def parse_handicap_selection(selection):
    text = str(selection or "")
    match = re.search(r"\b(Home|Away)\b\s*([+-]?\d+(?:\.\d+)?(?:/[+-]?\d+(?:\.\d+)?)?)", text, re.I)
    if match:
        line_info = normalize_handicap_line(match.group(2))
        return match.group(1).lower(), line_info.get("decimal_line")
    return None, None

def parse_total_selection(selection):
    text = str(selection or "")
    match = re.search(r"(Under|Over|小于|大于)\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
    if not match:
        return None, None
    side = "under" if match.group(1).lower() in {"under", "小于"} else "over"
    return side, float(match.group(2))

def winner_outcome(item, match, home_goals, away_goals):
    selection = str(item.get("selection") or item.get("name") or "")
    if home_goals == away_goals:
        result = "平局"
    elif home_goals > away_goals:
        result = match["home_cn"]
    else:
        result = match["away_cn"]
    return "win" if result in selection else "lose"

def handicap_outcome(item, home_goals, away_goals):
    side, line = parse_handicap_selection(item.get("selection") or item.get("name"))
    if side is None:
        return None
    adjusted = home_goals + line if side == "home" else away_goals + line
    opponent = away_goals if side == "home" else home_goals
    if abs(adjusted - opponent) < 0.001:
        return "push"
    return "win" if adjusted > opponent else "lose"

def handicap_profit_value(item, match, score, amount=None):
    odds_value = item.get("odds") or item.get("effective_odds") or item.get("standard_odds")
    if not odds_value:
        return 0
    side, line = parse_handicap_selection(item.get("selection") or item.get("name"))
    if side is None:
        return 0
    line_info = item.get("handicap_line") or normalize_handicap_line(line)
    return round(settle_asian_handicap(score, side, line_info.get("split_legs"), odds_value, amount if amount is not None else item.get("amount", 0)))

def total_outcome(item, home_goals, away_goals):
    side, line = parse_total_selection(item.get("selection") or item.get("name"))
    if side is None:
        return None
    total_goals = home_goals + away_goals
    if side == "under":
        return "win" if total_goals < line else "lose"
    return "win" if total_goals > line else "lose"

def correct_score_outcome(item, home_goals, away_goals):
    return "win" if str(item.get("selection")) == f"{home_goals}:{away_goals}" else "lose"
