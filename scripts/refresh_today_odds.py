from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.match_parser import parse_match
from modules.odds_client import (
    fetch_odds,
    fetch_asian_handicap_odds_for_fixture,
    fetch_correct_score_odds_for_fixture,
    find_fixture,
)
from modules.schedule_client import fetch_world_cup_schedule, fixture_local_datetime
from modules.team_resolver import alias_candidates


LOCAL_TZ = ZoneInfo("Asia/Shanghai")


def today_key():
    return datetime.now(LOCAL_TZ).strftime("%m-%d")


def match_text(fixture):
    home = (fixture.get("home_team") or {}).get("name") or ""
    away = (fixture.get("away_team") or {}).get("name") or ""
    return f"{home} vs {away}"


def match_with_fixture_context(match, fixture):
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


def fixture_date_key(fixture):
    local_time = fixture_local_datetime(fixture)
    if not local_time:
        return None
    return local_time.strftime("%m-%d")


def odds_date_key(fixture):
    kickoff = fixture.get("kickoff_utc")
    if not kickoff:
        return datetime.now(LOCAL_TZ).strftime("%Y-%m-%d")
    try:
        parsed = datetime.fromisoformat(str(kickoff).replace("Z", "+00:00"))
        return parsed.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%d")
    except ValueError:
        return datetime.now(LOCAL_TZ).strftime("%Y-%m-%d")


def today_fixtures(fixtures):
    key = today_key()
    return [fixture for fixture in fixtures if fixture_date_key(fixture) == key]


def resolver_summary(match):
    return {
        "home": alias_candidates(match["home_en"])[:6],
        "away": alias_candidates(match["away_en"])[:6],
    }


def main():
    print(f"Project: {ROOT}")
    print(f"Today: {datetime.now(LOCAL_TZ).strftime('%Y-%m-%d %H:%M %Z')}")
    schedule = fetch_world_cup_schedule(force_refresh=True)
    fixtures = today_fixtures(schedule.get("fixtures") or [])
    print(
        "Schedule:",
        schedule.get("source"),
        schedule.get("updated_at"),
        schedule.get("cache_status"),
    )
    print(f"Today's matches: {len(fixtures)}")

    if not fixtures:
        print("No matches found for today.")
        return

    for index, fixture in enumerate(fixtures, start=1):
        text = match_text(fixture)
        print("=" * 80)
        print(f"{index}. {text}")
        print("Kickoff:", fixture.get("kickoff_utc"), "Local:", fixture_local_datetime(fixture))
        match = parse_match(text)
        market_match = match_with_fixture_context(match, fixture)
        print("Alias candidates:", resolver_summary(match))

        date_key = odds_date_key(fixture)
        odds = fetch_odds(market_match, date_key, "manual_refresh_today_24h")
        print(
            "API-Football Winner Odds:",
            "SUCCESS" if odds.get("found") else "FAILED",
            "| date_key=", date_key,
            "| event=", odds.get("event_title"),
            "| message=", odds.get("message"),
            "| cache=", odds.get("cache"),
        )
        print(
            "  Match Winner:",
            odds.get("home_win"),
            odds.get("draw"),
            odds.get("away_win"),
            "| Totals rows:",
            len(odds.get("over_under") or []),
        )

        try:
            fixture_result = find_fixture(market_match)
        except Exception as error:
            print("API-Football Fixture: FAILED | error=", error)
            continue
        api_fixture = fixture_result.get("fixture")
        print(
            "API-Football Fixture:",
            "SUCCESS" if api_fixture else "FAILED",
            "| fixture_id=", (api_fixture or {}).get("id"),
            "| message=", fixture_result.get("message"),
        )
        print(
            "  Teams:",
            (fixture_result.get("home_team") or {}).get("name"),
            (fixture_result.get("away_team") or {}).get("name"),
        )

        if not api_fixture:
            print("  Skipped API-Football markets because fixture was not found.")
            continue

        fixture_id = api_fixture.get("id")
        handicap = fetch_asian_handicap_odds_for_fixture(fixture_id)
        correct = fetch_correct_score_odds_for_fixture(fixture_id)
        print(
            "  Asian Handicap:",
            "SUCCESS" if handicap.get("found") else "FAILED",
            "| rows=", len(handicap.get("rows") or []),
            "| message=", handicap.get("message"),
            "| cache=", handicap.get("cache"),
        )
        print(
            "  Correct Score:",
            "SUCCESS" if correct.get("found") else "FAILED",
            "| rows=", len(correct.get("rows") or []),
            "| message=", correct.get("message"),
            "| cache=", correct.get("cache"),
        )


if __name__ == "__main__":
    main()
