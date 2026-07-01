import json
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st
import yaml

from modules.api_client import request_json
from modules.cache_config import TEAM_ID_CACHE_TTL


TEAM_VARIANT_TOKENS = (" w", " u17", " u18", " u19", " u20", " u21", " u22", " u23")


def normalize_text(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_text.lower().replace(".", " ").replace("-", " ").split())


def data_dir():
    path = Path(__file__).resolve().parents[1] / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache_dir():
    path = data_dir() / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def aliases_path():
    return data_dir() / "team_aliases.yaml"


def team_id_cache_path():
    return cache_dir() / "team_id_cache.json"


def load_team_aliases():
    with aliases_path().open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def canonical_name(value):
    aliases = load_team_aliases()
    entry = aliases.get(value)
    if isinstance(entry, dict):
        return entry.get("canonical") or value
    if isinstance(entry, str):
        return entry
    return value


def alias_candidates(team_name):
    aliases = load_team_aliases()
    candidates = [team_name]
    entry = aliases.get(team_name)
    if isinstance(entry, dict):
        canonical = entry.get("canonical")
        if canonical:
            candidates.append(canonical)
        candidates.extend(entry.get("aliases") or [])
    elif isinstance(entry, str):
        candidates.append(entry)

    normalized_target = normalize_text(team_name)
    for key, value in aliases.items():
        values = []
        if isinstance(value, dict):
            values = [value.get("canonical"), *(value.get("aliases") or [])]
        elif isinstance(value, str):
            values = [value]
        normalized_values = {normalize_text(item) for item in [key, *values] if item}
        if normalized_target in normalized_values:
            candidates.append(key)
            candidates.extend(item for item in values if item)

    deduped = []
    seen = set()
    for candidate in candidates:
        normalized = normalize_text(candidate)
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append(candidate)
    return deduped


def request_teams(query):
    return request_json("/teams", {"search": query})


def is_unwanted_team_variant(team_name, target_name):
    normalized_name = normalize_text(team_name)
    normalized_target = normalize_text(target_name)
    target_allows_variant = any(token.strip() in normalized_target.split() for token in TEAM_VARIANT_TOKENS)
    if target_allows_variant:
        return False
    return any(
        normalized_name.endswith(token) or f"{token} " in normalized_name
        for token in TEAM_VARIANT_TOKENS
    )


def team_match_score(team_name, team, allow_fuzzy=True):
    target = normalize_text(team_name)
    name = normalize_text(team.get("name", ""))
    code = normalize_text(team.get("code", ""))
    country = normalize_text(team.get("country", ""))

    if is_unwanted_team_variant(team.get("name", ""), team_name):
        return -1
    if target == name:
        return 100
    if target == country:
        return 95
    if code and target == code:
        return 90
    if allow_fuzzy and target and name and (target in name or name in target):
        return 60
    if allow_fuzzy and target and country and (target in country or country in target):
        return 55
    return 0


def select_team_from_response(team_name, teams):
    if not teams:
        return None

    national_teams = [item for item in teams if item.get("team", {}).get("national")]
    candidates = national_teams or teams

    scored = []
    for index, item in enumerate(candidates):
        team = item.get("team", {})
        score = team_match_score(team_name, team)
        if team.get("national"):
            score += 5
        if score > 0:
            scored.append((score, -index, team))

    if scored:
        return sorted(scored, reverse=True)[0][2]

    fallback = next(
        (
            item.get("team")
            for item in candidates
            if not is_unwanted_team_variant((item.get("team") or {}).get("name", ""), team_name)
        ),
        None,
    )
    return fallback


def read_team_cache():
    path = team_id_cache_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_team_cache(payload):
    with team_id_cache_path().open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def cache_keys(team_name):
    keys = {normalize_text(team_name)}
    for candidate in alias_candidates(team_name):
        keys.add(normalize_text(candidate))
    return {key for key in keys if key}


def cache_entry_to_team(entry, team_name):
    team = dict(entry.get("team") or {})
    if team_match_score(team_name, team) <= 0:
        return None
    team["_resolver"] = {
        "input": team_name,
        "matched_query": entry.get("matched_query"),
        "matched_name": team.get("name"),
        "team_id": team.get("id"),
        "attempted": entry.get("attempted") or [],
        "cache_status": "team_id_cache",
    }
    return team if team.get("id") else None


def read_cached_team(team_name):
    cache = read_team_cache()
    for key in cache_keys(team_name):
        entry = cache.get(key)
        if entry:
            return cache_entry_to_team(entry, team_name)
    return None


def write_cached_team(team_name, team, matched_query, attempted):
    cache = read_team_cache()
    entry = {
        "team": {key: value for key, value in team.items() if not key.startswith("_")},
        "matched_query": matched_query,
        "attempted": attempted,
        "updated_at": datetime.now().isoformat(),
    }
    for key in cache_keys(team_name) | cache_keys(team.get("name") or ""):
        cache[key] = entry
    write_team_cache(cache)


@st.cache_data(ttl=TEAM_ID_CACHE_TTL, show_spinner=False)
def resolve_team(team_name):
    cached = read_cached_team(team_name)
    if cached:
        return cached

    attempted = []
    for candidate in alias_candidates(team_name):
        attempted.append(candidate)
        try:
            teams = request_teams(candidate)
        except RuntimeError:
            continue
        team = select_team_from_response(candidate, teams)
        if team:
            team = dict(team)
            team["_resolver"] = {
                "input": team_name,
                "matched_query": candidate,
                "matched_name": team.get("name"),
                "team_id": team.get("id"),
                "attempted": attempted,
                "cache_status": "api_resolved",
            }
            write_cached_team(team_name, team, candidate, attempted)
            return team
    return None
