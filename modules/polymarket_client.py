import json
import unicodedata

import requests
import streamlit as st

from modules.cache_config import POLYMARKET_DATA_TTL


GAMMA_API_BASE = "https://gamma-api.polymarket.com"
SOCCER_TAG_ID = "100350"


def normalize_text(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_text.lower().replace(".", " ").split())


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
    return normalize_text(match["home_en"]) in text and normalize_text(match["away_en"]) in text


def map_binary_markets(event, match):
    result = {
        "home_win": None,
        "draw": None,
        "away_win": None,
        "home_market": None,
        "draw_market": None,
        "away_market": None,
    }
    home = normalize_text(match["home_en"])
    away = normalize_text(match["away_en"])

    for market in event.get("markets", []):
        question = normalize_text(market.get("question", ""))
        price = yes_price(market)

        if price is None:
            continue

        if "draw" in question:
            result["draw"] = price
            result["draw_market"] = market
        elif home in question and "win" in question:
            result["home_win"] = price
            result["home_market"] = market
        elif away in question and "win" in question:
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


@st.cache_data(ttl=POLYMARKET_DATA_TTL, show_spinner=False)
def fetch_polymarket(match, limit=100):
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
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        return empty_result(match, f"无法连接 Polymarket API：{error}")

    events = response.json()
    matches = [event for event in events if event_matches(event, match)]

    if not matches:
        return empty_result(
            match,
            f"未找到 {match['home_cn']} vs {match['away_cn']} 对应的 Polymarket 活跃市场。",
        )

    event = matches[0]
    mapped = map_binary_markets(event, match)
    required_prices = [mapped["home_win"], mapped["draw"], mapped["away_win"]]

    if any(price is None for price in required_prices):
        return empty_result(
            match,
            f"找到了 Polymarket 事件“{event.get('title')}”，但没有完整的主胜/平局/客胜价格。",
        )

    selected_markets = [mapped["home_market"], mapped["draw_market"], mapped["away_market"]]
    volume = parse_float(event.get("volume")) or market_total(selected_markets, "volume")
    liquidity = parse_float(event.get("liquidity")) or market_total(selected_markets, "liquidity")
    slug = event.get("slug")

    return {
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
