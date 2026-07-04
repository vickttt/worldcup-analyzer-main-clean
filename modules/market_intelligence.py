from modules.market_utils import identify_handicap_center, identify_total_center, safe_float
from modules.probability_base import true_probability_base


def _percent(value):
    return round(float(value or 0) * 100, 1)


def _team_label(match, side):
    if not match:
        return side
    key = "home_cn" if side == "home" else "away_cn"
    fallback = "home_en" if side == "home" else "away_en"
    return match.get(key) or match.get(fallback) or side


def _favorite_from_tpb(tpb, match):
    probabilities = (tpb or {}).get("probabilities") or {}
    if not probabilities:
        return {"outcome": None, "label": "暂无主方向", "probability": 0, "edge": 0}
    ordered = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
    top_key, top_probability = ordered[0]
    second_probability = ordered[1][1] if len(ordered) > 1 else 0
    labels = {
        "home_win": _team_label(match, "home"),
        "draw": "平局",
        "away_win": _team_label(match, "away"),
    }
    return {
        "outcome": top_key,
        "label": labels.get(top_key, top_key),
        "probability": top_probability,
        "edge": max(0, top_probability - second_probability),
    }


def _correct_score_tail_density(rows):
    if not rows:
        return 0
    tail_count = 0
    for row in rows:
        odds = safe_float(row.get("odd"))
        score = str(row.get("score") or "")
        if odds is not None and odds >= 50:
            tail_count += 1
        elif ":" in score:
            try:
                home, away = [int(part) for part in score.split(":", 1)]
            except ValueError:
                continue
            if home >= 4 or away >= 4:
                tail_count += 1
    return tail_count / max(1, len(rows))


def _directional_strength(favorite, handicap=None, totals=None):
    edge = favorite.get("edge", 0)
    score = edge * 100
    if score >= 35:
        return "Strong", round(score)
    if score >= 18:
        return "Medium", round(score)
    return "Weak", round(score)


def _conflict_index(tpb, favorite, handicap, totals, tail_density):
    probabilities = tpb.get("probabilities") or {}
    draw_probability = probabilities.get("draw", 0)
    favorite_edge = favorite.get("edge", 0)
    conflict = draw_probability * 45 + max(0, 0.16 - favorite_edge) * 160
    if not handicap.get("available"):
        conflict += 15
    if totals.get("available") and safe_float(totals.get("center_line")) is not None:
        total_line = float(totals.get("center_line"))
        if total_line <= 2 and favorite_edge >= 0.18:
            conflict += 10
    conflict += tail_density * 20
    return max(0, min(100, round(conflict)))


def _conflict_label(value):
    if value <= 30:
        return "低冲突"
    if value <= 70:
        return "中冲突"
    return "高不确定性市场"


def _market_agreement(tpb, api_markets):
    dispersion = float(tpb.get("market_dispersion") or 0)
    handicap_count = len(((api_markets.get("asian_handicap") or {}).get("rows") or []))
    total_count = len(((api_markets.get("over_under") or {}).get("rows") or []))
    depth_bonus = min(12, (handicap_count + total_count) / 24)
    score = max(0, min(100, round(100 - dispersion * 120 + depth_bonus)))
    if score >= 75:
        return "High", score
    if score >= 50:
        return "Medium", score
    return "Low", score


def _volatility_pressure(tpb, tail_density, agreement_score):
    probabilities = tpb.get("probabilities") or {}
    draw_probability = probabilities.get("draw", 0)
    disagreement = 1 - max(0, min(100, agreement_score)) / 100
    score = draw_probability * 55 + tail_density * 35 + disagreement * 45
    if score >= 45:
        return "High", round(score)
    if score >= 25:
        return "Medium", round(score)
    return "Low", round(score)


def _upset_probability(tpb, handicap, tail_density):
    probabilities = tpb.get("probabilities") or {}
    underdog_probability = min(
        probabilities.get("home_win", 0),
        probabilities.get("away_win", 0),
    ) if probabilities else 0
    draw_probability = probabilities.get("draw", 0)
    score = underdog_probability * 60 + draw_probability * 30 + tail_density * 25
    if not handicap.get("available"):
        score += 8
    if score >= 42:
        return "High", round(score)
    if score >= 28:
        return "Medium", round(score)
    return "Low", round(score)


def _efficiency_score(tpb, api_markets, tail_density):
    dispersion = float(tpb.get("market_dispersion") or 0)
    handicap_count = len(((api_markets.get("asian_handicap") or {}).get("rows") or []))
    total_count = len(((api_markets.get("over_under") or {}).get("rows") or []))
    depth_bonus = min(15, (handicap_count + total_count) / 20)
    score = 100 - dispersion * 90 - tail_density * 25 + depth_bonus
    return max(0, min(100, round(score)))


def _volatility_index(draw_probability, conflict_index, tail_density):
    score = draw_probability * 50 + conflict_index * 0.45 + tail_density * 25
    if score >= 55:
        return "High", round(score)
    if score >= 35:
        return "Medium", round(score)
    return "Low", round(score)


def _system_positions(favorite, metrics):
    main = {
        "name": "Main Position",
        "label": f"主方向：{favorite.get('label')}",
        "rationale": "System 层综合 TPB baseline strength 与 Directional Strength；Market Structure 本身不覆盖 TPB。",
    }
    defensive = {
        "name": "Defensive Position",
        "label": "防守组合：平局/受让覆盖",
        "rationale": "用于解释 Conflict、Volatility 或平局风险偏高的防守结构，不改变 stake。",
    }
    tail = {
        "name": "Tail Risk Position",
        "label": "尾部组合：小额波胆/极端路径观察",
        "rationale": "低概率高赔率路径仅作为受约束尾部覆盖参考，不进入 EV/ROI 或 stake。",
    }
    ranking_basis = (
        f"SS {metrics.get('direction_score', 0)}; "
        f"Scenario Alignment pending; "
        f"RSI pending"
    )
    ranking = [
        {
            "rank": 1,
            "position": main["label"],
            "basis": ranking_basis,
        },
        {
            "rank": 2,
            "position": defensive["label"],
            "basis": f"Market Agreement {metrics.get('market_agreement')} / Volatility Pressure {metrics.get('volatility_pressure')}",
        },
        {
            "rank": 3,
            "position": tail["label"],
            "basis": f"Tail density {metrics.get('tail_density')} / Volatility Pressure {metrics.get('volatility_pressure')}",
        },
    ]
    return {
        "main_position": main,
        "defensive_position": defensive,
        "tail_risk_position": tail,
        "ranking": ranking,
    }


def build_market_intelligence(match=None, odds=None, api_football_data=None, betting_opinion=None):
    odds = odds or {}
    api_football_data = api_football_data or {}
    api_markets = {
        "asian_handicap": api_football_data.get("asian_handicap") or {},
        "over_under": {"rows": odds.get("over_under") or []},
        "correct_score": api_football_data.get("correct_score") or {},
    }
    tpb = true_probability_base(odds)
    favorite = _favorite_from_tpb(tpb, match)
    handicap = identify_handicap_center((api_markets["asian_handicap"].get("rows") or []), odds=odds, match=match)
    totals = identify_total_center(api_markets["over_under"].get("rows") or [])
    tail_density = _correct_score_tail_density(api_markets["correct_score"].get("rows") or [])

    directional_strength, direction_score = _directional_strength(favorite, handicap, totals)
    market_agreement, agreement_score = _market_agreement(tpb, api_markets)
    volatility_pressure, volatility_score = _volatility_pressure(tpb, tail_density, agreement_score)
    conflict_index = max(0, min(100, 100 - agreement_score))
    upset_probability, upset_score = _upset_probability(tpb, handicap, tail_density)
    efficiency_score = agreement_score
    volatility_index = volatility_pressure

    metrics = {
        "model_version": "lite_explainable_betting_decision_v1",
        "directional_strength": directional_strength,
        "direction_score": direction_score,
        "market_agreement": market_agreement,
        "market_agreement_score": agreement_score,
        "volatility_pressure": volatility_pressure,
        "volatility_pressure_score": volatility_score,
        "market_conflict_index": conflict_index,
        "market_conflict_label": _conflict_label(conflict_index),
        "upset_probability": upset_probability,
        "upset_score": upset_score,
        "market_efficiency_score": efficiency_score,
        "volatility_index": volatility_index,
        "volatility_score": volatility_score,
        "favorite_label": favorite.get("label"),
        "favorite_probability": _percent(favorite.get("probability")),
        "tail_density": round(tail_density, 3),
        "lite_summary": (
            f"方向强度 {directional_strength}；市场一致性 {market_agreement}；"
            f"波动压力 {volatility_pressure}。"
        ),
        "explanation": "Market Structure Lite 只保留方向强度、市场一致性、波动压力三个指标；不使用用户输入，不计算 EV/ROI。",
    }
    return {
        "available": tpb.get("available", False),
        "tpb_baseline": tpb,
        "metrics": metrics,
        "system_portfolio": _system_positions(favorite, metrics),
    }
