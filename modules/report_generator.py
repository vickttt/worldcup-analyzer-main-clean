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


SCENARIO_NAME_CN = {
    "S1": "强热门获胜",
    "S2": "热门小胜",
    "S3": "平局",
    "S4": "冷门获胜",
    "S5": "低比分比赛",
    "S6": "高波动比赛",
}

LEVEL_CN = {
    "Low": "低",
    "Medium": "中",
    "High": "高",
}

PORTFOLIO_SET_CN = {
    "Primary Coverage Set": "主覆盖组合",
    "Defensive Coverage Set": "防守覆盖组合",
    "Tail Coverage Set": "高波动覆盖组合",
}


def _level_cn(value):
    return LEVEL_CN.get(str(value), format_value(value))


def _scenario_name_cn(code, name=None):
    return f"{code} {SCENARIO_NAME_CN.get(code, name or '-')}"


def _portfolio_position_cn(value):
    return PORTFOLIO_SET_CN.get(str(value), format_value(value))


def _team_labels_from_match(match):
    if not match:
        return "热门方向", "冷门方向"
    home = _match_team_label(match, "home")
    away = _match_team_label(match, "away")
    return home, away


def _favorite_and_underdog(match=None, market_intelligence=None, scenario_engine=None):
    home, away = _team_labels_from_match(match)
    metrics = (market_intelligence or {}).get("metrics") or {}
    favorite = metrics.get("favorite_label")
    if not favorite:
        primary = ((scenario_engine or {}).get("scenario_optimization_v2") or {}).get("primary_coverage_set") or []
        favorite = (primary[0] or {}).get("selection") if primary else None
    favorite = favorite or home
    favorite_text = str(favorite)
    if favorite_text in {home, away}:
        underdog = away if favorite_text == home else home
    elif home in favorite_text:
        favorite_text = home
        underdog = away
    elif away in favorite_text:
        favorite_text = away
        underdog = home
    else:
        underdog = "冷门方向"
    return favorite_text, underdog


def _score_for_side(match, side, home_goals, away_goals):
    if not match:
        return f"{home_goals}:{away_goals}"
    home = _match_team_label(match, "home")
    away = _match_team_label(match, "away")
    if side == home:
        return f"{home_goals}:{away_goals}"
    if side == away:
        return f"{away_goals}:{home_goals}"
    return f"{home_goals}:{away_goals}"


def _basis_cn(value):
    text = str(value or "").strip()
    replacements = {
        "TPB anchor": "TPB 锚点",
        "Directional Strength": "方向强度",
        "scenario weights": "情景权重",
        "Conflict Index": "冲突指数",
        "Volatility": "波动指数",
        "tail exposure constraint": "尾部风险约束",
        "S1/S2": "S1/S2",
        "S3/S4/S5": "S3/S4/S5",
        "S4/S6": "S4/S6",
        "+": "+",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text or "-"


def portfolio_leg_display(leg, match=None, market_intelligence=None, scenario_engine=None):
    leg = leg or {}
    leg_id = leg.get("id")
    favorite, underdog = _favorite_and_underdog(match, market_intelligence, scenario_engine)
    selection = leg.get("selection") or "-"
    if selection in {"TPB 主方向", "热门方向"} or leg_id in {"primary_1x2", "primary_handicap"}:
        selection = favorite
    scenario_text = " / ".join(
        f"{item.get('code')} {percent(item.get('weight', 0))}"
        for item in (leg.get("scenario_dependency") or [])
    )
    templates = {
        "primary_1x2": {
            "bet": f"{selection} 独赢",
            "market": "胜平负",
            "reason": "覆盖 S1/S2 主方向情景，跟随 TPB 主方向。",
        },
        "primary_handicap": {
            "bet": f"{selection} -0.5",
            "market": "亚洲让球 -0.5",
            "reason": "主方向轻让球覆盖，适合热门方向兑现但不做收益优化。",
        },
        "defensive_draw": {
            "bet": "平局",
            "market": "胜平负",
            "reason": "覆盖 S3 平局风险，作为主方向的防守参考。",
        },
        "defensive_handicap": {
            "bet": f"{favorite} +1.0",
            "market": "亚洲让球 +1.0",
            "reason": "平局和冷门保护，降低主方向单边暴露。",
        },
        "defensive_under": {
            "bet": "小球 Under 2.5",
            "market": "大小球 2.5",
            "reason": "覆盖 S5 低比分和热门小胜情景。",
        },
        "tail_upset": {
            "bet": f"{underdog} 冷门胜",
            "market": "胜平负",
            "reason": "仅覆盖 S4 冷门尾部风险，不放大推荐金额。",
        },
        "tail_variance": {
            "bet": "大球 Over 3.5",
            "market": "大小球 3.5",
            "reason": "覆盖 S6 高波动路径；波胆由高波动策略层单独表达。",
        },
    }
    template = templates.get(leg_id, {})
    return {
        "中文投注描述": template.get("bet") or leg.get("name") or "-",
        "对应盘口": template.get("market") or leg.get("market") or "-",
        "理由": template.get("reason") or leg.get("explanation") or "-",
        "情景依赖": scenario_text or "-",
        "覆盖贡献": format_value(leg.get("coverage_contribution")),
        "风险暴露": format_value(leg.get("risk_exposure")),
    }


def portfolio_leg_display_rows(legs, match=None, market_intelligence=None, scenario_engine=None):
    return [
        portfolio_leg_display(
            leg,
            match=match,
            market_intelligence=market_intelligence,
            scenario_engine=scenario_engine,
        )
        for leg in (legs or [])
    ]


def correct_score_strategy_rows(match=None, market_intelligence=None, scenario_engine=None):
    favorite, underdog = _favorite_and_underdog(match, market_intelligence, scenario_engine)
    primary_10 = _score_for_side(match, favorite, 1, 0)
    primary_20 = _score_for_side(match, favorite, 2, 0)
    primary_21 = _score_for_side(match, favorite, 2, 1)
    upset_01 = _score_for_side(match, underdog, 1, 0)
    high_32 = _score_for_side(match, favorite, 3, 2)
    high_31 = _score_for_side(match, favorite, 3, 1)
    return [
        {
            "波胆层级": "主波胆",
            "中文投注描述": f"{primary_10} {favorite}胜",
            "对应盘口": "波胆 / Correct Score",
            "理由": "TPB + S1 主路径，小胜结构覆盖。",
            "情景依赖": "S1",
        },
        {
            "波胆层级": "主波胆",
            "中文投注描述": f"{primary_20} {favorite}胜",
            "对应盘口": "波胆 / Correct Score",
            "理由": "S1 + S2 强化路径，跟随 TPB 主方向。",
            "情景依赖": "S1/S2",
        },
        {
            "波胆层级": "主波胆",
            "中文投注描述": f"{primary_21} {favorite}胜",
            "对应盘口": "波胆 / Correct Score",
            "理由": "S2 窄胜路径，补充热门方向但保留失球风险。",
            "情景依赖": "S2",
        },
        {
            "波胆层级": "结构波胆",
            "中文投注描述": "1:1 平局",
            "对应盘口": "波胆 / Correct Score",
            "理由": "S3 平局密度与市场冲突结构覆盖。",
            "情景依赖": "S3",
        },
        {
            "波胆层级": "结构波胆",
            "中文投注描述": "0:0",
            "对应盘口": "波胆 / Correct Score",
            "理由": "S3 + S5 低节奏平局结构。",
            "情景依赖": "S3/S5",
        },
        {
            "波胆层级": "结构波胆",
            "中文投注描述": f"{upset_01} {underdog}冷门",
            "对应盘口": "波胆 / Correct Score",
            "理由": "S4 冷门路径与冲突市场保护。",
            "情景依赖": "S4",
        },
        {
            "波胆层级": "高波动波胆",
            "中文投注描述": "2:2",
            "对应盘口": "波胆 / Correct Score",
            "理由": "S6 高波动核心，兼顾进球扩展。",
            "情景依赖": "S6",
        },
        {
            "波胆层级": "高波动波胆",
            "中文投注描述": f"{high_32} 高进球波动",
            "对应盘口": "波胆 / Correct Score",
            "理由": "S6 高进球波动路径。",
            "情景依赖": "S6",
        },
        {
            "波胆层级": "高波动波胆",
            "中文投注描述": f"{high_31} 高波动胜出",
            "对应盘口": "波胆 / Correct Score",
            "理由": "S5/S6 低比分与高波动之间的扩展路径。",
            "情景依赖": "S6",
        },
    ]


def correct_score_strategy_summary_rows(match=None, market_intelligence=None, scenario_engine=None):
    rows = correct_score_strategy_rows(match, market_intelligence, scenario_engine)
    grouped = {
        "主波胆": [],
        "结构波胆": [],
        "高波动波胆": [],
    }
    for row in rows:
        level = row.get("波胆层级")
        if level in grouped:
            grouped[level].append(row)
    summaries = []
    for level, items in grouped.items():
        summaries.append({
            "波胆层级": level,
            "摘要": "；".join(item.get("中文投注描述", "-") for item in items[:3]) or "暂无",
            "情景依赖": " / ".join(sorted({item.get("情景依赖", "-") for item in items if item.get("情景依赖")})) or "-",
            "说明": {
                "主波胆": "TPB + S1/S2 主路径。",
                "结构波胆": "S3、市场冲突和平局密度结构。",
                "高波动波胆": "S5/S6 高方差结构核心。",
            }.get(level, "-"),
        })
    return summaries


def scenario_probability_weight_rows(scenario_engine):
    scenario = scenario_engine or {}
    weights = {
        item.get("code"): item
        for item in (scenario.get("scenario_weights") or [])
    }
    rows = []
    for item in scenario.get("probability_distribution") or []:
        code = item.get("code", "-")
        weight = weights.get(code) or {}
        rows.append({
            "情景": _scenario_name_cn(code, item.get("name")),
            "原始概率": percent(item.get("probability", 0)),
            "v2 权重": percent(weight.get("weight", 0)),
        })
    return rows


def scenario_risk_surface_rows(scenario_engine):
    risk = (scenario_engine or {}).get("risk_surface") or {}
    return [
        {"风险面": "尾部风险集中度", "等级": _level_cn(risk.get("tail_risk_concentration")), "数值": percent(risk.get("tail_risk_value", 0))},
        {"风险面": "市场脆弱性", "等级": _level_cn(risk.get("market_fragility")), "数值": percent(risk.get("market_fragility_value", 0))},
        {"风险面": "冷门暴露", "等级": _level_cn(risk.get("upset_exposure")), "数值": percent(risk.get("upset_exposure_value", 0))},
        {"风险面": "平局依赖", "等级": _level_cn(risk.get("draw_dependency")), "数值": percent(risk.get("draw_dependency_value", 0))},
    ]


def scenario_coverage_map_rows(scenario_engine):
    coverage = (scenario_engine or {}).get("coverage_map") or {}
    return [
        {
            "覆盖类型": "主覆盖",
            "情景": (coverage.get("primary_coverage") or {}).get("scenario", "-"),
            "说明": (coverage.get("primary_coverage") or {}).get("description", "-"),
        },
        {
            "覆盖类型": "防守覆盖",
            "情景": (coverage.get("defensive_coverage") or {}).get("scenario", "-"),
            "说明": (coverage.get("defensive_coverage") or {}).get("description", "-"),
        },
        {
            "覆盖类型": "高波动覆盖",
            "情景": (coverage.get("tail_optionality") or {}).get("scenario", "-"),
            "说明": (coverage.get("tail_optionality") or {}).get("description", "-"),
        },
    ]


def _optimization_sets(scenario_engine):
    optimization = (scenario_engine or {}).get("scenario_optimization_v2") or {}
    return {
        "Primary Coverage Set": optimization.get("primary_coverage_set") or [],
        "Defensive Coverage Set": optimization.get("defensive_coverage_set") or [],
        "Tail Coverage Set": optimization.get("tail_coverage_set") or [],
    }


def system_portfolio_display_rows(scenario_engine, match=None, market_intelligence=None):
    rows = []
    sets = _optimization_sets(scenario_engine)
    ordered_sets = [
        ("Primary Coverage Set", sets.get("Primary Coverage Set") or []),
        ("Defensive Coverage Set", sets.get("Defensive Coverage Set") or []),
        ("Tail Coverage Set", sets.get("Tail Coverage Set") or []),
    ]
    for title, legs in ordered_sets:
        display_legs = portfolio_leg_display_rows(
            legs,
            match=match,
            market_intelligence=market_intelligence,
            scenario_engine=scenario_engine,
        )
        if not display_legs:
            rows.append({
                "组合类型": _portfolio_position_cn(title),
                "中文投注描述": "暂无",
                "对应盘口": "-",
                "理由": "当前情景权重未生成该组合。",
            })
            continue
        for leg in display_legs:
            rows.append({"组合类型": _portfolio_position_cn(title), **leg})
    return rows


def system_portfolio_summary_rows(scenario_engine, match=None, market_intelligence=None):
    sets = _optimization_sets(scenario_engine)
    score_rows = correct_score_strategy_rows(match, market_intelligence, scenario_engine)
    return [
        {
            "层级": "主覆盖",
            "摘要": f"{len(sets.get('Primary Coverage Set') or [])} 个主覆盖投注",
            "角色": "TPB aligned 主方向集合。",
        },
        {
            "层级": "波胆策略",
            "摘要": f"{len(score_rows)} 个波胆结构，分为主波胆 / 结构波胆 / 高波动波胆",
            "角色": "高熵、高方差、高信息密度的情景波动层。",
        },
        {
            "层级": "防守覆盖",
            "摘要": f"{len(sets.get('Defensive Coverage Set') or [])} 个防守覆盖投注",
            "角色": "Under / Draw / Handicap hedge 防守集合。",
        },
        {
            "层级": "高波动覆盖",
            "摘要": f"{len(sets.get('Tail Coverage Set') or [])} 个极端情景投注",
            "角色": "S4/S6 高波动和冷门路径集合。",
        },
    ]


def _score_rows_for_ranking(position, match=None, market_intelligence=None, scenario_engine=None):
    rows = correct_score_strategy_rows(match, market_intelligence, scenario_engine)
    if position == "Primary Coverage Set":
        return [row for row in rows if row["波胆层级"] == "主波胆"][:2]
    if position == "Defensive Coverage Set":
        return [row for row in rows if row["波胆层级"] == "结构波胆"][:2]
    if position == "Tail Coverage Set":
        return [row for row in rows if row["波胆层级"] == "高波动波胆"][:2]
    return []


def _compact_legs_for_ranking(position, legs):
    if position == "Primary Coverage Set":
        return legs[:1]
    if position == "Defensive Coverage Set":
        return legs[:1]
    if position == "Tail Coverage Set":
        return legs[:1]
    return legs[:1]


def system_ranking_display_rows(portfolio, scenario_engine=None, match=None, market_intelligence=None):
    rows = []
    sets = _optimization_sets(scenario_engine)
    for item in (portfolio or {}).get("ranking") or []:
        position = item.get("position", "-")
        legs = portfolio_leg_display_rows(
            sets.get(position) or [],
            match=match,
            market_intelligence=market_intelligence,
            scenario_engine=scenario_engine,
        )
        legs = _compact_legs_for_ranking(position, legs)
        score_rows = _score_rows_for_ranking(position, match, market_intelligence, scenario_engine)[:1]
        bet_text = "；".join(
            [leg.get("中文投注描述", "-") for leg in legs]
            + [row.get("中文投注描述", "-") for row in score_rows]
        ) or "暂无"
        market_text = "；".join(
            [leg.get("对应盘口", "-") for leg in legs]
            + [row.get("对应盘口", "-") for row in score_rows]
        ) or "-"
        dependency_text = "；".join(
            [leg.get("情景依赖", "-") for leg in legs if leg.get("情景依赖")]
            + [row.get("情景依赖", "-") for row in score_rows if row.get("情景依赖")]
        ) or "-"
        score_reason = "；".join(row.get("理由", "-") for row in score_rows)
        reason = _basis_cn(item.get("basis"))
        if score_reason:
            reason = f"{reason}；波胆：{score_reason}"
        rows.append({
            "排名": f"Rank {item.get('rank', '-')}",
            "组合类型": _portfolio_position_cn(position),
            "具体投注组合": bet_text,
            "对应盘口": market_text,
            "结构理由": reason,
            "情景依赖": dependency_text,
        })
    return rows


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
        "## 1. 核心决策层",
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


def format_final_decision_block_lines(
    betting_opinion,
    portfolio_summary=None,
    odds=None,
    match=None,
    market_intelligence=None,
    scenario_engine=None,
):
    opinion = betting_opinion or {}
    portfolio_summary = portfolio_summary or {}
    tpb = true_probability_base(odds or {})
    probabilities = tpb.get("probabilities") or {}
    metrics = (market_intelligence or {}).get("metrics") or {}
    scenario = scenario_engine or {}
    portfolio = (
        scenario.get("system_optimized_portfolio_v2")
        or ((market_intelligence or {}).get("system_portfolio") or {})
    )
    optimization = scenario.get("scenario_optimization_v2") or {}
    risk = scenario.get("risk_surface") or {}
    coverage = scenario.get("coverage_map") or {}
    scenario_rows = scenario_probability_weight_rows(scenario)
    scenario_summary = "；".join(
        f"{row['情景']} {row['原始概率']} / 权重 {row['v2 权重']}"
        for row in scenario_rows
    ) or "暂无情景概率与权重数据。"
    score = portfolio_summary.get("decision_score")
    if score is None:
        score = portfolio_summary.get("score")

    lines = [
        "## 最终决策区（FINAL DECISION BLOCK）",
        "",
        "唯一决策入口视图：TPB 锚点 + 市场结构 + 情景权重 + 推荐组合 + 系统排名汇总展示。用户执行层不进入本区。",
        "",
        "### 1. TPB 结论",
        "",
        f"- 主方向：{metrics.get('favorite_label') or opinion.get('match_direction') or opinion.get('match_winner', '-')}",
        f"- 主方向概率：{format_value(metrics.get('favorite_probability'))}%",
        f"- TPB 概率：主胜 {percent(probabilities.get('home_win', 0)) if probabilities else '-'} / 平局 {percent(probabilities.get('draw', 0)) if probabilities else '-'} / 客胜 {percent(probabilities.get('away_win', 0)) if probabilities else '-'}",
        f"- 投注信心：{opinion.get('betting_confidence', opinion.get('confidence', 50))} / 100",
        f"- 比赛投资分：{format_value(score)}",
        f"- 推荐金额：{_recommended_stake_text(portfolio_summary)}",
        "",
        "### 2. 市场结构",
        "",
        f"- 方向强度：{metrics.get('directional_strength', '-')}",
        f"- 市场冲突指数：{format_value(metrics.get('market_conflict_index'))} / 100",
        f"- 市场效率分：{format_value(metrics.get('market_efficiency_score'))} / 100",
        f"- 波动指数：{metrics.get('volatility_index', '-')}",
        f"- 冷门概率：{metrics.get('upset_probability', '-')}",
        "",
        "### 3. 情景概率与权重分析（Scenario Engine v2）",
        "",
        f"- S1-S6：{scenario_summary}",
        f"- 风险面：尾部 {_level_cn(risk.get('tail_risk_concentration'))} / 脆弱性 {_level_cn(risk.get('market_fragility'))} / 冷门 {_level_cn(risk.get('upset_exposure'))} / 平局 {_level_cn(risk.get('draw_dependency'))}",
        f"- 覆盖图：主覆盖 {(coverage.get('primary_coverage') or {}).get('scenario', '-')} / 防守覆盖 {(coverage.get('defensive_coverage') or {}).get('scenario', '-')} / 高波动覆盖 {(coverage.get('tail_optionality') or {}).get('scenario', '-')}",
        f"- 覆盖效率 v2：{format_value(optimization.get('coverage_efficiency_score_v2'))} / 100",
        "",
        "### 4. 系统推荐投注组合（System Portfolio）",
        "",
        "Portfolio 是投注组合集合；本区只显示压缩摘要，完整明细见下方系统组合明细。",
        "Portfolio Priority v2：主覆盖（TPB aligned） -> 波胆策略（Correct Score Layer） -> 防守覆盖 -> 高波动覆盖。",
        "",
    ]
    for row in system_portfolio_summary_rows(scenario, match=match, market_intelligence=market_intelligence):
        lines.append(
            f"- {row['层级']}：{row['摘要']}｜角色：{row['角色']}"
        )
    lines.extend([
        "",
        "#### 波胆策略摘要（Correct Score Strategy v2.2 / High Variance Strategy Layer）",
        "",
        "说明：波胆是高熵、高方差、高信息密度市场，用于表达情景波动结构，不作为 EV/ROI 或收益优化。",
        "",
    ])
    for row in correct_score_strategy_summary_rows(match, market_intelligence, scenario):
        lines.append(
            f"- {row['波胆层级']}：{row['摘要']}｜情景依赖：{row['情景依赖']}｜说明：{row['说明']}"
        )
    lines.extend([
        "",
        "### 5. 系统排名组合（System Ranking Bets，仅系统）",
        "",
        "Ranking 是优先级排序结果，不是 Portfolio 明细复制；本区只保留 Top3 精简投注。",
        "",
    ])
    ranking_rows = system_ranking_display_rows(
        portfolio,
        scenario,
        match=match,
        market_intelligence=market_intelligence,
    )
    if not ranking_rows:
        lines.append("- 暂无系统排序。")
    for row in ranking_rows:
        lines.append(
            f"- {row['排名']}：{row['具体投注组合']}｜盘口：{row['对应盘口']}｜原因：{row['结构理由']}｜情景依赖：{row['情景依赖']}"
        )
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
        "## 2. 市场结构层",
        "",
        "该层只解释市场结构，不独立决策，不覆盖 TPB，不影响推荐金额，不使用用户输入，不计算 EV/ROI。",
        "",
        f"- 方向强度：{metrics.get('directional_strength', '-')}",
        f"- 市场冲突指数：{format_value(metrics.get('market_conflict_index'))} / 100（{metrics.get('market_conflict_label', '-')}）",
        f"- 市场效率分：{format_value(metrics.get('market_efficiency_score'))} / 100",
        f"- 波动指数：{metrics.get('volatility_index', '-')}",
        f"- 冷门概率：{metrics.get('upset_probability', '-')}",
    ]
    if metrics.get("favorite_label"):
        lines.append(f"- TPB baseline 主方向：{metrics.get('favorite_label')}（{format_value(metrics.get('favorite_probability'))}%）")
    if metrics.get("explanation"):
        lines.extend(["", f"说明：{metrics.get('explanation')}"])
    return lines


def format_scenario_engine_lines(scenario_engine):
    scenario = scenario_engine or {}
    lines = [
        "## 3. 情景概率与权重分析（Scenario Engine v2）",
        "",
        scenario.get("disclaimer")
        or "Scenario Engine v2 使用受约束启发式情景权重做覆盖优化；不覆盖 TPB，不计算 EV/ROI，不改变推荐金额，不使用用户输入。",
        "",
        "### S1-S6 原始概率与 v2 权重",
    ]
    probability_rows = scenario_probability_weight_rows(scenario)
    if not probability_rows:
        lines.append("暂无情景概率数据。")
    else:
        for row in probability_rows:
            lines.append(f"- {row['情景']}：原始概率 {row['原始概率']}；v2 权重 {row['v2 权重']}")

    lines.extend([
        "",
        "### 风险面",
        "",
    ])
    for row in scenario_risk_surface_rows(scenario):
        lines.append(f"- {row['风险面']}：{row['等级']}（{row['数值']}）")
    lines.extend([
        "",
        "### 覆盖图",
        "",
    ])
    for row in scenario_coverage_map_rows(scenario):
        lines.append(f"- {row['覆盖类型']}：{row['情景']}；{row['说明']}")

    mapping = scenario.get("scenario_market_mapping") or {}
    lines.extend(["", "### 情景与盘口映射", ""])
    for code, name in [
        ("S1", "Strong Favorite Win"),
        ("S2", "Narrow Favorite Win"),
        ("S3", "Draw"),
        ("S4", "Upset Win"),
        ("S5", "Low Scoring Match"),
        ("S6", "High Variance Match"),
    ]:
        item = mapping.get(code) or {}
        lines.append(
            f"- {_scenario_name_cn(code, name)}：受益盘口 {', '.join(item.get('benefits') or ['-'])}；"
            f"失败盘口 {', '.join(item.get('fails') or ['-'])}；对冲关系：{item.get('hedge', '-')}"
        )

    lines.extend([
        "",
        "### 情景到组合的解释映射",
        "",
    ])
    portfolio_mapping = scenario.get("portfolio_mapping_explanation") or {}
    for label, key in [
        ("主推荐覆盖", "main_position_coverage"),
        ("防守覆盖", "defensive_position_coverage"),
        ("高波动覆盖", "tail_exposure"),
    ]:
        item = portfolio_mapping.get(key) or {}
        lines.append(f"- {label}：{item.get('scenario', '-')}；{item.get('explanation', '-')}")

    lines.extend([
        "",
        "### 情景覆盖效率分",
        "",
        f"- 覆盖效率分：{format_value(scenario.get('coverage_efficiency_score'))} / 100",
    ])
    return lines


def format_scenario_optimization_v2_lines(scenario_engine):
    scenario = scenario_engine or {}
    optimization = scenario.get("scenario_optimization_v2") or {}
    if not optimization:
        return [
            "## 情景覆盖优化层 v2",
            "",
            "暂无情景覆盖优化层 v2 输出。",
        ]

    lines = [
        "## 情景覆盖优化层 v2",
        "",
        "该层只做受约束启发式覆盖优化：不计算 EV/ROI，不做盈利最大化，不使用用户输入，不覆盖 TPB，不改变推荐金额。",
        "",
        "### 覆盖优化目标",
        "",
    ]
    objective = optimization.get("objective") or {}
    lines.extend([
        f"- 类型：{objective.get('type', 'bounded deterministic heuristic')}",
        f"- 最大化：{', '.join(objective.get('maximize') or ['-'])}",
        f"- 最小化：{', '.join(objective.get('minimize') or ['-'])}",
        "",
        "### 系统推荐投注组合",
        "",
    ])
    for title, key in [
        ("主覆盖组合", "primary_coverage_set"),
        ("防守覆盖组合", "defensive_coverage_set"),
        ("高波动覆盖组合", "tail_coverage_set"),
    ]:
        lines.append(f"#### {title}")
        rows = optimization.get(key) or []
        if not rows:
            lines.append("- 暂无。")
        for leg in rows:
            display = portfolio_leg_display(leg)
            lines.append(
                f"- {display['中文投注描述']}｜盘口：{display['对应盘口']}｜理由：{display['理由']}｜情景依赖：{display['情景依赖']}"
            )

    lines.extend([
        "",
        "### 情景覆盖图 v2",
        "",
    ])
    for item in optimization.get("scenario_coverage_map_v2") or []:
        lines.append(
            f"- {_scenario_name_cn(item.get('code', '-'), item.get('name'))}："
            f"权重 {percent(item.get('weight', 0))}；覆盖 {percent(item.get('coverage_score', 0))}；"
            f"覆盖组合 {', '.join(item.get('covered_by') or ['-'])}"
        )

    lines.extend([
        "",
        "### 风险分布面",
        "",
    ])
    for item in optimization.get("risk_distribution_surface") or []:
        lines.append(
            f"- {_scenario_name_cn(item.get('code', '-'), item.get('name'))}："
            f"风险暴露 {format_value(item.get('risk_exposure'))}；冗余 {format_value(item.get('redundancy'))}"
        )

    lines.extend([
        "",
        "### 覆盖效率分 v2",
        "",
        f"- {format_value(optimization.get('coverage_efficiency_score_v2'))} / 100",
        "",
        "说明：覆盖效率 v2 = 情景覆盖 /（风险暴露 + 冗余），是可解释的受约束覆盖评分，不是 EV/ROI 或收益优化。",
    ])
    return lines


def format_model_explanation_lines(scenario_engine):
    methodology = (scenario_engine or {}).get("methodology") or {}
    lines = [
        "## 模型方法透明层",
        "",
        methodology.get("disclaimer") or "模型方法透明层只展示计算说明，不参与任何模型计算。",
        "",
        "### 市场结构计算方法",
        "",
    ]
    methods = methodology.get("market_structure_methods") or {}
    for key in ["directional_strength", "market_conflict_index", "efficiency_score", "volatility_index"]:
        item = methods.get(key) or {}
        lines.append(f"- {item.get('name', key)}")
        lines.append(f"  - 输入：{', '.join(item.get('inputs') or ['-'])}")
        lines.append(f"  - 逻辑：{item.get('logic', '-')}")
        thresholds = item.get("thresholds") or {}
        if thresholds:
            lines.append("  - 阈值：" + "；".join(f"{label}={value}" for label, value in thresholds.items()))

    scenario_method = methodology.get("scenario_probability_derivation") or {}
    weighting_method = methodology.get("scenario_weighting_method_v2") or {}
    mapping_method = methodology.get("scenario_mapping_method") or {}
    coverage_method = methodology.get("coverage_mapping_logic") or {}
    optimization_method = methodology.get("coverage_optimization_v2") or {}
    lines.extend([
        "",
        "### 情景概率推导方法",
        "",
        f"- 原则：{scenario_method.get('principle', '-')}",
        f"- 输入：{', '.join(scenario_method.get('inputs') or ['-'])}",
        f"- 逻辑：{scenario_method.get('logic', '-')}",
        f"- 禁止：{', '.join(scenario_method.get('forbidden') or ['-'])}",
        "",
        "### 情景权重函数 v2",
        "",
        f"- 原则：{weighting_method.get('principle', '-')}",
        f"- 公式：{weighting_method.get('formula', '-')}",
        f"- 约束：{', '.join(weighting_method.get('constraints') or ['-'])}",
        f"- 禁止：{', '.join(weighting_method.get('forbidden') or ['-'])}",
        "",
        "### 情景映射方法",
        "",
        mapping_method.get("logic", "-"),
        "",
        "### 覆盖映射逻辑",
        "",
        f"- 主覆盖：{coverage_method.get('primary_coverage', '-')}",
        f"- 防守覆盖：{coverage_method.get('defensive_coverage', '-')}",
        f"- 高波动覆盖：{coverage_method.get('tail_coverage', '-')}",
        f"- 覆盖效率：{coverage_method.get('coverage_efficiency_score', '-')}",
        f"- 覆盖效率 v2：{coverage_method.get('coverage_efficiency_score_v2', '-')}",
        "",
        "### 覆盖优化引擎 v2",
        "",
        f"- 类型：{optimization_method.get('type', '-')}",
        f"- 禁止：{', '.join(optimization_method.get('forbidden') or ['-'])}",
        "",
        "### 审计防线",
        "",
    ])
    for guard in methodology.get("audit_guards") or []:
        lines.append(f"- {guard}")
    return lines


def format_system_portfolio_lines(market_intelligence, scenario_engine=None, match=None):
    scenario = scenario_engine or {}
    lines = [
        "## 系统推荐组合明细（非决策入口）",
        "",
        "本区是 Portfolio 明细，不是新的决策入口；FINAL DECISION BLOCK 仍是唯一压缩决策视图。",
        "系统推荐投注组合 = TPB 锚点 + 市场结构 + 受约束情景权重综合生成。用户实盘输入不参与系统组合、推荐或排序。",
        "Portfolio Priority v2：主覆盖（TPB aligned） -> 波胆策略（Correct Score Layer） -> 防守覆盖 -> 高波动覆盖。",
        "",
    ]
    for row in system_portfolio_display_rows(scenario, match=match, market_intelligence=market_intelligence):
        lines.append(
            f"- {row['组合类型']}：{row['中文投注描述']}｜盘口：{row['对应盘口']}｜理由：{row['理由']}｜情景依赖：{row['情景依赖']}"
        )
    lines.extend([
        "",
        "### 波胆策略层（Correct Score Strategy v2.2 / High Variance Strategy Layer）",
        "",
        "说明：波胆是高熵、高方差、高信息密度市场，用于表达情景波动结构，不作为 EV/ROI 或收益优化。",
        "",
    ])
    for row in correct_score_strategy_rows(match, market_intelligence, scenario):
        lines.append(
            f"- {row['波胆层级']}：{row['中文投注描述']}｜盘口：{row['对应盘口']}｜理由：{row['理由']}｜情景依赖：{row['情景依赖']}"
        )
    return lines


def format_user_portfolio_lines(user_portfolio):
    comparison = user_portfolio or {}
    lines = [
        "## 6. Execution Layer（用户执行层）",
        "",
        "客户执行层仅用于记录实盘输入、执行价格对比和人工复盘；不参与 TPB、系统推荐、系统排序或推荐金额。",
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
    *,
    probabilities=None,
    scores=None,
    rating=None,
    api_football_data=None,
    value_analysis=None,
    betting_opinion=None,
    portfolio_summary=None,
    actual_odds=None,
    user_portfolio=None,
    market_intelligence=None,
    scenario_engine=None,
):
    lines = [
        f"# {match['display_name']} 分析报告",
        "",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        *format_fixture_lines(api_football_data, match),
        "",
        *format_final_decision_block_lines(
            betting_opinion,
            portfolio_summary,
            odds,
            match,
            market_intelligence,
            scenario_engine,
        ),
        "",
        *format_system_portfolio_lines(market_intelligence, scenario_engine, match),
        "",
        *format_model_explanation_lines(scenario_engine),
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
