from modules.probability_base import true_probability_base


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


def _portfolio_mapping_explanation(coverage_map):
    primary = coverage_map.get("primary_coverage") or {}
    defensive = coverage_map.get("defensive_coverage") or {}
    tail = coverage_map.get("tail_optionality") or {}
    return {
        "main_position_coverage": {
            "scenario": primary.get("scenario", "-"),
            "explanation": "Main Position 主要解释概率空间中的主覆盖路径；它不是 scenario-driven recommendation。",
        },
        "defensive_position_coverage": {
            "scenario": defensive.get("scenario", "-"),
            "explanation": "Defensive Position 解释平局、冷门或低比分防守路径；它不改变 stake 或 ranking。",
        },
        "tail_exposure": {
            "scenario": tail.get("scenario", "-"),
            "explanation": "Tail Optionality 标记未充分覆盖的尾部暴露；仅用于风险说明，不放大推荐。",
        },
    }


def build_scenario_engine(match=None, odds=None, market_intelligence=None):
    tpb = (market_intelligence or {}).get("tpb_baseline") or true_probability_base(odds or {})
    metrics = (market_intelligence or {}).get("metrics") or {}
    distribution = _scenario_distribution(tpb, metrics)
    risk_surface = _risk_surface(distribution, metrics)
    coverage_map = _coverage_map(distribution)
    return {
        "version": "scenario_engine_v1",
        "taxonomy": [
            {"code": code, "name": name}
            for code, name in SCENARIO_TAXONOMY
        ],
        "probability_distribution": distribution,
        "risk_surface": risk_surface,
        "coverage_map": coverage_map,
        "portfolio_mapping_explanation": _portfolio_mapping_explanation(coverage_map),
        "scenario_market_mapping": _scenario_market_mapping(),
        "coverage_efficiency_score": _coverage_efficiency_score(distribution, risk_surface),
        "disclaimer": (
            "Scenario Engine v1 只做概率空间、风险覆盖和情景结构分析；"
            "不预测比分，不计算 EV/ROI，不影响 TPB、investment_score、stake、system ranking 或 recommendation。"
        ),
    }
