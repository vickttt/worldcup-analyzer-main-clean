import json
from datetime import datetime, timezone

import requests

from modules.team_resolver import load_api_key, normalize_text, resolve_team


API_FOOTBALL_BASE = "https://v3.football.api-sports.io"
API_REQUEST_TIMEOUT = 6


def safe_json_preview(payload, max_chars=2000):
    text = json.dumps(payload, ensure_ascii=False, default=str)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "...[truncated]"


def parse_match_datetime(match):
    value = match.get("fixture_kickoff_utc") or match.get("kickoff_utc")
    if not value:
        return None
    text = str(value).strip()
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        pass
    for pattern in ("%m/%d/%Y %H:%M", "%m/%d/%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern)
        except ValueError:
            continue
    return None


def match_season(match):
    target = parse_match_datetime(match)
    if target:
        return target.year
    league_name = str(match.get("fixture_league_name") or "")
    for token in league_name.split():
        if token.isdigit() and len(token) == 4:
            return int(token)
    return None


def api_fixture_datetime(item):
    value = (item.get("fixture") or {}).get("date")
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
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


def candidate_score(item, home_team, away_team, match):
    if not fixture_matches(item, home_team, away_team):
        return None

    score = 1
    league = item.get("league") or {}
    target_season = match_season(match)
    target_datetime = parse_match_datetime(match)
    fixture_datetime = api_fixture_datetime(item)

    if league.get("id") == 1:
        score += 10
    if target_season and league.get("season") == target_season:
        score += 8
    if target_datetime and fixture_datetime and target_datetime.date() == fixture_datetime.date():
        score += 20
    if normalize_text(league.get("name") or "") == "world cup":
        score += 5

    return score


def select_best_fixture(items, home_team, away_team, match):
    scored = []
    for item in items or []:
        score = candidate_score(item, home_team, away_team, match)
        if score is not None:
            scored.append((score, item))
    if not scored:
        return None
    scored.sort(
        key=lambda pair: (
            pair[0],
            (api_fixture_datetime(pair[1]) or datetime.min.replace(tzinfo=timezone.utc)).timestamp(),
        ),
        reverse=True,
    )
    return scored[0][1]


class FixtureIDMapper:
    _cache = {}
    _result_cache = {}
    _stats = {
        "hits": 0,
        "misses": 0,
        "api_calls": 0,
        "head_to_head_calls": 0,
        "fixtures_search_calls": 0,
    }

    @classmethod
    def reset(cls):
        cls._cache = {}
        cls._result_cache = {}
        cls._stats = {
            "hits": 0,
            "misses": 0,
            "api_calls": 0,
            "head_to_head_calls": 0,
            "fixtures_search_calls": 0,
        }

    @classmethod
    def cache_key(cls, match):
        home = normalize_text(match.get("home_en") or match.get("home_cn") or "")
        away = normalize_text(match.get("away_en") or match.get("away_cn") or "")
        target = parse_match_datetime(match)
        date_key = target.date().isoformat() if target else str(match.get("fixture_kickoff_utc") or "")
        return home, away, date_key

    @classmethod
    def stats(cls):
        total = cls._stats["hits"] + cls._stats["misses"]
        hit_rate = cls._stats["hits"] / total if total else 0
        return {**cls._stats, "cache_size": len(cls._cache), "hit_rate": hit_rate}

    @classmethod
    def get(cls, match):
        key = cls.cache_key(match)
        if key in cls._cache:
            cls._stats["hits"] += 1
            result = cls._result_cache.get(key) or {}
            cls.log_result(match, result, "cache_hit")
            return cls._cache[key]

        cls._stats["misses"] += 1
        result = cls.resolve(match)
        fixture = result.get("fixture") or {}
        fixture_id = fixture.get("id")
        cls._result_cache[key] = result
        if fixture_id:
            cls._cache[key] = fixture_id
        cls.log_result(match, result, "cache_miss")
        return fixture_id

    @classmethod
    def get_result(cls, match):
        key = cls.cache_key(match)
        if key not in cls._result_cache:
            cls.get(match)
        return cls._result_cache.get(key) or {
            "fixture": None,
            "home_team": None,
            "away_team": None,
            "message": "未找到 API-Football fixture_id。",
        }

    @classmethod
    def prefetch(cls, matches):
        return [cls.get(match) for match in matches]

    @classmethod
    def resolve(cls, match):
        metadata_result = cls.from_metadata(match)
        if metadata_result:
            return metadata_result

        home_team = resolve_team(match["home_en"])
        away_team = resolve_team(match["away_en"])
        for label, team in [("home", home_team), ("away", away_team)]:
            resolver = (team or {}).get("_resolver") or {}
            print(
                "[FixtureIDMapper Team Resolver]",
                label,
                "input=", resolver.get("input") or match.get(f"{label}_en"),
                "matched=", resolver.get("matched_name"),
                "team_id=", resolver.get("team_id"),
            )

        if not home_team or not away_team:
            reason = (
                "未找到双方国家队信息："
                f"home={match.get('home_en')} resolved={bool(home_team)}, "
                f"away={match.get('away_en')} resolved={bool(away_team)}。"
            )
            print("[FixtureIDMapper Missing]", reason)
            return {
                "fixture": None,
                "home_team": home_team,
                "away_team": away_team,
                "message": reason,
                "mapping_reason": reason,
            }

        h2h_rows = cls.request_json("/fixtures/headtohead", {"h2h": f"{home_team['id']}-{away_team['id']}"})
        cls._stats["head_to_head_calls"] += 1
        item = select_best_fixture(h2h_rows, home_team, away_team, match)
        if item:
            fixture = fixture_from_response(item)
            return {
                "fixture": fixture,
                "home_team": home_team,
                "away_team": away_team,
                "competition_pair": item.get("league", {}),
                "message": "已通过 FixtureIDMapper head-to-head 找到 API-Football fixture_id。",
                "mapping_reason": "resolved via /fixtures/headtohead",
            }

        season = match_season(match)
        fixture_pool = []
        if season:
            for team in [home_team, away_team]:
                fixture_pool.extend(cls.request_json("/fixtures", {"team": team["id"], "league": 1, "season": season}))
                cls._stats["fixtures_search_calls"] += 1
        item = select_best_fixture(fixture_pool, home_team, away_team, match)
        if item:
            fixture = fixture_from_response(item)
            return {
                "fixture": fixture,
                "home_team": home_team,
                "away_team": away_team,
                "competition_pair": item.get("league", {}),
                "message": "已通过 FixtureIDMapper fixtures search 找到 API-Football fixture_id。",
                "mapping_reason": "resolved via /fixtures team/league/season search",
            }

        reason = (
            "未找到双方对应 API-Football fixture："
            f"home_id={home_team.get('id')} home={home_team.get('name')}, "
            f"away_id={away_team.get('id')} away={away_team.get('name')}。"
        )
        print("[FixtureIDMapper Missing]", reason)
        return {
            "fixture": None,
            "home_team": home_team,
            "away_team": away_team,
            "message": reason,
            "mapping_reason": reason,
        }

    @classmethod
    def from_metadata(cls, match):
        fixture_source = match.get("fixture_source") or match.get("schedule_source")
        schedule_fixture_id = match.get("schedule_fixture_id")
        api_football_fixture_id = match.get("api_football_fixture_id")

        if api_football_fixture_id:
            fixture_id = api_football_fixture_id
            source_note = "api_football_fixture_id"
        elif fixture_source == "API-Football" and schedule_fixture_id:
            fixture_id = schedule_fixture_id
            source_note = "selected fixture source is API-Football"
        else:
            if schedule_fixture_id:
                print(
                    "[FixtureIDMapper]",
                    "selected fixture id not used for API-Football odds;",
                    f"id={schedule_fixture_id}",
                    f"source={fixture_source or 'unknown'}",
                )
            return None

        home_team = match.get("fixture_home_team") or {}
        away_team = match.get("fixture_away_team") or {}
        return {
            "fixture": {
                "id": fixture_id,
                "name": f"{home_team.get('name') or match.get('home_en')} vs {away_team.get('name') or match.get('away_en')}",
                "home_team": home_team,
                "away_team": away_team,
                "raw": {
                    "fixture": {
                        "id": fixture_id,
                        "date": match.get("fixture_kickoff_utc"),
                    },
                    "league": {
                        "name": match.get("fixture_league_name"),
                        "round": match.get("fixture_round"),
                    },
                },
            },
            "home_team": home_team,
            "away_team": away_team,
            "message": f"已使用选中赛程的 API-Football fixture_id：{fixture_id}。",
            "mapping_reason": source_note,
        }

    @classmethod
    def request_json(cls, path, params=None):
        api_key = load_api_key()
        if not api_key:
            raise RuntimeError(
                "缺少 API-Football Key。请在环境变量、.streamlit/secrets.toml 或 .env 中保存 API_FOOTBALL_KEY。"
            )
        response = requests.get(
            f"{API_FOOTBALL_BASE}{path}",
            params=params or {},
            timeout=API_REQUEST_TIMEOUT,
            headers={"x-apisports-key": api_key, "Accept": "application/json"},
        )
        cls._stats["api_calls"] += 1
        payload = response.json()
        cls.log_api_response(path, params or {}, payload, response.status_code)
        response.raise_for_status()
        errors = payload.get("errors")
        if isinstance(errors, dict) and errors:
            raise RuntimeError("; ".join(str(value) for value in errors.values()))
        if isinstance(errors, list) and errors:
            raise RuntimeError("; ".join(str(value) for value in errors))
        return payload.get("response", [])

    @classmethod
    def log_api_response(cls, path, params, payload, status_code):
        rows = payload.get("response") if isinstance(payload, dict) else None
        print(
            "[FixtureIDMapper API Response]",
            safe_json_preview({
                "endpoint": f"{API_FOOTBALL_BASE}{path}",
                "params": params,
                "status": status_code,
                "results": payload.get("results") if isinstance(payload, dict) else None,
                "message": payload.get("message") if isinstance(payload, dict) else None,
                "response_count": len(rows or []) if isinstance(rows, list) else None,
            }),
        )

    @classmethod
    def log_result(cls, match, result, cache_status):
        fixture = result.get("fixture") or {}
        raw = fixture.get("raw") or {}
        api_fixture = raw.get("fixture") or {}
        league = raw.get("league") or {}
        print(
            "[FixtureIDMapper Result]",
            safe_json_preview({
                "worldcup_match_id": match.get("schedule_fixture_id") or match.get("fixture_id"),
                "home_team": match.get("home_en") or match.get("home_cn"),
                "away_team": match.get("away_en") or match.get("away_cn"),
                "resolved_fixture_id": fixture.get("id") or api_fixture.get("id"),
                "cache_status": cache_status,
                "league_id": league.get("id"),
                "season": league.get("season"),
                "api_fixture_date": api_fixture.get("date"),
                "mapping_reason": result.get("mapping_reason") or result.get("message"),
                "stats": cls.stats(),
            }),
        )
