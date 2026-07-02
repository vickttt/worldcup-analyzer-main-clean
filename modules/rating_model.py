from modules.probability_base import true_probability_base


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
    return true_probability_base(odds).get("probabilities")


def get_polymarket_probabilities(polymarket):
    return None


def rate_opportunity(probabilities, polymarket, news, odds=None):
    odds_probs = get_odds_probabilities(odds or {})
    polymarket_probs = get_polymarket_probabilities(polymarket)

    if not odds_probs:
        return {
            "grade": "放弃",
            "risk_level": "高",
            "summary": "API-Football 未返回可用胜平负概率。",
            "recommendation": "No bet",
            "value_signal": "No",
            "reason": "缺少 API-Football 市场数据。",
        }

    best_direction = max(odds_probs, key=odds_probs.get)
    best_probability = odds_probs[best_direction]
    recommendation = label_for_direction(best_direction)

    if best_probability >= 0.62:
        grade = "A"
        risk_level = "中"
        value_signal = "API-Football direction signal"
    elif best_probability >= 0.55:
        grade = "B"
        risk_level = "中"
        value_signal = "API-Football direction signal"
    elif best_probability >= 0.48:
        grade = "C"
        risk_level = "中高"
        value_signal = "No"
    else:
        grade = "放弃"
        risk_level = "高"
        value_signal = "No"
        recommendation = "No bet"

    reason = (
        f"API-Football 对 {label_for_direction(best_direction)} 的隐含概率为 "
        f"{best_probability * 100:.1f}%。"
    )

    return {
        "grade": grade,
        "risk_level": risk_level,
        "summary": reason,
        "recommendation": recommendation,
        "value_signal": value_signal,
        "reason": reason,
        "odds_probabilities": odds_probs,
        "probability_gap": 0,
    }
