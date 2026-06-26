#!/usr/bin/env python3
"""Run a 10-match historical odds backfill and ranking benchmark pilot.

This script is report-only. It writes isolated backfill snapshots under
data/history/backfill/ and Markdown reports. It does not import app.py or
modify production ranking, recommendation logic, UI, or existing history files.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import tomllib
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.result_distribution import build_result_distribution
from modules.shadow_metadata import attach_shadow_metadata
from modules.user_odds import build_recommendation_slots
from scripts.generate_hybrid_ranking_report import attach_hybrid_metadata
from scripts.generate_post_match_validation_report import settle_portfolio


API_BASE = "https://v3.football.api-sports.io"
BACKFILL_DIR = ROOT / "data/history/backfill"
PORTFOLIOS_REPORT = ROOT / "WORLD_CUP_BACKTEST_PORTFOLIOS.md"
BENCHMARK_REPORT = ROOT / "WORLD_CUP_RANKING_BENCHMARK_REPORT.md"

MARKETS = {
    "match_winner": {"bet_id": 1, "label": "Match Winner"},
    "asian_handicap": {"bet_id": 4, "label": "Asian Handicap"},
    "over_under": {"bet_id": 5, "label": "Over/Under"},
    "correct_score": {"bet_id": 10, "label": "Correct Score"},
}

SAMPLE_MATCHES = [
    {
        "fixture_id": 1489383,
        "date": "2026-06-16",
        "home": "France",
        "away": "Senegal",
        "final_score": "3:1",
        "sample_type": "强队深盘 / 高比分局",
    },
    {
        "fixture_id": 1489381,
        "date": "2026-06-17",
        "home": "Argentina",
        "away": "Algeria",
        "final_score": "3:0",
        "sample_type": "强队深盘",
    },
    {
        "fixture_id": 1539003,
        "date": "2026-06-17",
        "home": "Portugal",
        "away": "Congo DR",
        "final_score": "1:1",
        "sample_type": "冷门风险局 / 低比分局",
    },
    {
        "fixture_id": 1489384,
        "date": "2026-06-17",
        "home": "England",
        "away": "Croatia",
        "final_score": "4:2",
        "sample_type": "平衡局 / 高比分局",
    },
    {
        "fixture_id": 1489387,
        "date": "2026-06-18",
        "home": "Canada",
        "away": "Qatar",
        "final_score": "6:0",
        "sample_type": "强队深盘 / 高比分局",
    },
    {
        "fixture_id": 1489390,
        "date": "2026-06-19",
        "home": "Scotland",
        "away": "Morocco",
        "final_score": "0:1",
        "sample_type": "平衡局 / 冷门风险局",
    },
    {
        "fixture_id": 1489389,
        "date": "2026-06-20",
        "home": "Brazil",
        "away": "Haiti",
        "final_score": "3:0",
        "sample_type": "强队深盘",
    },
    {
        "fixture_id": 1539007,
        "date": "2026-06-20",
        "home": "Netherlands",
        "away": "Sweden",
        "final_score": "5:1",
        "sample_type": "平衡局 / 高比分局",
    },
    {
        "fixture_id": 1489393,
        "date": "2026-06-20",
        "home": "Germany",
        "away": "Ivory Coast",
        "final_score": "2:1",
        "sample_type": "强队深盘 / 盘口边界",
    },
    {
        "fixture_id": 1489392,
        "date": "2026-06-21",
        "home": "Ecuador",
        "away": "Curaçao",
        "final_score": "0:0",
        "sample_type": "平衡局 / 低比分局",
    },
]


def load_api_key() -> str:
    env_key = os.getenv("API_FOOTBALL_KEY")
    if env_key:
        return env_key.strip()

    secrets_path = ROOT / ".streamlit/secrets.toml"
    if secrets_path.exists():
        with secrets_path.open("rb") as handle:
            secrets = tomllib.load(handle)
        for key in ("API_FOOTBALL_KEY", "api_football_key"):
            if secrets.get(key):
                return str(secrets[key]).strip()

    raise RuntimeError("Missing API_FOOTBALL_KEY in environment or .streamlit/secrets.toml")


def request_api(path: str, params: dict[str, Any], retries: int = 4) -> list[dict[str, Any]]:
    api_key = load_api_key()
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                f"{API_BASE}{path}",
                params=params,
                timeout=30,
                headers={"x-apisports-key": api_key, "Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
            errors = payload.get("errors")
            if isinstance(errors, dict) and errors:
                raise RuntimeError("; ".join(str(value) for value in errors.values()))
            if isinstance(errors, list) and errors:
                raise RuntimeError("; ".join(str(value) for value in errors))
            response_rows = payload.get("response", [])
            return response_rows if isinstance(response_rows, list) else []
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * attempt)
    raise RuntimeError(f"API request failed for {path} {params}: {last_error}")


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def slugify(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return re.sub(r"_+", "_", text)


def match_slug(match: dict[str, Any]) -> str:
    return slugify(f"{match['date']}_{match['home']}_{match['away']}")


def safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def mean(values: list[float]) -> float | None:
    clean = [value for value in values if value is not None]
    return round(sum(clean) / len(clean), 4) if clean else None


def collect_values(api_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for row in api_rows:
        for bookmaker in row.get("bookmakers") or []:
            bookmaker_name = bookmaker.get("name") or f"bookmaker_{bookmaker.get('id')}"
            for bet in bookmaker.get("bets") or []:
                for value in bet.get("values") or []:
                    odd = safe_float(value.get("odd"))
                    if odd is None:
                        continue
                    values.append(
                        {
                            "bookmaker": bookmaker_name,
                            "value": str(value.get("value") or "").strip(),
                            "odd": odd,
                        }
                    )
    return values


def bookmaker_count(api_rows: list[dict[str, Any]]) -> int:
    names = {
        str(bookmaker.get("name") or bookmaker.get("id"))
        for row in api_rows
        for bookmaker in row.get("bookmakers") or []
    }
    return len([name for name in names if name])


def market_update(api_rows: list[dict[str, Any]]) -> str | None:
    updates = [str(row.get("update")) for row in api_rows if row.get("update")]
    if not updates:
        return None
    parsed = sorted((parse_dt(value), value) for value in updates if parse_dt(value))
    return parsed[-1][1] if parsed else updates[-1]


def kickoff_from_rows(api_rows: list[dict[str, Any]]) -> str | None:
    for row in api_rows:
        fixture = row.get("fixture") or {}
        if fixture.get("date"):
            return str(fixture["date"])
    return None


def average_winner(values: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for item in values:
        key = item["value"].lower()
        if key in {"home", "draw", "away"}:
            grouped[key].append(item["odd"])
    home = mean(grouped["home"])
    draw = mean(grouped["draw"])
    away = mean(grouped["away"])
    raw = {}
    if home and draw and away:
        raw = {"home_win": 1 / home, "draw": 1 / draw, "away_win": 1 / away}
        total = sum(raw.values())
        implied = {key: value / total for key, value in raw.items()}
    else:
        implied = {}
    return {
        "home_win": home,
        "draw": draw,
        "away_win": away,
        "raw_probabilities": raw,
        "implied_probabilities": implied,
    }


def normalize_handicap(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in values:
        if re.search(r"\b(Home|Away)\b\s*[+-]?\d+(?:\.\d+)?", item["value"], re.I):
            rows.append(
                {
                    "bookmaker": item["bookmaker"],
                    "value": item["value"],
                    "odd": item["odd"],
                }
            )
    return rows


def normalize_totals(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[float, dict[str, list[float]]] = defaultdict(lambda: {"over": [], "under": []})
    bookmakers: dict[float, set[str]] = defaultdict(set)
    for item in values:
        match = re.search(r"\b(Over|Under)\b\s*(\d+(?:\.\d+)?)", item["value"], re.I)
        if not match:
            continue
        side = match.group(1).lower()
        line = float(match.group(2))
        grouped[line][side].append(item["odd"])
        bookmakers[line].add(item["bookmaker"])

    rows = []
    for line, sides in sorted(grouped.items()):
        over_odds = mean(sides["over"])
        under_odds = mean(sides["under"])
        if over_odds and under_odds:
            rows.append(
                {
                    "line": line,
                    "over_odds": over_odds,
                    "under_odds": under_odds,
                    "bookmakers": sorted(bookmakers[line]),
                }
            )
    return rows


def normalize_correct_scores(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in values:
        score = str(item["value"]).replace(" - ", ":").replace("-", ":").strip()
        match = re.search(r"^(\d+):(\d+)$", score)
        if not match:
            continue
        rows.append(
            {
                "bookmaker": item["bookmaker"],
                "score": f"{int(match.group(1))}:{int(match.group(2))}",
                "odd": item["odd"],
            }
        )
    return rows


def market_quality(api_rows: list[dict[str, Any]], kickoff: str | None) -> dict[str, Any]:
    update = market_update(api_rows)
    update_dt = parse_dt(update)
    kickoff_dt = parse_dt(kickoff)
    is_before = bool(update_dt and kickoff_dt and update_dt < kickoff_dt)
    if not api_rows:
        quality = "invalid"
    elif is_before:
        quality = "true_pre_match"
    else:
        quality = "invalid"
    return {
        "odds_update_timestamp": update,
        "kickoff_timestamp": kickoff,
        "is_before_kickoff": is_before,
        "bookmaker_count": bookmaker_count(api_rows),
        "data_quality": quality,
    }


def fetch_fixture(match: dict[str, Any]) -> dict[str, Any]:
    rows = request_api("/fixtures", {"id": match["fixture_id"]})
    if not rows:
        raise RuntimeError(f"Fixture not found: {match['fixture_id']}")
    return rows[0]


def fetch_market(fixture_id: int, bet_id: int) -> list[dict[str, Any]]:
    return request_api("/odds", {"fixture": fixture_id, "bet": bet_id})


def build_snapshot(match: dict[str, Any]) -> dict[str, Any]:
    fixture = fetch_fixture(match)
    fixture_info = fixture.get("fixture") or {}
    teams = fixture.get("teams") or {}
    goals = fixture.get("goals") or {}
    kickoff = fixture_info.get("date")

    raw_markets: dict[str, list[dict[str, Any]]] = {}
    market_summaries: dict[str, dict[str, Any]] = {}
    market_values: dict[str, list[dict[str, Any]]] = {}

    for market_key, config in MARKETS.items():
        api_rows = fetch_market(match["fixture_id"], config["bet_id"])
        raw_markets[market_key] = api_rows
        market_values[market_key] = collect_values(api_rows)
        quality = market_quality(api_rows, kickoff)
        market_summaries[market_key] = {
            "market": config["label"],
            "bet_id": config["bet_id"],
            "odds_source": "API-Football",
            **quality,
        }

    winner = average_winner(market_values["match_winner"])
    odds = {
        "found": bool(winner.get("home_win") and winner.get("draw") and winner.get("away_win")),
        "home_win": winner.get("home_win"),
        "draw": winner.get("draw"),
        "away_win": winner.get("away_win"),
        "over_under": normalize_totals(market_values["over_under"]),
        "asian_handicap": normalize_handicap(market_values["asian_handicap"]),
        "raw_probabilities": winner.get("raw_probabilities"),
        "implied_probabilities": winner.get("implied_probabilities"),
        "source": "API-Football historical odds backfill",
        "event_title": f"{match['home']} vs {match['away']}",
        "event_id": match["fixture_id"],
        "message": "Historical pre-match odds loaded for benchmark pilot.",
    }
    api_football_data = {
        "asian_handicap": {
            "found": bool(odds["asian_handicap"]),
            "rows": odds["asian_handicap"],
            "raw": raw_markets["asian_handicap"],
        },
        "correct_score": {
            "found": bool(market_values["correct_score"]),
            "rows": normalize_correct_scores(market_values["correct_score"]),
            "raw": raw_markets["correct_score"],
        },
    }

    available_markets = [
        key
        for key, summary in market_summaries.items()
        if summary["bookmaker_count"] > 0 and summary["data_quality"] == "true_pre_match"
    ]
    all_true_pre_match = len(available_markets) == len(MARKETS)
    snapshot = {
        "source": "api_football_backfill",
        "is_backfill": True,
        "is_true_pre_match": all_true_pre_match,
        "odds_timestamp": max(
            (summary.get("odds_update_timestamp") or "" for summary in market_summaries.values()),
            default=None,
        ),
        "kickoff_time": kickoff,
        "data_quality": "true_pre_match" if all_true_pre_match else "invalid",
        "available_markets": available_markets,
        "market_quality": market_summaries,
        "match": {
            "fixture_id": match["fixture_id"],
            "date": match["date"],
            "home": (teams.get("home") or {}).get("name") or match["home"],
            "away": (teams.get("away") or {}).get("name") or match["away"],
            "home_cn": (teams.get("home") or {}).get("name") or match["home"],
            "away_cn": (teams.get("away") or {}).get("name") or match["away"],
            "display": f"{match['home']} vs {match['away']}",
            "sample_type": match["sample_type"],
            "status": (fixture_info.get("status") or {}).get("short"),
        },
        "post_match": {
            "final_score": f"{goals.get('home')}:{goals.get('away')}",
            "source": "API-Football fixture final score",
        },
        "odds": odds,
        "api_football_data": api_football_data,
        "raw_markets": raw_markets,
    }
    return snapshot


def write_backfill_snapshot(match: dict[str, Any], snapshot: dict[str, Any]) -> Path:
    BACKFILL_DIR.mkdir(parents=True, exist_ok=True)
    path = BACKFILL_DIR / f"{match_slug(match)}_pre.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return path


def num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def role_for_item(item: dict[str, Any]) -> str:
    item_type = item.get("type")
    if item_type in {"winner", "handicap"}:
        return "方向资产"
    if item_type == "total":
        return "节奏资产"
    if item_type == "correct_score":
        odds = num(item.get("effective_odds") or item.get("standard_odds"))
        selection = str(item.get("selection") or "")
        if odds >= 18 or re.match(r"^[45]:", selection):
            return "尾部资产"
        return "收益资产"
    return "保险资产"


def with_amounts(items: list[dict[str, Any]], budget: float = 1000.0) -> list[dict[str, Any]]:
    active = [deepcopy(item) for item in items if item.get("type") != "empty"]
    if not active:
        return []
    total_share = sum(max(num(item.get("share")), 0.0) for item in active)
    if total_share <= 0:
        equal = 1 / len(active)
        for item in active:
            item["share"] = equal
    else:
        for item in active:
            item["share"] = max(num(item.get("share")), 0.0) / total_share
    for item in active:
        item["amount"] = round(budget * num(item.get("share")), 2)
        item["odds"] = num(item.get("effective_odds") or item.get("standard_odds"))
    return active


def score_item(item: dict[str, Any]) -> float:
    return num(item.get("score")) + num(item.get("path_consistency_score")) - num(item.get("path_conflict_penalty")) * 0.5


def candidate_portfolios(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    recommended = [item for item in slots if item.get("recommended") and item.get("type") != "empty"]
    if not recommended:
        recommended = sorted([item for item in slots if item.get("type") != "empty"], key=score_item, reverse=True)[:5]

    direction = [item for item in slots if item.get("type") in {"winner", "handicap"}]
    totals = sorted([item for item in slots if item.get("type") == "total"], key=score_item, reverse=True)
    correct_core = sorted(
        [
            item
            for item in slots
            if item.get("type") == "correct_score" and num(item.get("path_conflict_penalty")) < 35
        ],
        key=lambda item: (
            -num(item.get("market_center_rank"), 99),
            score_item(item),
        ),
        reverse=True,
    )
    correct_tail = sorted(
        [item for item in slots if item.get("type") == "correct_score"],
        key=lambda item: num(item.get("effective_odds") or item.get("standard_odds")),
        reverse=True,
    )
    legacy_value = sorted(
        [item for item in slots if item.get("type") != "empty"],
        key=lambda item: (
            score_item(item)
            + max(num(item.get("effective_odds") or item.get("standard_odds")) - 2, 0) * 1.4
            + max(num(item.get("ev_lift")), 0) * 60
        ),
        reverse=True,
    )

    specs = [
        ("Legacy Value Portfolio", legacy_value[:7]),
        ("Recommended Blend Portfolio", recommended[:8]),
        ("Direction + Return Portfolio", direction[:2] + correct_core[:3]),
        ("Scenario Balanced Portfolio", direction[:2] + totals[:1] + correct_core[:2]),
        ("Tempo Watch Portfolio", totals[:2] + direction[:1]),
        ("Tail Upside Portfolio", direction[:1] + correct_tail[:4]),
    ]

    portfolios = []
    for name, items in specs:
        unique: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for item in items:
            key = (str(item.get("type")), str(item.get("selection")))
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        if unique:
            portfolios.append({"name": name, "rank_name": name, "items": with_amounts(unique)})
    return portfolios


def evaluate_strategy(strategy: dict[str, Any]) -> dict[str, Any]:
    items = strategy.get("items") or []
    stake = sum(num(item.get("amount")) for item in items)
    if stake <= 0:
        strategy.update({"score": 0, "expected_yield": 0, "sharpe_ratio": 0, "max_loss": 0})
        return strategy

    expected_profit = 0.0
    coverage = 0.0
    direction = 0.0
    strategic = 0.0
    consistency = 0.0
    exposure: dict[str, float] = defaultdict(float)

    for item in items:
        amount = num(item.get("amount"))
        share = amount / stake
        odds = num(item.get("effective_odds") or item.get("standard_odds") or item.get("odds"))
        probability = num(item.get("probability"), 1 / odds if odds else 0)
        expected_profit += amount * (probability * odds - 1) if odds else 0
        coverage += share * num(item.get("coverage_rate"))
        direction += share * num(item.get("direction_alignment_score"))
        strategic += share * score_item(item)
        item_consistency = clamp(num(item.get("path_consistency_score")) - num(item.get("path_conflict_penalty")) * 0.6 + 60)
        consistency += share * item_consistency / 100
        exposure[role_for_item(item)] += share

    expected_yield = expected_profit / stake
    tail_share = exposure.get("尾部资产", 0.0)
    tempo_share = exposure.get("节奏资产", 0.0)
    direction_share = exposure.get("方向资产", 0.0)
    return_share = exposure.get("收益资产", 0.0)
    max_loss = stake
    max_profit = sum(num(item.get("amount")) * max(num(item.get("odds")) - 1, 0) for item in items)
    concentration = max((num(item.get("amount")) / stake for item in items), default=0)
    upside_ratio = max_profit / stake if stake else 0
    role_adjustment = 0
    if direction_share >= 0.25:
        role_adjustment += 6
    if return_share >= 0.12:
        role_adjustment += 3
    if tempo_share > 0.55 and direction_share < 0.20:
        role_adjustment -= 2
    if tail_share > 0.25:
        role_adjustment += 6
    elif tail_share > 0.15:
        role_adjustment += 3

    score = (
        38
        + expected_yield * 90
        + coverage * 12
        + consistency * 18
        + direction * 0.08
        + strategic * 0.10
        + min(upside_ratio, 12) * 4.2
        + role_adjustment
        - concentration * 8
    )
    strategy.update(
        {
            "score": round(clamp(score), 1),
            "expected_yield": round(expected_yield, 4),
            "capital_efficiency": round(expected_yield, 4),
            "sharpe_ratio": round(expected_profit / max_loss, 4) if max_loss else 0,
            "max_loss": round(max_loss, 2),
            "max_profit": round(max_profit, 2),
            "coverage": round(coverage, 4),
            "direction_alignment": round(direction, 2),
            "strategic_value": round(strategic, 2),
            "consistency_score": round(consistency, 4),
            "concentration": round(concentration, 4),
            "portfolio_style": {
                "role_exposure": dict(exposure),
                "tail_share": round(tail_share, 4),
                "tempo_share": round(tempo_share, 4),
                "return_share": round(return_share, 4),
                "insurance_share": round(exposure.get("保险资产", 0.0), 4),
            },
            "role_constraint": {"adjustment": role_adjustment},
        }
    )
    return strategy


def build_strategies(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    match = snapshot["match"]
    odds = snapshot["odds"]
    api_football_data = snapshot["api_football_data"]
    distribution = build_result_distribution(match, odds, {"found": False})
    slots = build_recommendation_slots(match, odds, api_football_data, {}, distribution)
    strategies = [evaluate_strategy(strategy) for strategy in candidate_portfolios(slots)]
    strategies.sort(key=lambda item: num(item.get("score")), reverse=True)
    for index, strategy in enumerate(strategies, start=1):
        strategy["legacy_rank"] = index
    shadowed = attach_shadow_metadata(strategies, match, distribution)
    attach_hybrid_metadata(shadowed)
    snapshot["probability_distribution"] = distribution
    snapshot["strategy_snapshot"] = {"strategies": shadowed}
    return shadowed


def pick_tops(strategies: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    legacy_top = strategies[0]
    scenario_top = min(strategies, key=lambda item: num((item.get("shadow") or {}).get("scenario_rank"), 999))
    hybrid_top = min(strategies, key=lambda item: num((item.get("hybrid") or {}).get("hybrid_rank"), 999))
    return legacy_top, scenario_top, hybrid_top


def portfolio_name(strategy: dict[str, Any]) -> str:
    return str(strategy.get("rank_name") or strategy.get("name") or "-")


def percent(value: Any) -> str:
    return f"{num(value) * 100:.1f}%"


def money(value: Any) -> str:
    return f"{num(value):+.0f}"


def strategy_row(strategy: dict[str, Any]) -> str:
    shadow = strategy.get("shadow") or {}
    hybrid = strategy.get("hybrid") or {}
    return (
        "| "
        + " | ".join(
            [
                portfolio_name(strategy),
                str(shadow.get("legacy_rank", "-")),
                str(shadow.get("scenario_rank", "-")),
                str(hybrid.get("hybrid_rank", "-")),
                f"{num(strategy.get('score')):.1f}",
                f"{num(hybrid.get('hybrid_score')):.1f}",
                str(shadow.get("shadow_verdict", "-")),
                str(hybrid.get("guardrail_status", "-")),
                str(hybrid.get("hybrid_rank_reason", "-")),
            ]
        )
        + " |"
    )


def settle_top(strategy: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    match = snapshot["match"]
    final_score = snapshot["post_match"]["final_score"]
    return settle_portfolio(strategy, match, final_score)


def compare_systems(rows: dict[str, dict[str, Any]]) -> str:
    rois = {key: num(value["outcome"]["roi"]) for key, value in rows.items()}
    best_roi = max(rois.values())
    winners = [key for key, value in rois.items() if abs(value - best_roi) < 0.02]
    if len(winners) != 1:
        return "Draw"
    return f"{winners[0]} Winner"


def run() -> list[dict[str, Any]]:
    results = []
    for match in SAMPLE_MATCHES:
        snapshot = build_snapshot(match)
        strategies = build_strategies(snapshot)
        snapshot_path = write_backfill_snapshot(match, snapshot)
        legacy_top, scenario_top, hybrid_top = pick_tops(strategies)
        rows = {
            "Legacy": {"strategy": legacy_top, "outcome": settle_top(legacy_top, snapshot)},
            "Scenario": {"strategy": scenario_top, "outcome": settle_top(scenario_top, snapshot)},
            "Hybrid": {"strategy": hybrid_top, "outcome": settle_top(hybrid_top, snapshot)},
        }
        results.append(
            {
                "match": match,
                "snapshot": snapshot,
                "snapshot_path": snapshot_path,
                "strategies": strategies,
                "systems": rows,
                "winner": compare_systems(rows),
            }
        )
    return results


def build_portfolios_report(results: list[dict[str, Any]]) -> str:
    lines = [
        "# World Cup Backtest Portfolios",
        "",
        "Date: 2026-06-21",
        "",
        "## Scope",
        "",
        "- Phase B pilot only: 10 completed matches.",
        "- Reads API-Football historical odds for Match Winner, Asian Handicap, Over/Under, and Correct Score.",
        "- Writes isolated snapshots under `data/history/backfill/` only.",
        "- Generates report-only Legacy, Scenario, and Hybrid portfolio candidates.",
        "- Does not modify production ranking, recommendation logic, UI, or existing history snapshots.",
        "",
    ]
    for result in results:
        match = result["match"]
        snapshot = result["snapshot"]
        lines.extend(
            [
                f"## {match['home']} vs {match['away']}",
                "",
                f"- Fixture ID: `{match['fixture_id']}`",
                f"- Sample type: {match['sample_type']}",
                f"- Final score: `{snapshot['post_match']['final_score']}`",
                f"- Backfill snapshot: `{result['snapshot_path'].relative_to(ROOT)}`",
                f"- Data quality: `{snapshot['data_quality']}`",
                f"- Available markets: {', '.join(snapshot['available_markets'])}",
                "",
                "| Portfolio | Legacy Rank | Scenario Rank | Hybrid Rank | Legacy Score | Hybrid Score | Shadow Verdict | Guardrail | Hybrid Rank Reason |",
                "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
            ]
        )
        for strategy in sorted(result["strategies"], key=lambda item: num((item.get("shadow") or {}).get("legacy_rank"), 999)):
            lines.append(strategy_row(strategy))
        lines.append("")
        for label, row in result["systems"].items():
            outcome = row["outcome"]
            strategy = row["strategy"]
            lines.append(
                f"- {label} Top: {portfolio_name(strategy)} | Hit: `{outcome['hit_status']}` | "
                f"P/L: {money(outcome['profit_loss'])} | ROI: {percent(outcome['roi'])} | "
                f"Max Drawdown: {money(-num(outcome['max_drawdown']))}"
            )
        lines.extend(["", f"- Match winner: `{result['winner']}`", ""])
    return "\n".join(lines).rstrip() + "\n"


def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [item for item in results if item["snapshot"]["data_quality"] == "true_pre_match"]
    invalid = [item for item in results if item["snapshot"]["data_quality"] != "true_pre_match"]
    counters = {"Legacy Wins": 0, "Scenario Wins": 0, "Hybrid Wins": 0, "Draws": 0}
    profits = {"Legacy": 0.0, "Scenario": 0.0, "Hybrid": 0.0}
    stakes = {"Legacy": 0.0, "Scenario": 0.0, "Hybrid": 0.0}
    for item in valid:
        winner = item["winner"]
        if winner == "Legacy Winner":
            counters["Legacy Wins"] += 1
        elif winner == "Scenario Winner":
            counters["Scenario Wins"] += 1
        elif winner == "Hybrid Winner":
            counters["Hybrid Wins"] += 1
        else:
            counters["Draws"] += 1
        for system in profits:
            outcome = item["systems"][system]["outcome"]
            profits[system] += num(outcome["profit_loss"])
            stakes[system] += num(outcome["stake"])
    roi = {system: profits[system] / stakes[system] if stakes[system] else 0.0 for system in profits}
    return {
        "valid_matches": len(valid),
        "invalid_matches": len(invalid),
        **counters,
        "roi": roi,
        "profits": profits,
        "stakes": stakes,
    }


def build_benchmark_report(results: list[dict[str, Any]]) -> str:
    stats = aggregate(results)
    roi = stats["roi"]
    hybrid_vs_legacy = roi["Hybrid"] - roi["Legacy"]
    hybrid_vs_scenario = roi["Hybrid"] - roi["Scenario"]
    best_system = max(roi, key=lambda key: roi[key])

    lines = [
        "# World Cup Ranking Benchmark Report",
        "",
        "Date: 2026-06-21",
        "",
        "## Phase B Pilot Summary",
        "",
        f"- Valid matches: {stats['valid_matches']}.",
        f"- Invalid odds matches: {stats['invalid_matches']}.",
        f"- Legacy Wins: {stats['Legacy Wins']}.",
        f"- Scenario Wins: {stats['Scenario Wins']}.",
        f"- Hybrid Wins: {stats['Hybrid Wins']}.",
        f"- Draws: {stats['Draws']}.",
        f"- Legacy ROI: {percent(roi['Legacy'])}.",
        f"- Scenario ROI: {percent(roi['Scenario'])}.",
        f"- Hybrid ROI: {percent(roi['Hybrid'])}.",
        f"- Hybrid vs Legacy Edge: {percent(hybrid_vs_legacy)}.",
        f"- Hybrid vs Scenario Edge: {percent(hybrid_vs_scenario)}.",
        f"- Best system in this pilot: `{best_system}`.",
        "",
        "## Match-Level Benchmark",
        "",
        "| Match | Type | Quality | Legacy Top ROI | Scenario Top ROI | Hybrid Top ROI | Winner |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for item in results:
        match = item["match"]
        systems = item["systems"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{match['home']} vs {match['away']}",
                    match["sample_type"],
                    item["snapshot"]["data_quality"],
                    percent(systems["Legacy"]["outcome"]["roi"]),
                    percent(systems["Scenario"]["outcome"]["roi"]),
                    percent(systems["Hybrid"]["outcome"]["roi"]),
                    item["winner"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Data Quality",
            "",
            "| Match | Match Winner | Asian Handicap | Over/Under | Correct Score |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in results:
        match = item["match"]
        quality = item["snapshot"]["market_quality"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{match['home']} vs {match['away']}",
                    quality["match_winner"]["data_quality"],
                    quality["asian_handicap"]["data_quality"],
                    quality["over_under"]["data_quality"],
                    quality["correct_score"]["data_quality"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Phase C Recommendation",
            "",
            (
                "- Recommendation: `Phase C Ready`."
                if stats["valid_matches"] == 10 and stats["invalid_matches"] == 0
                else "- Recommendation: `Phase C Not Ready` until invalid/missing odds are resolved."
            ),
            "- Phase C should still remain report-only until the full completed-match benchmark confirms Hybrid stability.",
            "- No production sorting, UI, recommendation logic, or historical source snapshots were modified by this pilot.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    results = run()
    PORTFOLIOS_REPORT.write_text(build_portfolios_report(results), encoding="utf-8")
    BENCHMARK_REPORT.write_text(build_benchmark_report(results), encoding="utf-8")
    stats = aggregate(results)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
