from pathlib import Path
from datetime import datetime, timedelta
from html import escape
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
import yaml

from modules.match_parser import parse_match
from modules.market_utils import correct_score_summary, identify_handicap_center, identify_total_center
from modules.betting_opinion import build_betting_opinion
from modules.decision_engine import build_decision_engine
from modules.odds_client import fetch_match_data
from modules.market_data import build_market_data
from modules.polymarket_client import fetch_polymarket
from modules.pregame_content import (
    BANNER_IMAGE_URL,
    bet_cn,
    build_risk_notes,
    build_storylines,
    predicted_lineup_for,
    profile_for,
    static_recent_form_for,
    team_cn,
)
from modules.report_generator import build_report, save_report
from modules.result_distribution import build_result_distribution
from modules.schedule_client import (
    available_match_dates,
    default_date_key,
    fetch_world_cup_schedule,
    fixtures_for_date,
    fixture_local_datetime,
    group_by_match_date,
    is_finished,
    is_live,
    tournament_stats,
)
from modules.team_profile_client import fetch_team_profile
from modules.weather_client import weather_for_fixture
from modules.perf_logger import perf_timer
from modules.portfolio_engine import build_core_decision_layers


MODEL_VERSION_TRACKING = {
    "model_version": "v1.61",
    "probability_engine_version": "score_distribution_v1",
    "optimizer_version": "tpb_only_no_optimizer",
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
    fixture_id = fixture.get("fixture_id")
    return {
        "id": fixture_id,
        "home_team": fixture.get("home_team") or {},
        "away_team": fixture.get("away_team") or {},
        "raw": {
            "fixture": {
                "id": fixture_id,
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
    return bool(left_id and right_id and str(left_id) == str(right_id))


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
    schedule = fetch_world_cup_schedule(force_refresh=False)
    for candidate in schedule.get("fixtures", []):
        if same_fixture(fixture, candidate):
            st.session_state.selected_fixture = candidate
            return candidate
    return fixture


def remember_valid_fixture(fixture, reason=""):
    if not fixture or not fixture.get("fixture_id"):
        return fixture
    st.session_state.selected_fixture = fixture
    st.session_state.last_valid_fixture = fixture
    st.session_state.last_valid_fixture_id = fixture.get("fixture_id")
    if reason:
        print("[Fixture Guard]", reason, f"stored_fixture_id={fixture.get('fixture_id')}")
    return fixture


def normalized_match_text(value):
    return " ".join(str(value or "").lower().replace("&", " and ").replace(".", " ").split())


def fixture_matches_text(fixture, match_text):
    wanted = normalized_match_text(match_text)
    if not fixture or not wanted:
        return False
    candidate = normalized_match_text(schedule_match_text(fixture))
    return candidate == wanted


def fixture_by_id_or_match(fixtures, fixture_id=None, match_text=None):
    wanted_id = normalized_fixture_id(fixture_id)
    for fixture in fixtures or []:
        if wanted_id and normalized_fixture_id(fixture.get("fixture_id")) == wanted_id:
            return fixture
    for fixture in fixtures or []:
        if fixture_matches_text(fixture, match_text):
            return fixture
    return None


def resolve_fixture_fallback(match_text=None, selected_fixture=None):
    candidates = []
    if st.session_state.get("selected_fixture"):
        candidates.append(("session_selected_fixture", st.session_state.selected_fixture))
    if selected_fixture:
        candidates.append(("passed_selected_fixture", selected_fixture))

    for label, fixture in candidates:
        if fixture and fixture.get("fixture_id"):
            return remember_valid_fixture(fixture, f"fallback:{label}")

    schedule = fetch_world_cup_schedule(force_refresh=False)
    fixtures = schedule.get("fixtures") or []
    active_match_text = match_text or st.session_state.get("selected_match_text")
    resolved = fixture_by_id_or_match(fixtures, match_text=active_match_text)
    if resolved:
        return remember_valid_fixture(resolved, "fallback:schedule")

    last_valid = st.session_state.get("last_valid_fixture")
    if last_valid and last_valid.get("fixture_id"):
        return remember_valid_fixture(last_valid, "fallback:last_valid_fixture")

    resolved = fixture_by_id_or_match(fixtures, fixture_id=st.session_state.get("last_valid_fixture_id"))
    if resolved:
        return remember_valid_fixture(resolved, "fallback:last_valid_fixture_id")

    return None


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


def normalized_fixture_id(value):
    if value in (None, ""):
        return None
    return str(value)


def log_fixture_route(stage, ui_fixture_id, request_fixture_id):
    print(
        "[Fixture Guard]",
        stage,
        f"UI_fixture_id={ui_fixture_id or '-'}",
        f"request_fixture_id={request_fixture_id or '-'}",
    )


def enforce_ui_fixture_for_market_request(stage, selected_fixture, request_fixture_id=None):
    ui_fixture = resolve_fixture_fallback(st.session_state.get("selected_match_text"), selected_fixture)
    ui_fixture_id = normalized_fixture_id((ui_fixture or {}).get("fixture_id"))
    candidate_request_id = normalized_fixture_id(
        request_fixture_id if request_fixture_id is not None else (selected_fixture or {}).get("fixture_id")
    )
    log_fixture_route(stage, ui_fixture_id, candidate_request_id)

    if not ui_fixture_id:
        st.warning("暂时无法恢复当前比赛 fixture_id，请从赛程页重新选择比赛。")
        return None

    if candidate_request_id and candidate_request_id != ui_fixture_id:
        log_fixture_route(f"{stage}:mismatch_reset", ui_fixture_id, candidate_request_id)
        st.warning("检测到 fixture_id 短暂不一致，已自动恢复为当前界面比赛。")
        st.session_state.selected_fixture = ui_fixture
        return ui_fixture

    return ui_fixture


def render_debug_panel(match, odds, api_football_data, odds_date_key):
    fixture_result = (api_football_data or {}).get("fixture_result") or {}
    fixture = (api_football_data or {}).get("fixture") or {}
    home_team = fixture_result.get("home_team") or fixture.get("home_team") or {}
    away_team = fixture_result.get("away_team") or fixture.get("away_team") or {}
    handicap = (api_football_data or {}).get("asian_handicap") or {}
    correct_score = (api_football_data or {}).get("correct_score") or {}
    debug_rows = [
        {"项目": "Match", "状态": match.get("display_name"), "详情": f"{match.get('home_en')} vs {match.get('away_en')}"},
        {"项目": "Odds Date Key", "状态": odds_date_key or "-", "详情": "API-Football UTC比赛日"},
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
            "详情": "API-Football totals rows",
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


def render_market_debug_summary(odds, api_football_data, section_results):
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
    ]
    debug_rows.extend(
        {"项目": row["模块"], "状态": row["状态"], "详情": row["错误"] or "-"}
        for row in section_results
    )
    if st.checkbox("显示 Debug Summary", value=False, key="market_debug_summary"):
        st.dataframe(pd.DataFrame(debug_rows), use_container_width=True, hide_index=True)


def render_match_overview(match, api_football_data, selected_fixture=None, allow_live_weather=True):
    if selected_fixture:
        home = selected_fixture.get("home_team") or {"name": match["home_cn"]}
        away = selected_fixture.get("away_team") or {"name": match["away_cn"]}
        kickoff_text = fixture_time_text(selected_fixture)
        venue_name = selected_fixture.get("venue_name") or "球场待确认"
        city = selected_fixture.get("venue_city") or "城市待确认"
        weather = weather_for_fixture(selected_fixture) if allow_live_weather else {
            "summary": "天气暂不可用",
            "source": "Local cache",
        }
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
        weather = weather_for_fixture(fixture) if allow_live_weather else {
            "summary": "天气暂不可用",
            "source": "Local cache",
        }

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
    data_quality_label = {"High": "高", "Medium": "中等", "Low": "低"}.get(str(opinion.get("data_quality", "")), opinion.get("data_quality", "-"))
    with st.container(border=True):
        st.markdown('<div class="section-title">🎯 投注观点</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            soft_card("比赛主方向", bet_cn(opinion.get("match_direction") or opinion.get("match_winner", "暂无观点")))
        with col2:
            soft_card("覆盖 / 保险候选", bet_cn(opinion.get("coverage_candidate", "暂无候选")))
        with col3:
            soft_card("投注信心", f"{opinion.get('betting_confidence', opinion.get('confidence', 50))} / 100", f"数据质量：{data_quality_label}")
        tpb = opinion.get("true_probability_base") or {}
        tpb_probs = tpb.get("probabilities") or {}
        if tpb_probs:
            st.caption(
                "TPB："
                f"主胜 {percent(tpb_probs.get('home_win', 0))} · "
                f"平局 {percent(tpb_probs.get('draw', 0))} · "
                f"客胜 {percent(tpb_probs.get('away_win', 0))}"
            )
        confidence_breakdown = opinion.get("betting_confidence_breakdown") or {}
        if confidence_breakdown:
            entropy_value = confidence_breakdown.get("entropy")
            entropy_text = "-" if entropy_value is None else f"{entropy_value:.3f}"
            st.caption(
                f"信心公式：{confidence_breakdown.get('formula', '-')}；"
                f"TPB 熵值 {entropy_text}；隐藏扣分：无。"
            )

        blocks = [
            ("比赛主方向", opinion.get("match_winner_reason", "-")),
            ("让球盘口方向", f"{bet_cn(opinion.get('handicap_market_direction') or opinion.get('asian_handicap', '暂无观点'))}。{opinion.get('asian_handicap_reason', '')}"),
            ("覆盖 / 保险候选", f"{bet_cn(opinion.get('coverage_candidate', '暂无候选'))}。{opinion.get('coverage_reason', '')}"),
            ("进球数观点", f"总进球盘口中心：{opinion.get('total_center', '-')}。{opinion.get('goals_market_bias', '')}"),
            ("比赛投资价值", f"TPB 熵信心 {opinion.get('betting_confidence', '-')} / 100；市场方向：{opinion.get('market_direction_label', '-')}。"),
        ]
        for title, text in blocks:
            st.markdown(
                f'<div class="analysis-block"><div class="analysis-title">{title}</div>'
                f'<p class="analysis-text">{text}</p></div>',
                unsafe_allow_html=True,
            )

        notes = opinion.get("data_quality_notes") or []
        if notes:
            st.markdown("**数据质量提示**")
            for note in notes[:5]:
                st.caption(f"- {note}")


def neutral_news_context():
    return {
        "home": [],
        "away": [],
        "risk_flags": [],
        "news_score_adjustment": 0,
    }


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


def tpb_report_strategy(decision):
    stake = decision.get("recommended_stake") or {}
    score = decision.get("value_rating_score") or decision.get("final_confidence_score") or 0
    return {
        "code": "tpb_decision",
        "name": "TPB 单一决策",
        "rank_name": "TPB 单一决策",
        "score": score,
        "decision_score": score,
        "portfolio_style_label": "TPB确定性",
        "items": [],
        "risk_diagnostic": {
            "risk_level": "诊断",
            "reason": "风险不阻断 TPB 决策；推荐金额只由投资分决定。",
        },
        "rank1_eligibility": {
            "rank1_eligible": True,
            "eligible": True,
            "rank1_blockers": [],
            "summary": "TPB 决策无 legacy gate 阻断。",
        },
        "recommended_stake": stake,
    }


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


def render_ranking_score_notes(decision_layers):
    score_layer = (decision_layers or {}).get("score_layer") or {}
    execution_layer = (decision_layers or {}).get("execution_layer") or {}
    explanation_layer = (decision_layers or {}).get("explanation_layer") or {}
    stake = execution_layer.get("stake") or {}
    with st.expander("评分说明", expanded=False):
        rows = [
            {"项目": "TPB", "说明": "API-Football 胜平负赔率归一化后的唯一概率基础。"},
            {"项目": "投资分", "说明": f"{score_layer.get('investment_score', 0)} / 100；由 TPB 集中度、热门差值和平/冷概率派生。"},
            {"项目": "投注信心", "说明": f"{score_layer.get('betting_confidence', 0)} / 100；由 TPB 熵值派生，无首发/伤病扣分。"},
            {"项目": "推荐金额", "说明": f"{stake.get('amount', 0)} 元；只由投资分档位决定。"},
            {"项目": "覆盖定义", "说明": explanation_layer.get("coverage_explanation", "-")},
            {"项目": "风险解释", "说明": explanation_layer.get("risk_explanation", "-")},
            {"项目": "最大亏损", "说明": "主表不展示；诊断中 null=未计算，0=无仓位，正数=真实敞口。"},
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_match_decision_cards(decision_layers):
    score_layer = (decision_layers or {}).get("score_layer") or {}
    execution_layer = (decision_layers or {}).get("execution_layer") or {}
    explanation_layer = (decision_layers or {}).get("explanation_layer") or {}
    stake = execution_layer.get("stake") or {"amount": 0, "risk_mode": "-", "amount_rule": "-", "reason": "-"}
    cols = st.columns(2)
    with cols[0]:
        with st.container(border=True):
            st.markdown("**比赛投资分**")
            st.metric("比赛投资分", f"{score_layer.get('investment_score', 0)} / 100", execution_layer.get("risk_decision", "-"))
            st.caption("数据质量说明：" + score_layer.get("data_quality_note", "-"))
            components = explanation_layer.get("components") or {}
            if components:
                component_text = " · ".join(f"{key}: {value}" for key, value in components.items())
                st.caption(component_text)
    with cols[1]:
        with st.container(border=True):
            st.markdown("**推荐金额**")
            st.metric("推荐金额", f"{stake['amount']} 元", stake["risk_mode"])
            st.caption("金额规则：" + stake.get("amount_rule", "-"))
            st.caption("推荐原因：" + stake["reason"])


def render_portfolio_ranking(strategies, match, distribution, my_portfolio=None, data_context=None):
    with perf_timer("detail", "render_tpb_decision", {"mode": "tpb_only"}):
        st.markdown("**TPB 决策输出**")
        st.caption("旧组合排序、收益排序与剧本排序已退出决策链；本区只展示 TPB 模型层返回值。")
        decision_layers = build_core_decision_layers([], match, distribution, data_context)
        render_match_decision_cards(decision_layers)
        score_layer = decision_layers.get("score_layer") or {}
        execution_layer = decision_layers.get("execution_layer") or {}
        stake = execution_layer.get("stake") or {}
        tpb = score_layer.get("tpb") or {}
        probs = tpb.get("probabilities") or {}
        rows = [{
            "决策层": "TPB 单一决策",
            "主胜": percent(probs.get("home_win", 0)) if probs else "-",
            "平局": percent(probs.get("draw", 0)) if probs else "-",
            "客胜": percent(probs.get("away_win", 0)) if probs else "-",
            "投注信心": f"{score_layer.get('betting_confidence', 0)} / 100",
            "投资分": f"{score_layer.get('investment_score', 0)} / 100",
            "推荐金额": f"{stake.get('amount', 0)} 元",
            "执行判断": execution_layer.get("risk_decision", "-"),
        }]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        render_ranking_score_notes(decision_layers)


def odds_from_market_data(market_data):
    api_odds = (market_data or {}).get("api_football_odds") or {}
    one_x_two = dict(api_odds.get("one_x_two") or {})
    one_x_two["over_under"] = ((api_odds.get("over_under") or {}).get("rows") or [])
    one_x_two["over_under_line"] = (api_odds.get("over_under") or {}).get("line")
    return one_x_two


def api_markets_from_market_data(market_data):
    return (market_data or {}).get("api_football_odds") or {}


def path_layer_summary(match, market_data):
    api_markets = api_markets_from_market_data(market_data)
    odds = odds_from_market_data(market_data)
    handicap = identify_handicap_center(((api_markets.get("asian_handicap") or {}).get("rows") or []), odds=odds, match=match)
    totals = identify_total_center(((api_markets.get("over_under") or {}).get("rows") or []))
    correct = correct_score_summary(((api_markets.get("correct_score") or {}).get("rows") or []), limit=5)

    direction_path = handicap.get("center_label") or "暂无亚洲盘主线"
    if handicap.get("available"):
        line_strength = abs(float(handicap.get("center_line") or 0))
        confidence = min(100, 45 + line_strength * 15 + min(20, len(handicap.get("rows") or []) / 8))
        handicap_confidence = f"{round(confidence)} / 100"
        handicap_reason = f"主线 {direction_path}，来自 {len(handicap.get('rows') or [])} 条真实亚洲盘。"
    else:
        handicap_confidence = "0 / 100"
        handicap_reason = "未解析到真实亚洲让球盘。"

    if totals.get("available"):
        tempo_path = f"{totals.get('center_label')} 附近"
    else:
        tempo_path = "暂无大小球主线"

    score_path = " / ".join(item.get("score", "-") for item in (correct.get("hot") or [])[:3]) or "暂无波胆中心"
    return {
        "direction_path": direction_path,
        "tempo_path": tempo_path,
        "score_path": score_path,
        "handicap_confidence": handicap_confidence,
        "handicap_reason": handicap_reason,
    }


def render_path_layers(match, market_data):
    summary = path_layer_summary(match, market_data)
    st.markdown("**主路径结构**")
    cols = st.columns(4)
    cols[0].metric("主方向", summary["direction_path"])
    cols[1].metric("主节奏", summary["tempo_path"])
    cols[2].metric("主波胆", summary["score_path"])
    cols[3].metric("让球信心", summary["handicap_confidence"])
    st.caption(summary["handicap_reason"])


def render_market_consensus_panel(match, market_data):
    summary = path_layer_summary(match, market_data)
    with st.container(border=True):
        st.markdown("**Market Consensus**")
        cols = st.columns(3)
        cols[0].metric("主亚洲盘", summary["direction_path"])
        cols[1].metric("主大小球", summary["tempo_path"])
        cols[2].metric("主波胆路径", summary["score_path"])
        st.caption(summary["handicap_reason"])


def render_core_risk_summary(match, decision, distribution):
    with st.container(border=True):
        st.markdown('<div class="section-title">风险提示</div>', unsafe_allow_html=True)
        notes = build_risk_notes(match, decision)[:3]
        for note in notes:
            st.markdown(f'<div class="warning-item">{note}</div>', unsafe_allow_html=True)
        exposure = (distribution or {}).get("risk_exposure") or {}
        if exposure.get("lose_paths"):
            st.caption("重点风险路径：" + " / ".join(exposure.get("lose_paths", [])[:5]))
        if exposure.get("meaning"):
            st.caption(exposure.get("meaning"))


def render_core_decision(match, odds, api_football_data, distribution, decision, betting_opinion, actual_odds=None, selected_fixture=None, my_portfolio=None, polymarket=None):
    with st.container(border=True):
        st.markdown('<div class="section-title">核心决策</div>', unsafe_allow_html=True)
        render_betting_opinion(betting_opinion, odds, polymarket, match)
        render_portfolio_ranking(
            [],
            match,
            distribution,
            None,
            {
                "odds": odds,
                "api_football_data": api_football_data,
                "polymarket": polymarket,
            },
        )
        render_core_risk_summary(match, decision, distribution)
        st.caption("结果分布为观察层，不参与 TPB 投资分、推荐金额或排序。")
        render_result_distribution(distribution)

        st.caption("用户赔率、我的组合、收益对比和剧本组合排行不再参与决策输出。")

    return {
        "strategies": [],
        "top_strategy": {},
        "my_portfolio": my_portfolio or {},
        "actual_odds": {},
    }


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


def team_profile_metrics(profile):
    items = [
        ("FIFA排名", profile.get("fifa_rank")),
        ("ELO评分", profile.get("elo")),
        ("球队身价", profile.get("team_value")),
        ("平均年龄", profile.get("average_age")),
        ("主教练", profile.get("coach")),
        ("世界杯最佳", profile.get("best_world_cup")),
        ("参赛次数", profile.get("world_cup_appearances")),
    ]
    return [{"项目": label, "数据": str(value)} for label, value in items if value not in {None, "", "待接入"}]


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
        with col:
            with st.container(border=True):
                team_visual({"name": team_name, "logo": profile.get("logo") or team.get("logo")}, size=64)
                st.markdown(f"### {team_cn(team_name)}")
                st.markdown("**预计/官方首发阵容**")
                rows = lineup_rows_for_team(lineups, team_name)
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                else:
                    lineup = predicted_lineup_for(team_name)
                    if lineup:
                        st.caption("市场预测首发，非官方首发。")
                        st.write(f"阵型：{lineup.get('formation', '-')}")
                        st.write(f"门将：{', '.join(lineup.get('goalkeeper', []))}")
                        st.write(f"后卫：{', '.join(lineup.get('defenders', []))}")
                        st.write(f"中场：{', '.join(lineup.get('midfielders', []))}")
                        st.write(f"前锋：{', '.join(lineup.get('forwards', []))}")
                    else:
                        st.info("本场官方首发暂未公布。")

                injury_rows = injury_rows_for_team(injuries, team_name)
                st.markdown("**伤病与停赛**")
                if injury_rows:
                    st.dataframe(pd.DataFrame(injury_rows), use_container_width=True, hide_index=True)
                else:
                    st.info("暂无公开伤病或停赛信息。")

                lineup = predicted_lineup_for(team_name)
                key_players = (lineup or {}).get("key_players") or []
                if key_players:
                    st.markdown("**关键球员**")
                    st.caption("、".join(key_players))

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

                profile_rows = team_profile_metrics(profile)
                if profile_rows:
                    st.markdown("**球队资料**")
                    st.dataframe(pd.DataFrame(profile_rows), use_container_width=True, hide_index=True)


def render_match_winner(match, market_data):
    with st.container(border=True):
        st.markdown('<div class="section-title">胜平负赔率</div>', unsafe_allow_html=True)
        odds = odds_from_market_data(market_data)
        if not odds.get("found"):
            st.info("未找到盘口数据：API-Football 当前没有返回该比赛的胜平负市场。")
            return
        home_name = team_cn(match["home_cn"])
        away_name = team_cn(match["away_cn"])
        tpb = odds.get("true_probability_base") or {}
        implied = tpb.get("probabilities") or {}
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


def render_handicap(match, market_data):
    with st.container(border=True):
        st.markdown('<div class="section-title">亚洲让球盘</div>', unsafe_allow_html=True)
        handicap = (api_markets_from_market_data(market_data).get("asian_handicap") or {})
        if not handicap.get("found"):
            st.info(handicap.get("message", "未找到盘口数据：API-Football 当前没有返回该比赛的亚洲让球盘。"))
            return

        rows = handicap.get("rows") or []
        bookmakers = handicap.get("bookmakers") or []
        summary = identify_handicap_center(rows, odds=odds_from_market_data(market_data), match=match)
        st.success(handicap.get("message", "已获取真实亚洲让球盘。"))
        st.caption(
            f"数据来源：{handicap.get('source')} · "
            f"博彩公司：{', '.join(bookmakers[:6]) or '-'}"
        )
        if summary.get("available"):
            c1, c2, c3 = st.columns(3)
            c1.metric("盘口中心", summary.get("center_label"))
            c2.metric("市场均值", f"{summary.get('avg_odds'):.2f}" if summary.get("avg_odds") else "-")
            c3.metric("最佳赔率", f"{summary.get('best_odds'):.2f}" if summary.get("best_odds") else "-")
            st.caption("盘口中心公司：" + (", ".join(summary.get("bookmakers", [])[:6]) or "-"))
            if summary.get("coverage_label") not in (None, "No coverage candidate"):
                st.info(f"覆盖/保险候选：{summary.get('coverage_label')}。这不是主方向，只用于防守平局、低节奏或热门方不打穿。")
            if summary.get("secondary_handicap_label"):
                st.caption(f"盘口参考：{summary.get('secondary_handicap_label')}（仅展示，不参与 TPB 决策）。")
            trace = summary.get("coverage_trace") or {}
            if trace:
                st.caption(
                    "覆盖 trace："
                    f"raw {trace.get('raw_rows', 0)} → "
                    f"parsed {trace.get('parsed_rows', 0)} → "
                    f"filtered {trace.get('filtered_rows', 0)} → "
                    f"secondary_handicap {trace.get('secondary_handicap_rows', 0)} → "
                    f"relaxed_secondary {trace.get('relaxed_secondary_handicap_rows', 0)}；"
                    f"fallback：{trace.get('fallback_used', '-')}"
                )
            if summary.get("warning"):
                st.warning(summary.get("warning"))
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


def render_totals(market_data):
    with st.container(border=True):
        st.markdown('<div class="section-title">大小球盘口</div>', unsafe_allow_html=True)
        totals_data = api_markets_from_market_data(market_data).get("over_under") or {}
        markets = totals_data.get("rows") or []
        if not markets:
            st.info(totals_data.get("message") or "未找到盘口数据：API-Football 当前没有返回该比赛的大小球盘口。")
            return

        summary = identify_total_center(markets)
        selected = summary.get("rows") or []
        bookmakers = sorted({market.get("bookmaker") for market in selected if market.get("bookmaker")})
        best_over = max((market.get("over_odds") for market in selected if market.get("over_odds")), default=None)
        best_under = max((market.get("under_odds") for market in selected if market.get("under_odds")), default=None)
        avg_over = summary.get("avg_over") or 0
        avg_under = summary.get("avg_under") or 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("总进球中心", f"{summary.get('center_label', '-')} 球")
        col2.metric("市场均值", f"{avg_over:.2f} / {avg_under:.2f}")
        col3.metric("大球最佳赔率", fmt(best_over))
        col4.metric("小球最佳赔率", fmt(best_under))
        st.caption(f"数据来源：{totals_data.get('source') or 'API-Football / Goals Over/Under'}")
        st.caption("主要公司：" + (", ".join(bookmakers[:3]) if bookmakers else "-"))
        st.info(summary.get("market_bias", "大小球盘口中心暂不明确。"))
        st.caption(summary.get("recommended_interpretation", ""))

        if st.checkbox("展开全部赔率", value=False, key="market_all_totals"):
            st.dataframe(markets, use_container_width=True, hide_index=True)


def render_correct_score_market(market_data):
    correct_score = (api_markets_from_market_data(market_data).get("correct_score") or {})
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


def render_polymarket_comparison(market_data):
    reference = (market_data or {}).get("polymarket_reference") or {}
    metrics = (market_data or {}).get("comparison_metrics") or {}
    with st.container(border=True):
        st.markdown('<div class="section-title">Polymarket 概率对比</div>', unsafe_allow_html=True)
        if not reference.get("found"):
            st.info(reference.get("message") or "未找到对应 Polymarket 活跃市场。")
            st.caption("Polymarket 仅作为情绪/概率参考，不替代 API-Football 赔率。")
            return

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("主胜参考概率", percent(reference.get("win_probability_home") or 0))
        col2.metric("平局参考概率", percent(reference.get("win_probability_draw") or 0))
        col3.metric("客胜参考概率", percent(reference.get("win_probability_away") or 0))
        col4.metric("市场一致度", f"{metrics.get('market_agreement_score', '-')}/100")

        rows = []
        for row in metrics.get("rows") or []:
            rows.append({
                "方向": row.get("label"),
                "API-Football": percent(row.get("api_football_probability") or 0),
                "Polymarket": percent(row.get("polymarket_probability") or 0),
                "偏差": percent(row.get("deviation") or 0),
            })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        if reference.get("event_title"):
            st.caption(f"事件：{reference.get('event_title')}")
        st.caption("Polymarket 是只读对比层；推荐、赔率和盘口结构仍以 API-Football 为主。")


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


def render_post_match_analysis_tab(match, selected_fixture, distribution, strategies=None, my_portfolio=None):
    with st.container(border=True):
        st.markdown('<div class="section-title">Post Match Analysis</div>', unsafe_allow_html=True)
        if not selected_fixture or not is_finished(selected_fixture):
            st.info("比赛尚未结束。赛后总结将在最终比分返回后自动核算。")
            return

        final_score = final_score_from_fixture(selected_fixture)
        if not final_score:
            st.warning("比赛已结束，但当前赛程数据没有最终比分，暂无法核算盈亏。")
            return

        score_cols = st.columns(3)
        score_cols[0].metric("最终比分", final_score)
        score_cols[1].metric("数据来源", "API-Football")
        score_cols[2].metric("决策模型", "TPB-only")
        st.caption("赛后页仅展示比赛结果与观察层分布；旧组合结算、收益率审计和历史绩效写入已退出运行路径。")
        render_result_distribution(distribution)


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
            "赛程、比赛、赔率、伤病、首发来源：API-Football",
            "旧版外部数据源未参与当前页面数据流。",
        ]
        if not odds.get("found"):
            notes.append(f"赔率状态：{odds.get('message')}")
        if api_football_data.get("error"):
            notes.append(f"比赛数据状态：{api_football_data.get('error')}")
        for note in notes:
            st.caption(note)


def render_detail_data_source(odds=None, fixture=None):
    with st.container(border=True):
        st.markdown('<div class="section-title">数据来源</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        cols[0].metric("赛程 / 比分", (fixture or {}).get("source", "API-Football"))
        cols[1].metric("赔率", (odds or {}).get("source", "API-Football"))
        cols[2].metric("比赛 ID", str((fixture or {}).get("fixture_id") or "-"))
        st.caption("当前数据流只启用 API-Football；旧赛程源、二级市场源和本地历史库不作为页面数据源。")


def schedule_match_text(fixture):
    home = fixture.get("home_team", {}).get("name") or ""
    away = fixture.get("away_team", {}).get("name") or ""
    return f"{home} vs {away}"


def fixture_time_text(fixture, compact=False):
    kickoff = fixture_local_datetime(fixture)
    if not kickoff:
        return "时间待定"
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
    remember_valid_fixture(fixture, "open_fixture")
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
    st.write("这里聚合未来重点比赛的 API-Football 赛前市场分析入口。")
    render_popular_matches(fixtures, "market_popular")
    with st.container(border=True):
        st.markdown("**市场数据缓存**")
        st.write("API-Football 赛程、赔率与球队资料：会话缓存")
        st.write("旧版外部数据源：未启用")


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


def render_schedule_page():
    with perf_timer("home", "total"):
        if st.button("重新加载赛程", type="secondary"):
            fetch_world_cup_schedule.clear()
            st.session_state.force_schedule_refresh = True
            st.rerun()
        force_refresh = st.session_state.pop("force_schedule_refresh", False)
        with perf_timer("home", "fetch_schedule", {"force_refresh": force_refresh}):
            schedule = fetch_world_cup_schedule(force_refresh=force_refresh)
        fixtures = schedule.get("fixtures", [])

        with perf_timer("home", "banner"):
            render_portal_banner(fixtures)
        with perf_timer("home", "search"):
            render_search(fixtures)
        st.caption(
            f"赛程数据来源：{schedule.get('source')} · 更新时间：{schedule.get('updated_at', '-')}"
        )
        with perf_timer("home", "date_nav"):
            render_date_nav(fixtures)
        with perf_timer("home", "tournament_stats"):
            render_tournament_stats_center(fixtures, schedule)
        if st.checkbox("显示全部世界杯赛程", value=False, key="full_schedule_toggle"):
            with perf_timer("home", "full_schedule"):
                render_full_schedule(fixtures)


def render_analysis_page(match_text):
    if st.button("← 返回赛程", type="secondary"):
        st.session_state.page = "schedule"
        st.session_state.selected_match_text = None
        st.session_state.selected_fixture = None
        st.rerun()

    try:
        with perf_timer("detail", "pre_tab_total", {"match": match_text}):
            with perf_timer("detail", "parse_and_fixture"):
                match = parse_match(match_text)
                selected_fixture = refresh_selected_fixture_if_needed(st.session_state.get("selected_fixture"))
                if selected_fixture and is_finished(selected_fixture):
                    st.session_state.selected_fixture = selected_fixture
                    st.session_state.page = "post_match"
                    st.rerun()
                selected_fixture = enforce_ui_fixture_for_market_request("before_api_football_odds", selected_fixture)
                if not selected_fixture:
                    return
            with perf_timer("detail", "load_api_football_data"):
                api_football_data = fetch_match_data(match, "api_football_ssot_v1", selected_fixture)
                request_fixture_id = ((api_football_data or {}).get("fixture") or {}).get("id")
                selected_fixture = enforce_ui_fixture_for_market_request(
                    "after_api_football_odds",
                    selected_fixture,
                    request_fixture_id,
                )
                if not selected_fixture:
                    return
                if normalized_fixture_id(request_fixture_id) != normalized_fixture_id(selected_fixture.get("fixture_id")):
                    api_football_data = fetch_match_data(match, "api_football_ssot_v1", selected_fixture)
                odds_date_key = odds_date_key_from_fixture(selected_fixture, api_football_data)
                odds = (api_football_data or {}).get("odds") or {}
            with perf_timer("detail", "load_polymarket_reference"):
                selected_fixture = enforce_ui_fixture_for_market_request("before_polymarket", selected_fixture)
                if not selected_fixture:
                    return
                polymarket = fetch_polymarket(match, selected_fixture)
                selected_fixture = enforce_ui_fixture_for_market_request("before_market_data", selected_fixture)
                if not selected_fixture:
                    return
                market_data = build_market_data(odds, api_football_data, polymarket)
            with perf_timer("detail", "base_models"):
                news = neutral_news_context()
                betting_opinion = build_betting_opinion(match, odds, polymarket, None, api_football_data)
            with perf_timer("detail", "result_distribution"):
                result_distribution = build_result_distribution(match, odds, polymarket)
                betting_opinion["result_distribution"] = result_distribution
            with perf_timer("detail", "render_match_overview"):
                render_match_overview(match, api_football_data, selected_fixture, allow_live_weather=True)
            with perf_timer("detail", "decision_engine"):
                decision = build_decision_engine(
                    match,
                    odds,
                    polymarket,
                    api_football_data,
                    betting_opinion,
                    None,
                    result_distribution,
                )
            my_portfolio = {}
            with perf_timer("detail", "tpb_report_strategy"):
                top_strategy = tpb_report_strategy(decision)
            with perf_timer("detail", "report_generation"):
                report = build_report(
                    match,
                    odds,
                    polymarket,
                    news,
                    None,
                    None,
                    None,
                    api_football_data,
                    None,
                    betting_opinion,
                    top_strategy,
                    None,
                )
                report_path = save_report(report, match, config["report"]["output_dir"])

        core_tab, team_tab, market_tab, post_tab, source_tab = st.tabs([
            "核心决策",
            "球队信息",
            "市场盘口",
            "赛后总结",
            "数据来源",
        ])

        with core_tab:
            with perf_timer("detail", "tab_core_decision"):
                render_core_decision(
                    match,
                    odds,
                    api_football_data,
                    result_distribution,
                    decision,
                    betting_opinion,
                    None,
                    selected_fixture,
                    my_portfolio,
                    polymarket,
                )

        with team_tab:
            with perf_timer("detail", "tab_team_intelligence"):
                render_team_intelligence(match, selected_fixture, api_football_data)

        with market_tab:
            with perf_timer("detail", "tab_market"):
                render_market_consensus_panel(match, market_data)
                market_results = [
                    safe_render_market_section("胜平负赔率", render_match_winner, match, market_data),
                    safe_render_market_section("大小球盘口", render_totals, market_data),
                    safe_render_market_section("亚洲让球盘", render_handicap, match, market_data),
                    safe_render_market_section("真实波胆盘口", render_correct_score_market, market_data),
                    safe_render_market_section("Polymarket概率对比", render_polymarket_comparison, market_data),
                ]
                render_market_debug_summary(odds, api_football_data, market_results)

        with post_tab:
            with perf_timer("detail", "tab_post_match"):
                render_post_match_analysis_tab(match, selected_fixture, result_distribution, [], my_portfolio)

        with source_tab:
            with perf_timer("detail", "tab_source"):
                render_debug_panel(match, odds, api_football_data, odds_date_key)
                render_detail_data_source(odds, selected_fixture)
                render_technical_notes(odds, api_football_data)
                st.caption("高级收益 / 组合研究已退出 TPB 决策链；剧本系统仅作为观察层保留。")

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
        distribution = {"rows": []}
        strategies = []
        my_portfolio = {}
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
st.caption("用 API-Football 赛程、赔率和规则引擎识别淘汰赛机会与风险。")

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
