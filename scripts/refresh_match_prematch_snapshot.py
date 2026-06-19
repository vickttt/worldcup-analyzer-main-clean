import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.match_parser import parse_match
from modules.odds_client import (
    ASIAN_HANDICAP_BET_ID,
    EXACT_SCORE_BET_ID,
    empty_asian_handicap_result,
    empty_correct_score_result,
    parse_odd,
    request_json,
    write_api_football_market_cache,
)
from modules.result_distribution import build_result_distribution
from modules.schedule_client import fetch_world_cup_schedule, fixture_local_datetime
from modules.team_resolver import alias_candidates, request_teams, select_team_from_response
from modules.the_odds_client import (
    THE_ODDS_API_BASE,
    WORLD_CUP_SPORT_KEYS,
    cache_metadata,
    daily_utc_window,
    event_matches,
    extract_h2h_prices,
    extract_spreads,
    extract_totals,
    implied_probabilities,
    load_the_odds_api_key,
    raw_probabilities,
    read_daily_cache,
    write_daily_cache,
)
from modules.user_odds import build_market_candidates, build_recommendation_slots
from modules.weather_client import weather_for_fixture


LOCAL_TZ = ZoneInfo("Asia/Shanghai")


def normalize(value):
    return " ".join(str(value or "").lower().replace("&", "and").split())


def schedule_match(fixture, match):
    home = normalize((fixture.get("home_team") or {}).get("name"))
    away = normalize((fixture.get("away_team") or {}).get("name"))
    wanted_home = normalize(match["home_en"])
    wanted_away = normalize(match["away_en"])
    direct = wanted_home in home and wanted_away in away
    reversed_match = wanted_home in away and wanted_away in home
    return direct or reversed_match


def api_error_payload(source, error):
    return {
        "found": False,
        "source": source,
        "message": str(error),
        "rows": [],
        "bookmakers": [],
    }


def force_fetch_schedule(match):
    schedule = fetch_world_cup_schedule(force_refresh=True)
    fixtures = schedule.get("fixtures") or []
    fixture = next((item for item in fixtures if schedule_match(item, match)), None)
    return schedule, fixture


def fetch_the_odds_force(match, date_key):
    api_key = load_the_odds_api_key()
    if not api_key:
        return {
            "found": False,
            "source": "The Odds API",
            "message": "缺少 THE_ODDS_API_KEY。",
            "events": [],
        }

    last_error = None
    for sport_key in WORLD_CUP_SPORT_KEYS:
        start_utc, end_utc = daily_utc_window(date_key)
        try:
            response = requests.get(
                f"{THE_ODDS_API_BASE}/sports/{sport_key}/odds",
                params={
                    "apiKey": api_key,
                    "regions": "eu,us,uk,au",
                    "markets": "h2h,spreads,totals",
                    "oddsFormat": "decimal",
                    "dateFormat": "iso",
                    "commenceTimeFrom": start_utc,
                    "commenceTimeTo": end_utc,
                },
                timeout=25,
            )
            if response.status_code == 404:
                events = []
            else:
                response.raise_for_status()
                events = response.json()
        except requests.RequestException as error:
            last_error = error
            cached_payload = read_daily_cache(sport_key, date_key)
            if not cached_payload:
                continue
            events = cached_payload.get("events") or []
            payload = {
                **cached_payload,
                "cache_status": "cached fallback after request error",
                "request_headers": cached_payload.get("request_headers") or {},
            }
        else:
            payload = {
                "source": "The Odds API",
                "sport_key": sport_key,
                "date_key": date_key,
                "fetched_at": datetime.now(LOCAL_TZ).isoformat(),
                "cache_status": "fresh api response - forced single match refresh",
                "events": events,
                "request_headers": {
                    "x-requests-used": response.headers.get("x-requests-used") if "response" in locals() else None,
                    "x-requests-remaining": response.headers.get("x-requests-remaining") if "response" in locals() else None,
                    "x-requests-last": response.headers.get("x-requests-last") if "response" in locals() else None,
                },
            }
            write_daily_cache(sport_key, date_key, payload)

        for event in events:
            if not event_matches(event, match):
                continue
            prices, bookmaker = extract_h2h_prices(event, match)
            spreads = extract_spreads(event, match)
            totals = extract_totals(event)
            if not prices:
                return {
                    "found": False,
                    "source": "The Odds API",
                    "event_id": event.get("id"),
                    "event_title": f"{event.get('home_team')} vs {event.get('away_team')}",
                    "message": "找到赛事，但没有完整胜平负赔率。",
                    "asian_handicap": spreads,
                    "over_under": totals,
                    "raw_event": event,
                }
            return {
                "found": True,
                "home_win": prices["home_win"],
                "draw": prices["draw"],
                "away_win": prices["away_win"],
                "over_under_line": totals[0].get("line") if totals else None,
                "asian_handicap": spreads,
                "over_under": totals,
                "raw_probabilities": raw_probabilities(prices["home_win"], prices["draw"], prices["away_win"]),
                "implied_probabilities": implied_probabilities(prices["home_win"], prices["draw"], prices["away_win"]),
                "source": f"The Odds API / {bookmaker or 'Bookmaker'}",
                "event_title": f"{event.get('home_team')} vs {event.get('away_team')}",
                "event_id": event.get("id"),
                "message": "已强制刷新 The Odds API 胜平负、让球、大小球。",
                "cache": cache_metadata("fresh api response", sport_key, date_key, events),
                "request_headers": payload["request_headers"],
                "raw_event": event,
            }

    return {
        "found": False,
        "source": "The Odds API",
        "message": f"无法连接或未找到赛事：{last_error}" if last_error else "未找到赛事。",
        "asian_handicap": [],
        "over_under": [],
    }


def parse_api_football_market(response, bet_id):
    rows = []
    bookmaker_names = []
    for item in response:
        for bookmaker in item.get("bookmakers", []):
            bookmaker_id = bookmaker.get("id")
            bookmaker_name = bookmaker.get("name")
            if bookmaker_name:
                bookmaker_names.append(bookmaker_name)
            for bet in bookmaker.get("bets", []):
                if bet.get("id") != bet_id:
                    continue
                for value in bet.get("values", []):
                    odd = parse_odd(value.get("odd"))
                    if not odd:
                        continue
                    row = {
                        "bookmaker_id": bookmaker_id,
                        "bookmaker": bookmaker_name,
                        "market": bet.get("name"),
                        "odd": odd,
                    }
                    if bet_id == EXACT_SCORE_BET_ID:
                        row["score"] = value.get("value")
                    else:
                        row["value"] = value.get("value")
                    rows.append(row)
    return sorted(set(bookmaker_names)), rows


def fetch_api_football_fixture(match):
    team_errors = {}

    def resolve_fresh(team_name):
        attempted = []
        last_error = None
        for candidate in alias_candidates(team_name):
            attempted.append(candidate)
            teams = []
            for attempt in range(3):
                try:
                    teams = request_teams(candidate)
                    break
                except (RuntimeError, requests.RequestException) as error:
                    last_error = str(error)
                    if attempt == 2:
                        teams = []
            team = select_team_from_response(candidate, teams)
            if team:
                team["_resolver"] = {
                    "input": team_name,
                    "matched_query": candidate,
                    "matched_name": team.get("name"),
                    "team_id": team.get("id"),
                    "attempted": attempted,
                    "cache_status": "fresh api response",
                }
                return team, None
        return None, {
            "input": team_name,
            "attempted": attempted,
            "error": last_error or "API-Football 未返回国家队。",
        }

    home_team, home_error = resolve_fresh(match["home_en"])
    away_team, away_error = resolve_fresh(match["away_en"])
    if home_error:
        team_errors["home"] = home_error
    if away_error:
        team_errors["away"] = away_error
    if not home_team or not away_team:
        return home_team, away_team, None, f"未找到双方 Team ID。errors={team_errors}"

    response = request_json("/fixtures/headtohead", {"h2h": f"{home_team['id']}-{away_team['id']}"})
    candidates = []
    for item in response:
        league = item.get("league") or {}
        fixture = item.get("fixture") or {}
        teams = item.get("teams") or {}
        home_id = (teams.get("home") or {}).get("id")
        away_id = (teams.get("away") or {}).get("id")
        if {home_id, away_id} != {home_team["id"], away_team["id"]}:
            continue
        if league.get("season") == 2026 and "world cup" in normalize(league.get("name")):
            candidates.append(item)
        elif "2026-06-19" in str(fixture.get("date") or ""):
            candidates.append(item)

    selected = candidates[0] if candidates else (response[0] if response else None)
    if not selected:
        return home_team, away_team, None, "API-Football head-to-head 未返回对应 fixture。"
    return home_team, away_team, selected, "API-Football head-to-head 已返回 fixture。"


def fixture_summary_from_api(item):
    if not item:
        return None
    fixture = item.get("fixture") or {}
    league = item.get("league") or {}
    venue = fixture.get("venue") or {}
    return {
        "fixture_id": fixture.get("id"),
        "kickoff_utc": fixture.get("date"),
        "league_id": league.get("id"),
        "league": league.get("name"),
        "season": league.get("season"),
        "round": league.get("round"),
        "venue": venue.get("name"),
        "city": venue.get("city"),
        "status": (fixture.get("status") or {}).get("short"),
        "raw": item,
    }


def fetch_api_football_odds(fixture_id):
    if not fixture_id:
        return {
            "all_odds": api_error_payload("API-Football / All Odds", "缺少 fixture_id。"),
            "asian_handicap": empty_asian_handicap_result("缺少 fixture_id。"),
            "correct_score": empty_correct_score_result("缺少 fixture_id。"),
        }

    result = {}
    try:
        result["all_odds"] = {
            "found": True,
            "source": "API-Football / All Odds",
            "response": request_json("/odds", {"fixture": fixture_id}),
        }
    except (requests.RequestException, RuntimeError) as error:
        result["all_odds"] = api_error_payload("API-Football / All Odds", error)

    for label, bet_id, empty_func in [
        ("asian_handicap", ASIAN_HANDICAP_BET_ID, empty_asian_handicap_result),
        ("correct_score", EXACT_SCORE_BET_ID, empty_correct_score_result),
    ]:
        try:
            response = request_json("/odds", {"fixture": fixture_id, "bet": bet_id})
            bookmakers, rows = parse_api_football_market(response, bet_id)
            if rows:
                market = {
                    "found": True,
                    "source": f"API-Football / {'Asian Handicap' if bet_id == ASIAN_HANDICAP_BET_ID else 'Exact Score'}",
                    "bookmakers": bookmakers,
                    "rows": rows,
                    "all_rows": rows,
                    "message": "强制刷新成功。",
                }
                write_api_football_market_cache(fixture_id, bet_id, market)
                result[label] = market
            else:
                result[label] = empty_func("API-Football 返回为空。")
        except (requests.RequestException, RuntimeError) as error:
            result[label] = empty_func(f"API-Football 请求失败：{error}")

    return result


def standing_for_fixture(schedule, fixture):
    group = (fixture or {}).get("group") or (fixture or {}).get("round") or ""
    standings = schedule.get("standings") or {}
    if not group:
        return None
    for key, rows in standings.items():
        if normalize(group) in normalize(key) or normalize(key) in normalize(group):
            return {"group": key, "rows": rows}
    return None


def asset_role(candidate):
    item_type = candidate.get("type")
    if item_type == "winner":
        return "主方向资产"
    if item_type == "handicap":
        return "方向增强资产"
    if item_type == "total":
        return "节奏资产"
    if item_type == "correct_score":
        return "收益放大资产"
    return "观察资产"


def portfolio_name(items):
    names = [item.get("name") for item in items if item.get("name")]
    return " + ".join(names[:4]) if names else "无推荐组合"


def build_portfolios(slots):
    recommended = [item for item in slots if item.get("recommended") and item.get("share", 0) > 0]
    recommended.sort(key=lambda item: item.get("share", 0), reverse=True)
    score_sorted = sorted([item for item in slots if item.get("recommended")], key=lambda item: item.get("score", 0), reverse=True)
    correct_scores = [item for item in score_sorted if item.get("type") == "correct_score"]
    non_correct = [item for item in score_sorted if item.get("type") != "correct_score"]
    portfolios = [
        {"rank": 1, "name": portfolio_name(recommended), "items": recommended},
        {"rank": 2, "name": portfolio_name(non_correct[:3] + correct_scores[:1]), "items": non_correct[:3] + correct_scores[:1]},
        {"rank": 3, "name": portfolio_name(correct_scores[:3] + non_correct[:1]), "items": correct_scores[:3] + non_correct[:1]},
    ]
    return portfolios


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--match", required=True)
    args = parser.parse_args()

    match = parse_match(args.match)
    print(f"Match: {match['home_en']} vs {match['away_en']}")
    print(f"Date: {args.date}")

    schedule, schedule_fixture = force_fetch_schedule(match)
    print(f"Schedule source: {schedule.get('source')} / {schedule.get('cache_status')}")
    print(f"Schedule fixture found: {bool(schedule_fixture)}")

    try:
        weather = weather_for_fixture(schedule_fixture) if schedule_fixture else {"available": False, "summary": "天气暂不可用"}
    except Exception as error:
        weather = {"available": False, "summary": "天气暂不可用", "message": str(error)}

    odds = fetch_the_odds_force(match, args.date)
    print(f"The Odds API found: {odds.get('found')} / {odds.get('message')}")
    print(f"The Odds API event: {odds.get('event_title')} / {odds.get('event_id')}")
    print(f"The Odds API spreads: {len(odds.get('asian_handicap') or [])}")
    print(f"The Odds API totals: {len(odds.get('over_under') or [])}")

    api_fixture_error = None
    try:
        home_team, away_team, api_fixture_raw, api_fixture_message = fetch_api_football_fixture(match)
    except Exception as error:
        home_team, away_team, api_fixture_raw, api_fixture_message = None, None, None, str(error)
        api_fixture_error = str(error)
    api_fixture = fixture_summary_from_api(api_fixture_raw)

    print("Team mapping:")
    for label, team in [("home", home_team), ("away", away_team)]:
        resolver = (team or {}).get("_resolver") or {}
        print(
            f"  {label}: input={resolver.get('input') or match.get(label + '_en')} "
            f"matched={resolver.get('matched_name') or (team or {}).get('name')} "
            f"id={(team or {}).get('id')}"
        )
    print(f"API-Football fixture message: {api_fixture_message}")
    print(f"API-Football fixture_id: {(api_fixture or {}).get('fixture_id')}")

    api_markets = fetch_api_football_odds((api_fixture or {}).get("fixture_id"))
    print(f"API-Football Asian Handicap: {api_markets['asian_handicap'].get('found')} rows={len(api_markets['asian_handicap'].get('rows') or [])}")
    print(f"API-Football Correct Score: {api_markets['correct_score'].get('found')} rows={len(api_markets['correct_score'].get('rows') or [])}")

    api_football_data = {
        "fixture": api_fixture,
        "home_team": home_team,
        "away_team": away_team,
        "asian_handicap": api_markets["asian_handicap"],
        "correct_score": api_markets["correct_score"],
        "all_odds": api_markets["all_odds"],
    }
    distribution = build_result_distribution(match, odds, {"found": False})
    slots = build_recommendation_slots(match, odds, api_football_data, {}, distribution)
    portfolios = build_portfolios(slots)
    market_candidates = build_market_candidates(match, odds, api_football_data)

    snapshot = {
        "snapshot_type": "pre_match",
        "match": match,
        "date": args.date,
        "created_at": datetime.now(LOCAL_TZ).isoformat(),
        "model_version": "v1.61",
        "schedule": {
            "source": schedule.get("source"),
            "updated_at": schedule.get("updated_at"),
            "cache_status": schedule.get("cache_status"),
            "fixture": schedule_fixture,
            "standings": standing_for_fixture(schedule, schedule_fixture),
        },
        "fixture": {
            "api_football": api_fixture,
            "api_football_message": api_fixture_message,
            "api_football_error": api_fixture_error,
        },
        "weather": weather,
        "team_mapping": {
            "home": home_team,
            "away": away_team,
        },
        "odds": {
            "the_odds_api": odds,
            "api_football": api_markets,
        },
        "probability_distribution": distribution,
        "market_candidates": market_candidates,
        "recommendation_slots": slots,
        "portfolios": portfolios,
        "asset_roles": [
            {
                "name": item.get("name"),
                "type": item.get("type"),
                "role": asset_role(item),
                "standard_odds": item.get("standard_odds"),
                "score": item.get("score"),
                "share": item.get("share"),
            }
            for item in slots
            if item.get("type") != "empty"
        ],
        "risk_paths": distribution.get("risk_exposure"),
        "top_probable_outcomes": distribution.get("rows"),
    }

    history_dir = ROOT / "data" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    output_path = history_dir / "2026_06_19_Scotland_Morocco_pre.json"
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(snapshot, file, ensure_ascii=False, indent=2)

    print(f"Snapshot: {output_path}")
    print("Recommended portfolio:")
    for item in portfolios[0]["items"]:
        print(
            f"  - {item.get('name')} | share={item.get('share', 0):.2%} "
            f"odds={item.get('standard_odds')} score={item.get('score')}"
        )
    print("Top probable outcomes:")
    for row in (distribution.get("rows") or [])[:5]:
        print(f"  - {row.get('label')}: {row.get('probability', 0):.1%}")


if __name__ == "__main__":
    main()
