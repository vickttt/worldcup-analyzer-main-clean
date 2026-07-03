from modules.probability_base import true_probability_base
from modules.model_methodology import build_model_methodology


SCENARIO_TAXONOMY = [
    ("S1", "Strong Favorite Win"),
    ("S2", "Narrow Favorite Win"),
    ("S3", "Draw"),
    ("S4", "Upset Win"),
    ("S5", "Low Scoring Match"),
    ("S6", "High Variance Match"),
]


def _clamp(value, low=0, high=100):
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    return max(low, min(high, number))


def _scenario_label(code):
    return dict(SCENARIO_TAXONOMY).get(code, code)


def _probabilities_from_tpb(tpb):
    probabilities = (tpb or {}).get("probabilities") or {}
    return {
        "home_win": float(probabilities.get("home_win") or 0),
        "draw": float(probabilities.get("draw") or 0),
        "away_win": float(probabilities.get("away_win") or 0),
    }


def _normalize_weights(weights):
    total = sum(max(0, value) for value in weights.values())
    if total <= 0:
        return {code: round(1 / len(SCENARIO_TAXONOMY), 4) for code, _label in SCENARIO_TAXONOMY}
    normalized = {code: max(0, value) / total for code, value in weights.items()}
    rounded = {code: round(value, 4) for code, value in normalized.items()}
    drift = round(1 - sum(rounded.values()), 4)
    if rounded:
        first_key = next(iter(rounded))
        rounded[first_key] = round(rounded[first_key] + drift, 4)
    return rounded


def _scenario_distribution(tpb, metrics):
    probabilities = _probabilities_from_tpb(tpb)
    home = probabilities["home_win"]
    draw = probabilities["draw"]
    away = probabilities["away_win"]
    favorite = max(home, away)
    underdog = min(home, away)
    favorite_edge = max(0, favorite - max(draw, underdog))
    conflict = _clamp(metrics.get("market_conflict_index"), 0, 100) / 100
    efficiency = _clamp(metrics.get("market_efficiency_score"), 0, 100) / 100
    upset_score = _clamp(metrics.get("upset_score"), 0, 100) / 100
    volatility_score = _clamp(metrics.get("volatility_score"), 0, 100) / 100
    tail_density = _clamp(metrics.get("tail_density"), 0, 1)

    weights = {
        "S1": favorite * (0.55 + favorite_edge) * (0.65 + efficiency * 0.35),
        "S2": favorite * (0.35 + conflict * 0.30) * (1 - min(0.4, favorite_edge)),
        "S3": draw * (0.85 + conflict * 0.45),
        "S4": underdog * (0.80 + upset_score * 0.65 + conflict * 0.20),
        "S5": max(0.08, draw * 0.40 + conflict * 0.15 + (1 - volatility_score) * 0.20),
        "S6": max(0.06, volatility_score * 0.45 + tail_density * 0.35 + conflict * 0.20),
    }
    distribution = _normalize_weights(weights)
    return [
        {
            "code": code,
            "name": _scenario_label(code),
            "probability": distribution.get(code, 0),
        }
        for code, _label in SCENARIO_TAXONOMY
    ]


def _level(value, low=0.28, high=0.42):
    if value >= high:
        return "High"
    if value >= low:
        return "Medium"
    return "Low"


def _risk_surface(distribution, metrics):
    probabilities = {item["code"]: item["probability"] for item in distribution}
    tail_risk = probabilities.get("S4", 0) + probabilities.get("S6", 0)
    draw_dependency = probabilities.get("S3", 0)
    upset_exposure = probabilities.get("S4", 0)
    fragility = (
        _clamp(metrics.get("market_conflict_index"), 0, 100) / 100 * 0.45
        + _clamp(metrics.get("volatility_score"), 0, 100) / 100 * 0.35
        + (1 - _clamp(metrics.get("market_efficiency_score"), 0, 100) / 100) * 0.20
    )
    return {
        "tail_risk_concentration": _level(tail_risk),
        "tail_risk_value": round(tail_risk, 4),
        "market_fragility": _level(fragility),
        "market_fragility_value": round(fragility, 4),
        "upset_exposure": _level(upset_exposure, low=0.18, high=0.28),
        "upset_exposure_value": round(upset_exposure, 4),
        "draw_dependency": _level(draw_dependency, low=0.20, high=0.30),
        "draw_dependency_value": round(draw_dependency, 4),
    }


def _coverage_map(distribution):
    ordered = sorted(distribution, key=lambda item: item["probability"], reverse=True)
    primary = ordered[0] if ordered else {"code": "-", "name": "-", "probability": 0}
    defensive = next(
        (item for item in ordered if item["code"] in {"S3", "S4", "S5"} and item["code"] != primary["code"]),
        ordered[1] if len(ordered) > 1 else primary,
    )
    tail = next(
        (item for item in ordered if item["code"] in {"S4", "S6"}),
        ordered[-1] if ordered else primary,
    )
    return {
        "primary_coverage": {
            "scenario": f"{primary['code']}: {primary['name']}",
            "description": "主覆盖路径，代表当前概率空间中权重最高的结构。",
        },
        "defensive_coverage": {
            "scenario": f"{defensive['code']}: {defensive['name']}",
            "description": "防守路径，用于观察平局、冷门或低比分覆盖结构。",
        },
        "tail_optionality": {
            "scenario": f"{tail['code']}: {tail['name']}",
            "description": "尾部路径，只用于识别极端或高方差结构，不放大推荐。",
        },
    }


def _scenario_market_mapping():
    return {
        "S1": {
            "benefits": ["独赢热门方向", "让球热门方向"],
            "fails": ["受让冷门", "平局路径"],
            "hedge": "通常不形成 hedge；需要关注防守覆盖。",
        },
        "S2": {
            "benefits": ["独赢热门方向", "小让球/轻让球"],
            "fails": ["深让球穿盘", "大比分波胆"],
            "hedge": "可与低比分或平局观察形成防守关系。",
        },
        "S3": {
            "benefits": ["平局", "受让方向", "部分低比分路径"],
            "fails": ["单边热门深盘", "强方向波胆"],
            "hedge": "对主方向形成防守覆盖。",
        },
        "S4": {
            "benefits": ["冷门独赢", "受让方向"],
            "fails": ["热门独赢", "热门让球"],
            "hedge": "对热门主路径形成尾部 hedge。",
        },
        "S5": {
            "benefits": ["小球", "低比分波胆"],
            "fails": ["大球", "高比分路径"],
            "hedge": "可防守节奏偏慢的比赛结构。",
        },
        "S6": {
            "benefits": ["大球", "高赔率尾部波胆"],
            "fails": ["低波动小球结构"],
            "hedge": "仅作为尾部可选性观察，不作为主推荐。",
        },
    }


def _coverage_efficiency_score(distribution, risk_surface):
    sorted_probabilities = sorted((item["probability"] for item in distribution), reverse=True)
    top_three = sum(sorted_probabilities[:3])
    redundancy = max(0, sorted_probabilities[0] - sorted_probabilities[1]) if len(sorted_probabilities) > 1 else 0
    risk_concentration = risk_surface.get("tail_risk_value", 0) + risk_surface.get("market_fragility_value", 0)
    score = top_three * 70 + (1 - min(1, risk_concentration / 2)) * 20 + (1 - redundancy) * 10
    return round(_clamp(score, 0, 100))


def _scenario_weights_v2(distribution, metrics):
    base = {item["code"]: item["probability"] for item in distribution}
    direction = _clamp(metrics.get("direction_score"), 0, 100) / 100
    conflict = _clamp(metrics.get("market_conflict_index"), 0, 100) / 100
    efficiency = _clamp(metrics.get("market_efficiency_score"), 0, 100) / 100
    upset = _clamp(metrics.get("upset_score"), 0, 100) / 100
    volatility = _clamp(metrics.get("volatility_score"), 0, 100) / 100
    tail_density = _clamp(metrics.get("tail_density"), 0, 1)

    weighted = {
        "S1": base.get("S1", 0) * (1 + direction * 0.28 + efficiency * 0.18),
        "S2": base.get("S2", 0) * (1 + direction * 0.12 + conflict * 0.16),
        "S3": base.get("S3", 0) * (1 + conflict * 0.22 + volatility * 0.12),
        "S4": base.get("S4", 0) * (1 + upset * 0.30 + conflict * 0.14),
        "S5": base.get("S5", 0) * (1 + (1 - volatility) * 0.18 + conflict * 0.10),
        "S6": base.get("S6", 0) * (1 + volatility * 0.30 + tail_density * 0.20),
    }
    normalized = _normalize_weights(weighted)
    return [
        {
            "code": code,
            "name": _scenario_label(code),
            "weight": normalized.get(code, 0),
            "base_probability": base.get(code, 0),
            "rationale": (
                "Bounded heuristic weight from TPB baseline, Market Structure, "
                "Volatility, Upset Probability, and tail density; no EV/ROI or ML."
            ),
        }
        for code, _label in SCENARIO_TAXONOMY
    ]


def _weight_map(scenario_weights):
    return {item["code"]: item["weight"] for item in scenario_weights or []}


def _portfolio_leg_templates(metrics):
    favorite = metrics.get("favorite_label") or "TPB 主方向"
    return [
        {
            "id": "primary_1x2",
            "name": f"主覆盖：{favorite} 独赢方向",
            "market": "胜平负",
            "selection": favorite,
            "set": "primary",
            "scenario_dependencies": ["S1", "S2"],
            "risk_exposure": 0.25,
            "redundancy": 0.16,
        },
        {
            "id": "primary_handicap",
            "name": f"主覆盖：{favorite} 轻让球方向",
            "market": "亚洲让球",
            "selection": favorite,
            "set": "primary",
            "scenario_dependencies": ["S1", "S2"],
            "risk_exposure": 0.34,
            "redundancy": 0.22,
        },
        {
            "id": "defensive_draw",
            "name": "防守覆盖：平局路径",
            "market": "胜平负",
            "selection": "平局",
            "set": "defensive",
            "scenario_dependencies": ["S3"],
            "risk_exposure": 0.38,
            "redundancy": 0.08,
        },
        {
            "id": "defensive_handicap",
            "name": "防守覆盖：受让/对冲方向",
            "market": "亚洲让球",
            "selection": "受让方向",
            "set": "defensive",
            "scenario_dependencies": ["S3", "S4"],
            "risk_exposure": 0.36,
            "redundancy": 0.18,
        },
        {
            "id": "defensive_under",
            "name": "防守覆盖：低比分/小球路径",
            "market": "大小球",
            "selection": "Under",
            "set": "defensive",
            "scenario_dependencies": ["S2", "S5"],
            "risk_exposure": 0.31,
            "redundancy": 0.14,
        },
        {
            "id": "tail_upset",
            "name": "尾部覆盖：冷门方向",
            "market": "胜平负/受让",
            "selection": "冷门路径",
            "set": "tail",
            "scenario_dependencies": ["S4"],
            "risk_exposure": 0.74,
            "redundancy": 0.04,
        },
        {
            "id": "tail_variance",
            "name": "尾部覆盖：高方差进球路径",
            "market": "大小球/波胆",
            "selection": "高方差路径",
            "set": "tail",
            "scenario_dependencies": ["S6"],
            "risk_exposure": 0.78,
            "redundancy": 0.05,
        },
    ]


def _score_leg(leg, weights):
    coverage = sum(weights.get(code, 0) for code in leg["scenario_dependencies"])
    risk_penalty = leg["risk_exposure"] * 0.22
    redundancy_penalty = leg["redundancy"] * 0.18
    contribution = max(0, coverage * (1 - risk_penalty - redundancy_penalty))
    enriched = dict(leg)
    enriched["coverage_contribution"] = round(contribution, 4)
    enriched["scenario_dependency"] = [
        {
            "code": code,
            "name": _scenario_label(code),
            "weight": weights.get(code, 0),
        }
        for code in leg["scenario_dependencies"]
    ]
    enriched["explanation"] = (
        "Coverage contribution is a bounded heuristic from scenario weight, "
        "risk exposure, and redundancy. It is not EV, ROI, or profit optimization."
    )
    return enriched


def _select_set(scored_legs, set_name, limit=2):
    rows = [leg for leg in scored_legs if leg.get("set") == set_name]
    return sorted(rows, key=lambda item: item.get("coverage_contribution", 0), reverse=True)[:limit]


def _scenario_coverage_map_v2(scored_legs, weights):
    rows = []
    for code, name in SCENARIO_TAXONOMY:
        covering = [
            leg
            for leg in scored_legs
            if code in (leg.get("scenario_dependencies") or [])
        ]
        coverage_score = min(1, sum(1 - leg.get("risk_exposure", 0) for leg in covering) / 2)
        rows.append({
            "code": code,
            "name": name,
            "weight": weights.get(code, 0),
            "covered_by": [leg.get("name") for leg in covering],
            "coverage_score": round(coverage_score, 4),
        })
    return rows


def _risk_distribution_surface(scored_legs, weights):
    rows = []
    for code, name in SCENARIO_TAXONOMY:
        covering = [
            leg
            for leg in scored_legs
            if code in (leg.get("scenario_dependencies") or [])
        ]
        if covering:
            exposure = sum(leg.get("risk_exposure", 0) for leg in covering) / len(covering)
            redundancy = sum(leg.get("redundancy", 0) for leg in covering)
        else:
            exposure = 1
            redundancy = 0
        rows.append({
            "code": code,
            "name": name,
            "weight": weights.get(code, 0),
            "risk_exposure": round(exposure, 4),
            "redundancy": round(redundancy, 4),
        })
    return rows


def _coverage_efficiency_v2(scenario_coverage_map, risk_surface_rows):
    weighted_coverage = sum(
        row.get("weight", 0) * row.get("coverage_score", 0)
        for row in scenario_coverage_map
    )
    weighted_risk = sum(
        row.get("weight", 0) * row.get("risk_exposure", 0)
        for row in risk_surface_rows
    )
    weighted_redundancy = sum(
        row.get("weight", 0) * row.get("redundancy", 0)
        for row in risk_surface_rows
    )
    denominator = max(0.1, weighted_risk + weighted_redundancy)
    score = (weighted_coverage / denominator) * 55
    return round(_clamp(score, 0, 100))


def _scenario_weighted_ranking_v2(primary_set, defensive_set, tail_set, weights, metrics):
    direction_bonus = _clamp(metrics.get("direction_score"), 0, 100) / 100
    conflict = _clamp(metrics.get("market_conflict_index"), 0, 100) / 100
    volatility = _clamp(metrics.get("volatility_score"), 0, 100) / 100

    candidates = [
        {
            "position": "Primary Coverage Set",
            "legs": primary_set,
            "score": sum(leg.get("coverage_contribution", 0) for leg in primary_set) * (1 + direction_bonus * 0.15),
            "basis": "TPB anchor + Directional Strength + S1/S2 scenario weights",
        },
        {
            "position": "Defensive Coverage Set",
            "legs": defensive_set,
            "score": sum(leg.get("coverage_contribution", 0) for leg in defensive_set) * (1 + conflict * 0.18),
            "basis": "Conflict Index + Volatility + S3/S4/S5 scenario weights",
        },
        {
            "position": "Tail Coverage Set",
            "legs": tail_set,
            "score": sum(leg.get("coverage_contribution", 0) for leg in tail_set) * (1 + volatility * 0.12),
            "basis": "S4/S6 scenario weights + tail exposure constraint",
        },
    ]
    ranked = sorted(candidates, key=lambda item: item["score"], reverse=True)
    return [
        {
            "rank": index,
            "position": item["position"],
            "score": round(item["score"] * 100, 1),
            "basis": item["basis"],
            "legs": [leg.get("name") for leg in item["legs"]],
        }
        for index, item in enumerate(ranked, start=1)
    ]


def _coverage_optimization_v2(scenario_weights, metrics):
    weights = _weight_map(scenario_weights)
    leg_templates = _portfolio_leg_templates(metrics)
    scored_legs = [_score_leg(leg, weights) for leg in leg_templates]
    primary_set = _select_set(scored_legs, "primary")
    defensive_set = _select_set(scored_legs, "defensive", limit=3)
    tail_set = _select_set(scored_legs, "tail")
    scenario_coverage_map = _scenario_coverage_map_v2(scored_legs, weights)
    risk_surface = _risk_distribution_surface(scored_legs, weights)
    efficiency = _coverage_efficiency_v2(scenario_coverage_map, risk_surface)
    ranking = _scenario_weighted_ranking_v2(primary_set, defensive_set, tail_set, weights, metrics)
    return {
        "version": "coverage_optimization_v2",
        "objective": {
            "maximize": ["scenario coverage", "probability alignment", "risk balance"],
            "minimize": ["tail exposure", "conflict exposure", "redundancy"],
            "type": "bounded deterministic heuristic",
        },
        "constraints": [
            "TPB remains anchor and cannot be overridden",
            "No EV / ROI / profit maximization",
            "No ML training or black-box optimizer",
            "No user input influence",
        ],
        "primary_coverage_set": primary_set,
        "defensive_coverage_set": defensive_set,
        "tail_coverage_set": tail_set,
        "scenario_coverage_map_v2": scenario_coverage_map,
        "risk_distribution_surface": risk_surface,
        "coverage_efficiency_score_v2": efficiency,
        "scenario_weighted_ranking_v2": ranking,
        "explanation": (
            "Coverage Optimization Engine v2 is a bounded heuristic coverage layer. "
            "It optimizes scenario coverage, not expected profit."
        ),
    }


def _system_optimized_portfolio_v2(optimization):
    primary = optimization.get("primary_coverage_set") or []
    defensive = optimization.get("defensive_coverage_set") or []
    tail = optimization.get("tail_coverage_set") or []
    return {
        "version": "system_optimized_portfolio_v2",
        "main_position": {
            "name": "Primary Coverage Set",
            "label": " / ".join(leg.get("name") for leg in primary) or "-",
            "rationale": "Scenario-weighted primary coverage anchored to TPB and constrained by Market Structure.",
        },
        "defensive_position": {
            "name": "Defensive Coverage Set",
            "label": " / ".join(leg.get("name") for leg in defensive) or "-",
            "rationale": "Defensive coverage balances conflict, draw, upset, and low-scoring scenario weights.",
        },
        "tail_risk_position": {
            "name": "Tail Coverage Set",
            "label": " / ".join(leg.get("name") for leg in tail) or "-",
            "rationale": "Tail coverage is bounded optionality only; it does not amplify stake or profit targets.",
        },
        "ranking": optimization.get("scenario_weighted_ranking_v2") or [],
        "coverage_efficiency_score_v2": optimization.get("coverage_efficiency_score_v2"),
    }


def _portfolio_mapping_explanation(coverage_map):
    primary = coverage_map.get("primary_coverage") or {}
    defensive = coverage_map.get("defensive_coverage") or {}
    tail = coverage_map.get("tail_optionality") or {}
    return {
        "main_position_coverage": {
            "scenario": primary.get("scenario", "-"),
            "explanation": "Main Position 使用 bounded scenario weights 解释主覆盖路径；不是 EV/ROI 或盈利优化。",
        },
        "defensive_position_coverage": {
            "scenario": defensive.get("scenario", "-"),
            "explanation": "Defensive Position 解释平局、冷门或低比分防守路径；不改变 TPB、stake 或用户执行层。",
        },
        "tail_exposure": {
            "scenario": tail.get("scenario", "-"),
            "explanation": "Tail Optionality 标记尾部暴露；只用于 bounded coverage，不做利润最大化。",
        },
    }


def build_scenario_engine(match=None, odds=None, market_intelligence=None):
    tpb = (market_intelligence or {}).get("tpb_baseline") or true_probability_base(odds or {})
    metrics = (market_intelligence or {}).get("metrics") or {}
    distribution = _scenario_distribution(tpb, metrics)
    scenario_weights = _scenario_weights_v2(distribution, metrics)
    risk_surface = _risk_surface(distribution, metrics)
    coverage_map = _coverage_map(distribution)
    optimization_v2 = _coverage_optimization_v2(scenario_weights, metrics)
    return {
        "version": "scenario_engine_v2",
        "taxonomy": [
            {"code": code, "name": name}
            for code, name in SCENARIO_TAXONOMY
        ],
        "probability_distribution": distribution,
        "scenario_weights": scenario_weights,
        "risk_surface": risk_surface,
        "coverage_map": coverage_map,
        "portfolio_mapping_explanation": _portfolio_mapping_explanation(coverage_map),
        "scenario_market_mapping": _scenario_market_mapping(),
        "coverage_efficiency_score": _coverage_efficiency_score(distribution, risk_surface),
        "scenario_optimization_v2": optimization_v2,
        "system_optimized_portfolio_v2": _system_optimized_portfolio_v2(optimization_v2),
        "methodology": build_model_methodology(),
        "disclaimer": (
            "Scenario Engine v2 使用 bounded heuristic scenario weights 做覆盖优化；"
            "不预测比分，不计算 EV/ROI，不做盈利最大化，不覆盖 TPB，不改变 stake，也不使用用户输入。"
        ),
    }
