import os
import tomllib
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st

from modules.cache_config import MATCH_DATA_TTL, TEAM_DATA_TTL


API_FOOTBALL_BASE = "https://v3.football.api-sports.io"


def normalize_text(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_text.lower().replace(".", " ").replace("-", " ").split())


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
        timeout=20,
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


@st.cache_data(ttl=TEAM_DATA_TTL, show_spinner=False)
def search_team(team_name):
    teams = request_json("/teams", {"search": team_name})
    if not teams:
        return None

    target = normalize_text(team_name)
    national_teams = [item for item in teams if item.get("team", {}).get("national")]
    candidates = national_teams or teams

    for item in candidates:
        team = item.get("team", {})
        name = normalize_text(team.get("name", ""))
        code = normalize_text(team.get("code", ""))
        if target == name or target == code:
            return team

    for item in candidates:
        team = item.get("team", {})
        if target in normalize_text(team.get("name", "")):
            return team

    return candidates[0].get("team")


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
def find_fixture(match):
    home_team = search_team(match["home_en"])
    away_team = search_team(match["away_en"])

    if not home_team or not away_team:
        return {
            "fixture": None,
            "home_team": home_team,
            "away_team": away_team,
            "message": "未找到双方国家队信息。",
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


def fetch_odds(match):
    try:
        fixture_result = find_fixture(match)
    except (requests.RequestException, RuntimeError) as error:
        return empty_result(f"无法连接 API-Football 或读取数据：{error}")

    fixture = fixture_result.get("fixture")
    if not fixture:
        return empty_result(fixture_result["message"])

    return fetch_odds_for_fixture(fixture)


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
        result["injuries"] = fetch_injuries_for_fixture(fixture["id"])
        result["lineups"] = fetch_lineups_for_fixture(fixture["id"])
        result["home_recent"] = fetch_recent_fixtures(fixture_result["home_team"]["id"])
        result["away_recent"] = fetch_recent_fixtures(fixture_result["away_team"]["id"])
        return result
    except (requests.RequestException, RuntimeError) as error:
        result["error"] = str(error)
        return result


@st.cache_data(ttl=MATCH_DATA_TTL, show_spinner=False)
def fetch_match_data(match):
    data = {
        "fixture_result": None,
        "fixture": None,
        "odds": None,
        "injuries": [],
        "lineups": [],
        "home_recent": [],
        "away_recent": [],
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

        try:
            data["injuries"] = fetch_injuries_for_fixture(fixture["id"])
        except (requests.RequestException, RuntimeError) as error:
            data["injuries_error"] = str(error)

        try:
            data["lineups"] = fetch_lineups_for_fixture(fixture["id"])
        except (requests.RequestException, RuntimeError) as error:
            data["lineups_error"] = str(error)

        try:
            data["home_recent"] = fetch_recent_fixtures(fixture_result["home_team"]["id"])
        except (requests.RequestException, RuntimeError) as error:
            data["home_recent_error"] = str(error)

        try:
            data["away_recent"] = fetch_recent_fixtures(fixture_result["away_team"]["id"])
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
            data["error"] = str(error)
            try:
                data["home_recent"] = fetch_recent_fixtures(known_fixture["home_team"]["id"])
            except (requests.RequestException, RuntimeError) as recent_error:
                data["home_recent_error"] = str(recent_error)
            try:
                data["away_recent"] = fetch_recent_fixtures(known_fixture["away_team"]["id"])
            except (requests.RequestException, RuntimeError) as recent_error:
                data["away_recent_error"] = str(recent_error)
            return data

        data["odds"] = empty_result(f"无法连接 API-Football 或读取数据：{error}")
        data["error"] = str(error)
        return data
