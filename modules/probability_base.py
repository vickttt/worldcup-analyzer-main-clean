"""Canonical probability base for decision scoring.

TPB intentionally depends only on API-Football 1X2 prices. Everything exposed
here is a deterministic derivative of that normalized probability object.
"""

import math


OUTCOMES = ("home_win", "draw", "away_win")


def clamp(value, low=0, high=100):
    return max(low, min(high, round(value)))


def normalize(values):
    total = sum(float(values.get(key) or 0) for key in OUTCOMES)
    if total <= 0:
        return None
    return {key: float(values.get(key) or 0) / total for key in OUTCOMES}


def probabilities_from_decimal_odds(prices):
    if not prices or any(not prices.get(key) for key in OUTCOMES):
        return None
    raw = {}
    for key in OUTCOMES:
        try:
            price = float(prices.get(key))
        except (TypeError, ValueError):
            return None
        if price <= 1:
            return None
        raw[key] = 1 / price
    return normalize(raw)


def consensus_probabilities(rows):
    normalized_rows = []
    for row in rows or []:
        probs = probabilities_from_decimal_odds(row)
        if probs:
            normalized_rows.append(probs)
    if not normalized_rows:
        return None
    averaged = {
        key: sum(row[key] for row in normalized_rows) / len(normalized_rows)
        for key in OUTCOMES
    }
    return normalize(averaged)


def market_dispersion(rows, base=None):
    base = base or consensus_probabilities(rows)
    normalized_rows = []
    for row in rows or []:
        probs = probabilities_from_decimal_odds(row)
        if probs:
            normalized_rows.append(probs)
    if not base or len(normalized_rows) < 2:
        return 0
    total_deviation = 0
    for row in normalized_rows:
        total_deviation += sum(abs(row[key] - base[key]) for key in OUTCOMES) / len(OUTCOMES)
    return total_deviation / len(normalized_rows)


def true_probability_base(odds):
    odds = odds or {}
    rows = odds.get("match_winner_rows") or []
    probabilities = odds.get("true_probability_base") or consensus_probabilities(rows)
    if not probabilities:
        probabilities = probabilities_from_decimal_odds(odds)
    probabilities = normalize(probabilities or {})
    if not probabilities:
        return {
            "available": False,
            "probabilities": None,
            "home_win": None,
            "draw": None,
            "away_win": None,
            "source": "API-Football 胜平负赔率不可用",
            "market_dispersion": None,
        }
    dispersion = market_dispersion(rows, probabilities)
    return {
        "available": True,
        "probabilities": probabilities,
        "home_win": probabilities["home_win"],
        "draw": probabilities["draw"],
        "away_win": probabilities["away_win"],
        "source": "API-Football 胜平负博彩公司共识概率",
        "market_dispersion": dispersion,
    }


def entropy(probabilities):
    if not probabilities:
        return None
    value = 0
    for key in OUTCOMES:
        probability = float(probabilities.get(key) or 0)
        if probability > 0:
            value -= probability * math.log(probability)
    return value / math.log(len(OUTCOMES))


def betting_confidence_from_tpb(tpb):
    return signal_strength_from_tpb(tpb)


def signal_strength_from_tpb(tpb):
    probabilities = (tpb or {}).get("probabilities")
    if not probabilities:
        return 0
    ordered = sorted((float(probabilities.get(key) or 0) for key in OUTCOMES), reverse=True)
    if len(ordered) < 2:
        return 0
    return clamp((ordered[0] - ordered[1]) * 100)


def betting_confidence_breakdown(tpb):
    probabilities = (tpb or {}).get("probabilities")
    if not probabilities:
        return {
            "tpb_edge": None,
            "base": 0,
            "adjustments": [],
            "formula": "Signal Strength unavailable",
        }
    ordered = sorted((float(probabilities.get(key) or 0) for key in OUTCOMES), reverse=True)
    edge = (ordered[0] - ordered[1]) * 100 if len(ordered) >= 2 else 0
    score = signal_strength_from_tpb(tpb)
    return {
        "tpb_edge": edge,
        "base": score,
        "adjustments": [],
        "formula": "Signal Strength = (top TPB probability - second TPB probability) * 100",
    }


def risk_adjustment_from_rsi(level):
    normalized = str(level or "Medium").strip().lower()
    if normalized == "low":
        return 0.9
    if normalized == "high":
        return 0.4
    return 0.65


def rsi_penalty(level):
    normalized = str(level or "Medium").strip().lower()
    if normalized == "low":
        return 15
    if normalized == "high":
        return 55
    return 35


def market_direction_from_tpb(tpb, labels=None):
    probabilities = (tpb or {}).get("probabilities")
    labels = labels or {
        "home_win": "主队占优",
        "draw": "平衡 / 平局权重高",
        "away_win": "客队占优",
    }
    if not probabilities:
        return "暂无 API-Football 胜平负 TPB 概率"
    ordered = sorted(OUTCOMES, key=lambda key: probabilities.get(key, 0), reverse=True)
    top = ordered[0]
    second = ordered[1]
    if probabilities[top] - probabilities[second] < 0.08:
        return "均衡"
    return labels.get(top, top)


def investment_score_from_tpb(tpb, scenario_alignment=None, risk_surface_index=None):
    probabilities = (tpb or {}).get("probabilities")
    if not probabilities:
        return 0
    tpb_edge = signal_strength_from_tpb(tpb)
    alignment = tpb_edge if scenario_alignment is None else clamp(scenario_alignment)
    signal = min(100, tpb_edge + alignment)
    risk_adjustment = risk_adjustment_from_rsi(risk_surface_index)
    return clamp(signal * risk_adjustment)


def investment_score_breakdown(tpb, scenario_alignment=None, risk_surface_index=None):
    tpb_edge = signal_strength_from_tpb(tpb)
    alignment = tpb_edge if scenario_alignment is None else clamp(scenario_alignment)
    signal = min(100, tpb_edge + alignment)
    rsi = risk_surface_index or "Medium"
    risk_adjustment = risk_adjustment_from_rsi(rsi)
    score = investment_score_from_tpb(tpb, alignment, rsi)
    return {
        "formula": "Investment Score = Signal × Risk Adjustment",
        "signal_formula": "Signal = TPB Edge + Scenario Alignment",
        "risk_formula": "Risk Adjustment = 1 - RSI qualitative penalty",
        "tpb_edge": tpb_edge,
        "scenario_alignment": alignment,
        "signal": round(signal),
        "rsi": rsi,
        "risk_adjustment": risk_adjustment,
        "score": score,
    }


def stake_from_investment_score(score):
    score = float(score or 0)
    if score < 50:
        amount = 0
        rule = "0元：投资分低于50。"
    elif score < 60:
        amount = 300
        rule = "300元：投资分50-59。"
    elif score < 70:
        amount = 500
        rule = "500元：投资分60-69。"
    elif score < 80:
        amount = 800
        rule = "800元：投资分70-79。"
    elif score < 90:
        amount = 1200
        rule = "1200元：投资分80-89。"
    else:
        amount = 1500
        rule = "1500元：投资分90以上。"
    return {
        "amount": amount,
        "risk_mode": "TPB 确定性",
        "amount_rule": rule,
        "reason": f"推荐金额只由投资分 {round(score)} / 100 决定。",
    }


def odds_data_quality(odds=None, api_football_data=None):
    odds = odds or {}
    api_football_data = api_football_data or {}
    asian_handicap = api_football_data.get("asian_handicap") or {}
    correct_score = api_football_data.get("correct_score") or {}
    checks = [
        ("胜平负", bool(true_probability_base(odds).get("available"))),
        ("亚洲盘", bool(asian_handicap.get("rows"))),
        ("大小球", bool(odds.get("over_under"))),
        ("波胆", bool(correct_score.get("rows"))),
    ]
    success_checks = [
        bool(odds.get("found")),
        asian_handicap.get("status") != "unavailable",
        bool(odds.get("over_under")) or odds.get("over_under_source") == "not_returned",
        correct_score.get("status") != "unavailable",
    ]
    passed = [label for label, ok in checks if ok]
    missing = [label for label, ok in checks if not ok]
    completeness_score = round(len(passed) / len(checks) * 100) if checks else 0
    api_success_rate = round(sum(1 for ok in success_checks if ok) / len(success_checks) * 100)
    score = round(completeness_score * 0.8 + api_success_rate * 0.2)
    label = "High" if score >= 90 else "Medium" if score >= 50 else "Low"
    note = (
        f"赔率数据完整：{'、'.join(passed)}。"
        if not missing
        else f"赔率数据缺少：{'、'.join(missing)}。"
    )
    return {
        "score": score,
        "completeness_score": completeness_score,
        "api_success_rate": api_success_rate,
        "label": label,
        "note": note,
        "checks": checks,
    }
