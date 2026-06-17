from modules.pregame_content import team_cn


POPULAR_TEAMS = {
    "argentina",
    "france",
    "brazil",
    "england",
    "germany",
    "spain",
    "portugal",
    "netherlands",
}

TEAM_CN = {
    "Argentina": "阿根廷",
    "Algeria": "阿尔及利亚",
    "Draw": "平局",
}

AFRICA_TEAMS = {
    "algeria",
    "morocco",
    "senegal",
    "tunisia",
    "egypt",
    "ghana",
    "nigeria",
    "cameroon",
    "ivory coast",
    "south africa",
}

ASIA_TEAMS = {
    "japan",
    "south korea",
    "iran",
    "saudi arabia",
    "qatar",
    "australia",
    "uzbekistan",
}


def clamp(value, low=0, high=100):
    return max(low, min(high, round(value)))


def normalize_name(value):
    return str(value or "").strip().lower()


def display_team(value):
    return team_cn(TEAM_CN.get(value, value))


def odds_probabilities(odds):
    if not odds.get("found"):
        return None
    if odds.get("implied_probabilities"):
        return odds["implied_probabilities"]
    if all(odds.get(key) for key in ["home_win", "draw", "away_win"]):
        raw = {
            "home_win": 1 / odds["home_win"],
            "draw": 1 / odds["draw"],
            "away_win": 1 / odds["away_win"],
        }
        total = sum(raw.values())
        return {key: value / total for key, value in raw.items()}
    return None


def polymarket_probabilities(polymarket):
    if not polymarket.get("found"):
        return None
    if not all(polymarket.get(key) is not None for key in ["home_win", "draw", "away_win"]):
        return None
    raw = {
        "home_win": polymarket["home_win"],
        "draw": polymarket["draw"],
        "away_win": polymarket["away_win"],
    }
    total = sum(raw.values())
    if total <= 0:
        return None
    return {key: value / total for key, value in raw.items()}


def label_for_key(match, key):
    return {
        "home_win": match["home_cn"],
        "draw": "平局",
        "away_win": match["away_cn"],
    }.get(key, "-")


def score_level(score):
    if score >= 67:
        return "High"
    if score >= 34:
        return "Medium"
    return "Low"


def traffic_light(score, high_label="High"):
    if score >= 67:
        return f"🔴 {high_label}"
    if score >= 34:
        return "🟡 中等"
    return "🟢 较低"


def market_disagreement(match, odds, polymarket):
    odds_probs = odds_probabilities(odds)
    poly_probs = polymarket_probabilities(polymarket)
    if not odds_probs or not poly_probs:
        return {
            "score": 0,
            "level": "低分歧",
            "direction": "-",
            "difference": 0,
            "odds_probability": None,
            "polymarket_probability": None,
            "reason": "缺少可比较的市场数据。",
        }

    diffs = {
        key: abs(poly_probs[key] - odds_probs[key])
        for key in ["home_win", "draw", "away_win"]
    }
    key = max(diffs, key=diffs.get)
    difference = diffs[key]
    score = clamp(difference * 1000)
    level = {
        "Low": "低分歧",
        "Medium": "中分歧",
        "High": "高分歧",
    }[score_level(score)]

    return {
        "score": score,
        "level": level,
        "direction": label_for_key(match, key),
        "difference": difference,
        "odds_probability": odds_probs[key],
        "polymarket_probability": poly_probs[key],
        "reason": f"最大市场价差出现在{label_for_key(match, key)}方向。",
    }


def market_favorites(match, odds, polymarket):
    odds_probs = odds_probabilities(odds) or {}
    poly_probs = polymarket_probabilities(polymarket) or {}
    odds_favorite = max(odds_probs, key=odds_probs.get) if odds_probs else None
    poly_favorite = max(poly_probs, key=poly_probs.get) if poly_probs else None
    return odds_favorite, poly_favorite, odds_probs, poly_probs


def contrarian_score(match, odds, polymarket):
    odds_favorite, poly_favorite, odds_probs, poly_probs = market_favorites(match, odds, polymarket)
    if not odds_favorite and not poly_favorite:
        return {
            "score": 20,
            "level": "较低",
            "popular_side": "-",
            "reason": "缺少市场数据，暂不形成逆向判断。",
        }

    favorite = poly_favorite or odds_favorite
    favorite_name = normalize_name(label_for_key(match, favorite))
    is_popular = favorite_name in POPULAR_TEAMS
    markets_aligned = odds_favorite and poly_favorite and odds_favorite == poly_favorite
    concentration = max(
        odds_probs.get(favorite, 0),
        poly_probs.get(favorite, 0),
    )

    score = 15
    if is_popular:
        score += 25
    if markets_aligned:
        score += 20
    if concentration >= 0.65:
        score += 25
    elif concentration >= 0.55:
        score += 15
    if concentration >= 0.75:
        score += 10

    score = clamp(score)
    return {
        "score": score,
        "level": {"Low": "较低", "Medium": "中等", "High": "较高"}[score_level(score)],
        "popular_side": label_for_key(match, favorite),
        "reason": "热门球队与多市场一致预期可能带来拥挤定价。"
        if is_popular and markets_aligned
        else "当前市场结构下，逆向压力有限。",
    }


def fixture_round(api_football_data):
    fixture = (api_football_data or {}).get("fixture") or {}
    raw = fixture.get("raw", {})
    return str((raw.get("league") or {}).get("round") or "")


def upset_index(match, odds, polymarket, api_football_data):
    odds_favorite, poly_favorite, odds_probs, poly_probs = market_favorites(match, odds, polymarket)
    favorite = poly_favorite or odds_favorite
    favorite_probability = max(
        odds_probs.get(favorite, 0) if favorite else 0,
        poly_probs.get(favorite, 0) if favorite else 0,
    )

    score = 35
    if "group" in fixture_round(api_football_data).lower():
        score += 12
    if favorite_probability >= 0.65:
        score += 8
    elif favorite_probability <= 0.50:
        score -= 8

    home = normalize_name(match["home_cn"])
    away = normalize_name(match["away_cn"])
    underdog = away if favorite == "home_win" else home if favorite == "away_win" else None
    if underdog in AFRICA_TEAMS:
        score += 8
    if underdog in ASIA_TEAMS:
        score += 7
    if normalize_name(label_for_key(match, favorite)) in POPULAR_TEAMS:
        score += 5

    score = clamp(score)
    meaning = "高爆冷风险" if score >= 70 else "中等爆冷风险" if score >= 45 else "低爆冷风险"
    return {
        "score": score,
        "meaning": meaning,
        "reason": "小组赛阶段与弱势方属性提高了爆冷敏感度。",
    }


def recent_form_score(api_football_data):
    home_recent = (api_football_data or {}).get("home_recent") or []
    away_recent = (api_football_data or {}).get("away_recent") or []
    if not home_recent or not away_recent:
        return {
            "score": 50,
            "reason": "近期状态暂不可用，采用中性分。",
        }
    return {
        "score": 55,
        "reason": "近期状态可用，V1 框架给予轻微信号。",
    }


def injury_impact_score(api_football_data):
    injuries = (api_football_data or {}).get("injuries") or []
    if not injuries:
        return {
            "score": 50,
            "reason": "暂无公开伤病信息，采用中性分。",
        }
    return {
        "score": 60,
        "reason": "存在公开伤病信息，不确定性上升。",
    }


def placeholder_score(name):
    return {
        "score": 50,
        "reason": f"{name} 为 V1 框架占位，待后续接入可靠数据源。",
    }


def value_rating(score):
    if score >= 75:
        return "A"
    if score >= 55:
        return "B"
    if score >= 35:
        return "C"
    return "D"


def rating_meaning(rating, score):
    meanings = {
        "A": "赔率吸引力强",
        "B": "存在价值",
        "C": "价格基本合理",
        "D": "价值有限",
    }
    return f"赔率价值 {score} / 100，评级 {rating}：{meanings.get(rating, '-')}"


def score_from_gap(gap, scale):
    if gap < 0.02:
        return 0
    if gap < 0.05:
        return scale["low"]
    if gap < 0.08:
        return scale["medium"]
    return scale["high"]


def biggest_probability_gap(match, odds, polymarket):
    odds_probs = odds_probabilities(odds)
    poly_probs = polymarket_probabilities(polymarket)
    if not odds_probs or not poly_probs:
        return None
    gaps = {
        key: abs(poly_probs[key] - odds_probs[key])
        for key in ["home_win", "draw", "away_win"]
    }
    key = max(gaps, key=gaps.get)
    return {
        "key": key,
        "label": display_team(label_for_key(match, key)),
        "gap": gaps[key],
        "odds_probability": odds_probs[key],
        "model_probability": poly_probs[key],
    }


def favorite_probability_gap(match, odds, polymarket):
    odds_probs = odds_probabilities(odds)
    poly_probs = polymarket_probabilities(polymarket)
    if not odds_probs or not poly_probs:
        return None
    favorite_key = max(odds_probs, key=odds_probs.get)
    difference = poly_probs[favorite_key] - odds_probs[favorite_key]
    return {
        "key": favorite_key,
        "label": display_team(label_for_key(match, favorite_key)),
        "difference": difference,
        "market_probability": odds_probs[favorite_key],
        "model_probability": poly_probs[favorite_key],
    }


def odds_value_analysis(match, odds, polymarket):
    gap = favorite_probability_gap(match, odds, polymarket)
    odds_probs = odds_probabilities(odds)
    if not gap or not odds_probs:
        score = 35
        return {
            "score": score,
            "rating": value_rating(score),
            "label": "-",
            "market_probability": None,
            "model_probability": None,
            "difference": 0,
            "components": [
                {"name": "市场价差", "points": 0, "max_points": 40, "reason": "缺少 Polymarket 对比数据。"},
                {"name": "盘口一致", "points": 15, "max_points": 25, "reason": "缺少完整市场数据，按中性处理。"},
                {"name": "赔率可用性", "points": 20, "max_points": 20, "reason": "胜平负盘口可用。"},
                {"name": "价格风险", "points": 0, "max_points": 15, "reason": "缺少概率对比，保守处理。"},
            ],
            "reason": "缺少模型概率与市场概率的可比数据，赔率价值按中性偏低处理。",
        }

    difference_pct = gap["difference"] * 100

    if gap["difference"] >= 0.08:
        edge_points = 40
    elif gap["difference"] >= 0.05:
        edge_points = 30
    elif gap["difference"] >= 0.02:
        edge_points = 20
    elif gap["difference"] >= 0:
        edge_points = 10
    elif gap["difference"] >= -0.03:
        edge_points = 5
    else:
        edge_points = 0

    favorite = gap["key"]
    h_side = handicap_side(odds)
    if h_side == favorite:
        consistency_points = 25
        consistency_reason = "让球盘与胜平负主方向一致。"
    elif h_side == "neutral":
        consistency_points = 15
        consistency_reason = "让球盘接近均衡。"
    elif h_side:
        consistency_points = 5
        consistency_reason = "让球盘与胜平负主方向冲突。"
    else:
        consistency_points = 8
        consistency_reason = "让球盘缺失。"

    availability_points = 10
    availability_reasons = ["胜平负盘口可用。"]
    if odds.get("asian_handicap"):
        availability_points += 5
        availability_reasons.append("让球盘口可用。")
    if odds.get("over_under"):
        availability_points += 5
        availability_reasons.append("大小球盘口可用。")

    market_probability = gap["market_probability"]
    if market_probability >= 0.78 and gap["difference"] <= 0.01:
        risk_points = 3
        risk_reason = "热门方向价格较短，赔率补偿有限。"
    elif market_probability >= 0.68:
        risk_points = 8
        risk_reason = "热门方向价格偏短，但方向较清晰。"
    else:
        risk_points = 12
        risk_reason = "赔率价格仍有一定回报空间。"

    score = clamp(edge_points + consistency_points + availability_points + risk_points)
    components = [
        {
            "name": "市场价差",
            "points": edge_points,
            "max_points": 40,
            "reason": f"Polymarket 与赔率市场差异 {difference_pct:+.1f}%。",
        },
        {
            "name": "盘口一致",
            "points": consistency_points,
            "max_points": 25,
            "reason": consistency_reason,
        },
        {
            "name": "盘口完整",
            "points": availability_points,
            "max_points": 20,
            "reason": " ".join(availability_reasons),
        },
        {
            "name": "价格风险",
            "points": risk_points,
            "max_points": 15,
            "reason": risk_reason,
        },
    ]
    rating = value_rating(score)
    return {
        "score": score,
        "rating": rating,
        "label": gap["label"],
        "market_probability": gap["market_probability"],
        "model_probability": gap["model_probability"],
        "difference": gap["difference"],
        "components": components,
        "reason": (
            f"{gap['label']}方向：市场概率 {gap['market_probability'] * 100:.1f}%，"
            f"Polymarket {gap['model_probability'] * 100:.1f}%，差异 {difference_pct:+.1f}%；"
            f"多因素得分 {score} / 100。"
        ),
    }


def market_value_component(match, odds, polymarket):
    value = odds_value_analysis(match, odds, polymarket)
    points = next(
        (item["points"] for item in value.get("components", []) if item["name"] == "市场价差"),
        0,
    )
    return {
        "name": "赔率价值",
        "points": points,
        "max_points": 40,
        "reason": value["reason"],
    }


def market_disagreement_component(match, odds, polymarket):
    gap = biggest_probability_gap(match, odds, polymarket)
    if not gap:
        return {
            "name": "市场分歧",
            "points": 0,
            "max_points": 20,
            "reason": "Polymarket 与赔率市场缺少可比较数据。",
        }
    points = score_from_gap(gap["gap"], {"low": 8, "medium": 14, "high": 20})
    return {
        "name": "市场分歧",
        "points": points,
        "max_points": 20,
        "reason": f"Polymarket 与赔率市场最大差异为 {gap['gap'] * 100:.1f}%。",
    }


def consensus_line(markets):
    if not markets:
        return None, []
    counts = {}
    for market in markets:
        line = market.get("line")
        counts[line] = counts.get(line, 0) + 1
    line = max(counts, key=counts.get)
    return line, [market for market in markets if market.get("line") == line]


def handicap_side(odds):
    line, selected = consensus_line(odds.get("asian_handicap") or [])
    if line is None or not selected:
        return None
    home_values = [market.get("home_odds") for market in selected if market.get("home_odds")]
    away_values = [market.get("away_odds") for market in selected if market.get("away_odds")]
    if not home_values or not away_values:
        return None
    avg_home = sum(home_values) / len(home_values)
    avg_away = sum(away_values) / len(away_values)
    if abs(avg_home - avg_away) <= 0.08:
        return "neutral"
    return "home_win" if avg_home < avg_away else "away_win"


def totals_available(odds):
    line, selected = consensus_line(odds.get("over_under") or [])
    return line is not None and bool(selected)


def market_consistency_component(match, odds):
    odds_probs = odds_probabilities(odds)
    if not odds_probs:
        return {
            "name": "盘口一致性",
            "points": 0,
            "max_points": 20,
            "reason": "缺少胜平负赔率，无法判断盘口一致性。",
        }

    favorite = max(odds_probs, key=odds_probs.get)
    points = 8
    reasons = [f"胜平负主方向为{display_team(label_for_key(match, favorite))}。"]

    h_side = handicap_side(odds)
    if h_side == favorite:
        points += 8
        reasons.append("让球盘与胜平负方向一致。")
    elif h_side == "neutral":
        points += 4
        reasons.append("让球盘接近均衡，未明显反向。")
    elif h_side:
        reasons.append("让球盘与胜平负方向存在矛盾。")
    else:
        reasons.append("让球盘缺失。")

    if totals_available(odds):
        points += 4
        reasons.append("大小球盘口可用，节奏判断有真实市场支撑。")
    else:
        reasons.append("大小球盘口缺失。")

    return {
        "name": "盘口一致性",
        "points": clamp(points, 0, 20),
        "max_points": 20,
        "reason": " ".join(reasons),
    }


def extreme_path_risk_score(odds):
    odds_probs = odds_probabilities(odds) or {}
    favorite_prob = max(odds_probs.values()) if odds_probs else 0
    line, _ = consensus_line(odds.get("asian_handicap") or [])
    line_strength = abs(float(line or 0))
    if favorite_prob >= 0.65 and line_strength >= 1.25:
        return 55
    if favorite_prob >= 0.58 and line_strength >= 0.75:
        return 35
    return 20


def risk_adjustment_component(odds, upset):
    extreme = extreme_path_risk_score(odds)
    penalty = round(upset["score"] * 0.12 + extreme * 0.08)
    points = clamp(20 - penalty, 0, 20)
    return {
        "name": "风险调整",
        "points": points,
        "max_points": 20,
        "reason": (
            f"爆冷指数 {upset['score']} / 100，极端路径风险 {extreme} / 100，"
            f"风险扣分 {penalty}。"
        ),
    }


def build_value_rating_breakdown(match, odds, polymarket, upset):
    components = [
        market_value_component(match, odds, polymarket),
        market_disagreement_component(match, odds, polymarket),
        market_consistency_component(match, odds),
        risk_adjustment_component(odds, upset),
    ]
    total = clamp(sum(item["points"] for item in components), 0, 100)
    rating = value_rating(total)
    return total, rating, components


def winner_strength_points(probability):
    if probability >= 0.75:
        return 32
    if probability >= 0.65:
        return 30
    if probability >= 0.55:
        return 24
    if probability >= 0.45:
        return 16
    return 8


def direction_confidence(match, odds, polymarket, upset):
    odds_probs = odds_probabilities(odds)
    poly_probs = polymarket_probabilities(polymarket)
    if not odds_probs:
        return {
            "score": 0,
            "level": "观望",
            "components": [],
            "reason": "缺少胜平负赔率，无法形成方向把握。",
        }

    favorite = max(odds_probs, key=odds_probs.get)
    favorite_label = display_team(label_for_key(match, favorite))
    favorite_probability = odds_probs[favorite]
    components = []

    winner_points = winner_strength_points(favorite_probability)
    components.append({
        "name": "胜平负方向",
        "points": winner_points,
        "max_points": 35,
        "reason": f"{favorite_label}市场概率 {favorite_probability * 100:.1f}%。",
    })

    poly_points = 8
    if poly_probs:
        poly_favorite = max(poly_probs, key=poly_probs.get)
        if poly_favorite == favorite:
            poly_points = 23 if abs(poly_probs[favorite] - favorite_probability) <= 0.05 else 20
            poly_reason = f"Polymarket 同样支持{favorite_label}，概率 {poly_probs[favorite] * 100:.1f}%。"
        else:
            poly_points = 6
            poly_reason = "Polymarket 与赔率市场主方向不一致。"
    else:
        poly_reason = "Polymarket 数据不可用。"
    components.append({
        "name": "Polymarket",
        "points": poly_points,
        "max_points": 25,
        "reason": poly_reason,
    })

    h_side = handicap_side(odds)
    if h_side == favorite:
        handicap_points = 23
        handicap_reason = "让球盘与胜平负主方向一致。"
    elif h_side == "neutral":
        handicap_points = 13
        handicap_reason = "让球盘接近均衡。"
    elif h_side:
        handicap_points = 4
        handicap_reason = "让球盘与胜平负主方向冲突。"
    else:
        handicap_points = 0
        handicap_reason = "让球盘缺失。"
    components.append({
        "name": "盘口一致性",
        "points": handicap_points,
        "max_points": 25,
        "reason": handicap_reason,
    })

    totals_points = 8 if totals_available(odds) else 0
    components.append({
        "name": "大小球辅助",
        "points": totals_points,
        "max_points": 10,
        "reason": "大小球盘口可用，比赛节奏判断有市场支撑。" if totals_points else "大小球盘口缺失。",
    })

    risk_points = max(0, 5 - round(upset["score"] / 25))
    components.append({
        "name": "风险清晰度",
        "points": risk_points,
        "max_points": 5,
        "reason": f"爆冷指数 {upset['score']} / 100。",
    })

    score = clamp(sum(item["points"] for item in components))
    if score >= 90:
        level = "非常有把握"
    elif score >= 80:
        level = "较有把握"
    elif score >= 70:
        level = "中等把握"
    elif score >= 60:
        level = "谨慎参与"
    else:
        level = "观望"
    return {
        "score": score,
        "level": level,
        "components": components,
        "reason": f"{favorite_label}方向较清晰，主要依据为胜平负、Polymarket与让球盘一致性。",
    }


def participation_advice(direction, odds_value, upset):
    score = direction["score"]
    value_rating_text = odds_value["rating"]
    risk_score = upset["score"]

    if score >= 90 and value_rating_text in {"A", "B", "C", "D"} and risk_score < 65:
        advice = "强烈参与"
    elif score >= 80 and risk_score < 70:
        advice = "建议参与"
    elif score >= 70:
        advice = "小仓参与"
    elif score >= 60 and value_rating_text in {"A", "B"}:
        advice = "小仓参与"
    elif score >= 55:
        advice = "仅观察"
    else:
        advice = "放弃"

    return {
        "advice": advice,
        "reason": (
            f"方向把握 {score} / 100，赔率价值 {value_rating_text}，"
            f"爆冷指数 {risk_score} / 100。"
        ),
    }


def recommended_stake(direction, odds_value, participation):
    score = direction["score"]
    if score >= 90:
        base = 1500
    elif score >= 80:
        base = 1200
    elif score >= 70:
        base = 900
    elif score >= 60:
        base = 500
    else:
        base = 200 if participation["advice"] == "仅观察" else 0

    adjustment = {
        "A": 300,
        "B": 200,
        "C": 0,
        "D": -100,
    }.get(odds_value["rating"], 0)

    if participation["advice"] in {"仅观察", "放弃"}:
        base = min(base, 300)

    final = clamp(round((base + adjustment) / 100) * 100, 100, 2000)
    return {
        "amount": final,
        "base": base,
        "adjustment": adjustment,
        "reason": (
            f"方向把握 {score} 分，对应基础仓位 {base}；"
            f"赔率价值 {odds_value['rating']}，调整 {adjustment:+d}。"
        ),
    }


def final_recommendation(match, betting_opinion, contrarian, upset):
    handicap = (betting_opinion or {}).get("asian_handicap", "No view").replace("Lean ", "")
    if handicap != "No view" and (contrarian["score"] >= 55 or upset["score"] >= 55):
        return {
            "bet": handicap,
            "reason": [
                f"市场共识明显支持{display_team(match['home_cn'])}",
                "逆向分数处于偏高区间",
                "爆冷指数高于基准水平",
                "让球盘相比独赢具备更好的风险收益比",
            ],
        }

    winner = (betting_opinion or {}).get("match_winner", "No view").replace("Lean ", "")
    return {
        "bet": winner if winner != "No view" else "观察为主",
        "reason": [
            "暂未发现强逆向让球机会",
            "当前仅将市场方向作为参考",
        ],
    }


def stake_suggestion(final_score):
    if final_score >= 70:
        return {"Conservative": 500, "Standard": 1000, "Aggressive": 1500}
    if final_score >= 55:
        return {"Conservative": 300, "Standard": 600, "Aggressive": 900}
    if final_score >= 40:
        return {"Conservative": 100, "Standard": 300, "Aggressive": 500}
    return {"Conservative": 0, "Standard": 0, "Aggressive": 0}


def build_decision_engine(match, odds, polymarket, api_football_data, betting_opinion):
    disagreement = market_disagreement(match, odds, polymarket)
    contrarian = contrarian_score(match, odds, polymarket)
    upset = upset_index(match, odds, polymarket, api_football_data)
    recent_form = recent_form_score(api_football_data)
    injury_impact = injury_impact_score(api_football_data)
    elo = placeholder_score("ELO评分")
    team_value = placeholder_score("球队身价")
    old_value_score, old_rating, rating_breakdown = build_value_rating_breakdown(match, odds, polymarket, upset)
    direction = direction_confidence(match, odds, polymarket, upset)
    odds_value = odds_value_analysis(match, odds, polymarket)
    participation = participation_advice(direction, odds_value, upset)
    stake = recommended_stake(direction, odds_value, participation)

    return {
        "market_disagreement": disagreement,
        "contrarian": contrarian,
        "upset_index": upset,
        "recent_form": recent_form,
        "elo_rating": elo,
        "injury_impact": injury_impact,
        "team_value": team_value,
        "direction_confidence": direction,
        "odds_value": odds_value,
        "participation_advice": participation,
        "recommended_stake": stake,
        "final_confidence_score": direction["score"],
        "value_rating": odds_value["rating"],
        "value_rating_score": odds_value["score"],
        "value_rating_breakdown": rating_breakdown,
        "value_rating_meaning": rating_meaning(odds_value["rating"], odds_value["score"]),
        "final_recommendation": final_recommendation(match, betting_opinion, contrarian, upset),
        "stake_suggestion": stake_suggestion(direction["score"]),
        "weights": {
            "方向把握": "胜平负35 + Polymarket25 + 盘口25 + 大小球10 + 风险清晰度5",
            "赔率价值": "Polymarket概率 - 赔率市场概率",
            "参与建议": "方向把握 + 赔率价值 + 风险暴露",
            "推荐仓位": "方向把握为主，赔率价值微调",
        },
    }
