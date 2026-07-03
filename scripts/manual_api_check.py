"""
Manual API-Football diagnostic script.

This file is intentionally not named test_*.py so pytest does not collect it.
Run it only when the user explicitly authorizes a real API-Football diagnostic.
It may perform keyed API calls and must not be part of normal CI validation.
"""

import json

from modules.api_client import load_api_key
from modules.odds_client import (
    fetch_injuries_for_fixture,
    fetch_lineups_for_fixture,
    request_json,
    search_team,
)


HOME_TEAM = "Argentina"
AWAY_TEAM = "Algeria"
MATCH_DATE = "2026-06-17"


def compact(value, limit=1600):
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...省略..."


def section(title, success, sample=None, note=None):
    print("\n" + "=" * 80)
    print(title)
    print("结果:", "成功" if success else "失败")
    if note:
        print("说明:", note)
    if sample is not None:
        print("返回数据样例:")
        print(compact(sample))


def find_fixture_by_date(home_team, away_team, match_date):
    fixtures = request_json("/fixtures", {"date": match_date})

    for item in fixtures:
        teams = item.get("teams", {})
        home = teams.get("home", {})
        away = teams.get("away", {})

        direct = home.get("id") == home_team.get("id") and away.get("id") == away_team.get("id")
        reversed_match = home.get("id") == away_team.get("id") and away.get("id") == home_team.get("id")

        if direct or reversed_match:
            return item, fixtures

    return None, fixtures


def fetch_odds_for_fixture(fixture_id):
    return request_json("/odds", {"fixture": fixture_id})


def main():
    key = load_api_key()
    section(
        "0. API Key读取",
        bool(key),
        {"loaded": bool(key), "length": len(key) if key else 0},
        "不会打印 API Key 原文。",
    )

    argentina = None
    try:
        argentina = search_team(HOME_TEAM)
        section("1. 查询 Argentina", bool(argentina), argentina)
    except Exception as error:
        section("1. 查询 Argentina", False, note=str(error))

    algeria = None
    try:
        algeria = search_team(AWAY_TEAM)
        section("2. 查询 Algeria", bool(algeria), algeria)
    except Exception as error:
        section("2. 查询 Algeria", False, note=str(error))

    fixture = None
    fixtures_response = None
    try:
        if argentina and algeria:
            fixture, fixtures_response = find_fixture_by_date(argentina, algeria, MATCH_DATE)
            if fixture:
                fixture_info = fixture.get("fixture", {})
                league_info = fixture.get("league", {})
                section(
                    f"3. 查找 {MATCH_DATE} Argentina vs Algeria fixture",
                    True,
                    fixture,
                    (
                        f"fixture_id={fixture_info.get('id')}; "
                        f"league_id={league_info.get('id')}; "
                        f"season={league_info.get('season')}; "
                        f"比赛时间={fixture_info.get('date')}"
                    ),
                )
            else:
                section(
                    f"3. 查找 {MATCH_DATE} Argentina vs Algeria fixture",
                    False,
                    fixtures_response[:8] if fixtures_response else fixtures_response,
                    "该日期返回的 fixtures 中没有找到 Argentina vs Algeria。",
                )
        else:
            section("3. 查找 fixture", False, note="Argentina 或 Algeria 查询失败。")
    except Exception as error:
        section("3. 查找 fixture", False, note=str(error))

    if not fixture:
        section("4. 查询 odds", False, note="没有 fixture_id，跳过 odds 查询。")
        section("5. 查询 lineups", False, note="没有 fixture_id，跳过 lineups 查询。")
        section("6. 查询 injuries", False, note="没有 fixture_id，跳过 injuries 查询。")
        return

    fixture_id = fixture["fixture"]["id"]

    try:
        odds = fetch_odds_for_fixture(fixture_id)
        section(
            "4. 查询 odds",
            bool(odds),
            odds[:2] if odds else odds,
            f"fixture_id={fixture_id}; 返回数量={len(odds)}",
        )
    except Exception as error:
        section("4. 查询 odds", False, note=str(error))

    try:
        lineups = fetch_lineups_for_fixture(fixture_id)
        section(
            "5. 查询 lineups",
            bool(lineups),
            lineups[:2] if lineups else lineups,
            f"fixture_id={fixture_id}; 返回数量={len(lineups)}",
        )
    except Exception as error:
        section("5. 查询 lineups", False, note=str(error))

    try:
        injuries = fetch_injuries_for_fixture(fixture_id)
        section(
            "6. 查询 injuries",
            injuries is not None,
            injuries[:5] if injuries else injuries,
            f"fixture_id={fixture_id}; 返回数量={len(injuries)}",
        )
    except Exception as error:
        section("6. 查询 injuries", False, note=str(error))


if __name__ == "__main__":
    main()
