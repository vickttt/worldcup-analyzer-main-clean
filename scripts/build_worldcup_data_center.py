import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.match_parser import parse_match
from modules.odds_client import request_json
from modules.result_distribution import build_result_distribution
from modules.schedule_client import fetch_world_cup_schedule
from modules.user_odds import build_market_candidates, build_recommendation_slots
from modules.worldcup_db import data_completeness, load_match_database
from scripts.refresh_match_prematch_snapshot import (
    asset_role,
    build_portfolios,
    fetch_api_football_fixture,
    fetch_api_football_odds,
    fetch_the_odds_force,
    fixture_summary_from_api,
    force_fetch_schedule,
    standing_for_fixture,
)


LOCAL_TZ = ZoneInfo("Asia/Shanghai")
MATCHES = [
    {"source_id": "66456944", "date": "2026-06-19", "match": "USA vs Australia"},
    {"source_id": "66456934", "date": "2026-06-19", "match": "Scotland vs Morocco"},
    {"source_id": "66456932", "date": "2026-06-19", "match": "Brazil vs Haiti"},
    {"source_id": "66456946", "date": "2026-06-19", "match": "Turkey vs Paraguay"},
]
HISTORY_MATCHES = [
    {"source_id": "17", "date": "2026-06-16", "match": "France vs Senegal"},
    {"source_id": "21", "date": "2026-06-17", "match": "Portugal vs Democratic Republic of the Congo"},
    {"source_id": "22", "date": "2026-06-17", "match": "England vs Croatia"},
    {"source_id": "26", "date": "2026-06-18", "match": "Switzerland vs Bosnia and Herzegovina"},
]
KNOWN_API_FOOTBALL_FIXTURES = {
    "66456944": 1489391,
    "66456934": 1489390,
    "66456932": 1489389,
    "66456946": 1539006,
    "17": 1489383,
    "21": 1539003,
    "22": 1489384,
    "26": 1539005,
}


def slug(value):
    return (
        str(value)
        .replace("&", "and")
        .replace("/", "_")
        .replace(" ", "_")
        .replace("-", "_")
        .replace("__", "_")
    )


def match_dir(date_key, match):
    path = ROOT / "data" / "worldcup2026" / f"{date_key.replace('-', '_')}_{slug(match['home_en'])}_{slug(match['away_en'])}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path):
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def existing_fixture_for_match(date_key, match):
    path = match_dir(date_key, match) / "fixture.json"
    payload = read_json(path) or {}
    fixture = payload.get("api_football_fixture")
    if fixture:
        return payload.get("home_team"), payload.get("away_team"), fixture, "History Database fixture fallback"
    return None, None, None, None


def known_fixture_summary(entry):
    fixture_id = KNOWN_API_FOOTBALL_FIXTURES.get(str(entry.get("source_id")))
    if not fixture_id:
        return None
    return {
        "fixture_id": fixture_id,
        "kickoff_utc": None,
        "league_id": None,
        "league": "World Cup",
        "season": 2026,
        "round": None,
        "venue": None,
        "city": None,
        "status": None,
        "raw": None,
        "source": "Known verified API-Football fixture fallback",
    }


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def fetch_log_dir():
    path = ROOT / "data" / "fetch_logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def fetch_status_rows(match, fixture_id, odds, api_markets, fixture_assets):
    return [
        {
            "source": "The Odds API",
            "endpoint": "/v4/sports/{sport_key}/odds?markets=h2h,spreads,totals",
            "dataset": "Winner Odds / Totals",
            "success": bool(odds.get("found")),
            "records": len(odds.get("over_under") or []),
            "empty": not bool(odds.get("found")),
            "message": odds.get("message") or odds.get("event_title"),
        },
        {
            "source": "API-Football",
            "endpoint": f"/odds?fixture={fixture_id}&bet=4",
            "dataset": "Asian Handicap",
            "success": bool((api_markets.get("asian_handicap") or {}).get("found")),
            "records": len((api_markets.get("asian_handicap") or {}).get("rows") or []),
            "empty": not bool((api_markets.get("asian_handicap") or {}).get("rows")),
            "message": (api_markets.get("asian_handicap") or {}).get("message"),
        },
        {
            "source": "API-Football",
            "endpoint": f"/odds?fixture={fixture_id}&bet=10",
            "dataset": "Correct Score",
            "success": bool((api_markets.get("correct_score") or {}).get("found")),
            "records": len((api_markets.get("correct_score") or {}).get("rows") or []),
            "empty": not bool((api_markets.get("correct_score") or {}).get("rows")),
            "message": (api_markets.get("correct_score") or {}).get("message"),
        },
        {
            "source": "API-Football",
            "endpoint": f"/fixtures/lineups?fixture={fixture_id}",
            "dataset": "Lineups",
            "success": bool((fixture_assets.get("lineups") or {}).get("ok")),
            "records": len((fixture_assets.get("lineups") or {}).get("response") or []),
            "empty": not bool((fixture_assets.get("lineups") or {}).get("response")),
            "message": (fixture_assets.get("lineups") or {}).get("error"),
        },
        {
            "source": "API-Football",
            "endpoint": f"/injuries?fixture={fixture_id}",
            "dataset": "Injuries",
            "success": bool((fixture_assets.get("injuries") or {}).get("ok")),
            "records": len((fixture_assets.get("injuries") or {}).get("response") or []),
            "empty": not bool((fixture_assets.get("injuries") or {}).get("response")),
            "message": (fixture_assets.get("injuries") or {}).get("error"),
        },
        {
            "source": "API-Football",
            "endpoint": f"/fixtures/statistics?fixture={fixture_id}",
            "dataset": "Match Stats",
            "success": bool((fixture_assets.get("match_stats") or {}).get("ok")),
            "records": len((fixture_assets.get("match_stats") or {}).get("response") or []),
            "empty": not bool((fixture_assets.get("match_stats") or {}).get("response")),
            "message": (fixture_assets.get("match_stats") or {}).get("error"),
        },
        {
            "source": "API-Football",
            "endpoint": f"/fixtures/players?fixture={fixture_id}",
            "dataset": "Players",
            "success": bool((fixture_assets.get("players") or {}).get("ok")),
            "records": len((fixture_assets.get("players") or {}).get("response") or []),
            "empty": not bool((fixture_assets.get("players") or {}).get("response")),
            "message": (fixture_assets.get("players") or {}).get("error"),
        },
    ]


def safe_api(path, params):
    try:
        return {"ok": True, "response": request_json(path, params), "error": None}
    except (requests.RequestException, RuntimeError) as error:
        return {"ok": False, "response": [], "error": str(error)}


def fetch_team_assets(team):
    if not team or not team.get("id"):
        return {"squad": {"ok": False, "response": [], "error": "missing team_id"}}
    return {
        "squad": safe_api("/players/squads", {"team": team["id"]}),
        "team_id": team.get("id"),
        "name": team.get("name"),
    }


def fetch_fixture_assets(fixture_id):
    if not fixture_id:
        empty = {"ok": False, "response": [], "error": "missing fixture_id"}
        return {
            "lineups": empty,
            "injuries": empty,
            "events": empty,
            "match_stats": empty,
            "players": empty,
        }
    return {
        "lineups": safe_api("/fixtures/lineups", {"fixture": fixture_id}),
        "injuries": safe_api("/injuries", {"fixture": fixture_id}),
        "events": safe_api("/fixtures/events", {"fixture": fixture_id}),
        "match_stats": safe_api("/fixtures/statistics", {"fixture": fixture_id}),
        "players": safe_api("/fixtures/players", {"fixture": fixture_id}),
    }


def build_match_database(entry):
    match = parse_match(entry["match"])
    print(f"\n=== {entry['source_id']} {match['home_en']} vs {match['away_en']} ===")

    schedule, schedule_fixture = force_fetch_schedule(match)
    odds = fetch_the_odds_force(match, entry["date"])

    try:
        home_team, away_team, api_fixture_raw, api_fixture_message = fetch_api_football_fixture(match)
    except Exception as error:
        home_team, away_team, api_fixture_raw, api_fixture_message = None, None, None, str(error)

    api_fixture = fixture_summary_from_api(api_fixture_raw)
    if not api_fixture:
        cached_home, cached_away, cached_fixture, cached_message = existing_fixture_for_match(entry["date"], match)
        if cached_fixture:
            home_team = home_team or cached_home
            away_team = away_team or cached_away
            api_fixture = cached_fixture
            api_fixture_message = f"{api_fixture_message}; {cached_message}"
    if not api_fixture:
        known_fixture = known_fixture_summary(entry)
        if known_fixture:
            api_fixture = known_fixture
            api_fixture_message = f"{api_fixture_message}; Known verified fixture fallback"
    fixture_id = (api_fixture or {}).get("fixture_id")
    api_markets = fetch_api_football_odds(fixture_id)
    fixture_assets = fetch_fixture_assets(fixture_id)

    api_football_data = {
        "fixture": api_fixture,
        "home_team": home_team,
        "away_team": away_team,
        "asian_handicap": api_markets["asian_handicap"],
        "correct_score": api_markets["correct_score"],
        "all_odds": api_markets["all_odds"],
        "lineups": fixture_assets["lineups"].get("response") or [],
        "injuries": fixture_assets["injuries"].get("response") or [],
    }
    fetch_rows = fetch_status_rows(match, fixture_id, odds, api_markets, fixture_assets)

    distribution = build_result_distribution(match, odds, {"found": False})
    recommendation_slots = build_recommendation_slots(match, odds, api_football_data, {}, distribution)
    portfolios = build_portfolios(recommendation_slots)
    candidates = build_market_candidates(match, odds, api_football_data)
    assets = [
        {
            "name": item.get("name"),
            "type": item.get("type"),
            "role": asset_role(item),
            "standard_odds": item.get("standard_odds"),
            "score": item.get("score"),
            "share": item.get("share"),
        }
        for item in recommendation_slots
        if item.get("type") != "empty"
    ]

    base = match_dir(entry["date"], match)
    meta = {
        "source_id": entry["source_id"],
        "match": match,
        "created_at": datetime.now(LOCAL_TZ).isoformat(),
        "schedule_source": schedule.get("source"),
        "schedule_cache_status": schedule.get("cache_status"),
        "api_football_fixture_message": api_fixture_message,
    }

    write_json(base / "fixture.json", {
        **meta,
        "schedule_fixture": schedule_fixture,
        "api_football_fixture": api_fixture,
        "home_team": home_team,
        "away_team": away_team,
        "standings": standing_for_fixture(schedule, schedule_fixture),
    })
    write_json(base / "odds.json", {
        **meta,
        "the_odds_api": odds,
        "api_football": api_markets,
    })
    write_json(base / "lineups.json", {**meta, **fixture_assets["lineups"]})
    write_json(base / "injuries.json", {**meta, **fixture_assets["injuries"]})
    write_json(base / "events.json", {**meta, **fixture_assets["events"]})
    write_json(base / "match_stats.json", {**meta, **fixture_assets["match_stats"]})
    write_json(base / "players.json", {
        **meta,
        "fixture_players": fixture_assets["players"],
        "home_team_assets": fetch_team_assets(home_team),
        "away_team_assets": fetch_team_assets(away_team),
    })
    write_json(base / "team_stats.json", {
        **meta,
        "standings": standing_for_fixture(schedule, schedule_fixture),
        "home_recent": [],
        "away_recent": [],
    })
    write_json(base / "pre_match.json", {
        **meta,
        "model_version": "v1.61",
        "probability_distribution": distribution,
        "strategy_candidates": candidates,
        "recommendation_slots": recommendation_slots,
        "portfolios": portfolios,
        "asset_roles": assets,
        "risk_paths": distribution.get("risk_exposure"),
        "top_probable_outcomes": distribution.get("rows"),
    })
    write_json(base / "post_match.json", {
        **meta,
        "status": "pending_post_match" if not (schedule_fixture or {}).get("post_match") else "available",
        "post_match": (schedule_fixture or {}).get("post_match"),
    })

    print(f"Directory: {base}")
    print(f"Schedule fixture: {(schedule_fixture or {}).get('fixture_id')} / API-Football fixture: {fixture_id}")
    print(f"The Odds API: found={odds.get('found')} spreads={len(odds.get('asian_handicap') or [])} totals={len(odds.get('over_under') or [])}")
    print(f"API-Football Asian: {api_markets['asian_handicap'].get('found')} rows={len(api_markets['asian_handicap'].get('rows') or [])}")
    print(f"API-Football Correct: {api_markets['correct_score'].get('found')} rows={len(api_markets['correct_score'].get('rows') or [])}")
    print(f"Lineups: {fixture_assets['lineups'].get('ok')} rows={len(fixture_assets['lineups'].get('response') or [])}")
    print(f"Injuries: {fixture_assets['injuries'].get('ok')} rows={len(fixture_assets['injuries'].get('response') or [])}")
    print(f"Recommended: {portfolios[0]['name'] if portfolios else '-'}")
    db = load_match_database(match, schedule_fixture)
    completeness = (db or {}).get("completeness") or {}
    return {
        "match": entry["match"],
        "directory": str(base),
        "schedule_fixture_id": (schedule_fixture or {}).get("fixture_id"),
        "api_football_fixture_id": fixture_id,
        "odds_found": odds.get("found"),
        "api_asian_rows": len(api_markets["asian_handicap"].get("rows") or []),
        "api_correct_rows": len(api_markets["correct_score"].get("rows") or []),
        "lineups_rows": len(fixture_assets["lineups"].get("response") or []),
        "injuries_rows": len(fixture_assets["injuries"].get("response") or []),
        "recommended": portfolios[0]["name"] if portfolios else None,
        "data_completeness": completeness.get("score"),
        "fetch_rows": fetch_rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scope",
        choices=["today", "history", "all"],
        default="today",
        help="today=2026-06-19 matches, history=priority finished matches, all=both",
    )
    args = parser.parse_args()

    entries = []
    if args.scope in {"today", "all"}:
        entries.extend(MATCHES)
    if args.scope in {"history", "all"}:
        entries.extend(HISTORY_MATCHES)

    summary = [build_match_database(entry) for entry in entries]
    summary_name = "history_backfill_summary" if args.scope == "history" else "2026_06_19_refresh_summary"
    if args.scope == "all":
        summary_name = "all_refresh_summary"
    out = ROOT / "data" / "worldcup2026" / f"{summary_name}.json"
    write_json(out, {"created_at": datetime.now(LOCAL_TZ).isoformat(), "matches": summary})
    log_path = fetch_log_dir() / f"{datetime.now(LOCAL_TZ).strftime('%Y%m%d_%H%M%S')}_{summary_name}.json"
    write_json(log_path, {
        "created_at": datetime.now(LOCAL_TZ).isoformat(),
        "scope": args.scope,
        "mode": "Terminal Fetch Mode",
        "matches": summary,
    })
    print(f"\nSummary: {out}")
    print(f"Fetch Log: {log_path}")


if __name__ == "__main__":
    main()
