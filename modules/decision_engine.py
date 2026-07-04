from modules.pregame_content import team_cn
from modules.probability_base import (
    betting_confidence_from_tpb,
    investment_score_breakdown,
    investment_score_from_tpb,
    market_direction_from_tpb,
    stake_from_investment_score,
    true_probability_base,
)


def clamp(value, low=0, high=100):
    return max(low, min(high, round(value)))


def display_team(value):
    return team_cn(value)


def label_for_key(match, key):
    return {
        "home_win": match["home_cn"],
        "draw": "平局",
        "away_win": match["away_cn"],
    }.get(key, "-")


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
        "A": "TPB 投资分强",
        "B": "TPB 投资分可参与",
        "C": "TPB 投资分偏谨慎",
        "D": "TPB 投资分不足",
    }
    return f"TPB 投资分 {score} / 100，评级 {rating}：{meanings.get(rating, '-')}"


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


def direction_confidence(match, odds, polymarket=None, api_football_data=None, scenario_engine=None):
    tpb = true_probability_base(odds)
    probabilities = tpb.get("probabilities")
    if not probabilities:
        return {
            "score": 0,
            "level": "观望",
            "components": [],
            "investment_score": 0,
            "market_direction": "No API-Football 1X2 probability",
            "true_probability_base": tpb,
            "reason": "缺少 API-Football 1X2 赔率，无法形成 TPB。",
        }

    favorite = max(probabilities, key=probabilities.get)
    favorite_label = display_team(label_for_key(match, favorite))
    favorite_probability = probabilities[favorite]
    score = betting_confidence_from_tpb(tpb)
    scenario_alignment = (scenario_engine or {}).get("scenario_alignment")
    rsi = (scenario_engine or {}).get("risk_surface_index")
    investment_score = investment_score_from_tpb(
        tpb,
        scenario_alignment=scenario_alignment,
        risk_surface_index=rsi,
    )
    investment_breakdown = investment_score_breakdown(
        tpb,
        scenario_alignment=scenario_alignment,
        risk_surface_index=rsi,
    )
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
                "Signal Strength 由 TPB 最高概率与第二概率差值派生。"
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
    summary = f"TPB 显示 {favorite_label} 为最高概率方向，Signal Strength 为{level}。"
    return {
        "score": score,
        "level": level,
        "components": components,
        "investment_score": investment_score,
        "investment_breakdown": investment_breakdown,
        "market_direction": market_direction,
        "true_probability_base": tpb,
        "summary": summary,
        "reason": "方向把握由 TPB Edge 表达；Scenario Alignment 和 RSI 只进入 Lite Investment Score。",
    }


def participation_advice(direction):
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
        "reason": f"参与建议只由 TPB 投资分 {score} / 100 派生。",
    }


def recommended_stake(direction):
    score = direction.get("investment_score", direction.get("score", 0))
    stake = stake_from_investment_score(score)
    return {
        **stake,
        "base": stake["amount"],
        "adjustment": 0,
    }


def final_recommendation(match, betting_opinion):
    winner = (betting_opinion or {}).get("match_winner", "No view").replace("Lean ", "")
    return {
        "bet": winner if winner != "No view" else "观察为主",
        "reason": [
            "最终推荐跟随 TPB 最高概率方向",
            "让球、剧本观察层与二级市场参考不改写主推荐",
        ],
    }


def build_decision_engine(match, odds, polymarket, api_football_data, betting_opinion, actual_odds=None, distribution=None, market_intelligence=None, scenario_engine=None):
    direction = direction_confidence(match, odds, polymarket, api_football_data, scenario_engine=scenario_engine)
    investment_score = direction.get("investment_score", 0)
    odds_value = {
        "score": investment_score,
        "rating": value_rating(investment_score),
        "components": direction.get("components", []),
        "reason": "赔率价值已并入 TPB 投资分，不再单独重复计分。",
    }
    disabled_observation = {
        "score": 0,
        "level": "观察层",
        "meaning": "观察层",
        "direction": "-",
        "difference": 0,
        "reason": "Probability-first 架构下该项不参与决策。",
    }
    participation = participation_advice(direction)
    stake = recommended_stake(direction)

    return {
        "market_disagreement": dict(disabled_observation),
        "contrarian": dict(disabled_observation),
        "upset_index": dict(disabled_observation),
        "recent_form": dict(disabled_observation),
        "elo_rating": dict(disabled_observation),
        "injury_impact": dict(disabled_observation),
        "team_value": dict(disabled_observation),
        "direction_confidence": direction,
        "odds_value": odds_value,
        "participation_advice": participation,
        "recommended_stake": stake,
        "final_confidence_score": direction["score"],
        "value_rating": odds_value["rating"],
        "value_rating_score": odds_value["score"],
        "value_rating_breakdown": odds_value.get("components", []),
        "value_rating_meaning": rating_meaning(odds_value["rating"], odds_value["score"]),
        "final_recommendation": final_recommendation(match, betting_opinion),
        "stake_suggestion": {
            "Conservative": stake["amount"],
            "Standard": stake["amount"],
            "Aggressive": stake["amount"],
        },
        "weights": {
            "TPB": "API-Football 胜平负博彩公司共识概率",
            "Signal Strength": "TPB 最高概率 - 第二概率",
            "投资分": "Signal × Risk Adjustment",
            "推荐仓位": "仅由投资分档位确定",
        },
    }
