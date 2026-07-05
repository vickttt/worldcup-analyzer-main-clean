from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from modules.api_client import request_json
from modules.venue_utils import venue_city_for

LOCAL_TZ = ZoneInfo("Asia/Shanghai")
LIVE_CACHE_TTL = 5 * 60
API_FOOTBALL_WORLD_CUP_LEAGUE_ID = 1
API_FOOTBALL_WORLD_CUP_SEASON = 2026


def parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        pass
    for fmt in ("%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=LOCAL_TZ)
        except ValueError:
            continue
    return None


def normalize_fixture(item, source):
    fixture = item.get("fixture", {}) or {}
    teams = item.get("teams", {}) or {}
    league = item.get("league", {}) or {}
    venue = fixture.get("venue", {}) or {}
    home = teams.get("home", {}) or {}
    away = teams.get("away", {}) or {}
    status = fixture.get("status", {}) or {}
    goals = item.get("goals", {}) or {}
    home_goals = goals.get("home")
    away_goals = goals.get("away")
    finished = status.get("short") in {"FT", "AET", "PEN"}
    score = None
    if home_goals is not None or away_goals is not None:
        score = {"home": home_goals, "away": away_goals}

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
        "league_name": f"{league.get('name') or 'World Cup'} {league.get('season') or 2026}",
        "round": league.get("round") or "",
        "venue_name": venue.get("name") or "",
        "venue_city": venue_city_for(venue.get("name"), venue.get("city")),
        "group": league.get("round") or "",
        "status": status.get("short") or "NS",
        "status_text": status.get("long") or "未开始",
        "score": score,
        "post_match": {
            "stats": {},
            "goals": [],
            "cards": [],
            "prematch_review": "待复盘",
            "odds_review": "赛后赔率复盘待补充。",
        } if finished else None,
        "source": source,
    }


def fetch_api_football_schedule():
    response = request_json(
        "/fixtures",
        {
            "league": API_FOOTBALL_WORLD_CUP_LEAGUE_ID,
            "season": API_FOOTBALL_WORLD_CUP_SEASON,
        },
    )
    fixtures = [normalize_fixture(item, "API-Football") for item in response]
    fixtures = [
        fixture for fixture in fixtures
        if fixture.get("fixture_id")
        and fixture.get("home_team", {}).get("name")
        and fixture.get("away_team", {}).get("name")
    ]
    return sorted(fixtures, key=lambda item: item.get("kickoff_utc") or "")


@st.cache_data(ttl=LIVE_CACHE_TTL, show_spinner=False)
def fetch_world_cup_schedule(force_refresh=False):
    updated_at = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M CST")
    try:
        fixtures = fetch_api_football_schedule()
        return {
            "fixtures": fixtures,
            "source": "API-Football",
            "updated_at": updated_at,
            "fetched_at": datetime.now(LOCAL_TZ).isoformat(),
            "cache_status": "实时数据",
            "api_calls": 1,
            "message": "赛程、赛果和 fixture_id 仅来自 API-Football；未启用旧赛程或本地备用源。",
        }
    except (RuntimeError, ValueError, KeyError) as error:
        return {
            "fixtures": [],
            "source": "API-Football",
            "updated_at": updated_at,
            "fetched_at": datetime.now(LOCAL_TZ).isoformat(),
            "cache_status": "API-Football unavailable",
            "api_calls": 1,
            "message": f"API-Football 暂不可用，已按单一来源策略停止加载旧赛程和本地备用源：{error}",
            "error": str(error),
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


def available_match_dates(fixtures):
    return list(group_by_match_date(fixtures).keys())


def fixtures_for_date(fixtures, date_key):
    return group_by_match_date(fixtures).get(date_key, [])


def default_date_key(fixtures):
    today_key = datetime.now(LOCAL_TZ).strftime("%m-%d")
    dates = available_match_dates(fixtures)
    if today_key in dates:
        return today_key
    future_dates = []
    for key in dates:
        try:
            parsed = datetime.strptime(f"2026-{key}", "%Y-%m-%d").date()
        except ValueError:
            continue
        if parsed >= datetime.now(LOCAL_TZ).date():
            future_dates.append(key)
    return future_dates[0] if future_dates else dates[0] if dates else today_key


def is_finished(fixture):
    return fixture.get("status") in {"FT", "AET", "PEN"} or fixture.get("status_text") == "已结束"


def is_live(fixture):
    status = str(fixture.get("status") or "").upper()
    text = str(fixture.get("status_text") or "")
    return status in {"LIVE", "IN", "STATUS_IN_PROGRESS"} or "进行中" in text


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
