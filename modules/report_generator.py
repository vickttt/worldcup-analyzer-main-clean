from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from modules.market_utils import identify_handicap_center, identify_total_center, parse_handicap_value, safe_float
from modules.pregame_content import static_recent_form_for, team_cn
from modules.probability_base import true_probability_base


def percent(value):
    return f"{value * 100:.1f}%"


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


def format_value(value):
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _match_team_label(match, side):
    if not match:
        return side.title()
    key = "home_cn" if side == "home" else "away_cn"
    fallback = "home_en" if side == "home" else "away_en"
    return team_cn(match.get(key) or match.get(fallback) or side.title())


def format_handicap_label(value, match=None):
    parsed = parse_handicap_value(value)
    if not parsed:
        return format_value(value)
    return f"{_match_team_label(match, parsed['side'])} {parsed['line']:+g}"


def _dedupe_markets(rows, key_fn, limit):
    seen = set()
    selected = []
    for row in rows or []:
        key = key_fn(row)
        if key in seen:
            continue
        seen.add(key)
        selected.append(row)
        if len(selected) >= limit:
            break
    return selected


def _portfolio_item_name(item, match=None):
    name = item.get("name") or item.get("selection") or "-"
    if item.get("type") == "handicap":
        return format_handicap_label(item.get("selection") or name, match)
    if item.get("type") == "winner":
        selection = item.get("selection") or str(name).replace("独赢", "").strip()
        return f"{team_cn(selection)}独赢"
    return str(name).replace("Home ", f"{_match_team_label(match, 'home')} ").replace(
        "Away ", f"{_match_team_label(match, 'away')} "
    )


def _portfolio_display_name(portfolio_summary, match=None):
    items = (portfolio_summary or {}).get("items") or []
    base = (
        portfolio_summary.get("rank_name")
        or portfolio_summary.get("portfolio_style_label")
        or portfolio_summary.get("name")
        or "-"
    )
    if items and (str(base).strip() == "推荐组合" or "Home " in str(base) or "Away " in str(base)):
        return " + ".join(_portfolio_item_name(item, match) for item in items[:4])
    return str(base)


def quality_cn(value):
    return {
        "High": "高",
        "Medium": "中等",
        "Low": "低",
    }.get(str(value or ""), str(value or "-"))


def format_kickoff(value):
    if not value:
        return "-"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    local_time = parsed.astimezone(ZoneInfo("Asia/Shanghai"))
    return local_time.strftime("%Y-%m-%d %H:%M CST")


def summarize_form(fixtures, team_id):
    results = []
    goals_for = 0
    goals_against = 0

    for item in (fixtures or [])[:5]:
        teams = item.get("teams", {})
        goals = item.get("goals", {})
        home = teams.get("home", {})
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


def summarize_static_form(rows, count=5):
    selected = (rows or [])[:count]
    form = [row.get("result") for row in selected if row.get("result")]
    gf = sum(row.get("gf", 0) for row in selected)
    ga = sum(row.get("ga", 0) for row in selected)
    return {
        "form": form,
        "gf": gf,
        "ga": ga,
    }


def _first_text(*values):
    for value in values:
        if value not in (None, "", "-"):
            return value
    return None


def fixture_metadata(api_football_data, match=None):
    fixture = (api_football_data or {}).get("fixture")
    fixture_result = (api_football_data or {}).get("fixture_result") or {}
    fixture = fixture or {}
    schedule_fixture = (api_football_data or {}).get("schedule_fixture") or fixture.get("schedule_fixture") or {}
    raw = fixture.get("raw", {}) or fixture_result.get("raw", {}) or {}
    fixture_info = raw.get("fixture", {})
    league = raw.get("league", {})
    venue = fixture_info.get("venue", {}) or {}
    home_name = _first_text(
        (fixture.get("home_team") or {}).get("name"),
        (fixture_result.get("home_team") or {}).get("name"),
        ((raw.get("teams") or {}).get("home") or {}).get("name"),
        (match or {}).get("home_cn"),
        (match or {}).get("home_en"),
        (match or {}).get("home"),
    )
    away_name = _first_text(
        (fixture.get("away_team") or {}).get("name"),
        (fixture_result.get("away_team") or {}).get("name"),
        ((raw.get("teams") or {}).get("away") or {}).get("name"),
        (match or {}).get("away_cn"),
        (match or {}).get("away_en"),
        (match or {}).get("away"),
    )
    competition = _first_text(
        " ".join(str(part) for part in [league.get("name"), league.get("season")] if part),
        " ".join(str(part) for part in [fixture.get("league"), fixture.get("season")] if part),
        schedule_fixture.get("league_name"),
    )
    stage = _first_text(
        league.get("round"),
        fixture.get("round"),
        schedule_fixture.get("round"),
        schedule_fixture.get("group"),
    )
    kickoff = _first_text(
        fixture_info.get("date"),
        fixture.get("kickoff_utc"),
        schedule_fixture.get("kickoff_utc"),
        schedule_fixture.get("kickoff_display"),
    )
    venue_name = _first_text(
        venue.get("name"),
        fixture.get("venue"),
        schedule_fixture.get("venue_name"),
    )
    venue_city = _first_text(
        venue.get("city"),
        fixture.get("city"),
        schedule_fixture.get("venue_city"),
    )
    missing = []
    for key, label in [
        (competition, "赛事"),
        (stage, "阶段"),
        (kickoff, "开球时间"),
        (venue_name, "场地"),
        (venue_city, "城市"),
    ]:
        if not key:
            missing.append(label)
    return {
        "home_name": team_cn(home_name),
        "away_name": team_cn(away_name),
        "competition": competition,
        "stage": stage,
        "kickoff": kickoff,
        "venue_name": venue_name,
        "venue_city": venue_city,
        "missing": missing,
    }


def format_fixture_lines(api_football_data, match=None):
    if not api_football_data and not match:
        return [
            "## 比赛概览",
            "",
            "缺少 fixture metadata。",
        ]

    meta = fixture_metadata(api_football_data, match)
    venue_text = "，".join(part for part in [meta.get("venue_name"), meta.get("venue_city")] if part)

    return [
        "## 比赛概览",
        "",
        f"### {format_value(meta.get('home_name'))} vs {format_value(meta.get('away_name'))}",
        "",
        f"- 赛事：{meta.get('competition') or '缺少 fixture metadata'}",
        f"- 阶段：{format_value(meta.get('stage')) if meta.get('stage') else '缺少 fixture metadata'}",
        f"- 开球时间：{format_kickoff(meta.get('kickoff')) if meta.get('kickoff') else '缺少 fixture metadata'}",
        f"- 场地：{venue_text or '缺少 fixture metadata'}",
    ]


def format_match_winner_lines(odds):
    if not odds.get("found", True):
        return [
            "## 胜平负 / Match Winner",
            "",
            f"- 状态：{odds.get('message')}",
        ]

    tpb = true_probability_base(odds)
    implied = tpb.get("probabilities") or {}
    return [
        "## 胜平负 / Match Winner",
        "",
        f"- 主胜：{format_value(odds['home_win'])}",
        f"- 平局：{format_value(odds['draw'])}",
        f"- 客胜：{format_value(odds['away_win'])}",
        f"- 主胜 TPB 概率：{percent(implied.get('home_win', 0))}",
        f"- 平局 TPB 概率：{percent(implied.get('draw', 0))}",
        f"- 客胜 TPB 概率：{percent(implied.get('away_win', 0))}",
    ]


def format_injuries_lines(api_football_data):
    injuries = (api_football_data or {}).get("injuries")
    error = (api_football_data or {}).get("injuries_error")
    lines = ["## 伤病信息", ""]

    if error:
        return lines + [f"- 状态：{error}"]

    if not injuries:
        return lines + ["暂无公开伤病信息"]

    for item in injuries:
        team = item.get("team", {}).get("name")
        player = item.get("player", {}).get("name")
        reason = item.get("player", {}).get("reason")
        injury_type = item.get("player", {}).get("type")
        lines.append(
            f"- {format_value(team)} / {format_value(player)} / "
            f"{format_value(injury_type)} / {format_value(reason)}"
        )

    return lines


def format_lineups_lines(api_football_data):
    lineups = (api_football_data or {}).get("lineups")
    error = (api_football_data or {}).get("lineups_error")
    lines = ["## 首发阵容", ""]

    if error:
        return lines + [f"- 状态：{error}"]

    if not lineups:
        return lines + ["官方首发尚未公布"]

    for lineup in lineups:
        team = lineup.get("team", {}).get("name")
        formation = lineup.get("formation")
        start_players = lineup.get("startXI", [])
        names = [
            item.get("player", {}).get("name")
            for item in start_players
            if item.get("player", {}).get("name")
        ]
        lines.append(f"- {format_value(team)} 阵型：{format_value(formation)}")
        lines.append(f"  首发：{', '.join(names) if names else '无'}")

    return lines


def format_asian_handicap_lines(api_football_data, odds=None, match=None):
    lines = ["## 亚洲让球 / Asian Handicap", ""]
    handicap = (api_football_data or {}).get("asian_handicap") or {}
    markets = handicap.get("rows") or []
    if not markets:
        return lines + [handicap.get("message", "API-Football did not return this market")]

    center = identify_handicap_center(markets, odds=odds, match=match)
    if center.get("available"):
        lines.extend([
            f"让球盘口中心：{center.get('center_label')}",
            f"覆盖 / 保险候选：{center.get('coverage_label')}",
        ])
        if center.get("warning"):
            lines.append(f"数据提示：已过滤 {center.get('outlier_count')} 条可能异常盘口。")
        lines.append("")

    lines.append(f"数据来源：{handicap.get('source', 'API-Football / Asian Handicap')}")
    lines.append("")

    nearby = []
    center_rows = center.get("rows") or []
    nearby.extend(center_rows)
    coverage_side = center.get("coverage_side")
    coverage_line = center.get("coverage_line")
    if coverage_side and coverage_line is not None:
        for market in markets:
            parsed = parse_handicap_value(market.get("value"))
            if parsed and parsed["side"] == coverage_side and abs(parsed["line"] - coverage_line) < 0.001:
                nearby.append(market)
    if not nearby:
        nearby = markets
    nearby = _dedupe_markets(
        nearby,
        lambda row: (format_handicap_label(row.get("value"), match), row.get("bookmaker")),
        5,
    )

    lines.extend(["### 主流盘口附近", ""])
    for market in nearby:
        lines.extend([
            f"- 盘口：{format_handicap_label(market.get('value'), match)}",
            f"  赔率：{format_value(market.get('odd'))}",
            f"  公司：{format_value(market.get('bookmaker'))}",
        ])
    lines.extend([
        "",
        "<details>",
        "<summary>完整亚洲让球明细</summary>",
        "",
    ])
    for market in markets:
        lines.extend([
            f"- 盘口：{format_handicap_label(market.get('value'), match)}",
            f"  赔率：{format_value(market.get('odd'))}",
            f"  公司：{format_value(market.get('bookmaker'))}",
        ])
    lines.extend(["", "</details>"])
    return lines


def format_correct_score_lines(api_football_data):
    lines = ["## 波胆 / Correct Score", ""]
    correct_score = (api_football_data or {}).get("correct_score") or {}
    markets = correct_score.get("rows") or []
    if not markets:
        return lines + [correct_score.get("message", "API-Football did not return this market")]

    lines.append(f"数据来源：{correct_score.get('source', 'API-Football / Exact Score')}")
    lines.append("")
    for market in markets[:40]:
        lines.extend([
            f"- 比分：{format_value(market.get('score'))}",
            f"  赔率：{format_value(market.get('odd'))}",
            f"  公司：{format_value(market.get('bookmaker'))}",
        ])
    return lines


def format_over_under_lines(odds):
    lines = ["## 大小球 / Over/Under", ""]
    markets = odds.get("over_under") if odds else None
    if not markets:
        return lines + ["API-Football 未返回该盘口。"]

    center = identify_total_center(markets)
    if center.get("available"):
        lines.extend([
            f"总进球盘口中心：{center.get('center_label')}",
            f"市场倾向：{center.get('market_bias')}",
            f"解释：{center.get('recommended_interpretation')}",
            "",
        ])

    center_line = safe_float(center.get("center_line") if center else None)
    nearby = []
    if center_line is not None:
        nearby = [
            market for market in markets
            if safe_float(market.get("line")) is not None
            and abs(safe_float(market.get("line")) - center_line) <= 0.5
        ]
    if not nearby:
        nearby = markets
    nearby = _dedupe_markets(
        sorted(
            nearby,
            key=lambda market: (
                abs((safe_float(market.get("line")) or center_line or 0) - (center_line or 0)),
                str(market.get("bookmaker") or ""),
            ),
        ),
        lambda row: (row.get("line"), row.get("bookmaker")),
        5,
    )

    lines.extend(["### 主流盘口附近", ""])
    for market in nearby:
        lines.extend([
            f"- 盘口：{format_value(market.get('line'))} 球",
            f"  大球赔率：{format_value(market.get('over_odds'))}",
            f"  小球赔率：{format_value(market.get('under_odds'))}",
            f"  公司：{format_value(market.get('bookmaker'))}",
        ])
    lines.extend([
        "",
        "<details>",
        "<summary>完整大小球明细</summary>",
        "",
    ])
    for market in markets:
        lines.extend([
            f"- 盘口：{format_value(market.get('line'))} 球",
            f"  大球赔率：{format_value(market.get('over_odds'))}",
            f"  小球赔率：{format_value(market.get('under_odds'))}",
            f"  公司：{format_value(market.get('bookmaker'))}",
        ])
    lines.extend(["", "</details>"])
    return lines


def format_betting_opinion_lines(betting_opinion):
    opinion = betting_opinion or {}
    lines = [
        "## 投注观点",
        "",
        "### 比赛主方向",
        "",
        opinion.get("match_direction") or opinion.get("match_winner", "No view"),
        "",
        "理由：",
        opinion.get("match_winner_reason", "-"),
        "",
        "### 让球盘口方向",
        "",
        opinion.get("handicap_market_direction") or opinion.get("asian_handicap", "No view"),
        "",
        "理由：",
        opinion.get("asian_handicap_reason", "-"),
        "",
        "### 覆盖 / 保险候选",
        "",
        opinion.get("coverage_candidate", "No coverage candidate"),
        "",
        "理由：",
        opinion.get("coverage_reason", "-"),
        "",
        "建议用途：",
        opinion.get("recommended_use", "-"),
        "",
        "### 进球数观点",
        "",
        f"总进球盘口中心：{opinion.get('total_center', '-')}",
        "",
        f"市场倾向：{opinion.get('goals_market_bias', opinion.get('over_under_reason', '-'))}",
        "",
        f"比赛行为提示：{opinion.get('goals_game_behavior_note', '-')}",
        "",
        f"解释：{opinion.get('goals_recommended_interpretation', '-')}",
        "",
        "### 比赛投资价值",
        "",
        f"市场方向：{opinion.get('market_direction_label', '-')}",
        "",
        f"TPB 熵信心：{opinion.get('betting_confidence', opinion.get('confidence', 50))} / 100",
        "",
        f"数据质量：{quality_cn(opinion.get('data_quality'))}",
    ]
    return lines


def format_data_quality_lines(betting_opinion, api_football_data=None, match=None, actual_odds=None):
    notes = list((betting_opinion or {}).get("data_quality_notes") or [])
    if not ((api_football_data or {}).get("lineups")) and "Official lineups not released." not in notes:
        if "官方首发尚未公布。" not in notes:
            notes.append("官方首发尚未公布。")
    missing = fixture_metadata(api_football_data, match).get("missing") if (api_football_data or match) else []
    if missing:
        notes.append("缺少 fixture metadata：" + "、".join(missing) + "。")
    if not notes:
        return []
    lines = ["## 数据质量提示", ""]
    for note in notes:
        lines.append(f"- {note}")
    return lines


def _portfolio_blockers(eligibility):
    return (eligibility or {}).get("blockers") or (eligibility or {}).get("rank1_blockers") or []


def _portfolio_pass_reasons(portfolio_summary):
    reasons = []
    risk_diagnostic = portfolio_summary.get("risk_diagnostic") or {}
    if risk_diagnostic:
        reasons.append(risk_diagnostic.get("reason") or "TPB 风险诊断不阻断推荐")
    return reasons or ["TPB 决策输出可作为当前报告的唯一推荐来源。"]


def format_portfolio_eligibility_lines(portfolio_summary=None, match=None):
    if not portfolio_summary:
        return [
            "## TPB 推荐资格",
            "",
            "- TPB 推荐：未生成",
            "- TPB 风险诊断：无法获取，报告生成时未收到 TPB 输出。",
            "- 第一推荐资格：无法获取",
    ]
    eligibility = portfolio_summary.get("rank1_eligibility") or {}
    risk_diagnostic = portfolio_summary.get("risk_diagnostic") or {}
    blockers = _portfolio_blockers(eligibility)
    eligible = eligibility.get("rank1_eligible")
    if eligible is None:
        eligible = eligibility.get("eligible")
    items = portfolio_summary.get("items") or []
    lines = [
        "## TPB 推荐资格",
        "",
        f"- TPB 推荐名称：{_portfolio_display_name(portfolio_summary, match)}",
        f"- TPB 决策分：{format_value(portfolio_summary.get('decision_score') or portfolio_summary.get('score'))}",
        f"- 组合风格：{portfolio_summary.get('portfolio_style_label') or (portfolio_summary.get('portfolio_style') or {}).get('style_cn') or '-'}",
        f"- TPB 风险诊断：{risk_diagnostic.get('risk_level') or '-'}",
        f"- 第一推荐资格：{'YES' if eligible else 'NO'}",
    ]
    if items:
        lines.extend(["", "核心投注："])
        for item in items[:6]:
            amount = item.get("amount")
            odds = item.get("actual_odds") or item.get("effective_odds") or item.get("standard_odds")
            suffix = []
            if amount is not None:
                suffix.append(f"{format_value(amount)}元")
            if odds is not None:
                suffix.append(f"赔率 {format_value(odds)}")
            lines.append(f"- {_portfolio_item_name(item, match)}" + (f"（{'，'.join(suffix)}）" if suffix else ""))
    lines.extend(["", "通过原因：" if eligible else "阻碍因素："])
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        for reason in _portfolio_pass_reasons(portfolio_summary):
            lines.append(f"- {reason}")
    return lines


def format_recent_form_lines(api_football_data):
    data = api_football_data or {}
    fixture_result = data.get("fixture_result") or {}
    fixture = data.get("fixture") or {}
    teams = [
        (
            fixture_result.get("home_team") or fixture.get("home_team") or {},
            data.get("home_recent") or [],
        ),
        (
            fixture_result.get("away_team") or fixture.get("away_team") or {},
            data.get("away_recent") or [],
        ),
    ]

    lines = ["## 近期状态", ""]
    has_team = False
    for team, fixtures in teams:
        team_name = team.get("name")
        team_id = team.get("id")
        if not team_name or not team_id:
            continue
        has_team = True
        summary = summarize_form(fixtures, team_id)
        source = "API-Football"
        if not summary["form"]:
            static_rows = static_recent_form_for(team_name)
            summary = summarize_static_form(static_rows, 5)
            source = "Static local form database"

        if not summary["form"]:
            lines.extend([
                team_name,
                "",
                "近期状态样本不可用。",
                "",
            ])
            continue

        lines.extend([
            team_name,
            "",
            " ".join(summary["form"]),
            "",
            f"GF: {summary['gf']}",
            f"GA: {summary['ga']}",
            f"数据来源：{source}",
            "",
        ])

    return lines if has_team else []


def build_report(
    match,
    odds,
    polymarket,
    news,
    probabilities,
    scores,
    rating,
    api_football_data=None,
    value_analysis=None,
    betting_opinion=None,
    portfolio_summary=None,
    actual_odds=None,
):
    lines = [
        f"# {match['display_name']} 分析报告",
        "",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        *format_fixture_lines(api_football_data, match),
        "",
        *format_betting_opinion_lines(betting_opinion),
        "",
        *format_data_quality_lines(betting_opinion, api_football_data, match, actual_odds),
        "",
        *format_portfolio_eligibility_lines(portfolio_summary, match),
        "",
        *format_match_winner_lines(odds),
        "",
        *format_asian_handicap_lines(api_football_data, odds, match),
        "",
        *format_over_under_lines(odds),
        "",
        *format_correct_score_lines(api_football_data),
        "",
        *format_injuries_lines(api_football_data),
        "",
        *format_lineups_lines(api_football_data),
    ]
    return "\n".join(lines)


def save_report(report, match, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    safe_name = match["display_name"].replace(" ", "_").replace("/", "_")
    path = Path(output_dir) / f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path.write_text(report, encoding="utf-8")
    return path
