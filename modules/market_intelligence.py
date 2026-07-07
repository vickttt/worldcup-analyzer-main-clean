from statistics import median

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


def _correct_score_tail_density_deprecated(rows):
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


def _parse_score(score):
    text = str(score or "").strip()
    if ":" not in text:
        return None
    try:
        home, away = [int(part) for part in text.split(":", 1)]
    except ValueError:
        return None
    return home, away


def _is_tail_correct_score(row):
    odds = safe_float(row.get("odd"))
    score = str(row.get("score") or "")
    if odds is not None and odds >= 50:
        return True
    parsed = _parse_score(score)
    if not parsed:
        return False
    home, away = parsed
    return home >= 4 or away >= 4


def _correct_score_true_tail_probability(rows):
    """Display-only normalized implied probability mass for tail correct scores."""
    total_implied = 0
    tail_implied = 0
    for row in rows or []:
        odds = safe_float(row.get("odd"))
        if odds is None or odds <= 1:
            continue
        implied = 1 / odds
        total_implied += implied
        if _is_tail_correct_score(row):
            tail_implied += implied
    if total_implied <= 0:
        return 0
    return tail_implied / total_implied


def _result_key(home_goals, away_goals):
    if home_goals > away_goals:
        return "home_win"
    if home_goals < away_goals:
        return "away_win"
    return "draw"


def _favorite_outcome_from_tpb(tpb):
    probabilities = (tpb or {}).get("probabilities") or {}
    if not probabilities:
        return None
    top_key, top_probability = max(probabilities.items(), key=lambda item: item[1])
    second_probability = sorted(probabilities.values(), reverse=True)[1] if len(probabilities) > 1 else 0
    if top_key == "draw" or top_probability - second_probability < 0.08:
        return None
    return top_key


def _correct_score_probability_profile(rows, tpb=None):
    grouped = {}
    for row in rows or []:
        score = str(row.get("score") or "").strip()
        parsed = _parse_score(score)
        odds = safe_float(row.get("odd"))
        if not parsed or odds is None or odds <= 1:
            continue
        grouped.setdefault(score, []).append(1 / odds)

    raw = {
        score: median(values)
        for score, values in grouped.items()
        if values
    }
    total_raw = sum(raw.values())
    if total_raw <= 0:
        return {
            "available": False,
            "score_probabilities": {},
            "expected_goals": None,
            "over_25_probability": None,
            "over_35_probability": None,
            "score_extension_probability": 0,
            "adverse_tail_probability": 0,
            "true_tail_probability": 0,
            "true_tail_probability_score": 0,
            "true_tail_risk_score": 0,
            "tail_scores": [],
            "method": "unavailable",
        }

    probabilities = {score: value / total_raw for score, value in raw.items()}
    favorite = _favorite_outcome_from_tpb(tpb)
    underdog = None
    if favorite == "home_win":
        underdog = "away_win"
    elif favorite == "away_win":
        underdog = "home_win"

    expected_goals = 0
    over_25 = 0
    over_35 = 0
    score_extension = 0
    adverse_tail = 0
    true_tail = 0
    tail_scores = []

    for score, probability in probabilities.items():
        home_goals, away_goals = _parse_score(score)
        total_goals = home_goals + away_goals
        margin = abs(home_goals - away_goals)
        result = _result_key(home_goals, away_goals)
        expected_goals += total_goals * probability
        if total_goals > 2.5:
            over_25 += probability
        if total_goals > 3.5:
            over_35 += probability
        if total_goals >= 4:
            score_extension += probability
        if underdog and result == underdog:
            adverse_tail += probability

        if favorite:
            favorite_margin = (
                home_goals - away_goals
                if favorite == "home_win"
                else away_goals - home_goals
            )
            is_tail = (
                (underdog and result == underdog)
                or (home_goals == away_goals and home_goals >= 2)
                or total_goals >= 5
                or favorite_margin >= 4
            )
        else:
            is_tail = (
                margin >= 3
                or total_goals >= 4
                or (home_goals == away_goals and home_goals >= 2)
            )
        if is_tail:
            true_tail += probability
            tail_scores.append(score)

    true_tail_risk_score = max(0, min(100, (true_tail - 0.08) / 0.17 * 100))
    return {
        "available": True,
        "score_probabilities": probabilities,
        "expected_goals": round(expected_goals, 3),
        "over_25_probability": round(over_25, 4),
        "over_35_probability": round(over_35, 4),
        "score_extension_probability": round(score_extension, 4),
        "adverse_tail_probability": round(adverse_tail, 4),
        "true_tail_probability": round(true_tail, 4),
        "true_tail_probability_score": round(true_tail * 100, 1),
        "true_tail_risk_score": round(true_tail_risk_score, 1),
        "tail_scores": sorted(tail_scores),
        "method": "deduped median implied probability normalized by score",
    }


def _directional_strength(favorite, handicap=None, totals=None):
    edge = favorite.get("edge", 0)
    score = edge * 100
    if score >= 35:
        return "Strong", round(score)
    if score >= 18:
        return "Medium", round(score)
    return "Weak", round(score)


def _conflict_label(value):
    if value <= 30:
        return "低冲突"
    if value <= 70:
        return "中冲突"
    return "高不确定性市场"


def _component(score=None, available=True, reason="-", value=None):
    if not available or score is None:
        return {"available": False, "score": None, "reason": reason, "value": value}
    return {
        "available": True,
        "score": round(max(0, min(100, float(score)))),
        "reason": reason,
        "value": value,
    }


def _weighted_available_score(components, weights):
    available = [
        (key, weights[key], components[key]["score"])
        for key in weights
        if components.get(key, {}).get("available")
    ]
    total_weight = sum(weight for _key, weight, _score in available)
    if total_weight <= 0:
        return 0
    return round(sum(score * weight for _key, weight, score in available) / total_weight)


def _favorite_side_from_tpb(tpb):
    probabilities = (tpb or {}).get("probabilities") or {}
    if not probabilities:
        return None, 0, 0
    ordered = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
    top_key, top_probability = ordered[0]
    second_probability = ordered[1][1] if len(ordered) > 1 else 0
    if top_key == "home_win":
        return "home", top_probability, top_probability - second_probability
    if top_key == "away_win":
        return "away", top_probability, top_probability - second_probability
    return None, top_probability, top_probability - second_probability


def _handicap_depth_for_favorite(handicap, favorite_side):
    if not handicap.get("available") or not favorite_side:
        return None
    center_side = handicap.get("center_side")
    center_line = safe_float(handicap.get("center_line"))
    if center_side is None or center_line is None:
        return None
    if center_side == favorite_side:
        return abs(center_line) if center_line <= 0 else 0
    return -abs(center_line) if center_line <= 0 else 0


def _over_under_center_probability(totals):
    if not totals.get("available"):
        return None
    probabilities = []
    for row in totals.get("rows") or []:
        over = safe_float(row.get("over_odds"))
        under = safe_float(row.get("under_odds"))
        if over is None or under is None or over <= 1 or under <= 1:
            continue
        over_implied = 1 / over
        under_implied = 1 / under
        total = over_implied + under_implied
        if total > 0:
            probabilities.append(over_implied / total)
    return median(probabilities) if probabilities else None


def _polymarket_probabilities(source):
    source = source or {}
    candidates = [
        source.get("polymarket_reference"),
        source.get("polymarket"),
        source,
    ]
    for item in candidates:
        if not isinstance(item, dict):
            continue
        home = item.get("home_win", item.get("win_probability_home"))
        draw = item.get("draw", item.get("win_probability_draw"))
        away = item.get("away_win", item.get("win_probability_away"))
        if home is not None and draw is not None and away is not None:
            return {
                "home_win": float(home),
                "draw": float(draw),
                "away_win": float(away),
            }
    return None


def _market_consistency(tpb, api_markets, handicap, totals, correct_score_profile, match=None, odds=None, betting_opinion=None):
    probabilities = (tpb or {}).get("probabilities") or {}
    favorite_side, favorite_probability, favorite_edge = _favorite_side_from_tpb(tpb)
    dispersion = float(tpb.get("market_dispersion") or 0)
    one_x_two_internal = 100 - min(100, dispersion * 250)

    components = {
        "one_x_two_internal_consistency": _component(
            one_x_two_internal,
            available=bool(probabilities),
            reason="胜平负博彩公司离散度越低，一致性越高。",
        )
    }

    actual_depth = _handicap_depth_for_favorite(handicap, favorite_side)
    if actual_depth is None:
        components["one_x_two_vs_handicap_direction"] = _component(available=False, reason="亚洲让球中心不可用。")
        components["handicap_depth_vs_tpb"] = _component(available=False, reason="亚洲让球深度不可用。")
    else:
        if actual_depth > 0:
            direction_score = 100
        elif abs(actual_depth) <= 0.25 and favorite_edge < 0.12:
            direction_score = 80
        elif actual_depth == 0 and favorite_edge < 0.20:
            direction_score = 65
        elif actual_depth == 0:
            direction_score = 55
        elif actual_depth < 0:
            direction_score = 20
        else:
            direction_score = 50
        components["one_x_two_vs_handicap_direction"] = _component(
            direction_score,
            reason="TPB 主方向与亚洲让球中心方向的一致性。",
            value=actual_depth,
        )
        expected_depth = max(0, min(1.75, (favorite_probability - 0.52) * 4.0))
        depth_score = 100 - min(100, abs(abs(actual_depth) - expected_depth) * 80)
        components["handicap_depth_vs_tpb"] = _component(
            depth_score,
            reason="亚洲让球深度与 TPB 主方向概率的匹配度。",
            value={"expected": round(expected_depth, 3), "actual": round(abs(actual_depth), 3)},
        )

    center_line = safe_float(totals.get("center_line"))
    over_probability = _over_under_center_probability(totals)
    cs_expected_goals = correct_score_profile.get("expected_goals")
    cs_over_25 = correct_score_profile.get("over_25_probability")
    if (
        center_line is None
        or over_probability is None
        or cs_expected_goals is None
        or cs_over_25 is None
    ):
        components["over_under_vs_correct_score"] = _component(available=False, reason="大小球中心或波胆概率 profile 不足。")
    else:
        line_score = 100 - min(100, abs(cs_expected_goals - center_line) * 35)
        over_score = 100 - min(100, abs(cs_over_25 - over_probability) * 200)
        ou_cs_score = 0.50 * line_score + 0.50 * over_score
        components["over_under_vs_correct_score"] = _component(
            ou_cs_score,
            reason="大小球盘口中心与波胆隐含进球结构的一致性。",
            value={
                "expected_goals": cs_expected_goals,
                "center_line": center_line,
                "correct_score_over_25": cs_over_25,
                "market_over_probability": round(over_probability, 4),
            },
        )

    polymarket = _polymarket_probabilities(betting_opinion)
    if not polymarket or not probabilities:
        components["polymarket_vs_api"] = _component(available=False, reason="Polymarket 概率缺失，按规则剔除该分量。")
    else:
        tv_distance = 0.5 * sum(abs(polymarket[key] - probabilities.get(key, 0)) for key in ["home_win", "draw", "away_win"])
        poly_score = 100 - min(100, tv_distance * 300)
        if max(polymarket, key=polymarket.get) != max(probabilities, key=probabilities.get):
            poly_score = min(poly_score, 45)
        components["polymarket_vs_api"] = _component(
            poly_score,
            reason="Polymarket 与 API-Football TPB 三项概率的一致性。",
            value={"tv_distance": round(tv_distance, 4)},
        )

    weights = {
        "one_x_two_internal_consistency": 0.15,
        "one_x_two_vs_handicap_direction": 0.25,
        "handicap_depth_vs_tpb": 0.20,
        "over_under_vs_correct_score": 0.25,
        "polymarket_vs_api": 0.15,
    }
    score = _weighted_available_score(components, weights)
    if score >= 75:
        label = "High"
    elif score >= 50:
        label = "Medium"
    else:
        label = "Low"
    return {
        "label": label,
        "score": score,
        "components": components,
    }


def _score_path_uncertainty(tpb, market_consistency_components):
    probabilities = (tpb or {}).get("probabilities") or {}
    draw_probability = probabilities.get("draw", 0)
    draw_pressure = min(100, draw_probability * 250)
    ou_cs = (market_consistency_components or {}).get("over_under_vs_correct_score") or {}
    if ou_cs.get("available"):
        structure_tension = 100 - float(ou_cs.get("score") or 0)
        score = 0.60 * draw_pressure + 0.40 * structure_tension
        method = "draw pressure + over/under-correct-score structure tension"
    else:
        structure_tension = None
        score = draw_pressure
        method = "draw pressure only; over/under-correct-score component unavailable"
    score = max(0, min(100, round(score)))
    if score >= 60:
        label = "High"
    elif score >= 35:
        label = "Medium"
    else:
        label = "Low"
    return {
        "label": label,
        "score": score,
        "components": {
            "draw_stalemate_pressure": round(draw_pressure, 1),
            "over_under_correct_score_tension": None if structure_tension is None else round(structure_tension, 1),
            "method": method,
        },
    }


def _upset_probability(tpb, handicap, adverse_tail_probability):
    probabilities = tpb.get("probabilities") or {}
    underdog_probability = min(
        probabilities.get("home_win", 0),
        probabilities.get("away_win", 0),
    ) if probabilities else 0
    draw_probability = probabilities.get("draw", 0)
    score = underdog_probability * 60 + draw_probability * 30 + adverse_tail_probability * 25
    if not handicap.get("available"):
        score += 8
    if score >= 42:
        return "High", round(score)
    if score >= 28:
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
        f"Main Path Support pending; "
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
            "basis": f"市场一致性 {metrics.get('market_consistency')} / 比分路径不确定性 {metrics.get('score_path_uncertainty')}",
        },
        {
            "rank": 3,
            "position": tail["label"],
            "basis": f"真实尾部概率 {metrics.get('true_tail_probability_score')} / 比分路径不确定性 {metrics.get('score_path_uncertainty')}",
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
    correct_score_rows = api_markets["correct_score"].get("rows") or []
    tail_density_deprecated = _correct_score_tail_density_deprecated(correct_score_rows)
    correct_score_profile = _correct_score_probability_profile(correct_score_rows, tpb=tpb)

    directional_strength, direction_score = _directional_strength(favorite, handicap, totals)
    consistency = _market_consistency(
        tpb,
        api_markets,
        handicap,
        totals,
        correct_score_profile,
        match=match,
        odds=odds,
        betting_opinion=betting_opinion,
    )
    market_consistency = consistency["label"]
    consistency_score = consistency["score"]
    market_disagreement_score = max(0, min(100, 100 - consistency_score))
    score_path = _score_path_uncertainty(tpb, consistency["components"])
    score_path_uncertainty = score_path["label"]
    score_path_uncertainty_score = score_path["score"]
    upset_probability, upset_score = _upset_probability(
        tpb,
        handicap,
        correct_score_profile.get("adverse_tail_probability", 0),
    )
    efficiency_score = consistency_score
    volatility_index = score_path_uncertainty

    metrics = {
        "model_version": "lite_explainable_betting_decision_v2",
        "directional_strength": directional_strength,
        "direction_score": direction_score,
        "market_consistency": market_consistency,
        "market_consistency_score": consistency_score,
        "market_consistency_components": consistency["components"],
        "market_disagreement_score": market_disagreement_score,
        "market_agreement": market_consistency,
        "market_agreement_score": consistency_score,
        "score_path_uncertainty": score_path_uncertainty,
        "score_path_uncertainty_score": score_path_uncertainty_score,
        "score_path_uncertainty_components": score_path["components"],
        "volatility_pressure": score_path_uncertainty,
        "volatility_pressure_score": score_path_uncertainty_score,
        "market_conflict_index": market_disagreement_score,
        "market_conflict_label": _conflict_label(market_disagreement_score),
        "upset_probability": upset_probability,
        "upset_score": upset_score,
        "market_efficiency_score": efficiency_score,
        "volatility_index": volatility_index,
        "volatility_score": score_path_uncertainty_score,
        "favorite_label": favorite.get("label"),
        "favorite_probability": _percent(favorite.get("probability")),
        "tail_density_deprecated": round(tail_density_deprecated, 3),
        "correct_score_probability_profile": correct_score_profile,
        "true_tail_probability": correct_score_profile.get("true_tail_probability", 0),
        "true_tail_probability_score": correct_score_profile.get("true_tail_probability_score", 0),
        "true_tail_risk_score": correct_score_profile.get("true_tail_risk_score", 0),
        "score_extension_probability": correct_score_profile.get("score_extension_probability", 0),
        "adverse_tail_probability": correct_score_profile.get("adverse_tail_probability", 0),
        "true_tail_probability_note": "按波胆赔率隐含概率归一化后的尾部概率质量；通过真实尾部概率风险进入 RSI，并经风险折减间接影响 Investment Score；不直接输入 stake。",
        "lite_summary": (
            f"方向强度 {directional_strength}；市场一致性 {market_consistency}；"
            f"比分路径不确定性 {score_path_uncertainty}。"
        ),
        "explanation": "Market Structure Lite 使用方向强度、市场一致性评分、比分路径不确定性；真实尾部概率进入 RSI，旧 tail_density 仅并列展示；不使用用户输入，不计算 EV/ROI。",
    }
    return {
        "available": tpb.get("available", False),
        "tpb_baseline": tpb,
        "metrics": metrics,
        "system_portfolio": _system_positions(favorite, metrics),
    }
