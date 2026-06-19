import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from modules.schedule_client import fixture_local_datetime


LOCAL_TZ = ZoneInfo("Asia/Shanghai")
ROOT = Path(__file__).resolve().parents[1]
DB_ROOT = ROOT / "data" / "worldcup2026"


def slug(value):
    return re.sub(r"[^A-Za-z0-9]+", "_", str(value or "")).strip("_")


def match_date_key(selected_fixture=None):
    if selected_fixture:
        local_time = fixture_local_datetime(selected_fixture)
        if local_time:
            return local_time.strftime("%Y_%m_%d")
    return datetime.now(LOCAL_TZ).strftime("%Y_%m_%d")


def match_dir(match, selected_fixture=None):
    date_key = match_date_key(selected_fixture)
    home = slug(match.get("home_en") or match.get("home_cn"))
    away = slug(match.get("away_en") or match.get("away_cn"))
    return DB_ROOT / f"{date_key}_{home}_{away}"


def read_json(path):
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_match_database(match, selected_fixture=None):
    base = match_dir(match, selected_fixture)
    if not base.exists():
        return None
    payload = {
        "base_dir": base,
        "fixture": read_json(base / "fixture.json"),
        "odds": read_json(base / "odds.json"),
        "lineups": read_json(base / "lineups.json"),
        "injuries": read_json(base / "injuries.json"),
        "players": read_json(base / "players.json"),
        "events": read_json(base / "events.json"),
        "match_stats": read_json(base / "match_stats.json"),
        "team_stats": read_json(base / "team_stats.json"),
        "pre_match": read_json(base / "pre_match.json"),
        "post_match": read_json(base / "post_match.json"),
    }
    payload["completeness"] = data_completeness(payload)
    return payload


def db_odds(db):
    odds = (db or {}).get("odds") or {}
    result = odds.get("the_odds_api") or {}
    if result:
        result = dict(result)
        result["cache"] = result.get("cache") or {
            "source": "History Database",
            "path": str(((db or {}).get("base_dir") or Path("")) / "odds.json"),
        }
    return result


def db_api_football_data(db):
    fixture_payload = (db or {}).get("fixture") or {}
    odds_payload = (db or {}).get("odds") or {}
    api_markets = odds_payload.get("api_football") or {}
    return {
        "fixture_result": {
            "fixture": fixture_payload.get("api_football_fixture"),
            "home_team": fixture_payload.get("home_team"),
            "away_team": fixture_payload.get("away_team"),
            "message": fixture_payload.get("api_football_fixture_message"),
            "cache_status": "History Database",
        },
        "fixture": fixture_payload.get("api_football_fixture"),
        "home_team": fixture_payload.get("home_team"),
        "away_team": fixture_payload.get("away_team"),
        "asian_handicap": api_markets.get("asian_handicap"),
        "correct_score": api_markets.get("correct_score"),
        "all_odds": api_markets.get("all_odds"),
        "lineups": ((db or {}).get("lineups") or {}).get("response") or [],
        "injuries": ((db or {}).get("injuries") or {}).get("response") or [],
        "home_recent": ((db or {}).get("team_stats") or {}).get("home_recent") or [],
        "away_recent": ((db or {}).get("team_stats") or {}).get("away_recent") or [],
        "source": "History Database",
    }


def truthy_market(result, rows_key="rows"):
    if not isinstance(result, dict):
        return False
    if result.get("found"):
        return True
    return bool(result.get(rows_key))


def data_completeness(db):
    odds = ((db or {}).get("odds") or {}).get("the_odds_api") or {}
    api = ((db or {}).get("odds") or {}).get("api_football") or {}
    fixture = (db or {}).get("fixture") or {}
    checks = [
        ("Fixture", bool(fixture.get("api_football_fixture"))),
        ("Winner Odds", bool(odds.get("found"))),
        ("Asian Handicap", truthy_market(api.get("asian_handicap"))),
        ("Totals", bool(odds.get("over_under"))),
        ("Correct Score", truthy_market(api.get("correct_score"))),
        ("Lineups", bool(((db or {}).get("lineups") or {}).get("response"))),
        ("Injuries", ((db or {}).get("injuries") or {}).get("ok") is True),
        ("Players", bool((((db or {}).get("players") or {}).get("fixture_players") or {}).get("response"))),
        ("Match Stats", bool(((db or {}).get("match_stats") or {}).get("response"))),
    ]
    passed = sum(1 for _, ok in checks if ok)
    return {
        "score": round((passed / len(checks)) * 100) if checks else 0,
        "checks": [{"item": item, "ok": ok} for item, ok in checks],
    }
