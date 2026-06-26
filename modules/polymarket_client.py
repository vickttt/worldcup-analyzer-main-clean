import json
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st

from modules.cache_config import POLYMARKET_DATA_TTL
from modules.team_resolver import alias_candidates


GAMMA_API_BASE = "https://gamma-api.polymarket.com"
SOCCER_TAG_ID = "100350"
ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "cache" / "polymarket"
REQUEST_TIMEOUT = 4


def normalize_text(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_text.lower().replace(".", " ").split())


def name_candidates(value):
    candidates = {normalize_text(value)}
    for alias in alias_candidates(value):
        candidates.add(normalize_text(alias))
    return {candidate for candidate in candidates if candidate}


def parse_json_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    return []


def parse_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def yes_price(market):
    prices = parse_json_list(market.get("outcomePrices"))
    outcomes = parse_json_list(market.get("outcomes"))

    for index, outcome in enumerate(outcomes):
        if normalize_text(str(outcome)) == "yes" and index < len(prices):
            return parse_float(prices[index])

    return parse_float(market.get("lastTradePrice"))


def event_matches(event, match):
    text = normalize_text(" ".join([
        str(event.get("title", "")),
        str(event.get("slug", "")),
    ]))
    home_candidates = name_candidates(match["home_en"])
    away_candidates = name_candidates(match["away_en"])
    return any(name in text for name in home_candidates) and any(name in text for name in away_candidates)


def map_binary_markets(event, match):
    result = {
        "home_win": None,
        "draw": None,
        "away_win": None,
        "home_market": None,
        "draw_market": None,
        "away_market": None,
    }
    home_candidates = name_candidates(match["home_en"])
    away_candidates = name_candidates(match["away_en"])

    for market in event.get("markets", []):
        question = normalize_text(market.get("question", ""))
        price = yes_price(market)

        if price is None:
            continue

        if "draw" in question:
            result["draw"] = price
            result["draw_market"] = market
        elif any(name in question for name in home_candidates) and "win" in question:
            result["home_win"] = price
            result["home_market"] = market
        elif any(name in question for name in away_candidates) and "win" in question:
            result["away_win"] = price
            result["away_market"] = market

    return result


def market_total(markets, field):
    values = [parse_float(market.get(field)) for market in markets if market]
    values = [value for value in values if value is not None]
    return sum(values) if values else None


def empty_result(match, reason):
    return {
        "found": False,
        "home_win": None,
        "draw": None,
        "away_win": None,
        "volume": None,
        "liquidity": None,
        "source": "Polymarket Gamma API",
        "event_title": None,
        "event_slug": None,
        "event_url": None,
        "message": reason,
    }


def cache_key(match):
    home = normalize_text(match.get("home_en") or match.get("home_cn")).replace(" ", "_")
    away = normalize_text(match.get("away_en") or match.get("away_cn")).replace(" ", "_")
    return f"{home}_{away}".strip("_") or "unknown_match"


def cache_path(match):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{cache_key(match)}.json"


def parse_cache_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def read_file_cache(match):
    path = cache_path(match)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    fetched_at = parse_cache_datetime(payload.get("fetched_at"))
    result = payload.get("result")
    if not fetched_at or not isinstance(result, dict):
        return None
    age = (datetime.now(timezone.utc) - fetched_at.astimezone(timezone.utc)).total_seconds()
    if age <= POLYMARKET_DATA_TTL:
        result["cache"] = {
            "status": "file_cache",
            "age_hours": round(age / 3600, 2),
            "path": path.name,
        }
        return result
    return None


def write_file_cache(match, result):
    if not isinstance(result, dict):
        return
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }
    try:
        cache_path(match).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


@st.cache_data(ttl=POLYMARKET_DATA_TTL, show_spinner=False)
def fetch_polymarket(match, limit=100):
    cached = read_file_cache(match)
    if cached:
        return cached
    try:
        response = requests.get(
            f"{GAMMA_API_BASE}/events",
            params={
                "tag_id": SOCCER_TAG_ID,
                "related_tags": "true",
                "active": "true",
                "closed": "false",
                "limit": limit,
                "order": "volume",
                "ascending": "false",
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        result = empty_result(match, f"无法连接 Polymarket API：{error}")
        write_file_cache(match, result)
        return result

    events = response.json()
    matches = [event for event in events if event_matches(event, match)]

    if not matches:
        result = empty_result(
            match,
            f"未找到 {match['home_cn']} vs {match['away_cn']} 对应的 Polymarket 活跃市场。",
        )
        write_file_cache(match, result)
        return result

    event = matches[0]
    mapped = map_binary_markets(event, match)
    required_prices = [mapped["home_win"], mapped["draw"], mapped["away_win"]]

    if any(price is None for price in required_prices):
        result = empty_result(
            match,
            f"找到了 Polymarket 事件“{event.get('title')}”，但没有完整的主胜/平局/客胜价格。",
        )
        write_file_cache(match, result)
        return result

    selected_markets = [mapped["home_market"], mapped["draw_market"], mapped["away_market"]]
    volume = parse_float(event.get("volume")) or market_total(selected_markets, "volume")
    liquidity = parse_float(event.get("liquidity")) or market_total(selected_markets, "liquidity")
    slug = event.get("slug")

    result = {
        "found": True,
        "home_win": mapped["home_win"],
        "draw": mapped["draw"],
        "away_win": mapped["away_win"],
        "volume": volume,
        "liquidity": liquidity,
        "source": "Polymarket Gamma API 真实数据",
        "event_title": event.get("title"),
        "event_slug": slug,
        "event_url": f"https://polymarket.com/event/{slug}" if slug else None,
        "message": "已找到对应 Polymarket 市场。",
    }
    write_file_cache(match, result)
    return result
