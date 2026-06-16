import os
import re
import tomllib
import unicodedata
from pathlib import Path

import requests
import streamlit as st

from modules.cache_config import ODDS_DATA_TTL


THE_ODDS_API_BASE = "https://api.the-odds-api.com/v4"
WORLD_CUP_SPORT_KEYS = ["soccer_fifa_world_cup"]


def normalize_text(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_text.lower().replace(".", " ").replace("-", " ").split())


def load_the_odds_api_key():
    env_key = os.getenv("THE_ODDS_API_KEY")
    if env_key:
        return env_key.strip()

    secrets_path = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        with secrets_path.open("rb") as file:
            secrets = tomllib.load(file)
        for key in ["THE_ODDS_API_KEY", "the_odds_api_key"]:
            if secrets.get(key):
                return str(secrets[key]).strip()

    return None


def empty_result(reason):
    return {
        "found": False,
        "home_win": None,
        "draw": None,
        "away_win": None,
        "over_under_line": None,
        "asian_handicap": [],
        "over_under": [],
        "raw_probabilities": None,
        "implied_probabilities": None,
        "source": "The Odds API",
        "event_title": None,
        "event_id": None,
        "message": reason,
    }


def redact_secret(value):
    return re.sub(r"apiKey=[^&\\s)]+", "apiKey=***", str(value))


def raw_probabilities(home_win, draw, away_win):
    return {
        "home_win": 1 / home_win,
        "draw": 1 / draw,
        "away_win": 1 / away_win,
    }


def implied_probabilities(home_win, draw, away_win):
    raw = raw_probabilities(home_win, draw, away_win)
    total = sum(raw.values())
    return {key: value / total for key, value in raw.items()}


def parse_price(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 1 else None


def event_matches(event, match):
    home = normalize_text(match["home_en"])
    away = normalize_text(match["away_en"])
    event_home = normalize_text(event.get("home_team", ""))
    event_away = normalize_text(event.get("away_team", ""))
    title = normalize_text(" ".join([event_home, event_away]))

    direct = home in event_home and away in event_away
    reversed_match = home in event_away and away in event_home
    fuzzy = home in title and away in title
    return direct or reversed_match or fuzzy


def extract_h2h_prices(event, match):
    home = normalize_text(match["home_en"])
    away = normalize_text(match["away_en"])

    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market.get("key") != "h2h":
                continue

            prices = {}
            for outcome in market.get("outcomes", []):
                name = normalize_text(outcome.get("name", ""))
                price = parse_price(outcome.get("price"))
                if not price:
                    continue
                if name == "draw":
                    prices["draw"] = price
                elif home in name:
                    prices["home_win"] = price
                elif away in name:
                    prices["away_win"] = price

            if all(prices.get(key) for key in ["home_win", "draw", "away_win"]):
                return prices, bookmaker.get("title")

    return None, None


def extract_spreads(event, match):
    home = normalize_text(match["home_en"])
    away = normalize_text(match["away_en"])
    markets = []

    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market.get("key") != "spreads":
                continue

            home_row = None
            away_row = None
            for outcome in market.get("outcomes", []):
                name = normalize_text(outcome.get("name", ""))
                price = parse_price(outcome.get("price"))
                point = outcome.get("point")
                if price is None or point is None:
                    continue
                if home in name:
                    home_row = {"line": point, "odds": price}
                elif away in name:
                    away_row = {"line": point, "odds": price}

            if home_row and away_row:
                markets.append({
                    "line": home_row["line"],
                    "home_odds": home_row["odds"],
                    "away_odds": away_row["odds"],
                    "bookmaker": bookmaker.get("title"),
                })

    return markets


def extract_totals(event):
    markets = []

    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market.get("key") != "totals":
                continue

            over_row = None
            under_row = None
            for outcome in market.get("outcomes", []):
                name = normalize_text(outcome.get("name", ""))
                price = parse_price(outcome.get("price"))
                point = outcome.get("point")
                if price is None or point is None:
                    continue
                if name == "over":
                    over_row = {"line": point, "odds": price}
                elif name == "under":
                    under_row = {"line": point, "odds": price}

            if over_row and under_row:
                markets.append({
                    "line": over_row["line"],
                    "over_odds": over_row["odds"],
                    "under_odds": under_row["odds"],
                    "bookmaker": bookmaker.get("title"),
                })

    return markets


@st.cache_data(ttl=ODDS_DATA_TTL, show_spinner=False)
def fetch_odds(match):
    api_key = load_the_odds_api_key()
    if not api_key:
        return empty_result(
            "缺少 The Odds API Key。请在 .streamlit/secrets.toml 中保存 THE_ODDS_API_KEY。"
        )

    last_error = None
    for sport_key in WORLD_CUP_SPORT_KEYS:
        try:
            response = requests.get(
                f"{THE_ODDS_API_BASE}/sports/{sport_key}/odds",
                params={
                    "apiKey": api_key,
                    "regions": "us,uk,eu",
                    "markets": "h2h,spreads,totals",
                    "oddsFormat": "decimal",
                    "dateFormat": "iso",
                },
                timeout=20,
            )
            response.raise_for_status()
            events = response.json()
        except requests.RequestException as error:
            last_error = error
            continue

        for event in events:
            if not event_matches(event, match):
                continue

            prices, bookmaker = extract_h2h_prices(event, match)
            spreads = extract_spreads(event, match)
            totals = extract_totals(event)
            if not prices:
                return empty_result(
                    f"找到了 The Odds API 赛事，但没有完整 h2h 胜平负赔率：{event.get('id')}"
                )

            return {
                "found": True,
                "home_win": prices["home_win"],
                "draw": prices["draw"],
                "away_win": prices["away_win"],
                "over_under_line": totals[0].get("line") if totals else None,
                "asian_handicap": spreads,
                "over_under": totals,
                "raw_probabilities": raw_probabilities(
                    prices["home_win"], prices["draw"], prices["away_win"]
                ),
                "implied_probabilities": implied_probabilities(
                    prices["home_win"], prices["draw"], prices["away_win"]
                ),
                "source": f"The Odds API / {bookmaker or 'Bookmaker'}",
                "event_title": f"{event.get('home_team')} vs {event.get('away_team')}",
                "event_id": event.get("id"),
                "message": "已找到 The Odds API h2h 真实赔率。",
            }

    if last_error:
        return empty_result(f"无法连接 The Odds API 或读取赔率：{redact_secret(last_error)}")

    return empty_result("The Odds API 未找到对应世界杯 h2h 赔率市场。")
