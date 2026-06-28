import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from modules.schedule_client import fixture_local_datetime


LOCAL_TZ = ZoneInfo("Asia/Shanghai")
ROOT = Path(__file__).resolve().parents[1]
DB_ROOT = ROOT / "data" / "worldcup2026"
INDEX_PATH = DB_ROOT / "index.json"


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


def match_pair_suffix(match):
    home = slug(match.get("home_en") or match.get("home_cn"))
    away = slug(match.get("away_en") or match.get("away_cn"))
    return f"{home}_{away}"


def database_fixture_datetime(path):
    payload = read_json(path / "fixture.json") or {}
    fixture = payload.get("api_football_fixture") or {}
    raw = fixture.get("raw") or {}
    kickoff = fixture.get("kickoff_utc") or ((raw.get("fixture") or {}).get("date"))
    if not kickoff:
        return None
    try:
        return datetime.fromisoformat(str(kickoff).replace("Z", "+00:00")).astimezone(LOCAL_TZ)
    except ValueError:
        return None


def match_dir_sort_key(path, selected_fixture=None):
    selected_time = fixture_local_datetime(selected_fixture) if selected_fixture else None
    db_time = database_fixture_datetime(path)
    if selected_time and db_time:
        return (0, abs((db_time - selected_time).total_seconds()))
    return (1, -path.stat().st_mtime)


def candidate_match_dirs(match, selected_fixture=None):
    exact = match_dir(match, selected_fixture)
    candidates = [exact]

    suffix = match_pair_suffix(match)
    if DB_ROOT.exists() and suffix:
        for path in sorted(DB_ROOT.glob(f"*_{suffix}"), key=lambda item: match_dir_sort_key(item, selected_fixture)):
            if path not in candidates:
                candidates.append(path)

    return candidates


def read_json(path):
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def indexed_match_dir(match, selected_fixture=None):
    index = read_json(INDEX_PATH) or {}
    items = index.get("matches") or []
    fixture_id = str((selected_fixture or {}).get("fixture_id") or "")
    home = slug(match.get("home_en") or match.get("home_cn"))
    away = slug(match.get("away_en") or match.get("away_cn"))
    date_key = match_date_key(selected_fixture)
    for item in items:
        if fixture_id and str(item.get("fixture_id") or "") == fixture_id:
            path = ROOT / str(item.get("database_dir") or "")
            if path.exists():
                return path
        item_home = slug(item.get("home"))
        item_away = slug(item.get("away"))
        item_date = str(item.get("date") or "").replace("-", "_")
        if item_date == date_key and item_home == home and item_away == away:
            path = ROOT / str(item.get("database_dir") or "")
            if path.exists():
                return path
    return None


def parse_price(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 1 else None


def raw_probabilities(home_win, draw, away_win):
    return {
        "home_win": 1 / home_win,
        "draw": 1 / draw,
        "away_win": 1 / away_win,
    }


def implied_probabilities(home_win, draw, away_win):
    raw = raw_probabilities(home_win, draw, away_win)
    total = sum(raw.values())
    return {key: value / total for key, value in raw.items()}


def parse_api_football_winner_and_totals(api_football):
    response = ((api_football or {}).get("all_odds") or {}).get("response") or []
    winner = None
    totals = []
    winner_bookmaker = None

    for item in response:
        for bookmaker in item.get("bookmakers", []):
            bookmaker_name = bookmaker.get("name")
            for bet in bookmaker.get("bets", []):
                bet_id = bet.get("id")
                if bet_id == 1 and not winner:
                    prices = {}
                    for value in bet.get("values", []):
                        label = str(value.get("value") or "").strip().lower()
                        odd = parse_price(value.get("odd"))
                        if label == "home":
                            prices["home_win"] = odd
                        elif label == "draw":
                            prices["draw"] = odd
                        elif label == "away":
                            prices["away_win"] = odd
                    if all(prices.get(key) for key in ["home_win", "draw", "away_win"]):
                        winner = prices
                        winner_bookmaker = bookmaker_name

                if bet_id == 5:
                    by_line = {}
                    for value in bet.get("values", []):
                        label = str(value.get("value") or "").strip()
                        odd = parse_price(value.get("odd"))
                        parts = label.split()
                        if len(parts) != 2 or not odd:
                            continue
                        side, line_text = parts
                        try:
                            line = float(line_text)
                        except ValueError:
                            continue
                        row = by_line.setdefault(line, {"line": line, "bookmaker": bookmaker_name})
                        if side.lower() == "over":
                            row["over_odds"] = odd
                        elif side.lower() == "under":
                            row["under_odds"] = odd
                    totals.extend(
                        row for row in by_line.values()
                        if row.get("over_odds") and row.get("under_odds")
                    )

    if not winner:
        return None
    return {
        **winner,
        "over_under_line": totals[0].get("line") if totals else None,
        "asian_handicap": [],
        "over_under": totals,
        "raw_probabilities": raw_probabilities(winner["home_win"], winner["draw"], winner["away_win"]),
        "implied_probabilities": implied_probabilities(winner["home_win"], winner["draw"], winner["away_win"]),
        "source": f"API-Football / {winner_bookmaker or 'All Odds'}",
        "event_title": None,
        "event_id": None,
        "message": "已从 API-Football All Odds 读取胜平负和大小球。",
        "found": True,
    }


def load_match_database(match, selected_fixture=None, full=True):
    base = indexed_match_dir(match, selected_fixture)
    if not base:
        base = next((path for path in candidate_match_dirs(match, selected_fixture) if path.exists()), None)
    if not base:
        return None
    payload = {
        "base_dir": base,
        "fixture": read_json(base / "fixture.json"),
        "odds": read_json(base / "odds.json"),
        "lineups": read_json(base / "lineups.json"),
        "injuries": read_json(base / "injuries.json"),
        "team_stats": read_json(base / "team_stats.json"),
    }
    if full:
        payload.update({
            "players": read_json(base / "players.json"),
            "events": read_json(base / "events.json"),
            "match_stats": read_json(base / "match_stats.json"),
            "pre_match": read_json(base / "pre_match.json"),
            "post_match": read_json(base / "post_match.json"),
        })
    payload["completeness"] = data_completeness(payload)
    return payload


def db_polymarket(db):
    base = (db or {}).get("base_dir")
    pre_match = (db or {}).get("pre_match")
    if pre_match is None and base:
        pre_match = read_json(Path(base) / "pre_match.json") or {}

    payload = (pre_match or {}).get("polymarket")
    if isinstance(payload, dict):
        result = dict(payload)
        result["cache"] = result.get("cache") or {
            "source": "World Cup Database pre_match",
            "path": str(Path(base) / "pre_match.json") if base else None,
        }
        return result

    return {
        "found": False,
        "home_win": None,
        "draw": None,
        "away_win": None,
        "volume": None,
        "liquidity": None,
        "event_title": None,
        "event_id": None,
        "event_url": None,
        "source": "Local cache",
        "message": "本地数据库没有 Polymarket 数据；为避免重复请求，本次未实时调用 API。",
        "cache": {
            "source": "World Cup Database",
            "path": str(Path(base) / "pre_match.json") if base else None,
        },
    }


def db_odds(db):
    odds = (db or {}).get("odds") or {}
    effective = odds.get("effective_winner_totals") or {}
    if effective.get("found"):
        result = dict(effective)
        result["cache"] = result.get("cache") or {
            "source": "World Cup Database effective_winner_totals",
            "path": str(((db or {}).get("base_dir") or Path("")) / "odds.json"),
        }
        return result
    result = odds.get("api_football_winner_totals") or {}
    api_fallback = parse_api_football_winner_and_totals(odds.get("api_football") or {})
    if not result.get("found") and api_fallback:
        result = api_fallback
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
    api_fixture = dict(fixture_payload.get("api_football_fixture") or {})
    if api_fixture.get("fixture_id") and not api_fixture.get("id"):
        api_fixture["id"] = api_fixture.get("fixture_id")
    return {
        "schedule_fixture": fixture_payload.get("schedule_fixture"),
        "fixture_result": {
            "fixture": api_fixture,
            "home_team": fixture_payload.get("home_team"),
            "away_team": fixture_payload.get("away_team"),
            "message": fixture_payload.get("api_football_fixture_message"),
            "cache_status": "History Database",
        },
        "fixture": api_fixture,
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
    odds = ((db or {}).get("odds") or {}).get("api_football_winner_totals") or {}
    api = ((db or {}).get("odds") or {}).get("api_football") or {}
    api_odds_fallback = parse_api_football_winner_and_totals(api)
    fixture = (db or {}).get("fixture") or {}
    checks = [
        ("Fixture", bool(fixture.get("api_football_fixture"))),
        ("Winner Odds", bool(odds.get("found")) or bool(api_odds_fallback)),
        ("Asian Handicap", truthy_market(api.get("asian_handicap"))),
        ("Totals", bool(odds.get("over_under")) or bool((api_odds_fallback or {}).get("over_under"))),
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
