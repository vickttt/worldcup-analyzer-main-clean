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


def tpb_probability_label(odds=None, match=None, fallback=None):
    fallback_text = str(fallback or "").strip()
    if fallback_text and fallback_text not in {"-", "暂无标签，详见胜平负 TPB 概率"}:
        return fallback_text

    probabilities = (true_probability_base(odds or {}).get("probabilities") or {})
    if not probabilities:
        return "暂无标签，详见胜平负 TPB 概率"

    outcome_labels = {
        "home_win": _match_team_label(match, "home"),
        "draw": "平局",
        "away_win": _match_team_label(match, "away"),
    }
    ordered = sorted(probabilities, key=lambda key: probabilities.get(key, 0), reverse=True)
    top = ordered[0]
    top_probability = probabilities.get(top, 0)
    second_probability = probabilities.get(ordered[1], 0) if len(ordered) > 1 else 0
    draw_probability = probabilities.get("draw", 0)

    if top == "draw" or draw_probability >= 0.30 or top_probability - second_probability < 0.08:
        return "均衡/平局风险较高"
    if top_probability >= 0.75:
        return f"强热门方向：{outcome_labels.get(top, top)}"
    if top_probability >= 0.60:
        return f"优势方向：{outcome_labels.get(top, top)}"
    if top_probability >= 0.45:
        return f"轻微优势方向：{outcome_labels.get(top, top)}"
    return "均衡/平局风险较高"


def _coverage_display_text(value):
    text = str(value or "").strip()
    if not text:
        return text
    replacements = {
        "防守型覆盖资产": "防守参考",
        "保险 / 覆盖资产": "覆盖说明 / 防守参考",
        "保险/覆盖资产": "覆盖说明 / 防守参考",
        "保险资产": "防守参考",
        "覆盖资产": "覆盖说明",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _localized_injury_text(value):
    text = str(value or "").strip()
    if not text:
        return format_value(value)
    translations = {
        "Missing Fixture": "缺席本场",
        "Hamstring Injury": "腘绳肌伤病",
        "Ankle Problems": "脚踝问题",
        "Yellow Card": "黄牌停赛/黄牌风险",
        "Suspension Through Sports Court": "停赛",
        "Muscle Bruise": "肌肉挫伤",
    }
    return translations.get(text, text)


def _score_parts(score):
    text = str(score or "").strip()
    separators = (":", "-", "–")
    for separator in separators:
        if separator not in text:
            continue
        left, right = text.split(separator, 1)
        try:
            return int(left.strip()), int(right.strip())
        except (TypeError, ValueError):
            return None
    return None


def _displayable_correct_score(score):
    parsed = _score_parts(score)
    if not parsed:
        return True
    home_score, away_score = parsed
    return home_score < 10 and away_score < 10


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
            f"{_localized_injury_text(injury_type)} / {_localized_injury_text(reason)}"
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
            f"TPB 覆盖说明：{center.get('coverage_label')}",
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
    display_markets = [
        market for market in markets
        if _displayable_correct_score(market.get("score"))
    ]
    hidden_count = len(markets) - len(display_markets)
    if hidden_count:
        lines.append(f"数据提示：已隐藏 {hidden_count} 条 10球级极端比分，仅保留常规波胆展示。")
        lines.append("")
    for market in display_markets[:40]:
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


def _data_quality_notes(betting_opinion, api_football_data=None, match=None, actual_odds=None):
    opinion = betting_opinion or {}
    notes = list(opinion.get("data_quality_notes") or [])
    if not ((api_football_data or {}).get("lineups")) and "Official lineups not released." not in notes:
        if "官方首发尚未公布。" not in notes:
            notes.append("官方首发尚未公布。")
    missing = fixture_metadata(api_football_data, match).get("missing") if (api_football_data or match) else []
    if missing:
        notes.append("缺少 fixture metadata：" + "、".join(missing) + "。")
    return notes


def _portfolio_eligible(portfolio_summary):
    eligibility = (portfolio_summary or {}).get("rank1_eligibility") or {}
    eligible = eligibility.get("rank1_eligible")
    if eligible is None:
        eligible = eligibility.get("eligible")
    return eligible


def _recommended_stake_amount(portfolio_summary):
    stake = (portfolio_summary or {}).get("recommended_stake") or {}
    amount = stake.get("amount")
    if amount is None:
        return None
    try:
        return float(amount)
    except (TypeError, ValueError):
        return None


def format_core_conclusion_lines(
    betting_opinion,
    portfolio_summary=None,
    odds=None,
    match=None,
    api_football_data=None,
    actual_odds=None,
):
    opinion = betting_opinion or {}
    portfolio_summary = portfolio_summary or {}
    risk_diagnostic = portfolio_summary.get("risk_diagnostic") or {}
    eligible = _portfolio_eligible(portfolio_summary)
    stake_amount = _recommended_stake_amount(portfolio_summary)
    if stake_amount == 0:
        execution_judgment = "可观察，当前不建议投入"
    else:
        execution_judgment = "无法获取" if eligible is None else "可执行" if eligible else "暂不执行"
    score = portfolio_summary.get("decision_score")
    if score is None:
        score = portfolio_summary.get("score")
    notes = _data_quality_notes(opinion, api_football_data, match, actual_odds)
    lines = [
        "## 1. Core Decision Layer（核心决策层）",
        "",
        f"- 比赛主方向：{opinion.get('match_direction') or opinion.get('match_winner', '暂无观点')}",
        f"- TPB 概率标签：{tpb_probability_label(odds, match, opinion.get('market_direction_label'))}",
        f"- 比赛投资分：{format_value(score)}",
        f"- 投注信心：{opinion.get('betting_confidence', opinion.get('confidence', 50))} / 100",
        f"- 推荐金额：{_recommended_stake_text(portfolio_summary)}",
        f"- 执行判断：{execution_judgment}",
        f"- 数据质量：{quality_cn(opinion.get('data_quality'))}",
        f"- 执行模式：{portfolio_summary.get('portfolio_style_label') or (portfolio_summary.get('portfolio_style') or {}).get('style_cn') or '-'}",
        "",
        "主依据：",
        f"- {opinion.get('match_winner_reason', '-')}",
        f"- {risk_diagnostic.get('reason') or 'TPB 风险诊断不阻断推荐；推荐金额只由比赛投资分决定。'}",
    ]
    if stake_amount == 0:
        lines.append("- 推荐金额为 0 元表示当前不建议下注；该金额仍由比赛投资分映射得出。")
    if notes:
        lines.extend(["", "数据质量提示："])
        for note in notes[:5]:
            lines.append(f"- {note}")
    return lines


def format_tpb_coverage_lines(betting_opinion):
    opinion = betting_opinion or {}
    lines = [
        "## TPB 覆盖说明",
        "",
        opinion.get("coverage_candidate") or "暂无 TPB 覆盖说明",
        "",
        "说明：",
        _coverage_display_text(opinion.get("coverage_reason")) or "-",
        "",
        "用途：",
        _coverage_display_text(opinion.get("recommended_use")) or "-",
        "",
        "TPB 覆盖说明仅作为防守参考，不是主方向投注，不参与 TPB、比赛投资分或推荐金额。",
    ]
    return lines


def format_handicap_observation_lines(betting_opinion):
    opinion = betting_opinion or {}
    lines = [
        "## 盘口观察",
        "",
        opinion.get("handicap_market_direction") or opinion.get("asian_handicap", "暂无观点"),
        "",
        "理由：",
        opinion.get("asian_handicap_reason", "-"),
        "",
        "盘口观察是市场结构观察，不是 TPB 主决策来源，不参与比赛投资分或推荐金额。",
    ]
    return lines


def format_goals_view_lines(betting_opinion):
    opinion = betting_opinion or {}
    return [
        "## 进球数观点",
        "",
        f"总进球盘口中心：{opinion.get('total_center', '-')}",
        "",
        f"市场倾向：{opinion.get('goals_market_bias', opinion.get('over_under_reason', '-'))}",
        "",
        f"比赛行为提示：{opinion.get('goals_game_behavior_note', '-')}",
        "",
        f"解释：{opinion.get('goals_recommended_interpretation', '-')}",
    ]


def format_data_quality_lines(betting_opinion, api_football_data=None, match=None, actual_odds=None):
    notes = _data_quality_notes(betting_opinion, api_football_data, match, actual_odds)
    if not notes:
        return []
    lines = ["## 数据质量提示", ""]
    for note in notes:
        lines.append(f"- {note}")
    return lines


def _recommended_stake_text(portfolio_summary):
    stake = (portfolio_summary or {}).get("recommended_stake") or {}
    amount = stake.get("amount")
    if amount is None:
        return "未计算（推荐金额由比赛投资分映射得出）"
    return f"{format_value(amount)}元"


def format_result_distribution_observation_lines(betting_opinion):
    distribution = (betting_opinion or {}).get("result_distribution") or {}
    rows = distribution.get("rows") or []
    lines = [
        "## 结果分布观察",
        "",
        "结果分布仅作为观察层展示，不参与 TPB、比赛投资分或推荐金额。",
    ]
    if not rows:
        return lines + ["", "结果分布观察：暂无可用观察数据。"]
    lines.append("")
    for row in rows[:6]:
        probability = row.get("probability")
        probability_text = percent(probability) if probability is not None else "-"
        lines.append(f"- {row.get('label', '-')}：{probability_text} · {row.get('meaning', '-')}")
    return lines


def format_polymarket_observation_lines(polymarket):
    reference = polymarket or {}
    lines = [
        "## Polymarket 只读对比层",
        "",
        "Polymarket 仅作为市场情绪观察，不替代 API-Football 赔率，也不参与 TPB、比赛投资分或推荐金额。",
    ]
    if not reference.get("found"):
        return lines + ["", f"Polymarket 只读对比层：{reference.get('message') or '暂无可用市场对比数据。'}"]
    rows = [
        ("主胜参考概率", reference.get("home_win")),
        ("平局参考概率", reference.get("draw")),
        ("客胜参考概率", reference.get("away_win")),
    ]
    lines.append("")
    for label, value in rows:
        lines.append(f"- {label}：{percent(value) if value is not None else '-'}")
    if reference.get("event_title"):
        lines.append(f"- 事件：{reference.get('event_title')}")
    return lines


def format_market_intelligence_lines(market_intelligence):
    intelligence = market_intelligence or {}
    metrics = intelligence.get("metrics") or {}
    lines = [
        "## 2. Market Structure Layer（市场结构层）",
        "",
        "该层只解释市场结构，不独立决策，不覆盖 TPB，不影响 stake，不使用用户输入，不计算 EV/ROI。",
        "",
        f"- Directional Strength：{metrics.get('directional_strength', '-')}",
        f"- Market Conflict Index：{format_value(metrics.get('market_conflict_index'))} / 100（{metrics.get('market_conflict_label', '-')}）",
        f"- Efficiency Score：{format_value(metrics.get('market_efficiency_score'))} / 100",
        f"- Volatility Index：{metrics.get('volatility_index', '-')}",
        f"- Upset Probability：{metrics.get('upset_probability', '-')}",
    ]
    if metrics.get("favorite_label"):
        lines.append(f"- TPB baseline 主方向：{metrics.get('favorite_label')}（{format_value(metrics.get('favorite_probability'))}%）")
    if metrics.get("explanation"):
        lines.extend(["", f"说明：{metrics.get('explanation')}"])
    return lines


def format_system_portfolio_lines(market_intelligence):
    portfolio = ((market_intelligence or {}).get("system_portfolio") or {})
    lines = [
        "## 3. System Portfolio Layer（系统推荐组合）",
        "",
        "系统组合仅使用 TPB baseline 与 Market Structure signals；用户实盘输入不参与系统组合、推荐或排序。",
        "",
    ]
    for key in ["main_position", "defensive_position", "tail_risk_position"]:
        item = portfolio.get(key) or {}
        lines.append(f"- {item.get('name', '-')}：{item.get('label', '-')}")
        lines.append(f"  - 说明：{item.get('rationale', '-')}")
    lines.extend([
        "",
        "## 4. System Ranking（系统级排序）",
        "",
        "仅系统组合参与排序；依据 TPB baseline strength、Directional Strength、Conflict、Efficiency、Volatility 与 Upset signals；不使用用户输入、EV/ROI 或 legacy optimizer。",
    ])
    ranking = portfolio.get("ranking") or []
    if not ranking:
        return lines + ["", "暂无系统组合排序。"]
    for item in ranking:
        lines.append(
            f"- Rank {item.get('rank', '-')}: {item.get('position', '-')} "
            f"（依据：{item.get('basis', '-')}）"
        )
    return lines


def format_user_portfolio_lines(user_portfolio):
    comparison = user_portfolio or {}
    lines = [
        "## 5. Execution Layer（用户执行层）",
        "",
        "客户执行层仅用于记录实盘输入、执行价格对比和人工复盘；不参与 TPB、系统推荐、系统排序或 stake。",
        "",
        "### 我的实盘组合",
        "",
        comparison.get("disclaimer")
        or "我的执行价格分析仅用于复盘和价格偏差提醒，不参与 TPB、比赛投资分或推荐金额。",
        "",
    ]
    if not comparison.get("has_input"):
        return lines + ["我的实盘组合：未输入。系统输出不受用户组合影响。"]

    errors = comparison.get("errors") or []
    if errors:
        lines.append("输入提示：")
        for error in errors:
            lines.append(f"- {error}")
        lines.append("")

    positions = comparison.get("positions") or []
    if not positions:
        return lines + ["暂未解析到有效实盘组合。"]

    lines.extend([
        f"- 总笔数：{comparison.get('total_count', 0)}",
        "",
        "明细：",
    ])
    for item in positions:
        lines.append(
            "- "
            f"{format_value(item.get('market'))} / "
            f"{format_value(item.get('selection'))} / "
            f"盘口 {format_value(item.get('handicap_display') or '-')} / "
            f"{'系统识别为分段盘口 / ' if item.get('is_split_line') else ''}"
            f"实际赔率 {format_value(item.get('user_odds'))}"
        )

    lines.extend([
        "",
        "### 我的执行价格分析（Value Check）",
        "",
        "仅用于复盘，不影响 TPB 决策；价格差异不参与比赛投资分、推荐金额或系统主结论。",
        "",
    ])
    for item in positions:
        api_odds = item.get("api_reference_odds")
        lines.append(
            "- "
            f"{format_value(item.get('market'))} / "
            f"{format_value(item.get('selection'))} / "
            f"盘口 {format_value(item.get('handicap_display') or '-')}："
            f"用户实际赔率 {format_value(item.get('user_odds'))}；"
            f"API参考赔率 {format_value(api_odds) if api_odds is not None else '暂无可比 API 赔率'}；"
            f"赔率差值 {item.get('price_difference_pct_text', '-')}；"
            f"判断：{item.get('price_judgment', '-')}"
        )
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
    user_portfolio=None,
    market_intelligence=None,
):
    lines = [
        f"# {match['display_name']} 分析报告",
        "",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        *format_fixture_lines(api_football_data, match),
        "",
        *format_core_conclusion_lines(
            betting_opinion,
            portfolio_summary,
            odds,
            match,
            api_football_data,
            actual_odds,
        ),
        "",
        *format_market_intelligence_lines(market_intelligence),
        "",
        *format_system_portfolio_lines(market_intelligence),
        "",
        *format_user_portfolio_lines(user_portfolio),
        "",
        *format_tpb_coverage_lines(betting_opinion),
        "",
        *format_handicap_observation_lines(betting_opinion),
        "",
        *format_goals_view_lines(betting_opinion),
        "",
        *format_result_distribution_observation_lines(betting_opinion),
        "",
        *format_polymarket_observation_lines(polymarket),
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
