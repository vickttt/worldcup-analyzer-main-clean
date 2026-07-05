from datetime import datetime, timedelta

import requests
import streamlit as st

from modules.venue_utils import venue_city_for


WEATHER_TTL = 6 * 60 * 60
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_TIMEOUT = 2


def clean_city(value):
    text = str(value or "").strip()
    if not text:
        return ""
    return text.split(",")[0].split("(")[0].strip()


def parse_match_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        pass
    for fmt in ("%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue
    return None


@st.cache_data(ttl=WEATHER_TTL, show_spinner=False)
def geocode_city(city):
    city = clean_city(city)
    if not city:
        return None
    response = requests.get(
        GEOCODE_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=WEATHER_TIMEOUT,
    )
    response.raise_for_status()
    results = response.json().get("results") or []
    if not results:
        return None
    result = results[0]
    return {
        "name": result.get("name") or city,
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
        "country": result.get("country"),
    }


def nearest_hour_index(times, target):
    if not times or not target:
        return None
    best_index = None
    best_delta = None
    target_naive = target.replace(tzinfo=None)
    for index, value in enumerate(times):
        try:
            hour = datetime.fromisoformat(value)
        except ValueError:
            continue
        delta = abs(hour - target_naive)
        if best_delta is None or delta < best_delta:
            best_index = index
            best_delta = delta
    if best_delta is not None and best_delta <= timedelta(hours=2):
        return best_index
    return None


@st.cache_data(ttl=WEATHER_TTL, show_spinner=False)
def fetch_weather(city, kickoff_value):
    location = geocode_city(city)
    kickoff = parse_match_datetime(kickoff_value)
    if not location or not kickoff:
        return {
            "available": False,
            "summary": "天气暂不可用",
            "source": "Open-Meteo",
            "message": "缺少城市或比赛时间。",
        }

    date_text = kickoff.date().isoformat()
    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,wind_speed_10m",
            "start_date": date_text,
            "end_date": date_text,
            "timezone": "auto",
        },
        timeout=WEATHER_TIMEOUT,
    )
    response.raise_for_status()
    hourly = response.json().get("hourly") or {}
    index = nearest_hour_index(hourly.get("time") or [], kickoff)
    if index is None:
        return {
            "available": False,
            "summary": "天气暂不可用",
            "source": "Open-Meteo",
            "message": "未找到接近比赛时间的逐小时天气。",
        }

    def at(key):
        values = hourly.get(key) or []
        return values[index] if index < len(values) else None

    temperature = at("temperature_2m")
    humidity = at("relative_humidity_2m")
    rain = at("precipitation_probability")
    wind = at("wind_speed_10m")
    return {
        "available": True,
        "temperature": temperature,
        "humidity": humidity,
        "rain_probability": rain,
        "wind_speed": wind,
        "location": location,
        "source": "Open-Meteo",
        "summary": f"{temperature:g}°C · 湿度{humidity:g}% · 降雨{rain:g}% · 风速{wind:g}km/h",
    }


def weather_for_fixture(fixture):
    if not fixture:
        return {"available": False, "summary": "天气暂不可用", "source": "Open-Meteo"}
    raw_venue = ((fixture.get("raw") or {}).get("fixture") or {}).get("venue", {}) or {}
    venue_name = fixture.get("venue_name") or raw_venue.get("name")
    city = venue_city_for(venue_name, fixture.get("venue_city") or raw_venue.get("city"))
    kickoff = fixture.get("kickoff_utc") or ((fixture.get("raw") or {}).get("fixture") or {}).get("date")
    try:
        return fetch_weather(city, kickoff)
    except (requests.RequestException, ValueError, TypeError) as error:
        return {
            "available": False,
            "summary": "天气暂不可用",
            "source": "Open-Meteo",
            "message": str(error),
        }
