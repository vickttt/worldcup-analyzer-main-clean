import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import streamlit as st

LOCAL_TZ = ZoneInfo("Asia/Shanghai")

BASE_DIR = Path(__file__).resolve().parent.parent
RUNTIME_CONFIG_PATH = BASE_DIR / "config" / "runtime.json"


def load_runtime_config():
    return json.loads(RUNTIME_CONFIG_PATH.read_text(encoding="utf-8"))


WORLDCUP2026_BASE = load_runtime_config()["api_base_url"].rstrip("/") + "/"
ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
ESPN_STANDINGS_URL = "https://site.web.api.espn.com/apis/v2/sports/soccer/fifa.world/standings"
LIVE_CACHE_TTL = 5 * 60
FUTURE_CACHE_TTL = 12 * 60 * 60
FINISHED_CACHE_TTL = 24 * 60 * 60


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


def official_schedule_path():
    return Path(__file__).resolve().parents[1] / "data" / "worldcup_2026_schedule.json"


def cache_dir():
    path = Path(__file__).resolve().parents[1] / "data" / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def schedule_cache_path():
    return cache_dir() / "worldcup_schedule_cache.json"


def schedule_fallback_path():
    return Path(__file__).resolve().parents[1] / "data" / "world_cup_schedule_fallback.json"


def load_json(path):
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_official_schedule():
    payload = load_json(official_schedule_path())
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, list):
        return {"fixtures": payload, "standings": {}}
    return {"fixtures": [], "standings": {}}


def read_local_cache():
    payload = load_json(schedule_cache_path())
    if isinstance(payload, dict) and payload.get("fixtures"):
        return payload
    return None


def write_local_cache(payload):
    cache_path = schedule_cache_path()
    with cache_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def cache_age_seconds(payload):
    fetched_at = parse_datetime(payload.get("fetched_at"))
    if not fetched_at:
        return None
    return (datetime.now(LOCAL_TZ) - fetched_at.astimezone(LOCAL_TZ)).total_seconds()


def cache_ttl_for_payload(payload):
    fixtures = payload.get("fixtures") or []
    if any(is_live(fixture) for fixture in fixtures):
        return LIVE_CACHE_TTL
    if any(not is_finished(fixture) for fixture in fixtures):
        return FUTURE_CACHE_TTL
    return FINISHED_CACHE_TTL


def fresh_cached_payload(force_refresh=False):
    if force_refresh:
        return None
    payload = read_local_cache()
    if not payload:
        return None
    if payload.get("source") != "WorldCup2026 API":
        return None
    age = cache_age_seconds(payload)
    if age is None:
        return None
    ttl = cache_ttl_for_payload(payload)
    if age <= ttl:
        hours = age / 3600
        computed_standings = compute_standings_from_fixtures(payload.get("fixtures") or [])
        if computed_standings:
            payload["standings"] = computed_standings
        payload["cache_status"] = "实时数据" if age < 300 else f"缓存数据（{hours:.1f}小时前）"
        payload["api_calls"] = 0
        return payload
    return None


def load_fallback_schedule():
    payload = load_json(schedule_fallback_path())
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return payload.get("fixtures", [])
    return []


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_worldcup_scorers(value):
    if not value or value == "null":
        return []
    return [item.strip(" {}\"") for item in str(value).split(",") if item.strip(" {}\"")]


def worldcup_request(path):
    response = requests.get(f"{WORLDCUP2026_BASE}{path.lstrip('/')}", timeout=6)
    response.raise_for_status()
    return response.json()


def worldcup_lookup(items, key="id"):
    return {str(item.get(key)): item for item in items}


def worldcup_fixture(game, teams, stadiums):
    home = teams.get(str(game.get("home_team_id")), {})
    away = teams.get(str(game.get("away_team_id")), {})
    stadium = stadiums.get(str(game.get("stadium_id")), {})
    finished = str(game.get("finished", "")).upper() == "TRUE"
    elapsed = str(game.get("time_elapsed") or "").lower()
    live = elapsed not in {"notstarted", "finished", "fulltime"} and not finished
    home_score = to_int(game.get("home_score"))
    away_score = to_int(game.get("away_score"))
    status = "FT" if finished else "LIVE" if live else "NS"
    status_text = "已结束" if finished else "进行中" if live else "未开始"

    return {
        "fixture_id": game.get("id"),
        "home_team": {
            "id": home.get("id") or game.get("home_team_id"),
            "name": home.get("name_en") or game.get("home_team_name_en") or game.get("home_team_label"),
            "logo": home.get("flag"),
        },
        "away_team": {
            "id": away.get("id") or game.get("away_team_id"),
            "name": away.get("name_en") or game.get("away_team_name_en") or game.get("away_team_label"),
            "logo": away.get("flag"),
        },
        "kickoff_utc": game.get("local_date"),
        "kickoff_display": game.get("local_date"),
        "league_name": "World Cup 2026",
        "round": game.get("type") or "group",
        "group": game.get("group") or "",
        "venue_name": stadium.get("fifa_name") or stadium.get("name_en") or "",
        "venue_city": ", ".join(
            item for item in [stadium.get("city_en"), stadium.get("country_en")] if item
        ),
        "status": status,
        "status_text": status_text,
        "score": {"home": home_score, "away": away_score} if finished or live else None,
        "market_heat": None,
        "post_match": {
            "stats": {},
            "goals": [
                {"球队": home.get("name_en") or game.get("home_team_name_en"), "球员": scorer}
                for scorer in parse_worldcup_scorers(game.get("home_scorers"))
            ] + [
                {"球队": away.get("name_en") or game.get("away_team_name_en"), "球员": scorer}
                for scorer in parse_worldcup_scorers(game.get("away_scorers"))
            ],
            "cards": [],
            "prematch_review": "待复盘",
            "odds_review": "赛后赔率复盘待补充。",
        } if finished else None,
        "source": "WorldCup2026 API",
    }


def group_stage_name(fixture):
    group = fixture.get("group") or ""
    round_name = str(fixture.get("round") or "").lower()
    if group:
        return f"Group {group}"
    if "group" in round_name:
        return "Group Stage"
    return None


def init_standing_row(team_name):
    return {
        "team": team_name,
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "gf": 0,
        "ga": 0,
        "gd": 0,
        "points": 0,
    }


def apply_result(row, goals_for, goals_against):
    row["played"] += 1
    row["gf"] += goals_for
    row["ga"] += goals_against
    row["gd"] = row["gf"] - row["ga"]
    if goals_for > goals_against:
        row["wins"] += 1
        row["points"] += 3
    elif goals_for == goals_against:
        row["draws"] += 1
        row["points"] += 1
    else:
        row["losses"] += 1


def sort_standing_rows(rows):
    return sorted(
        rows,
        key=lambda row: (
            -to_int(row.get("points")),
            -to_int(row.get("gd")),
            -to_int(row.get("gf")),
            str(row.get("team") or ""),
        ),
    )


def compute_standings_from_fixtures(fixtures):
    standings = {}
    for fixture in fixtures:
        score = fixture.get("score") or {}
        if not is_finished(fixture) or score.get("home") is None or score.get("away") is None:
            continue
        group_name = group_stage_name(fixture)
        if not group_name:
            continue

        home = (fixture.get("home_team") or {}).get("name")
        away = (fixture.get("away_team") or {}).get("name")
        if not home or not away:
            continue

        group_rows = standings.setdefault(group_name, {})
        group_rows.setdefault(home, init_standing_row(home))
        group_rows.setdefault(away, init_standing_row(away))

        home_score = to_int(score.get("home"))
        away_score = to_int(score.get("away"))
        apply_result(group_rows[home], home_score, away_score)
        apply_result(group_rows[away], away_score, home_score)

    return {
        group: sort_standing_rows(list(rows.values()))
        for group, rows in standings.items()
        if rows
    }


def fetch_worldcup2026_data():
    games_payload = worldcup_request("games")
    groups_payload = worldcup_request("groups")
    teams_payload = worldcup_request("teams")
    stadiums_payload = worldcup_request("stadiums")

    teams = worldcup_lookup(teams_payload.get("teams") or [])
    stadiums = worldcup_lookup(stadiums_payload.get("stadiums") or [])
    fixtures = [
        worldcup_fixture(game, teams, stadiums)
        for game in games_payload.get("games") or []
    ]
    fixtures = [
        fixture for fixture in fixtures
        if fixture.get("home_team", {}).get("name") and fixture.get("away_team", {}).get("name")
    ]

    standings = compute_standings_from_fixtures(fixtures)
    fallback_standings = {}
    for group in groups_payload.get("groups") or []:
        rows = []
        for entry in group.get("teams") or []:
            team = teams.get(str(entry.get("team_id")), {})
            rows.append({
                "team": team.get("name_en") or entry.get("team_id"),
                "played": to_int(entry.get("mp")),
                "wins": to_int(entry.get("w")),
                "draws": to_int(entry.get("d")),
                "losses": to_int(entry.get("l")),
                "gf": to_int(entry.get("gf")),
                "ga": to_int(entry.get("ga")),
                "gd": to_int(entry.get("gd")),
                "points": to_int(entry.get("pts")),
            })
        fallback_standings[f"Group {group.get('name')}"] = sort_standing_rows(rows)
    if not standings:
        standings = fallback_standings

    now_text = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M CST")
    return {
        "fixtures": sorted(fixtures, key=lambda item: item.get("kickoff_utc") or ""),
        "standings": standings,
        "source": "WorldCup2026 API",
        "updated_at": now_text,
        "fetched_at": datetime.now(LOCAL_TZ).isoformat(),
        "cache_status": "实时数据",
        "api_calls": 4,
    }


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
        "league_name": f"{league.get('name') or 'World Cup'} {league.get('season') or 2026}",
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


def espn_competitor(competition, home_away):
    competitors = competition.get("competitors") or []
    for competitor in competitors:
        if competitor.get("homeAway") == home_away:
            team = competitor.get("team") or {}
            return competitor, team
    return {}, {}


def espn_score(competitor):
    value = competitor.get("score")
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def espn_fixture(event):
    competition = (event.get("competitions") or [{}])[0]
    venue = competition.get("venue") or {}
    status = event.get("status", {}).get("type", {}) or {}
    home_competitor, home_team = espn_competitor(competition, "home")
    away_competitor, away_team = espn_competitor(competition, "away")
    completed = bool(status.get("completed"))
    score = None
    if completed:
        score = {
            "home": espn_score(home_competitor),
            "away": espn_score(away_competitor),
        }

    return {
        "fixture_id": event.get("id"),
        "home_team": {
            "id": home_team.get("id"),
            "name": home_team.get("displayName") or home_team.get("name"),
            "logo": (home_team.get("logos") or [{}])[0].get("href"),
        },
        "away_team": {
            "id": away_team.get("id"),
            "name": away_team.get("displayName") or away_team.get("name"),
            "logo": (away_team.get("logos") or [{}])[0].get("href"),
        },
        "kickoff_utc": event.get("date"),
        "league_name": "World Cup 2026",
        "round": (event.get("season") or {}).get("slug") or "World Cup",
        "group": "",
        "venue_name": venue.get("fullName") or venue.get("name") or "",
        "venue_city": ", ".join(
            item for item in [
                (venue.get("address") or {}).get("city"),
                (venue.get("address") or {}).get("country"),
            ] if item
        ),
        "status": status.get("name") or status.get("state") or "NS",
        "status_text": "已结束" if completed else status.get("description") or "未开始",
        "score": score,
        "market_heat": None,
        "post_match": None,
        "source": "ESPN",
    }


def fetch_espn_scoreboard():
    today = datetime.now(LOCAL_TZ).date()
    dates = [
        (today + timedelta(days=offset)).strftime("%Y%m%d")
        for offset in range(-2, 8)
    ]
    fixtures = []
    latest_update = None
    for date_value in dates:
        response = requests.get(ESPN_SCOREBOARD_URL, params={"dates": date_value}, timeout=6)
        response.raise_for_status()
        payload = response.json()
        latest_update = payload.get("timestamp") or latest_update
        for event in payload.get("events") or []:
            fixture = espn_fixture(event)
            if fixture.get("home_team", {}).get("name") and fixture.get("away_team", {}).get("name"):
                fixtures.append(fixture)
    unique = {}
    for fixture in fixtures:
        unique[fixture.get("fixture_id") or f"{fixture.get('kickoff_utc')}-{fixture['home_team']['name']}"] = fixture
    return list(unique.values()), latest_update


def fetch_espn_standings():
    try:
        response = requests.get(ESPN_STANDINGS_URL, timeout=6)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return {}
    standings = {}
    for group in payload.get("children") or []:
        name = group.get("name") or group.get("abbreviation") or "Group"
        rows = []
        for entry in ((group.get("standings") or {}).get("entries") or []):
            team = (entry.get("team") or {}).get("displayName")
            stats = {stat.get("name"): stat.get("value") for stat in entry.get("stats") or []}
            if team:
                rows.append({
                    "team": team,
                    "played": int(stats.get("gamesPlayed", 0) or 0),
                    "wins": int(stats.get("wins", 0) or 0),
                    "draws": int(stats.get("ties", 0) or 0),
                    "losses": int(stats.get("losses", 0) or 0),
                    "gf": int(stats.get("pointsFor", 0) or stats.get("goalsFor", 0) or 0),
                    "ga": int(stats.get("pointsAgainst", 0) or stats.get("goalsAgainst", 0) or 0),
                    "gd": int(stats.get("pointDifferential", 0) or 0),
                    "points": int(stats.get("points", 0) or 0),
                })
        if rows:
            standings[name] = rows
    return standings


@st.cache_data(ttl=LIVE_CACHE_TTL, show_spinner=False)
def fetch_world_cup_schedule(force_refresh=False):
    updated_at = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M CST")
    cached = fresh_cached_payload(force_refresh=force_refresh)
    if cached:
        return {
            **cached,
            "message": f"读取项目缓存：{cached.get('source')}。",
        }

    try:
        payload = fetch_worldcup2026_data()
        write_local_cache(payload)
        return {
            **payload,
            "message": "赛程、赛果、实时比分与积分榜来自 WorldCup2026 API。",
        }
    except (requests.RequestException, ValueError, KeyError) as error:
        worldcup_error = error

    try:
        fixtures, espn_updated_at = fetch_espn_scoreboard()
        if fixtures:
            standings = fetch_espn_standings()
            payload = {
                "fixtures": sorted(fixtures, key=lambda item: item.get("kickoff_utc") or ""),
                "standings": standings,
                "source": "ESPN",
                "updated_at": espn_updated_at or updated_at,
                "fetched_at": datetime.now(LOCAL_TZ).isoformat(),
                "cache_status": "实时数据",
                "api_calls": 1,
            }
            write_local_cache(payload)
            return {
                **payload,
                "message": f"WorldCup2026 API 暂不可用，已切换 ESPN：{worldcup_error}",
            }
    except (requests.RequestException, ValueError, KeyError) as error:
        cached = read_local_cache()
        if cached:
            return {
                **cached,
                "source": cached.get("source", "Local cache"),
                "cache_status": cached.get("cache_status") or "缓存数据",
                "message": f"WorldCup2026 与 ESPN 暂不可用，已读取项目缓存：{error}",
                "api_calls": 0,
            }

    payload = load_official_schedule()
    fixtures = payload.get("fixtures", [])
    if fixtures:
        return {
            "fixtures": sorted(fixtures, key=lambda item: item.get("kickoff_utc") or ""),
            "standings": payload.get("standings", {}),
            "source": "Local static fallback",
            "updated_at": updated_at,
            "cache_status": "本地备用数据",
            "message": "WorldCup2026、ESPN 和项目缓存均不可用，当前使用本地备用数据。",
            "api_calls": 0,
        }

    fallback = load_fallback_schedule()
    return {
        "fixtures": fallback,
        "standings": {},
        "source": "Local fallback schedule",
        "updated_at": updated_at,
        "cache_status": "本地备用数据",
        "message": "本地官方赛程库为空，已使用旧版本地赛程缓存。",
        "api_calls": 0,
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


def default_standings():
    payload = load_official_schedule()
    if payload.get("standings"):
        return payload["standings"]
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
