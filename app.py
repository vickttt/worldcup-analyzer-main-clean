from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
import yaml

from modules.match_parser import parse_match
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
from modules.score_model import recommend_scores
from modules.the_odds_client import fetch_odds
from modules.value_model import analyze_value


def percent(value):
    return f"{value * 100:.1f}%"


def fmt(value):
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:g}"
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


def official_name(match_name, fallback):
    return team_cn(match_name or fallback)


def render_match_overview(match, api_football_data):
    fixture = api_football_data.get("fixture")
    if not fixture:
        st.markdown(
            """
            <div class="hero-banner">
                <div class="hero-kicker">2026 FIFA World Cup · Kansas City</div>
                <div class="hero-match">阿根廷 vs 阿尔及利亚</div>
                <div class="hero-meta">
                    <span class="hero-chip">小组赛第 1 轮</span>
                    <span class="hero-chip">2026-06-17 09:00 CST</span>
                    <span class="hero-chip">Arrowhead Stadium</span>
                    <span class="hero-chip">Kansas City</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    raw = fixture.get("raw", {})
    fixture_info = raw.get("fixture", {})
    league = raw.get("league", {})
    venue = fixture_info.get("venue", {}) or {}
    home = fixture["home_team"]
    away = fixture["away_team"]
    kickoff_date, kickoff_time = parse_kickoff(fixture_info.get("date"))

    home_name = home.get("name") or match["home_cn"]
    away_name = away.get("name") or match["away_cn"]
    stage = league.get("round", "Group Stage - 1").replace("Group Stage", "小组赛第").replace(" - ", " ")
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-kicker">2026 FIFA World Cup · Kansas City</div>
            <div class="hero-match">{team_cn(home_name)} vs {team_cn(away_name)}</div>
            <div class="hero-meta">
                <span class="hero-chip">{stage}</span>
                <span class="hero-chip">{kickoff_date} {kickoff_time}</span>
                <span class="hero-chip">{venue.get("name") or "Arrowhead Stadium"}</span>
                <span class="hero-chip">{venue.get("city") or "Kansas City"}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_betting_opinion(opinion, odds=None, polymarket=None):
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

        blocks = [
            (
                "胜平负观点",
                f"市场普遍认为阿根廷具备明显优势。Odds API 隐含概率约为 {odds_home}，"
                f"Polymarket 概率约为 {poly_home}。两者差异约 {value_gap}，当前未发现明显市场错价。"
            ),
            (
                "亚洲让球观点",
                "主流盘口集中在阿根廷让球方向，但受让方赔率并未明显走弱。"
                "这说明市场认可阿根廷取胜概率较高，但对其赢两球以上并没有形成强共识。"
            ),
            (
                "大小球观点",
                "主流盘口集中在 2.5 球附近，大球与小球赔率接近。"
                "市场对总进球数暂未形成一致方向，当前更适合观察临场变化。"
            ),
        ]
        for title, text in blocks:
            st.markdown(
                f'<div class="analysis-block"><div class="analysis-title">{title}</div>'
                f'<p class="analysis-text">{text}</p></div>',
                unsafe_allow_html=True,
            )


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

        support_cols = st.columns(4)
        with support_cols[0]:
            render_score_card("近期状态", decision["recent_form"]["score"], "框架分", decision["recent_form"]["reason"])
        with support_cols[1]:
            render_score_card("ELO评分", decision["elo_rating"]["score"], "待接入", decision["elo_rating"]["reason"])
        with support_cols[2]:
            render_score_card("伤病影响", decision["injury_impact"]["score"], "框架分", decision["injury_impact"]["reason"])
        with support_cols[3]:
            render_score_card("球队身价", decision["team_value"]["score"], "待接入", decision["team_value"]["reason"])

        with st.expander("推荐理由"):
            for reason in decision["final_recommendation"]["reason"]:
                st.markdown(f"- {reason}")
            st.caption(
                "权重："
                + "，".join(f"{name} {weight}" for name, weight in decision["weights"].items())
            )


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
    }


def summarize_static_form(rows, count):
    selected = rows[:count]
    return {
        "form": [row["result"] for row in selected],
        "gf": sum(row["gf"] for row in selected),
        "ga": sum(row["ga"] for row in selected),
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
                        f'<div class="form-strip">{" ".join(summary["last5"]["form"])}</div>',
                        unsafe_allow_html=True,
                    )
                    w_col, gf_col, ga_col = st.columns(3)
                    w_col.metric("最近5场", "".join(summary["last5"]["form"]))
                    gf_col.metric("进球", summary["last5"]["gf"])
                    ga_col.metric("失球", summary["last5"]["ga"])
                    t1, t2, t3 = st.columns(3)
                    t1.metric("最近10场", "".join(summary["last10"]["form"]))
                    t2.metric("总进球", summary["last10"]["gf"])
                    t3.metric("总失球", summary["last10"]["ga"])
                    st.caption(f"数据来源：{summary['source']}")
                else:
                    st.info("近期战绩样本不足")


def render_match_winner(match, odds, api_football_data):
    with st.container(border=True):
        st.markdown('<div class="section-title">胜平负赔率</div>', unsafe_allow_html=True)
        if not odds.get("found"):
            st.info("The Odds API 暂未返回胜平负赔率")
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


def render_handicap(match, odds):
    with st.container(border=True):
        st.markdown('<div class="section-title">亚洲让球盘</div>', unsafe_allow_html=True)
        markets = odds.get("asian_handicap") or []
        if not markets:
            st.info("The Odds API 暂未返回亚洲让球盘")
            return

        main_line, selected = consensus_market(markets)
        bookmakers = sorted({market.get("bookmaker") for market in selected if market.get("bookmaker")})
        best_home = max((market.get("home_odds") for market in selected if market.get("home_odds")), default=None)
        best_away = max((market.get("away_odds") for market in selected if market.get("away_odds")), default=None)

        col1, col2, col3 = st.columns(3)
        col1.metric("主盘口", format_team_line(match["home_cn"], main_line))
        col2.metric("主队最佳赔率", fmt(best_home))
        col3.metric("客队最佳赔率", fmt(best_away))
        st.caption("主要公司：" + (", ".join(bookmakers[:3]) if bookmakers else "-"))

        with st.expander("查看全部让球盘口"):
            st.dataframe(markets, use_container_width=True, hide_index=True)


def render_totals(odds):
    with st.container(border=True):
        st.markdown('<div class="section-title">大小球盘口</div>', unsafe_allow_html=True)
        markets = odds.get("over_under") or []
        if not markets:
            st.info("The Odds API 暂未返回大小球盘口")
            return

        main_line, selected = consensus_market(markets)
        bookmakers = sorted({market.get("bookmaker") for market in selected if market.get("bookmaker")})
        best_over = max((market.get("over_odds") for market in selected if market.get("over_odds")), default=None)
        best_under = max((market.get("under_odds") for market in selected if market.get("under_odds")), default=None)

        col1, col2, col3 = st.columns(3)
        col1.metric("主流总进球", f"{fmt(main_line)} 球")
        col2.metric("大球最佳赔率", fmt(best_over))
        col3.metric("小球最佳赔率", fmt(best_under))
        st.caption("主要公司：" + (", ".join(bookmakers[:3]) if bookmakers else "-"))

        with st.expander("查看全部大小球盘口"):
            st.dataframe(markets, use_container_width=True, hide_index=True)


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


def render_team_profiles(match, api_football_data):
    fixture = api_football_data.get("fixture") or {}
    teams = [
        fixture.get("home_team", {}).get("name") or match["home_cn"],
        fixture.get("away_team", {}).get("name") or match["away_cn"],
    ]
    with st.container(border=True):
        st.markdown('<div class="section-title">球队概览</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for col, team_name in zip(cols, teams):
            profile = profile_for(team_name)
            with col:
                st.markdown(f"**{team_cn(team_name)}**")
                m1, m2, m3 = st.columns(3)
                m1.metric("FIFA排名", profile["fifa_rank"])
                m2.metric("ELO评分", profile["elo"])
                m3.metric("球队身价", profile["team_value"])
                m4, m5, m6 = st.columns(3)
                m4.metric("平均年龄", profile["average_age"])
                m5.metric("主教练", profile["coach"])
                m6.metric("世界杯最佳", profile["best_world_cup"])


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


def render_injuries_lineups(api_football_data):
    with st.container(border=True):
        st.markdown('<div class="section-title">伤病与首发</div>', unsafe_allow_html=True)
        injuries = api_football_data.get("injuries") or []
        lineups = api_football_data.get("lineups") or []
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**伤病信息**")
            if injuries:
                st.dataframe(injuries, use_container_width=True, hide_index=True)
            else:
                st.info("暂无公开伤病信息")
        with col2:
            st.markdown("**官方首发**")
            if lineups:
                st.dataframe(lineups, use_container_width=True, hide_index=True)
            else:
                st.info("官方首发尚未公布")

        fixture = api_football_data.get("fixture") or {}
        home_name = fixture.get("home_team", {}).get("name")
        away_name = fixture.get("away_team", {}).get("name")
        if home_name and away_name:
            st.divider()
            st.markdown("**市场预测首发**")
            pred_left, pred_right = st.columns(2)
            with pred_left:
                render_predicted_lineup_for_team(home_name)
            with pred_right:
                render_predicted_lineup_for_team(away_name)


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


def load_config():
    path = Path(__file__).resolve().parent / "config.yaml"
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


config = load_config()

st.set_page_config(page_title=config["app"]["title"], layout="wide")
card_css()
st.title("世界杯赛前分析平台")
st.caption("用赔率、预测市场和规则引擎识别市场可能错在哪里。")

match_text = st.text_input("请输入比赛名称", value="Argentina vs Algeria")

if st.button("生成赛前分析", type="primary"):
    try:
        match = parse_match(match_text)
        api_football_data = fetch_match_data(match)
        odds = fetch_odds(match)
        polymarket = fetch_polymarket(match)
        news = get_mock_news_and_injuries(match)
        probabilities = combine_probabilities(odds, polymarket, news, config)
        scores = recommend_scores(match, probabilities, odds)
        rating = rate_opportunity(probabilities, polymarket, news, odds)
        value_analysis = analyze_value(match, odds, polymarket)
        betting_opinion = build_betting_opinion(match, odds, polymarket, value_analysis)
        decision = build_decision_engine(
            match,
            odds,
            polymarket,
            api_football_data,
            betting_opinion,
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

        render_match_overview(match, api_football_data)

        core_tab, market_tab, team_tab, risk_tab = st.tabs([
            "核心决策",
            "市场盘口",
            "球队信息",
            "风险与说明",
        ])

        with core_tab:
            render_betting_opinion(betting_opinion, odds, polymarket)
            render_decision_engine(decision)
            render_storylines(match, betting_opinion, decision)

        with market_tab:
            render_match_winner(match, odds, api_football_data)
            render_handicap(match, odds)
            render_totals(odds)
            render_polymarket(match, api_football_data, polymarket)
            render_value(value_analysis)

        with team_tab:
            render_team_profiles(match, api_football_data)
            render_recent_form(api_football_data)
            render_injuries_lineups(api_football_data)

        with risk_tab:
            render_risk_notes(match, decision)
            render_technical_notes(odds, api_football_data)

        st.download_button(
            "下载 Markdown 报告",
            data=report,
            file_name=report_path.name,
            mime="text/markdown",
        )
    except Exception as error:
        st.error(str(error))
