"""Read-only portfolio shadow helpers.

This module mirrors selected portfolio allocation and stake-sizing rules for
observation only. It is intentionally not imported by the application runtime.
"""

from __future__ import annotations

from copy import deepcopy


def clamp(value, low=0, high=100):
    return max(low, min(high, value))


def round_to_hundred(value):
    return int(round(value / 100.0) * 100)


def recommended_total_stake(decision):
    stake = (decision or {}).get("recommended_stake") or {}
    return stake.get("amount", 0), stake.get("reason", "推荐仓位暂不可用。")


def stake_amounts(combo, decision):
    total, _ = recommended_total_stake(decision or {})
    rows = []
    recommended_rows = []
    for item in combo or []:
        effective_odds = item.get("effective_odds") or item.get("standard_odds") or item.get("odds")
        amount = round_to_hundred(total * item.get("share", 0)) if item.get("recommended") else 0
        row = {
            **item,
            "odds": effective_odds,
            "amount": amount,
        }
        rows.append(row)
        if row.get("recommended"):
            recommended_rows.append(row)

    difference = total - sum(item.get("amount", 0) for item in recommended_rows)
    if recommended_rows and difference:
        target = max(recommended_rows, key=lambda item: item.get("share", 0))
        target["amount"] = max(0, target.get("amount", 0) + difference)
    return rows


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
    # Mirrors modules.strategy.core.strategy_score for shadow observation only.
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


def strategy_weight(item):
    if item.get("path_probability") is not None:
        return max(0.05, item.get("path_probability", 0))
    if item.get("type") == "winner":
        return 1.25
    if item.get("type") == "handicap":
        return 1.15
    if item.get("type") == "total":
        return 0.90
    if item.get("type") == "correct_score":
        return 0.80
    return 0.50


def shadow_bet_correlation(first, second):
    first_type = first.get("type")
    second_type = second.get("type")
    pair = {first_type, second_type}
    if first_type == second_type == "correct_score":
        return 0.35
    if first_type == second_type:
        return 1.0
    if pair == {"winner", "handicap"}:
        return 0.90
    if pair == {"winner", "correct_score"}:
        return 0.95
    if pair == {"handicap", "correct_score"}:
        return 0.88
    if pair == {"winner", "total"}:
        return 0.40
    if pair == {"handicap", "total"}:
        return 0.45
    if pair == {"total", "correct_score"}:
        return 0.55
    return 0.30


def correlation_adjusted_weight(item, items):
    base = strategy_weight(item)
    score_boost = max(item.get("score", 50), 1) / 70
    ev_boost = 1 + max(item.get("ev_lift") or 0, 0) * 4
    coverage_boost = 0.75 + min(item.get("coverage_rate") or 0, 0.60)
    peers = [peer for peer in items if peer is not item]
    avg_corr = sum(shadow_bet_correlation(item, peer) for peer in peers) / len(peers) if peers else 0
    correlation_penalty = 1 - avg_corr * 0.42
    return max(0.03, base * score_boost * ev_boost * coverage_boost * correlation_penalty)


def enforce_correct_score_floor(items, total_stake):
    correct_items = [item for item in items if item.get("type") == "correct_score"]
    other_items = [item for item in items if item.get("type") != "correct_score"]
    if not correct_items or not other_items or not total_stake:
        return items
    current = sum(item.get("amount", 0) for item in correct_items)
    target = max(100, round_to_hundred(total_stake * 0.16))
    if current >= target:
        return items
    needed = target - current
    removable = sum(max(0, item.get("amount", 0) - 100) for item in other_items)
    transfer = min(needed, removable)
    if transfer <= 0:
        return items

    donor_total = sum(max(0, item.get("amount", 0) - 100) for item in other_items)
    removed = 0
    for item in other_items:
        capacity = max(0, item.get("amount", 0) - 100)
        reduction = round_to_hundred(transfer * capacity / donor_total) if donor_total else 0
        reduction = min(capacity, reduction)
        item["amount"] -= reduction
        removed += reduction
    if removed < transfer and other_items:
        donor = max(other_items, key=lambda item: item.get("amount", 0))
        extra = min(donor.get("amount", 0) - 100, transfer - removed)
        donor["amount"] -= max(0, extra)
        removed += max(0, extra)

    correct_weight_total = sum(strategy_weight(item) for item in correct_items)
    added = 0
    for item in correct_items:
        addition = round_to_hundred(removed * strategy_weight(item) / correct_weight_total) if correct_weight_total else 0
        item["amount"] += addition
        added += addition
    if added != removed:
        correct_items[0]["amount"] += removed - added
    return items


def allocate_strategy_items(items, total_stake):
    if not items or not total_stake:
        return []
    shadow_items = [deepcopy(item) for item in items]
    weight_total = sum(correlation_adjusted_weight(item, shadow_items) for item in shadow_items)
    allocated = []
    for item in shadow_items:
        amount = round_to_hundred(total_stake * correlation_adjusted_weight(item, shadow_items) / weight_total) if weight_total else 0
        allocated.append({**item, "amount": amount})
    difference = total_stake - sum(item.get("amount", 0) for item in allocated)
    if allocated and difference:
        target = max(allocated, key=lambda item: correlation_adjusted_weight(item, shadow_items))
        target["amount"] = max(0, target.get("amount", 0) + difference)
    allocated = enforce_correct_score_floor(allocated, total_stake)
    for item in allocated:
        item["share"] = item.get("amount", 0) / total_stake if total_stake else 0
    return allocated


def item_shadow_row(item):
    amount = float(item.get("amount") or 0)
    return {
        "name": item.get("name") or item.get("selection") or "-",
        "type": item.get("type") or "-",
        "selection": item.get("selection"),
        "amount": amount,
        "share": item.get("share"),
        "score": item.get("score"),
        "ev_lift": item.get("ev_lift"),
        "coverage_rate": item.get("coverage_rate"),
        "path_consistency": item_path_consistency(item),
        "shadow_weight": correlation_adjusted_weight(item, [item]),
    }


def strategy_capital_summary(strategy):
    items = strategy.get("items") or []
    active = [item for item in items if float(item.get("amount") or 0) > 0]
    total = sum(float(item.get("amount") or 0) for item in active)
    by_type = {}
    for item in active:
        by_type[item.get("type") or "-"] = by_type.get(item.get("type") or "-", 0) + float(item.get("amount") or 0)
    return {
        "name": strategy.get("name"),
        "display_name": strategy.get("rank_name"),
        "score": strategy.get("score"),
        "max_loss": strategy.get("max_loss"),
        "total_stake": total,
        "item_count": len(active),
        "by_type": by_type,
        "items": [item_shadow_row(item) for item in active],
        "rank_key": rank_key_with_eligibility(strategy),
        "risk_gate": strategy.get("risk_gate"),
        "correct_score_exposure": strategy.get("correct_score_exposure"),
    }


def shadow_match_summary(match_id, snapshot_entry):
    metadata = snapshot_entry.get("metadata") or {}
    decision = ((snapshot_entry.get("final_recommendation") or {}).get("decision") or {})
    strategies = ((snapshot_entry.get("strategy_ranking") or {}).get("strategies") or [])
    combo = ((snapshot_entry.get("portfolio_selection") or {}).get("recommendation_combo") or [])
    decision_stake, decision_reason = recommended_total_stake(decision)
    positive_combo = [item for item in combo if float(item.get("amount") or 0) > 0]
    top = strategies[0] if strategies else {}
    top_total = sum(float(item.get("amount") or 0) for item in (top.get("items") or []))
    return {
        "match_id": match_id,
        "match": metadata.get("match"),
        "scenario_role": metadata.get("scenario_role"),
        "decision_stake": decision_stake,
        "decision_stake_reason": decision_reason,
        "final_recommendation": (decision.get("final_recommendation") or {}).get("bet"),
        "top_strategy": strategy_capital_summary(top) if top else {},
        "strategy_count": len(strategies),
        "positive_combo_stake": sum(float(item.get("amount") or 0) for item in positive_combo),
        "positive_combo_items": [item_shadow_row(item) for item in positive_combo],
        "ranking_to_capital": [
            {
                "rank": index,
                "name": strategy.get("name"),
                "display_name": strategy.get("rank_name"),
                "score": strategy.get("score"),
                "max_loss": strategy.get("max_loss"),
                "stake": sum(float(item.get("amount") or 0) for item in (strategy.get("items") or [])),
                "risk_level": ((strategy.get("risk_gate") or {}).get("risk_level")),
                "correct_score_share": ((strategy.get("correct_score_exposure") or {}).get("stake_share")),
            }
            for index, strategy in enumerate(strategies, start=1)
        ],
        "stake_alignment": {
            "decision_vs_combo_delta": sum(float(item.get("amount") or 0) for item in positive_combo) - float(decision_stake or 0),
            "decision_vs_top_strategy_delta": top_total - float(decision_stake or 0),
        },
    }


def shadow_golden_v2(snapshot):
    return {
        match_id: shadow_match_summary(match_id, entry)
        for match_id, entry in (snapshot.get("matches") or {}).items()
    }
