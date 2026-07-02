"""Strategy scoring helpers extracted from app.py.

This module is a pure move refactor target; function bodies are intentionally unchanged.
"""


def clamp(value, low=0, high=100):
    return max(low, min(high, round(value)))

def round_to_hundred(value):
    return int(round(value / 100) * 100)

def confidence_reason(decision, odds):
    direction = decision.get("direction_confidence") or {}
    score = direction.get("score", decision["final_confidence_score"])
    if not odds.get("found"):
        return "信心受限于赔率盘口数据不足。"
    return direction.get("reason", f"方向把握 {score} / 100。")

def market_disagreement_reason(disagreement):
    if disagreement["score"] >= 67:
        return "不同市场存在明显分歧，说明当前定价并不统一。"
    if disagreement["score"] >= 34:
        return "Polymarket 与传统赔率存在一定差异，需要观察临场变化。"
    return "Polymarket 与传统赔率观点基本一致。"

def shadow_verdict_label(verdict):
    labels = {
        "Agreement": "一致",
        "Watch": "观察",
        "Disagreement": "分歧",
        "Blocker Candidate": "高风险观察",
    }
    return labels.get(verdict, "-")

def match_betting_score(strategies):
    return {
        "score": 0,
        "decision": "已停用",
        "reason": "legacy match_betting_score 已停用；TPB 决策由 probability_base / portfolio_engine 输出。",
        "positive_reasons": [],
        "negative_reasons": [],
        "final_judgement": "请读取 TPB score_layer / execution_layer。",
        "risk_mode": "TPB确定性",
    }

def recommended_stake_mvp(match_score):
    return {
        "amount": 0,
        "risk_mode": "已停用",
        "amount_rule": "legacy recommended_stake_mvp 已停用。",
        "reason": "推荐金额只允许来自 TPB investment_score -> stake_from_investment_score。",
    }

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
    base = weighted / sum(weights)
    severe_conflicts = [
        item for item in items
        if item.get("type") == "correct_score" and item.get("path_conflict_penalty", 0) >= 35
    ]
    if severe_conflicts:
        base = min(base, 0.35)
    return base

def strategy_score(
    legacy_yield,
    hit_rate,
    risk_reward,
    max_loss,
    total_stake,
    concentration,
    direction_alignment,
    strategic_value,
    consistency_score,
    sharpe_ratio,
    stability_score,
):
    return 0, {"状态": "legacy strategy_score 已停用；TPB 投资分是唯一决策评分。"}

def rank_key_with_eligibility(strategy):
    return (
        strategy.get("investment_score", strategy.get("score", 0)),
    )
