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
    TEAM_CN,
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
from modules.team_profile_client import fetch_team_profile
from modules.user_odds import (
    build_market_candidates,
    build_recommendation_slots,
    candidate_with_actual,
    normalize_score,
    parse_actual_odds,
    parse_score,
    recommendation_reason,
)
from modules.value_model import analyze_value
from modules.weather_client import weather_for_fixture
from modules.worldcup_db import (
    db_api_football_data,
    db_odds,
    load_match_database,
    match_dir as db_match_dir,
)


MODEL_VERSION_TRACKING = {
    "model_version": "v1.61",
    "probability_engine_version": "score_distribution_v1",
    "optimizer_version": "portfolio_optimizer_v1",
    "asset_framework_version": "multi_role_asset_framework_v1",
    "audit_version": "prediction_audit_v1",
}


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


def same_fixture(left, right):
    if not left or not right:
        return False
    left_id = left.get("fixture_id")
    right_id = right.get("fixture_id")
    if left_id and right_id and str(left_id) == str(right_id):
        return True
    left_home = team_cn((left.get("home_team") or {}).get("name") or "")
    left_away = team_cn((left.get("away_team") or {}).get("name") or "")
    right_home = team_cn((right.get("home_team") or {}).get("name") or "")
    right_away = team_cn((right.get("away_team") or {}).get("name") or "")
    left_time = fixture_local_datetime(left)
    right_time = fixture_local_datetime(right)
    same_teams = left_home == right_home and left_away == right_away
    same_day = bool(left_time and right_time and left_time.date() == right_time.date())
    return same_teams and same_day


def fixture_needs_status_refresh(fixture):
    if not fixture or is_finished(fixture):
        return False
    if is_live(fixture):
        return True
    kickoff = fixture_local_datetime(fixture)
    if not kickoff:
        return False
    return datetime.now(ZoneInfo("Asia/Shanghai")) >= kickoff + timedelta(hours=2)


def refresh_selected_fixture_if_needed(fixture):
    if not fixture_needs_status_refresh(fixture):
        return fixture
    fetch_world_cup_schedule.clear()
    schedule = fetch_world_cup_schedule(force_refresh=True)
    for candidate in schedule.get("fixtures", []):
        if same_fixture(fixture, candidate):
            st.session_state.selected_fixture = candidate
            return candidate
    return fixture


def odds_date_key_from_fixture(selected_fixture, api_football_data):
    fixture = selected_fixture or (api_football_data or {}).get("fixture") or {}
    kickoff = fixture.get("kickoff_utc")
    if not kickoff:
        raw = fixture.get("raw") or {}
        kickoff = (raw.get("fixture") or {}).get("date")
    if not kickoff:
        return None
    text = str(kickoff).strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%d")
    except ValueError:
        pass

    for pattern in ("%m/%d/%Y %H:%M", "%m/%d/%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


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
    if st.checkbox("显示 Debug Panel：页面实际读取的数据对象", value=False, key="debug_panel_data_objects"):
        st.dataframe(pd.DataFrame(debug_rows), use_container_width=True, hide_index=True)


def safe_render_market_section(label, renderer, *args, **kwargs):
    try:
        renderer(*args, **kwargs)
        return {"模块": label, "状态": "Success", "错误": ""}
    except Exception as error:
        st.error(f"{label}模块加载失败。")
        st.caption(str(error))
        return {"模块": label, "状态": "Failed", "错误": str(error)}


def render_market_debug_summary(odds, api_football_data, polymarket, section_results):
    handicap = (api_football_data or {}).get("asian_handicap") or {}
    correct_score = (api_football_data or {}).get("correct_score") or {}
    debug_rows = [
        {
            "项目": "Fixture",
            "状态": "Success" if ((api_football_data or {}).get("fixture") or {}).get("id") else "Missing",
            "详情": str(((api_football_data or {}).get("fixture") or {}).get("id") or "-"),
        },
        {
            "项目": "Winner Odds",
            "状态": "Success" if (odds or {}).get("found") else "Missing",
            "详情": (odds or {}).get("event_title") or (odds or {}).get("message") or "-",
        },
        {
            "项目": "Asian Handicap",
            "状态": "Success" if handicap.get("found") else "Missing",
            "详情": f"{len(handicap.get('rows') or [])} rows",
        },
        {
            "项目": "Totals",
            "状态": "Success" if (odds or {}).get("over_under") else "Missing",
            "详情": f"{len((odds or {}).get('over_under') or [])} rows",
        },
        {
            "项目": "Correct Score",
            "状态": "Success" if correct_score.get("found") else "Missing",
            "详情": f"{len(correct_score.get('rows') or [])} rows",
        },
        {
            "项目": "Polymarket",
            "状态": "Success" if (polymarket or {}).get("found") else "Missing",
            "详情": (polymarket or {}).get("event_title") or (polymarket or {}).get("message") or "-",
        },
    ]
    debug_rows.extend(
        {"项目": row["模块"], "状态": row["状态"], "详情": row["错误"] or "-"}
        for row in section_results
    )
    if st.checkbox("显示 Debug Summary", value=False, key="market_debug_summary"):
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

        if st.checkbox("显示推荐理由", value=False, key="decision_recommendation_reasons"):
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
    if outcome == "push":
        return 0
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


def kelly_fraction(item):
    odds_value = item.get("odds") or item.get("effective_odds") or item.get("standard_odds")
    probability = item.get("probability")
    try:
        odds_value = float(odds_value)
        probability = float(probability)
    except (TypeError, ValueError):
        return 0
    if odds_value <= 1 or probability <= 0:
        return 0
    b = odds_value - 1
    q = 1 - probability
    full_kelly = (b * probability - q) / b
    return max(0, min(1, full_kelly))


def kelly_reference_rows(strategy):
    total_stake = sum(item.get("amount", 0) for item in (strategy or {}).get("items") or [])
    rows = []
    for item in (strategy or {}).get("items") or []:
        full = kelly_fraction(item)
        quarter_amount = round_to_hundred(total_stake * full * 0.25)
        half_amount = round_to_hundred(total_stake * full * 0.50)
        current = item.get("amount", 0)
        deviation = current - quarter_amount
        rows.append({
            "投注": item.get("name", "-"),
            "Kelly": percent(full),
            "25% Kelly": f"{quarter_amount}元",
            "50% Kelly": f"{half_amount}元",
            "当前仓位": f"{current}元",
            "偏离25% Kelly": f"{deviation:+d}元",
        })
    return rows


def strategy_holdings_rows(strategy, match, distribution):
    rows = []
    for item in (strategy or {}).get("items") or []:
        full_kelly = kelly_fraction(item)
        rows.append({
            "投注": item.get("name", "-"),
            "角色": insurance_asset_role(item, match, distribution),
            "仓位": f"{item.get('amount', 0)}元",
            "使用赔率": fmt_odds(item.get("odds") or item.get("effective_odds") or item.get("standard_odds")),
            "Kelly": percent(full_kelly),
            "市场赔率": fmt_odds(item.get("standard_odds")),
            "实际赔率": fmt_odds(item.get("actual_odds")),
            "EV提升": f"{(item.get('ev_lift') or 0) * 100:+.1f}%" if item.get("ev_lift") is not None else "-",
            "覆盖率": percent(item.get("coverage_rate") or 0),
            "方向一致性": percent(item_direction_alignment(item, match, distribution)),
            "说明": recommendation_reason(item),
        })
    return rows


ROLE_CN = {
    "Return Asset": "收益资产",
    "Insurance Asset": "保险资产",
    "Directional Asset": "方向资产",
    "Tempo Asset": "节奏资产",
    "Tail Asset": "尾部资产",
    "Auxiliary Asset": "辅助资产",
}

ROLE_CONSTRAINTS = {
    "保险资产": (0.20, 0.40),
    "收益资产": (0.30, 0.60),
    "方向资产": (0.15, 0.45),
    "节奏资产": (0.00, 0.35),
    "尾部资产": (0.00, 0.15),
}


def role_entry(role, weight, reason):
    return {
        "role": role,
        "role_cn": ROLE_CN.get(role, role),
        "weight": max(0, min(1, weight)),
        "reason": reason,
    }


def normalize_role_weights(roles):
    cleaned = [role for role in roles if role.get("weight", 0) > 0]
    if not cleaned:
        cleaned = [role_entry("Auxiliary Asset", 1.0, "当前角色识别信号不足。")]
    total = sum(role.get("weight", 0) for role in cleaned) or 1
    for role in cleaned:
        role["weight"] = role.get("weight", 0) / total
    cleaned.sort(key=lambda role: role["weight"], reverse=True)
    return cleaned


def betting_asset_roles(item, match, distribution):
    item_type = item.get("type")
    odds_value = item.get("odds") or item.get("effective_odds") or item.get("standard_odds") or 0
    coverage = item.get("coverage_rate") or 0
    if match and match.get("home_cn") and match.get("away_cn"):
        alignment = item_direction_alignment(item, match, distribution)
    else:
        alignment = item.get("direction_alignment_score", 0) / 100
    try:
        odds_value = float(odds_value)
    except (TypeError, ValueError):
        odds_value = 0

    roles = []
    if item_type == "correct_score":
        parsed = parse_score(item.get("selection"))
        if parsed:
            home_goals, away_goals = parsed
            favorite_home = bool(match and match.get("home_cn")) and distribution.get("favorite") in {team_cn(match["home_cn"]), match["home_cn"]}
            margin = home_goals - away_goals if favorite_home else away_goals - home_goals
            total_goals = home_goals + away_goals
            if margin in {1, 2} and alignment >= 0.85:
                roles.append(role_entry("Directional Asset", 0.45, "主路径波胆，直接表达比赛主逻辑。"))
                roles.append(role_entry("Return Asset", 0.45, "赔率较高，用于放大主路径利润。"))
            else:
                roles.append(role_entry("Return Asset", 0.55, "赔率高、覆盖窄，用于放大利润。"))
            if odds_value >= 18 or margin >= 3 or margin <= 0 or total_goals >= 4:
                roles.append(role_entry("Tail Asset", 0.35, "覆盖低概率但可能造成组合偏离的极端比分。"))
            elif margin in {0, -1}:
                roles.append(role_entry("Insurance Asset", 0.20, "覆盖主逻辑偏离后的防守路径。"))
        else:
            roles.append(role_entry("Return Asset", 1.0, "波胆赔率高、覆盖窄，用于放大利润。"))
        return normalize_role_weights(roles)
    if item_type == "winner":
        roles.append(role_entry("Insurance Asset", 0.55, "覆盖多个胜利比分路径，降低波胆组合失配风险。"))
        if alignment >= 0.70:
            roles.append(role_entry("Directional Asset", 0.45, "直接表达比赛主方向。"))
        return normalize_role_weights(roles)
    if item_type == "handicap":
        if alignment >= 0.85 and coverage >= 0.25:
            roles.append(role_entry("Directional Asset", 0.60, "表达热门方优势是否能打穿盘口。"))
            roles.append(role_entry("Insurance Asset", 0.30, "覆盖赢球边界和大胜路径。"))
        else:
            roles.append(role_entry("Insurance Asset", 0.60, "覆盖赢球边界和受让路径。"))
            roles.append(role_entry("Directional Asset", 0.25, "辅助表达比赛方向。"))
        if odds_value >= 2.4:
            roles.append(role_entry("Return Asset", 0.15, "赔率具备一定收益弹性。"))
        return normalize_role_weights(roles)
    if item_type == "total":
        roles.append(role_entry("Tempo Asset", 0.70, "表达比赛进球节奏，不直接判断谁赢。"))
        if coverage >= 0.45:
            roles.append(role_entry("Insurance Asset", 0.20, "覆盖多种比分路径下的进球区间。"))
        if odds_value >= 2.15:
            roles.append(role_entry("Return Asset", 0.10, "赔率具备轻微收益弹性。"))
        return normalize_role_weights(roles)
    return normalize_role_weights([role_entry("Auxiliary Asset", 1.0, "辅助覆盖，当前角色识别信号不足。")])


def betting_asset_role(item, match, distribution):
    roles = betting_asset_roles(item, match, distribution)
    primary = roles[0]
    return {
        **primary,
        "roles": roles,
        "role_names_cn": [role["role_cn"] for role in roles],
        "reason": "；".join(f"{role['role_cn']}：{role['reason']}" for role in roles[:3]),
    }


def insurance_asset_role(item, match, distribution):
    role = betting_asset_role(item, match, distribution)
    return role["reason"]


def asset_role_key(item, match, distribution):
    return betting_asset_role(item, match, distribution)["role_cn"]


def role_allocation_rows(items, match, distribution):
    total = sum(item.get("amount", 0) for item in items)
    grouped = {}
    for item in items:
        amount = item.get("amount", 0)
        for role in betting_asset_roles(item, match, distribution):
            role_name = role["role_cn"]
            role_amount = amount * role["weight"]
            grouped.setdefault(role_name, {"amount": 0, "count": 0, "names": [], "reasons": []})
            grouped[role_name]["amount"] += role_amount
            grouped[role_name]["count"] += 1
            grouped[role_name]["names"].append(item.get("name", "-"))
            grouped[role_name]["reasons"].append(role["reason"])
    rows = []
    for role, data in sorted(grouped.items(), key=lambda entry: entry[1]["amount"], reverse=True):
        rows.append({
            "资产角色": role,
            "仓位": f"{round(data['amount'])}元",
            "占比": percent(data["amount"] / total) if total else "-",
            "资产数量": data["count"],
            "代表资产": "、".join(data["names"][:3]),
            "角色说明": "；".join(dict.fromkeys(data["reasons"][:2])),
        })
    return rows


def role_exposure(items, match, distribution):
    total = sum(item.get("amount", 0) for item in items)
    exposure = {}
    if not total:
        return exposure
    for item in items:
        amount = item.get("amount", 0)
        for role in betting_asset_roles(item, match, distribution):
            role_name = role["role_cn"]
            exposure[role_name] = exposure.get(role_name, 0) + (amount * role["weight"] / total)
    return exposure


def role_balance_adjustment(items, match, distribution):
    exposure = role_exposure(items, match, distribution)
    if not exposure:
        return 0
    adjustment = role_constraint_adjustment(exposure)
    if exposure.get("方向资产", 0) + exposure.get("保险资产", 0) >= 0.35:
        adjustment += 20
    if 0.05 <= exposure.get("尾部资产", 0) <= 0.15:
        adjustment += 8
    return adjustment


def role_constraint_adjustment(exposure):
    adjustment = 0
    for role, (lower, upper) in ROLE_CONSTRAINTS.items():
        value = exposure.get(role, 0)
        if value < lower:
            adjustment -= min(35, round((lower - value) * 120))
        elif value > upper:
            adjustment -= min(35, round((value - upper) * 120))
        else:
            adjustment += 4
    return adjustment


def role_constraint_rows(items, match, distribution):
    exposure = role_exposure(items or [], match, distribution)
    rows = []
    for role, (lower, upper) in ROLE_CONSTRAINTS.items():
        value = exposure.get(role, 0)
        if value < lower:
            status = "偏低"
        elif value > upper:
            status = "偏高"
        else:
            status = "合理"
        rows.append({
            "资产角色": role,
            "当前占比": percent(value),
            "目标区间": f"{percent(lower)} - {percent(upper)}",
            "状态": status,
        })
    return rows


def portfolio_style(items, match, distribution, strategy=None):
    exposure = role_exposure(items or [], match, distribution)
    return_share = exposure.get("收益资产", 0)
    insurance_share = exposure.get("保险资产", 0)
    tail_share = exposure.get("尾部资产", 0)
    tempo_share = exposure.get("节奏资产", 0)
    concentration = (strategy or {}).get("concentration")
    volatility = (strategy or {}).get("volatility")
    total_stake = sum(item.get("amount", 0) for item in items or [])
    volatility_ratio = volatility / total_stake if volatility and total_stake else 0

    if return_share >= 0.48 or tail_share >= 0.14 or volatility_ratio >= 0.85:
        label = "Aggressive"
        label_cn = "激进型"
        reason = "收益资产或尾部资产占比较高，组合更追求盈利弹性。"
    elif insurance_share >= 0.32 and return_share <= 0.38 and tail_share <= 0.08:
        label = "Conservative"
        label_cn = "保守型"
        reason = "保险资产占比较高，组合更重视覆盖和回撤控制。"
    else:
        label = "Balanced"
        label_cn = "均衡型"
        reason = "收益、保险与方向资产相对均衡。"

    return {
        "style": label,
        "style_cn": label_cn,
        "reason": reason,
        "role_exposure": exposure,
        "return_share": return_share,
        "insurance_share": insurance_share,
        "tail_share": tail_share,
        "tempo_share": tempo_share,
        "correlation": concentration,
        "volatility": volatility,
    }


def strategy_path_rows(strategy):
    rows = []
    for row in (strategy or {}).get("score_rows") or []:
        rows.append({
            "比分": row.get("比分", "-"),
            "路径": row.get("路径", "-"),
            "比分概率": row.get("比分概率", row.get("路径权重", "-")),
            "组合收益": row.get("组合收益", "-"),
            "EV贡献": row.get("EV贡献", "-"),
        })
    return rows


def marginal_contribution_rows(strategy, match, distribution):
    items = (strategy or {}).get("items") or []
    if len(items) < 2:
        return []
    baseline_stake = sum(item.get("amount", 0) for item in items)
    baseline = strategy
    rows = []
    for item in items:
        remaining = [other for other in items if other is not item]
        remaining_stake = sum(other.get("amount", 0) for other in remaining)
        if not remaining or not remaining_stake:
            continue
        without = evaluate_strategy(
            {"code": "M", "name": "移除后组合", "items": remaining, "fixed_amounts": True},
            match,
            distribution,
            remaining_stake,
        )
        ev_delta = baseline.get("expected_profit", 0) - without.get("expected_profit", 0)
        risk_delta = baseline.get("max_loss", 0) - without.get("max_loss", 0)
        sharpe_delta = baseline.get("sharpe_ratio", 0) - without.get("sharpe_ratio", 0)
        rows.append({
            "资产": item.get("name", "-"),
            "当前仓位": f"{item.get('amount', 0)}元",
            "EV边际贡献": f"{ev_delta:+.0f}",
            "最大亏损变化": f"{risk_delta:+.0f}",
            "Sharpe变化": f"{sharpe_delta:+.2f}",
            "解释": "提升EV" if ev_delta > 0 else "主要承担保险/覆盖作用",
        })
    return sorted(rows, key=lambda row: float(str(row["EV边际贡献"]).replace("+", "")), reverse=True)


def correct_score_marginal_ev_rows(combo):
    correct_items = [item for item in combo if item.get("type") == "correct_score" and item.get("standard_odds")]
    if not correct_items:
        return []
    correct_items.sort(
        key=lambda item: (
            item.get("path_match_score", 0),
            item.get("actual_ev") if item.get("actual_ev") is not None else -99,
            item.get("score", 0),
        ),
        reverse=True,
    )
    rows = []
    cumulative = 0
    for index, item in enumerate(correct_items[:12], start=1):
        probability = exact_score_probability([item], item.get("selection")) or 0
        marginal_ev = (item.get("actual_ev") if item.get("actual_ev") is not None else item.get("standard_ev") or 0) * 100
        cumulative += marginal_ev
        if index <= 2:
            action = "保留"
        elif marginal_ev >= 8:
            action = "继续加入"
        elif marginal_ev >= 2:
            action = "低金额观察"
        else:
            action = "停止/不优先"
        rows.append({
            "顺序": index,
            "波胆": item.get("selection", "-"),
            "赔率": fmt_odds(item.get("effective_odds") or item.get("standard_odds")),
            "隐含概率": percent(probability),
            "边际EV/100元": f"{marginal_ev:+.0f}",
            "累计EV": f"{cumulative:+.0f}",
            "处理": action,
        })
    return rows


def numeric_text(value):
    text = str(value or "").strip().replace(",", "").replace("%", "").replace("+", "")
    if not text or text == "-":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def chart_health_check():
    try:
        pd.DataFrame({"value": [1]}).set_index(pd.Index(["check"]))
        return True
    except Exception:
        return False


def render_probability_profit_charts(paths):
    if not paths:
        return
    if not chart_health_check():
        st.warning("图表组件暂不可用，已保留表格数据。")
        return

    rows = []
    for row in paths:
        score = str(row.get("比分", "-"))
        probability = numeric_text(row.get("比分概率"))
        profit = numeric_text(row.get("组合收益"))
        if probability is None and profit is None:
            continue
        rows.append({
            "比分": score,
            "概率": (probability or 0) / 100,
            "组合收益": profit or 0,
        })
    if not rows:
        return

    chart_df = pd.DataFrame(rows).set_index("比分")
    left, right = st.columns(2)
    with left:
        st.caption("比分概率曲线")
        st.line_chart(chart_df[["概率"]], use_container_width=True)
    with right:
        st.caption("收益曲线")
        st.bar_chart(chart_df[["组合收益"]], use_container_width=True)


def render_strategy_detail(strategy, match, distribution):
    if not strategy:
        return
    st.markdown(f"**{strategy.get('rank_name') or strategy['name']}**")
    if strategy.get("original_name") and strategy.get("original_name") != strategy.get("rank_name"):
        st.caption(f"策略来源：{strategy.get('original_name')}")
    metric_cols = st.columns(6)
    metric_cols[0].metric("总仓位", f"{sum(item.get('amount', 0) for item in strategy.get('items', []))}元")
    metric_cols[1].metric("命中率", percent(strategy.get("hit_rate", 0)))
    metric_cols[2].metric("EV", f"{strategy.get('expected_profit', 0):+.0f}")
    metric_cols[3].metric("Sharpe", f"{strategy.get('sharpe_ratio', 0):.2f}")
    metric_cols[4].metric("稳定性", f"{strategy.get('stability_score', 0)} / 100")
    metric_cols[5].metric("评分", strategy.get("score", 0))

    holdings = strategy_holdings_rows(strategy, match, distribution)
    if holdings:
        st.markdown("**策略组成与仓位结构**")
        st.dataframe(pd.DataFrame(holdings), use_container_width=True, hide_index=True)
        role_rows = role_allocation_rows(strategy.get("items") or [], match, distribution)
        if role_rows:
            st.markdown("**资产角色配置**")
            st.caption("组合先按资产角色理解，再映射到具体投注。")
            st.dataframe(pd.DataFrame(role_rows), use_container_width=True, hide_index=True)
        kelly_rows = kelly_reference_rows(strategy)
        if kelly_rows:
            st.markdown("**Kelly 仓位参考**")
            st.caption("Kelly 只作为参考，不使用满Kelly；重点看当前仓位相对 25% Kelly 是否明显偏离。")
            st.dataframe(pd.DataFrame(kelly_rows), use_container_width=True, hide_index=True)

    paths = strategy_path_rows(strategy)
    if paths:
        st.markdown("**比分概率曲线与收益曲面**")
        render_probability_profit_charts(paths)
        st.dataframe(pd.DataFrame(paths), use_container_width=True, hide_index=True)
        marginal_rows = marginal_contribution_rows(strategy, match, distribution)
        if marginal_rows:
            st.markdown("**边际贡献分析**")
            st.caption("逐个移除资产后重新计算组合，观察该资产对EV、风险和Sharpe的边际影响。")
            st.dataframe(pd.DataFrame(marginal_rows), use_container_width=True, hide_index=True)

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


def reasonable_score_space(max_home=7, max_away=5, max_total=8):
    scores = []
    for home_goals in range(max_home + 1):
        for away_goals in range(max_away + 1):
            if home_goals + away_goals <= max_total:
                scores.append(f"{home_goals}:{away_goals}")
    return scores


def score_probability_sort_key(match, distribution, combo, score):
    probability = exact_score_probability(combo, score)
    if probability is None:
        category = score_category(match, distribution, score)
        category_count = sum(
            1 for candidate_score in reasonable_score_space()
            if score_category(match, distribution, candidate_score) == category
        )
        category_probability = distribution_category_probability(distribution, category)
        probability = category_probability / category_count if category_count else 0
    category_priority = {
        "favorite_1": 5,
        "favorite_2": 4,
        "favorite_3_plus": 3,
        "draw": 2,
        "underdog": 1,
    }.get(score_category(match, distribution, score), 0)
    return probability, category_priority


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


def asset_profit_per_unit(item, match, score):
    home_goals, away_goals = [int(part) for part in score.split(":", 1)]
    odds_value = item.get("odds") or item.get("effective_odds") or item.get("standard_odds")
    item_type = item.get("type")
    if item_type == "winner":
        outcome = winner_outcome(item, match, home_goals, away_goals)
    elif item_type == "handicap":
        outcome = handicap_outcome(item, home_goals, away_goals)
    elif item_type == "total":
        outcome = total_outcome(item, home_goals, away_goals)
    elif item_type == "correct_score":
        outcome = correct_score_outcome(item, home_goals, away_goals)
    else:
        outcome = "lose"
    if outcome == "win" and odds_value:
        return float(odds_value) - 1
    if outcome == "lose":
        return -1
    return 0


def build_score_distribution(match, distribution, assets):
    scores = score_candidates(match, distribution, assets)
    probabilities = scenario_probability_map(match, distribution, assets, scores)
    return [{"score": score, "probability": probabilities.get(score, 0)} for score in scores]


def build_return_matrix(match, score_distribution, assets):
    rows = []
    for score_row in score_distribution:
        row = {"score": score_row["score"], "probability": score_row["probability"]}
        for index, asset in enumerate(assets):
            row[f"asset_{index}"] = asset_profit_per_unit(asset, match, score_row["score"])
        rows.append(row)
    return rows


def auto_correct_score_pool(correct_scores, target_share=0.55, min_count=2, max_count=8):
    enriched = []
    total_implied = 0
    for item in correct_scores:
        odds_value = item.get("standard_odds") or item.get("odds")
        try:
            probability = 1 / float(odds_value)
        except (TypeError, ValueError, ZeroDivisionError):
            probability = 0
        total_implied += probability
        enriched.append({**item, "_market_probability": probability})
    if not enriched:
        return []
    enriched.sort(
        key=lambda item: (
            item.get("_market_probability", 0),
            item.get("path_match_score", 0),
            item.get("score", 0),
        ),
        reverse=True,
    )
    selected = []
    cumulative = 0
    for item in enriched:
        share = item.get("_market_probability", 0) / total_implied if total_implied else 0
        if len(selected) >= min_count and share < 0.02:
            break
        selected.append(item)
        cumulative += share
        if len(selected) >= min_count and cumulative >= target_share:
            break
        if len(selected) >= max_count:
            break
    return [{key: value for key, value in item.items() if not key.startswith("_")} for item in selected]


def optimizer_asset_pool(assets, match, distribution, limit=12):
    core_types = {"winner", "handicap", "total"}
    core_assets = [item for item in assets if item.get("type") in core_types]
    correct_scores = [item for item in assets if item.get("type") == "correct_score"]
    correct_scores.sort(
        key=lambda item: (
            item_direction_alignment(item, match, distribution),
            item.get("actual_ev") if item.get("actual_ev") is not None else -99,
            item.get("score", 0),
        ),
        reverse=True,
    )
    correct_scores = auto_correct_score_pool(correct_scores)
    pool = []
    seen = set()
    for item in core_assets + correct_scores:
        key = bet_identity(item)
        if key in seen:
            continue
        seen.add(key)
        pool.append(item)
        if len(pool) >= limit:
            break
    return pool


def allocation_vectors(asset_count, units, max_assets=5):
    current = [0] * asset_count

    def walk(index, remaining, used):
        if index == asset_count - 1:
            current[index] = remaining
            if used + (1 if remaining else 0) <= max_assets:
                yield list(current)
            current[index] = 0
            return
        for value in range(remaining + 1):
            next_used = used + (1 if value else 0)
            if next_used <= max_assets:
                current[index] = value
                yield from walk(index + 1, remaining - value, next_used)
        current[index] = 0

    yield from walk(0, units, 0)


def portfolio_stability_score(volatility, max_loss, total_stake, concentration, profits):
    if not total_stake:
        return 0
    volatility_ratio = volatility / total_stake
    loss_ratio = max_loss / total_stake
    tail_loss_probability = sum(probability for profit, probability in profits if profit < -0.5 * total_stake)
    score = (
        100
        - min(35, volatility_ratio * 35)
        - min(25, loss_ratio * 25)
        - min(25, concentration * 25)
        - min(15, tail_loss_probability * 30)
    )
    return clamp(score)


def evaluate_allocation(vector, assets, return_matrix, total_stake, match, distribution, risk_lambda):
    amounts = [unit * 100 for unit in vector]
    active = [{**asset, "amount": amount, "share": amount / total_stake if total_stake else 0} for asset, amount in zip(assets, amounts) if amount > 0]
    if not active:
        return None

    profits = []
    expected_profit = 0
    hit_probability = 0
    for row in return_matrix:
        profit = 0
        for index, amount in enumerate(amounts):
            profit += amount * row.get(f"asset_{index}", 0)
        probability = row["probability"]
        profits.append((profit, probability))
        expected_profit += probability * profit
        if profit > 0:
            hit_probability += probability

    variance = sum(probability * ((profit - expected_profit) ** 2) for profit, probability in profits)
    volatility = variance ** 0.5
    max_profit = max((profit for profit, _ in profits), default=0)
    min_profit = min((profit for profit, _ in profits), default=0)
    max_loss = abs(min(0, min_profit))
    correlation = weighted_combo_correlation(active)
    strategic_value = strategy_strategic_value(active, match, distribution)
    sharpe_ratio = expected_profit / volatility if volatility else 0
    stability = portfolio_stability_score(volatility, max_loss, total_stake, correlation, profits)
    risk = volatility + max_loss * 0.35 + correlation * total_stake * 0.20
    risk_reward = max_profit / max_loss if max_loss else max_profit / total_stake if total_stake else 0
    score, _ = strategy_score(
        expected_profit / total_stake if total_stake else 0,
        hit_probability,
        risk_reward,
        max_loss,
        total_stake,
        correlation,
        strategy_direction_alignment(active, match, distribution),
        strategic_value,
        sharpe_ratio,
        stability,
    )
    utility = score * 10 + expected_profit * 0.04 - risk_lambda * risk * 0.04 + role_balance_adjustment(active, match, distribution)
    return {
        "items": active,
        "utility": utility,
        "expected_profit": expected_profit,
        "expected_yield": expected_profit / total_stake if total_stake else 0,
        "hit_rate": hit_probability,
        "max_profit": max_profit,
        "max_loss": max_loss,
        "volatility": volatility,
        "correlation": correlation,
        "strategic_value": strategic_value,
        "sharpe_ratio": sharpe_ratio,
        "stability_score": stability,
    }


def optimize_betting_portfolio(match, distribution, combo, total_stake, risk_profile="standard"):
    assets = [item for item in combo if item.get("recommended") and item.get("type") != "empty"]
    if not assets or not total_stake:
        return None
    assets = optimizer_asset_pool(assets, match, distribution, limit=9)
    units = max(1, int(round(total_stake / 100)))
    total_stake = units * 100
    score_distribution = build_score_distribution(match, distribution, assets)
    return_matrix = build_return_matrix(match, score_distribution, assets)
    risk_lambda = {"conservative": 0.34, "standard": 0.20, "aggressive": 0.09}.get(risk_profile, 0.20)
    best = None
    for vector in allocation_vectors(len(assets), units, max_assets=min(5, len(assets))):
        evaluated = evaluate_allocation(vector, assets, return_matrix, total_stake, match, distribution, risk_lambda)
        if evaluated and (best is None or evaluated["utility"] > best["utility"]):
            best = evaluated
    if not best:
        return None
    return {
        **best,
        "score_distribution": score_distribution,
        "return_matrix": return_matrix,
        "risk_lambda": risk_lambda,
    }


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
    if abs(adjusted - opponent) < 0.001:
        return "push"
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
    correct_score_profit = sum(
        profit_value(item.get("amount"), item.get("odds"), correct_score_outcome(item, home_goals, away_goals))
        for item in correct_scores
    )
    total_value = winner_profit + handicap_profit + total_profit + correct_score_profit
    probability = exact_score_probability(combo, score)
    ev_contribution = total_value * probability if probability is not None else None
    return {
        "比分": score,
        "路径": score_path_label(match, distribution, score),
        "比分概率": percent(probability) if probability is not None else "-",
        "独赢收益": f"{winner_profit:+d}",
        "让球收益": f"{handicap_profit:+d}",
        "大小球收益": f"{total_profit:+d}",
        "波胆收益": f"{correct_score_profit:+d}",
        "组合收益": f"{total_value:+d}",
        "概率×收益": "-",
        "EV贡献": f"{ev_contribution:+.0f}" if ev_contribution is not None else "-",
        "_total": total_value,
        "_ev_contribution": ev_contribution,
    }


def score_candidates(match, distribution, combo):
    correct = [item.get("selection") for item in combo_items(combo, "correct_score") if item.get("selection")]
    ordered = []
    for score in correct + reasonable_score_space():
        if score not in ordered and re.match(r"^\d+:\d+$", str(score)):
            ordered.append(score)
    ordered.sort(
        key=lambda score: score_probability_sort_key(match, distribution, combo, score),
        reverse=True,
    )
    return ordered


def path_analysis_rows(match, distribution, combo):
    scores = score_candidates(match, distribution, combo)
    probabilities = scenario_probability_map(match, distribution, combo, scores)
    rows = []
    for score in scores:
        row = score_profit_row(match, distribution, combo, score)
        probability = probabilities.get(score, 0)
        ev_contribution = row["_total"] * probability
        row["比分概率"] = percent(probability)
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


def final_score_from_fixture(fixture):
    score = (fixture or {}).get("score") or {}
    home = score.get("home")
    away = score.get("away")
    if home is None or away is None:
        return None
    try:
        return f"{int(home)}:{int(away)}"
    except (TypeError, ValueError):
        return None


def settle_items(match, distribution, items, final_score):
    if not final_score or not items:
        return {"rows": [], "stake": 0, "profit": 0, "roi": 0}
    rows = []
    total_stake = 0
    total_profit = 0
    home_goals, away_goals = [int(part) for part in final_score.split(":", 1)]
    for item in items:
        amount = int(item.get("amount") or 0)
        odds_value = item.get("odds") or item.get("effective_odds") or item.get("standard_odds")
        item_type = item.get("type")
        if not odds_value:
            outcome = "no_odds"
        elif item_type == "winner":
            outcome = winner_outcome(item, match, home_goals, away_goals)
        elif item_type == "handicap":
            outcome = handicap_outcome(item, home_goals, away_goals)
        elif item_type == "total":
            outcome = total_outcome(item, home_goals, away_goals)
        elif item_type == "correct_score":
            outcome = correct_score_outcome(item, home_goals, away_goals)
        else:
            outcome = "lose"
        profit = profit_value(amount, odds_value, outcome)
        roles = betting_asset_roles(item, match, distribution)
        total_stake += amount
        total_profit += profit
        rows.append({
            "投注": item.get("name") or item.get("selection") or "-",
            "资产角色": " / ".join(role["role_cn"] for role in roles),
            "金额": f"{amount}元",
            "赔率": fmt_odds(odds_value),
            "结果": {"win": "赢", "lose": "输", "push": "走水", "no_odds": "未找到赔率"}.get(outcome, outcome),
            "盈亏": f"{profit:+d}元",
            "_roles": roles,
            "_profit": profit,
            "_amount": amount,
        })
    roi = total_profit / total_stake if total_stake else 0
    return {"rows": rows, "stake": total_stake, "profit": total_profit, "roi": roi}


def settle_strategies(match, distribution, strategies, my_portfolio, final_score):
    results = []
    for index, strategy in enumerate(strategies or []):
        settled = settle_items(match, distribution, strategy.get("items") or [], final_score)
        results.append({
            "组合": normalize_portfolio_name(strategy.get("rank_name", strategy.get("name", "-")), index),
            "来源": strategy.get("original_name", strategy.get("name", "-")),
            "投入": f"{settled['stake']}元",
            "盈亏": f"{settled['profit']:+d}元",
            "ROI": percent(settled["roi"]),
            "_profit": settled["profit"],
            "_detail": settled["rows"],
        })
    if (my_portfolio or {}).get("items"):
        settled = settle_items(match, distribution, my_portfolio.get("items") or [], final_score)
        results.append({
            "组合": "我的组合",
            "来源": "My Portfolio",
            "投入": f"{settled['stake']}元",
            "盈亏": f"{settled['profit']:+d}元",
            "ROI": percent(settled["roi"]),
            "_profit": settled["profit"],
            "_detail": settled["rows"],
        })
    return sorted(results, key=lambda row: row["_profit"], reverse=True)


def audit_failure_reason(item, outcome, final_score):
    if outcome in {"win", "push"}:
        return "命中或走水"
    item_type = item.get("type")
    if item_type == "winner":
        return "方向判断错误"
    if item_type == "handicap":
        return "赢球幅度或受让边界判断错误"
    if item_type == "total":
        return "比赛节奏判断错误"
    if item_type == "correct_score":
        return f"精确比分路径偏离，实际比分 {final_score}"
    return "路径判断错误"


def prediction_audit(match, distribution, strategy, final_score):
    if not strategy or not final_score:
        return {}
    home_goals, away_goals = [int(part) for part in final_score.split(":", 1)]
    rows = []
    settled = settle_items(match, distribution, strategy.get("items") or [], final_score)
    for item in strategy.get("items") or []:
        item_type = item.get("type")
        if item_type == "winner":
            outcome = winner_outcome(item, match, home_goals, away_goals)
        elif item_type == "handicap":
            outcome = handicap_outcome(item, home_goals, away_goals)
        elif item_type == "total":
            outcome = total_outcome(item, home_goals, away_goals)
        elif item_type == "correct_score":
            outcome = correct_score_outcome(item, home_goals, away_goals)
        else:
            outcome = "lose"
        rows.append({
            "赛前推荐": item.get("name") or item.get("selection") or "-",
            "推荐原因": recommendation_reason(item),
            "赛前风险": insurance_asset_role(item, match, distribution),
            "赛前主要路径": score_path_label(match, distribution, item.get("selection")) if item_type == "correct_score" else item.get("selection", "-"),
            "赛后真实结果": final_score,
            "是否命中": {"win": "命中", "lose": "未命中", "push": "走水"}.get(outcome, outcome),
            "失败原因": audit_failure_reason(item, outcome, final_score),
        })
    missed = [row["失败原因"] for row in rows if row["是否命中"] == "未命中"]
    return {
        "strategy": strategy.get("rank_name", strategy.get("name", "-")),
        "final_score": final_score,
        "profit": settled.get("profit", 0),
        "roi": settled.get("roi", 0),
        "hit_count": sum(1 for row in rows if row["是否命中"] == "命中"),
        "total_count": len(rows),
        "failure_reasons": sorted(set(missed)),
        "rows": rows,
    }


def role_performance_summary(detail_rows):
    grouped = {}
    for row in detail_rows or []:
        roles = row.get("_roles") or []
        if not roles:
            roles = [{"role_cn": row.get("资产角色") or "未分类", "weight": 1}]
        for role in roles:
            role_name = role.get("role_cn") or "未分类"
            weight = role.get("weight", 1)
            grouped[role_name] = grouped.get(role_name, 0) + row.get("_profit", 0) * weight
    if not grouped:
        return "-"
    ordered = sorted(grouped.items(), key=lambda item: item[1], reverse=True)
    return " / ".join(f"{role} {profit:+.0f}" for role, profit in ordered[:3])


def portfolio_items_summary(detail_rows):
    rows = detail_rows or []
    if not rows:
        return "-"
    summary = []
    for row in rows[:5]:
        summary.append(f"{row.get('投注', '-')} {row.get('金额', '-')}")
    if len(rows) > 5:
        summary.append(f"+{len(rows) - 5}项")
    return "；".join(summary)


def portfolio_audit_detail_rows(detail_rows):
    output = []
    for row in detail_rows or []:
        amount_text = str(row.get("金额", "0")).replace("元", "")
        profit_text = str(row.get("盈亏", "0")).replace("元", "")
        try:
            amount = float(amount_text)
            profit = float(profit_text.replace("+", ""))
        except ValueError:
            amount = 0
            profit = 0
        roi = profit / amount if amount else 0
        output.append({
            "投注": row.get("投注", "-"),
            "资产角色": row.get("资产角色", "-"),
            "金额": row.get("金额", "-"),
            "盈亏": row.get("盈亏", "-"),
            "ROI": percent(roi) if amount else "-",
            "作用": role_contribution_explanation(str(row.get("资产角色", "")).split(" / ")[0], profit),
            "结果": row.get("结果", "-"),
        })
    return output


def result_hit_summary(detail_rows):
    rows = detail_rows or []
    if not rows:
        return "-"
    wins = sum(1 for row in rows if row.get("结果") == "赢")
    pushes = sum(1 for row in rows if row.get("结果") == "走水")
    return f"{wins}赢 / {pushes}走 / {len(rows)}项"


def result_failure_summary(detail_rows):
    reasons = []
    for row in detail_rows or []:
        if row.get("结果") != "输":
            continue
        role_text = row.get("资产角色", "")
        if "节奏资产" in role_text:
            reasons.append("节奏判断错误")
        elif "方向资产" in role_text:
            reasons.append("方向判断未兑现")
        elif "收益资产" in role_text:
            reasons.append("高收益路径未命中")
        elif "尾部资产" in role_text:
            reasons.append("尾部路径未触发")
        else:
            reasons.append("路径覆盖不足")
    return "；".join(dict.fromkeys(reasons[:2])) if reasons else "无"


def recommendation_audit(match, distribution, strategies, final_score, settlement_results=None):
    audits = []
    strategy_map = {}
    for index, strategy in enumerate(strategies or []):
        names = {
            strategy.get("rank_name", ""),
            strategy.get("name", ""),
            normalize_portfolio_name(strategy.get("rank_name", strategy.get("name", "")), index),
        }
        for name in names:
            if name:
                strategy_map[name] = strategy
    if settlement_results:
        for index, result in enumerate(sorted(settlement_results, key=lambda row: row.get("_profit", 0), reverse=True), start=1):
            display_name = normalize_portfolio_name(result.get("组合"), source=result.get("来源"))
            strategy = strategy_map.get(result.get("组合")) or strategy_map.get(display_name)
            if strategy:
                style = strategy.get("portfolio_style") or portfolio_style(strategy.get("items") or [], match, distribution, strategy)
            else:
                style = {"style_cn": "用户组合"}
            audits.append({
                "排名": index,
                "组合名称": display_name,
                "组合风格": style.get("style_cn", "-"),
                "具体投注": portfolio_items_summary(result.get("_detail") or []),
                "总投入": result.get("投入", "-"),
                "最终比分": final_score,
                "实际盈亏": result.get("盈亏", "-"),
                "ROI": result.get("ROI", "-"),
                "命中情况": result_hit_summary(result.get("_detail") or []),
                "失败原因": result_failure_summary(result.get("_detail") or []),
                "资产角色表现": role_performance_summary(result.get("_detail") or []),
            })
        return audits

    for strategy in strategies or []:
        audit = prediction_audit(match, distribution, strategy, final_score)
        if not audit:
            continue
        style = strategy.get("portfolio_style") or portfolio_style(strategy.get("items") or [], match, distribution, strategy)
        audits.append({
            "排名": len(audits) + 1,
            "组合名称": normalize_portfolio_name(strategy.get("rank_name", strategy.get("name", "-")), len(audits)),
            "组合风格": style.get("style_cn", "-"),
            "具体投注": "-",
            "总投入": "-",
            "最终比分": final_score,
            "实际盈亏": f"{audit['profit']:+d}元",
            "ROI": percent(audit["roi"]),
            "命中情况": f"{audit['hit_count']} / {audit['total_count']}",
            "失败原因": "；".join(audit["failure_reasons"][:2]) if audit["failure_reasons"] else "无",
            "资产角色表现": "-",
        })
    return audits


def style_performance_path():
    return HISTORY_DIR / "style_performance.json"


def portfolio_performance_path():
    return HISTORY_DIR / "portfolio_performance.json"


def update_style_performance_database(match, selected_fixture, strategies, settlement_results):
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = style_performance_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"schema_version": 1, "matches": {}, "styles": {}}
    except (OSError, json.JSONDecodeError):
        data = {"schema_version": 1, "matches": {}, "styles": {}}
    match_key = history_slug(match, selected_fixture)
    if match_key in data.get("matches", {}):
        return data

    strategies_by_name = {
        strategy.get("rank_name", strategy.get("name", "-")): strategy
        for strategy in strategies or []
    }
    data.setdefault("matches", {})[match_key] = datetime.now().astimezone().isoformat()
    styles = data.setdefault("styles", {})
    for result in settlement_results or []:
        strategy = strategies_by_name.get(result.get("组合"))
        if not strategy:
            continue
        style = (strategy.get("portfolio_style") or {}).get("style_cn") or "未分类"
        stake_text = str(result.get("投入", "0")).replace("元", "")
        try:
            stake = int(float(stake_text))
        except ValueError:
            stake = 0
        profit = result.get("_profit", 0)
        stats = styles.setdefault(style, {"matches": 0, "stake": 0, "profit": 0, "wins": 0, "max_drawdown": 0})
        stats["matches"] += 1
        stats["stake"] += stake
        stats["profit"] += profit
        stats["wins"] += 1 if profit > 0 else 0
        stats["max_drawdown"] = min(stats.get("max_drawdown", 0), profit)
        stats["roi"] = stats["profit"] / stats["stake"] if stats["stake"] else 0
        stats["win_rate"] = stats["wins"] / stats["matches"] if stats["matches"] else 0
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def update_portfolio_performance_database(match, selected_fixture, settlement_results):
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = portfolio_performance_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"schema_version": 1, "matches": {}, "portfolios": {}}
    except (OSError, json.JSONDecodeError):
        data = {"schema_version": 1, "matches": {}, "portfolios": {}}
    match_key = history_slug(match, selected_fixture)
    if match_key in data.get("matches", {}):
        return data

    data.setdefault("matches", {})[match_key] = datetime.now().astimezone().isoformat()
    portfolios = data.setdefault("portfolios", {})
    for result in settlement_results or []:
        name = normalize_portfolio_name(result.get("组合", "未命名组合"), source=result.get("来源"))
        stake_text = str(result.get("投入", "0")).replace("元", "")
        try:
            stake = int(float(stake_text))
        except ValueError:
            stake = 0
        profit = result.get("_profit", 0)
        stats = portfolios.setdefault(name, {"matches": 0, "stake": 0, "profit": 0, "wins": 0, "max_drawdown": 0})
        stats["matches"] += 1
        stats["stake"] += stake
        stats["profit"] += profit
        stats["wins"] += 1 if profit > 0 else 0
        stats["max_drawdown"] = min(stats.get("max_drawdown", 0), profit)
        stats["roi"] = stats["profit"] / stats["stake"] if stats["stake"] else 0
        stats["win_rate"] = stats["wins"] / stats["matches"] if stats["matches"] else 0
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def role_contribution_rows(settlement_results):
    grouped = {}
    for result in settlement_results or []:
        for row in result.get("_detail") or []:
            roles = row.get("_roles") or []
            if not roles:
                roles = [{"role_cn": row.get("_role") or row.get("资产角色") or "未分类", "weight": 1}]
            for role_entry_data in roles:
                role = role_entry_data.get("role_cn") or "未分类"
                weight = role_entry_data.get("weight", 1)
                grouped.setdefault(role, {"stake": 0, "profit": 0, "count": 0, "bets": []})
                grouped[role]["stake"] += row.get("_amount", 0) * weight
                grouped[role]["profit"] += row.get("_profit", 0) * weight
                grouped[role]["count"] += 1
                bet_name = row.get("投注")
                if bet_name and bet_name not in grouped[role]["bets"]:
                    grouped[role]["bets"].append(bet_name)
    output = []
    for role, data in sorted(grouped.items(), key=lambda item: item[1]["profit"], reverse=True):
        roi = data["profit"] / data["stake"] if data["stake"] else 0
        output.append({
            "资产角色": role,
            "代表投注": "、".join(data.get("bets", [])[:4]) or "-",
            "投入": f"{round(data['stake'])}元",
            "盈亏": f"{round(data['profit']):+d}元",
            "ROI": percent(roi),
            "结算项": data["count"],
            "解释": role_contribution_explanation(role, data["profit"]),
        })
    return output


def role_contribution_explanation(role, profit):
    if role == "收益资产":
        return "负责放大利润。" if profit > 0 else "高波动资产未命中。"
    if role == "保险资产":
        return "降低偏离路径亏损。" if profit >= 0 else "保险成本支出。"
    if role == "方向资产":
        return "主逻辑兑现。" if profit > 0 else "方向判断未兑现。"
    if role == "节奏资产":
        return "比赛节奏判断兑现。" if profit > 0 else "节奏判断偏离。"
    if role == "尾部资产":
        return "极端路径保护生效。" if profit > 0 else "尾部保护成本。"
    return "辅助贡献。"


def model_error_summary(match, distribution, final_score):
    if not final_score:
        return "缺少最终比分，暂无法计算模型误差。"
    top_scores = score_candidates(match, distribution, [])[:3]
    actual_category = score_path_label(match, distribution, final_score)
    if final_score in top_scores:
        return f"最终比分 {final_score} 命中模型主路径候选。"
    try:
        home_goals, away_goals = [int(part) for part in final_score.split(":", 1)]
        top_home, top_away = [int(part) for part in top_scores[0].split(":", 1)] if top_scores else (0, 0)
        goal_error = abs((home_goals + away_goals) - (top_home + top_away))
    except (ValueError, IndexError):
        goal_error = 0
    return (
        f"最终比分 {final_score} 属于「{actual_category}」。"
        f"模型候选主路径为 {', '.join(top_scores[:3]) or '-'}，总进球误差约 {goal_error} 球。"
    )


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
    selected = auto_correct_score_pool(ranked, target_share=0.55, min_count=2, max_count=max(limit, 8))
    return selected or ranked[:limit]


def build_strategy_library(combo, match, distribution):
    groups = strategy_item_groups(combo)
    best_correct = groups["correct"][:1]
    double_correct = groups["correct"][:2]
    main_path_correct = main_path_correct_scores(combo, match, distribution, limit=8)
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
    active = [
        item for item in combo
        if item.get("type") != "empty" and item.get("standard_odds")
    ]
    if len(active) < 2:
        return None
    optimized = optimize_betting_portfolio(match, distribution, active, total_stake, risk_profile="standard")
    if not optimized:
        return None
    candidate = {
        "code": "O",
        "name": "赔率分布优化器",
        "items": optimized["items"],
        "fixed_amounts": True,
        "optimizer": optimized,
    }
    return evaluate_strategy(candidate, match, distribution, total_stake)


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
    role_scores = {
        "方向资产": 1.0,
        "保险资产": 0.78,
        "收益资产": 0.68,
        "节奏资产": 0.45,
        "尾部资产": 0.40,
        "辅助资产": 0.30,
    }
    roles = betting_asset_roles(item, match, distribution)
    base = sum(role_scores.get(role["role_cn"], 0.30) * role["weight"] for role in roles)
    alignment = item_direction_alignment(item, match, distribution)
    if any(role["role_cn"] == "方向资产" for role in roles):
        base = min(1.0, base + alignment * 0.08)
    return base


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
    sharpe_ratio,
    stability_score,
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
    sharpe_points = max(0, min(8, (sharpe_ratio + 0.2) * 10))
    stability_points = max(0, min(8, stability_score / 12.5))
    concentration_points = max(0, (1 - concentration) * 8)
    raw_total = (
        ev_points
        + hit_points
        + rr_points
        + loss_points
        + direction_points
        + strategic_points
        + sharpe_points
        + stability_points
        + concentration_points
    )
    total = round(50 + (raw_total - 50) * 1.35)
    if direction_alignment < 0.45:
        total = min(total, 80)
    return clamp(total), {
        "方向一致性": round(direction_points),
        "战略价值": round(strategic_points),
        "Sharpe": round(sharpe_points),
        "稳定性": round(stability_points),
        "命中率": round(hit_points),
        "EV": round(ev_points),
        "风险收益比": round(rr_points),
        "最大亏损控制": round(loss_points),
        "路径分散度": round(concentration_points),
    }


def evaluate_strategy(strategy, match, distribution, total_stake):
    items = strategy["items"] if strategy.get("fixed_amounts") else allocate_strategy_items(strategy["items"], total_stake)
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
        row["比分概率"] = percent(probability)
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
    sharpe_ratio = expected_profit / volatility if volatility else 0
    risk_reward = max_profit / max_loss if max_loss else max_profit / total_stake if total_stake else 0
    coverage = sum(item.get("coverage_rate") or 0 for item in items) / len(items) if items else 0
    concentration = weighted_combo_correlation(items)
    direction_alignment = strategy_direction_alignment(items, match, distribution)
    strategic_value = strategy_strategic_value(items, match, distribution)
    ev_yield = expected_profit / total_stake if total_stake else 0
    capital_efficiency = expected_profit / total_stake if total_stake else 0
    stability_score = portfolio_stability_score(volatility, max_loss, total_stake, concentration, profits)
    score, score_components = strategy_score(
        ev_yield,
        hit_rate,
        risk_reward,
        max_loss,
        total_stake,
        concentration,
        direction_alignment,
        strategic_value,
        sharpe_ratio,
        stability_score,
    )
    style = portfolio_style(items, match, distribution, {"concentration": concentration, "volatility": volatility})

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
        "sharpe_ratio": sharpe_ratio,
        "risk_reward": risk_reward,
        "coverage": min(1, coverage),
        "concentration": concentration,
        "direction_alignment": direction_alignment,
        "strategic_value": strategic_value,
        "role_constraint": {
            "adjustment": role_balance_adjustment(items, match, distribution),
            "rows": role_constraint_rows(items, match, distribution),
        },
        "portfolio_style": style,
        "stability_score": stability_score,
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
    ranked = sorted(evaluated, key=lambda item: item["score"], reverse=True)
    for index, strategy in enumerate(ranked):
        strategy["original_name"] = strategy["name"]
        strategy["rank_name"] = normalize_portfolio_name(strategy["name"], index)
    return ranked


def efficient_frontier_rows(strategies):
    if not strategies:
        return []
    sorted_by_risk = sorted(strategies, key=lambda item: item.get("volatility", 0))
    rows = []
    for index, strategy in enumerate(sorted_by_risk):
        if index == 0:
            zone = "低风险"
        elif index == len(sorted_by_risk) - 1:
            zone = "高收益高风险"
        else:
            zone = "均衡"
        rows.append({
            "区域": zone,
            "组合": strategy.get("rank_name", strategy["name"]),
            "EV": f"{strategy['expected_profit']:+.0f}",
            "风险": f"{strategy.get('volatility', 0):.0f}",
            "最大亏损": f"-{strategy.get('max_loss', 0):.0f}",
            "Sharpe": f"{strategy.get('sharpe_ratio', 0):.2f}",
            "说明": "风险更低" if zone == "低风险" else ("收益弹性更高" if zone == "高收益高风险" else "收益和风险较均衡"),
        })
    return rows


def strategy_table_rows(strategies, match=None, distribution=None):
    rows = []
    for strategy in strategies:
        role_rows = role_allocation_rows(strategy.get("items") or [], match or {}, distribution or {})
        role_text = " / ".join(f"{row['资产角色']} {row['占比']}" for row in role_rows[:3])
        rows.append({
            "组合": strategy.get("rank_name", strategy["name"]),
            "来源": strategy.get("original_name", strategy["name"]),
            "风格": (strategy.get("portfolio_style") or {}).get("style_cn", "-"),
            "角色结构": role_text or "-",
            "命中率": percent(strategy["hit_rate"]),
            "EV": f"{strategy['expected_profit']:+.0f}",
            "预期收益率": f"{strategy['expected_yield'] * 100:+.1f}%",
            "资金效率": f"{strategy['capital_efficiency'] * 100:+.1f}%",
            "最大盈利": f"{strategy['max_profit']:+.0f}",
            "最大亏损": f"-{strategy['max_loss']:.0f}",
            "盈亏波动": f"{strategy['volatility']:.0f}",
            "Sharpe": f"{strategy.get('sharpe_ratio', 0):.2f}",
            "稳定性": f"{strategy.get('stability_score', 0)} / 100",
            "风险收益比": f"{strategy['risk_reward']:.2f}",
            "覆盖率": percent(strategy["coverage"]),
            "路径集中度": percent(strategy["concentration"]),
            "方向一致性": percent(strategy["direction_alignment"]),
            "战略价值": percent(strategy["strategic_value"]),
            "综合评分": strategy["score"],
        })
    return rows


def prematch_strategy_ranking_rows(strategies):
    rows = []
    for strategy in strategies[:5]:
        rows.append({
            "组合": strategy.get("rank_name", strategy["name"]),
            "来源": strategy.get("original_name", strategy["name"]),
            "EV": f"{strategy['expected_profit']:+.0f}",
            "ROI预测": f"{strategy['expected_yield'] * 100:+.1f}%",
            "命中率": percent(strategy["hit_rate"]),
            "最大盈利": f"{strategy['max_profit']:+.0f}",
            "最大亏损": f"-{strategy['max_loss']:.0f}",
            "Sharpe": f"{strategy.get('sharpe_ratio', 0):.2f}",
            "稳定性": f"{strategy.get('stability_score', 0)} / 100",
            "保险成本": insurance_cost_summary(strategy, strategies),
            "综合评分": strategy["score"],
        })
    return rows


def insurance_cost_summary(strategy, strategies):
    correct_only = [
        item for item in strategies
        if item.get("items") and all(asset.get("type") == "correct_score" for asset in item.get("items", []))
    ]
    if not correct_only:
        return "-"
    pure = max(correct_only, key=lambda item: item.get("expected_profit", -999999))
    delta = strategy.get("expected_profit", 0) - pure.get("expected_profit", 0)
    if strategy is pure:
        return "纯收益路径"
    return f"{delta:+.0f}"


def settlement_preview_rows(strategy, match, distribution):
    rows = []
    for item in (strategy or {}).get("items") or []:
        rows.append({
            "投注": item.get("name", "-"),
            "资产角色": insurance_asset_role(item, match, distribution),
            "金额": f"{item.get('amount', 0)}元",
            "赔率": fmt_odds(item.get("odds") or item.get("effective_odds") or item.get("standard_odds")),
            "覆盖率": percent(item.get("coverage_rate") or 0),
            "作用": recommendation_reason(item),
        })
    return rows


def why_portfolio_rows(strategy, match, distribution):
    rows = []
    for item in (strategy or {}).get("items") or []:
        rows.append({
            "资产": item.get("name", "-"),
            "角色": " / ".join(role["role_cn"] for role in betting_asset_roles(item, match, distribution)),
            "原因": recommendation_reason(item),
            "方向一致性": percent(item_direction_alignment(item, match, distribution)),
            "EV提升": f"{(item.get('ev_lift') or 0) * 100:+.1f}%" if item.get("ev_lift") is not None else "-",
        })
    return rows


def top_outcome_preview_rows(strategy):
    rows = []
    for row in (strategy or {}).get("score_rows", [])[:10]:
        rows.append({
            "比分": row.get("比分", "-"),
            "概率": row.get("比分概率", "-"),
            "组合收益": row.get("组合收益", "-"),
            "EV贡献": row.get("EV贡献", "-"),
            "路径": row.get("路径", "-"),
        })
    return rows


def risk_path_rows(strategy):
    rows = sorted(
        strategy.get("score_rows", []),
        key=lambda row: row.get("_total", 0),
    )
    labels = ["主要风险路径", "次要风险路径", "尾部风险路径"]
    output = []
    for label, row in zip(labels, rows[:3]):
        output.append({
            "风险类型": label,
            "比分": row.get("比分", "-"),
            "概率": row.get("比分概率", "-"),
            "组合收益": row.get("组合收益", "-"),
            "原因": row.get("路径", "-"),
        })
    return output


def strategy_component_rows(strategies):
    rows = []
    for strategy in strategies:
        row = {"组合": strategy.get("rank_name", strategy["name"]), "来源": strategy.get("original_name", strategy["name"])}
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
            "组合": current.get("rank_name", current["name"]),
            "来源": current.get("original_name", current["name"]),
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
            "方案": "当前第一名",
            "组合": best.get("rank_name", best["name"]),
            "来源": best.get("original_name", best["name"]),
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


def insurance_cost_rows(strategies, match=None, distribution=None):
    if not strategies:
        return []
    protected = strategies[0]
    rows = []
    correct_only_candidates = [
        strategy for strategy in strategies
        if strategy.get("items") and all(item.get("type") == "correct_score" for item in strategy.get("items", []))
    ]
    if correct_only_candidates:
        pure = max(correct_only_candidates, key=lambda strategy: strategy.get("expected_profit", -999999))
        ev_delta = protected["expected_profit"] - pure["expected_profit"]
        risk_reduction = pure["max_loss"] - protected["max_loss"]
        efficiency = risk_reduction / abs(ev_delta) if ev_delta < 0 else None
        rows.extend([
            {
            "组合": protected.get("rank_name", protected["name"]),
            "类型": "含保险资产",
            "EV": f"{protected['expected_profit']:+.0f}",
            "预期收益率": f"{protected['expected_yield'] * 100:+.1f}%",
            "命中率": percent(protected["hit_rate"]),
            "最大亏损": f"-{protected['max_loss']:.0f}",
            "保险效率": "-",
            "说明": "独赢、让球、大小球用于覆盖非精确比分路径。",
        },
        {
            "组合": pure.get("rank_name", pure["name"]),
            "类型": "纯波胆路径",
            "EV": f"{pure['expected_profit']:+.0f}",
            "预期收益率": f"{pure['expected_yield'] * 100:+.1f}%",
            "命中率": percent(pure["hit_rate"]),
            "最大亏损": f"-{pure['max_loss']:.0f}",
            "保险效率": "-",
            "说明": "更依赖精确比分，收益弹性高但路径覆盖窄。",
        },
        {
            "组合": "保险成本",
            "类型": "差额",
            "EV": f"{ev_delta:+.0f}",
            "预期收益率": f"{(protected['expected_yield'] - pure['expected_yield']) * 100:+.1f}%",
            "命中率": f"{(protected['hit_rate'] - pure['hit_rate']) * 100:+.1f}pct",
            "最大亏损": f"{risk_reduction:+.0f}",
            "保险效率": f"{efficiency:.2f}" if efficiency is not None else "无需牺牲EV",
            "说明": "如果EV下降但命中率提升，这部分下降就是购买路径保险的成本。",
            },
        ])

    items = protected.get("items") or []
    total_stake = sum(item.get("amount", 0) for item in items)
    if match and distribution and total_stake:
        for item in items:
            if item.get("type") == "correct_score":
                continue
            remaining = [other for other in items if other is not item]
            if not remaining:
                continue
            without = evaluate_strategy(
                {"code": "I", "name": "移除保险资产", "items": remaining, "fixed_amounts": True},
                match,
                distribution,
                sum(other.get("amount", 0) for other in remaining),
            )
            ev_delta = protected["expected_profit"] - without["expected_profit"]
            risk_reduction = without["max_loss"] - protected["max_loss"]
            efficiency = risk_reduction / abs(ev_delta) if ev_delta < 0 else None
            rows.append({
                "组合": item.get("name", "-"),
                "类型": insurance_asset_role(item, match, distribution),
                "EV": f"{ev_delta:+.0f}",
                "预期收益率": "-",
                "命中率": "-",
                "最大亏损": f"{risk_reduction:+.0f}",
                "保险效率": f"{efficiency:.2f}" if efficiency is not None else ("提升EV" if ev_delta >= 0 else "-"),
                "说明": "相对移除该资产后，衡量它带来的EV变化与最大亏损下降。",
            })
    return rows


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
            f"策略优化器首选「{best.get('rank_name', best['name'])}」。虽然「{second.get('rank_name', second['name'])}」预期收益率更高，"
            f"但「{best.get('rank_name', best['name'])}」命中率更高、路径更稳，综合评分更优。"
        )
    if best["concentration"] >= 0.75:
        return (
            f"策略优化器首选「{best.get('rank_name', best['name'])}」，但路径集中度偏高。"
            "这代表多个投注依赖同一比赛剧本，需要控制总仓位。"
        )
    return (
        f"策略优化器首选「{best.get('rank_name', best['name'])}」，综合评分 {best['score']}。"
        "该策略在命中率、EV和风险收益比之间更均衡。"
    )


def strategy_j_comparison(strategies):
    current = next((strategy for strategy in strategies if strategy["code"] == "A"), None)
    main_correct = next((strategy for strategy in strategies if strategy["code"] == "J"), None)
    if not current or not main_correct:
        return None
    if main_correct["score"] > current["score"]:
        return (
            f"「主路径波胆组合」评分 {main_correct['score']}，高于当前推荐组合 {current['score']}。"
            f"它的预期收益率为 {main_correct['expected_yield'] * 100:+.1f}%，"
            f"命中率为 {percent(main_correct['hit_rate'])}。"
            "这说明本场可以把主路径波胆作为激进策略重点观察。"
        )
    return (
        f"当前推荐组合评分 {current['score']}，高于「主路径波胆组合」{main_correct['score']}。"
        f"主路径波胆组合预期收益率为 {main_correct['expected_yield'] * 100:+.1f}%，"
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


def normalize_portfolio_name(name, index=None, source=None):
    if source == "My Portfolio" or str(name or "").strip() in {"用户实际组合", "我的组合", "User Portfolio"}:
        return "我的组合"
    text = str(name or "").strip()
    if text in {"推荐组合（当前最优）", "首选组合", "当前推荐组合"}:
        return "推荐组合"
    if text.startswith("备选组合"):
        try:
            number = int(re.sub(r"\D+", "", text))
            return f"第{number + 1}组合"
        except ValueError:
            return text
    match = re.search(r"第(\d+)优组合", text)
    if match:
        return f"第{match.group(1)}组合"
    if text == "推荐组合":
        return text
    if re.match(r"^第\d+组合$", text):
        return text
    if index == 0:
        return "推荐组合"
    if index is not None:
        return f"第{index + 1}组合"
    return text or "-"


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
        if st.checkbox("显示支持的输入格式", value=False, key=f"actual_odds_format_{user_odds_slug(match)}"):
            st.code(actual_odds_example(match), language="text")
            st.caption("一行一个投注，适合从 Excel 复制；旧的多行格式仍然兼容。")
        return parsed


HISTORY_DIR = Path("data/history")
MY_PORTFOLIO_DIR = HISTORY_DIR / "my_portfolios"


def history_slug(match, selected_fixture=None):
    date_key = None
    if selected_fixture:
        local_time = fixture_local_datetime(selected_fixture)
        if local_time:
            date_key = local_time.strftime("%Y-%m-%d")
    raw = f"{date_key or 'match'}_{match['home_cn']}_{match['away_cn']}"
    return re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "_", raw).strip("_") or "match"


def snapshot_path(match, selected_fixture=None):
    return pre_match_snapshot_path(match, selected_fixture)


def legacy_snapshot_path(match, selected_fixture=None):
    return HISTORY_DIR / f"{history_slug(match, selected_fixture)}.json"


def pre_match_snapshot_path(match, selected_fixture=None):
    return HISTORY_DIR / f"{history_slug(match, selected_fixture)}_pre.json"


def post_match_snapshot_path(match, selected_fixture=None):
    return HISTORY_DIR / f"{history_slug(match, selected_fixture)}_post.json"


def my_portfolio_path(match, selected_fixture=None):
    return MY_PORTFOLIO_DIR / f"{history_slug(match, selected_fixture)}.json"


def json_safe(value):
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def save_match_snapshot(match, selected_fixture, payload):
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = pre_match_snapshot_path(match, selected_fixture)
    if path.exists():
        return path, False
    data = {
        "schema_version": 2,
        "snapshot_type": "pre_match_snapshot",
        "created_at": datetime.now().astimezone().isoformat(),
        "match": {
            "home": match["home_cn"],
            "away": match["away_cn"],
            "display": f"{team_cn(match['home_cn'])} vs {team_cn(match['away_cn'])}",
        },
        "fixture": json_safe(selected_fixture),
        **json_safe(payload),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path, True


def save_post_match_snapshot(match, selected_fixture, payload):
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = post_match_snapshot_path(match, selected_fixture)
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
        changed = False
        refreshable_keys = {
            "strategy_settlement",
            "role_contribution",
            "role_contribution_by_portfolio",
            "model_error",
            "prediction_audit",
            "prediction_audit_by_portfolio",
            "recommendation_audit",
            "portfolio_audit_details",
            "best_strategy",
            "worst_strategy",
            "my_portfolio",
        }
        for key, value in json_safe(payload).items():
            if key not in existing or key in refreshable_keys:
                existing[key] = value
                changed = True
        if changed:
            existing["updated_at"] = datetime.now().astimezone().isoformat()
            path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
        return path, False
    data = {
        "schema_version": 2,
        "snapshot_type": "post_match_snapshot",
        "created_at": datetime.now().astimezone().isoformat(),
        "match": {
            "home": match["home_cn"],
            "away": match["away_cn"],
            "display": f"{team_cn(match['home_cn'])} vs {team_cn(match['away_cn'])}",
        },
        "fixture": json_safe(selected_fixture),
        **json_safe(payload),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path, True


def load_match_snapshot(match, selected_fixture=None):
    for path in (
        pre_match_snapshot_path(match, selected_fixture),
        legacy_snapshot_path(match, selected_fixture),
    ):
        if not path.exists():
            continue
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    return None


def load_post_match_snapshot(match, selected_fixture=None):
    path = post_match_snapshot_path(match, selected_fixture)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def my_portfolio_example():
    return """独赢,瑞士,600
让球,瑞士,-1,600
大小球,Under 2.5,600
波胆,2:0,500
波胆,1:0,300"""


def my_portfolio_market_key(label):
    text = str(label or "").strip().lower()
    if "独赢" in text or "winner" in text:
        return "winner"
    if "让球" in text or "handicap" in text:
        return "handicap"
    if "大小" in text or "over" in text or "under" in text:
        return "total"
    if "波胆" in text or "correct" in text or re.match(r"^\d+\s*[:：-]\s*\d+$", text):
        return "correct_score"
    return None


TEAM_CODE_ALIASES = {
    "sui": "瑞士",
    "switzerland": "瑞士",
    "bosnia": "波黑",
    "bih": "波黑",
    "bosnia&herzegovina": "波黑",
    "bosniaandherzegovina": "波黑",
    "bosniaherzegovina": "波黑",
}


def compact_text(value):
    text = str(value or "").lower()
    text = text.replace("（", "(").replace("）", ")")
    return re.sub(r"\s+", "", text)


def team_alias_map(match=None):
    aliases = {}
    for en, cn in TEAM_CN.items():
        aliases[compact_text(en)] = cn
        aliases[compact_text(cn)] = cn
    aliases.update(TEAM_CODE_ALIASES)
    if match:
        for key in ("home_cn", "away_cn", "home_en", "away_en"):
            value = match.get(key)
            if value:
                aliases[compact_text(value)] = team_cn(value)
                aliases[compact_text(team_cn(value))] = team_cn(value)
    return aliases


def canonical_bet_text(value, match=None):
    text = compact_text(value).replace("：", ":")
    text = text.replace("小于", "under").replace("小", "under")
    text = text.replace("大于", "over").replace("大", "over")
    text = text.replace("独赢", "win").replace("获胜", "win").replace("胜", "win")
    text = text.replace("受让", "+").replace("让球", "").replace("让", "-").replace("球", "")
    if match:
        text = text.replace("home", compact_text(team_cn(match.get("home_cn"))))
        text = text.replace("away", compact_text(team_cn(match.get("away_cn"))))
    for alias, canonical in sorted(team_alias_map(match).items(), key=lambda item: len(item[0]), reverse=True):
        if alias:
            text = text.replace(alias, compact_text(canonical))
    text = re.sub(r"\.0\b", "", text)
    return text


def match_portfolio_candidate(selection, candidates, item_type=None, match=None):
    normalized_selection = normalize_score(selection)
    canonical_selection = canonical_bet_text(selection, match)
    for candidate in candidates:
        if item_type and candidate.get("type") != item_type:
            continue
        candidate_selection = str(candidate.get("selection") or "")
        candidate_name = str(candidate.get("name") or "")
        if candidate.get("type") == "correct_score":
            if normalize_score(candidate_selection) == normalized_selection:
                return candidate
        else:
            candidate_text = canonical_bet_text(f"{candidate_selection} {candidate_name}", match)
            if canonical_selection and (canonical_selection in candidate_text or candidate_text in canonical_selection):
                return candidate
            if normalized_selection.lower() in candidate_selection.lower() or normalized_selection.lower() in candidate_name.lower():
                return candidate
    return None


def normalize_portfolio_line(raw_line):
    line = str(raw_line or "").strip()
    line = line.replace("，", ",").replace("；", ",").replace(";", ",")
    line = line.replace("\t", " ")
    return re.sub(r"\s+", " ", line).strip()


def split_portfolio_amount(line):
    text = normalize_portfolio_line(line)
    if not text:
        return "", None
    if "," in text:
        parts = [part.strip() for part in text.split(",") if part.strip()]
        if len(parts) >= 2:
            try:
                return " ".join(parts[:-1]), int(float(parts[-1]))
            except ValueError:
                return text, None
    score_glued = re.search(r"(\d+\s*[:：-]\s*\d+)\s*(\d{2,7})$", text)
    if score_glued:
        return score_glued.group(1), int(score_glued.group(2))
    total_glued = re.search(r"((?:under|over|小于|大于|小|大)\s*\d+(?:\.\d)?)\s*(\d{2,7})$", text, re.I)
    if total_glued:
        return total_glued.group(1), int(total_glued.group(2))
    handicap_glued = re.search(r"(.+?[+-]\d(?:\.\d{1,2})?)\s*(\d{2,7})$", text)
    if handicap_glued:
        return handicap_glued.group(1), int(handicap_glued.group(2))
    normal = re.search(r"(.+?)\s+(\d{1,7})$", text)
    if normal:
        return normal.group(1), int(normal.group(2))
    glued = re.search(r"(.+?)(\d{2,7})$", text)
    if glued:
        return glued.group(1), int(glued.group(2))
    return text, None


def outcome_selection_for_manual_item(selection, item_type, match):
    text = str(selection or "").strip()
    if item_type == "handicap" and match:
        line_match = re.search(r"([+-]?\d+(?:\.\d+)?)", text)
        line = line_match.group(1) if line_match else ""
        if team_cn(match.get("home_cn")) in text or str(match.get("home_cn")) in text:
            return f"Home {line}".strip()
        if team_cn(match.get("away_cn")) in text or str(match.get("away_cn")) in text:
            return f"Away {line}".strip()
    return text


def infer_portfolio_type_and_selection(body, match=None):
    text = normalize_portfolio_line(body)
    score_match = re.search(r"(\d+\s*[:：-]\s*\d+)", text)
    if score_match:
        return "correct_score", normalize_score(score_match.group(1)) or score_match.group(1)
    text = re.sub(r"(?<!\d)[:：]|[:：](?!\d)", " ", text).strip()
    total_match = re.search(r"(under|over|小于|大于|小|大)\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
    if total_match:
        side = total_match.group(1).lower()
        side_en = "Under" if side in {"under", "小于", "小"} else "Over"
        return "total", f"{side_en} {total_match.group(2)}"
    explicit_type = my_portfolio_market_key(text)
    line_match = re.search(r"([+-]\d+(?:\.\d+)?)", text)
    let_match = re.search(r"(.+?)(?:让球|让)\s*([0-9]+(?:\.[0-9]+)?)", text)
    receive_match = re.search(r"(.+?)受让\s*([0-9]+(?:\.[0-9]+)?)", text)
    if explicit_type == "handicap" or "让" in text or line_match or let_match or receive_match:
        if receive_match:
            team_text = receive_match.group(1)
            line = f"+{receive_match.group(2)}"
        elif let_match:
            team_text = let_match.group(1)
            line = f"-{let_match.group(2)}"
        else:
            line = line_match.group(1) if line_match else ""
            team_text = text.replace(line, "")
        team_text = re.sub(r"(让球|handicap|让|受让)", "", team_text, flags=re.I).strip(" ,:")
        return "handicap", f"{team_text} {line}".strip()
    if explicit_type == "winner" or "win" in compact_text(text) or "胜" in text or text:
        team_text = re.sub(r"(独赢|winner|win|获胜|胜)", "", text, flags=re.I).strip(" ,:")
        return "winner", team_text or text
    return None, text


def parse_my_portfolio(raw_text, candidates, match=None):
    items = []
    for line in str(raw_text or "").splitlines():
        body, amount = split_portfolio_amount(line)
        if not body or amount is None:
            continue
        item_type, selection = infer_portfolio_type_and_selection(body, match)
        candidate = match_portfolio_candidate(selection, candidates, item_type, match)
        if not candidate:
            settlement_selection = outcome_selection_for_manual_item(selection, item_type, match)
            items.append({
                "type": item_type or "unknown",
                "selection": settlement_selection,
                "name": selection,
                "amount": amount,
                "odds": None,
                "standard_odds": None,
                "effective_odds": None,
                "matched": False,
                "match_error": unmatched_portfolio_reason(item_type),
                "raw_input": line,
            })
            continue
        odds_value = candidate.get("effective_odds") or candidate.get("odds") or candidate.get("standard_odds")
        items.append({
            **candidate,
            "amount": amount,
            "odds": odds_value,
            "effective_odds": odds_value,
            "matched": True,
            "raw_input": line,
        })
    return items


def unmatched_portfolio_reason(item_type):
    if item_type == "winner":
        return "未找到对应独赢赔率。"
    if item_type == "handicap":
        return "未找到对应让球赔率。"
    if item_type == "total":
        return "未找到对应大小球赔率。"
    if item_type == "correct_score":
        return "未找到对应波胆赔率。"
    return "未找到对应赔率。"


def load_my_portfolio(match, selected_fixture=None):
    path = my_portfolio_path(match, selected_fixture)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def save_my_portfolio(match, selected_fixture, raw_text, items):
    MY_PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": 1,
        "updated_at": datetime.now().astimezone().isoformat(),
        "match": f"{team_cn(match['home_cn'])} vs {team_cn(match['away_cn'])}",
        "raw_text": raw_text,
        "items": json_safe(items),
    }
    path = my_portfolio_path(match, selected_fixture)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def render_my_portfolio_input(match, selected_fixture, candidates, title="我的组合", submit_label="保存我的组合", show_examples=False):
    key = f"my_portfolio_{history_slug(match, selected_fixture)}"
    cache = load_my_portfolio(match, selected_fixture)
    if key not in st.session_state and cache:
        st.session_state[key] = cache.get("raw_text", "")
    raw = st.session_state.get(key, "")
    with st.container(border=True):
        st.markdown(f'<div class="section-title">{escape(title)}</div>', unsafe_allow_html=True)
        st.caption("记录你真实下注的组合。赛后会用最终比分自动核算盈亏。")
        if show_examples:
            input_col, example_col = st.columns([1.15, 0.85])
            form_area = input_col
        else:
            form_area, example_col = None, None
        if form_area:
            form_context = form_area
        else:
            form_context = st.container()
        with form_context:
            with st.form(key=f"{key}_form"):
                raw_input = st.text_area(
                    "真实下注组合",
                    value=raw,
                    height=180 if show_examples else 150,
                    placeholder=my_portfolio_example(),
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button(submit_label, type="secondary")
        if example_col:
            with example_col:
                st.markdown("**输入格式示例**")
                st.code(my_portfolio_example(), language="text")
                st.caption("最后一个数字为下注金额。可混合录入独赢、让球、大小球和波胆。")
        if submitted:
            st.session_state[key] = raw_input
            raw = raw_input
        items = parse_my_portfolio(raw, candidates, match)
        if submitted:
            cache = save_my_portfolio(match, selected_fixture, raw, items)
            st.success(f"我的组合已保存：{format_cache_time(cache.get('updated_at'))} · {len(items)}项")
        if items:
            rows = [
                {
                    "原始输入": item.get("raw_input", "-"),
                    "识别类型": {
                        "winner": "独赢",
                        "handicap": "让球",
                        "total": "大小球",
                        "correct_score": "波胆",
                    }.get(item.get("type"), "未知"),
                    "投注": item.get("name", item.get("selection", "-")),
                    "金额": f"{item.get('amount', 0)}元",
                    "赔率": fmt_odds(item.get("odds")),
                    "匹配": "已匹配赛前赔率" if item.get("matched") else item.get("match_error", "未找到对应赔率。"),
                }
                for item in items
            ]
            st.markdown("**解析结果**")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            missing = [item.get("match_error") for item in items if not item.get("matched")]
            if missing:
                st.warning("；".join(dict.fromkeys(error for error in missing if error)))
        else:
            st.caption("尚未保存真实下注组合。")
        return {"raw_text": raw, "items": items}


def snapshot_portfolio_candidates(snapshot, match, distribution):
    items = []
    for item in (((snapshot or {}).get("actual_odds") or {}).get("items") or []):
        item_type = item.get("type")
        selection = item.get("selection")
        odds_value = item.get("odds")
        if not item_type or not selection or not odds_value:
            continue
        name = f"波胆 {selection}" if item_type == "correct_score" else str(selection)
        if item_type == "winner":
            name = f"{team_cn(selection)}独赢"
        items.append({
            "slot": "用户赛前赔率",
            "type": item_type,
            "selection": selection,
            "name": name,
            "standard_odds": odds_value,
            "effective_odds": odds_value,
            "odds": odds_value,
            "source": "用户赛前录入赔率",
        })
    for strategy in ((snapshot or {}).get("strategy_snapshot") or {}).get("strategies") or []:
        for item in strategy.get("items") or []:
            if item.get("type") != "empty":
                items.append(item)
    if items:
        unique = {}
        for item in items:
            key = (item.get("type"), item.get("selection"), item.get("name"))
            if key not in unique:
                unique[key] = item
        return list(unique.values())
    return ((snapshot or {}).get("recommendation_combo") or [])


def render_my_portfolio_settlement(match, selected_fixture, snapshot, distribution, final_score):
    candidates = snapshot_portfolio_candidates(snapshot, match, distribution)
    with st.container(border=True):
        st.markdown('<div class="section-title">我的组合结算</div>', unsafe_allow_html=True)
        st.caption("输入或修改你的真实下注组合，保存后会立即按最终比分结算，并进入 Recommendation Audit。")
        portfolio = render_my_portfolio_input(
            match,
            selected_fixture,
            candidates,
            title="我的组合",
            submit_label="保存并结算",
            show_examples=True,
        )
        if not (portfolio or {}).get("items"):
            return portfolio
        settled = settle_items(match, distribution, portfolio.get("items") or [], final_score)
        style = portfolio_style(portfolio.get("items") or [], match, distribution, {
            "concentration": weighted_combo_correlation(portfolio.get("items") or []),
            "volatility": None,
        })
        profit_rows = [score_profit_row(match, distribution, portfolio.get("items") or [], score) for score in score_candidates(match, distribution, portfolio.get("items") or [])]
        max_profit = max((row.get("_total", 0) for row in profit_rows), default=0)
        max_loss = abs(min((row.get("_total", 0) for row in profit_rows), default=0))
        cols = st.columns(6)
        cols[0].metric("最终比分", final_score)
        cols[1].metric("命中情况", result_hit_summary(settled.get("rows") or []))
        cols[2].metric("盈亏", f"{settled.get('profit', 0):+d}元")
        cols[3].metric("ROI", percent(settled.get("roi", 0)))
        cols[4].metric("最大盈利", f"{max_profit:+d}元")
        cols[5].metric("最大亏损", f"-{max_loss}元")
        st.caption(f"组合风格：{style.get('style_cn', '-')} · {style.get('reason', '')}")
        role_rows = role_allocation_rows(portfolio.get("items") or [], match, distribution)
        if role_rows:
            st.dataframe(pd.DataFrame(role_rows), use_container_width=True, hide_index=True)
        return portfolio


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
            st.caption(f"推荐组合来源：{selected_strategy.get('rank_name', selected_strategy['name'])}（{selected_strategy['score']}分）。")
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

        if strategies:
            st.markdown("**赛前策略排行榜**")
            st.caption("按当前真实盘口、实际赔率和比分路径矩阵，对所有候选组合进行赛前排序。")
            st.dataframe(pd.DataFrame(prematch_strategy_ranking_rows(strategies)), use_container_width=True, hide_index=True)

        if selected_strategy:
            role_rows = role_allocation_rows(selected_strategy.get("items") or [], match, distribution)
            if role_rows:
                st.markdown("**赛前资产角色分析**")
                st.caption("先看组合角色，再看具体投注。组合是否稳健，取决于收益、保险、方向、节奏和尾部资产是否失衡。")
                st.dataframe(pd.DataFrame(role_rows), use_container_width=True, hide_index=True)

            preview_rows = settlement_preview_rows(selected_strategy, match, distribution)
            if preview_rows:
                st.markdown("**赛前逐项结算预演**")
                st.caption("这里直接展开推荐组合的每一笔资产，避免推荐逻辑藏在算法里。")
                st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)

            why_rows = why_portfolio_rows(selected_strategy, match, distribution)
            if why_rows:
                st.markdown("**Why This Portfolio**")
                st.caption("解释每个资产为什么进入当前组合。")
                st.dataframe(pd.DataFrame(why_rows), use_container_width=True, hide_index=True)

            risk_rows = risk_path_rows(selected_strategy)
            if risk_rows:
                st.markdown("**赛前风险暴露**")
                st.caption("提前看到当前组合最怕哪些比分路径。")
                st.dataframe(pd.DataFrame(risk_rows), use_container_width=True, hide_index=True)

            top_rows = top_outcome_preview_rows(selected_strategy)
            if top_rows:
                st.markdown("**Top 10 Probable Outcomes**")
                st.caption("按当前概率模型列出最重要的比分路径及对应组合收益。")
                st.dataframe(pd.DataFrame(top_rows), use_container_width=True, hide_index=True)

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
                    st.markdown("**推荐组合生成原因**")
                    st.dataframe(pd.DataFrame(reason_rows), use_container_width=True, hide_index=True)
                discarded_rows = discarded_bet_rows(initial_combo_with_amounts, selected_strategy)
                if discarded_rows:
                    if st.checkbox("显示未进入优化组合的原因", value=False, key="discarded_bet_reasons"):
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
                if st.checkbox("展开推荐组合", value=False, key="strategy_selected_detail"):
                    st.caption("推荐组合来自策略优化器当前第一名，因此这里展示的是最终执行层组合。")
                    render_strategy_detail(selected_strategy, match, distribution)
            matrix_rows = correlation_matrix_rows(combo_with_amounts)
            if matrix_rows:
                if st.checkbox("显示组合相关性矩阵", value=False, key="combo_correlation_matrix"):
                    st.caption("相关性越高，说明多个投注依赖同一比赛路径；组合器会降低过度重叠的仓位。")
                    st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)
                    penalty_rows = correlation_penalty_rows(combo_with_amounts)
                    if penalty_rows:
                        st.markdown("**相关性惩罚如何影响仓位**")
                        st.dataframe(pd.DataFrame(penalty_rows), use_container_width=True, hide_index=True)

            if strategies:
                if st.checkbox("显示高级策略研究", value=False, key="advanced_strategy_research"):
                    st.info(strategy_conclusion(strategies))
                    j_note = strategy_j_comparison(strategies)
                    if j_note:
                        st.caption(j_note)
                    comparison_rows = strategy_direct_comparison_rows(strategies)
                    if comparison_rows:
                        st.markdown("**原始推荐组合 vs 策略第一名**")
                        st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)
                    frontier_rows = efficient_frontier_rows(strategies)
                    if frontier_rows:
                        st.markdown("**有效前沿**")
                        st.caption("按组合风险从低到高排列，用来区分保守、均衡和激进区域。")
                        st.dataframe(pd.DataFrame(frontier_rows), use_container_width=True, hide_index=True)
                    marginal_correct_rows = correct_score_marginal_ev_rows(initial_combo_with_amounts)
                    if marginal_correct_rows:
                        st.markdown("**波胆边际EV曲线**")
                        st.caption("按边际贡献观察波胆数量是否继续增加；边际EV变低时，优化器会自动停止。")
                        st.dataframe(pd.DataFrame(marginal_correct_rows), use_container_width=True, hide_index=True)
                    insurance_rows = insurance_cost_rows(strategies, match, distribution)
                    if insurance_rows:
                        st.markdown("**保险成本分析**")
                        st.caption("把独赢、让球、大小球视为保险资产，比较它们相对纯波胆组合带来的EV变化和路径覆盖变化。")
                        st.dataframe(pd.DataFrame(insurance_rows), use_container_width=True, hide_index=True)
                    st.dataframe(pd.DataFrame(strategy_table_rows(strategies, match, distribution)), use_container_width=True, hide_index=True)
                    st.markdown("**策略评分来源**")
                    st.dataframe(pd.DataFrame(strategy_component_rows(strategies)), use_container_width=True, hide_index=True)
                    st.markdown("**策略详情**")
                    for index, strategy in enumerate(strategies[:5], start=1):
                        label = f"{strategy.get('rank_name', strategy['name'])} · {strategy['score']}分"
                        if st.checkbox(label, value=False, key=f"strategy_detail_{index}_{strategy.get('code', index)}"):
                            render_strategy_detail(strategy, match, distribution)
        else:
            st.info("当前没有足够真实盘口生成投注组合。")
        st.caption("实际赔率优先；未输入时使用真实市场标准赔率。禁止使用估算波胆赔率。")

        top_cols = st.columns(2)
        recommendation = decision["final_recommendation"]
        top_cols[0].metric("推荐方向", bet_cn(recommendation["bet"]))
        top_cols[0].caption(recommendation["reason"][0])
        top_cols[1].metric("赔率价值分", f"{odds_value.get('score', 0)} / 100")
        top_cols[1].caption(decision["value_rating_meaning"])

        if st.checkbox("显示方向把握与赔率价值计算", value=False, key="rating_breakdown_detail"):
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


def worldcup_data_match_dir(match, selected_fixture=None):
    return db_match_dir(match, selected_fixture)


def render_data_completeness(db):
    completeness = (db or {}).get("completeness") or {}
    if not completeness:
        return
    with st.container(border=True):
        st.markdown("**Data Completeness**")
        st.metric("完整度", f"{completeness.get('score', 0)}%")
        rows = [
            {"数据项": row["item"], "状态": "√" if row["ok"] else "×"}
            for row in completeness.get("checks", [])
        ]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def standings_row_for_team(team_name, selected_fixture=None):
    try:
        schedule = fetch_world_cup_schedule(force_refresh=False)
    except Exception:
        return None
    group = (selected_fixture or {}).get("group") or (selected_fixture or {}).get("round") or ""
    standings = schedule.get("standings") or {}
    candidate_groups = []
    if group:
        candidate_groups = [
            rows for name, rows in standings.items()
            if str(group).lower() in str(name).lower() or str(name).lower() in str(group).lower()
        ]
    if not candidate_groups:
        candidate_groups = list(standings.values())
    wanted = str(team_name or "").lower()
    for rows in candidate_groups:
        for row in rows:
            if str(row.get("team") or "").lower() == wanted:
                return row
    return None


def team_profile_metrics(profile, standing):
    items = [
        ("FIFA排名", profile.get("fifa_rank")),
        ("ELO评分", profile.get("elo")),
        ("球队身价", profile.get("team_value")),
        ("平均年龄", profile.get("average_age")),
        ("主教练", profile.get("coach")),
        ("世界杯最佳", profile.get("best_world_cup")),
        ("参赛次数", profile.get("world_cup_appearances")),
    ]
    if standing:
        items.extend([
            ("当前积分", standing.get("points")),
            ("净胜球", standing.get("gd")),
            ("胜平负", f"{standing.get('wins', 0)}胜 {standing.get('draws', 0)}平 {standing.get('losses', 0)}负"),
        ])
    return [{"项目": label, "数据": value} for label, value in items if value not in {None, "", "待接入"}]


def lineup_rows_for_team(lineups, team_name):
    rows = []
    wanted = str(team_name or "").lower()
    for lineup in lineups or []:
        team = (lineup.get("team") or {}).get("name") or ""
        if wanted and team.lower() != wanted:
            continue
        for item in lineup.get("startXI") or []:
            player = item.get("player") or {}
            rows.append({
                "位置": player.get("pos") or "-",
                "球员": player.get("name") or "-",
                "年龄": player.get("age") or "-",
                "俱乐部": player.get("club") or "-",
                "是否主力": "是",
                "身价": player.get("value") or "-",
            })
    return rows


def injury_rows_for_team(injuries, team_name):
    rows = []
    wanted = str(team_name or "").lower()
    for item in injuries or []:
        team = (item.get("team") or {}).get("name") or ""
        if wanted and team.lower() != wanted:
            continue
        player = item.get("player") or {}
        fixture = item.get("fixture") or {}
        rows.append({
            "球员": player.get("name") or "-",
            "原因": player.get("reason") or "-",
            "比赛": fixture.get("date") or "-",
        })
    return rows


def render_team_intelligence(match, selected_fixture, api_football_data):
    st.markdown('<div class="section-title">球队信息</div>', unsafe_allow_html=True)
    fixture_result = (api_football_data or {}).get("fixture_result") or {}
    fixture = (api_football_data or {}).get("fixture") or {}
    teams = [
        fixture_result.get("home_team") or fixture.get("home_team") or (selected_fixture or {}).get("home_team") or {"name": match["home_en"]},
        fixture_result.get("away_team") or fixture.get("away_team") or (selected_fixture or {}).get("away_team") or {"name": match["away_en"]},
    ]
    lineups = (api_football_data or {}).get("lineups") or []
    injuries = (api_football_data or {}).get("injuries") or []
    recent_map = {
        teams[0].get("name"): (api_football_data or {}).get("home_recent") or [],
        teams[1].get("name"): (api_football_data or {}).get("away_recent") or [],
    }
    cols = st.columns(2)
    for col, team in zip(cols, teams):
        team_name = team.get("name") or "-"
        profile = fetch_team_profile(team_name)
        standing = standings_row_for_team(team_name, selected_fixture)
        with col:
            with st.container(border=True):
                team_visual({"name": team_name, "logo": profile.get("logo") or team.get("logo")}, size=64)
                st.markdown(f"### {team_cn(team_name)}")
                profile_rows = team_profile_metrics(profile, standing)
                if profile_rows:
                    st.dataframe(pd.DataFrame(profile_rows), use_container_width=True, hide_index=True)
                summary = team_form_summary(team, recent_map.get(team_name) or [])
                if summary["last5"]["form"]:
                    st.markdown("**近期战绩**")
                    st.markdown(
                        '<div class="form-strip">'
                        + "".join(f'<span class="form-tag form-{result}">{result}</span>' for result in summary["last5"]["form"])
                        + '</div>',
                        unsafe_allow_html=True,
                    )
                    st.caption(
                        f"最近5场：{summary['last5']['wins']}胜{summary['last5']['draws']}平{summary['last5']['losses']}负 · "
                        f"进球/失球 {summary['last5']['gf']}/{summary['last5']['ga']}"
                    )
                rows = lineup_rows_for_team(lineups, team_name)
                st.markdown("**预计/官方首发阵容**")
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                else:
                    st.info("本场官方首发暂未公布；上一场阵容样本未返回。")
                injury_rows = injury_rows_for_team(injuries, team_name)
                st.markdown("**伤病与停赛**")
                if injury_rows:
                    st.dataframe(pd.DataFrame(injury_rows), use_container_width=True, hide_index=True)
                else:
                    st.info("暂无公开伤病或停赛信息。")

    db_dir = worldcup_data_match_dir(match, selected_fixture)
    with st.container(border=True):
        st.markdown("**永久数据库状态**")
        st.caption(f"目录：{db_dir}")
        expected = ["fixture.json", "odds.json", "lineups.json", "injuries.json", "players.json", "events.json", "match_stats.json", "pre_match.json", "post_match.json"]
        rows = [{"文件": name, "状态": "已保存" if (db_dir / name).exists() else "未保存"} for name in expected]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


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
        if st.checkbox("展开全部盘口", value=False, key="market_all_handicap"):
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

        if st.checkbox("展开全部赔率", value=False, key="market_all_totals"):
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
        if st.checkbox("展开全部波胆", value=False, key="market_all_correct_score"):
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


def render_post_match_analysis_tab(match, selected_fixture, distribution, strategies=None, my_portfolio=None):
    with st.container(border=True):
        st.markdown('<div class="section-title">Post Match Analysis</div>', unsafe_allow_html=True)
        snapshot = load_match_snapshot(match, selected_fixture)
        post_snapshot = load_post_match_snapshot(match, selected_fixture)
        if snapshot:
            st.caption(f"Match Snapshot：已保存 · {format_cache_time(snapshot.get('created_at'))}")
        else:
            st.caption("Match Snapshot：尚未保存。打开赛前分析页后会自动保存一次。")
        if post_snapshot:
            st.caption(f"Post Match Snapshot：已保存 · {format_cache_time(post_snapshot.get('created_at'))}")

        if not selected_fixture or not is_finished(selected_fixture):
            st.info("比赛尚未结束。赛后总结将在最终比分返回后自动核算。")
            return

        final_score = final_score_from_fixture(selected_fixture)
        if not final_score:
            st.warning("比赛已结束，但当前赛程数据没有最终比分，暂无法核算盈亏。")
            return

        score_cols = st.columns(4)
        score_cols[0].metric("最终比分", final_score)
        score_cols[1].metric("模型误差", "已计算")
        score_cols[2].metric("快照状态", "已保存" if snapshot else "缺失")
        score_cols[3].metric("用户组合", "已保存" if (my_portfolio or {}).get("items") else "未录入")

        if not strategies and snapshot:
            strategies = (snapshot.get("strategy_snapshot") or {}).get("strategies") or []
        if not my_portfolio:
            my_portfolio = load_my_portfolio(match, selected_fixture) or {}

        my_portfolio = render_my_portfolio_settlement(match, selected_fixture, snapshot or {}, distribution, final_score) or my_portfolio

        results = settle_strategies(match, distribution, strategies or [], my_portfolio or {}, final_score)
        if not results:
            st.info("缺少赛前策略快照或用户实际组合，暂无法生成 Recommendation Audit。")
            return

        model_error = model_error_summary(match, distribution, final_score)
        strategy_by_display_name = {
            normalize_portfolio_name(strategy.get("rank_name", strategy.get("name", "-")), index): strategy
            for index, strategy in enumerate(strategies or [])
        }
        if (my_portfolio or {}).get("items"):
            strategy_by_display_name["我的组合"] = {
                "rank_name": "我的组合",
                "name": "我的组合",
                "items": my_portfolio.get("items") or [],
            }
        selected_strategy = strategy_by_display_name.get("推荐组合") or (strategies[0] if strategies else {})
        prediction_audit_data = prediction_audit(match, distribution, selected_strategy, final_score)
        recommendation_audit_rows = recommendation_audit(match, distribution, strategies or [], final_score, results)
        role_contribution_by_portfolio = {
            result.get("组合", "-"): role_contribution_rows([result])
            for result in results
        }
        prediction_audit_by_portfolio = {
            name: prediction_audit(match, distribution, strategy, final_score)
            for name, strategy in strategy_by_display_name.items()
        }
        post_payload = {
            "model_versions": MODEL_VERSION_TRACKING,
            "final_score": final_score,
            "final_result": {
                "home": parse_score(final_score)[0] if parse_score(final_score) else None,
                "away": parse_score(final_score)[1] if parse_score(final_score) else None,
            },
            "pre_match_snapshot": str(pre_match_snapshot_path(match, selected_fixture)),
            "probability_distribution": distribution,
            "strategies": strategies or [],
            "strategy_settlement": results,
            "my_portfolio": my_portfolio or {},
            "role_contribution_by_portfolio": role_contribution_by_portfolio,
            "model_error": model_error,
            "prediction_audit": prediction_audit_data,
            "prediction_audit_by_portfolio": prediction_audit_by_portfolio,
            "recommendation_audit": recommendation_audit_rows,
            "portfolio_audit_details": {
                result.get("组合", "-"): {
                    "settlement": {key: value for key, value in result.items() if not key.startswith("_")},
                    "items": portfolio_audit_detail_rows(result.get("_detail") or []),
                    "prediction_audit": (prediction_audit_by_portfolio.get(result.get("组合", "-")) or {}).get("rows", []),
                    "model_error": model_error,
                }
                for result in results
            },
            "best_strategy": results[0],
            "worst_strategy": results[-1],
        }
        post_file, post_created = save_post_match_snapshot(match, selected_fixture, post_payload)
        update_style_performance_database(match, selected_fixture, strategies or [], results)
        update_portfolio_performance_database(match, selected_fixture, results)
        st.caption(
            f"Post Match Snapshot：{'已创建' if post_created else '已存在'} · "
            f"{post_file}"
        )

        if recommendation_audit_rows:
            st.markdown("**Recommendation Audit**")
            st.caption("唯一主表：排名、具体投注、盈亏、命中情况和资产角色表现集中在这里。")
            st.dataframe(pd.DataFrame(recommendation_audit_rows), use_container_width=True, hide_index=True)

        st.markdown("**模型误差分析**")
        st.write(model_error)

        contribution_rows = role_contribution_rows(results)
        if contribution_rows:
            st.markdown("**资产角色贡献分析**")
            st.caption("按全部已结算组合汇总，代表投注用于解释每类资产主要来自哪些下注。")
            st.dataframe(pd.DataFrame(contribution_rows), use_container_width=True, hide_index=True)


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
            if st.checkbox("显示官方首发状态", value=False, key="lineups_official_status"):
                if lineups:
                    st.dataframe(lineups, use_container_width=True, hide_index=True)
                else:
                    st.info("官方首发尚未公布")


def render_technical_notes(odds, api_football_data):
    if st.checkbox("显示开发者信息", value=False, key="technical_notes_debug"):
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
    if st.button("刷新赛程状态", type="secondary"):
        fetch_world_cup_schedule.clear()
        st.session_state.force_schedule_refresh = True
        st.rerun()
    force_refresh = st.session_state.pop("force_schedule_refresh", False)
    schedule = fetch_world_cup_schedule(force_refresh=force_refresh)
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
    if st.checkbox("显示全部世界杯赛程", value=False, key="full_schedule_toggle"):
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
        selected_fixture = refresh_selected_fixture_if_needed(st.session_state.get("selected_fixture"))
        if selected_fixture and is_finished(selected_fixture):
            st.session_state.selected_fixture = selected_fixture
            st.session_state.page = "post_match"
            st.rerun()
        local_db = load_match_database(match, selected_fixture)
        if local_db:
            api_football_data = db_api_football_data(local_db)
            odds = db_odds(local_db)
            odds_date_key = odds_date_key_from_fixture(selected_fixture, api_football_data)
        else:
            api_football_data = fetch_match_data(match, "page_market_data_v3")
            odds_date_key = odds_date_key_from_fixture(selected_fixture, api_football_data)
            odds = fetch_odds(match, odds_date_key, "odds_page_v4_24h_cache")
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
        portfolio_candidates = recommendation_combo(match, odds, api_football_data, result_distribution, actual_odds)
        my_portfolio = render_my_portfolio_input(match, selected_fixture, portfolio_candidates)
        total_stake, _ = recommended_total_stake(decision)
        snapshot_combo = stake_amounts(portfolio_candidates, decision)
        snapshot_strategies = strategy_comparison(match, result_distribution, snapshot_combo, total_stake)
        top_strategy = snapshot_strategies[0] if snapshot_strategies else {}
        snapshot_payload = {
            "model_versions": MODEL_VERSION_TRACKING,
            "match_info": {
                "odds_date_key": odds_date_key,
                "report_path": str(report_path),
            },
            "odds": odds,
            "api_football_data": api_football_data,
            "polymarket": polymarket,
            "actual_odds": actual_odds,
            "my_portfolio": my_portfolio,
            "recommendation_combo": snapshot_combo,
            "strategy_snapshot": {
                "strategies": snapshot_strategies,
                "strategy_table": strategy_table_rows(snapshot_strategies, match, result_distribution),
                "insurance_cost": insurance_cost_rows(snapshot_strategies, match, result_distribution),
                "correlation_matrix": correlation_matrix_rows(snapshot_combo),
                "kelly": kelly_reference_rows(snapshot_strategies[0]) if snapshot_strategies else [],
                "return_matrix": (snapshot_strategies[0].get("score_rows") if snapshot_strategies else []),
                "role_constraints": (top_strategy.get("role_constraint") or {}).get("rows", []),
                "portfolio_style": top_strategy.get("portfolio_style", {}),
            },
            "decision": decision,
            "probability_distribution": result_distribution,
            "value_analysis": value_analysis,
            "betting_opinion": betting_opinion,
        }
        snapshot_file, snapshot_created = save_match_snapshot(match, selected_fixture, snapshot_payload)
        st.caption(
            f"Match Snapshot：{'已创建' if snapshot_created else '已存在'} · "
            f"{snapshot_file}"
        )

        core_tab, market_tab, post_tab, source_tab, team_tab = st.tabs([
            "核心决策",
            "市场盘口",
            "赛后总结",
            "数据来源",
            "球队信息",
        ])

        with core_tab:
            render_core_decision(match, odds, api_football_data, result_distribution, decision, betting_opinion, actual_odds)
            render_storylines(match, betting_opinion, decision)

        with market_tab:
            market_results = [
                safe_render_market_section("胜平负赔率", render_match_winner, match, odds, api_football_data),
                safe_render_market_section("亚洲让球盘", render_handicap, match, api_football_data),
                safe_render_market_section("大小球盘口", render_totals, odds),
                safe_render_market_section("真实波胆盘口", render_correct_score_market, api_football_data),
                safe_render_market_section("Polymarket", render_polymarket, match, api_football_data, polymarket),
                safe_render_market_section("市场价值分析", render_value, value_analysis),
                safe_render_market_section("市场一致性分析", render_market_consistency, match, odds, polymarket),
            ]
            render_market_debug_summary(odds, api_football_data, polymarket, market_results)

        with source_tab:
            render_data_completeness(local_db)
            render_debug_panel(match, odds, api_football_data, polymarket, odds_date_key)
            render_detail_data_source(odds, polymarket, selected_fixture)
            render_technical_notes(odds, api_football_data)

        with post_tab:
            render_post_match_analysis_tab(match, selected_fixture, result_distribution, snapshot_strategies, my_portfolio)

        with team_tab:
            render_team_intelligence(match, selected_fixture, api_football_data)

        st.download_button(
            "下载 Markdown 报告",
            data=report,
            file_name=report_path.name,
            mime="text/markdown",
        )
    except Exception as error:
        st.error(str(error))


def render_post_match_page(fixture):
    fixture = refresh_selected_fixture_if_needed(fixture)
    if st.button("← 返回赛程", type="secondary"):
        st.session_state.page = "schedule"
        st.session_state.selected_match_text = None
        st.session_state.selected_fixture = None
        st.rerun()

    home = fixture.get("home_team", {})
    away = fixture.get("away_team", {})
    score = fixture.get("score") or {}

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

    try:
        match = parse_match(schedule_match_text(fixture))
        snapshot = load_match_snapshot(match, fixture) or {}
        distribution = snapshot.get("probability_distribution") or {"rows": []}
        strategies = (snapshot.get("strategy_snapshot") or {}).get("strategies") or []
        my_portfolio = load_my_portfolio(match, fixture) or snapshot.get("my_portfolio") or {}
        render_post_match_analysis_tab(match, fixture, distribution, strategies, my_portfolio)
    except Exception as error:
        st.warning(f"赛后策略核算暂不可用：{error}")


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
