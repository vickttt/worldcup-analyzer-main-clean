import requests
import streamlit as st

from modules.cache_config import TEAM_PROFILE_TTL
from modules.odds_client import search_team
from modules.pregame_content import profile_for


PENDING_VALUES = {"待接入", "后续扩展", "", None}


def clean_value(value):
    if value in PENDING_VALUES:
        return None
    return value


@st.cache_data(ttl=TEAM_PROFILE_TTL, show_spinner=False)
def fetch_team_profile(team_name):
    static_profile = profile_for(team_name)
    api_team = None
    api_error = None

    try:
        api_team = search_team(team_name)
    except (requests.RequestException, RuntimeError) as error:
        api_error = str(error)

    profile = {
        "name": (api_team or {}).get("name") or team_name,
        "country": (api_team or {}).get("country"),
        "code": (api_team or {}).get("code"),
        "founded": (api_team or {}).get("founded"),
        "logo": (api_team or {}).get("logo"),
        "national": (api_team or {}).get("national"),
        "fifa_rank": clean_value(static_profile.get("fifa_rank")),
        "elo": clean_value(static_profile.get("elo")),
        "team_value": clean_value(static_profile.get("team_value")),
        "average_age": clean_value(static_profile.get("average_age")),
        "coach": clean_value(static_profile.get("coach")),
        "best_world_cup": clean_value(static_profile.get("best_world_cup")),
        "world_cup_appearances": clean_value(static_profile.get("world_cup_appearances")),
        "team_value_number": static_profile.get("team_value_number", 0),
        "colors": static_profile.get("colors", ("#64748b", "#94a3b8")),
        "source": "API-Football + 本地公开资料补充" if api_team else "本地公开资料补充",
        "cache_ttl": "7天",
        "api_error": api_error,
    }
    return profile

