"""Legacy strategy compatibility helpers.

TPB is the only active decision engine. This module no longer exposes old
ranking or observation-mode decision functions.
"""


def clamp(value, low=0, high=100):
    return max(low, min(high, round(value)))


def round_to_hundred(value):
    return int(round(value / 100) * 100)


def confidence_reason(decision, odds):
    direction = decision.get("direction_confidence") or {}
    score = direction.get("score", decision.get("final_confidence_score", 0))
    if not odds.get("found"):
        return "信心受限于赔率盘口数据不足。"
    return direction.get("reason", f"方向把握 {score} / 100。")


def market_disagreement_reason(disagreement):
    if disagreement["score"] >= 67:
        return "不同市场存在明显分歧，说明当前定价并不统一。"
    if disagreement["score"] >= 34:
        return "Polymarket 与传统赔率存在一定差异，需要观察临场变化。"
    return "Polymarket 与传统赔率观点基本一致。"


def item_path_consistency(item):
    if item.get("type") == "correct_score":
        raw = 55 + item.get("path_consistency_score", 0) - item.get("path_conflict_penalty", 0)
        return max(0, min(1, raw / 100))
    if item.get("type") in {"winner", "handicap"}:
        return 0.88
    if item.get("type") == "total":
        return 0.58
    return 0.45


def strategy_path_consistency(items):
    if not items:
        return 0
    weights = [max(item.get("amount", 0), 1) for item in items]
    weighted = sum(item_path_consistency(item) * weight for item, weight in zip(items, weights))
    return weighted / sum(weights)


def rank_key_with_eligibility(strategy):
    return (strategy.get("investment_score", strategy.get("score", 0)),)
