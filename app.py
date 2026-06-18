from pathlib import Path
from datetime import datetime, timedelta
from html import escape
from itertools import combinations
import json
import re
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
import yaml

from modules.match_parser import parse_match
from modules.market_utils import asian_handicap_summary, correct_score_summary
from modules.betting_opinion import build_betting_opinion
from modules.decision_engine import build_decision_engine, traffic_light
from modules.mock_data import get_mock_news_and_injuries
from modules.odds_client import fetch_match_data
from modules.pregame_content import (
    BANNER_IMAGE_URL,
    bet_cn,
    build_risk_notes,
    build_storylines,
    disagreement_label,
    predicted_lineup_for,
    profile_for,
    reason_cn,
    static_recent_form_for,
    team_cn,
)
from modules.polymarket_client import fetch_polymarket
from modules.probability_model import combine_probabilities
from modules.rating_model import rate_opportunity
from modules.report_generator import build_report, save_report
from modules.result_distribution import (
    betting_structure,
    build_extreme_scenarios,
    build_result_distribution,
)
from modules.schedule_client import (
    default_standings,
    available_match_dates,
    default_date_key,
    fetch_world_cup_schedule,
    fixtures_for_date,
    fixture_local_datetime,
    group_by_match_date,
    is_finished,
    is_live,
    schedule_groups,
    tournament_stats,
)
from modules.score_model import recommend_scores
from modules.the_odds_client import fetch_odds
from modules.user_odds import (
    build_market_candidates,
    build_recommendation_slots,
    candidate_with_actual,
    parse_actual_odds,
    parse_score,
    recommendation_reason,
)
from modules.value_model import analyze_value
from modules.weather_client import weather_for_fixture


def percent(value):
    return f"{value * 100:.1f}%"


def fmt(value):
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def fmt_odds(value):
    if value is None:
        return "-"
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return str(value)


def clamp(value, low=0, high=100):
    return max(low, min(high, round(value)))


def money(value):
    if value is None:
        return "-"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number >= 1_000_000:
        return f"${number / 1_000_000:.2f}M"
    if number >= 1_000:
        return f"${number / 1_000:.1f}K"
    return f"${number:.0f}"


def parse_kickoff(value):
    if not value:
        return "-", "-"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value, "-"
    local_time = parsed.astimezone(ZoneInfo("Asia/Shanghai"))
    return local_time.strftime("%Y-%m-%d"), local_time.strftime("%H:%M CST")


def flag_for_team(name):
    flags = {
        "Argentina": "🇦🇷",
        "Algeria": "🇩🇿",
    }
    return flags.get(name, "")


def risk_color(risk):
    return {
        "Low": "#16a34a",
        "Medium": "#f59e0b",
        "High": "#dc2626",
    }.get(risk, "#64748b")


def card_css():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.5rem; max-width: 1180px;}
        h1 {font-size: 1.65rem !important; line-height: 1.25 !important;}
        p, li, div {font-size: 0.95rem;}
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 14px 16px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
            min-height: 104px;
        }
        div[data-testid="stMetricLabel"] p {
            font-size: 0.82rem;
            color: #64748b;
            white-space: normal;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.02rem;
            color: #0f172a;
            white-space: normal;
            overflow-wrap: anywhere;
        }
        .section-title {
            font-size: 1.08rem;
            font-weight: 700;
            color: #0f172a;
            margin: 0.3rem 0 0.7rem 0;
        }
        .hero-banner {
            position: relative;
            min-height: 260px;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid #dbe3ef;
            background-image: linear-gradient(90deg, rgba(15,23,42,.86), rgba(15,23,42,.38)), url("__BANNER__");
            background-size: cover;
            background-position: center;
            padding: 26px;
            color: white;
            margin-bottom: 1rem;
        }
        .hero-kicker {
            font-size: 0.84rem;
            font-weight: 800;
            letter-spacing: 0.08rem;
            text-transform: uppercase;
            color: #cbd5e1;
        }
        .hero-match {
            font-size: 2.05rem;
            line-height: 1.15;
            font-weight: 900;
            margin-top: 0.5rem;
            color: white;
        }
        .hero-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 1rem;
        }
        .hero-chip {
            background: rgba(255,255,255,.14);
            border: 1px solid rgba(255,255,255,.26);
            border-radius: 999px;
            padding: 7px 12px;
            font-size: 0.86rem;
            font-weight: 700;
            color: white;
        }
        .hero-title {
            font-size: 1.8rem;
            font-weight: 800;
            color: #0f172a;
            margin: 0;
        }
        .hero-subtitle {
            color: #475569;
            font-weight: 600;
            margin-top: 0.15rem;
        }
        .team-name {
            font-size: 1.3rem;
            font-weight: 800;
            color: #0f172a;
            margin-top: 0.35rem;
        }
        .vs-label {
            font-size: 1.45rem;
            font-weight: 900;
            color: #334155;
            margin-top: 2.25rem;
            text-align: center;
        }
        .reason-text {
            color: #64748b;
            font-size: 0.83rem;
            line-height: 1.35;
            margin-top: -0.35rem;
        }
        .form-strip {
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: 0.12rem;
            color: #0f172a;
            margin: 0.2rem 0 0.45rem 0;
        }
        .risk-pill {
            display: inline-block;
            color: white;
            border-radius: 999px;
            padding: 5px 12px;
            font-size: 0.88rem;
            font-weight: 700;
        }
        .soft-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 14px 16px;
            min-height: 92px;
        }
        .soft-card-title {
            color: #64748b;
            font-size: 0.82rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .soft-card-value {
            color: #0f172a;
            font-size: 1.08rem;
            font-weight: 800;
            overflow-wrap: anywhere;
        }
        .story-item {
            padding: 10px 12px;
            border-left: 4px solid #2563eb;
            background: #f8fafc;
            border-radius: 8px;
            margin-bottom: 8px;
            color: #0f172a;
        }
        .analysis-block {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 10px;
        }
        .analysis-title {
            color: #0f172a;
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .analysis-text {
            color: #334155;
            line-height: 1.7;
            margin-bottom: 0;
        }
        .warning-item {
            padding: 10px 12px;
            border-left: 4px solid #f59e0b;
            background: #fffbeb;
            border-radius: 8px;
            margin-bottom: 8px;
            color: #0f172a;
        }
        .schedule-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
        .schedule-match {
            font-size: 1.05rem;
            font-weight: 850;
            color: #0f172a;
            margin-bottom: 0.35rem;
        }
        .schedule-meta {
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.6;
        }
        .schedule-empty {
            background: #f8fafc;
            border: 1px dashed #cbd5e1;
            border-radius: 12px;
            padding: 18px;
            color: #64748b;
        }
        .portal-banner {
            min-height: 300px;
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid #dbe3ef;
            background-image: linear-gradient(90deg, rgba(8,25,64,.08), rgba(8,25,64,.08), rgba(3,7,18,.42)), url("__BANNER__");
            background-size: cover;
            background-position: center;
            padding: 24px 28px;
            box-sizing: border-box;
            color: white;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: flex-start;
            justify-content: flex-end;
        }
        .portal-title {
            font-size: 1.45rem;
            line-height: 1.08;
            font-weight: 950;
            color: white;
            margin-top: 0;
            max-width: 760px;
            letter-spacing: 0.08rem;
            text-transform: uppercase;
        }
        .portal-subtitle {
            color: #dbeafe;
            font-size: 0.95rem;
            line-height: 1.5;
            max-width: 620px;
            margin-top: 0.45rem;
        }
        .portal-stat-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(90px, 1fr));
            gap: 10px;
            margin-top: 16px;
            max-width: 620px;
        }
        .portal-stat {
            background: rgba(255,255,255,.13);
            border: 1px solid rgba(255,255,255,.24);
            border-radius: 14px;
            padding: 10px 12px;
            color: white;
        }
        .portal-stat-label {
            color: #cbd5e1;
            font-size: .78rem;
            font-weight: 800;
        }
        .portal-stat-value {
            color: white;
            font-size: 1.12rem;
            font-weight: 900;
            margin-top: .25rem;
        }
        .status-pill {
            display: inline-block;
            border-radius: 999px;
            padding: 4px 10px;
            background: #e0f2fe;
            color: #075985;
            font-size: .78rem;
            font-weight: 800;
        }
        .status-pill-finished {
            background: #dcfce7;
            color: #166534;
        }
        .status-pill-live {
            background: #fee2e2;
            color: #991b1b;
        }
        .match-hero-card {
            background: linear-gradient(135deg, #061a3d, #0f3b7c 48%, #07111f);
            border: 1px solid rgba(148, 163, 184, .25);
            border-radius: 18px;
            padding: 22px;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 14px 34px rgba(15, 23, 42, .16);
        }
        .match-hero-grid {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
            gap: 18px;
        }
        .match-team {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .match-team.away {
            justify-content: flex-end;
            text-align: right;
        }
        .team-badge {
            width: 72px;
            height: 72px;
            border-radius: 999px;
            background: rgba(255,255,255,.13);
            border: 1px solid rgba(255,255,255,.24);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            flex: 0 0 auto;
        }
        .team-badge img {
            max-width: 62px;
            max-height: 62px;
            object-fit: contain;
        }
        .team-flag {font-size: 1.65rem; line-height: 1;}
        .match-team-name {
            font-size: 1.55rem;
            font-weight: 900;
            line-height: 1.15;
            color: white;
        }
        .vs-mark {
            width: 54px;
            height: 54px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255,255,255,.15);
            border: 1px solid rgba(255,255,255,.25);
            font-weight: 950;
            color: white;
        }
        .match-meta-row {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin-top: 18px;
        }
        .match-meta-item {
            background: rgba(255,255,255,.12);
            border: 1px solid rgba(255,255,255,.18);
            border-radius: 12px;
            padding: 10px 12px;
        }
        .match-meta-label {
            color: #bfdbfe;
            font-size: .76rem;
            font-weight: 800;
        }
        .match-meta-value {
            color: white;
            font-weight: 850;
            margin-top: 3px;
            overflow-wrap: anywhere;
        }
        .date-nav-wrap {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding: 8px 0 14px 0;
            margin-bottom: 4px;
        }
        .date-chip {
            min-width: 92px;
            text-align: center;
            border: 1px solid #dbe3ef;
            border-radius: 10px;
            padding: 8px 10px;
            background: #f8fafc;
            color: #334155;
            font-weight: 800;
            white-space: nowrap;
        }
        .date-chip-active {
            background: #1d4ed8;
            color: white;
            border-color: #1d4ed8;
        }
        .standings-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 6px;
            font-size: 0.9rem;
        }
        .standings-table th {
            color: #64748b;
            font-size: 0.78rem;
            text-align: left;
            padding: 7px 8px;
        }
        .standings-table td {
            background: #f8fafc;
            padding: 8px;
            border-top: 1px solid #e2e8f0;
            border-bottom: 1px solid #e2e8f0;
        }
        .standings-table tr.qualify-1 td {background:#dcfce7;}
        .standings-table tr.qualify-2 td {background:#ecfdf5;}
        .standings-table td:first-child {border-left:1px solid #e2e8f0;border-radius:8px 0 0 8px;}
        .standings-table td:last-child {border-right:1px solid #e2e8f0;border-radius:0 8px 8px 0;}
        div[role="radiogroup"] {
            overflow-x: auto;
            flex-wrap: nowrap !important;
            padding-bottom: 8px;
        }
        div[role="radiogroup"] label {
            min-width: 92px;
            white-space: nowrap;
        }
        .form-tag {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            border-radius: 8px;
            color: white;
            font-weight: 900;
            margin-right: 5px;
        }
        .form-W {background:#16a34a;}
        .form-D {background:#64748b;}
        .form-L {background:#dc2626;}
        @media (max-width: 760px) {
            .block-container {padding-left: 0.8rem; padding-right: 0.8rem;}
            .portal-banner, .hero-banner {min-height: 260px; padding: 20px;}
            .portal-title, .hero-match {font-size: 1.55rem;}
            .portal-stat-grid {grid-template-columns: repeat(2, minmax(0, 1fr));}
            .match-hero-grid {grid-template-columns: 1fr; text-align: center;}
            .match-team, .match-team.away {justify-content: center; text-align: center;}
            .match-meta-row {grid-template-columns: repeat(2, minmax(0, 1fr));}
            div[data-testid="stMetric"] {min-height: 88px; padding: 10px 12px;}
            div[data-testid="stMetricValue"] {font-size: 0.92rem;}
            .schedule-match {font-size: 0.95rem;}
            .schedule-meta {font-size: 0.82rem;}
        }
        </style>
        """.replace("__BANNER__", BANNER_IMAGE_URL),
        unsafe_allow_html=True,
    )


def consensus_market(markets):
    if not markets:
        return None
    counts = {}
    for market in markets:
        line = market.get("line")
        counts[line] = counts.get(line, 0) + 1
    main_line = max(counts, key=counts.get)
    selected = [market for market in markets if market.get("line") == main_line]
    return main_line, selected


def format_team_line(team, line):
    if line is None:
        return "-"
    sign = "+" if line > 0 else ""
    return f"{team_cn(team)} {sign}{line:g}"


def soft_card(title, value, caption=None):
    st.markdown(
        f"""
        <div class="soft-card">
            <div class="soft-card-title">{title}</div>
            <div class="soft-card-value">{value}</div>
            <div class="reason-text">{caption or ""}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def probability_bar(label, value, price=None):
    label_text = f"{label} · {price}" if price else label
    st.write(f"**{label_text}**")
    st.progress(max(0, min(1, value or 0)))
    st.caption(percent(value or 0))


def comparison_bar(label, value, max_value, color="#2563eb"):
    ratio = 0.0 if not max_value else float(max(0, min(1, value / max_value)))
    st.write(f"**{label}**")
    st.progress(ratio)
    st.caption(f"约 €{value:.0f}M")


def official_name(match_name, fallback):
    return team_cn(match_name or fallback)


TEAM_FLAGS = {
    "Argentina": "🇦🇷",
    "Algeria": "🇩🇿",
    "Austria": "🇦🇹",
    "Jordan": "🇯🇴",
    "France": "🇫🇷",
    "England": "🏴",
    "Germany": "🇩🇪",
    "Spain": "🇪🇸",
    "Brazil": "🇧🇷",
    "Japan": "🇯🇵",
    "Portugal": "🇵🇹",
    "Democratic Republic of the Congo": "🇨🇩",
    "DR Congo": "🇨🇩",
    "Croatia": "🇭🇷",
    "Ghana": "🇬🇭",
    "Panama": "🇵🇦",
    "Uzbekistan": "🇺🇿",
    "Colombia": "🇨🇴",
    "United States": "🇺🇸",
}


def team_flag(name):
    return TEAM_FLAGS.get(name, "")


def team_badge_html(team):
    logo = team.get("logo")
    name = team.get("name") or ""
    if logo:
        return f'<div class="team-badge"><img src="{escape(str(logo), quote=True)}" alt="{escape(team_cn(name), quote=True)}"></div>'
    flag = team_flag(name) or team_cn(name)[:1]
    return f'<div class="team-badge"><span class="team-flag">{escape(flag)}</span></div>'


def selected_fixture_as_api_fixture(fixture):
    if not fixture:
        return None
    return {
        "home_team": fixture.get("home_team") or {},
        "away_team": fixture.get("away_team") or {},
        "raw": {
            "fixture": {
                "date": fixture.get("kickoff_utc"),
                "venue": {
                    "name": fixture.get("venue_name"),
                    "city": fixture.get("venue_city"),
                },
            },
            "league": {
                "round": fixture.get("round"),
                "name": fixture.get("league_name"),
            },
        },
    }


def odds_date_key_from_fixture(selected_fixture, api_football_data):
    fixture = selected_fixture or (api_football_data or {}).get("fixture") or {}
    kickoff = fixture.get("kickoff_utc")
    if not kickoff:
        raw = fixture.get("raw") or {}
        kickoff = (raw.get("fixture") or {}).get("date")
    if not kickoff:
        return None
    try:
        parsed = datetime.fromisoformat(str(kickoff).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%d")


def render_debug_panel(match, odds, api_football_data, polymarket, odds_date_key):
    fixture_result = (api_football_data or {}).get("fixture_result") or {}
    fixture = (api_football_data or {}).get("fixture") or {}
    home_team = fixture_result.get("home_team") or fixture.get("home_team") or {}
    away_team = fixture_result.get("away_team") or fixture.get("away_team") or {}
    handicap = (api_football_data or {}).get("asian_handicap") or {}
    correct_score = (api_football_data or {}).get("correct_score") or {}
    debug_rows = [
        {"项目": "Match", "状态": match.get("display_name"), "详情": f"{match.get('home_en')} vs {match.get('away_en')}"},
        {"项目": "Odds Date Key", "状态": odds_date_key or "-", "详情": "The Odds API UTC比赛日"},
        {"项目": "Fixture ID", "状态": fixture.get("id") or "-", "详情": fixture_result.get("message") or "-"},
        {
            "项目": "Home Team",
            "状态": home_team.get("id") or "-",
            "详情": f"{home_team.get('name') or '-'} / {(home_team.get('_resolver') or {}).get('cache_status', '-')}",
        },
        {
            "项目": "Away Team",
            "状态": away_team.get("id") or "-",
            "详情": f"{away_team.get('name') or '-'} / {(away_team.get('_resolver') or {}).get('cache_status', '-')}",
        },
        {
            "项目": "Match Winner",
            "状态": "found" if odds.get("found") else "missing",
            "详情": f"{odds.get('event_title') or odds.get('message')} / cache={odds.get('cache')}",
        },
        {
            "项目": "Over/Under",
            "状态": len(odds.get("over_under") or []),
            "详情": "The Odds API totals rows",
        },
        {
            "项目": "Asian Handicap",
            "状态": len(handicap.get("rows") or []),
            "详情": f"{handicap.get('source')} / {handicap.get('message')} / cache={handicap.get('cache')}",
        },
        {
            "项目": "Correct Score",
            "状态": len(correct_score.get("rows") or []),
            "详情": f"{correct_score.get('source')} / {correct_score.get('message')} / cache={correct_score.get('cache')}",
        },
        {
            "项目": "Polymarket",
            "状态": "found" if polymarket.get("found") else "missing",
            "详情": polymarket.get("event_title") or polymarket.get("message"),
        },
    ]
    debug_rows = [
        {key: "" if value is None else str(value) for key, value in row.items()}
        for row in debug_rows
    ]
    with st.expander("Debug Panel：页面实际读取的数据对象", expanded=True):
        st.dataframe(pd.DataFrame(debug_rows), use_container_width=True, hide_index=True)


def render_match_overview(match, api_football_data, selected_fixture=None):
    if selected_fixture:
        home = selected_fixture.get("home_team") or {"name": match["home_cn"]}
        away = selected_fixture.get("away_team") or {"name": match["away_cn"]}
        kickoff_text = fixture_time_text(selected_fixture)
        venue_name = selected_fixture.get("venue_name") or "球场待确认"
        city = selected_fixture.get("venue_city") or "城市待确认"
        weather = weather_for_fixture(selected_fixture)
    else:
        fixture = api_football_data.get("fixture")
        if not fixture:
            fixture = None

    if not selected_fixture and not fixture:
        home = {"name": match["home_cn"]}
        away = {"name": match["away_cn"]}
        kickoff_text = "时间待确认"
        venue_name = "球场待确认"
        city = "城市待确认"
        weather = {"summary": "天气暂不可用", "source": "Open-Meteo"}
    elif not selected_fixture:
        raw = fixture.get("raw", {})
        fixture_info = raw.get("fixture", {})
        venue = fixture_info.get("venue", {}) or {}
        home = fixture["home_team"]
        away = fixture["away_team"]
        kickoff_date, kickoff_time = parse_kickoff(fixture_info.get("date"))
        kickoff_text = f"{kickoff_date} {kickoff_time}" if kickoff_date != "TBD" else "时间待确认"
        venue_name = venue.get("name") or "球场待确认"
        city = venue.get("city") or "城市待确认"
        weather = weather_for_fixture(fixture)

    home_name = home.get("name") or match["home_cn"]
    away_name = away.get("name") or match["away_cn"]
    st.markdown(
        f"""
        <div class="match-hero-card">
            <div class="match-hero-grid">
                <div class="match-team">
                    {team_badge_html(home)}
                    <div>
                        <div class="team-flag">{escape(team_flag(home_name))}</div>
                        <div class="match-team-name">{escape(team_cn(home_name))}</div>
                    </div>
                </div>
                <div class="vs-mark">VS</div>
                <div class="match-team away">
                    <div>
                        <div class="team-flag">{escape(team_flag(away_name))}</div>
                        <div class="match-team-name">{escape(team_cn(away_name))}</div>
                    </div>
                    {team_badge_html(away)}
                </div>
            </div>
            <div class="match-meta-row">
                <div class="match-meta-item"><div class="match-meta-label">开球时间</div><div class="match-meta-value">{escape(kickoff_text)}</div></div>
                <div class="match-meta-item"><div class="match-meta-label">球场</div><div class="match-meta-value">{escape(str(venue_name))}</div></div>
                <div class="match-meta-item"><div class="match-meta-label">城市</div><div class="match-meta-value">{escape(str(city))}</div></div>
                <div class="match-meta-item"><div class="match-meta-label">天气</div><div class="match-meta-value">{escape(str(weather.get("summary") or "天气暂不可用"))}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_betting_opinion(opinion, odds=None, polymarket=None, match=None):
    distribution = opinion.get("result_distribution") or {}
    with st.container(border=True):
        st.markdown('<div class="section-title">🎯 投注观点</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            soft_card("胜平负", bet_cn(opinion.get("match_winner", "暂无观点")))
        with col2:
            soft_card("亚洲让球", bet_cn(opinion.get("asian_handicap", "暂无观点")))
        with col3:
            soft_card("大小球", bet_cn(opinion.get("over_under", "暂无观点")))
        with col4:
            soft_card("信心分", f"{opinion.get('confidence', 50)} / 100", "规则引擎评分")

        implied = (odds or {}).get("implied_probabilities") or {}
        odds_home = percent(implied.get("home_win", 0)) if implied else "-"
        poly_home = percent((polymarket or {}).get("home_win", 0)) if (polymarket or {}).get("found") else "-"
        value_gap = "-"
        if implied and (polymarket or {}).get("home_win") is not None:
            value_gap = percent(abs((polymarket or {}).get("home_win", 0) - implied.get("home_win", 0)))

        home_name = team_cn((match or {}).get("home_cn", "主队"))
        away_name = team_cn((match or {}).get("away_cn", "客队"))
        if implied:
            winner_text = (
                f"当前胜平负市场对 {home_name} / 平局 / {away_name} 的定价分别为 "
                f"{percent(implied.get('home_win', 0))} / {percent(implied.get('draw', 0))} / {percent(implied.get('away_win', 0))}。"
                f"Polymarket 主胜概率约为 {poly_home}，两者差异约 {value_gap}。"
            )
        else:
            winner_text = "当前缺少完整胜平负赔率，暂不形成单一方向判断。"

        handicap_text = (
            f"亚洲盘当前结论为：{bet_cn(opinion.get('asian_handicap'))}。"
            "需要同时观察主路径、边界路径和极端路径，避免只围绕最低赔率结果下注。"
        )
        goals_text = (
            f"大小球当前结论为：{bet_cn(opinion.get('over_under'))}。"
            "如果盘口数据不足，则以结果分布和临场价格变化作为主要观察对象。"
        )
        blocks = [
            ("胜平负观点", winner_text),
            ("亚洲让球观点", handicap_text),
            ("大小球观点", goals_text),
        ]
        for title, text in blocks:
            st.markdown(
                f'<div class="analysis-block"><div class="analysis-title">{title}</div>'
                f'<p class="analysis-text">{text}</p></div>',
                unsafe_allow_html=True,
            )

        if distribution:
            path_cols = st.columns(3)
            path_cols[0].metric("市场主路径", distribution.get("main_path", "-"))
            path_cols[1].metric("市场边界路径", distribution.get("boundary_path", "-"))
            path_cols[2].metric("市场极端路径", distribution.get("extreme_path", "-"))
            st.caption("最低赔率结果不是唯一结果；需要同时观察边界路径和极端路径。")


def render_score_card(title, score, status, reason=None):
    st.metric(title, f"{score} / 100", status)
    st.progress(score / 100)
    if reason:
        st.caption(reason)


def render_decision_engine(decision):
    with st.container(border=True):
        st.markdown('<div class="section-title">决策引擎 V1</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("综合信心分", f"{decision['final_confidence_score']} / 100")
            st.progress(decision["final_confidence_score"] / 100)
        with col2:
            st.metric("价值评级", decision["value_rating"])
            st.caption(decision["value_rating_meaning"])
        with col3:
            recommendation = decision["final_recommendation"]
            st.metric("推荐方向", bet_cn(recommendation["bet"]))
            st.caption(recommendation["reason"][0])
        with col4:
            stakes = decision["stake_suggestion"]
            st.metric("标准仓位", stakes["Standard"])
            st.caption(f"保守 {stakes['Conservative']} · 激进 {stakes['Aggressive']}")

        metric_cols = st.columns(3)
        disagreement = decision["market_disagreement"]
        contrarian = decision["contrarian"]
        upset = decision["upset_index"]
        with metric_cols[0]:
            render_score_card(
                "市场分歧",
                disagreement["score"],
                disagreement_label(disagreement["score"]),
                f"{team_cn(disagreement['direction'])} 分歧：{percent(disagreement['difference'])}",
            )
        with metric_cols[1]:
            render_score_card(
                "逆向分数",
                contrarian["score"],
                traffic_light(contrarian["score"], "偏高"),
                contrarian["reason"],
            )
        with metric_cols[2]:
            render_score_card(
                "爆冷指数",
                upset["score"],
                upset["meaning"],
                upset["reason"],
            )

        support_cols = st.columns(3)
        with support_cols[0]:
            render_score_card("ELO评分", decision["elo_rating"]["score"], "待接入", decision["elo_rating"]["reason"])
        with support_cols[1]:
            render_score_card("伤病影响", decision["injury_impact"]["score"], "框架分", decision["injury_impact"]["reason"])
        with support_cols[2]:
            render_score_card("球队身价", decision["team_value"]["score"], "待接入", decision["team_value"]["reason"])

        with st.expander("推荐理由"):
            for reason in decision["final_recommendation"]["reason"]:
                st.markdown(f"- {reason}")
            st.caption(
                "权重："
                + "，".join(f"{name} {weight}" for name, weight in decision["weights"].items())
            )


def render_result_distribution(distribution):
    with st.container(border=True):
        st.markdown('<div class="section-title">结果分布</div>', unsafe_allow_html=True)
        st.caption(distribution.get("explanation", "规则分布，不是比分预测。"))
        rows = distribution.get("rows", [])
        favorite = distribution.get("favorite", "")
        home_like = sum(row["probability"] for row in rows if favorite and favorite in row["label"] and "不败" not in row["label"])
        draw_like = sum(row["probability"] for row in rows if "平局" in row["label"])
        upset_like = sum(row["probability"] for row in rows if "不败" in row["label"])
        coverage = st.columns(3)
        coverage[0].metric("主胜覆盖区间", percent(home_like))
        coverage[1].metric("平局区间", percent(draw_like))
        coverage[2].metric("弱队不败区间", percent(upset_like))
        for row in distribution.get("rows", []):
            st.write(f"**{row['label']}**")
            st.progress(row["probability"])
            st.caption(f"{percent(row['probability'])} · {row['meaning']}")

        exposure = distribution.get("risk_exposure") or {}
        with st.container(border=True):
            st.markdown("**风险暴露**")
            st.write(f"示例下注：{exposure.get('example_bet', '-')}")
            st.write("输的路径：" + " / ".join(exposure.get("lose_paths", [])))
            st.caption(exposure.get("meaning", ""))


def render_extreme_scenarios(distribution):
    scenarios = build_extreme_scenarios(distribution)
    with st.container(border=True):
        st.markdown('<div class="section-title">极端路径风险</div>', unsafe_allow_html=True)
        if not scenarios:
            st.info("暂无足够市场数据识别极端路径。")
            return
        cols = st.columns(len(scenarios))
        for col, scenario in zip(cols, scenarios):
            with col:
                st.metric(scenario["name"], scenario["level"], percent(scenario["probability"]))
                st.caption(scenario["note"])


def render_betting_structure(distribution):
    rows = betting_structure(distribution)
    with st.container(border=True):
        st.markdown('<div class="section-title">资金结构参考</div>', unsafe_allow_html=True)
        st.caption("仅展示预算结构，不推荐具体投注金额。示例以 1000 元预算表达层级。")
        cols = st.columns(3)
        for col, row in zip(cols, rows):
            with col:
                st.metric(row["layer"], f"{int(row['share'] * 1000)}", f"{row['share'] * 100:.0f}%")
                st.caption(row["path"])


def recommendation_combo(match, odds, api_football_data=None, distribution=None, actual_odds=None):
    return build_recommendation_slots(match, odds, api_football_data, actual_odds or {}, distribution)


def round_to_hundred(value):
    return int(round(value / 100) * 100)


def recommended_total_stake(decision):
    stake = decision.get("recommended_stake") or {}
    return stake.get("amount", 0), stake.get("reason", "推荐仓位暂不可用。")


def stake_amounts(combo, decision):
    total, _ = recommended_total_stake(decision)
    rows = []
    recommended_rows = []
    for item in combo:
        effective_odds = item.get("effective_odds") or item.get("standard_odds") or item.get("odds")
        amount = round_to_hundred(total * item.get("share", 0)) if item.get("recommended") else 0
        row = {
            **item,
            "odds": effective_odds,
            "amount": amount,
        }
        rows.append(row)
        if row.get("recommended"):
            recommended_rows.append(row)

    difference = total - sum(item.get("amount", 0) for item in recommended_rows)
    if recommended_rows and difference:
        target = max(recommended_rows, key=lambda item: item.get("share", 0))
        target["amount"] = max(0, target.get("amount", 0) + difference)
    return rows


def rating_class(rating):
    return {
        "A+": "rating-Ap",
        "A": "rating-A",
        "B": "rating-B",
        "C": "rating-C",
        "D": "rating-D",
    }.get(rating, "rating-D")


def rating_badge(rating):
    return {
        "A": "🟢 A",
        "B": "🟡 B",
        "C": "🟠 C",
        "D": "🔴 D",
    }.get(rating, f"⚪ {rating}")


def combo_role(index, item):
    if not item.get("recommended"):
        return "⚪ 不推荐"
    if index == 1:
        return "🟢 主逻辑"
    if index == 2:
        return "🟡 次逻辑"
    if index == 3:
        return "🔵 辅助逻辑"
    if item.get("type") == "correct_score":
        return "⚪ 波胆逻辑"
    return "⚪ 补充逻辑"


def score_stars(score):
    filled = max(1, min(5, round((score or 0) / 20)))
    return "★" * filled + "☆" * (5 - filled)


def render_recommended_combo(match, odds, api_football_data, distribution):
    combo = recommendation_combo(match, odds, api_football_data, distribution)
    with st.container(border=True):
        st.markdown('<div class="section-title">推荐投注组合</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for col, item in zip(cols, combo):
            with col:
                st.metric(item["name"], f"{int(item['share'] * 100)}%")
        st.caption("组合用于展示结果覆盖结构，不构成具体投注指令。")
        render_betting_structure(distribution)


def confidence_reason(decision, odds):
    direction = decision.get("direction_confidence") or {}
    score = direction.get("score", decision["final_confidence_score"])
    if not odds.get("found"):
        return "信心受限于赔率盘口数据不足。"
    return direction.get("reason", f"方向把握 {score} / 100。")


def market_disagreement_reason(disagreement):
    if disagreement["score"] >= 67:
        return "不同市场存在明显分歧，说明当前定价并不统一。"
    if disagreement["score"] >= 34:
        return "Polymarket 与传统赔率存在一定差异，需要观察临场变化。"
    return "Polymarket 与传统赔率观点基本一致。"


def profit_text(amount, odds, outcome):
    if outcome == "win" and amount and odds:
        return f"+{round(amount * (odds - 1))}"
    if outcome == "lose" and amount:
        return f"-{amount}"
    return "视比分"


def profit_value(amount, odds, outcome):
    if outcome == "win" and amount and odds:
        return round(amount * (odds - 1))
    if outcome == "lose" and amount:
        return -amount
    return 0


def combo_item(combo, item_type):
    return next((item for item in combo if item.get("type") == item_type and item.get("recommended")), {})


def combo_items(combo, item_type):
    return [item for item in combo if item.get("type") == item_type and item.get("recommended")]


def total_known_profit(values):
    total = 0
    unknown = False
    for value in values:
        text = str(value)
        if text == "视比分":
            unknown = True
            continue
        try:
            total += int(text.replace("+", ""))
        except ValueError:
            unknown = True
    return f"{total:+d}" + (" + 浮动" if unknown else "")


def portfolio_metrics(combo):
    active = [item for item in combo if item.get("recommended") and item.get("amount")]
    total_stake = sum(item.get("amount", 0) for item in active)
    expected_profit = sum(item.get("amount", 0) * (item.get("actual_ev") or 0) for item in active)
    core_expected_profit = sum(
        item.get("amount", 0) * (item.get("actual_ev") or 0)
        for item in active
        if item.get("type") in {"winner", "handicap", "total"}
    )
    correct_score_expected_profit = sum(
        item.get("amount", 0) * (item.get("actual_ev") or 0)
        for item in active
        if item.get("type") == "correct_score"
    )
    max_loss = total_stake
    ratio = expected_profit / max_loss if max_loss else 0
    return {
        "total_stake": total_stake,
        "expected_profit": round(expected_profit),
        "expected_yield": expected_profit / total_stake if total_stake else 0,
        "core_expected_profit": round(core_expected_profit),
        "correct_score_expected_profit": round(correct_score_expected_profit),
        "max_loss": max_loss,
        "risk_reward": ratio,
        "weighted_correlation": weighted_combo_correlation(active),
    }


def bet_correlation(first, second):
    first_type = first.get("type")
    second_type = second.get("type")
    pair = {first_type, second_type}
    if first_type == second_type == "correct_score":
        return 0.35
    if first_type == second_type:
        return 1.0
    if pair == {"winner", "handicap"}:
        return 0.90
    if pair == {"winner", "correct_score"}:
        return 0.95
    if pair == {"handicap", "correct_score"}:
        return 0.88
    if pair == {"winner", "total"}:
        return 0.40
    if pair == {"handicap", "total"}:
        return 0.45
    if pair == {"total", "correct_score"}:
        return 0.55
    return 0.30


def weighted_combo_correlation(active):
    if len(active) < 2:
        return 0
    weighted_sum = 0
    weight_total = 0
    for left_index, left in enumerate(active):
        for right in active[left_index + 1:]:
            weight = (left.get("amount", 0) or 0) * (right.get("amount", 0) or 0)
            weighted_sum += weight * bet_correlation(left, right)
            weight_total += weight
    return weighted_sum / weight_total if weight_total else 0


def correlation_matrix_rows(combo):
    active = [item for item in combo if item.get("recommended") and item.get("amount")]
    rows = []
    for left in active:
        row = {"投注": left.get("name", "-")}
        for right in active:
            row[right.get("name", "-")] = f"{bet_correlation(left, right) * 100:.0f}%"
        rows.append(row)
    return rows


def market_odds_overview_rows(combo):
    rows = []
    for item in combo:
        if item.get("type") in {"empty"}:
            continue
        actual = item.get("actual_odds")
        market = item.get("standard_odds")
        if actual is None or market is None:
            status = "⚪ 未输入实际赔率"
        elif actual > market:
            status = "🟢 实际赔率更优"
        elif actual < market:
            status = "🔴 实际赔率偏低"
        else:
            status = "⚪ 与市场一致"
        rows.append({
            "投注": item.get("name", "-"),
            "实际赔率": fmt_odds(actual),
            "市场赔率": fmt_odds(market),
            "差异": f"{(item.get('edge') or 0) * 100:+.1f}%" if item.get("edge") is not None else "-",
            "状态": status,
        })
    return rows


def actual_odds_completeness(combo):
    candidates = [item for item in combo if item.get("type") != "empty"]
    if not candidates:
        return {"entered": 0, "total": 0, "ratio": 0, "missing": []}
    entered = [item for item in candidates if item.get("actual_odds")]
    missing = [item.get("name", "-") for item in candidates if not item.get("actual_odds")]
    return {
        "entered": len(entered),
        "total": len(candidates),
        "ratio": len(entered) / len(candidates),
        "missing": missing,
    }


def actual_odds_completeness_for_match(match, odds, api_football_data, actual_odds, fallback_combo):
    raw_candidates = build_market_candidates(match, odds, api_football_data)
    if not raw_candidates:
        return actual_odds_completeness(fallback_combo)

    required = []
    seen = set()
    for candidate in raw_candidates:
        key = (candidate.get("type"), candidate.get("slot"))
        if candidate.get("type") == "total":
            key = ("total", "主大小球")
            if key in seen:
                continue
            total_candidates = [
                candidate_with_actual(item, actual_odds)
                for item in raw_candidates
                if item.get("type") == "total"
            ]
            matched_total = next((item for item in total_candidates if item.get("actual_odds")), None)
            required.append(matched_total or {**candidate, "name": "大小球主盘口", "actual_odds": None})
            seen.add(key)
            continue
        if key in seen:
            continue
        seen.add(key)
        required.append(candidate_with_actual(candidate, actual_odds))

    entered = [item for item in required if item.get("actual_odds")]
    missing = [item.get("name", "-") for item in required if not item.get("actual_odds")]
    return {
        "entered": len(entered),
        "total": len(required),
        "ratio": len(entered) / len(required) if required else 0,
        "missing": missing,
    }


def optimized_strategy_reason_rows(strategy, match, distribution):
    if not strategy:
        return []
    items = strategy.get("items") or []
    positive_total = sum(max((item.get("amount", 0) * (item.get("actual_ev") or 0)), 0) for item in items)
    rows = []
    for item in items:
        ev_amount = item.get("amount", 0) * (item.get("actual_ev") or 0)
        contribution = max(ev_amount, 0) / positive_total if positive_total else 0
        rows.append({
            "保留投注": item.get("name", "-"),
            "仓位": f"{item.get('amount', 0)}元",
            "EV贡献占比": percent(contribution) if positive_total else "-",
            "方向一致性": percent(item_direction_alignment(item, match, distribution)),
            "保留原因": recommendation_reason(item),
        })
    return rows


def strategy_holdings_rows(strategy, match, distribution):
    rows = []
    for item in (strategy or {}).get("items") or []:
        rows.append({
            "投注": item.get("name", "-"),
            "仓位": f"{item.get('amount', 0)}元",
            "使用赔率": fmt_odds(item.get("odds") or item.get("effective_odds") or item.get("standard_odds")),
            "市场赔率": fmt_odds(item.get("standard_odds")),
            "实际赔率": fmt_odds(item.get("actual_odds")),
            "EV提升": f"{(item.get('ev_lift') or 0) * 100:+.1f}%" if item.get("ev_lift") is not None else "-",
            "覆盖率": percent(item.get("coverage_rate") or 0),
            "方向一致性": percent(item_direction_alignment(item, match, distribution)),
            "说明": recommendation_reason(item),
        })
    return rows


def strategy_path_rows(strategy):
    rows = []
    for row in (strategy or {}).get("score_rows") or []:
        rows.append({
            "比分": row.get("比分", "-"),
            "路径": row.get("路径", "-"),
            "路径权重": row.get("路径权重", "-"),
            "组合收益": row.get("组合收益", "-"),
            "EV贡献": row.get("EV贡献", "-"),
        })
    return rows


def render_strategy_detail(strategy, match, distribution):
    if not strategy:
        return
    st.markdown(f"**策略{strategy['code']}：{strategy['name']}**")
    metric_cols = st.columns(6)
    metric_cols[0].metric("总仓位", f"{sum(item.get('amount', 0) for item in strategy.get('items', []))}元")
    metric_cols[1].metric("命中率", percent(strategy.get("hit_rate", 0)))
    metric_cols[2].metric("EV", f"{strategy.get('expected_profit', 0):+.0f}")
    metric_cols[3].metric("最大盈利", f"{strategy.get('max_profit', 0):+.0f}")
    metric_cols[4].metric("最大亏损", f"-{strategy.get('max_loss', 0):.0f}")
    metric_cols[5].metric("评分", strategy.get("score", 0))

    holdings = strategy_holdings_rows(strategy, match, distribution)
    if holdings:
        st.markdown("**策略组成与仓位结构**")
        st.dataframe(pd.DataFrame(holdings), use_container_width=True, hide_index=True)

    paths = strategy_path_rows(strategy)
    if paths:
        st.markdown("**收益路径与风险路径**")
        st.dataframe(pd.DataFrame(paths), use_container_width=True, hide_index=True)

    best = max((strategy.get("score_rows") or []), key=lambda row: row.get("_total", 0), default=None)
    worst = min((strategy.get("score_rows") or []), key=lambda row: row.get("_total", 0), default=None)
    if best or worst:
        best_text = f"{best.get('比分')} {best.get('组合收益')}" if best else "-"
        worst_text = f"{worst.get('比分')} {worst.get('组合收益')}" if worst else "-"
        st.caption(f"最佳比分路径：{best_text}；最差比分路径：{worst_text}。")


def bet_identity(item):
    return (
        item.get("type"),
        str(item.get("selection") or item.get("name") or ""),
    )


def discard_reason(item, selected_items):
    if not item.get("recommended"):
        return item.get("not_recommended_reason") or "未达到推荐阈值。"
    if not item.get("actual_odds"):
        return "未录入实际赔率，EV判断不完整。"
    if item.get("edge") is not None and item.get("edge") < 0:
        return "实际赔率低于市场赔率，价值不足。"
    if item.get("ev_lift") is not None and item.get("ev_lift") <= 0:
        return "EV贡献不足，未进入优化组合。"
    if selected_items:
        avg_corr = sum(bet_correlation(item, selected) for selected in selected_items) / len(selected_items)
        if avg_corr >= 0.75:
            return "与已选投注相关性过高，继续加入会造成路径集中。"
    return "综合评分低于已选组合，未被策略优化器保留。"


def discarded_bet_rows(all_combo, selected_strategy):
    selected_items = (selected_strategy or {}).get("items") or []
    selected_keys = {bet_identity(item) for item in selected_items}
    rows = []
    for item in all_combo:
        if item.get("type") == "empty" or bet_identity(item) in selected_keys:
            continue
        rows.append({
            "未保留投注": item.get("name", "-"),
            "市场赔率": fmt_odds(item.get("standard_odds")),
            "实际赔率": fmt_odds(item.get("actual_odds")),
            "EV提升": f"{(item.get('ev_lift') or 0) * 100:+.1f}%" if item.get("ev_lift") is not None else "-",
            "放弃原因": discard_reason(item, selected_items),
        })
    return rows


def score_path_label(match, distribution, score):
    try:
        home_goals, away_goals = [int(part) for part in str(score).split(":", 1)]
    except ValueError:
        return "-"
    favorite_home = distribution.get("favorite") in {team_cn(match["home_cn"]), match["home_cn"]}
    margin = home_goals - away_goals if favorite_home else away_goals - home_goals
    if margin == 1:
        return "热门方胜1球主路径"
    if margin == 2:
        return "热门方胜2球主路径"
    if margin >= 3:
        return "热门方胜3球以上极端路径"
    if margin == 0:
        return "平局风险路径"
    return "弱势方爆冷路径"


def exact_score_probability(combo, score):
    for item in combo_items(combo, "correct_score"):
        if str(item.get("selection")) == str(score):
            odds_value = item.get("standard_odds") or item.get("odds")
            try:
                return 1 / float(odds_value)
            except (TypeError, ValueError, ZeroDivisionError):
                return None
    return None


def score_category(match, distribution, score):
    try:
        home_goals, away_goals = [int(part) for part in str(score).split(":", 1)]
    except ValueError:
        return "unknown"
    favorite_home = distribution.get("favorite") in {team_cn(match["home_cn"]), match["home_cn"]}
    margin = home_goals - away_goals if favorite_home else away_goals - home_goals
    if margin == 1:
        return "favorite_1"
    if margin == 2:
        return "favorite_2"
    if margin >= 3:
        return "favorite_3_plus"
    if margin == 0:
        return "draw"
    return "underdog"


def distribution_category_probability(distribution, category):
    rows = distribution.get("rows") or []
    if category == "favorite_1":
        return sum(row.get("probability", 0) for row in rows if "小胜" in row.get("label", ""))
    if category == "favorite_2":
        return sum(row.get("probability", 0) for row in rows if "赢2球" in row.get("label", ""))
    if category == "favorite_3_plus":
        return sum(row.get("probability", 0) for row in rows if "3球以上" in row.get("label", ""))
    if category == "draw":
        return sum(row.get("probability", 0) for row in rows if "平局" in row.get("label", ""))
    if category == "underdog":
        return sum(row.get("probability", 0) for row in rows if "不败" in row.get("label", ""))
    return 0


def scenario_probability(match, distribution, combo, score, all_scores):
    exact_probability = exact_score_probability(combo, score)
    if exact_probability is not None:
        return exact_probability
    category = score_category(match, distribution, score)
    same_category_count = sum(
        1 for candidate_score in all_scores
        if score_category(match, distribution, candidate_score) == category
    )
    category_probability = distribution_category_probability(distribution, category)
    return category_probability / same_category_count if same_category_count else 0


def scenario_probability_map(match, distribution, combo, scores):
    raw = {
        score: max(0, scenario_probability(match, distribution, combo, score, scores))
        for score in scores
    }
    total = sum(raw.values())
    if total <= 0 and scores:
        return {score: 1 / len(scores) for score in scores}
    return {score: value / total for score, value in raw.items()} if total else {}


def parse_handicap_selection(selection):
    text = str(selection or "")
    match = re.search(r"\b(Home|Away)\b\s*([+-]?\d+(?:\.\d+)?)", text, re.I)
    if match:
        return match.group(1).lower(), float(match.group(2))
    return None, None


def parse_total_selection(selection):
    text = str(selection or "")
    match = re.search(r"(Under|Over|小于|大于)\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
    if not match:
        return None, None
    side = "under" if match.group(1).lower() in {"under", "小于"} else "over"
    return side, float(match.group(2))


def winner_outcome(item, match, home_goals, away_goals):
    selection = str(item.get("selection") or item.get("name") or "")
    if home_goals == away_goals:
        result = "平局"
    elif home_goals > away_goals:
        result = match["home_cn"]
    else:
        result = match["away_cn"]
    return "win" if result in selection else "lose"


def handicap_outcome(item, home_goals, away_goals):
    side, line = parse_handicap_selection(item.get("selection") or item.get("name"))
    if side is None:
        return None
    adjusted = home_goals + line if side == "home" else away_goals + line
    opponent = away_goals if side == "home" else home_goals
    return "win" if adjusted > opponent else "lose"


def total_outcome(item, home_goals, away_goals):
    side, line = parse_total_selection(item.get("selection") or item.get("name"))
    if side is None:
        return None
    total_goals = home_goals + away_goals
    if side == "under":
        return "win" if total_goals < line else "lose"
    return "win" if total_goals > line else "lose"


def correct_score_outcome(item, home_goals, away_goals):
    return "win" if str(item.get("selection")) == f"{home_goals}:{away_goals}" else "lose"


def score_profit_row(match, distribution, combo, score):
    home_goals, away_goals = [int(part) for part in score.split(":", 1)]
    winner = combo_item(combo, "winner")
    handicap = combo_item(combo, "handicap")
    total = combo_item(combo, "total")
    correct_scores = combo_items(combo, "correct_score")

    winner_profit = profit_value(winner.get("amount"), winner.get("odds"), winner_outcome(winner, match, home_goals, away_goals)) if winner else 0
    handicap_profit = profit_value(handicap.get("amount"), handicap.get("odds"), handicap_outcome(handicap, home_goals, away_goals)) if handicap else 0
    total_profit = profit_value(total.get("amount"), total.get("odds"), total_outcome(total, home_goals, away_goals)) if total else 0
    correct_1 = correct_scores[0] if len(correct_scores) > 0 else {}
    correct_2 = correct_scores[1] if len(correct_scores) > 1 else {}
    correct_1_profit = profit_value(correct_1.get("amount"), correct_1.get("odds"), correct_score_outcome(correct_1, home_goals, away_goals)) if correct_1 else 0
    correct_2_profit = profit_value(correct_2.get("amount"), correct_2.get("odds"), correct_score_outcome(correct_2, home_goals, away_goals)) if correct_2 else 0
    total_value = winner_profit + handicap_profit + total_profit + correct_1_profit + correct_2_profit
    probability = exact_score_probability(combo, score)
    ev_contribution = total_value * probability if probability is not None else None
    return {
        "比分": score,
        "路径": score_path_label(match, distribution, score),
        "路径权重": percent(probability) if probability is not None else "-",
        "独赢收益": f"{winner_profit:+d}",
        "让球收益": f"{handicap_profit:+d}",
        "大小球收益": f"{total_profit:+d}",
        "波胆1收益": f"{correct_1_profit:+d}",
        "波胆2收益": f"{correct_2_profit:+d}",
        "组合收益": f"{total_value:+d}",
        "概率×收益": "-",
        "EV贡献": f"{ev_contribution:+.0f}" if ev_contribution is not None else "-",
        "_total": total_value,
        "_ev_contribution": ev_contribution,
    }


def score_candidates(match, distribution, combo):
    favorite_home = distribution.get("favorite") == team_cn(match["home_cn"]) or distribution.get("favorite") == match["home_cn"]
    defaults = ["1:0", "2:0", "2:1", "3:0", "1:1", "0:1"] if favorite_home else ["0:1", "0:2", "1:2", "0:3", "1:1", "1:0"]
    correct = [item.get("selection") for item in combo_items(combo, "correct_score") if item.get("selection")]
    ordered = []
    for score in correct + defaults:
        if score not in ordered and re.match(r"^\d+:\d+$", str(score)):
            ordered.append(score)
    return ordered[:8]


def path_analysis_rows(match, distribution, combo):
    scores = score_candidates(match, distribution, combo)
    probabilities = scenario_probability_map(match, distribution, combo, scores)
    rows = []
    for score in scores:
        row = score_profit_row(match, distribution, combo, score)
        probability = probabilities.get(score, 0)
        ev_contribution = row["_total"] * probability
        row["路径权重"] = percent(probability)
        row["概率×收益"] = f"{percent(probability)} × {row['组合收益']}"
        row["EV贡献"] = f"{ev_contribution:+.0f}"
        row["_ev_contribution"] = ev_contribution
        rows.append(row)
    rows.sort(key=lambda row: row.get("_ev_contribution") or 0, reverse=True)
    positive_total = sum(max(row.get("_ev_contribution") or 0, 0) for row in rows)
    cumulative = 0
    for row in rows:
        contribution = max(row.get("_ev_contribution") or 0, 0)
        cumulative += contribution
        row["累计贡献"] = percent(cumulative / positive_total) if positive_total else "-"
    return [{key: value for key, value in row.items() if not key.startswith("_")} for row in rows]


def worst_score_path(match, distribution, combo):
    rows = [score_profit_row(match, distribution, combo, score) for score in score_candidates(match, distribution, combo)]
    if not rows:
        return {"score": "-", "profit": 0}
    worst = min(rows, key=lambda row: row["_total"])
    return {"score": worst["比分"], "profit": worst["_total"]}


def best_score_path(match, distribution, combo):
    rows = [score_profit_row(match, distribution, combo, score) for score in score_candidates(match, distribution, combo)]
    if not rows:
        return {"score": "-", "profit": 0}
    best = max(rows, key=lambda row: row["_total"])
    return {"score": best["比分"], "profit": best["_total"]}


def strategy_item_groups(combo):
    active = [item for item in combo if item.get("recommended") and item.get("type") != "empty"]
    correct_scores = [item for item in active if item.get("type") == "correct_score"]
    correct_scores.sort(key=lambda item: (item.get("score", 0), item.get("ev_lift") or -99), reverse=True)
    return {
        "all": active,
        "winner": [item for item in active if item.get("type") == "winner"][:1],
        "handicap": [item for item in active if item.get("type") == "handicap"][:1],
        "total": [item for item in active if item.get("type") == "total"][:1],
        "correct": correct_scores,
    }


def correct_score_path_probability(item, match, distribution):
    score = item.get("selection")
    exact_probability = exact_score_probability([item], score)
    if exact_probability is not None:
        return exact_probability
    category = score_category(match, distribution, score)
    return distribution_category_probability(distribution, category)


def main_path_correct_scores(combo, match, distribution, limit=3):
    correct_scores = [
        item for item in combo
        if item.get("recommended") and item.get("type") == "correct_score" and item.get("selection")
    ]
    ranked = []
    for item in correct_scores:
        alignment = item_direction_alignment(item, match, distribution)
        if alignment < 0.70:
            continue
        probability = correct_score_path_probability(item, match, distribution)
        ranked.append({
            **item,
            "path_probability": probability,
            "main_path_rank_score": probability * 100 + alignment * 10 + (item.get("score", 0) / 100),
        })
    ranked.sort(key=lambda item: item.get("main_path_rank_score", 0), reverse=True)
    return ranked[:limit]


def build_strategy_library(combo, match, distribution):
    groups = strategy_item_groups(combo)
    best_correct = groups["correct"][:1]
    double_correct = groups["correct"][:2]
    main_path_correct = main_path_correct_scores(combo, match, distribution, limit=3)
    strategies = [
        {"code": "A", "name": "当前推荐组合", "items": groups["all"]},
        {"code": "B", "name": "只买最佳波胆", "items": best_correct},
        {"code": "C", "name": "双波胆组合", "items": double_correct},
        {"code": "D", "name": "独赢策略", "items": groups["winner"]},
        {"code": "E", "name": "让球策略", "items": groups["handicap"]},
        {"code": "F", "name": "独赢 + 让球", "items": groups["winner"] + groups["handicap"]},
        {"code": "G", "name": "独赢 + 波胆", "items": groups["winner"] + best_correct},
        {"code": "H", "name": "让球 + 波胆", "items": groups["handicap"] + best_correct},
        {"code": "I", "name": "大小球策略", "items": groups["total"]},
        {"code": "J", "name": "主路径波胆组合", "items": main_path_correct},
    ]
    return [strategy for strategy in strategies if strategy["items"]]


def build_auto_optimized_strategy(combo, match, distribution, total_stake):
    active = [item for item in combo if item.get("recommended") and item.get("type") != "empty"]
    if len(active) < 2:
        return None
    best = None
    max_size = min(5, len(active))
    for size in range(2, max_size + 1):
        for items in combinations(active, size):
            candidate = {"code": "O", "name": "自动优化组合", "items": list(items)}
            evaluated = evaluate_strategy(candidate, match, distribution, total_stake)
            if best is None or evaluated["score"] > best["score"]:
                best = evaluated
    return best


def strategy_weight(item):
    if item.get("path_probability") is not None:
        return max(0.05, item.get("path_probability", 0))
    if item.get("type") == "winner":
        return 1.25
    if item.get("type") == "handicap":
        return 1.15
    if item.get("type") == "total":
        return 0.90
    if item.get("type") == "correct_score":
        return 0.80
    return 0.50


def correlation_adjusted_weight(item, items):
    base = strategy_weight(item)
    score_boost = max(item.get("score", 50), 1) / 70
    ev_boost = 1 + max(item.get("ev_lift") or 0, 0) * 4
    coverage_boost = 0.75 + min(item.get("coverage_rate") or 0, 0.60)
    peers = [peer for peer in items if peer is not item]
    avg_corr = sum(bet_correlation(item, peer) for peer in peers) / len(peers) if peers else 0
    correlation_penalty = 1 - avg_corr * 0.42
    return max(0.03, base * score_boost * ev_boost * coverage_boost * correlation_penalty)


def correlation_penalty_rows(items):
    rows = []
    for item in items:
        peers = [peer for peer in items if peer is not item]
        avg_corr = sum(bet_correlation(item, peer) for peer in peers) / len(peers) if peers else 0
        base = strategy_weight(item)
        score_boost = max(item.get("score", 50), 1) / 70
        ev_boost = 1 + max(item.get("ev_lift") or 0, 0) * 4
        coverage_boost = 0.75 + min(item.get("coverage_rate") or 0, 0.60)
        raw = base * score_boost * ev_boost * coverage_boost
        adjusted = correlation_adjusted_weight(item, items)
        reduction = 1 - adjusted / raw if raw else 0
        rows.append({
            "投注": item.get("name", "-"),
            "基础权重": f"{base:.2f}",
            "推荐分加成": f"{score_boost:.2f}",
            "EV加成": f"{ev_boost:.2f}",
            "覆盖率加成": f"{coverage_boost:.2f}",
            "平均相关性": percent(avg_corr),
            "相关性惩罚": f"-{reduction * 100:.1f}%",
            "调整前权重": f"{raw:.2f}",
            "调整后权重": f"{adjusted:.2f}",
            "仓位": f"{item.get('amount', 0)}元",
        })
    return rows


def allocate_strategy_items(items, total_stake):
    if not items or not total_stake:
        return []
    weight_total = sum(correlation_adjusted_weight(item, items) for item in items)
    allocated = []
    for item in items:
        amount = round_to_hundred(total_stake * correlation_adjusted_weight(item, items) / weight_total) if weight_total else 0
        allocated.append({**item, "amount": amount})
    difference = total_stake - sum(item.get("amount", 0) for item in allocated)
    if allocated and difference:
        target = max(allocated, key=lambda item: correlation_adjusted_weight(item, items))
        target["amount"] = max(0, target.get("amount", 0) + difference)
    allocated = enforce_correct_score_floor(allocated, total_stake)
    for item in allocated:
        item["share"] = item.get("amount", 0) / total_stake if total_stake else 0
    return allocated


def enforce_correct_score_floor(items, total_stake):
    correct_items = [item for item in items if item.get("type") == "correct_score"]
    other_items = [item for item in items if item.get("type") != "correct_score"]
    if not correct_items or not other_items or not total_stake:
        return items
    current = sum(item.get("amount", 0) for item in correct_items)
    target = max(100, round_to_hundred(total_stake * 0.16))
    if current >= target:
        return items
    needed = target - current
    removable = sum(max(0, item.get("amount", 0) - 100) for item in other_items)
    transfer = min(needed, removable)
    if transfer <= 0:
        return items

    donor_total = sum(max(0, item.get("amount", 0) - 100) for item in other_items)
    removed = 0
    for item in other_items:
        capacity = max(0, item.get("amount", 0) - 100)
        reduction = round_to_hundred(transfer * capacity / donor_total) if donor_total else 0
        reduction = min(capacity, reduction)
        item["amount"] -= reduction
        removed += reduction
    if removed < transfer and other_items:
        donor = max(other_items, key=lambda item: item.get("amount", 0))
        extra = min(donor.get("amount", 0) - 100, transfer - removed)
        donor["amount"] -= max(0, extra)
        removed += max(0, extra)

    correct_weight_total = sum(strategy_weight(item) for item in correct_items)
    added = 0
    for item in correct_items:
        addition = round_to_hundred(removed * strategy_weight(item) / correct_weight_total) if correct_weight_total else 0
        item["amount"] += addition
        added += addition
    if added != removed:
        correct_items[0]["amount"] += removed - added
    return items


def item_direction_alignment(item, match, distribution):
    item_type = item.get("type")
    favorite = distribution.get("favorite")
    selection = str(item.get("selection") or item.get("name") or "")
    if item_type == "winner":
        return 1.0 if favorite and favorite in selection else 0.30
    if item_type == "handicap":
        return 0.95
    if item_type == "correct_score":
        parsed = parse_score(item.get("selection"))
        if not parsed:
            return 0.45
        home_goals, away_goals = parsed
        favorite_home = favorite in {team_cn(match["home_cn"]), match["home_cn"]}
        margin = home_goals - away_goals if favorite_home else away_goals - home_goals
        if margin in {1, 2}:
            return 0.90
        if margin >= 3:
            return 0.75
        if margin == 0:
            return 0.35
        return 0.20
    if item_type == "total":
        return 0.35
    return 0.25


def strategy_direction_alignment(items, match, distribution):
    if not items:
        return 0
    weights = [max(item.get("amount", 0), 1) for item in items]
    weighted = sum(
        item_direction_alignment(item, match, distribution) * weight
        for item, weight in zip(items, weights)
    )
    base = weighted / sum(weights)
    has_core_direction = any(item.get("type") in {"winner", "handicap"} for item in items)
    has_total_only = all(item.get("type") == "total" for item in items)
    if has_core_direction:
        base = min(1.0, base + 0.08)
    if has_total_only:
        base = min(base, 0.42)
    return base


def item_strategic_value(item, match, distribution):
    item_type = item.get("type")
    if item_type in {"winner", "handicap"}:
        return 1.0
    if item_type == "correct_score":
        alignment = item_direction_alignment(item, match, distribution)
        if alignment >= 0.90:
            return 0.90
        if alignment >= 0.75:
            return 0.80
        return 0.45
    if item_type == "total":
        return 0.45
    return 0.35


def strategy_strategic_value(items, match, distribution):
    if not items:
        return 0
    weights = [max(item.get("amount", 0), 1) for item in items]
    weighted = sum(
        item_strategic_value(item, match, distribution) * weight
        for item, weight in zip(items, weights)
    )
    return weighted / sum(weights)


def strategy_score(
    ev_yield,
    hit_rate,
    risk_reward,
    max_loss,
    total_stake,
    concentration,
    direction_alignment,
    strategic_value,
):
    if ev_yield >= 0.06:
        ev_points = 32
    elif ev_yield >= 0.03:
        ev_points = 26
    elif ev_yield >= 0:
        ev_points = 18
    elif ev_yield >= -0.03:
        ev_points = 8
    else:
        ev_points = 2
    hit_points = min(28, hit_rate * 38)
    rr_points = min(10, max(0, risk_reward) * 3.5)
    loss_ratio = max_loss / total_stake if total_stake else 1
    if loss_ratio <= 0.50:
        loss_points = 10
    elif loss_ratio <= 0.75:
        loss_points = 7
    else:
        loss_points = 3
    direction_points = direction_alignment * 10
    strategic_points = strategic_value * 14
    concentration_points = max(0, (1 - concentration) * 8)
    raw_total = (
        ev_points
        + hit_points
        + rr_points
        + loss_points
        + direction_points
        + strategic_points
        + concentration_points
    )
    total = round(50 + (raw_total - 50) * 1.35)
    if direction_alignment < 0.45:
        total = min(total, 80)
    return clamp(total), {
        "方向一致性": round(direction_points),
        "战略价值": round(strategic_points),
        "命中率": round(hit_points),
        "EV": round(ev_points),
        "风险收益比": round(rr_points),
        "最大亏损控制": round(loss_points),
        "路径分散度": round(concentration_points),
    }


def evaluate_strategy(strategy, match, distribution, total_stake):
    items = allocate_strategy_items(strategy["items"], total_stake)
    scores = score_candidates(match, distribution, items)
    probabilities = scenario_probability_map(match, distribution, items, scores)
    score_rows = []
    total_probability = 0
    hit_probability = 0
    weighted_profit = 0
    profits = []
    for score in scores:
        row = score_profit_row(match, distribution, items, score)
        probability = probabilities.get(score, 0)
        profit = row["_total"]
        ev_contribution = probability * profit
        row["路径权重"] = percent(probability)
        row["概率×收益"] = f"{percent(probability)} × {row['组合收益']}"
        row["EV贡献"] = f"{ev_contribution:+.0f}"
        row["_ev_contribution"] = ev_contribution
        total_probability += probability
        if profit > 0:
            hit_probability += probability
        weighted_profit += ev_contribution
        profits.append((profit, probability))
        score_rows.append(row)

    if total_probability:
        hit_rate = hit_probability / total_probability
        expected_profit = weighted_profit / total_probability
    else:
        hit_rate = 0
        expected_profit = sum(item.get("amount", 0) * (item.get("actual_ev") or 0) for item in items)

    max_profit = max((profit for profit, _ in profits), default=0)
    min_profit = min((profit for profit, _ in profits), default=-total_stake)
    max_loss = abs(min(0, min_profit))
    variance = 0
    if total_probability:
        variance = sum(probability * ((profit - expected_profit) ** 2) for profit, probability in profits) / total_probability
    volatility = variance ** 0.5
    risk_reward = max_profit / max_loss if max_loss else max_profit / total_stake if total_stake else 0
    coverage = sum(item.get("coverage_rate") or 0 for item in items) / len(items) if items else 0
    concentration = weighted_combo_correlation(items)
    direction_alignment = strategy_direction_alignment(items, match, distribution)
    strategic_value = strategy_strategic_value(items, match, distribution)
    ev_yield = expected_profit / total_stake if total_stake else 0
    capital_efficiency = expected_profit / total_stake if total_stake else 0
    score, score_components = strategy_score(
        ev_yield,
        hit_rate,
        risk_reward,
        max_loss,
        total_stake,
        concentration,
        direction_alignment,
        strategic_value,
    )

    return {
        "code": strategy["code"],
        "name": strategy["name"],
        "items": items,
        "hit_rate": hit_rate,
        "expected_profit": expected_profit,
        "expected_yield": ev_yield,
        "capital_efficiency": capital_efficiency,
        "max_profit": max_profit,
        "max_loss": max_loss,
        "volatility": volatility,
        "risk_reward": risk_reward,
        "coverage": min(1, coverage),
        "concentration": concentration,
        "direction_alignment": direction_alignment,
        "strategic_value": strategic_value,
        "score": score,
        "score_components": score_components,
        "score_rows": score_rows,
    }


def strategy_comparison(match, distribution, combo, total_stake):
    strategies = build_strategy_library(combo, match, distribution)
    evaluated = [evaluate_strategy(strategy, match, distribution, total_stake) for strategy in strategies]
    optimized = build_auto_optimized_strategy(combo, match, distribution, total_stake)
    if optimized:
        evaluated.append(optimized)
    return sorted(evaluated, key=lambda item: item["score"], reverse=True)


def strategy_table_rows(strategies):
    rows = []
    for strategy in strategies:
        rows.append({
            "策略": f"{strategy['code']} · {strategy['name']}",
            "命中率": percent(strategy["hit_rate"]),
            "EV": f"{strategy['expected_profit']:+.0f}",
            "预期收益率": f"{strategy['expected_yield'] * 100:+.1f}%",
            "资金效率": f"{strategy['capital_efficiency'] * 100:+.1f}%",
            "最大盈利": f"{strategy['max_profit']:+.0f}",
            "最大亏损": f"-{strategy['max_loss']:.0f}",
            "盈亏波动": f"{strategy['volatility']:.0f}",
            "风险收益比": f"{strategy['risk_reward']:.2f}",
            "覆盖率": percent(strategy["coverage"]),
            "路径集中度": percent(strategy["concentration"]),
            "方向一致性": percent(strategy["direction_alignment"]),
            "战略价值": percent(strategy["strategic_value"]),
            "综合评分": strategy["score"],
        })
    return rows


def strategy_component_rows(strategies):
    rows = []
    for strategy in strategies:
        row = {"策略": f"{strategy['code']} · {strategy['name']}"}
        row.update({name: f"+{points}" for name, points in (strategy.get("score_components") or {}).items()})
        row["总分"] = strategy["score"]
        rows.append(row)
    return rows


def strategy_direct_comparison_rows(strategies):
    current = next((strategy for strategy in strategies if strategy["code"] == "A"), None)
    best = strategies[0] if strategies else None
    if not current or not best:
        return []
    return [
        {
            "方案": "原始推荐组合",
            "策略": current["name"],
            "命中率": percent(current["hit_rate"]),
            "EV": f"{current['expected_profit']:+.0f}",
            "预期收益率": f"{current['expected_yield'] * 100:+.1f}%",
            "资金效率": f"{current['capital_efficiency'] * 100:+.1f}%",
            "最大盈利": f"{current['max_profit']:+.0f}",
            "最大亏损": f"-{current['max_loss']:.0f}",
            "覆盖率": percent(current["coverage"]),
            "战略价值": percent(current["strategic_value"]),
            "综合评分": current["score"],
        },
        {
            "方案": "策略优化器第一名",
            "策略": best["name"],
            "命中率": percent(best["hit_rate"]),
            "EV": f"{best['expected_profit']:+.0f}",
            "预期收益率": f"{best['expected_yield'] * 100:+.1f}%",
            "资金效率": f"{best['capital_efficiency'] * 100:+.1f}%",
            "最大盈利": f"{best['max_profit']:+.0f}",
            "最大亏损": f"-{best['max_loss']:.0f}",
            "覆盖率": percent(best["coverage"]),
            "战略价值": percent(best["strategic_value"]),
            "综合评分": best["score"],
        },
    ]


def participation_with_portfolio(participation, portfolio):
    advice = participation.get("advice", "-")
    reason = participation.get("reason", "-")
    expected_yield = portfolio.get("expected_yield", 0)
    if expected_yield <= -0.05 and advice in {"强烈参与", "建议参与"}:
        return {
            "advice": "小仓参与",
            "reason": f"方向仍成立，但组合EV为 {expected_yield * 100:.1f}%，负EV偏高，因此自动降为小仓参与。",
        }
    if expected_yield <= -0.08:
        return {
            "advice": "仅观察",
            "reason": f"组合EV为 {expected_yield * 100:.1f}%，负EV过高，建议先观察而不是执行。",
        }
    if expected_yield < 0 and advice in {"强烈参与", "建议参与", "小仓参与"}:
        return {
            "advice": advice,
            "reason": f"{reason} 当前组合EV略负，主要需要关注波胆覆盖成本与相关性暴露。",
        }
    return {"advice": advice, "reason": reason}


def strategy_conclusion(strategies):
    if not strategies:
        return "当前真实盘口不足，暂无法比较策略。"
    best = strategies[0]
    second = strategies[1] if len(strategies) > 1 else None
    if second and best["expected_yield"] < second["expected_yield"] and best["hit_rate"] > second["hit_rate"]:
        return (
            f"策略优化器首选「{best['name']}」。虽然「{second['name']}」预期收益率更高，"
            f"但「{best['name']}」命中率更高、路径更稳，综合评分更优。"
        )
    if best["concentration"] >= 0.75:
        return (
            f"策略优化器首选「{best['name']}」，但路径集中度偏高。"
            "这代表多个投注依赖同一比赛剧本，需要控制总仓位。"
        )
    return (
        f"策略优化器首选「{best['name']}」，综合评分 {best['score']}。"
        "该策略在命中率、EV和风险收益比之间更均衡。"
    )


def strategy_j_comparison(strategies):
    current = next((strategy for strategy in strategies if strategy["code"] == "A"), None)
    main_correct = next((strategy for strategy in strategies if strategy["code"] == "J"), None)
    if not current or not main_correct:
        return None
    if main_correct["score"] > current["score"]:
        return (
            f"策略J「主路径波胆组合」评分 {main_correct['score']}，高于当前推荐组合 {current['score']}。"
            f"它的预期收益率为 {main_correct['expected_yield'] * 100:+.1f}%，"
            f"命中率为 {percent(main_correct['hit_rate'])}。"
            "这说明本场可以把主路径波胆作为激进策略重点观察。"
        )
    return (
        f"当前推荐组合评分 {current['score']}，高于策略J「主路径波胆组合」{main_correct['score']}。"
        f"策略J预期收益率为 {main_correct['expected_yield'] * 100:+.1f}%，"
        f"命中率为 {percent(main_correct['hit_rate'])}。"
        "这说明主路径波胆可以作为进攻型补充，但当前组合在稳定性上更占优。"
    )


def path_analysis_rows_old(distribution, combo):
    favorite = distribution.get("favorite", "热门方")
    underdog = distribution.get("underdog", "弱势方")
    winner = combo_item(combo, "winner")
    handicap = combo_item(combo, "handicap")
    total = combo_item(combo, "total")
    correct = combo_item(combo, "correct_score")

    def row(label, winner_result, handicap_result, total_result, correct_result, note):
        values = [
            profit_text(winner.get("amount"), winner.get("odds"), winner_result),
            profit_text(handicap.get("amount"), handicap.get("odds"), handicap_result),
            profit_text(total.get("amount"), total.get("odds"), total_result),
            profit_text(correct.get("amount"), correct.get("odds"), correct_result),
        ]
        return {
            "结果路径": label,
            "独赢收益": values[0],
            "让球收益": values[1],
            "大小球收益": values[2],
            "波胆收益": values[3],
            "组合总收益": total_known_profit(values),
            "解读": note,
        }

    return [
        row(f"{favorite}只赢1球", "win", "lose", None, "lose", "独赢成立，但深盘承压。"),
        row(f"{favorite}赢2球及以上", "win", "win", None, None, "主逻辑与让球逻辑同时受益，波胆取决于精确比分。"),
        row("平局", "lose", "lose", None, None, "热门方向失效，是组合主要风险。"),
        row(f"{underdog}取胜", "lose", "lose", None, None, "爆冷路径，对主逻辑最不利。"),
    ]


def render_rating_breakdown(decision):
    rows = (decision.get("direction_confidence") or {}).get("components") or []
    if not rows:
        return
    st.markdown("**方向把握计算**")
    cols = st.columns(len(rows))
    for col, row in zip(cols, rows):
        with col:
            with st.container(border=True):
                st.metric(row["name"], f"+{row['points']}", f"/ {row['max_points']}")
                st.caption(row["reason"])
    odds_value = decision.get("odds_value") or {}
    if odds_value:
        st.caption(f"赔率价值计算：{odds_value.get('reason')}")
        value_rows = odds_value.get("components") or []
        if value_rows:
            st.markdown("**赔率价值计算**")
            value_cols = st.columns(len(value_rows))
            for col, row in zip(value_cols, value_rows):
                with col:
                    with st.container(border=True):
                        st.metric(row["name"], f"+{row['points']}", f"/ {row['max_points']}")
                        st.caption(row["reason"])


def actual_odds_example(match):
    return f"""独赢,{team_cn(match['home_cn'])},1.62
让球,{team_cn(match['home_cn'])},-1,2.05
大小球,Under 2.5,1.91
波胆,1:0,6.80
波胆,2:0,7.20"""


USER_ODDS_CACHE_DIR = Path("data/cache/user_odds")
USER_ODDS_CACHE_TTL = timedelta(days=7)


def user_odds_slug(match):
    raw = f"{match['home_cn']}_vs_{match['away_cn']}"
    slug = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "_", raw).strip("_")
    return slug or "match"


def user_odds_cache_path(match):
    return USER_ODDS_CACHE_DIR / f"{user_odds_slug(match)}.json"


def load_user_odds_cache(match):
    path = user_odds_cache_path(match)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    updated_at = data.get("updated_at")
    if updated_at:
        try:
            updated = datetime.fromisoformat(updated_at)
        except ValueError:
            updated = None
        if updated and updated.tzinfo is None:
            updated = updated.astimezone()
        if updated and datetime.now().astimezone() - updated > USER_ODDS_CACHE_TTL:
            return None
    return data


def save_user_odds_cache(match, raw_text, parsed):
    USER_ODDS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone()
    data = {
        "schema_version": 1,
        "match": {
            "home": match["home_cn"],
            "away": match["away_cn"],
            "display": f"{team_cn(match['home_cn'])} vs {team_cn(match['away_cn'])}",
        },
        "profile": {
            "id": "default",
            "name": "我的赔率A",
            "source": "manual",
        },
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "raw_text": raw_text,
        "record_count": len(parsed.get("items") or []),
    }
    path = user_odds_cache_path(match)
    if path.exists():
        existing = load_user_odds_cache(match) or {}
        data["created_at"] = existing.get("created_at", data["created_at"])
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def clear_user_odds_cache(match):
    path = user_odds_cache_path(match)
    if path.exists():
        path.unlink()


def format_cache_time(value):
    if not value:
        return "-"
    try:
        parsed = datetime.fromisoformat(value).astimezone(ZoneInfo("Asia/Shanghai"))
    except ValueError:
        return value
    return parsed.strftime("%Y-%m-%d %H:%M")


def render_actual_odds_input(match):
    key = f"actual_odds_{match['home_cn']}_{match['away_cn']}"
    raw_key = f"{key}_raw"
    cache = load_user_odds_cache(match)
    if raw_key not in st.session_state and cache:
        st.session_state[raw_key] = cache.get("raw_text", "")
        st.session_state[f"{key}_restored"] = True
    current_raw = st.session_state.get(raw_key, "")
    with st.container(border=True):
        st.markdown('<div class="section-title">我的实际赔率</div>', unsafe_allow_html=True)
        st.caption("可选输入。这里填写你自己实际能买到的赔率，系统会优先用它评估价值；不填写则继续使用市场标准赔率。")
        if cache:
            st.info(
                f"当前已载入赔率：{format_cache_time(cache.get('updated_at'))} · "
                f"{cache.get('match', {}).get('display', '')} · "
                f"{cache.get('record_count', 0)}条赔率记录 · "
                f"{cache.get('profile', {}).get('name', '我的赔率A')}"
            )
            if st.session_state.get(f"{key}_restored"):
                st.caption("已恢复上次录入赔率。")

        restore_col, clear_col = st.columns(2)
        with restore_col:
            if st.button("恢复上次赔率", key=f"{key}_restore", disabled=not bool(cache)):
                st.session_state[raw_key] = (cache or {}).get("raw_text", "")
                st.session_state[f"{key}_restored"] = True
                st.rerun()
        with clear_col:
            if st.button("清空已保存赔率", key=f"{key}_clear", disabled=not bool(cache)):
                clear_user_odds_cache(match)
                st.session_state[raw_key] = ""
                st.session_state[f"{key}_restored"] = False
                st.rerun()

        with st.form(key=f"{key}_form"):
            raw_input = st.text_area(
                "粘贴实际赔率",
                value=current_raw,
                height=210,
                placeholder=actual_odds_example(match),
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("应用实际赔率", type="primary")
        if submitted:
            st.session_state[raw_key] = raw_input
            current_raw = raw_input
        raw = current_raw
        parsed = parse_actual_odds(raw)
        if submitted and raw.strip():
            cache = save_user_odds_cache(match, raw, parsed)
            st.success(f"已保存实际赔率：{format_cache_time(cache.get('updated_at'))} · {len(parsed.get('items') or [])}条记录")
        if parsed.get("items"):
            rows = [
                {"盘口": item["type"], "方向": item["selection"], "实际赔率": fmt_odds(item["odds"])}
                for item in parsed["items"]
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.caption("未应用实际赔率：推荐组合和赔率价值暂按市场标准赔率计算。")
        with st.expander("支持的输入格式", expanded=False):
            st.code(actual_odds_example(match), language="text")
            st.caption("一行一个投注，适合从 Excel 复制；旧的多行格式仍然兼容。")
        return parsed


def render_core_decision(match, odds, api_football_data, distribution, decision, betting_opinion, actual_odds=None):
    combo = recommendation_combo(match, odds, api_football_data, distribution, actual_odds)
    initial_combo_with_amounts = stake_amounts(combo, decision)
    total_stake, total_reason = recommended_total_stake(decision)
    strategies = strategy_comparison(match, distribution, initial_combo_with_amounts, total_stake)
    selected_strategy = strategies[0] if strategies else None
    combo_with_amounts = selected_strategy["items"] if selected_strategy else initial_combo_with_amounts
    portfolio = portfolio_metrics(combo_with_amounts)
    worst_path = worst_score_path(match, distribution, combo_with_amounts)
    best_path = best_score_path(match, distribution, combo_with_amounts)
    with st.container(border=True):
        st.markdown('<div class="section-title">核心决策</div>', unsafe_allow_html=True)

        direction = decision.get("direction_confidence") or {}
        odds_value = decision.get("odds_value") or {}
        participation = participation_with_portfolio(decision.get("participation_advice") or {}, portfolio)
        stake = decision.get("recommended_stake") or {}
        decision_cols = st.columns(4)
        decision_cols[0].metric("方向把握", f"{direction.get('score', decision['final_confidence_score'])} / 100")
        decision_cols[0].caption(direction.get("summary") or direction.get("level", "-"))
        decision_cols[1].metric("赔率价值", rating_badge(odds_value.get("rating", decision["value_rating"])))
        decision_cols[1].caption(odds_value.get("reason", decision["value_rating_meaning"]))
        decision_cols[2].metric("参与建议", participation.get("advice", "-"))
        decision_cols[2].caption(participation.get("reason", "-"))
        decision_cols[3].metric("推荐仓位", f"{stake.get('amount', total_stake)}元")
        decision_cols[3].caption(stake.get("reason", total_reason))
        standard_stake = stake.get("amount", total_stake)
        conservative_stake = round_to_hundred(standard_stake * 0.7)
        aggressive_stake = round_to_hundred(standard_stake * 1.3)
        decision_cols[3].caption(
            f"信心区间：保守 {conservative_stake} · 标准 {standard_stake} · 激进 {aggressive_stake}"
        )

        st.markdown("**推荐投注组合**")
        if selected_strategy:
            st.caption(f"推荐组合来源：策略优化器第一名「{selected_strategy['name']}」（{selected_strategy['score']}分）。")
        portfolio_cols = st.columns(5)
        portfolio_cols[0].metric("组合EV", f"{portfolio['expected_profit']:+d}元")
        portfolio_cols[0].caption("按当前组合的长期期望收益估算。")
        portfolio_cols[1].metric("预期收益率", f"{portfolio['expected_yield'] * 100:+.1f}%")
        portfolio_cols[1].caption("组合EV / 推荐总仓位。")
        portfolio_cols[2].metric("最大亏损", f"-{portfolio['max_loss']}元")
        portfolio_cols[2].caption("所有推荐项同时失效时的风险。")
        portfolio_cols[3].metric("最佳路径收益", best_path["score"], f"{best_path['profit']:+d}元")
        portfolio_cols[3].caption("当前候选比分里的最高收益。")
        portfolio_cols[4].metric("最差路径收益", worst_path["score"], f"{worst_path['profit']:+d}元")
        portfolio_cols[4].caption("当前组合最容易受伤的比分路径。")
        st.caption(
            f"路径相关性约 {portfolio['weighted_correlation'] * 100:.0f}%。"
            "独赢、让球和波胆通常高度相关，因此组合器会限制同一路径仓位过度集中。"
        )
        if portfolio["expected_profit"] < 0 and participation.get("advice") in {"强烈参与", "建议参与", "小仓参与"}:
            st.warning(
                "组合EV当前为负，但参与建议仍成立：负值主要可能来自波胆覆盖成本或个别保护仓位。"
                f"核心盘口EV约 {portfolio['core_expected_profit']:+d} 元，"
                f"波胆覆盖EV约 {portfolio['correct_score_expected_profit']:+d} 元。"
                "如果只追求EV，可降低波胆仓位；如果重视路径覆盖，可保留低金额波胆。"
            )

        if combo_with_amounts:
            overview_rows = market_odds_overview_rows(initial_combo_with_amounts)
            if overview_rows:
                st.markdown("**实际赔率 VS 市场赔率**")
                st.dataframe(pd.DataFrame(overview_rows), use_container_width=True, hide_index=True)
                completeness = actual_odds_completeness(initial_combo_with_amounts)
                if completeness["total"]:
                    st.caption(
                        f"实际赔率完整度：已录入 {completeness['entered']} / {completeness['total']}，"
                        f"完整度 {completeness['ratio'] * 100:.0f}%。"
                    )
                    if completeness["missing"]:
                        st.warning(
                            "实际赔率录入不完整，策略结果可能失真。缺少："
                            + "、".join(completeness["missing"])
                        )

            if selected_strategy:
                reason_rows = optimized_strategy_reason_rows(selected_strategy, match, distribution)
                if reason_rows:
                    st.markdown("**自动优化组合生成原因**")
                    st.dataframe(pd.DataFrame(reason_rows), use_container_width=True, hide_index=True)
                discarded_rows = discarded_bet_rows(initial_combo_with_amounts, selected_strategy)
                if discarded_rows:
                    with st.expander("未进入优化组合的原因", expanded=False):
                        st.dataframe(pd.DataFrame(discarded_rows), use_container_width=True, hide_index=True)

            combo_cols = st.columns(len(combo_with_amounts))
            for index, (col, item) in enumerate(zip(combo_cols, combo_with_amounts), start=1):
                with col:
                    with st.container(border=True):
                        st.caption(f"投注{index} · {combo_role(index, item)}")
                        if item.get("recommended"):
                            st.metric(item["name"], f"{item['amount']}元")
                            st.caption(f"占比 {int(item.get('share', 0) * 100)}% · 使用赔率 {fmt_odds(item.get('odds'))}")
                            st.caption(f"{score_stars(item.get('score', 0))} · 推荐指数")
                            if item.get("actual_odds"):
                                st.caption(f"市场标准 {fmt_odds(item.get('standard_odds'))} · 实际赔率 {fmt_odds(item.get('actual_odds'))}")
                            else:
                                st.caption(f"市场标准 {fmt_odds(item.get('standard_odds'))}")
                            if item.get("ev_lift") is not None:
                                rank_text = f" · EV排名 {item['ev_rank']}" if item.get("ev_rank") else ""
                                st.caption(f"EV提升 {item['ev_lift'] * 100:+.1f}%{rank_text} · 推荐分 {item.get('score', 0)}")
                            if item.get("coverage_rate") is not None:
                                st.caption(f"覆盖率 {item['coverage_rate'] * 100:.0f}% · {recommendation_reason(item)}")
                            st.caption(item.get("reason", item.get("source", "真实盘口")))
                        else:
                            st.metric(item.get("slot", f"投注{index}"), "不推荐")
                            st.caption(item.get("not_recommended_reason") or item.get("reason") or "当前没有达到推荐阈值。")
            if selected_strategy:
                with st.expander("展开推荐组合", expanded=False):
                    st.caption("推荐组合来自策略优化器第一名，因此这里展示的是最终执行层组合。")
                    render_strategy_detail(selected_strategy, match, distribution)
            matrix_rows = correlation_matrix_rows(combo_with_amounts)
            if matrix_rows:
                with st.expander("组合相关性矩阵", expanded=False):
                    st.caption("相关性越高，说明多个投注依赖同一比赛路径；组合器会降低过度重叠的仓位。")
                    st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)
                    penalty_rows = correlation_penalty_rows(combo_with_amounts)
                    if penalty_rows:
                        st.markdown("**相关性惩罚如何影响仓位**")
                        st.dataframe(pd.DataFrame(penalty_rows), use_container_width=True, hide_index=True)

            if strategies:
                st.markdown("**策略优化器**")
                leader_cols = st.columns(3)
                for col, strategy in zip(leader_cols, strategies[:3]):
                    with col:
                        with st.container(border=True):
                            st.caption(f"策略{strategy['code']}")
                            st.metric(strategy["name"], f"{strategy['score']}分")
                            st.caption(
                                f"命中率 {percent(strategy['hit_rate'])} · "
                                f"EV {strategy['expected_yield'] * 100:+.1f}% · "
                                f"方向 {percent(strategy['direction_alignment'])}"
                            )
                st.info(strategy_conclusion(strategies))
                j_note = strategy_j_comparison(strategies)
                if j_note:
                    st.caption(j_note)
                comparison_rows = strategy_direct_comparison_rows(strategies)
                if comparison_rows:
                    st.markdown("**原始推荐组合 vs 策略第一名**")
                    st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)
                st.dataframe(pd.DataFrame(strategy_table_rows(strategies)), use_container_width=True, hide_index=True)
                with st.expander("策略评分来源", expanded=False):
                    st.dataframe(pd.DataFrame(strategy_component_rows(strategies)), use_container_width=True, hide_index=True)
                with st.expander(f"查看详情：{strategies[0]['name']}", expanded=False):
                    render_strategy_detail(strategies[0], match, distribution)
                with st.expander("查看全部策略详情", expanded=False):
                    for strategy in strategies:
                        render_strategy_detail(strategy, match, distribution)
                        st.divider()
        else:
            st.info("当前没有足够真实盘口生成投注组合。")
        st.caption("实际赔率优先；未输入时使用真实市场标准赔率。禁止使用估算波胆赔率。")

        top_cols = st.columns(2)
        recommendation = decision["final_recommendation"]
        top_cols[0].metric("推荐方向", bet_cn(recommendation["bet"]))
        top_cols[0].caption(recommendation["reason"][0])
        top_cols[1].metric("赔率价值分", f"{odds_value.get('score', 0)} / 100")
        top_cols[1].caption(decision["value_rating_meaning"])

        with st.expander("方向把握与赔率价值计算", expanded=False):
            render_rating_breakdown(decision)

        risk_cols = st.columns(2)
        upset = decision["upset_index"]
        with risk_cols[0]:
            st.metric("爆冷指数", f"{upset['score']} / 100", upset["meaning"])
            st.caption(upset["reason"])
        with risk_cols[1]:
            st.metric("极端路径风险", worst_path["score"], f"{worst_path['profit']:+d}元")
            st.caption("这里的极端路径定义为：最容易导致当前推荐组合亏损的比分。")

        exposure = distribution.get("risk_exposure") or {}
        st.markdown("**风险暴露**")
        lose_paths = exposure.get("lose_paths", [])
        exposure_cols = st.columns(3)
        exposure_cols[0].metric("主要风险路径", lose_paths[0] if lose_paths else "-")
        exposure_cols[1].metric("次要风险路径", lose_paths[1] if len(lose_paths) > 1 else "-")
        exposure_cols[2].metric("极端风险路径", lose_paths[-1] if lose_paths else "-")
        st.caption(exposure.get("meaning", ""))

        st.markdown("**结果覆盖分析**")
        st.caption("比分级收益分析。使用实际可成交赔率优先计算；未输入时使用市场标准赔率。")
        st.dataframe(pd.DataFrame(path_analysis_rows(match, distribution, combo_with_amounts)), use_container_width=True, hide_index=True)


def summarize_form(fixtures, team_id):
    results = []
    goals_for = 0
    goals_against = 0

    for item in fixtures[:5]:
        teams = item.get("teams", {})
        goals = item.get("goals", {})
        home = teams.get("home", {})
        away = teams.get("away", {})
        home_goals = goals.get("home")
        away_goals = goals.get("away")
        if home_goals is None or away_goals is None:
            continue

        is_home = home.get("id") == team_id
        team_goals = home_goals if is_home else away_goals
        opponent_goals = away_goals if is_home else home_goals
        goals_for += team_goals
        goals_against += opponent_goals

        if team_goals > opponent_goals:
            results.append("W")
        elif team_goals < opponent_goals:
            results.append("L")
        else:
            results.append("D")

    return {
        "form": results,
        "gf": goals_for,
        "ga": goals_against,
        "wins": results.count("W"),
        "draws": results.count("D"),
        "losses": results.count("L"),
        "avg_gf": goals_for / len(results) if results else 0,
        "avg_ga": goals_against / len(results) if results else 0,
    }


def summarize_static_form(rows, count):
    selected = rows[:count]
    form = [row["result"] for row in selected]
    gf = sum(row["gf"] for row in selected)
    ga = sum(row["ga"] for row in selected)
    return {
        "form": form,
        "gf": gf,
        "ga": ga,
        "wins": form.count("W"),
        "draws": form.count("D"),
        "losses": form.count("L"),
        "avg_gf": gf / len(form) if form else 0,
        "avg_ga": ga / len(form) if form else 0,
    }


def team_form_summary(team, fixtures):
    live_summary = summarize_form(fixtures, team.get("id"))
    if live_summary["form"]:
        return {
            "source": "API-Football",
            "last5": live_summary,
            "last10": live_summary,
        }

    static_rows = static_recent_form_for(team.get("name"))
    return {
        "source": "静态赛果库",
        "last5": summarize_static_form(static_rows, 5),
        "last10": summarize_static_form(static_rows, 10),
    }


def render_recent_form(api_football_data):
    fixture_result = api_football_data.get("fixture_result") or {}
    fixture = api_football_data.get("fixture") or {}
    home_team = fixture_result.get("home_team") or fixture.get("home_team") or {}
    away_team = fixture_result.get("away_team") or fixture.get("away_team") or {}
    home_recent = api_football_data.get("home_recent") or []
    away_recent = api_football_data.get("away_recent") or []

    if not home_team or not away_team:
        return

    with st.container(border=True):
        st.markdown('<div class="section-title">近期状态</div>', unsafe_allow_html=True)
        left, right = st.columns(2)
        for column, team, fixtures in [
            (left, home_team, home_recent),
            (right, away_team, away_recent),
        ]:
            summary = team_form_summary(team, fixtures)
            with column:
                st.markdown(f"**{team_cn(team.get('name', '-'))}**")
                if summary["last5"]["form"]:
                    st.markdown(
                        '<div class="form-strip">'
                        + "".join(
                            f'<span class="form-tag form-{result}">{result}</span>'
                            for result in summary["last5"]["form"]
                        )
                        + '</div>',
                        unsafe_allow_html=True,
                    )
                    w_col, gf_col, ga_col = st.columns(3)
                    w_col.metric("最近5场", " ".join(summary["last5"]["form"]))
                    gf_col.metric("进球 / 失球", f"{summary['last5']['gf']} / {summary['last5']['ga']}")
                    ga_col.metric("胜平负", f"{summary['last5']['wins']}胜 {summary['last5']['draws']}平 {summary['last5']['losses']}负")
                    t1, t2, t3 = st.columns(3)
                    t1.metric("最近10场", " ".join(summary["last10"]["form"]))
                    t2.metric("总进球 / 总失球", f"{summary['last10']['gf']} / {summary['last10']['ga']}")
                    t3.metric("场均进失球", f"{summary['last10']['avg_gf']:.1f} / {summary['last10']['avg_ga']:.1f}")
                    st.caption(f"数据来源：{summary['source']}")
                else:
                    st.info("近期战绩样本不足")


def render_match_winner(match, odds, api_football_data):
    with st.container(border=True):
        st.markdown('<div class="section-title">胜平负赔率</div>', unsafe_allow_html=True)
        if not odds.get("found"):
            st.info("未找到盘口数据：The Odds API 当前没有返回该比赛的胜平负市场。")
            return
        fixture = api_football_data.get("fixture") or {}
        home_name = team_cn(fixture.get("home_team", {}).get("name") or match["home_cn"])
        away_name = team_cn(fixture.get("away_team", {}).get("name") or match["away_cn"])
        implied = odds.get("implied_probabilities") or {}
        col1, col2, col3 = st.columns(3)
        with col1:
            probability_bar(home_name, implied.get("home_win", 0), fmt(odds.get("home_win")))
        with col2:
            probability_bar("平局", implied.get("draw", 0), fmt(odds.get("draw")))
        with col3:
            probability_bar(away_name, implied.get("away_win", 0), fmt(odds.get("away_win")))
        favorite_label, favorite_prob = max(
            [(home_name, implied.get("home_win", 0)), ("平局", implied.get("draw", 0)), (away_name, implied.get("away_win", 0))],
            key=lambda item: item[1],
        )
        st.info(f"市场当前认为最可能结果是：{favorite_label}，概率约 {percent(favorite_prob)}。")


def render_handicap(match, api_football_data):
    with st.container(border=True):
        st.markdown('<div class="section-title">亚洲让球盘</div>', unsafe_allow_html=True)
        handicap = (api_football_data or {}).get("asian_handicap") or {}
        if not handicap.get("found"):
            st.info(handicap.get("message", "未找到盘口数据：API-Football 当前没有返回该比赛的亚洲让球盘。"))
            return

        rows = handicap.get("rows") or []
        bookmakers = handicap.get("bookmakers") or []
        summary = asian_handicap_summary(rows)
        st.success(handicap.get("message", "已获取真实亚洲让球盘。"))
        st.caption(
            f"数据来源：{handicap.get('source')} · "
            f"博彩公司：{', '.join(bookmakers[:6]) or '-'}"
        )
        if summary.get("available"):
            c1, c2, c3 = st.columns(3)
            c1.metric("主盘口", summary.get("main_value"))
            c2.metric("市场均值", f"{summary.get('avg_odds'):.2f}" if summary.get("avg_odds") else "-")
            c3.metric("最佳赔率", f"{summary.get('best_odds'):.2f}" if summary.get("best_odds") else "-")
            st.caption("主盘口公司：" + (", ".join(summary.get("bookmakers", [])[:6]) or "-"))
        with st.expander("展开全部盘口"):
            all_rows = [
                {
                    "博彩公司": row.get("bookmaker"),
                    "市场": row.get("market"),
                    "盘口": row.get("value"),
                    "赔率": row.get("odd"),
                }
                for row in rows
            ]
            st.dataframe(pd.DataFrame(all_rows), use_container_width=True, hide_index=True)


def render_totals(odds):
    with st.container(border=True):
        st.markdown('<div class="section-title">大小球盘口</div>', unsafe_allow_html=True)
        markets = odds.get("over_under") or []
        if not markets:
            st.info("未找到盘口数据：The Odds API 当前没有返回该比赛的大小球盘口。")
            return

        main_line, selected = consensus_market(markets)
        bookmakers = sorted({market.get("bookmaker") for market in selected if market.get("bookmaker")})
        best_over = max((market.get("over_odds") for market in selected if market.get("over_odds")), default=None)
        best_under = max((market.get("under_odds") for market in selected if market.get("under_odds")), default=None)
        over_values = [market.get("over_odds") for market in selected if market.get("over_odds")]
        under_values = [market.get("under_odds") for market in selected if market.get("under_odds")]
        avg_over = sum(over_values) / max(1, len(over_values))
        avg_under = sum(under_values) / max(1, len(under_values))

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("主流总进球", f"{fmt(main_line)} 球")
        col2.metric("市场均值", f"{avg_over:.2f} / {avg_under:.2f}")
        col3.metric("大球最佳赔率", fmt(best_over))
        col4.metric("小球最佳赔率", fmt(best_under))
        st.caption("主要公司：" + (", ".join(bookmakers[:3]) if bookmakers else "-"))
        if abs(avg_over - avg_under) <= 0.08:
            st.info("大小球价格接近，市场对总进球数暂未形成明显方向。")
        elif avg_over < avg_under:
            st.info("大球赔率更低，市场略偏向比赛打开、进球数偏高。")
        else:
            st.info("小球赔率更低，市场略偏向比赛节奏谨慎、进球数偏低。")

        with st.expander("展开全部赔率"):
            st.dataframe(markets, use_container_width=True, hide_index=True)


def render_correct_score_market(api_football_data):
    correct_score = (api_football_data or {}).get("correct_score") or {}
    with st.container(border=True):
        st.markdown('<div class="section-title">真实波胆盘口</div>', unsafe_allow_html=True)
        if not correct_score.get("found"):
            st.info(correct_score.get("message", "真实波胆盘口暂未返回。"))
            st.caption("波胆盘口未接入前，不参与推荐组合、收益曲线或风险暴露计算。")
            return

        rows = correct_score.get("rows") or []
        summary = correct_score_summary(rows)
        st.success(correct_score.get("message", "已获取真实波胆盘口。"))
        st.caption(
            f"数据来源：{correct_score.get('source')} · "
            f"博彩公司：{', '.join(correct_score.get('bookmakers', [])[:6]) or '-'}"
        )
        hot_rows = [
            {
                "比分": row.get("score"),
                "市场均值赔率": f"{row.get('avg_odds'):.2f}" if row.get("avg_odds") else "-",
                "最高赔率": f"{row.get('best_odds'):.2f}" if row.get("best_odds") else "-",
                "最低赔率": f"{row.get('min_odds'):.2f}" if row.get("min_odds") else "-",
                "博彩公司": ", ".join(row.get("bookmakers", [])[:4]),
            }
            for row in summary.get("hot", [])
        ]
        st.dataframe(pd.DataFrame(hot_rows), use_container_width=True, hide_index=True)
        with st.expander("展开全部波胆"):
            all_rows = [
                {
                    "博彩公司": row.get("bookmaker"),
                    "比分": row.get("score"),
                    "赔率": row.get("odd"),
                }
                for row in rows
            ]
            st.dataframe(pd.DataFrame(all_rows), use_container_width=True, hide_index=True)


def render_value(value_analysis):
    with st.container(border=True):
        st.markdown('<div class="section-title">市场价值分析</div>', unsafe_allow_html=True)
        if not value_analysis.get("available"):
            st.info("市场价值分析暂不可用")
            return
        rows = value_analysis.get("rows", [])
        main = max(rows, key=lambda row: abs(row.get("difference", 0))) if rows else None
        if value_analysis.get("has_value"):
            st.warning("⚠ 发现潜在价值机会")
        else:
            st.info("🟢 暂无显著市场分歧")
        if main:
            col1, col2, col3 = st.columns(3)
            col1.metric("Odds API", percent(main["odds_api"]))
            col2.metric("Polymarket", percent(main["polymarket"]))
            col3.metric("分歧幅度", percent(abs(main["difference"])))


def render_polymarket(match, api_football_data, polymarket):
    with st.container(border=True):
        st.markdown('<div class="section-title">Polymarket 预测市场</div>', unsafe_allow_html=True)
        if not polymarket.get("found"):
            st.info(polymarket.get("message", "Polymarket 暂未返回对应市场"))
            return
        fixture = api_football_data.get("fixture") or {}
        home_name = team_cn(fixture.get("home_team", {}).get("name") or match["home_cn"])
        away_name = team_cn(fixture.get("away_team", {}).get("name") or match["away_cn"])
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric(home_name, percent(polymarket.get("home_win", 0)))
        col2.metric("平局", percent(polymarket.get("draw", 0)))
        col3.metric(away_name, percent(polymarket.get("away_win", 0)))
        col4.metric("成交量", money(polymarket.get("volume")))
        col5.metric("流动性", money(polymarket.get("liquidity")))
        if polymarket.get("event_url"):
            st.link_button("打开 Polymarket 市场", polymarket["event_url"])


def render_market_consistency(match, odds, polymarket):
    with st.container(border=True):
        st.markdown('<div class="section-title">市场一致性分析</div>', unsafe_allow_html=True)
        odds_probs = odds.get("implied_probabilities") if odds.get("found") else None
        if not odds_probs or not polymarket.get("found"):
            st.info("传统赔率市场与 Polymarket 暂缺少可直接比较的数据。")
            return
        labels = [
            (team_cn(match["home_cn"]), odds_probs.get("home_win", 0), polymarket.get("home_win", 0)),
            ("平局", odds_probs.get("draw", 0), polymarket.get("draw", 0)),
            (team_cn(match["away_cn"]), odds_probs.get("away_win", 0), polymarket.get("away_win", 0)),
        ]
        largest = max(labels, key=lambda item: abs(item[2] - item[1]))
        gap = abs(largest[2] - largest[1])
        if gap >= 0.05:
            st.warning(f"赔率市场与 Polymarket 在 {largest[0]} 方向存在明显分歧，差异约 {percent(gap)}。")
        else:
            st.success("赔率市场与 Polymarket 观点整体一致，暂未发现明显市场错价。")
        for label, odds_value, poly_value in labels:
            st.write(f"**{label}**")
            cols = st.columns(3)
            cols[0].metric("赔率市场", percent(odds_value))
            cols[1].metric("Polymarket", percent(poly_value))
            cols[2].metric("差异", percent(poly_value - odds_value))


def render_predicted_lineup_for_team(team_name):
    lineup = predicted_lineup_for(team_name)
    st.markdown(f"**{team_cn(team_name)}**")
    st.caption("市场预测首发，不是官方首发")
    if not lineup:
        st.info("暂无足够阵容样本，暂不生成预测首发")
        return

    st.metric("预测阵型", lineup["formation"])
    st.write(f"门将：{', '.join(lineup['goalkeeper'])}")
    st.write(f"后卫：{', '.join(lineup['defenders'])}")
    st.write(f"中场：{', '.join(lineup['midfielders'])}")
    st.write(f"前锋：{', '.join(lineup['forwards'])}")
    st.write(f"关键球员：{', '.join(lineup.get('key_players', []))}")


def render_storylines(match, betting_opinion, decision):
    with st.container(border=True):
        st.markdown('<div class="section-title">本场关注点</div>', unsafe_allow_html=True)
        for story in build_storylines(match, betting_opinion, decision):
            st.markdown(f'<div class="story-item">{story}</div>', unsafe_allow_html=True)


def render_risk_notes(match, decision):
    with st.container(border=True):
        st.markdown('<div class="section-title">风险提示</div>', unsafe_allow_html=True)
        for note in build_risk_notes(match, decision):
            st.markdown(f'<div class="warning-item">{note}</div>', unsafe_allow_html=True)


def render_risk_analysis(match, decision, distribution, odds, polymarket, api_football_data):
    with st.container(border=True):
        st.markdown('<div class="section-title">风险分析</div>', unsafe_allow_html=True)
        disagreement = decision["market_disagreement"]
        upset = decision["upset_index"]
        scenarios = build_extreme_scenarios(distribution)
        risk_cols = st.columns(4)
        with risk_cols[0]:
            render_score_card("市场分歧指数", disagreement["score"], disagreement_label(disagreement["score"]), disagreement["reason"])
        with risk_cols[1]:
            render_score_card("爆冷指数", upset["score"], upset["meaning"], upset["reason"])
        with risk_cols[2]:
            top_extreme = scenarios[0] if scenarios else {"level": "低", "probability": 0, "note": "暂无明显极端路径。"}
            st.metric("极端路径风险", top_extreme["level"], percent(top_extreme["probability"]))
            st.caption(top_extreme["note"])
        with risk_cols[3]:
            missing = []
            if not odds.get("found"):
                missing.append("赔率")
            if not polymarket.get("found"):
                missing.append("Polymarket")
            if not api_football_data.get("fixture"):
                missing.append("比赛信息")
            quality = "高" if not missing else "中" if len(missing) == 1 else "低"
            st.metric("数据质量", quality)
            st.caption("缺失：" + "、".join(missing) if missing else "核心市场数据完整。")

        st.markdown("**重点风险**")
        for note in build_risk_notes(match, decision):
            st.markdown(f'<div class="warning-item">{note}</div>', unsafe_allow_html=True)
        exposure = distribution.get("risk_exposure") or {}
        if exposure:
            st.markdown("**最危险比分路径**")
            st.write(" / ".join(exposure.get("lose_paths", [])))
            st.caption(exposure.get("meaning", ""))


def render_injuries_lineups(api_football_data):
    with st.container(border=True):
        st.markdown('<div class="section-title">预测首发与伤病</div>', unsafe_allow_html=True)
        injuries = api_football_data.get("injuries") or []
        lineups = api_football_data.get("lineups") or []
        fixture = api_football_data.get("fixture") or {}
        home_name = fixture.get("home_team", {}).get("name")
        away_name = fixture.get("away_team", {}).get("name")
        has_predicted = bool(predicted_lineup_for(home_name)) or bool(predicted_lineup_for(away_name))
        if home_name and away_name and has_predicted:
            st.markdown("**市场预测首发**")
            pred_left, pred_right = st.columns(2)
            with pred_left:
                render_predicted_lineup_for_team(home_name)
            with pred_right:
                render_predicted_lineup_for_team(away_name)
            st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**伤病信息**")
            if injuries:
                st.dataframe(injuries, use_container_width=True, hide_index=True)
            else:
                st.info("暂无公开伤病信息")
        with col2:
            with st.expander("官方首发状态"):
                if lineups:
                    st.dataframe(lineups, use_container_width=True, hide_index=True)
                else:
                    st.info("官方首发尚未公布")


def render_technical_notes(odds, api_football_data):
    with st.expander("开发者信息"):
        notes = [
            "赔率来源：The Odds API",
            "比赛、伤病、首发来源：API-Football",
            "预测市场来源：Polymarket",
        ]
        if not odds.get("found"):
            notes.append(f"赔率状态：{odds.get('message')}")
        if api_football_data.get("error"):
            notes.append(f"比赛数据状态：{api_football_data.get('error')}")
        for note in notes:
            st.caption(note)


def render_detail_data_source(odds=None, polymarket=None, fixture=None):
    with st.container(border=True):
        st.markdown('<div class="section-title">数据来源</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        cols[0].metric("赛程 / 比分", (fixture or {}).get("source", "API-Football / 缓存"))
        cols[1].metric("赔率", (odds or {}).get("source", "The Odds API"))
        cols[2].metric("预测市场", "Polymarket" if (polymarket or {}).get("found") else "暂无市场")
        cols[3].metric("缓存状态", "按模块缓存")
        st.caption("赛程优先级：WorldCup2026 API → ESPN → 项目缓存 → 本地备用数据。")


def schedule_match_text(fixture):
    home = fixture.get("home_team", {}).get("name") or ""
    away = fixture.get("away_team", {}).get("name") or ""
    return f"{home} vs {away}"


def fixture_time_text(fixture, compact=False):
    kickoff = fixture_local_datetime(fixture)
    if not kickoff:
        return "时间待定"
    if fixture.get("source") == "WorldCup2026 API":
        return kickoff.strftime("%m-%d %H:%M") + " 当地时间"
    return kickoff.strftime("%m-%d %H:%M CST" if compact else "%Y-%m-%d %H:%M CST")


def date_until_world_cup():
    opening = datetime(2026, 6, 11, tzinfo=ZoneInfo("Asia/Shanghai")).date()
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date()
    days = (opening - today).days
    if days > 0:
        return f"开幕倒计时 {days} 天"
    return "赛事进行中"


def team_visual(team, size=48):
    logo = team.get("logo")
    name = team.get("name") or ""
    flags = {
        "Argentina": "🇦🇷",
        "Algeria": "🇩🇿",
        "Austria": "🇦🇹",
        "Jordan": "🇯🇴",
        "France": "🇫🇷",
        "England": "🏴",
        "Germany": "🇩🇪",
        "Spain": "🇪🇸",
        "Brazil": "🇧🇷",
        "Japan": "🇯🇵",
        "United States": "🇺🇸",
    }
    if logo:
        st.image(logo, width=size)
    else:
        st.markdown(
            f"""
            <div style="
                width:{size}px;height:{size}px;border-radius:999px;
                display:flex;align-items:center;justify-content:center;
                background:#f1f5f9;border:1px solid #cbd5e1;
                font-size:{max(22, int(size * .48))}px;">
                {flags.get(name, name[:1])}
            </div>
            """,
            unsafe_allow_html=True,
        )


def fixture_status_text(fixture):
    if is_finished(fixture):
        return "已结束"
    if is_live(fixture):
        return "进行中"
    text = fixture.get("status_text") or "未开始"
    if str(text).lower() in {"scheduled", "pre-game", "not started"}:
        return "未开始"
    return text


def fixture_score_text(fixture):
    score = fixture.get("score") or {}
    if is_finished(fixture) and score.get("home") is not None and score.get("away") is not None:
        return f"{score['home']}:{score['away']}"
    return "vs"


def open_fixture(fixture):
    st.session_state.selected_fixture = fixture
    st.session_state.selected_match_text = schedule_match_text(fixture)
    st.session_state.page = "post_match" if is_finished(fixture) else "analysis"
    st.rerun()


def render_schedule_card(fixture, index):
    home = fixture.get("home_team", {})
    away = fixture.get("away_team", {})
    kickoff_text = fixture_time_text(fixture, compact=True)
    venue = " · ".join(
        value for value in [fixture.get("venue_name"), fixture.get("venue_city")] if value
    )
    finished = is_finished(fixture)
    button_text = "查看赛后报告" if finished else "查看赛前分析"
    heat = fixture.get("market_heat")

    with st.container(border=True):
        logo_left, info_col, logo_right, action_col = st.columns([0.7, 4.4, 0.7, 1.35])
        with logo_left:
            team_visual(home)
        with info_col:
            status_class = "status-pill-finished" if finished else "status-pill-live" if is_live(fixture) else ""
            st.markdown(
                f"""
                <div class="schedule-match">
                    {team_cn(home.get("name"))} {fixture_score_text(fixture)} {team_cn(away.get("name"))}
                    <span class="status-pill {status_class}">{fixture_status_text(fixture)}</span>
                </div>
                <div class="schedule-meta">
                    {kickoff_text}<br>
                    {fixture.get("league_name") or "World Cup 2026"} · {fixture.get("round") or "Group Stage"}<br>
                    {venue or "比赛地点待确认"}
                    {"<br>市场热度 " + str(heat) if heat is not None else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )
        with logo_right:
            team_visual(away)
        with action_col:
            if st.button(button_text, key=f"open_{index}_{schedule_match_text(fixture)}", type="primary", use_container_width=True):
                open_fixture(fixture)


def render_schedule_section(fixtures, empty_text, key_prefix):
    if not fixtures:
        st.markdown(f'<div class="schedule-empty">{empty_text}</div>', unsafe_allow_html=True)
        return
    for index, fixture in enumerate(fixtures):
        render_schedule_card(fixture, f"{key_prefix}_{index}")


def render_portal_banner(fixtures):
    st.markdown(
        """
        <div class="portal-banner">
            <div class="portal-title">2026 FIFA World Cup</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_search(fixtures):
    query = st.text_input("搜索球队 / 比赛 / 日期", placeholder="例如：阿根廷、06-17、Argentina", label_visibility="collapsed")
    if not query:
        return
    terms = [term for term in query.strip().lower().split() if term]
    if not terms:
        return
    matches = []
    for fixture in fixtures:
        local_time = fixture_local_datetime(fixture)
        haystack = " ".join([
            fixture.get("home_team", {}).get("name") or "",
            fixture.get("away_team", {}).get("name") or "",
            team_cn(fixture.get("home_team", {}).get("name") or ""),
            team_cn(fixture.get("away_team", {}).get("name") or ""),
            local_time.strftime("%m-%d") if local_time else "",
            local_time.strftime("%Y-%m-%d") if local_time else "",
        ]).lower()
        if all(term in haystack for term in terms):
            matches.append(fixture)

    st.markdown("**搜索结果**")
    render_schedule_section(matches, "没有找到匹配的比赛。", "search")


def render_today_matches(groups):
    st.markdown('<div class="section-title">今日比赛</div>', unsafe_allow_html=True)
    render_schedule_section(groups["today"], "今日暂无世界杯比赛，建议查看全部赛程。", "home_today")


def render_date_nav(fixtures):
    dates = available_match_dates(fixtures)
    if not dates:
        return []
    selected = st.session_state.get("selected_schedule_date") or default_date_key(fixtures)
    if selected not in dates:
        selected = default_date_key(fixtures)
    st.session_state.selected_schedule_date = selected

    weekday_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    st.markdown('<div class="section-title">时间赛程</div>', unsafe_allow_html=True)
    def date_label(date_key):
        try:
            parsed = datetime.strptime(f"2026-{date_key}", "%Y-%m-%d")
            suffix = weekday_map[parsed.weekday()]
        except ValueError:
            suffix = ""
        if date_key == datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%m-%d"):
            suffix = "今天"
        return f"{date_key} {suffix}".strip()

    selected_index = dates.index(selected)
    nav_col1, nav_col2, nav_col3 = st.columns([1, 4, 1])
    with nav_col1:
        if st.button("← 前一天", disabled=selected_index == 0, use_container_width=True):
            st.session_state.selected_schedule_date = dates[selected_index - 1]
            st.rerun()
    with nav_col2:
        selected = st.selectbox(
            "选择比赛日期",
            dates,
            index=selected_index,
            format_func=date_label,
            label_visibility="collapsed",
        )
        st.session_state.selected_schedule_date = selected
    with nav_col3:
        if st.button("后一天 →", disabled=selected_index == len(dates) - 1, use_container_width=True):
            st.session_state.selected_schedule_date = dates[selected_index + 1]
            st.rerun()

    current_index = dates.index(st.session_state.selected_schedule_date)
    quick_dates = dates[max(0, current_index - 3): min(len(dates), current_index + 4)]
    quick_cols = st.columns(len(quick_dates))
    for col, date_key in zip(quick_cols, quick_dates):
        button_type = "primary" if date_key == st.session_state.selected_schedule_date else "secondary"
        if col.button(date_label(date_key), key=f"quick_date_{date_key}", type=button_type, use_container_width=True):
            st.session_state.selected_schedule_date = date_key
            st.rerun()

    selected_fixtures = fixtures_for_date(fixtures, st.session_state.selected_schedule_date)
    st.markdown(f"**{st.session_state.selected_schedule_date} 比赛**")
    render_schedule_section(selected_fixtures, "该日期暂无比赛。", f"selected_date_{st.session_state.selected_schedule_date}")
    return selected_fixtures


def render_focus_matches(fixtures):
    focus = sorted(
        [fixture for fixture in fixtures if not is_finished(fixture)],
        key=lambda item: item.get("market_heat") or 0,
        reverse=True,
    )
    if not focus:
        focus = [fixture for fixture in fixtures if not is_finished(fixture)][:2]
    st.markdown('<div class="section-title">今日焦点赛事</div>', unsafe_allow_html=True)
    render_schedule_section(focus[:2], "暂无焦点赛事。", "focus")


def render_match_status_sections(fixtures):
    finished = [fixture for fixture in fixtures if is_finished(fixture)]
    live = [fixture for fixture in fixtures if is_live(fixture)]
    upcoming = [fixture for fixture in fixtures if not is_finished(fixture) and not is_live(fixture)]
    st.markdown('<div class="section-title">已结束</div>', unsafe_allow_html=True)
    render_schedule_section(finished[:5], "暂无已结束比赛。", "status_finished")
    st.markdown('<div class="section-title">进行中</div>', unsafe_allow_html=True)
    render_schedule_section(live[:5], "暂无正在进行的比赛。", "status_live")
    st.markdown('<div class="section-title">即将开始</div>', unsafe_allow_html=True)
    render_schedule_section(upcoming[:6], "暂无即将开始的比赛。", "status_upcoming")


def render_popular_matches(fixtures, key_prefix="popular"):
    popular = sorted(
        [fixture for fixture in fixtures if fixture.get("market_heat")],
        key=lambda item: item.get("market_heat", 0),
        reverse=True,
    )
    if not popular:
        return
    st.markdown('<div class="section-title">热门分析</div>', unsafe_allow_html=True)
    render_schedule_section(popular[:4], "暂无热门比赛。", key_prefix)


def render_full_schedule(fixtures):
    st.markdown('<div class="section-title">全部世界杯赛程</div>', unsafe_allow_html=True)
    for date_key, date_fixtures in group_by_match_date(fixtures).items():
        st.markdown(f"**{date_key}**")
        render_schedule_section(date_fixtures, "当日暂无比赛。", f"date_{date_key}")


def render_standings(schedule):
    st.markdown('<div class="section-title">世界杯积分榜</div>', unsafe_allow_html=True)
    st.caption(f"数据来源：{schedule.get('source')} · 更新时间：{schedule.get('updated_at', '-')}")
    standings = schedule.get("standings") or default_standings()
    for group_name, rows in standings.items():
        st.markdown(f"**{group_name}**")
        sorted_rows = sorted(
            rows,
            key=lambda row: (
                -int(row.get("points", 0)),
                -int(row.get("gd", 0)),
                -int(row.get("gf", row.get("goals_for", 0) or 0)),
            ),
        )
        table_rows = []
        for index, row in enumerate(sorted_rows, start=1):
            goals_for = row.get("gf", row.get("goals_for", 0))
            goals_against = row.get("ga", row.get("goals_against", 0))
            table_rows.append({
                "排名": index,
                "球队": team_cn(row.get("team")),
                "场次": row.get("played", 0),
                "胜": row.get("wins", 0),
                "平": row.get("draws", 0),
                "负": row.get("losses", 0),
                "进球": goals_for,
                "失球": goals_against,
                "净胜球": row.get("gd", 0),
                "积分": row.get("points", 0),
            })
        if not table_rows:
            st.info("积分榜暂未更新。")
            continue

        dataframe = pd.DataFrame(table_rows)

        def style_standings(dataframe):
            styles = pd.DataFrame("", index=dataframe.index, columns=dataframe.columns)
            styles[["场次"]] = "background-color: #f8fafc;"
            styles[["胜", "平", "负"]] = "background-color: #eef6ff;"
            styles[["进球", "失球", "净胜球"]] = "background-color: #fff7ed;"
            styles[["积分"]] = "background-color: #dbeafe; color: #1e3a8a; font-weight: 900;"
            for row_index, row in dataframe.iterrows():
                if row["排名"] == 1:
                    styles.loc[row_index, :] = "background-color: #dcfce7; color: #14532d; font-weight: 700;"
                    styles.loc[row_index, "积分"] = "background-color: #bbf7d0; color: #14532d; font-weight: 950;"
                elif row["排名"] == 2:
                    styles.loc[row_index, :] = "background-color: #ecfdf5; color: #166534;"
                    styles.loc[row_index, "积分"] = "background-color: #d1fae5; color: #166534; font-weight: 900;"
            return styles

        st.dataframe(
            dataframe.style.apply(style_standings, axis=None),
            use_container_width=True,
            hide_index=True,
            height=min(210, 42 + 36 * len(dataframe)),
        )
        st.caption("列分组：场次｜胜平负｜进球/失球/净胜球｜积分。积分列使用浅色强调，前两名用绿色标识。")


def render_teams(fixtures):
    st.markdown('<div class="section-title">球队</div>', unsafe_allow_html=True)
    teams = {}
    for fixture in fixtures:
        for side in ["home_team", "away_team"]:
            team = fixture.get(side) or {}
            if team.get("name"):
                teams[team["name"]] = team
    cols = st.columns(4)
    for index, team in enumerate(sorted(teams.values(), key=lambda item: team_cn(item["name"]))):
        with cols[index % 4]:
            with st.container(border=True):
                team_visual(team, size=54)
                st.markdown(f"**{team_cn(team['name'])}**")
                profile = profile_for(team["name"])
                st.caption(f"FIFA排名：{profile['fifa_rank']} · 主教练：{profile['coach']}")


def render_market_center(fixtures):
    st.markdown('<div class="section-title">市场分析</div>', unsafe_allow_html=True)
    st.write("这里聚合未来重点比赛的赛前市场分析入口。不会新增预测模型，也不会新增付费数据源。")
    render_popular_matches(fixtures, "market_popular")
    with st.container(border=True):
        st.markdown("**市场数据缓存**")
        st.write("The Odds API 赔率：24小时缓存")
        st.write("Polymarket：5分钟缓存")
        st.write("赛程与球队资料：24小时缓存")


def render_finished_matches(fixtures, schedule):
    finished = [fixture for fixture in fixtures if is_finished(fixture)]
    if not finished:
        return
    st.markdown('<div class="section-title">最近结束比赛</div>', unsafe_allow_html=True)
    st.caption(f"数据来源：{schedule.get('source')} · 更新时间：{schedule.get('updated_at', '-')}")
    render_schedule_section(finished[:5], "暂无已结束比赛。", "finished")


def render_knockout_bracket(fixtures):
    knockout = [fixture for fixture in fixtures if str(fixture.get("round", "")).lower() != "group"]
    with st.container(border=True):
        st.markdown('<div class="section-title">淘汰赛对阵树</div>', unsafe_allow_html=True)
        if not knockout:
            st.info("淘汰赛对阵尚未产生。")
            return
        cols = st.columns(4)
        for index, fixture in enumerate(knockout[:16]):
            with cols[index % 4]:
                st.caption(fixture.get("round", "Knockout"))
                st.write(f"{team_cn(fixture['home_team']['name'])} vs {team_cn(fixture['away_team']['name'])}")


def render_tournament_stats_center(fixtures, schedule):
    stats = tournament_stats(fixtures)
    st.markdown('<div class="section-title">赛事统计中心</div>', unsafe_allow_html=True)
    st.caption(f"数据来源：{schedule.get('source')} · 更新时间：{schedule.get('updated_at', '-')}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("已结束比赛", stats["finished_matches"])
    col2.metric("总进球", stats["total_goals"])
    col3.metric("场均进球", f"{stats['avg_goals']:.2f}")
    col4.metric("最大比分", stats["biggest_score"])


def render_cache_notes(schedule):
    with st.container(border=True):
        st.markdown('<div class="section-title">缓存与数据策略</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("赛程", "真实源优先", "24小时缓存")
        col2.metric("球队资料", "API缓存", "24小时")
        col3.metric("赔率", "The Odds API", "24小时")
        col4.metric("Polymarket", "公开市场", "5分钟")
        st.caption(
            f"当前赛程来源：{schedule.get('source')} · 更新时间：{schedule.get('updated_at', '-')} · "
            f"缓存状态：{schedule.get('cache_status', '-')} · 首页赛程 API 调用：{schedule.get('api_calls', 0)}"
        )
        st.caption(schedule.get("message", "世界杯赛程已加载。"))


def render_schedule_page():
    schedule = fetch_world_cup_schedule()
    fixtures = schedule.get("fixtures", [])

    render_portal_banner(fixtures)
    render_search(fixtures)
    st.caption(
        f"赛程数据来源：{schedule.get('source')} · 更新时间：{schedule.get('updated_at', '-')} · "
        f"缓存状态：{schedule.get('cache_status', '-')}"
    )
    render_date_nav(fixtures)
    render_standings(schedule)
    render_tournament_stats_center(fixtures, schedule)
    with st.expander("全部世界杯赛程", expanded=False):
        render_full_schedule(fixtures)
    render_cache_notes(schedule)


def render_analysis_page(match_text):
    if st.button("← 返回赛程", type="secondary"):
        st.session_state.page = "schedule"
        st.session_state.selected_match_text = None
        st.session_state.selected_fixture = None
        st.rerun()

    try:
        match = parse_match(match_text)
        selected_fixture = st.session_state.get("selected_fixture")
        api_football_data = fetch_match_data(match, "page_market_data_v3")
        odds_date_key = odds_date_key_from_fixture(selected_fixture, api_football_data)
        odds = fetch_odds(match, odds_date_key, "odds_page_v3")
        polymarket = fetch_polymarket(match)
        news = get_mock_news_and_injuries(match)
        probabilities = combine_probabilities(odds, polymarket, news, config)
        scores = recommend_scores(match, probabilities, odds)
        rating = rate_opportunity(probabilities, polymarket, news, odds)
        value_analysis = analyze_value(match, odds, polymarket)
        betting_opinion = build_betting_opinion(match, odds, polymarket, value_analysis)
        result_distribution = build_result_distribution(match, odds, polymarket)
        betting_opinion["result_distribution"] = result_distribution
        render_match_overview(match, api_football_data, selected_fixture)
        actual_odds = render_actual_odds_input(match)
        decision = build_decision_engine(
            match,
            odds,
            polymarket,
            api_football_data,
            betting_opinion,
            actual_odds,
            result_distribution,
        )
        report = build_report(
            match,
            odds,
            polymarket,
            news,
            probabilities,
            scores,
            rating,
            api_football_data,
            value_analysis,
            betting_opinion,
        )
        report_path = save_report(report, match, config["report"]["output_dir"])

        core_tab, market_tab, source_tab = st.tabs([
            "核心决策",
            "市场盘口",
            "数据来源",
        ])

        with core_tab:
            render_core_decision(match, odds, api_football_data, result_distribution, decision, betting_opinion, actual_odds)
            render_storylines(match, betting_opinion, decision)

        with market_tab:
            render_match_winner(match, odds, api_football_data)
            render_handicap(match, api_football_data)
            render_totals(odds)
            render_correct_score_market(api_football_data)
            render_polymarket(match, api_football_data, polymarket)
            render_value(value_analysis)
            render_market_consistency(match, odds, polymarket)

        with source_tab:
            render_debug_panel(match, odds, api_football_data, polymarket, odds_date_key)
            render_detail_data_source(odds, polymarket, selected_fixture)
            render_technical_notes(odds, api_football_data)

        st.download_button(
            "下载 Markdown 报告",
            data=report,
            file_name=report_path.name,
            mime="text/markdown",
        )
    except Exception as error:
        st.error(str(error))


def render_post_match_page(fixture):
    if st.button("← 返回赛程", type="secondary"):
        st.session_state.page = "schedule"
        st.session_state.selected_match_text = None
        st.session_state.selected_fixture = None
        st.rerun()

    home = fixture.get("home_team", {})
    away = fixture.get("away_team", {})
    score = fixture.get("score") or {}
    post_match = fixture.get("post_match") or {}
    stats = post_match.get("stats") or {}
    goals = post_match.get("goals") or []
    cards = post_match.get("cards") or []

    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-kicker">赛后报告 · {fixture.get("league_name", "World Cup 2026")}</div>
            <div class="hero-match">
                {team_cn(home.get("name"))} {score.get("home", "-")}:{score.get("away", "-")} {team_cn(away.get("name"))}
            </div>
            <div class="hero-meta">
                <span class="hero-chip">{fixture.get("round") or "世界杯"}</span>
                <span class="hero-chip">{fixture_time_text(fixture)}</span>
                <span class="hero-chip">{fixture.get("venue_name") or "球场待确认"}</span>
                <span class="hero-chip">已结束</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_detail_data_source(fixture=fixture)

    if not post_match:
        st.info("这场比赛已标记为结束，但当前赛程缓存尚未包含进球、红黄牌和技术统计。不会显示投注建议。")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("控球率", stats.get("possession", "-"))
    col2.metric("射门", stats.get("shots", "-"))
    col3.metric("角球", stats.get("corners", "-"))
    col4.metric("赛前观点", post_match.get("prematch_review", "待复盘"))

    left, right = st.columns(2)
    with left:
        st.markdown("**进球球员**")
        if goals:
            st.dataframe(goals, use_container_width=True, hide_index=True)
        else:
            st.info("暂无进球明细")
    with right:
        st.markdown("**红黄牌**")
        if cards:
            st.dataframe(cards, use_container_width=True, hide_index=True)
        else:
            st.info("暂无红黄牌明细")

    with st.container(border=True):
        st.markdown('<div class="section-title">赔率复盘</div>', unsafe_allow_html=True)
        st.write(post_match.get("odds_review", "赛后赔率复盘待补充。"))


def load_config():
    path = Path(__file__).resolve().parent / "config.yaml"
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


config = load_config()

st.set_page_config(page_title=config["app"]["title"], layout="wide")
card_css()
st.title("世界杯赛前分析平台")
st.caption("用赔率、预测市场和规则引擎识别市场可能错在哪里。")

if "page" not in st.session_state:
    st.session_state.page = "schedule"
if "selected_match_text" not in st.session_state:
    st.session_state.selected_match_text = None
if "selected_fixture" not in st.session_state:
    st.session_state.selected_fixture = None

if st.session_state.page == "post_match" and st.session_state.selected_fixture:
    render_post_match_page(st.session_state.selected_fixture)
elif st.session_state.page == "analysis" and st.session_state.selected_match_text:
    render_analysis_page(st.session_state.selected_match_text)
else:
    render_schedule_page()
