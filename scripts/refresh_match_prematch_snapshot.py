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
from modules.fixture_id_mapper import FixtureIDMapper
from modules.odds_client import (
    ASIAN_HANDICAP_BET_ID,
    EXACT_SCORE_BET_ID,
    empty_asian_handicap_result,
    empty_correct_score_result,
    fetch_odds,
    parse_odd,
    request_json,
    write_api_football_market_cache,
)
from modules.result_distribution import build_result_distribution
from modules.schedule_client import fetch_world_cup_schedule, fixture_local_datetime
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


def match_with_fixture_context(match, fixture):
    if not fixture:
        return match
    enriched = dict(match)
    fixture_source = fixture.get("source")
    fixture_id = fixture.get("fixture_id")
    enriched.update({
        "schedule_fixture_id": fixture_id,
        "schedule_source": fixture_source,
        "fixture_source": fixture_source,
        "fixture_home_team": fixture.get("home_team") or {},
        "fixture_away_team": fixture.get("away_team") or {},
        "fixture_kickoff_utc": fixture.get("kickoff_utc"),
        "fixture_league_name": fixture.get("league_name"),
        "fixture_round": fixture.get("round"),
    })
    if fixture_source == "API-Football":
        enriched["fixture_id"] = fixture_id
        enriched["api_football_fixture_id"] = fixture_id
    return enriched


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


def fetch_api_football_winner_totals(match, date_key=None):
    result = fetch_odds(match, date_key, "api_football_snapshot_refresh")
    result["odds_provider"] = "API-Football"
    result["asian_handicap"] = result.get("asian_handicap") or []
    result["over_under"] = result.get("over_under") or []
    return result


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


def fetch_api_football_fixture(match, date_key=None):
    result = FixtureIDMapper.get_result(match)
    fixture = result.get("fixture") or {}
    raw = fixture.get("raw")
    if not fixture.get("id") or not raw:
        return (
            result.get("home_team"),
            result.get("away_team"),
            None,
            result.get("message") or "FixtureIDMapper 未返回 API-Football fixture。",
        )
    return (
        result.get("home_team"),
        result.get("away_team"),
        raw,
        result.get("message") or "FixtureIDMapper 已返回 API-Football fixture。",
    )


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
    market_match = match_with_fixture_context(match, schedule_fixture)
    print(f"Schedule source: {schedule.get('source')} / {schedule.get('cache_status')}")
    print(f"Schedule fixture found: {bool(schedule_fixture)}")

    try:
        weather = weather_for_fixture(schedule_fixture) if schedule_fixture else {"available": False, "summary": "天气暂不可用"}
    except Exception as error:
        weather = {"available": False, "summary": "天气暂不可用", "message": str(error)}

    odds = fetch_api_football_winner_totals(market_match, args.date)
    print(f"API-Football winner odds found: {odds.get('found')} / {odds.get('message')}")
    print(f"API-Football event: {odds.get('event_title')} / {odds.get('event_id')}")
    print(f"API-Football spreads: {len(odds.get('asian_handicap') or [])}")
    print(f"API-Football totals: {len(odds.get('over_under') or [])}")

    api_fixture_error = None
    try:
        home_team, away_team, api_fixture_raw, api_fixture_message = fetch_api_football_fixture(market_match)
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
            "api_football_winner_totals": odds,
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
    output_path = history_dir / (
        f"{args.date.replace('-', '_')}_{match['home_en'].replace(' ', '_')}_{match['away_en'].replace(' ', '_')}_pre.json"
        .replace("&", "and")
        .replace("/", "_")
    )
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
