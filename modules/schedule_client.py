import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import streamlit as st

from modules.cache_config import SCHEDULE_DATA_TTL
from modules.odds_client import request_json


LOCAL_TZ = ZoneInfo("Asia/Shanghai")
WORLD_CUP_LEAGUE_ID = 1
WORLD_CUP_SEASON = 2026


def parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def schedule_fallback_path():
    return Path(__file__).resolve().parents[1] / "data" / "world_cup_schedule_fallback.json"


def load_fallback_schedule():
    path = schedule_fallback_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_fixture(item, source):
    fixture = item.get("fixture", {}) or {}
    teams = item.get("teams", {}) or {}
    league = item.get("league", {}) or {}
    venue = fixture.get("venue", {}) or {}
    home = teams.get("home", {}) or {}
    away = teams.get("away", {}) or {}

    return {
        "fixture_id": fixture.get("id"),
        "home_team": {
            "id": home.get("id"),
            "name": home.get("name"),
            "logo": home.get("logo"),
        },
        "away_team": {
            "id": away.get("id"),
            "name": away.get("name"),
            "logo": away.get("logo"),
        },
        "kickoff_utc": fixture.get("date"),
        "league_name": f"{league.get('name') or 'World Cup'} {league.get('season') or WORLD_CUP_SEASON}",
        "round": league.get("round") or "",
        "venue_name": venue.get("name") or "",
        "venue_city": venue.get("city") or "",
        "group": league.get("round") or "",
        "status": (fixture.get("status", {}) or {}).get("short") or "NS",
        "status_text": (fixture.get("status", {}) or {}).get("long") or "未开始",
        "score": None,
        "post_match": None,
        "source": source,
    }


@st.cache_data(ttl=SCHEDULE_DATA_TTL, show_spinner=False)
def fetch_world_cup_schedule():
    try:
        response = request_json(
            "/fixtures",
            {
                "league": WORLD_CUP_LEAGUE_ID,
                "season": WORLD_CUP_SEASON,
            },
        )
        fixtures = [normalize_fixture(item, "API-Football") for item in response]
        fixtures = [item for item in fixtures if item.get("home_team", {}).get("name") and item.get("away_team", {}).get("name")]
        if fixtures:
            return {
                "fixtures": sorted(fixtures, key=lambda item: item.get("kickoff_utc") or ""),
                "source": "API-Football",
                "message": "世界杯赛程来自 API-Football，24小时缓存。",
                "api_calls": 1,
            }
    except (requests.RequestException, RuntimeError) as error:
        fallback = load_fallback_schedule()
        return {
            "fixtures": fallback,
            "source": "Local fallback schedule",
            "message": f"API-Football 赛程暂不可用，已使用本地赛程缓存：{error}",
            "api_calls": 1,
        }

    fallback = load_fallback_schedule()
    return {
        "fixtures": fallback,
        "source": "Local fallback schedule",
        "message": "API-Football 未返回赛程，已使用本地赛程缓存。",
        "api_calls": 1,
    }


def fixture_local_datetime(item):
    parsed = parse_datetime(item.get("kickoff_utc"))
    if not parsed:
        return None
    return parsed.astimezone(LOCAL_TZ)


def schedule_groups(fixtures, today=None):
    base_date = today or datetime.now(LOCAL_TZ).date()
    tomorrow = base_date + timedelta(days=1)
    seven_days_later = base_date + timedelta(days=7)

    groups = {
        "today": [],
        "tomorrow": [],
        "next_7_days": [],
    }

    for fixture in fixtures:
        local_time = fixture_local_datetime(fixture)
        if not local_time:
            continue
        match_date = local_time.date()
        if match_date == base_date:
            groups["today"].append(fixture)
        if match_date == tomorrow:
            groups["tomorrow"].append(fixture)
        if base_date <= match_date <= seven_days_later:
            groups["next_7_days"].append(fixture)

    for key in groups:
        groups[key].sort(key=lambda item: item.get("kickoff_utc") or "")
    return groups


def group_by_match_date(fixtures):
    grouped = {}
    for fixture in fixtures:
        local_time = fixture_local_datetime(fixture)
        if not local_time:
            continue
        key = local_time.strftime("%m-%d")
        grouped.setdefault(key, []).append(fixture)

    for key in grouped:
        grouped[key].sort(key=lambda item: item.get("kickoff_utc") or "")
    return dict(sorted(grouped.items()))


def is_finished(fixture):
    return fixture.get("status") in {"FT", "AET", "PEN"} or fixture.get("status_text") == "已结束"


def tournament_stats(fixtures):
    finished = [fixture for fixture in fixtures if is_finished(fixture)]
    total_goals = 0
    biggest = "-"
    biggest_margin = -1

    for fixture in finished:
        score = fixture.get("score") or {}
        home_goals = score.get("home")
        away_goals = score.get("away")
        if home_goals is None or away_goals is None:
            continue
        total_goals += home_goals + away_goals
        margin = abs(home_goals - away_goals)
        if margin > biggest_margin:
            biggest_margin = margin
            biggest = (
                f"{fixture.get('home_team', {}).get('name')} "
                f"{home_goals}:{away_goals} "
                f"{fixture.get('away_team', {}).get('name')}"
            )

    return {
        "finished_matches": len(finished),
        "total_goals": total_goals,
        "avg_goals": total_goals / len(finished) if finished else 0,
        "upsets": 0,
        "biggest_score": biggest,
    }


def default_standings():
    return {
        "A组": [
            {"team": "Argentina", "played": 0, "wins": 0, "draws": 0, "losses": 0, "gd": 0, "points": 0},
            {"team": "Algeria", "played": 0, "wins": 0, "draws": 0, "losses": 0, "gd": 0, "points": 0},
            {"team": "Austria", "played": 0, "wins": 0, "draws": 0, "losses": 0, "gd": 0, "points": 0},
            {"team": "Jordan", "played": 0, "wins": 0, "draws": 0, "losses": 0, "gd": 0, "points": 0},
        ],
        "B组": [
            {"team": "France", "played": 0, "wins": 0, "draws": 0, "losses": 0, "gd": 0, "points": 0},
            {"team": "England", "played": 0, "wins": 0, "draws": 0, "losses": 0, "gd": 0, "points": 0},
        ],
        "C组": [
            {"team": "Germany", "played": 0, "wins": 0, "draws": 0, "losses": 0, "gd": 0, "points": 0},
            {"team": "Spain", "played": 0, "wins": 0, "draws": 0, "losses": 0, "gd": 0, "points": 0},
        ],
    }
