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
EVENT_EXCLUDE_TERMS = (
    "more markets",
    "exact score",
    "player props",
    "team props",
    "spread",
    "o/u",
    "over under",
)
EXTRA_TEAM_ALIASES = {
    "usa": {"united states", "united states of america", "us", "usmnt"},
    "united states": {"usa", "united states of america", "us", "usmnt"},
    "bosnia and herzegovina": {"bosnia", "bosnia herzegovina", "bosnia-herzegovina", "bih"},
    "dr congo": {
        "congo dr",
        "drc",
        "congo drc",
        "democratic republic of congo",
        "democratic republic of the congo",
    },
}


def normalize_text(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(
        ascii_text.lower()
        .replace("&", " and ")
        .replace(".", " ")
        .replace("-", " ")
        .split()
    )


def name_candidates(value):
    candidates = {normalize_text(value)}
    for alias in alias_candidates(value):
        candidates.add(normalize_text(alias))
    for candidate in list(candidates):
        candidates.update(EXTRA_TEAM_ALIASES.get(candidate, set()))
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


def price_for_outcome(market, outcome_name):
    prices = parse_json_list(market.get("outcomePrices"))
    outcomes = parse_json_list(market.get("outcomes"))
    wanted = normalize_text(outcome_name)

    for index, outcome in enumerate(outcomes):
        if normalize_text(str(outcome)) == wanted and index < len(prices):
            return parse_float(prices[index])

    return None


def text_matches_any(text, candidates):
    return any(candidate and candidate in text for candidate in candidates)


def outcome_matches_team(outcome, candidates):
    return normalize_text(outcome) in candidates or text_matches_any(normalize_text(outcome), candidates)


def is_draw_outcome(outcome):
    return normalize_text(outcome) in {"draw", "tie"}


def event_matches(event, match):
    text = normalize_text(" ".join([
        str(event.get("title", "")),
        str(event.get("slug", "")),
    ]))
    home_candidates = name_candidates(match["home_en"])
    away_candidates = name_candidates(match["away_en"])
    return text_matches_any(text, home_candidates) and text_matches_any(text, away_candidates)


def empty_mapping():
    return {
        "home_win": None,
        "draw": None,
        "away_win": None,
        "home_market": None,
        "draw_market": None,
        "away_market": None,
    }


def map_three_way_market(event, match):
    result = empty_mapping()
    home_candidates = name_candidates(match["home_en"])
    away_candidates = name_candidates(match["away_en"])

    for market in event.get("markets", []):
        outcomes = parse_json_list(market.get("outcomes"))
        if len(outcomes) < 3:
            continue

        home_outcome = next((item for item in outcomes if outcome_matches_team(item, home_candidates)), None)
        away_outcome = next((item for item in outcomes if outcome_matches_team(item, away_candidates)), None)
        draw_outcome = next((item for item in outcomes if is_draw_outcome(item)), None)
        if not home_outcome or not away_outcome or not draw_outcome:
            continue

        result["home_win"] = price_for_outcome(market, home_outcome)
        result["draw"] = price_for_outcome(market, draw_outcome)
        result["away_win"] = price_for_outcome(market, away_outcome)
        result["home_market"] = market
        result["draw_market"] = market
        result["away_market"] = market
        if all(result[key] is not None for key in ("home_win", "draw", "away_win")):
            return result

    return result


def map_binary_markets(event, match):
    result = empty_mapping()
    home_candidates = name_candidates(match["home_en"])
    away_candidates = name_candidates(match["away_en"])

    for market in event.get("markets", []):
        market_text = normalize_text(" ".join([
            str(market.get("question", "")),
            str(market.get("groupItemTitle", "")),
        ]))
        price = yes_price(market)

        if price is None:
            continue

        if "draw" in market_text:
            result["draw"] = price
            result["draw_market"] = market
        elif text_matches_any(market_text, home_candidates) and "win" in market_text:
            result["home_win"] = price
            result["home_market"] = market
        elif text_matches_any(market_text, away_candidates) and "win" in market_text:
            result["away_win"] = price
            result["away_market"] = market

    return result


def map_event_markets(event, match):
    three_way = map_three_way_market(event, match)
    binary = map_binary_markets(event, match)
    return {
        key: three_way.get(key) if three_way.get(key) is not None else binary.get(key)
        for key in empty_mapping()
    }


def mapping_complete(mapped):
    return all(mapped.get(key) is not None for key in ("home_win", "draw", "away_win"))


def event_rank(event, mapped):
    title = normalize_text(event.get("title") or "")
    slug = normalize_text(event.get("slug") or "")
    text = f"{title} {slug}"
    rank = 100 if mapping_complete(mapped) else 0
    if " vs " in f" {title} " and not any(term in text for term in EVENT_EXCLUDE_TERMS):
        rank += 25
    if len(event.get("markets") or []) <= 8:
        rank += 10
    if any(term in text for term in EVENT_EXCLUDE_TERMS):
        rank -= 50
    return rank


def select_event_with_mapping(events, match):
    ranked = []
    for event in events:
        mapped = map_event_markets(event, match)
        ranked.append((event_rank(event, mapped), event, mapped))
    if not ranked:
        return None, empty_mapping()
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[0][1], ranked[0][2]


def market_total(markets, field):
    values = [parse_float(market.get(field)) for market in markets if market]
    values = [value for value in values if value is not None]
    return sum(values) if values else None


def empty_result(match, reason, event=None, mapped=None):
    slug = (event or {}).get("slug")
    return {
        "found": False,
        "home_win": (mapped or {}).get("home_win"),
        "draw": (mapped or {}).get("draw"),
        "away_win": (mapped or {}).get("away_win"),
        "volume": None,
        "liquidity": None,
        "source": "Polymarket Gamma API",
        "event_title": (event or {}).get("title"),
        "event_slug": slug,
        "event_url": f"https://polymarket.com/event/{slug}" if slug else None,
        "message": reason,
    }


def cache_key(match, selected_fixture=None):
    fixture_id = (selected_fixture or {}).get("fixture_id")
    if fixture_id:
        return f"fixture_{fixture_id}"
    home = normalize_text(match.get("home_en") or match.get("home_cn")).replace(" ", "_")
    away = normalize_text(match.get("away_en") or match.get("away_cn")).replace(" ", "_")
    return f"{home}_{away}".strip("_") or "unknown_match"


def cache_path(match, selected_fixture=None):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{cache_key(match, selected_fixture)}.json"


def parse_cache_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def read_file_cache(match, selected_fixture=None):
    path = cache_path(match, selected_fixture)
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


def write_file_cache(match, result, selected_fixture=None):
    if not isinstance(result, dict):
        return
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }
    try:
        cache_path(match, selected_fixture).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


@st.cache_data(ttl=POLYMARKET_DATA_TTL, show_spinner=False)
def fetch_polymarket(match, selected_fixture=None, limit=100):
    cached = read_file_cache(match, selected_fixture)
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
        write_file_cache(match, result, selected_fixture)
        return result

    events = response.json()
    matches = [event for event in events if event_matches(event, match)]

    if not matches:
        result = empty_result(
            match,
            f"未找到 {match['home_cn']} vs {match['away_cn']} 对应的 Polymarket 活跃市场。",
        )
        write_file_cache(match, result, selected_fixture)
        return result

    event, mapped = select_event_with_mapping(matches, match)
    required_prices = [mapped["home_win"], mapped["draw"], mapped["away_win"]]

    if any(price is None for price in required_prices):
        result = empty_result(
            match,
            f"找到了 Polymarket 事件“{event.get('title')}”，但没有完整的主胜/平局/客胜价格。",
            event=event,
            mapped=mapped,
        )
        write_file_cache(match, result, selected_fixture)
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
        "fixture_id": (selected_fixture or {}).get("fixture_id"),
        "message": "已找到对应 Polymarket 市场。",
    }
    write_file_cache(match, result, selected_fixture)
    return result
