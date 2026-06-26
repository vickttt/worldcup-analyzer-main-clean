import json
import os
import re
import tomllib
import unicodedata
from datetime import datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import streamlit as st

from modules.cache_config import ODDS_DATA_TTL
from modules.team_resolver import alias_candidates


THE_ODDS_API_BASE = "https://api.the-odds-api.com/v4"
LOCAL_TZ = ZoneInfo("Asia/Shanghai")
WORLD_CUP_SPORT_KEYS = [
    "soccer_fifa_world_cup",
    "soccer_international_friendlies",
]

TEAM_ODDS_ALIASES = {
    "democratic republic of the congo": ["democratic republic of the congo", "democratic republic of congo", "dr congo", "congo dr", "congo kinshasa"],
    "democratic republic of congo": ["democratic republic of congo", "democratic republic of the congo", "dr congo", "congo dr"],
    "congo dr": ["congo dr", "dr congo", "democratic republic of the congo", "democratic republic of congo"],
    "dr congo": ["dr congo", "congo dr", "democratic republic of the congo", "democratic republic of congo"],
    "czech republic": ["czech republic", "czechia"],
    "czechia": ["czechia", "czech republic"],
    "curacao": ["curacao", "curaçao"],
    "curaçao": ["curaçao", "curacao"],
    "ivory coast": ["ivory coast", "cote d ivoire", "côte d ivoire"],
    "south korea": ["south korea", "korea republic", "republic of korea"],
    "united states": ["united states", "usa", "usmnt"],
    "bosnia and herzegovina": ["bosnia and herzegovina", "bosnia & herzegovina", "bosnia herzegovina", "bosnia-herzegovina", "bosnia"],
    "bosnia herzegovina": ["bosnia herzegovina", "bosnia and herzegovina", "bosnia & herzegovina", "bosnia-herzegovina", "bosnia"],
    "bosnia": ["bosnia", "bosnia and herzegovina", "bosnia & herzegovina", "bosnia herzegovina", "bosnia-herzegovina"],
    "iran": ["iran", "ir iran"],
    "ir iran": ["ir iran", "iran"],
}


def normalize_text(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_text.lower().replace(".", " ").replace("-", " ").split())


def name_candidates(value):
    normalized = normalize_text(value)
    candidates = {normalized}
    for alias in alias_candidates(value):
        candidates.add(normalize_text(alias))
    for alias in TEAM_ODDS_ALIASES.get(normalized, []):
        candidates.add(normalize_text(alias))
    return {candidate for candidate in candidates if candidate}


def candidate_matches(candidates, text):
    normalized = normalize_text(text)
    return any(candidate == normalized or candidate in normalized or normalized in candidate for candidate in candidates)


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


def cache_dir():
    path = Path(__file__).resolve().parents[1] / "data" / "cache" / "odds_api"
    path.mkdir(parents=True, exist_ok=True)
    return path


def daily_cache_path(sport_key, date_key):
    safe_key = sport_key.replace("/", "_")
    return cache_dir() / f"{safe_key}_{date_key}_utc_h2h_totals.json"


def now_local():
    return datetime.now(LOCAL_TZ)


def parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def cache_is_fresh(payload):
    fetched_at = parse_datetime(payload.get("fetched_at"))
    if not fetched_at:
        return False
    return (now_local() - fetched_at.astimezone(LOCAL_TZ)).total_seconds() <= ODDS_DATA_TTL


def read_daily_cache(sport_key, date_key):
    path = daily_cache_path(sport_key, date_key)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if cache_is_fresh(payload):
        return payload
    return None


def write_daily_cache(sport_key, date_key, payload):
    path = daily_cache_path(sport_key, date_key)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def daily_utc_window(date_key=None):
    local_date = datetime.strptime(date_key, "%Y-%m-%d").date() if date_key else now_local().date()
    start_local = datetime.combine(local_date, time.min, tzinfo=timezone.utc)
    end_local = datetime.combine(local_date, time.max, tzinfo=timezone.utc)
    return (
        start_local.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        end_local.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    )


def cache_metadata(source, sport_key=None, date_key=None, events=None):
    return {
        "source": source,
        "sport_key": sport_key,
        "date_key": date_key,
        "events_count": len(events or []),
    }


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
        "cache": None,
    }


def redact_secret(value):
    return re.sub(r"apiKey=[^&\\s)]+", "apiKey=***", str(value))


def format_request_error(error):
    response = getattr(error, "response", None)
    if response is None:
        return redact_secret(error)

    try:
        payload = response.json()
    except ValueError:
        payload = {}

    error_code = payload.get("error_code")
    message = payload.get("message") or str(error)
    remaining = response.headers.get("x-requests-remaining")
    used = response.headers.get("x-requests-used")

    if error_code == "OUT_OF_USAGE_CREDITS":
        return f"The Odds API 额度已用完：{message}（remaining={remaining}, used={used}）"

    return redact_secret(f"{response.status_code} {message}")


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
    home_candidates = name_candidates(match["home_en"])
    away_candidates = name_candidates(match["away_en"])
    event_home = normalize_text(event.get("home_team", ""))
    event_away = normalize_text(event.get("away_team", ""))
    title = normalize_text(" ".join([event_home, event_away]))

    direct = candidate_matches(home_candidates, event_home) and candidate_matches(away_candidates, event_away)
    reversed_match = candidate_matches(home_candidates, event_away) and candidate_matches(away_candidates, event_home)
    fuzzy = candidate_matches(home_candidates, title) and candidate_matches(away_candidates, title)
    return direct or reversed_match or fuzzy


def extract_h2h_prices(event, match):
    home_candidates = name_candidates(match["home_en"])
    away_candidates = name_candidates(match["away_en"])

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
                elif candidate_matches(home_candidates, name):
                    prices["home_win"] = price
                elif candidate_matches(away_candidates, name):
                    prices["away_win"] = price

            if all(prices.get(key) for key in ["home_win", "draw", "away_win"]):
                return prices, bookmaker.get("title")

    return None, None


def extract_spreads(event, match):
    home_candidates = name_candidates(match["home_en"])
    away_candidates = name_candidates(match["away_en"])
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
                if candidate_matches(home_candidates, name):
                    home_row = {"line": point, "odds": price}
                elif candidate_matches(away_candidates, name):
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
def fetch_daily_events(sport_key, date_key):
    api_key = load_the_odds_api_key()
    if not api_key:
        raise RuntimeError("缺少 The Odds API Key。请在 .streamlit/secrets.toml 中保存 THE_ODDS_API_KEY。")

    cached = read_daily_cache(sport_key, date_key)
    if cached:
        return cached

    start_utc, end_utc = daily_utc_window(date_key)
    response = requests.get(
        f"{THE_ODDS_API_BASE}/sports/{sport_key}/odds",
        params={
            "apiKey": api_key,
            "regions": "eu",
            "markets": "h2h,totals",
            "oddsFormat": "decimal",
            "dateFormat": "iso",
            "commenceTimeFrom": start_utc,
            "commenceTimeTo": end_utc,
        },
        timeout=6,
    )
    if response.status_code == 404:
        return {
            "source": "The Odds API",
            "sport_key": sport_key,
            "date_key": date_key,
            "fetched_at": now_local().isoformat(),
            "cache_status": "sport key unavailable",
            "events": [],
            "request_headers": {},
        }
    response.raise_for_status()
    events = response.json()
    payload = {
        "source": "The Odds API",
        "sport_key": sport_key,
        "date_key": date_key,
        "fetched_at": now_local().isoformat(),
        "cache_status": "fresh api response",
        "events": events,
        "request_headers": {
            "x-requests-used": response.headers.get("x-requests-used"),
            "x-requests-remaining": response.headers.get("x-requests-remaining"),
            "x-requests-last": response.headers.get("x-requests-last"),
        },
    }
    write_daily_cache(sport_key, date_key, payload)
    return payload


@st.cache_data(ttl=ODDS_DATA_TTL, show_spinner=False)
def fetch_odds(match, date_key=None, data_flow_version="odds_page_v4_24h_cache"):
    date_key = date_key or now_local().strftime("%Y-%m-%d")
    last_error = None
    for sport_key in WORLD_CUP_SPORT_KEYS:
        try:
            payload = fetch_daily_events(sport_key, date_key)
            events = payload.get("events") or []
        except requests.RequestException as error:
            last_error = error
            continue
        except RuntimeError as error:
            return empty_result(str(error))

        for event in events:
            if not event_matches(event, match):
                continue

            prices, bookmaker = extract_h2h_prices(event, match)
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
                "asian_handicap": [],
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
                "cache": cache_metadata(payload.get("cache_status"), sport_key, date_key, events),
            }

    if last_error:
        return empty_result(f"无法连接 The Odds API 或读取赔率：{format_request_error(last_error)}")

    return empty_result("未找到盘口数据：The Odds API 当前没有返回该比赛的胜平负或大小球市场。")
