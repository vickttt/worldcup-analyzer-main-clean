import json
import re
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from modules.api_client import request_json
from modules.probability_base import consensus_probabilities
from modules.cache_config import (
    API_FOOTBALL_MARKET_DATA_TTL,
    CORRECT_SCORE_DATA_TTL,
    MATCH_DATA_TTL,
    ODDS_DATA_TTL,
    TEAM_DATA_TTL,
)
from modules.team_resolver import normalize_text, resolve_team as search_team


EXACT_SCORE_BET_ID = 10
ASIAN_HANDICAP_BET_ID = 4
OVER_UNDER_BET_ID = 5
PREFERRED_CORRECT_SCORE_BOOKMAKERS = {
    4: "Pinnacle",
    8: "Bet365",
    13: "188Bet",
}


def empty_result(reason, fixture=None, degraded=False, status=None, error=None):
    return {
        "found": False,
        "degraded": degraded,
        "status": status or ("unavailable" if degraded else "missing"),
        "error": error,
        "home_win": None,
        "draw": None,
        "away_win": None,
        "over_under_line": None,
        "over_under": [],
        "over_under_bookmakers": [],
        "over_under_source": "API-Football / Goals Over/Under",
        "over_under_message": reason,
        "source": "API-Football 免费版",
        "event_title": fixture.get("name") if fixture else None,
        "event_id": fixture.get("id") if fixture else None,
        "message": reason,
    }


def cache_dir():
    path = Path(__file__).resolve().parents[1] / "data" / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def fixture_cache_path():
    return cache_dir() / "fixture_cache.json"


def api_football_market_cache_path(fixture_id, bet_id):
    return cache_dir() / f"api_football_market_{fixture_id}_{bet_id}.json"


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


def parse_cache_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


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


def fixture_from_selected_fixture(selected_fixture):
    if not selected_fixture or not selected_fixture.get("fixture_id"):
        return None
    home = selected_fixture.get("home_team") or {}
    away = selected_fixture.get("away_team") or {}
    return {
        "id": selected_fixture.get("fixture_id"),
        "name": f"{home.get('name')} vs {away.get('name')}",
        "home_team": home,
        "away_team": away,
        "raw": {
            "fixture": {
                "id": selected_fixture.get("fixture_id"),
                "date": selected_fixture.get("kickoff_utc"),
                "venue": {
                    "name": selected_fixture.get("venue_name"),
                    "city": selected_fixture.get("venue_city"),
                },
                "status": {
                    "long": selected_fixture.get("status_text"),
                    "short": selected_fixture.get("status"),
                },
            },
            "league": {
                "name": selected_fixture.get("league_name"),
                "round": selected_fixture.get("round"),
                "season": 2026,
            },
            "teams": {
                "home": home,
                "away": away,
            },
        },
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

    try:
        h2h_fixtures = head_to_head_fixtures(home_team["id"], away_team["id"])
    except RuntimeError:
        h2h_fixtures = []

    for item in h2h_fixtures:
        if fixture_matches(item, home_team, away_team):
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


def extract_match_winner_rows(odds_response):
    rows = []
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
                    rows.append({
                        "home_win": home,
                        "draw": draw,
                        "away_win": away,
                        "bookmaker": bookmaker.get("name"),
                    })

    return rows


def extract_match_winner_odds(odds_response):
    rows = extract_match_winner_rows(odds_response)
    if rows:
        return rows[0]

    return None


def parse_total_value(value):
    text = str(value or "").strip()
    match = re.search(r"\b(over|under)\b\s*([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    if not match:
        return None, None
    return match.group(1).lower(), float(match.group(2))


def extract_over_under_odds(odds_response):
    rows = []
    bookmaker_names = []

    for item in odds_response:
        for bookmaker in item.get("bookmakers", []):
            bookmaker_name = bookmaker.get("name")
            if bookmaker_name:
                bookmaker_names.append(bookmaker_name)
            for bet in bookmaker.get("bets", []):
                bet_id = bet.get("id")
                bet_name = normalize_text(bet.get("name", ""))
                is_totals_market = bet_id == OVER_UNDER_BET_ID or bet_name in {
                    "goals over under",
                    "over under",
                    "total goals",
                    "goals overunder",
                }
                if not is_totals_market:
                    continue

                by_line = {}
                for value in bet.get("values", []):
                    side, line = parse_total_value(value.get("value"))
                    odd = parse_odd(value.get("odd"))
                    if not side or line is None or not odd:
                        continue
                    row = by_line.setdefault(line, {"line": line, "bookmaker": bookmaker_name})
                    if side == "over":
                        row["over_odds"] = odd
                    elif side == "under":
                        row["under_odds"] = odd

                rows.extend(
                    row for row in by_line.values()
                    if row.get("over_odds") and row.get("under_odds")
                )

    return rows, sorted(set(bookmaker_names))


def fetch_over_under_odds_for_fixture(fixture_id):
    if not fixture_id:
        return [], []
    try:
        response = request_json("/odds", {"fixture": fixture_id, "bet": OVER_UNDER_BET_ID})
    except RuntimeError:
        return [], []
    return extract_over_under_odds(response)


def fetch_odds_for_fixture(fixture):
    try:
        odds_response = request_json("/odds", {"fixture": fixture["id"]})
    except RuntimeError as error:
        return empty_result(f"API temporarily unavailable：{error}", fixture, degraded=True)

    winner_rows = extract_match_winner_rows(odds_response)
    prices = winner_rows[0] if winner_rows else None
    if not prices:
        return empty_result("找到了比赛，但没有返回完整的主胜/平局/客胜赔率。", fixture)
    totals, totals_bookmakers = extract_over_under_odds(odds_response)
    totals_source = "full_fixture_odds"
    if not totals:
        totals, totals_bookmakers = fetch_over_under_odds_for_fixture(fixture["id"])
        totals_source = "bet_5_retry" if totals else "not_returned"

    return {
        "found": True,
        "home_win": prices["home_win"],
        "draw": prices["draw"],
        "away_win": prices["away_win"],
        "over_under_line": totals[0].get("line") if totals else None,
        "over_under": totals,
        "over_under_bookmakers": totals_bookmakers,
        "over_under_source": f"API-Football / Goals Over/Under ({totals_source})",
        "true_probability_base": consensus_probabilities(winner_rows),
        "match_winner_rows": winner_rows,
        "source": f"API-Football 免费版 / {prices.get('bookmaker') or 'Bookmaker'}",
        "event_title": fixture["name"],
        "event_id": fixture["id"],
        "message": "已找到真实 1X2 赔率。",
    }


def empty_correct_score_result(reason, degraded=False, status=None, error=None):
    return {
        "found": False,
        "degraded": degraded,
        "status": status or ("unavailable" if degraded else "missing"),
        "error": error,
        "source": "API-Football / Exact Score",
        "bookmakers": [],
        "rows": [],
        "message": reason,
    }


def empty_asian_handicap_result(reason, degraded=False):
    return {
        "found": False,
        "degraded": degraded,
        "source": "API-Football / Asian Handicap",
        "bookmakers": [],
        "rows": [],
        "message": reason,
    }


@st.cache_data(ttl=API_FOOTBALL_MARKET_DATA_TTL, show_spinner=False)
def fetch_asian_handicap_odds_for_fixture(fixture_id):
    if not fixture_id:
        return empty_asian_handicap_result("缺少 API-Football fixture_id，无法查询真实亚洲让球盘。")

    try:
        response = request_json("/odds", {"fixture": fixture_id, "bet": ASIAN_HANDICAP_BET_ID})
    except RuntimeError as error:
        return empty_asian_handicap_result(
            f"API temporarily unavailable，亚洲让球盘将在下次刷新重试：{error}",
            degraded=True,
        )

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
    return result


@st.cache_data(ttl=CORRECT_SCORE_DATA_TTL, show_spinner=False)
def fetch_correct_score_odds_for_fixture(fixture_id):
    if not fixture_id:
        return empty_correct_score_result("缺少 API-Football fixture_id，无法查询真实波胆盘口。")

    try:
        response = request_json("/odds", {"fixture": fixture_id, "bet": EXACT_SCORE_BET_ID})
    except RuntimeError as error:
        return empty_correct_score_result(
            f"API temporarily unavailable，Correct Score 将在下次刷新重试：{error}",
            degraded=True,
            status="unavailable",
            error="API temporarily unavailable",
        )

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
    return result


def fetch_odds(match, selected_fixture=None):
    fixture = fixture_from_selected_fixture(selected_fixture)
    if not fixture:
        reason = "缺少当前 UI 选中赛程的 API-Football fixture_id，已阻止重新映射 fixture。"
        return empty_result(reason, status="unavailable", error="missing selected_fixture")

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


def fetch_match_diagnostics(match, selected_fixture=None):
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
        fixture = fixture_from_selected_fixture(selected_fixture)
        if not fixture:
            result["error"] = "缺少当前 UI 选中赛程的 API-Football fixture_id，已阻止重新映射 fixture。"
            return result
        fixture_result = {
            "fixture": fixture,
            "home_team": fixture.get("home_team") or {},
            "away_team": fixture.get("away_team") or {},
            "message": "已使用赛程页选择的 API-Football fixture_id。",
        }
        result["fixture"] = fixture_result

        result["odds"] = fetch_odds(match, selected_fixture)
        result["asian_handicap"] = fetch_asian_handicap_odds_for_fixture(fixture["id"])
        result["correct_score"] = fetch_correct_score_odds_for_fixture(fixture["id"])
        result["injuries"] = fetch_injuries_for_fixture(fixture["id"])
        result["lineups"] = fetch_lineups_for_fixture(fixture["id"])
        result["home_recent"] = fetch_recent_fixtures(fixture_result["home_team"]["id"])
        result["away_recent"] = fetch_recent_fixtures(fixture_result["away_team"]["id"])
        return result
    except RuntimeError as error:
        result["error"] = str(error)
        return result


@st.cache_data(ttl=MATCH_DATA_TTL, show_spinner=False)
def fetch_match_data(match, data_flow_version="team_resolver_v2", selected_fixture=None):
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
        "error": None,
    }

    try:
        selected_api_fixture = fixture_from_selected_fixture(selected_fixture)
        if not selected_api_fixture:
            reason = "缺少当前 UI 选中赛程的 API-Football fixture_id，已阻止重新映射 fixture。"
            data["fixture_result"] = {"fixture": None, "message": reason}
            data["odds"] = empty_result(reason, status="unavailable", error="missing selected_fixture")
            data["correct_score"] = empty_correct_score_result(
                reason,
                status="unavailable",
                error="missing selected_fixture",
            )
            data["error"] = reason
            return data

        fixture_result = {
            "fixture": selected_api_fixture,
            "home_team": selected_api_fixture.get("home_team") or {},
            "away_team": selected_api_fixture.get("away_team") or {},
            "message": "已使用赛程页选择的 API-Football fixture_id。",
        }
        data["fixture_result"] = fixture_result
        fixture = fixture_result.get("fixture")
        data["fixture"] = fixture

        if not fixture:
            data["odds"] = empty_result(fixture_result["message"])
            data["error"] = fixture_result["message"]
            return data

        data["odds"] = fetch_odds_for_fixture(fixture)

        data["correct_score"] = fetch_correct_score_odds_for_fixture(fixture["id"])
        data["asian_handicap"] = fetch_asian_handicap_odds_for_fixture(fixture["id"])

        try:
            data["injuries"] = fetch_injuries_for_fixture(fixture["id"])
        except RuntimeError as error:
            data["injuries_error"] = str(error)

        try:
            data["lineups"] = fetch_lineups_for_fixture(fixture["id"])
        except RuntimeError as error:
            data["lineups_error"] = str(error)

        try:
            home_team_id = (fixture_result.get("home_team") or {}).get("id")
            if home_team_id:
                data["home_recent"] = fetch_recent_fixtures(home_team_id, count=10)
        except RuntimeError as error:
            data["home_recent_error"] = str(error)

        try:
            away_team_id = (fixture_result.get("away_team") or {}).get("id")
            if away_team_id:
                data["away_recent"] = fetch_recent_fixtures(away_team_id, count=10)
        except RuntimeError as error:
            data["away_recent_error"] = str(error)

        return data
    except RuntimeError as error:
        data["odds"] = empty_result(f"API temporarily unavailable：{error}", degraded=True)
        data["error"] = str(error)
        return data
