"""TPB-only execution layer.

Legacy portfolio optimization and coverage-path blocking have been removed
from the active decision path. The active chain is:

API-Football odds -> TPB -> confidence -> investment_score -> stake.
"""

import re

from modules.probability_base import (
    betting_confidence_breakdown,
    betting_confidence_from_tpb,
    investment_score_from_tpb,
    odds_data_quality,
    stake_from_investment_score,
    true_probability_base,
)


def clamp(value, low=0, high=100):
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    return max(low, min(high, round(number)))


def _fmt_line(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value or "")
    if abs(number) < 0.001:
        return "0"
    return f"{number:+g}"


def _parse_line_number(value, inherited_sign=None):
    text = str(value or "").strip()
    if not text:
        return None
    sign = -1 if text.startswith("-") else 1 if text.startswith("+") else inherited_sign or 1
    try:
        number = float(text.lstrip("+-"))
    except ValueError:
        return None
    return sign * abs(number)


def normalize_handicap_line(raw_line):
    text = str(raw_line or "").strip()
    text = text.replace("－", "-").replace("＋", "+").replace("—", "-").replace("–", "-")
    text = text.replace(" ", "")
    match = re.search(r"([+-]?\d+(?:\.\d+)?(?:/[+-]?\d+(?:\.\d+)?)?)", text)
    token = match.group(1) if match else text
    if not token:
        return {
            "original_line": "",
            "decimal_line": None,
            "split_legs": [],
            "display_line": "",
            "is_split": False,
        }

    if "/" in token:
        left, right = token.split("/", 1)
        left_value = _parse_line_number(left)
        inherited_sign = -1 if str(left).startswith("-") else 1
        right_value = _parse_line_number(right, inherited_sign=inherited_sign)
        if left_value is None or right_value is None:
            decimal_line = None
            split_legs = []
        elif abs(abs(left_value) - 1.0) < 0.001 and abs(abs(right_value) - 2.0) < 0.001:
            decimal_line = inherited_sign * 0.5
            split_legs = [decimal_line]
        else:
            split_legs = [left_value, right_value]
            decimal_line = sum(split_legs) / 2
    else:
        decimal_line = _parse_line_number(token)
        split_legs = [decimal_line] if decimal_line is not None else []

    is_split = len(split_legs) == 2 and abs(split_legs[0] - split_legs[1]) > 0.001
    display_line = token
    if decimal_line is not None:
        display_line = f"{token} ({_fmt_line(decimal_line)})" if is_split else _fmt_line(decimal_line)
    return {
        "original_line": token,
        "decimal_line": decimal_line,
        "split_legs": split_legs,
        "display_line": display_line,
        "is_split": is_split,
    }


def handicap_line_from_text(value):
    text = str(value or "")
    match = re.search(r"([+-]?\d+(?:\.\d+)?(?:/[+-]?\d+(?:\.\d+)?)?)", text.replace(" ", ""))
    return normalize_handicap_line(match.group(1)) if match else normalize_handicap_line("")


def settle_asian_handicap(score, side, split_legs, odds, stake=1):
    try:
        home_goals, away_goals = [int(part) for part in str(score).split(":", 1)]
        price = float(odds)
        amount = float(stake)
    except (TypeError, ValueError):
        return 0
    legs = [float(line) for line in (split_legs or []) if line is not None]
    if not legs:
        return -amount
    leg_stake = amount / len(legs)
    profit = 0
    for line in legs:
        adjusted = home_goals + line if side == "home" else away_goals + line
        opponent = away_goals if side == "home" else home_goals
        diff = adjusted - opponent
        if diff > 0.001:
            profit += leg_stake * (price - 1)
        elif diff < -0.001:
            profit -= leg_stake
    return profit


def normalize_score(value):
    text = str(value or "").strip().replace("：", ":").replace(" - ", ":").replace("-", ":")
    text = re.sub(r"\s+", "", text)
    match = re.search(r"(\d+):(\d+)", text)
    return f"{int(match.group(1))}:{int(match.group(2))}" if match else text


def total_side_and_line(value):
    text = str(value or "").lower()
    line_match = re.search(r"(\d+(?:\.\d+)?)", text)
    line = float(line_match.group(1)) if line_match else None
    if "under" in text or "小" in text:
        return "under", line
    if "over" in text or "大" in text:
        return "over", line
    return None, line


def build_bet_id(bet):
    bet_type = str((bet or {}).get("type") or "unknown").strip().lower()
    selection = str((bet or {}).get("selection") or (bet or {}).get("name") or "").strip().lower()
    return f"{bet_type}|{selection}"


def dedupe_bets(bets):
    seen = {}
    for bet in bets or []:
        seen[build_bet_id(bet)] = dict(bet)
    return list(seen.values())


def dedupe_portfolios(portfolios):
    return list(portfolios or [])


def _api_quality(odds=None, api_football_data=None):
    quality = odds_data_quality(odds, api_football_data)
    return quality["score"], quality["note"]


def _coverage_from_tpb(tpb):
    probabilities = (tpb or {}).get("probabilities") or {}
    if not probabilities:
        return {
            "needed": False,
            "type": "none",
            "reason": "TPB 不可用，无法生成覆盖建议。",
        }
    draw_probability = probabilities.get("draw", 0)
    favorite = max(probabilities, key=lambda key: probabilities.get(key, 0))
    upset_probability = min(probabilities.get("home_win", 0), probabilities.get("away_win", 0))
    favorite_gap = probabilities.get(favorite, 0) - sorted(probabilities.values(), reverse=True)[1]
    if draw_probability >= 0.30:
        return {
            "needed": True,
            "type": "draw",
            "reason": f"平局概率 {draw_probability * 100:.1f}% 偏高，覆盖优先考虑平局。",
        }
    if upset_probability >= 0.24:
        return {
            "needed": True,
            "type": "upset",
            "reason": f"弱侧概率 {upset_probability * 100:.1f}% 不低，覆盖优先考虑冷门方向。",
        }
    if favorite_gap < 0.10:
        return {
            "needed": True,
            "type": "balanced",
            "reason": f"热门差值 {favorite_gap * 100:.1f}% 较窄，覆盖优先考虑均衡路径。",
        }
    return {
        "needed": False,
        "type": "none",
        "reason": "TPB 未触发平局、冷门或均衡覆盖阈值。",
    }


def compute_match_investment_score(strategies, match=None, distribution=None, context=None):
    context = context or {}
    odds = context.get("odds") or {}
    api_football_data = context.get("api_football_data") or {}
    tpb = true_probability_base(odds)
    data_quality_score, data_quality_note = _api_quality(odds, api_football_data)
    score = investment_score_from_tpb(tpb)
    confidence = betting_confidence_from_tpb(tpb)
    breakdown = betting_confidence_breakdown(tpb)
    probabilities = tpb.get("probabilities") or {}
    ordered = sorted(probabilities.values(), reverse=True) if probabilities else [0, 0]
    favorite_edge = (ordered[0] - ordered[1]) * 100 if len(ordered) >= 2 else 0
    dispersion_score = clamp(100 - (tpb.get("market_dispersion") or 0) * 100)
    coverage = _coverage_from_tpb(tpb)
    if score >= 80:
        rating = "值得重点研究"
    elif score >= 65:
        rating = "可小仓参与"
    elif score >= 50:
        rating = "谨慎观察"
    else:
        rating = "不建议下注"
    return {
        "score": score,
        "rating": rating,
        "main_reason": f"TPB 投资分 {score}，最高方向差值 {favorite_edge:.1f}。",
        "key_risk": "主要风险来自 TPB 熵值偏高或博彩公司概率分歧。" if score < 65 else "主要风险在临场赔率变化。",
        "data_quality_score": data_quality_score,
        "data_quality_note": data_quality_note,
        "true_probability_base": tpb,
        "coverage": coverage,
        "confidence_breakdown": breakdown,
        "components": {
            "TPB信心": confidence,
            "热门差值": round(favorite_edge),
            "平局概率": round((probabilities.get("draw", 0) if probabilities else 0) * 100),
            "冷门概率": round(min(
                probabilities.get("home_win", 0),
                probabilities.get("away_win", 0),
            ) * 100) if probabilities else 0,
            "博彩公司一致性": dispersion_score,
        },
        "weights": {
            "TPB信心": "55%",
            "热门差值": "35%",
            "平局概率": "5%",
            "冷门概率": "5%",
            "博彩公司一致性": "扣分项",
        },
    }


def build_core_decision_layers(strategies, match=None, distribution=None, context=None):
    investment = compute_match_investment_score(strategies, match or {}, distribution or {}, context or {})
    tpb = investment.get("true_probability_base") or {}
    score_layer = {
        "tpb": tpb,
        "betting_confidence": investment.get("components", {}).get("TPB信心", 0),
        "confidence_breakdown": investment.get("confidence_breakdown") or {},
        "investment_score": investment.get("score", 0),
        "data_quality_note": investment.get("data_quality_note", "-"),
    }
    stake = stake_from_investment_score(score_layer["investment_score"])
    risk_decision = (
        "可下注"
        if stake.get("amount", 0) >= 500
        else "观察"
        if stake.get("amount", 0) > 0
        else "不下注"
    )
    execution_layer = {
        "stake": stake,
        "recommended_bet_size": stake.get("amount", 0),
        "risk_decision": risk_decision,
        "investment_rating": investment.get("rating", "不建议下注"),
    }
    explanation_layer = {
        "main_reason": investment.get("main_reason", "-"),
        "risk_explanation": investment.get("key_risk", "-"),
        "coverage_explanation": (investment.get("coverage") or {}).get("reason", "-"),
        "coverage": investment.get("coverage") or {},
        "components": investment.get("components") or {},
        "weights": investment.get("weights") or {},
    }
    return {
        "score_layer": score_layer,
        "execution_layer": execution_layer,
        "explanation_layer": explanation_layer,
    }


def compute_portfolio_score(strategy, match, distribution):
    return {
        "score": 0,
        "items": dedupe_bets((strategy or {}).get("items") or []),
        "score_components": {},
        "why": ["旧组合评分已停用；请读取 TPB score_layer。"],
    }


def compute_portfolio_marginal_utility(base_portfolio, candidate_variants, score_grid):
    return []


def portfolio_risk_gate(portfolio, score_grid=None, match_context=None):
    return {
        "passed": True,
        "risk_level": "诊断",
        "reason": "旧风险门控已停用；风险只作为 TPB 诊断展示，不阻断推荐。",
        "failed_paths": [],
    }


def rank1_eligibility_check(portfolio, match=None, distribution=None):
    return {
        "rank1_eligible": True,
        "eligible": True,
        "rank1_blockers": [],
        "summary": "旧 Rank #1 gate 已停用；TPB 投资分是唯一排序来源。",
    }


def portfolio_style_name(strategy, metrics=None):
    return "TPB 单一决策"


def generate_style_portfolios(combo, match, distribution):
    return []
