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

def hybrid_v2_status_label(status):
    labels = {
        "Scenario-Supported Aggressive Upside": "剧本支持上行",
        "Watch: Small Upside Sleeve": "小仓观察",
        "Uncontrolled Tail": "无控制尾部",
        "Blocked Tail": "尾部阻断",
        "No Sleeve": "无上行袖仓",
    }
    return labels.get(status, "-")

def match_betting_score(strategies):
    if not strategies:
        return {
            "score": 0,
            "decision": "不建议投注",
            "reason": "没有可用组合，无法形成投注判断。",
            "positive_reasons": [],
            "negative_reasons": ["没有可用组合，无法形成投注判断。"],
            "final_judgement": "当前缺少可执行组合，不建议下注。",
            "risk_mode": "Balanced",
        }
    official = strategies[0]
    shadow = official.get("shadow") or {}
    hybrid_v2 = official.get("hybrid_v2") or {}
    max_loss = float(official.get("max_loss") or 0)
    legacy_score = float(official.get("score") or 0)
    consistency = float(official.get("consistency_score") or 0) * 100
    if not consistency:
        consistency = 60

    score = 50
    positive_reasons = []
    negative_reasons = []

    score += min(20, max(0, (consistency - 55) * 0.45))
    score += min(15, max(0, (legacy_score - 60) * 0.30))
    if consistency >= 75:
        positive_reasons.append(f"剧本一致性较高（{round(consistency)}分）")
    elif consistency < 60:
        negative_reasons.append(f"剧本一致性不足（{round(consistency)}分）")
    else:
        positive_reasons.append(f"剧本一致性可接受（{round(consistency)}分）")

    if legacy_score >= 75:
        positive_reasons.append(f"综合评分较强（{round(legacy_score)}）")
    elif legacy_score < 55:
        negative_reasons.append(f"综合评分偏弱（{round(legacy_score)}）")

    verdict = shadow.get("shadow_verdict")
    if verdict == "Agreement":
        score += 10
        positive_reasons.append("Legacy 与 Scenario 判断一致")
    elif verdict == "Watch":
        score += 4
        positive_reasons.append("Scenario 仅提示观察，没有直接阻断")
    elif verdict == "Disagreement":
        score -= 10
        negative_reasons.append("Legacy 与 Scenario 存在分歧")
    elif verdict == "Blocker Candidate":
        score -= 25
        negative_reasons.append("Scenario 标记为高风险观察")

    sleeve_status = hybrid_v2.get("sleeve_status")
    if sleeve_status == "Scenario-Supported Aggressive Upside":
        score += 4
        positive_reasons.append("上行袖仓有剧本支持")
    elif sleeve_status == "Watch: Small Upside Sleeve":
        score += 1
        positive_reasons.append("上行袖仓仅小仓观察")
    elif sleeve_status in {"Uncontrolled Tail", "Blocked Tail"}:
        score -= 18
        negative_reasons.append("尾部风险未被充分控制")

    if max_loss <= 500:
        score += 8
        positive_reasons.append(f"最大亏损可控（约{int(max_loss)}元）")
    elif max_loss <= 1000:
        score += 3
        positive_reasons.append(f"最大亏损处于可接受区间（约{int(max_loss)}元）")
    elif max_loss >= 1600:
        score -= 12
        negative_reasons.append(f"最大亏损偏高（约{int(max_loss)}元）")

    score = clamp(score, 0, 100)
    if score >= 80:
        decision = "值得投注"
        final_judgement = "主组合具备较好的剧本一致性和风险控制，可以作为正式下注候选。"
    elif score >= 60:
        decision = "小注观察"
        final_judgement = "可以小仓参与，但 Scenario 或风险信号仍需要观察。"
    else:
        decision = "不建议投注"
        final_judgement = "当前组合信号不足或风险过高，不适合作为正式下注。"

    reasons = []
    reasons.append(f"剧本一致性 {round(consistency)} 分")
    reasons.append(f"Shadow Verdict: {shadow_verdict_label(verdict)}")
    reasons.append(f"Sleeve Status: {hybrid_v2_status_label(sleeve_status)}")
    reasons.append(f"最大亏损约 {int(max_loss)} 元")
    return {
        "score": score,
        "decision": decision,
        "reason": "；".join(reasons),
        "positive_reasons": positive_reasons or ["暂无明显加分项"],
        "negative_reasons": negative_reasons or ["暂无明显扣分项"],
        "final_judgement": final_judgement,
        "risk_mode": "Balanced",
    }

def recommended_stake_mvp(match_score):
    score = match_score.get("score", 0)
    decision = match_score.get("decision")
    if decision == "不建议投注" or score < 50:
        amount = 0
        amount_rule = "0元：不建议投注，分数不足或风险信号过重。"
    elif score < 60:
        amount = 300
        amount_rule = "300元：边缘观察局，只允许极小仓验证判断。"
    elif score < 70:
        amount = 500
        amount_rule = "500元：小注观察，剧本成立但信心不足。"
    elif score < 80:
        amount = 800
        amount_rule = "800元：普通可投，仍需控制最大亏损。"
    elif score < 90:
        amount = 1200
        amount_rule = "1200元：高信心区间，要求剧本和风险同时过关。"
    else:
        amount = 1500
        amount_rule = "1500元：极高信心上限，本阶段不自动建议超过1500元。"
    amount = min(2000, max(0, round_to_hundred(amount)))
    if amount == 0:
        reason = "当前分数不足或风险较高，不建议下注。"
    elif amount <= 500:
        reason = "观察局，仅建议小金额验证判断。"
    elif amount <= 1000:
        reason = "普通可投，仍需控制风险。"
    elif amount <= 1500:
        reason = "高信心区间，但仍受最大亏损和剧本一致性约束。"
    else:
        reason = "极高信心区间，仅在严格条件满足时使用。"
    return {
        "amount": amount,
        "risk_mode": match_score.get("risk_mode", "Balanced"),
        "amount_rule": amount_rule,
        "reason": f"{reason} {match_score.get('reason', '')}",
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
    ev_yield,
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
    # 组合评分统一按五项权重计算：
    # EV/ROI 30%，风险控制 20%，剧本一致性 30%，赔率价值 10%，组合简洁度 10%。
    if ev_yield >= 0.08:
        ev_roi_score = 100
    elif ev_yield >= 0.04:
        ev_roi_score = 85
    elif ev_yield >= 0.01:
        ev_roi_score = 70
    elif ev_yield >= -0.02:
        ev_roi_score = 50
    elif ev_yield >= -0.06:
        ev_roi_score = 25
    else:
        ev_roi_score = 5

    loss_ratio = max_loss / total_stake if total_stake else 1
    if loss_ratio <= 0.35:
        loss_score = 100
    elif loss_ratio <= 0.55:
        loss_score = 80
    elif loss_ratio <= 0.75:
        loss_score = 55
    elif loss_ratio <= 0.95:
        loss_score = 30
    else:
        loss_score = 10
    concentration_penalty = min(30, concentration * 30)
    risk_control_score = clamp(loss_score - concentration_penalty)

    script_consistency_score = clamp(
        consistency_score * 55
        + direction_alignment * 25
        + strategic_value * 20
    )

    odds_value_score = clamp(ev_roi_score * 0.70 + max(0, min(100, risk_reward * 25)) * 0.30)

    if concentration <= 0.25:
        simplicity_score = 100
    elif concentration <= 0.45:
        simplicity_score = 80
    elif concentration <= 0.65:
        simplicity_score = 60
    elif concentration <= 0.85:
        simplicity_score = 38
    else:
        simplicity_score = 20

    total = round(
        ev_roi_score * 0.30
        + risk_control_score * 0.20
        + script_consistency_score * 0.30
        + odds_value_score * 0.10
        + simplicity_score * 0.10
    )
    return clamp(total), {
        "EV/ROI": round(ev_roi_score * 0.30),
        "风险控制": round(risk_control_score * 0.20),
        "剧本一致性": round(script_consistency_score * 0.30),
        "赔率价值": round(odds_value_score * 0.10),
        "组合简洁度": round(simplicity_score * 0.10),
    }

def rank_key_with_eligibility(strategy):
    eligibility = strategy.get("rank1_eligibility") or {}
    gate = strategy.get("risk_gate") or {}
    exposure = strategy.get("correct_score_exposure") or {}
    eligible = bool(eligibility.get("rank1_eligible"))
    risk_rank = {"LOW": 3, "MEDIUM": 2, "HIGH": 1, "CRITICAL": 0}.get(gate.get("risk_level"), 1)
    exposure_penalty = float(exposure.get("stake_share") or 0)
    return (
        1 if eligible else 0,
        risk_rank,
        -exposure_penalty,
        strategy.get("score", 0),
    )
