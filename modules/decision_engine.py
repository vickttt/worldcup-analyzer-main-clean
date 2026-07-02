from modules.pregame_content import team_cn
from modules.market_utils import (
    asian_handicap_summary,
    bookmaker_margin,
    correct_score_summary,
    totals_summary,
)
from modules.user_odds import actual_odds_summary, build_recommendation_slots
from modules.probability_base import (
    betting_confidence_from_tpb,
    investment_score_from_tpb,
    market_direction_from_tpb,
    stake_from_investment_score,
    true_probability_base,
)


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
    return true_probability_base(odds).get("probabilities")


def polymarket_probabilities(polymarket):
    return None


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
            "reason": "API-Football 单一来源模式下不启用二级市场价差比较。",
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


def favorite_key_from_odds(odds):
    odds_probs = odds_probabilities(odds)
    return max(odds_probs, key=odds_probs.get) if odds_probs else None


def api_handicap_summary(api_football_data):
    handicap = (api_football_data or {}).get("asian_handicap") or {}
    return asian_handicap_summary(handicap.get("rows") or [])


def api_correct_score_summary(api_football_data):
    correct_score = (api_football_data or {}).get("correct_score") or {}
    return correct_score_summary(correct_score.get("rows") or [])


def handicap_direction_points(favorite, summary, max_points):
    if not summary.get("available"):
        return 0, "亚洲让球盘缺失。"
    side_key = "home_win" if summary.get("main_side") == "home" else "away_win"
    line = summary.get("main_line")
    if side_key == favorite:
        points = max_points
        reason = f"主盘口为 {summary.get('main_value')}，与胜平负主方向一致。"
    elif abs(float(line or 0)) <= 0.25:
        points = round(max_points * 0.55)
        reason = "亚洲让球盘较浅，未明显反向。"
    else:
        points = round(max_points * 0.25)
        reason = f"主盘口为 {summary.get('main_value')}，与胜平负主方向存在冲突。"
    return points, reason


def totals_structure_points(odds, max_points):
    summary = totals_summary(odds.get("over_under") or [])
    if not summary.get("available"):
        return 0, "大小球盘口缺失。"
    avg_over = summary.get("avg_over")
    avg_under = summary.get("avg_under")
    if avg_over is None or avg_under is None:
        return round(max_points * 0.45), "大小球盘口可用，但结构不完整。"
    if abs(avg_over - avg_under) <= 0.08:
        points = round(max_points * 0.70)
        reason = f"大小球主盘口 {summary.get('line')}，大/小球均值接近，节奏判断中性。"
    else:
        points = max_points
        side = "大球" if avg_over < avg_under else "小球"
        reason = f"大小球主盘口 {summary.get('line')}，市场略偏向{side}。"
    return points, reason


def correct_score_points(match, favorite, api_football_data, max_points):
    summary = api_correct_score_summary(api_football_data)
    hot = summary.get("hot") or []
    if not hot:
        return 0, "真实波胆盘口缺失。"
    home_favorite = favorite == "home_win"
    support = 0
    for item in hot[:5]:
        score = str(item.get("score") or "")
        try:
            left, right = [int(part) for part in score.split(":", 1)]
        except (ValueError, TypeError):
            continue
        if (home_favorite and left > right) or ((not home_favorite) and right > left):
            support += 1
    ratio = support / min(5, len(hot))
    if ratio >= 0.8:
        points = max_points
    elif ratio >= 0.6:
        points = round(max_points * 0.75)
    elif ratio >= 0.4:
        points = round(max_points * 0.50)
    else:
        points = round(max_points * 0.25)
    favorite_label = display_team(label_for_key(match, favorite))
    return points, f"热门波胆中有 {support}/{min(5, len(hot))} 个支持{favorite_label}方向。"


def margin_points(odds, max_points):
    margin = bookmaker_margin(odds)
    if margin is None:
        return 0, "无法计算庄家利润率。", None
    if margin <= 0.04:
        points = max_points
        label = "抽水较低"
    elif margin <= 0.07:
        points = round(max_points * 0.75)
        label = "抽水正常"
    elif margin <= 0.10:
        points = round(max_points * 0.45)
        label = "抽水偏高"
    else:
        points = round(max_points * 0.20)
        label = "抽水过高"
    return points, f"庄家利润率约 {margin * 100:.1f}%，{label}。", margin


def actual_edge_points(summary):
    avg_ev_lift = summary.get("avg_ev_lift")
    weighted_ev_lift = summary.get("weighted_ev_lift", avg_ev_lift)
    best_ev_lift = summary.get("best_ev_lift") or 0
    positive_count = summary.get("positive_ev_count", 0)
    core_positive = summary.get("core_positive_count", 0)
    recommended_count = summary.get("recommended_count", 0)
    if weighted_ev_lift is None:
        return 0, "未输入可比较的实际赔率。"
    points = 0
    points += min(14, positive_count * 4)
    points += min(9, core_positive * 3)
    if best_ev_lift >= 0.06:
        points += 8
    elif best_ev_lift >= 0.03:
        points += 5
    elif best_ev_lift > 0:
        points += 3
    if weighted_ev_lift >= 0.02:
        points += 4
    elif weighted_ev_lift >= 0:
        points += 2
    elif weighted_ev_lift < -0.03:
        points -= 8
    points = clamp(points, 0, 45)
    return (
        points,
        f"{positive_count}/{recommended_count} 个推荐项为正EV，核心盘口正EV {core_positive} 个，"
        f"最佳EV提升 {best_ev_lift * 100:.1f}%，覆盖率加权EV {weighted_ev_lift * 100:+.1f}%。",
    )


def recommendation_coverage_points(summary):
    count = summary.get("recommended_count", 0)
    points = {5: 15, 4: 13, 3: 11, 2: 8, 1: 5}.get(count, 0)
    if count:
        reason = f"五个投注位置中有 {count} 个达到推荐阈值。"
    else:
        reason = "实际赔率输入后，暂未形成达到阈值的推荐位置。"
    return points, reason


def polymarket_aux_points(match, odds, polymarket):
    return 0, "API-Football 单一来源模式下不启用二级市场辅助项。", None


def odds_value_from_actual_odds(match, odds, polymarket, api_football_data, actual_odds, distribution=None):
    slots = build_recommendation_slots(match, odds, api_football_data, actual_odds, distribution)
    summary = actual_odds_summary(slots)
    avg_edge = summary.get("avg_edge") if summary.get("recommended_count") else None
    avg_ev_lift = summary.get("avg_ev_lift") if summary.get("recommended_count") else None
    weighted_ev_lift = summary.get("weighted_ev_lift") if summary.get("recommended_count") else None
    edge_score, edge_reason = actual_edge_points(summary)
    coverage_score, coverage_reason = recommendation_coverage_points(summary)

    favorite = favorite_key_from_odds(odds)
    handicap_summary = api_handicap_summary(api_football_data)
    handicap_raw, handicap_reason = handicap_direction_points(favorite, handicap_summary, 12) if favorite else (0, "缺少胜平负主方向。")
    structure_score = clamp(handicap_raw, 0, 12)

    margin_score_raw, margin_reason, margin = margin_points(odds, 8)
    score = clamp(edge_score + coverage_score + structure_score + margin_score_raw)
    components = [
        {
            "name": "实际赔率优势",
            "points": edge_score,
            "max_points": 45,
            "reason": edge_reason,
        },
        {
            "name": "推荐覆盖质量",
            "points": coverage_score,
            "max_points": 20,
            "reason": coverage_reason,
        },
        {
            "name": "盘口结构",
            "points": structure_score,
            "max_points": 15,
            "reason": handicap_reason,
        },
        {
            "name": "庄家利润率",
            "points": margin_score_raw,
            "max_points": 10,
            "reason": margin_reason,
        },
    ]
    rating = value_rating(score)
    best_edge = summary.get("best_edge")
    odds_probs = odds_probabilities(odds) or {}
    favorite = max(odds_probs, key=odds_probs.get) if odds_probs else None
    label = label_for_key(match, favorite) if favorite else "-"
    return {
        "score": score,
        "rating": rating,
        "label": label,
        "market_probability": odds_probs.get(favorite) if favorite else None,
        "model_probability": None,
        "difference": 0,
        "margin": margin,
        "components": components,
        "actual_odds": {
            "recommended_count": summary.get("recommended_count", 0),
            "avg_edge": avg_edge,
            "best_edge": best_edge,
            "avg_ev_lift": avg_ev_lift,
            "weighted_ev_lift": weighted_ev_lift,
            "best_ev_lift": summary.get("best_ev_lift"),
        },
        "reason": (
            f"已输入实际赔率，赔率价值主要由EV提升、实际赔率优势和盘口价值因子决定；"
            f"覆盖率加权EV {weighted_ev_lift * 100:+.1f}%。"
            if weighted_ev_lift is not None
            else "已输入实际赔率，但当前推荐位置没有形成可比较优势。"
        ),
    }


def odds_value_analysis(match, odds, polymarket, api_football_data=None, actual_odds=None, distribution=None):
    if (actual_odds or {}).get("items"):
        return odds_value_from_actual_odds(match, odds, polymarket, api_football_data, actual_odds, distribution)

    odds_probs = odds_probabilities(odds)
    if not odds_probs:
        score = 35
        return {
            "score": score,
            "rating": value_rating(score),
            "label": "-",
            "market_probability": None,
            "model_probability": None,
            "difference": 0,
            "margin": bookmaker_margin(odds),
            "components": [
                {"name": "单一来源状态", "points": 0, "max_points": 10, "reason": "API-Football 单一来源模式不启用二级市场价差。"},
                {"name": "盘口一致性", "points": 12, "max_points": 30, "reason": "缺少完整市场数据，按中性偏低处理。"},
                {"name": "亚洲盘结构", "points": 0, "max_points": 25, "reason": "亚洲让球盘缺失。"},
                {"name": "波胆结构", "points": 0, "max_points": 20, "reason": "真实波胆盘口缺失。"},
                {"name": "庄家利润率", "points": 8, "max_points": 15, "reason": "按中性抽水处理。"},
            ],
            "reason": "缺少模型概率与市场概率的可比数据，赔率价值按中性偏低处理。",
        }

    favorite = max(odds_probs, key=odds_probs.get)
    handicap_summary = api_handicap_summary(api_football_data)
    handicap_points, handicap_reason = handicap_direction_points(favorite, handicap_summary, 25)

    totals_points, totals_reason = totals_structure_points(odds, 8)
    h_consistency = 14 if handicap_points >= 20 else 8 if handicap_points >= 10 else 3
    winner_strength = 8 if odds_probs[favorite] >= 0.60 else 5 if odds_probs[favorite] >= 0.50 else 2
    consistency_points = clamp(h_consistency + totals_points + winner_strength, 0, 30)
    consistency_reason = f"胜平负主方向为{label_for_key(match, favorite)}。{handicap_reason} {totals_reason}"

    correct_points, correct_reason = correct_score_points(match, favorite, api_football_data, 20)
    margin_score, margin_reason, margin = margin_points(odds, 15)

    single_source_points = 10
    score = clamp(single_source_points + consistency_points + handicap_points + correct_points + margin_score)
    components = [
        {
            "name": "单一来源状态",
            "points": single_source_points,
            "max_points": 10,
            "reason": "使用 API-Football 赔率作为唯一市场数据源。",
        },
        {
            "name": "盘口一致性",
            "points": consistency_points,
            "max_points": 30,
            "reason": consistency_reason,
        },
        {
            "name": "亚洲盘结构",
            "points": handicap_points,
            "max_points": 25,
            "reason": handicap_reason,
        },
        {
            "name": "波胆结构",
            "points": correct_points,
            "max_points": 20,
            "reason": correct_reason,
        },
        {
            "name": "庄家利润率",
            "points": margin_score,
            "max_points": 15,
            "reason": margin_reason,
        },
    ]
    rating = value_rating(score)
    return {
        "score": score,
        "rating": rating,
        "label": label_for_key(match, favorite),
        "market_probability": odds_probs[favorite],
        "model_probability": None,
        "difference": 0,
        "margin": margin,
        "components": components,
        "reason": (
            f"{label_for_key(match, favorite)}方向：API-Football 市场概率 {odds_probs[favorite] * 100:.1f}%；"
            f"盘口、波胆与抽水综合得分 {score} / 100。"
        ),
    }

def market_value_component(match, odds, polymarket):
    tpb = true_probability_base(odds)
    score = investment_score_from_tpb(tpb)
    points = next(
        (item["points"] for item in direction_confidence(match, odds, polymarket, {}).get("components", []) if item["name"] == "TPB概率基础"),
        score,
    )
    return {
        "name": "TPB投资分",
        "points": points,
        "max_points": 100,
        "reason": f"投资分 {score} / 100，只由 TPB 和博彩公司离散度派生。",
    }


def market_disagreement_component(match, odds, polymarket):
    gap = biggest_probability_gap(match, odds, polymarket)
    if not gap:
        return {
            "name": "市场分歧",
            "points": 0,
            "max_points": 20,
            "reason": "API-Football 单一来源模式下不启用二级市场分歧比较。",
        }
    points = score_from_gap(gap["gap"], {"low": 8, "medium": 14, "high": 20})
    return {
        "name": "市场分歧",
        "points": points,
        "max_points": 20,
        "reason": f"二级市场与赔率市场最大差异为 {gap['gap'] * 100:.1f}%。",
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
    tpb = true_probability_base(odds)
    total = investment_score_from_tpb(tpb)
    components = [market_value_component(match, odds, polymarket)]
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


def direction_confidence(match, odds, polymarket, api_football_data):
    tpb = true_probability_base(odds)
    odds_probs = tpb.get("probabilities")
    if not odds_probs:
        return {
            "score": 0,
            "level": "观望",
            "components": [],
            "investment_score": 0,
            "market_direction": "No API-Football 1X2 probability",
            "true_probability_base": tpb,
            "reason": "缺少 API-Football 1X2 赔率，无法形成 TPB。",
        }

    favorite = max(odds_probs, key=odds_probs.get)
    favorite_label = display_team(label_for_key(match, favorite))
    favorite_probability = odds_probs[favorite]
    score = betting_confidence_from_tpb(tpb)
    investment_score = investment_score_from_tpb(tpb)
    market_direction = market_direction_from_tpb(tpb, {
        "home_win": f"{favorite_label}占优",
        "draw": "平衡 / 平局权重高",
        "away_win": f"{favorite_label}占优",
    })
    components = [
        {
            "name": "TPB概率基础",
            "points": score,
            "max_points": 100,
            "reason": (
                f"{favorite_label} TPB {favorite_probability * 100:.1f}%，"
                "信心由 TPB 熵值唯一派生。"
            ),
        },
        {
            "name": "博彩公司离散度",
            "points": clamp(100 - (tpb.get("market_dispersion") or 0) * 100),
            "max_points": 100,
            "reason": f"博彩公司概率离散度 {((tpb.get('market_dispersion') or 0) * 100):.1f}%。",
        },
    ]
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
    summary = f"TPB 显示 {favorite_label} 为最高概率方向，投注信心由熵值派生为{level}。"
    return {
        "score": score,
        "level": level,
        "components": components,
        "investment_score": investment_score,
        "market_direction": market_direction,
        "true_probability_base": tpb,
        "summary": summary,
        "reason": "方向把握只由 API-Football 1X2 TPB 决定；盘口与波胆不再参与方向评分。",
    }


def participation_advice(direction, odds_value, upset):
    score = direction.get("investment_score", direction.get("score", 0))

    if score >= 90:
        advice = "强烈参与"
    elif score >= 80:
        advice = "建议参与"
    elif score >= 60:
        advice = "小仓参与"
    elif score >= 50:
        advice = "仅观察"
    else:
        advice = "放弃"

    return {
        "advice": advice,
        "reason": (
            f"参与建议只由 TPB 投资分 {score} / 100 派生。"
        ),
    }


def recommended_stake(direction, odds_value, participation):
    score = direction.get("investment_score", direction.get("score", 0))
    stake = stake_from_investment_score(score)
    return {
        **stake,
        "base": stake["amount"],
        "adjustment": 0,
    }


def final_recommendation(match, betting_opinion, contrarian, upset):
    winner = (betting_opinion or {}).get("match_winner", "No view").replace("Lean ", "")
    return {
        "bet": winner if winner != "No view" else "观察为主",
        "reason": [
            "最终推荐跟随 TPB 最高概率方向",
            "让球、逆向与爆冷指标不再改写主推荐",
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


def build_decision_engine(match, odds, polymarket, api_football_data, betting_opinion, actual_odds=None, distribution=None):
    direction = direction_confidence(match, odds, polymarket, api_football_data)
    investment_score = direction.get("investment_score", 0)
    odds_value = {
        "score": investment_score,
        "rating": "A" if investment_score >= 80 else "B" if investment_score >= 65 else "C" if investment_score >= 50 else "D",
        "components": direction.get("components", []),
        "reason": "赔率价值已并入 TPB 投资分，不再单独重复计分。",
    }
    disabled_score = {
        "score": 0,
        "level": "已停用",
        "meaning": "已停用",
        "direction": "-",
        "difference": 0,
        "reason": "Probability-first 架构下该旧评分不再参与决策。",
    }
    disagreement = dict(disabled_score)
    contrarian = dict(disabled_score)
    upset = dict(disabled_score)
    recent_form = dict(disabled_score)
    injury_impact = dict(disabled_score)
    elo = dict(disabled_score)
    team_value = dict(disabled_score)
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
        "value_rating_breakdown": odds_value.get("components", []),
        "value_rating_meaning": rating_meaning(odds_value["rating"], odds_value["score"]),
        "final_recommendation": final_recommendation(match, betting_opinion, contrarian, upset),
        "stake_suggestion": {
            "Conservative": stake["amount"],
            "Standard": stake["amount"],
            "Aggressive": stake["amount"],
        },
        "weights": {
            "TPB": "API-Football 胜平负博彩公司共识概率",
            "投注信心": "仅由 TPB 熵值派生",
            "投资分": "TPB 集中度、热门差值、平局/冷门概率和博彩公司离散度",
            "推荐仓位": "仅由投资分档位确定",
        },
    }
