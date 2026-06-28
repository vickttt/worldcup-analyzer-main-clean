def normalize(values):
    total = sum(values.values())
    if total <= 0:
        return None
    return {key: value / total for key, value in values.items()}


def label_for_direction(direction):
    return {
        "home_win": "Home",
        "draw": "Draw",
        "away_win": "Away",
    }.get(direction, "Unknown")


def get_odds_probabilities(odds):
    if not odds.get("found"):
        return None
    probabilities = odds.get("implied_probabilities")
    if probabilities:
        return probabilities
    if all(odds.get(key) for key in ["home_win", "draw", "away_win"]):
        return normalize({
            "home_win": 1 / odds["home_win"],
            "draw": 1 / odds["draw"],
            "away_win": 1 / odds["away_win"],
        })
    return None


def get_polymarket_probabilities(polymarket):
    if not polymarket.get("found"):
        return None
    if not all(polymarket.get(key) is not None for key in ["home_win", "draw", "away_win"]):
        return None
    return normalize({
        "home_win": polymarket["home_win"],
        "draw": polymarket["draw"],
        "away_win": polymarket["away_win"],
    })


def rate_opportunity(probabilities, polymarket, news, odds=None):
    odds_probs = get_odds_probabilities(odds or {})
    polymarket_probs = get_polymarket_probabilities(polymarket)

    if not odds_probs and not polymarket_probs:
        return {
            "grade": "放弃",
            "risk_level": "高",
            "summary": "API-Football 和 Polymarket 均未返回可比较概率。",
            "recommendation": "No bet",
            "value_signal": "No",
            "reason": "缺少可比较市场数据。",
        }

    if not odds_probs:
        return {
            "grade": "C",
            "risk_level": "中高",
            "summary": "API-Football 未返回赔率，只能参考 Polymarket。",
            "recommendation": "Observe only",
            "value_signal": "No",
            "reason": "缺少博彩公司赔率，无法进行价差比较。",
        }

    if not polymarket_probs:
        return {
            "grade": "C",
            "risk_level": "中高",
            "summary": "Polymarket 未返回概率，只能参考 API-Football。",
            "recommendation": "Observe only",
            "value_signal": "No",
            "reason": "缺少预测市场价格，无法进行价差比较。",
        }

    diffs = {
        key: polymarket_probs[key] - odds_probs[key]
        for key in ["home_win", "draw", "away_win"]
    }
    best_direction = max(diffs, key=lambda key: abs(diffs[key]))
    best_gap = diffs[best_direction]
    abs_gap = abs(best_gap)
    recommendation = label_for_direction(best_direction)

    if abs_gap >= 0.10:
        grade = "A"
        risk_level = "中"
        value_signal = "Potential Value Opportunity"
    elif abs_gap >= 0.06:
        grade = "B"
        risk_level = "中"
        value_signal = "Potential Value Opportunity"
    elif abs_gap >= 0.03:
        grade = "C"
        risk_level = "中高"
        value_signal = "No"
    else:
        grade = "放弃"
        risk_level = "高"
        value_signal = "No"
        recommendation = "No bet"

    if best_gap > 0:
        reason = (
            f"Polymarket 对 {label_for_direction(best_direction)} 的概率 "
            f"比 API-Football 高 {abs_gap * 100:.1f} 个百分点。"
        )
    else:
        reason = (
            f"API-Football 对 {label_for_direction(best_direction)} 的隐含概率 "
            f"比 Polymarket 高 {abs_gap * 100:.1f} 个百分点。"
        )

    return {
        "grade": grade,
        "risk_level": risk_level,
        "summary": reason,
        "recommendation": recommendation,
        "value_signal": value_signal,
        "reason": reason,
        "odds_probabilities": odds_probs,
        "polymarket_probabilities": polymarket_probs,
        "probability_gap": best_gap,
    }
