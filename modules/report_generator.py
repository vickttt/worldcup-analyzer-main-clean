from datetime import datetime
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from modules.market_utils import identify_handicap_center, identify_total_center, parse_handicap_value, safe_float
from modules.pregame_content import static_recent_form_for, team_cn
from modules.probability_base import true_probability_base
from modules.venue_utils import venue_city_for


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


def _score_to_number(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("%", "")
    if "/" in text:
        text = text.split("/", 1)[0].strip()
    try:
        return float(text)
    except ValueError:
        return None


def _metric_number_text(value):
    number = _score_to_number(value)
    if number is None:
        return "-"
    return f"{number:.0f} / 100"


def _direction_strength_number(metrics):
    value = (
        metrics.get("directional_strength_score")
        or metrics.get("direction_score")
        or metrics.get("signal_strength")
    )
    number = _score_to_number(value)
    if number is not None:
        return number
    return {
        "Strong": 80,
        "Medium": 50,
        "Weak": 20,
        "强": 80,
        "中": 50,
        "弱": 20,
    }.get(str(metrics.get("directional_strength")), None)


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
        "SS": "Signal Strength",
        "alignment": "情景对齐",
        "RSI": "RSI",
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


def correct_score_top_signal_row(match=None, market_intelligence=None, scenario_engine=None):
    rows = correct_score_strategy_rows(match, market_intelligence, scenario_engine)
    for row in rows:
        if row.get("波胆层级") == "主波胆":
            return row
    return rows[0] if rows else {
        "波胆层级": "暂无",
        "中文投注描述": "暂无波胆信号",
        "对应盘口": "波胆 / Correct Score",
        "理由": "暂无可用波胆结构。",
        "情景依赖": "-",
    }


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
            "Lite 权重": percent(weight.get("weight", 0)),
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


RISK_MAP_LABEL_CN = {
    "tpb_uncertainty_concentration": "TPB 不确定性集中",
    "market_disagreement_zones": "市场分歧区",
    "scenario_volatility_clustering": "情景波动聚集",
    "draw_pressure_zones": "平局压力区",
    "upset_pressure_zones": "冷门压力区",
}

RISK_DECOMPOSITION_LABEL_CN = {
    "directional_risk": "方向风险",
    "volatility_risk": "波动风险",
    "market_conflict_risk": "盘口冲突风险",
    "tail_risk": "尾部风险",
}


def risk_surface_v3_map_rows(scenario_engine):
    risk_map = (scenario_engine or {}).get("structural_risk_map") or {}
    rows = []
    for key, label in RISK_MAP_LABEL_CN.items():
        item = risk_map.get(key) or {}
        rows.append({
            "结构风险区": label,
            "分数": f"{format_value(item.get('score'))} / 100",
            "等级": _level_cn(item.get("level")),
            "说明": item.get("explanation", "-"),
        })
    return rows


def risk_decomposition_v3_rows(scenario_engine):
    decomposition = (scenario_engine or {}).get("risk_decomposition") or {}
    rows = []
    for key, label in RISK_DECOMPOSITION_LABEL_CN.items():
        item = decomposition.get(key) or {}
        rows.append({
            "风险类型": label,
            "分数": f"{format_value(item.get('score'))} / 100",
            "等级": _level_cn(item.get("level")),
            "说明": item.get("explanation", "-"),
        })
    return rows


def risk_score_v3_summary(scenario_engine):
    score = (scenario_engine or {}).get("risk_score_v3") or {}
    components = score.get("components") or {}
    return {
        "RSI": _level_cn(score.get("level")),
        "RSS": _level_cn(score.get("level")),
        "等级": _level_cn(score.get("level")),
        "公式": score.get("formula", "-"),
        "组件": (
            f"市场分歧 {format_value(components.get('market_disagreement'))} / "
            f"波动压力 {format_value(components.get('volatility_pressure'))} / "
            f"尾部密度 {format_value(components.get('tail_density'))} / "
            f"情景离散 {format_value(components.get('scenario_dispersion'))}"
        ),
        "说明": score.get("disclaimer", "RSI 是 Low / Medium / High 结构风险索引，不是 EV/ROI/optimizer。"),
    }


def market_structure_numeric_rows(market_intelligence):
    metrics = (market_intelligence or {}).get("metrics") or {}
    return [
        {
            "指标": "Direction Strength",
            "数值": _metric_number_text(_direction_strength_number(metrics)),
            "说明": "TPB 集中度 + 盘口偏差",
        },
        {
            "指标": "Market Agreement",
            "数值": _metric_number_text(metrics.get("market_agreement_score")),
            "说明": "多市场一致性指数",
        },
        {
            "指标": "Volatility Pressure",
            "数值": _metric_number_text(metrics.get("volatility_pressure_score")),
            "说明": "波胆 + 平局 + odds spread",
        },
    ]


def _scenario_projection_meaning(code, match=None, market_intelligence=None):
    metrics = (market_intelligence or {}).get("metrics") or {}
    favorite = metrics.get("favorite_label") or _match_team_label(match, "home")
    underdog = _match_team_label(match, "away")
    meanings = {
        "S1": f"{favorite} 主路径更清晰，常见阅读为 1:0、2:0 这类热门获胜比分区间。",
        "S2": f"{favorite} 小胜路径，通常对应一球优势或轻让球覆盖，不代表大胜确定性。",
        "S3": "平局路径，表示比赛可能进入低节奏、僵持或主方向无法拉开差距的状态。",
        "S4": f"{underdog} 冷门路径，表示弱势方反击、定位球或主队失误导致方向反转的风险。",
        "S5": "低比分路径，通常对应小球、节奏慢、进攻效率下降或双方谨慎开局。",
        "S6": "高波动路径，表示大比分、连续进球或尾部波胆的概率解释空间增加。",
    }
    return meanings.get(code, "用于解释本场概率空间中的结构路径。")


def scenario_projection_table_rows(scenario_engine, match=None, market_intelligence=None):
    rows = []
    for row in scenario_probability_weight_rows(scenario_engine):
        scenario_text = str(row.get("情景", ""))
        code = scenario_text.split(" ", 1)[0] if scenario_text else "-"
        probability = row.get("原始概率", "-")
        rows.append({
            "Scenario": code,
            "描述": SCENARIO_NAME_CN.get(code, scenario_text.replace(code, "", 1).strip() or "-"),
            "概率": probability,
            "本场含义": _scenario_projection_meaning(code, match, market_intelligence),
        })
    return rows


def system_semantic_alignment_rows():
    return [
        {
            "层 / 指标": "TPB",
            "统一语义": "probability anchor",
            "真实作用": "提供主胜 / 平局 / 客胜三项概率坐标，不被其他层覆盖。",
        },
        {
            "层 / 指标": "Scenario",
            "统一语义": "bounded structural weighting layer",
            "真实作用": "提供受约束情景权重，用于组合构建、排序调整和风险估计。",
        },
        {
            "层 / 指标": "Portfolio",
            "统一语义": "coverage layer",
            "真实作用": "展示主覆盖、防守覆盖、高波动覆盖，不直接生成最终金额。",
        },
        {
            "层 / 指标": "Ranking",
            "统一语义": "ordering layer, not final execution instruction",
            "真实作用": "对投注结构排序；最终是否执行仍取决于 stake decision layer。",
        },
        {
            "层 / 指标": "RSI",
            "统一语义": "risk adjustment factor",
            "真实作用": "不直接输入 stake；通过 Risk Adjustment 改变 Investment Score，从而间接影响资金分配。",
        },
        {
            "层 / 指标": "Stake",
            "统一语义": "final execution mapping",
            "真实作用": "只由 Investment Score 档位映射得出。",
        },
        {
            "层 / 指标": "Market Conflict",
            "统一语义": "inverse of market agreement score",
            "真实作用": "当前 active model 使用 100 - market_agreement_score；legacy conflict function 已废弃且不使用。",
        },
        {
            "层 / 指标": "Correct Score",
            "统一语义": "high variance structural signal layer, not execution signal",
            "真实作用": "作为高波动结构信号展示，不进入 Investment Score、Ranking Score 或 stake mapping。",
        },
    ]


def system_semantic_alignment_sections():
    return [
        {
            "标题": "Scenario",
            "简短说明": "受约束情景权重层。",
            "详细说明": "Scenario 用于组合构建、排序调整和风险估计；不覆盖 TPB，不使用用户输入，不计算 EV/ROI。",
        },
        {
            "标题": "Portfolio",
            "简短说明": "覆盖结构层。",
            "详细说明": "Portfolio 展示主覆盖、防守覆盖、高波动覆盖，用于理解覆盖空间，不直接生成最终金额。",
        },
        {
            "标题": "Stake",
            "简短说明": "最终执行金额映射。",
            "详细说明": "Stake 只由 Investment Score 档位映射得出；RSI 不直接输入 stake mapping。",
        },
        {
            "标题": "Ranking",
            "简短说明": "结构排序层。",
            "详细说明": "Ranking 对系统投注结构排序，帮助阅读优先级；最终执行仍取决于 Investment Score 到 Stake 的映射。",
        },
        {
            "标题": "RSI",
            "简短说明": "风险调整因子。",
            "详细说明": "RSI 表示结构风险压力，较高时会压低 Investment Score 的风险调整项，并间接降低推荐金额；它不是单独下注信号。",
        },
        {
            "标题": "TPB",
            "简短说明": "概率锚点。",
            "详细说明": "TPB 提供主胜 / 平局 / 客胜三项概率坐标，不被 Scenario、Market 或用户输入覆盖。",
        },
        {
            "标题": "Market Conflict",
            "简短说明": "市场一致性的反向指标。",
            "详细说明": "当前 active model 使用 100 - market_agreement_score；legacy conflict function 已废弃且不使用。",
        },
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


def system_portfolio_top_rows(scenario_engine, match=None, market_intelligence=None):
    sets = _optimization_sets(scenario_engine)
    rows = []
    picks = [
        ("主覆盖", sets.get("Primary Coverage Set") or []),
        ("防守覆盖", sets.get("Defensive Coverage Set") or []),
        ("高波动覆盖", sets.get("Tail Coverage Set") or []),
    ]
    for label, legs in picks:
        display = portfolio_leg_display_rows(
            legs[:1],
            match=match,
            market_intelligence=market_intelligence,
            scenario_engine=scenario_engine,
        )
        if display:
            row = display[0]
            rows.append({
                "组合类型": label,
                "中文投注描述": row.get("中文投注描述", "-"),
                "对应盘口": row.get("对应盘口", "-"),
                "理由": row.get("理由", "-"),
            })
    return rows[:3]


def _score_rows_for_ranking(position, match=None, market_intelligence=None, scenario_engine=None):
    rows = correct_score_strategy_rows(match, market_intelligence, scenario_engine)
    if position == "Primary Coverage Set":
        return [row for row in rows if row["波胆层级"] == "主波胆"][:3]
    if position == "Defensive Coverage Set":
        return [row for row in rows if row["波胆层级"] == "结构波胆"][:3]
    if position == "Tail Coverage Set":
        return [row for row in rows if row["波胆层级"] == "高波动波胆"][:3]
    return []


def _scenario_basis_text(scenario_engine, codes):
    weights = {
        item.get("code"): item.get("weight")
        for item in ((scenario_engine or {}).get("scenario_weights") or [])
    }
    parts = []
    for code in codes:
        value = weights.get(code)
        parts.append(f"{code} {percent(value)}" if value is not None else code)
    return " / ".join(parts) or "-"


def _ranking_display_reason(position):
    if position == "Primary Coverage Set":
        return "主方向与热门小胜路径最匹配，用于展示主路径覆盖。"
    if position == "Defensive Coverage Set":
        return "平局和低比分路径仅作为防守覆盖，不是独立主推荐。"
    if position == "Tail Coverage Set":
        return "高波动尾部存在，但仅作观察，不作为主推荐。"
    return "结构排序展示，不代表最终下注指令。"


def _compact_legs_for_ranking(position, legs):
    if position == "Primary Coverage Set":
        handicap = [leg for leg in legs if "-0.5" in str(leg.get("中文投注描述", ""))]
        return handicap[:1] or (legs[1:2] if len(legs) > 1 else legs[:1])
    if position == "Defensive Coverage Set":
        draw = [leg for leg in legs if "平局" in str(leg.get("中文投注描述", ""))]
        return draw[:1] or (legs[2:3] if len(legs) > 2 else legs[1:2] if len(legs) > 1 else legs[:1])
    if position == "Tail Coverage Set":
        return []
    return legs[:1]


def system_ranking_display_rows(portfolio, scenario_engine=None, match=None, market_intelligence=None):
    rows = []
    sets = _optimization_sets(scenario_engine)
    ranking_by_position = {
        item.get("position"): item
        for item in ((portfolio or {}).get("ranking") or [])
    }
    display_order = [
        ("Primary Coverage Set", "主路径覆盖", ["S1", "S2"], "S1/S2"),
        ("Defensive Coverage Set", "防守覆盖", ["S3", "S5"], "S3/S5"),
        ("Tail Coverage Set", "高波动观察", ["S6", "S4"], "S6/S4"),
    ]
    for position, label, scenario_codes, scenario_label in display_order:
        item = ranking_by_position.get(position) or {"position": position}
        position = item.get("position", "-")
        legs = portfolio_leg_display_rows(
            sets.get(position) or [],
            match=match,
            market_intelligence=market_intelligence,
            scenario_engine=scenario_engine,
        )
        legs = _compact_legs_for_ranking(position, legs)
        bet_text = "；".join(
            [leg.get("中文投注描述", "-") for leg in legs]
        ) or "无主投注项（仅观察）"
        market_text = "；".join(
            [leg.get("对应盘口", "-") for leg in legs]
        ) or "不作为执行盘口"
        dependency_text = _scenario_basis_text(scenario_engine, scenario_codes)
        score_rows = _score_rows_for_ranking(position, match, market_intelligence, scenario_engine)[:3]
        correct_score_text = "；".join(row.get("中文投注描述", "-") for row in score_rows) or "-"
        rows.append({
            "覆盖定位": label,
            "主投注项": bet_text,
            "盘口": market_text,
            "附属波胆观察（非推荐）": correct_score_text,
            "本场解释": _ranking_display_reason(position),
            "情景依据": dependency_text,
            "情景": scenario_label,
        })
    return rows


def correct_score_limited_rows(match=None, market_intelligence=None, scenario_engine=None):
    rows = correct_score_strategy_rows(match, market_intelligence, scenario_engine)
    grouped = []
    grouped.extend([row for row in rows if row.get("波胆层级") == "主波胆"][:2])
    grouped.extend([row for row in rows if row.get("波胆层级") == "结构波胆"][:2])
    grouped.extend([row for row in rows if row.get("波胆层级") == "高波动波胆"][:1])
    return grouped


SCENARIO_CODES = ["S1", "S2", "S3", "S4", "S5", "S6"]
def _row_text(row):
    return " ".join(str(value) for value in (row or {}).values() if value is not None)


def _scenario_from_text(text):
    text = str(text or "")
    explicit = re.findall(r"\bS[1-6]\b", text)
    if explicit:
        return explicit[0]
    if "平局" in text or "Draw" in text or "0:0" in text or "1:1" in text:
        return "S3"
    if "冷门" in text or "Upset" in text or "0:1" in text:
        return "S4"
    if "小球" in text or "Under" in text or "低比分" in text:
        return "S5"
    if "大球" in text or "Over" in text or "高波动" in text or "2:2" in text or "3:2" in text or "3:1" in text:
        return "S6"
    if "让球" in text or "-0.5" in text or "小胜" in text:
        return "S2"
    if "独赢" in text or "主覆盖" in text or "胜平负" in text:
        return "S1"
    return "-"


def _scenario_for_exposure(row):
    dependency = (row or {}).get("情景依赖")
    if dependency:
        return _scenario_from_text(dependency)
    return _scenario_from_text(_row_text(row))


def _with_exposure_columns(row, scenario):
    output = dict(row or {})
    output["Scenario"] = scenario
    return output


def _build_scenario_exposure_summary(sections):
    counts = {code: 0 for code in SCENARIO_CODES}
    active = {name: [] for name, _rows in sections}
    for source, rows in sections:
        for row in rows or []:
            scenario = _scenario_for_exposure(row)
            active[source].append(_with_exposure_columns(row, scenario))
            if scenario in counts:
                counts[scenario] += 1

    exposure_map = [
        {
            "Scenario": code,
            "暴露数量": counts[code],
            "说明": "仅统计，不改变排序",
        }
        for code in SCENARIO_CODES
    ]
    return active, exposure_map


def scenario_exposure_control_display(
    market_intelligence=None,
    scenario_engine=None,
    match=None,
    portfolio_summary=None,
):
    scenario = scenario_engine or {}
    portfolio = (
        scenario.get("system_optimized_portfolio_v2")
        or ((market_intelligence or {}).get("system_portfolio") or {})
        or portfolio_summary
        or {}
    )
    portfolio_rows = system_portfolio_display_rows(
        scenario,
        match=match,
        market_intelligence=market_intelligence,
    )
    ranking_rows = system_ranking_display_rows(
        portfolio,
        scenario,
        match=match,
        market_intelligence=market_intelligence,
    )
    correct_score_rows = correct_score_limited_rows(match, market_intelligence, scenario)
    active, exposure_map = _build_scenario_exposure_summary([
        ("Portfolio", portfolio_rows),
        ("Ranking", ranking_rows),
        ("Correct Score", correct_score_rows),
    ])
    active_portfolio = active.get("Portfolio", [])
    active_ranking = []
    for row in active.get("Ranking", [])[:3]:
        display_row = dict(row)
        display_row.pop("Scenario", None)
        active_ranking.append(display_row)
    top_rows = [
        {
            "组合类型": row.get("组合类型", "-"),
            "中文投注描述": row.get("中文投注描述", "-"),
            "对应盘口": row.get("对应盘口", "-"),
            "理由": row.get("理由", "-"),
            "Scenario": row.get("Scenario", "-"),
        }
        for row in active_portfolio
        if row.get("中文投注描述") != "暂无"
    ][:3]
    return {
        "portfolio_rows": active_portfolio,
        "portfolio_top_rows": top_rows,
        "ranking_rows": active_ranking,
        "correct_score_rows": active.get("Correct Score", []),
        "exposure_map_rows": exposure_map,
        "removed_bets_rows": [],
    }


def markdown_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "-")) for header in headers) + " |")
    return lines


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
    venue_city = venue_city_for(venue_name, venue_city)
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
            f"结构观察 - 让球盘口中心（仅市场描述）：{center.get('center_label')}",
            f"TPB 覆盖说明（非推荐信号）：{center.get('coverage_label')}",
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
            f"结构观察 - 总进球盘口中心（仅市场描述）：{center.get('center_label')}",
            f"市场倾向（非推荐信号）：{center.get('market_bias')}",
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


def _is_observation_mode(portfolio_summary):
    stake_amount = _recommended_stake_amount(portfolio_summary)
    if stake_amount is not None:
        return stake_amount <= 0
    eligible = _portfolio_eligible(portfolio_summary)
    return eligible is False


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
        f"- Signal Strength：{opinion.get('betting_confidence', opinion.get('confidence', 50))} / 100",
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
    rss = risk_score_v3_summary(scenario)
    scenario_rows = scenario_projection_table_rows(scenario, match=match, market_intelligence=market_intelligence)
    top_score = correct_score_top_signal_row(match, market_intelligence, scenario)
    score = portfolio_summary.get("decision_score")
    if score is None:
        score = portfolio_summary.get("score")
    investment_breakdown = ((portfolio_summary or {}).get("investment_breakdown") or {})
    exposure_control = scenario_exposure_control_display(
        market_intelligence=market_intelligence,
        scenario_engine=scenario,
        match=match,
        portfolio_summary=portfolio_summary,
    )

    lines = [
        "## 最终决策区（FINAL DECISION BLOCK）",
        "",
        "### System Semantic Alignment Layer",
        "",
    ]
    for row in system_semantic_alignment_sections():
        lines.append(
            f"<details><summary>{row['标题']}｜{row['简短说明']}</summary>"
            f"{row['详细说明']}</details>"
        )
    lines.extend([
        "",
        "### 1. TPB Summary",
        "",
        f"- 主方向：{metrics.get('favorite_label') or opinion.get('match_direction') or opinion.get('match_winner', '-')}（{format_value(metrics.get('favorite_probability'))}%）｜TPB：主胜 {percent(probabilities.get('home_win', 0)) if probabilities else '-'} / 平局 {percent(probabilities.get('draw', 0)) if probabilities else '-'} / 客胜 {percent(probabilities.get('away_win', 0)) if probabilities else '-'}",
        f"- Signal Strength / 推荐金额：{opinion.get('betting_confidence', opinion.get('confidence', 50))} / 100；{_recommended_stake_text(portfolio_summary)}",
        "- Signal Strength = (max(TPB probabilities) - second max) × 100。",
        "- 推荐金额 = Investment Score → 固定区间映射。",
        "",
    ])
    lines.extend([
        "### 2. Market Structure（3指标）",
        "",
    ])
    for row in market_structure_numeric_rows(market_intelligence):
        lines.append(f"- {row['指标']}：{row['数值']}｜{row['说明']}")
    lines.extend([
        "",
        "### 3. Scenario Projection（简化版）",
        "",
        "- Scenario = 受约束结构权重层；用于 portfolio construction、ranking adjustment、risk estimation，不覆盖 TPB，不计算 EV/ROI。",
        "",
    ])
    if scenario_rows:
        lines.extend(markdown_table(["Scenario", "描述", "概率", "本场含义"], scenario_rows))
    else:
        lines.append("暂无情景概率与权重数据。")
    lines.extend([
        "",
        "### 4. Investment Score（2因子）",
        "",
        f"- 输入因素：TPB Edge / Scenario Alignment / Market Conflict / RSI",
        f"- 当前因子读数：TPB Edge + Scenario Alignment {format_value(investment_breakdown.get('signal'))} / 100；Risk Adjustment {format_value(investment_breakdown.get('risk_adjustment'))}；RSI {rss['RSI']}",
        f"- Investment Score：{format_value(score)} / 100",
        "- 解释：Investment Score 是多因子加权结果；TPB Edge、Scenario Alignment、Market Conflict 与 RSI 共同解释当前投资分。",
        "- RSI 是 risk adjustment factor：它不直接输入 stake mapping，但会通过 Investment Score 间接影响推荐金额。",
        "- 低分不下注：当 Investment Score 落入低分档位，推荐金额映射为 0 元。",
        "",
        "### 5. Portfolio（coverage only）",
        "",
        f"Portfolio 只保留 coverage structure，不参与 Ranking Score；CQS：{format_value(optimization.get('coverage_quality_score', optimization.get('coverage_efficiency_score_v2')))} / 100。",
        "",
    ])
    for row in exposure_control["portfolio_top_rows"]:
        lines.append(
            f"- {row['组合类型']}：{row['中文投注描述']}｜盘口：{row['对应盘口']}｜理由：{row['理由']}｜Scenario：{row.get('Scenario', '-')}"
        )
    lines.extend([
        "",
        "### 6. 组合覆盖结构（非投注推荐排序）",
        "",
        "本区展示主路径覆盖、防守覆盖和高波动观察三类结构。它用于理解系统如何覆盖主要比赛路径和风险路径，不等于逐个投注项的推荐强弱。附属波胆只作为结构观察，不构成独立推荐。",
        "",
    ])
    ranking_rows = exposure_control["ranking_rows"]
    if not ranking_rows:
        lines.append("- 暂无组合覆盖结构。")
    else:
        for row in ranking_rows:
            lines.append(
                f"- {row['覆盖定位']}：{row['主投注项']}｜盘口：{row['盘口']}｜附属波胆观察（非推荐）：{row.get('附属波胆观察（非推荐）', '-')}｜本场解释：{row['本场解释']}｜情景依据：{row.get('情景依据', '-')}｜情景：{row.get('情景', '-')}"
            )
    lines.extend([
        "",
        "### 7. RSI Risk",
        "",
        f"- RSI：{rss['RSI']}｜{rss['组件']}",
        "- RSI 表示结构风险压力；越高说明情景分散、尾部或市场分歧压力越大。它不是单独下注信号，会通过 Investment Score 间接影响推荐金额。",
        "",
        "### 8. High Variance Structural Signal（波胆）",
        "",
        "- Correct Score 是高波动结构信号，不是执行信号；这里只保留一个最高权重提示。",
        f"- 高波动结构信号：{top_score['中文投注描述']}｜盘口：{top_score['对应盘口']}｜情景依赖：{top_score['情景依赖']}",
        "",
        "重点风险路径：结构不确定性 + 情景分散 + 高波动尾部风险",
    ])
    return lines


def format_tpb_coverage_lines(betting_opinion):
    opinion = betting_opinion or {}
    lines = [
        "## TPB 覆盖说明",
        "",
        f"结构观察（非推荐信号）：{opinion.get('coverage_candidate') or '暂无 TPB 覆盖说明'}",
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
        f"结构观察 - 总进球盘口中心（仅市场描述）：{opinion.get('total_center', '-')}",
        "",
        f"市场倾向（非推荐信号）：{opinion.get('goals_market_bias', opinion.get('over_under_reason', '-'))}",
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
        "Lite v1 市场结构只保留 3 个指标：方向强度、市场一致性、波动压力；不使用用户输入，不计算 EV/ROI。",
        "",
    ]
    for row in market_structure_numeric_rows(market_intelligence):
        lines.append(f"- {row['指标']}：{row['数值']}｜{row['说明']}")
    if metrics.get("favorite_label"):
        lines.append(f"- TPB baseline 主方向：{metrics.get('favorite_label')}（{format_value(metrics.get('favorite_probability'))}%）")
    if metrics.get("explanation"):
        lines.extend(["", f"说明：{metrics.get('explanation')}"])
    return lines


def format_scenario_engine_lines(scenario_engine):
    scenario = scenario_engine or {}
    lines = [
        "## 3. Scenario Projection（Lite v1）",
        "",
        scenario.get("disclaimer")
        or "Scenario Projection Lite v1 使用 TPB + Market signal projection；不覆盖 TPB，不计算 EV/ROI，不改变推荐金额，不使用用户输入。",
        "",
        "### S1-S6 概率与本场含义",
    ]
    probability_rows = scenario_probability_weight_rows(scenario)
    if not probability_rows:
        lines.append("暂无情景概率数据。")
    else:
        for row in scenario_projection_table_rows(scenario):
            lines.append(f"- {row['Scenario']} {row['描述']}：概率 {row['概率']}；{row['本场含义']}")

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
        "### Coverage Quality Score",
        "",
        f"- CQS：{format_value(scenario.get('coverage_quality_score', scenario.get('coverage_efficiency_score')))} / 100",
    ])
    return lines


def format_scenario_optimization_v2_lines(scenario_engine):
    scenario = scenario_engine or {}
    optimization = scenario.get("scenario_optimization_v2") or {}
    if not optimization:
        return [
            "## Portfolio Coverage（Lite v1）",
            "",
            "暂无 Portfolio Coverage 输出。",
        ]

    lines = [
        "## Portfolio Coverage（Lite v1）",
        "",
        "该层只展示 coverage structure；Ranking Score 独立使用 SS + Scenario Alignment - RSI。",
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
        "### Coverage Quality Score",
        "",
        f"- {format_value(optimization.get('coverage_quality_score', optimization.get('coverage_efficiency_score_v2')))} / 100",
        "",
        "说明：CQS = coverage completeness - redundancy；不是 Ranking Score、EV/ROI 或收益优化。",
    ])
    return lines


def format_risk_surface_v3_lines(scenario_engine):
    scenario = scenario_engine or {}
    risk_surface_v3 = scenario.get("risk_surface_v3") or {}
    rss = risk_score_v3_summary(scenario)
    lines = [
        "## RSI Risk（Lite v1）",
        "",
        risk_surface_v3.get("description")
        or "Risk Surface v3 只刻画结构风险，不预测结果，不计算 EV/ROI，不做 optimizer；RSI 可通过 Investment Score 间接影响 stake，不直接输入 stake mapping。",
        "",
        "### RSI 结构风险",
        "",
        f"- RSI：{rss['RSI']}",
        f"- 组件：{rss['组件']}",
        f"- 公式：{rss['公式']}",
        f"- 说明：{rss['说明']}",
        "",
        "### Structural Risk Map",
        "",
    ]
    for row in risk_surface_v3_map_rows(scenario):
        lines.append(
            f"- {row['结构风险区']}：{row['分数']}（{row['等级']}）｜{row['说明']}"
        )
    lines.extend([
        "",
        "### Risk Decomposition",
        "",
    ])
    for row in risk_decomposition_v3_rows(scenario):
        lines.append(
            f"- {row['风险类型']}：{row['分数']}（{row['等级']}）｜{row['说明']}"
        )
    lines.extend([
        "",
        "边界：RSI 是 Low / Medium / High qualitative risk index；不是 EV、ROI、profit maximization、ML training 或 black-box scoring。RSI 不直接输入 stake mapping，但会通过 Investment Score 间接影响资金分配。",
    ])
    return lines


def format_model_explanation_lines(scenario_engine):
    methodology = (scenario_engine or {}).get("methodology") or {}
    lines = [
        "## 模型方法透明层",
        "",
        methodology.get("disclaimer") or "模型方法透明层只展示计算说明，不参与任何模型计算。",
        "",
        "### System Semantic Alignment Layer",
        "",
    ]
    for row in system_semantic_alignment_sections():
        lines.append(
            f"<details><summary>{row['标题']}｜{row['简短说明']}</summary>"
            f"{row['详细说明']}</details>"
        )
    lines.extend([
        "",
        "### 市场结构计算方法",
        "",
    ])
    methods = methodology.get("market_structure_methods") or {}
    for key in ["directional_strength", "market_agreement", "market_conflict_index", "volatility_pressure"]:
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
    risk_method = methodology.get("risk_surface_quantification_v3") or {}
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
        "### Risk Surface Quantification v3 方法",
        "",
        f"- 原则：{risk_method.get('principle', '-')}",
        f"- 输出：{', '.join(risk_method.get('outputs') or ['-'])}",
        f"- RSS 公式：{risk_method.get('rss_formula', '-')}",
        f"- 风险拆解：{', '.join(risk_method.get('risk_decomposition') or ['-'])}",
        f"- 禁止：{', '.join(risk_method.get('forbidden') or ['-'])}",
        "",
        "### 审计防线",
        "",
    ])
    for guard in methodology.get("audit_guards") or []:
        lines.append(f"- {guard}")
    return lines


def format_system_portfolio_lines(market_intelligence, scenario_engine=None, match=None, portfolio_summary=None):
    scenario = scenario_engine or {}
    exposure_control = scenario_exposure_control_display(
        market_intelligence=market_intelligence,
        scenario_engine=scenario,
        match=match,
        portfolio_summary=portfolio_summary,
    )
    lines = [
        "## Portfolio Coverage（coverage only）",
        "",
        "本区只展示 coverage structure，不参与 Ranking Score；FINAL DECISION BLOCK 仍是压缩决策视图。",
        "Lite v1：Portfolio 保留 Primary / Defensive / High Variance Coverage；Ranking 是结构排序层，不是最终执行指令。",
        "",
    ]
    for row in exposure_control["portfolio_rows"]:
        lines.append(
            f"- {row['组合类型']}：{row['中文投注描述']}｜盘口：{row['对应盘口']}｜理由：{row['理由']}｜情景依赖：{row['情景依赖']}｜Scenario：{row.get('Scenario', '-')}"
        )
    lines.extend([
        "",
        "### High Variance Structural Signal（波胆）",
        "",
        "说明：波胆是高波动结构信号，不是执行信号；最多展示 5 个：主波胆 2 个、结构波胆 2 个、高波动波胆 1 个。",
        "",
    ])
    for row in exposure_control["correct_score_rows"]:
        lines.append(
            f"- {row['波胆层级']}：{row['中文投注描述']}｜盘口：{row['对应盘口']}｜理由：{row['理由']}｜情景依赖：{row['情景依赖']}｜Scenario：{row.get('Scenario', '-')}"
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
        *format_system_portfolio_lines(market_intelligence, scenario_engine, match, portfolio_summary),
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
