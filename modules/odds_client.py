import json
import os
import tomllib
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st

from modules.cache_config import (
    API_FOOTBALL_MARKET_DATA_TTL,
    CORRECT_SCORE_DATA_TTL,
    MATCH_DATA_TTL,
    ODDS_DATA_TTL,
    SCHEDULE_DATA_TTL,
    TEAM_DATA_TTL,
)
from modules.team_resolver import normalize_text, resolve_team as search_team


API_FOOTBALL_BASE = "https://v3.football.api-sports.io"
API_REQUEST_TIMEOUT = 6
EXACT_SCORE_BET_ID = 10
ASIAN_HANDICAP_BET_ID = 4
PREFERRED_CORRECT_SCORE_BOOKMAKERS = {
    4: "Pinnacle",
    8: "Bet365",
    13: "188Bet",
}
FIXTURE_CACHE_TTL = 24 * 60 * 60


def load_api_key():
    env_key = os.getenv("API_FOOTBALL_KEY")
    if env_key:
        return env_key.strip()

    secrets_path = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        with secrets_path.open("rb") as file:
            secrets = tomllib.load(file)
        for key in ["API_FOOTBALL_KEY", "api_football_key"]:
            if secrets.get(key):
                return str(secrets[key]).strip()

    return None


def empty_result(reason, fixture=None):
    return {
        "found": False,
        "home_win": None,
        "draw": None,
        "away_win": None,
        "over_under_line": None,
        "raw_probabilities": None,
        "implied_probabilities": None,
        "source": "API-Football 免费版",
        "event_title": fixture.get("name") if fixture else None,
        "event_id": fixture.get("id") if fixture else None,
        "message": reason,
    }


def implied_probabilities(home_win, draw, away_win):
    raw = {
        "home_win": 1 / home_win,
        "draw": 1 / draw,
        "away_win": 1 / away_win,
    }
    total = sum(raw.values())
    return {key: value / total for key, value in raw.items()}


def raw_probabilities(home_win, draw, away_win):
    return {
        "home_win": 1 / home_win,
        "draw": 1 / draw,
        "away_win": 1 / away_win,
    }


def request_json(path, params=None):
    api_key = load_api_key()
    if not api_key:
        raise RuntimeError(
            "缺少 API-Football Key。请在 .streamlit/secrets.toml 中保存 API_FOOTBALL_KEY。"
        )

    response = requests.get(
        f"{API_FOOTBALL_BASE}{path}",
        params=params or {},
        timeout=API_REQUEST_TIMEOUT,
        headers={
            "x-apisports-key": api_key,
            "Accept": "application/json",
        },
    )
    response.raise_for_status()
    data = response.json()

    errors = data.get("errors")
    if isinstance(errors, dict) and errors:
        raise RuntimeError("; ".join(str(value) for value in errors.values()))
    if isinstance(errors, list) and errors:
        raise RuntimeError("; ".join(str(value) for value in errors))

    return data.get("response", [])


def cache_dir():
    path = Path(__file__).resolve().parents[1] / "data" / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def fixture_cache_path():
    return cache_dir() / "fixture_cache.json"


def api_football_market_cache_path(fixture_id, bet_id):
    return cache_dir() / f"api_football_market_{fixture_id}_{bet_id}.json"


def api_football_standings_cache_path(league_id, season):
    return cache_dir() / f"api_football_standings_{league_id}_{season}.json"


def read_fixture_cache_payload():
    path = fixture_cache_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_fixture_cache_payload(payload):
    with fixture_cache_path().open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def read_api_football_market_cache(fixture_id, bet_id, ttl):
    path = api_football_market_cache_path(fixture_id, bet_id)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    fetched_at = parse_cache_datetime(payload.get("fetched_at"))
    if not fetched_at:
        return None
    age = (datetime.now() - fetched_at).total_seconds()
    if age <= ttl:
        result = payload.get("result")
        if isinstance(result, dict):
            result["cache"] = {
                "status": "file_cache",
                "age_hours": round(age / 3600, 2),
                "path": path.name,
            }
            return result
    return None


def read_stale_api_football_market_cache(fixture_id, bet_id):
    path = api_football_market_cache_path(fixture_id, bet_id)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    result = payload.get("result")
    if isinstance(result, dict):
        result["cache"] = {
            "status": "stale_file_cache",
            "path": path.name,
        }
        return result
    return None


def write_api_football_market_cache(fixture_id, bet_id, result):
    if not result or not result.get("found"):
        return
    payload = {
        "fixture_id": fixture_id,
        "bet_id": bet_id,
        "fetched_at": datetime.now().isoformat(),
        "result": result,
    }
    with api_football_market_cache_path(fixture_id, bet_id).open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def flatten_standings_response(response):
    groups = []
    rows = []
    for competition in response or []:
        league = competition.get("league") or {}
        for group_rows in league.get("standings") or []:
            normalized_group = []
            for row in group_rows or []:
                all_stats = row.get("all") or {}
                goals = all_stats.get("goals") or {}
                normalized = {
                    "rank": row.get("rank"),
                    "group": row.get("group"),
                    "team": row.get("team") or {},
                    "points": row.get("points"),
                    "goals_diff": row.get("goalsDiff"),
                    "form": row.get("form"),
                    "status": row.get("status"),
                    "description": row.get("description"),
                    "played": all_stats.get("played"),
                    "win": all_stats.get("win"),
                    "draw": all_stats.get("draw"),
                    "lose": all_stats.get("lose"),
                    "goals_for": goals.get("for"),
                    "goals_against": goals.get("against"),
                    "raw": row,
                }
                normalized_group.append(normalized)
                rows.append(normalized)
            if normalized_group:
                groups.append({
                    "name": normalized_group[0].get("group") or f"Group {len(groups) + 1}",
                    "rows": normalized_group,
                })
    return {"groups": groups, "rows": rows}


def read_api_football_standings_cache(league_id, season, ttl=SCHEDULE_DATA_TTL):
    path = api_football_standings_cache_path(league_id, season)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    fetched_at = parse_cache_datetime(payload.get("fetched_at"))
    if not fetched_at:
        return None
    age = (datetime.now(timezone.utc) - fetched_at.astimezone(timezone.utc)).total_seconds()
    result = payload.get("result")
    if isinstance(result, dict) and age <= ttl:
        result["cache"] = {
            "status": "file_cache",
            "age_hours": round(age / 3600, 2),
            "path": path.name,
        }
        return result
    return None


def read_stale_api_football_standings_cache(league_id, season):
    path = api_football_standings_cache_path(league_id, season)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    result = payload.get("result")
    if isinstance(result, dict):
        result["cache"] = {
            "status": "stale_file_cache",
            "path": path.name,
        }
        return result
    return None


def write_api_football_standings_cache(league_id, season, result):
    if not result or not result.get("found"):
        return
    payload = {
        "league_id": league_id,
        "season": season,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }
    with api_football_standings_cache_path(league_id, season).open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def fixture_cache_key(home_team_id, away_team_id):
    return "-".join(str(team_id) for team_id in sorted([home_team_id, away_team_id]))


def parse_cache_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def read_cached_fixture(home_team, away_team):
    cache = read_fixture_cache_payload()
    key = fixture_cache_key(home_team.get("id"), away_team.get("id"))
    entry = cache.get(key)
    if not entry:
        return None
    fetched_at = parse_cache_datetime(entry.get("fetched_at"))
    if not fetched_at:
        return None
    age = (datetime.now(timezone.utc) - fetched_at.astimezone(timezone.utc)).total_seconds()
    if age > FIXTURE_CACHE_TTL:
        return None
    item = entry.get("fixture_item")
    if not item:
        return None
    return {
        "fixture": fixture_from_response(item),
        "home_team": home_team,
        "away_team": away_team,
        "competition_pair": item.get("league", {}),
        "message": "已从 fixture_cache.json 读取对应比赛。",
        "cache_status": f"fixture_cache（{age / 3600:.1f}小时前）",
    }


def write_cached_fixture(home_team, away_team, item, source):
    cache = read_fixture_cache_payload()
    key = fixture_cache_key(home_team.get("id"), away_team.get("id"))
    cache[key] = {
        "home_team_id": home_team.get("id"),
        "away_team_id": away_team.get("id"),
        "fixture_id": (item.get("fixture") or {}).get("id"),
        "fixture_item": item,
        "source": source,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    write_fixture_cache_payload(cache)


def fixture_from_response(item):
    fixture = item.get("fixture", {})
    teams = item.get("teams", {})
    home = teams.get("home", {})
    away = teams.get("away", {})
    return {
        "id": fixture.get("id"),
        "name": f"{home.get('name')} vs {away.get('name')}",
        "home_team": home,
        "away_team": away,
        "raw": item,
    }


def fixture_matches(item, home_team, away_team):
    teams = item.get("teams", {})
    home = teams.get("home", {})
    away = teams.get("away", {})
    home_id = home.get("id")
    away_id = away.get("id")
    wanted_home_id = home_team.get("id")
    wanted_away_id = away_team.get("id")

    direct = home_id == wanted_home_id and away_id == wanted_away_id
    reversed_match = home_id == wanted_away_id and away_id == wanted_home_id
    return direct or reversed_match


@st.cache_data(ttl=TEAM_DATA_TTL, show_spinner=False)
def team_competitions(team_id):
    competitions = request_json("/leagues", {"team": team_id})
    pairs = []

    for item in competitions:
        league = item.get("league", {})
        for season in item.get("seasons", []):
            year = season.get("year")
            if league.get("id") and year:
                pairs.append({
                    "league_id": league["id"],
                    "league_name": league.get("name"),
                    "season": year,
                    "current": bool(season.get("current")),
                })

    pairs.sort(key=lambda item: (not item["current"], -int(item["season"])))
    return competitions, pairs


def competition_key(pair):
    return pair["league_id"], pair["season"]


def common_competition_pairs(home_pairs, away_pairs):
    away_keys = {competition_key(pair) for pair in away_pairs}
    common = [pair for pair in home_pairs if competition_key(pair) in away_keys]
    return common or home_pairs


@st.cache_data(ttl=MATCH_DATA_TTL, show_spinner=False)
def fixtures_for_team_competition(team_id, pair):
    return request_json(
        "/fixtures",
        {
            "team": team_id,
            "league": pair["league_id"],
            "season": pair["season"],
        },
    )


@st.cache_data(ttl=MATCH_DATA_TTL, show_spinner=False)
def head_to_head_fixtures(home_team_id, away_team_id):
    return request_json("/fixtures/headtohead", {"h2h": f"{home_team_id}-{away_team_id}"})


@st.cache_data(ttl=MATCH_DATA_TTL, show_spinner=False)
def find_fixture(match):
    home_team = search_team(match["home_en"])
    away_team = search_team(match["away_en"])

    for label, team in [("home", home_team), ("away", away_team)]:
        resolver = (team or {}).get("_resolver") or {}
        print(
            "[Team Resolver]",
            label,
            "input=", resolver.get("input") or match.get(f"{label}_en"),
            "matched=", resolver.get("matched_name"),
            "team_id=", resolver.get("team_id"),
        )

    if not home_team or not away_team:
        return {
            "fixture": None,
            "home_team": home_team,
            "away_team": away_team,
            "message": "未找到双方国家队信息。",
        }

    cached_fixture = read_cached_fixture(home_team, away_team)
    if cached_fixture:
        return cached_fixture

    try:
        h2h_fixtures = head_to_head_fixtures(home_team["id"], away_team["id"])
    except (requests.RequestException, RuntimeError):
        h2h_fixtures = []

    for item in h2h_fixtures:
        if fixture_matches(item, home_team, away_team):
            write_cached_fixture(home_team, away_team, item, "API-Football head-to-head")
            return {
                "fixture": fixture_from_response(item),
                "home_team": home_team,
                "away_team": away_team,
                "competition_pair": item.get("league", {}),
                "message": "已通过 API-Football head-to-head 找到对应比赛。",
            }

    home_competitions, home_pairs = team_competitions(home_team["id"])
    away_competitions, away_pairs = team_competitions(away_team["id"])
    pairs = common_competition_pairs(home_pairs, away_pairs)

    fixture_pool = []
    for pair in pairs:
        fixture_pool.extend(fixtures_for_team_competition(home_team["id"], pair))
        fixture_pool.extend(fixtures_for_team_competition(away_team["id"], pair))

    for item in fixture_pool:
        if fixture_matches(item, home_team, away_team):
            write_cached_fixture(home_team, away_team, item, "API-Football fixtures")
            return {
                "fixture": fixture_from_response(item),
                "home_team": home_team,
                "away_team": away_team,
                "home_competitions_sample": home_competitions[:3],
                "away_competitions_sample": away_competitions[:3],
                "competition_pair": item.get("league", {}),
                "message": "已找到对应比赛。",
            }

    return {
        "fixture": None,
        "home_team": home_team,
        "away_team": away_team,
        "home_competitions_sample": home_competitions[:3],
        "away_competitions_sample": away_competitions[:3],
        "message": "未找到双方对应比赛。",
    }


def parse_odd(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 1 else None


def extract_match_winner_odds(odds_response):
    for item in odds_response:
        for bookmaker in item.get("bookmakers", []):
            for bet in bookmaker.get("bets", []):
                bet_name = normalize_text(bet.get("name", ""))
                if bet_name not in {"match winner", "winner"}:
                    continue

                values = {}
                for value in bet.get("values", []):
                    key = normalize_text(value.get("value", ""))
                    odd = parse_odd(value.get("odd"))
                    if odd:
                        values[key] = odd

                home = values.get("home")
                draw = values.get("draw")
                away = values.get("away")
                if home and draw and away:
                    return {
                        "home_win": home,
                        "draw": draw,
                        "away_win": away,
                        "bookmaker": bookmaker.get("name"),
                    }

    return None


def fetch_odds_for_fixture(fixture):
    try:
        odds_response = request_json("/odds", {"fixture": fixture["id"]})
    except (requests.RequestException, RuntimeError) as error:
        return empty_result(f"找到了比赛，但无法读取 API-Football 赔率：{error}", fixture)

    prices = extract_match_winner_odds(odds_response)
    if not prices:
        return empty_result("找到了比赛，但没有返回完整的主胜/平局/客胜赔率。", fixture)

    return {
        "found": True,
        "home_win": prices["home_win"],
        "draw": prices["draw"],
        "away_win": prices["away_win"],
        "over_under_line": None,
        "raw_probabilities": raw_probabilities(
            prices["home_win"], prices["draw"], prices["away_win"]
        ),
        "implied_probabilities": implied_probabilities(
            prices["home_win"], prices["draw"], prices["away_win"]
        ),
        "source": f"API-Football 免费版 / {prices.get('bookmaker') or 'Bookmaker'}",
        "event_title": fixture["name"],
        "event_id": fixture["id"],
        "message": "已找到真实 1X2 赔率。",
    }


def empty_correct_score_result(reason):
    return {
        "found": False,
        "source": "API-Football / Exact Score",
        "bookmakers": [],
        "rows": [],
        "message": reason,
    }


def empty_asian_handicap_result(reason):
    return {
        "found": False,
        "source": "API-Football / Asian Handicap",
        "bookmakers": [],
        "rows": [],
        "message": reason,
    }


@st.cache_data(ttl=API_FOOTBALL_MARKET_DATA_TTL, show_spinner=False)
def fetch_asian_handicap_odds_for_fixture(fixture_id):
    if not fixture_id:
        return empty_asian_handicap_result("缺少 API-Football fixture_id，无法查询真实亚洲让球盘。")

    cached = read_api_football_market_cache(fixture_id, ASIAN_HANDICAP_BET_ID, API_FOOTBALL_MARKET_DATA_TTL)
    if cached:
        return cached

    try:
        response = request_json("/odds", {"fixture": fixture_id, "bet": ASIAN_HANDICAP_BET_ID})
    except (requests.RequestException, RuntimeError) as error:
        stale = read_stale_api_football_market_cache(fixture_id, ASIAN_HANDICAP_BET_ID)
        if stale:
            stale["message"] = f"{stale.get('message', '已读取缓存亚洲让球盘。')} API暂不可用，使用已保存缓存。"
            return stale
        return empty_asian_handicap_result(f"API-Football Asian Handicap 暂不可用：{error}")

    rows = []
    bookmaker_names = []
    for item in response:
        for bookmaker in item.get("bookmakers", []):
            bookmaker_name = bookmaker.get("name")
            if bookmaker_name:
                bookmaker_names.append(bookmaker_name)
            for bet in bookmaker.get("bets", []):
                if bet.get("id") != ASIAN_HANDICAP_BET_ID:
                    continue
                market_name = bet.get("name") or "Asian Handicap"
                for value in bet.get("values", []):
                    odd = parse_odd(value.get("odd"))
                    line_value = value.get("value")
                    if odd and line_value:
                        rows.append({
                            "bookmaker": bookmaker_name,
                            "market": market_name,
                            "value": line_value,
                            "odd": odd,
                        })

    if not rows:
        return empty_asian_handicap_result("API-Football 没有返回该比赛的真实亚洲让球盘。")

    result = {
        "found": True,
        "source": "API-Football / Asian Handicap",
        "bookmakers": sorted(set(bookmaker_names)),
        "rows": rows,
        "message": "已获取 API-Football 真实亚洲让球盘。",
    }
    write_api_football_market_cache(fixture_id, ASIAN_HANDICAP_BET_ID, result)
    return result


@st.cache_data(ttl=CORRECT_SCORE_DATA_TTL, show_spinner=False)
def fetch_correct_score_odds_for_fixture(fixture_id):
    if not fixture_id:
        return empty_correct_score_result("缺少 API-Football fixture_id，无法查询真实波胆盘口。")

    cached = read_api_football_market_cache(fixture_id, EXACT_SCORE_BET_ID, CORRECT_SCORE_DATA_TTL)
    if cached:
        return cached

    try:
        response = request_json("/odds", {"fixture": fixture_id, "bet": EXACT_SCORE_BET_ID})
    except (requests.RequestException, RuntimeError) as error:
        stale = read_stale_api_football_market_cache(fixture_id, EXACT_SCORE_BET_ID)
        if stale:
            stale["message"] = f"{stale.get('message', '已读取缓存波胆盘口。')} API暂不可用，使用已保存缓存。"
            return stale
        return empty_correct_score_result(f"API-Football Exact Score 暂不可用：{error}")

    rows = []
    bookmaker_names = []
    for item in response:
        for bookmaker in item.get("bookmakers", []):
            bookmaker_id = bookmaker.get("id")
            bookmaker_name = bookmaker.get("name") or PREFERRED_CORRECT_SCORE_BOOKMAKERS.get(bookmaker_id)
            if bookmaker_name:
                bookmaker_names.append(bookmaker_name)
            for bet in bookmaker.get("bets", []):
                if bet.get("id") != EXACT_SCORE_BET_ID:
                    continue
                for value in bet.get("values", []):
                    odd = parse_odd(value.get("odd"))
                    score = value.get("value")
                    if odd and score:
                        rows.append({
                            "bookmaker_id": bookmaker_id,
                            "bookmaker": bookmaker_name,
                            "score": score,
                            "odd": odd,
                        })

    if not rows:
        return empty_correct_score_result("API-Football 没有返回该比赛的真实波胆盘口。")

    preferred_ids = set(PREFERRED_CORRECT_SCORE_BOOKMAKERS)
    preferred_rows = [row for row in rows if row.get("bookmaker_id") in preferred_ids]
    display_rows = preferred_rows or rows
    display_rows = sorted(display_rows, key=lambda row: (row["score"], -row["odd"]))

    result = {
        "found": True,
        "source": "API-Football / Exact Score",
        "bookmakers": sorted(set(bookmaker_names)),
        "rows": display_rows,
        "all_rows": rows,
        "message": "已获取 API-Football 真实 Exact Score 波胆盘口。",
    }
    write_api_football_market_cache(fixture_id, EXACT_SCORE_BET_ID, result)
    return result


def fetch_odds(match):
    try:
        fixture_result = find_fixture(match)
    except (requests.RequestException, RuntimeError) as error:
        return empty_result(f"无法连接 API-Football 或读取数据：{error}")

    fixture = fixture_result.get("fixture")
    if not fixture:
        return empty_result(fixture_result["message"])

    return fetch_odds_for_fixture(fixture)


def empty_standings_result(reason, league_id=None, season=None):
    return {
        "found": False,
        "source": "API-Football / Standings",
        "league_id": league_id,
        "season": season,
        "groups": [],
        "rows": [],
        "message": reason,
    }


@st.cache_data(ttl=SCHEDULE_DATA_TTL, show_spinner=False)
def fetch_standings_for_league(league_id, season):
    if not league_id or not season:
        return empty_standings_result("缺少 league_id 或 season，无法查询 API-Football 积分榜。", league_id, season)

    cached = read_api_football_standings_cache(league_id, season, SCHEDULE_DATA_TTL)
    if cached:
        return cached

    try:
        response = request_json("/standings", {"league": league_id, "season": season})
    except (requests.RequestException, RuntimeError) as error:
        stale = read_stale_api_football_standings_cache(league_id, season)
        if stale:
            stale["message"] = f"{stale.get('message', '已读取缓存积分榜。')} API暂不可用，使用已保存缓存。"
            return stale
        return empty_standings_result(f"API-Football Standings 暂不可用：{error}", league_id, season)

    flattened = flatten_standings_response(response)
    if not flattened["rows"]:
        return empty_standings_result("API-Football 没有返回该赛事积分榜。", league_id, season)

    result = {
        "found": True,
        "source": "API-Football / Standings",
        "league_id": league_id,
        "season": season,
        "groups": flattened["groups"],
        "rows": flattened["rows"],
        "raw": response,
        "message": "已获取 API-Football 小组积分榜。",
    }
    write_api_football_standings_cache(league_id, season, result)
    return result


@st.cache_data(ttl=TEAM_DATA_TTL, show_spinner=False)
def fetch_injuries_for_fixture(fixture_id):
    return request_json("/injuries", {"fixture": fixture_id})


@st.cache_data(ttl=TEAM_DATA_TTL, show_spinner=False)
def fetch_lineups_for_fixture(fixture_id):
    return request_json("/fixtures/lineups", {"fixture": fixture_id})


@st.cache_data(ttl=TEAM_DATA_TTL, show_spinner=False)
def fetch_recent_fixtures(team_id, count=5):
    fixtures = []
    finished_statuses = {"FT", "AET", "PEN"}
    for season in [2024, 2023, 2022]:
        for item in request_json("/fixtures", {"team": team_id, "season": season}):
            fixture = item.get("fixture", {})
            status = fixture.get("status", {}) or {}
            date_text = fixture.get("date", "")
            try:
                kickoff = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
            except ValueError:
                kickoff = None

            is_finished = status.get("short") in finished_statuses
            is_past = kickoff is not None and kickoff <= datetime.now(timezone.utc)
            if is_finished or is_past:
                fixtures.append(item)

        fixtures.sort(
            key=lambda item: item.get("fixture", {}).get("date", ""),
            reverse=True,
        )
        if len(fixtures) >= count:
            break

    fixtures.sort(
        key=lambda item: item.get("fixture", {}).get("date", ""),
        reverse=True,
    )
    return fixtures[:count]


def known_fixture_for_match(match):
    home = normalize_text(match.get("home_en") or match.get("home_cn"))
    away = normalize_text(match.get("away_en") or match.get("away_cn"))
    if home != "argentina" or away != "algeria":
        return None

    home_team = {
        "id": 26,
        "name": "Argentina",
        "code": "ARG",
        "country": "Argentina",
        "national": True,
        "logo": "https://media.api-sports.io/football/teams/26.png",
    }
    away_team = {
        "id": 1532,
        "name": "Algeria",
        "code": "ALG",
        "country": "Algeria",
        "national": True,
        "logo": "https://media.api-sports.io/football/teams/1532.png",
    }
    fixture = {
        "id": None,
        "name": "Argentina vs Algeria",
        "home_team": home_team,
        "away_team": away_team,
        "raw": {
            "fixture": {
                "id": None,
                "date": "2026-06-17T01:00:00+00:00",
                "timezone": "UTC",
                "venue": {
                    "name": "Arrowhead Stadium",
                    "city": "Kansas City",
                },
                "status": {"long": "Not Started", "short": "NS"},
            },
            "league": {
                "id": 1,
                "name": "World Cup",
                "season": 2026,
                "round": "Group Stage - 1",
            },
            "teams": {
                "home": home_team,
                "away": away_team,
            },
        },
    }
    return {
        "fixture": fixture,
        "home_team": home_team,
        "away_team": away_team,
        "message": "使用已验证的 Argentina vs Algeria fixture 概览数据。",
    }


def fetch_match_diagnostics(match):
    result = {
        "fixture": None,
        "odds": None,
        "asian_handicap": None,
        "correct_score": None,
        "injuries": None,
        "lineups": None,
        "home_recent": None,
        "away_recent": None,
        "error": None,
    }

    try:
        fixture_result = find_fixture(match)
        result["fixture"] = fixture_result
        fixture = fixture_result.get("fixture")
        if not fixture:
            result["error"] = fixture_result["message"]
            return result

        result["odds"] = fetch_odds(match)
        result["asian_handicap"] = fetch_asian_handicap_odds_for_fixture(fixture["id"])
        result["correct_score"] = fetch_correct_score_odds_for_fixture(fixture["id"])
        result["injuries"] = fetch_injuries_for_fixture(fixture["id"])
        result["lineups"] = fetch_lineups_for_fixture(fixture["id"])
        result["home_recent"] = fetch_recent_fixtures(fixture_result["home_team"]["id"])
        result["away_recent"] = fetch_recent_fixtures(fixture_result["away_team"]["id"])
        return result
    except (requests.RequestException, RuntimeError) as error:
        result["error"] = str(error)
        return result


@st.cache_data(ttl=MATCH_DATA_TTL, show_spinner=False)
def fetch_match_data(match, data_flow_version="team_resolver_v2"):
    data = {
        "fixture_result": None,
        "fixture": None,
        "odds": None,
        "asian_handicap": None,
        "correct_score": None,
        "injuries": [],
        "lineups": [],
        "home_recent": [],
        "away_recent": [],
        "standings": None,
        "error": None,
    }

    try:
        fixture_result = find_fixture(match)
        data["fixture_result"] = fixture_result
        fixture = fixture_result.get("fixture")
        data["fixture"] = fixture

        if not fixture:
            data["odds"] = empty_result(fixture_result["message"])
            data["error"] = fixture_result["message"]
            return data

        data["odds"] = empty_result(
            "API-Football 免费版无法获取 2026 World Cup odds：Free plans do not have access to this season。",
            fixture,
        )

        data["correct_score"] = fetch_correct_score_odds_for_fixture(fixture["id"])
        data["asian_handicap"] = fetch_asian_handicap_odds_for_fixture(fixture["id"])

        raw_league = ((fixture or {}).get("raw") or {}).get("league") or {}
        try:
            data["standings"] = fetch_standings_for_league(raw_league.get("id"), raw_league.get("season"))
        except (requests.RequestException, RuntimeError) as error:
            data["standings"] = empty_standings_result(
                f"API-Football Standings 暂不可用：{error}",
                raw_league.get("id"),
                raw_league.get("season"),
            )

        try:
            data["injuries"] = fetch_injuries_for_fixture(fixture["id"])
        except (requests.RequestException, RuntimeError) as error:
            data["injuries_error"] = str(error)

        try:
            data["lineups"] = fetch_lineups_for_fixture(fixture["id"])
        except (requests.RequestException, RuntimeError) as error:
            data["lineups_error"] = str(error)

        try:
            data["home_recent"] = fetch_recent_fixtures(fixture_result["home_team"]["id"], count=10)
        except (requests.RequestException, RuntimeError) as error:
            data["home_recent_error"] = str(error)

        try:
            data["away_recent"] = fetch_recent_fixtures(fixture_result["away_team"]["id"], count=10)
        except (requests.RequestException, RuntimeError) as error:
            data["away_recent_error"] = str(error)

        return data
    except (requests.RequestException, RuntimeError) as error:
        known_fixture = known_fixture_for_match(match)
        if known_fixture:
            data["fixture_result"] = known_fixture
            data["fixture"] = known_fixture["fixture"]
            data["odds"] = empty_result(
                "API-Football 免费版当前无法读取 2026 World Cup odds；赔率使用 The Odds API。",
                known_fixture["fixture"],
            )
            data["correct_score"] = empty_correct_score_result("缺少 API-Football fixture_id，无法查询真实波胆盘口。")
            data["asian_handicap"] = empty_asian_handicap_result("缺少 API-Football fixture_id，无法查询真实亚洲让球盘。")
            raw_league = ((known_fixture["fixture"] or {}).get("raw") or {}).get("league") or {}
            data["standings"] = empty_standings_result(
                "备用 fixture 没有可验证的 API-Football standings。",
                raw_league.get("id"),
                raw_league.get("season"),
            )
            data["error"] = str(error)
            try:
                data["home_recent"] = fetch_recent_fixtures(known_fixture["home_team"]["id"], count=10)
            except (requests.RequestException, RuntimeError) as recent_error:
                data["home_recent_error"] = str(recent_error)
            try:
                data["away_recent"] = fetch_recent_fixtures(known_fixture["away_team"]["id"], count=10)
            except (requests.RequestException, RuntimeError) as recent_error:
                data["away_recent_error"] = str(recent_error)
            return data

        data["odds"] = empty_result(f"无法连接 API-Football 或读取数据：{error}")
        data["error"] = str(error)
        return data
