from modules.pregame_content import team_cn


def clamp(value, low=0.03, high=0.75):
    return max(low, min(high, value))


def normalize(rows):
    total = sum(row["probability"] for row in rows)
    if total <= 0:
        return rows
    for row in rows:
        row["probability"] = row["probability"] / total
    return rows


def odds_probs(odds):
    if not odds.get("found"):
        return None
    return odds.get("implied_probabilities")


def poly_probs(polymarket):
    return None


def blended_probabilities(odds, polymarket):
    odds_data = odds_probs(odds)
    poly_data = poly_probs(polymarket)
    return odds_data


def consensus_line(markets):
    if not markets:
        return None
    counts = {}
    for market in markets:
        line = market.get("line")
        counts[line] = counts.get(line, 0) + 1
    return max(counts, key=counts.get)


def totals_bias(odds):
    markets = odds.get("over_under") or []
    line = consensus_line(markets)
    if line is None:
        return 0
    selected = [market for market in markets if market.get("line") == line]
    over = [market.get("over_odds") for market in selected if market.get("over_odds")]
    under = [market.get("under_odds") for market in selected if market.get("under_odds")]
    if not over or not under:
        return 0
    avg_over = sum(over) / len(over)
    avg_under = sum(under) / len(under)
    if avg_over < avg_under - 0.06:
        return 0.06
    if avg_under < avg_over - 0.06:
        return -0.05
    return 0


def handicap_signal(odds):
    markets = odds.get("asian_handicap") or []
    line = consensus_line(markets)
    if line is None:
        return 0
    return abs(float(line))


def build_result_distribution(match, odds, polymarket, match_context=None):
    probs = blended_probabilities(odds, polymarket)
    if not probs:
        return {
            "available": False,
            "source": "api_football",
            "main_path": "暂无 API-Football 胜平负概率",
            "rows": [],
            "overround": odds.get("bookmaker_margin") if odds else None,
        }
    home_prob = probs["home_win"]
    draw_prob = probs["draw"]
    away_prob = probs["away_win"]
    favorite_is_home = home_prob >= away_prob
    favorite = team_cn(match["home_cn"] if favorite_is_home else match["away_cn"])
    underdog = team_cn(match["away_cn"] if favorite_is_home else match["home_cn"])
    favorite_prob = max(home_prob, away_prob)
    underdog_prob = min(home_prob, away_prob)
    line_strength = handicap_signal(odds)
    goal_bias = totals_bias(odds)

    small_share = 0.42
    two_goal_share = 0.34
    big_share = 0.24

    if line_strength >= 1.25:
        two_goal_share += 0.08
        big_share += 0.10
        small_share -= 0.18
    elif line_strength >= 0.75:
        two_goal_share += 0.05
        big_share += 0.04
        small_share -= 0.09

    if goal_bias > 0:
        big_share += goal_bias
        small_share -= goal_bias / 2
    elif goal_bias < 0:
        small_share += abs(goal_bias)
        big_share -= abs(goal_bias)

    draw_zone = clamp(draw_prob)
    underdog_zone = clamp(underdog_prob * 0.55, 0.02, 0.25)
    favorite_mass = clamp(favorite_prob + underdog_prob * 0.2, 0.35, 0.88)

    rows = [
        {
            "label": "平局区间",
            "probability": draw_zone,
            "meaning": "比赛进入低分差或胶着路径。",
        },
        {
            "label": f"{favorite}小胜（1球）",
            "probability": favorite_mass * small_share,
            "meaning": "市场主路径之一，强队赢但不打穿深盘。",
        },
        {
            "label": f"{favorite}赢2球",
            "probability": favorite_mass * two_goal_share,
            "meaning": "盘口边界路径，决定让球盘输赢。",
        },
        {
            "label": f"{favorite}赢3球以上",
            "probability": favorite_mass * big_share,
            "meaning": "强队大胜路径，过去版本容易低估。",
        },
        {
            "label": f"{underdog}不败",
            "probability": underdog_zone,
            "meaning": "爆冷或热门方向失效路径。",
        },
    ]
    rows = normalize(rows)
    rows.sort(key=lambda row: row["probability"], reverse=True)
    main_path = rows[0]["label"]
    boundary_path = f"{favorite}赢2球"
    extreme_path = f"{favorite}赢3球以上"

    return {
        "available": True,
        "favorite": favorite,
        "underdog": underdog,
        "rows": rows,
        "risk_exposure": build_risk_exposure(favorite, underdog),
        "main_path": main_path,
        "boundary_path": boundary_path,
        "extreme_path": extreme_path,
        "explanation": "基于 API-Football 胜平负概率、亚洲让球盘、大小球盘口与真实波胆盘口的路径分布。",
    }


def build_risk_exposure(favorite, underdog):
    return {
        "example_bet": f"{favorite} -1.5",
        "lose_paths": [
            f"{favorite}只赢1球",
            "平局",
            f"{underdog}胜",
        ],
        "meaning": "如果下注深盘，风险主要来自强队小胜、平局和弱队爆冷，而不是独赢方向本身。",
    }


def scenario_level(probability):
    if probability >= 0.26:
        return "高"
    if probability >= 0.14:
        return "中"
    return "低"


def build_extreme_scenarios(distribution):
    rows = distribution.get("rows") or []
    big = next((row for row in rows if "3球以上" in row["label"]), None)
    upset = next((row for row in rows if "不败" in row["label"]), None)
    scenarios = []
    if big:
        scenarios.append({
            "name": big["label"],
            "level": scenario_level(big["probability"]),
            "probability": big["probability"],
            "note": "强队效率较高或早早领先时，比赛可能脱离常规盘口区间。",
        })
    if upset:
        scenarios.append({
            "name": upset["label"],
            "level": scenario_level(upset["probability"]),
            "probability": upset["probability"],
            "note": "热门方向拥挤、早段不进球或弱队反击效率提升时需要关注。",
        })
    return scenarios


def betting_structure(distribution):
    return [
        {"layer": "主逻辑", "share": 0.60, "path": distribution.get("main_path", "-")},
        {"layer": "边界逻辑", "share": 0.25, "path": distribution.get("boundary_path", "-")},
        {"layer": "极端逻辑", "share": 0.15, "path": distribution.get("extreme_path", "-")},
    ]
