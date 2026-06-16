POPULAR_TEAMS = {
    "argentina",
    "france",
    "brazil",
    "england",
    "germany",
    "spain",
    "portugal",
    "netherlands",
}

TEAM_CN = {
    "Argentina": "阿根廷",
    "Algeria": "阿尔及利亚",
    "Draw": "平局",
}

AFRICA_TEAMS = {
    "algeria",
    "morocco",
    "senegal",
    "tunisia",
    "egypt",
    "ghana",
    "nigeria",
    "cameroon",
    "ivory coast",
    "south africa",
}

ASIA_TEAMS = {
    "japan",
    "south korea",
    "iran",
    "saudi arabia",
    "qatar",
    "australia",
    "uzbekistan",
}


def clamp(value, low=0, high=100):
    return max(low, min(high, round(value)))


def normalize_name(value):
    return str(value or "").strip().lower()


def display_team(value):
    return TEAM_CN.get(value, value)


def odds_probabilities(odds):
    if not odds.get("found"):
        return None
    if odds.get("implied_probabilities"):
        return odds["implied_probabilities"]
    if all(odds.get(key) for key in ["home_win", "draw", "away_win"]):
        raw = {
            "home_win": 1 / odds["home_win"],
            "draw": 1 / odds["draw"],
            "away_win": 1 / odds["away_win"],
        }
        total = sum(raw.values())
        return {key: value / total for key, value in raw.items()}
    return None


def polymarket_probabilities(polymarket):
    if not polymarket.get("found"):
        return None
    if not all(polymarket.get(key) is not None for key in ["home_win", "draw", "away_win"]):
        return None
    raw = {
        "home_win": polymarket["home_win"],
        "draw": polymarket["draw"],
        "away_win": polymarket["away_win"],
    }
    total = sum(raw.values())
    if total <= 0:
        return None
    return {key: value / total for key, value in raw.items()}


def label_for_key(match, key):
    return {
        "home_win": match["home_cn"],
        "draw": "平局",
        "away_win": match["away_cn"],
    }.get(key, "-")


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


def market_disagreement(match, odds, polymarket):
    odds_probs = odds_probabilities(odds)
    poly_probs = polymarket_probabilities(polymarket)
    if not odds_probs or not poly_probs:
        return {
            "score": 0,
            "level": "低分歧",
            "direction": "-",
            "difference": 0,
            "odds_probability": None,
            "polymarket_probability": None,
            "reason": "缺少可比较的市场数据。",
        }

    diffs = {
        key: abs(poly_probs[key] - odds_probs[key])
        for key in ["home_win", "draw", "away_win"]
    }
    key = max(diffs, key=diffs.get)
    difference = diffs[key]
    score = clamp(difference * 1000)
    level = {
        "Low": "低分歧",
        "Medium": "中分歧",
        "High": "高分歧",
    }[score_level(score)]

    return {
        "score": score,
        "level": level,
        "direction": label_for_key(match, key),
        "difference": difference,
        "odds_probability": odds_probs[key],
        "polymarket_probability": poly_probs[key],
        "reason": f"最大市场价差出现在{label_for_key(match, key)}方向。",
    }


def market_favorites(match, odds, polymarket):
    odds_probs = odds_probabilities(odds) or {}
    poly_probs = polymarket_probabilities(polymarket) or {}
    odds_favorite = max(odds_probs, key=odds_probs.get) if odds_probs else None
    poly_favorite = max(poly_probs, key=poly_probs.get) if poly_probs else None
    return odds_favorite, poly_favorite, odds_probs, poly_probs


def contrarian_score(match, odds, polymarket):
    odds_favorite, poly_favorite, odds_probs, poly_probs = market_favorites(match, odds, polymarket)
    if not odds_favorite and not poly_favorite:
        return {
            "score": 20,
            "level": "较低",
            "popular_side": "-",
            "reason": "缺少市场数据，暂不形成逆向判断。",
        }

    favorite = poly_favorite or odds_favorite
    favorite_name = normalize_name(label_for_key(match, favorite))
    is_popular = favorite_name in POPULAR_TEAMS
    markets_aligned = odds_favorite and poly_favorite and odds_favorite == poly_favorite
    concentration = max(
        odds_probs.get(favorite, 0),
        poly_probs.get(favorite, 0),
    )

    score = 15
    if is_popular:
        score += 25
    if markets_aligned:
        score += 20
    if concentration >= 0.65:
        score += 25
    elif concentration >= 0.55:
        score += 15
    if concentration >= 0.75:
        score += 10

    score = clamp(score)
    return {
        "score": score,
        "level": {"Low": "较低", "Medium": "中等", "High": "较高"}[score_level(score)],
        "popular_side": label_for_key(match, favorite),
        "reason": "热门球队与多市场一致预期可能带来拥挤定价。"
        if is_popular and markets_aligned
        else "当前市场结构下，逆向压力有限。",
    }


def fixture_round(api_football_data):
    fixture = (api_football_data or {}).get("fixture") or {}
    raw = fixture.get("raw", {})
    return str((raw.get("league") or {}).get("round") or "")


def upset_index(match, odds, polymarket, api_football_data):
    odds_favorite, poly_favorite, odds_probs, poly_probs = market_favorites(match, odds, polymarket)
    favorite = poly_favorite or odds_favorite
    favorite_probability = max(
        odds_probs.get(favorite, 0) if favorite else 0,
        poly_probs.get(favorite, 0) if favorite else 0,
    )

    score = 35
    if "group" in fixture_round(api_football_data).lower():
        score += 12
    if favorite_probability >= 0.65:
        score += 8
    elif favorite_probability <= 0.50:
        score -= 8

    home = normalize_name(match["home_cn"])
    away = normalize_name(match["away_cn"])
    underdog = away if favorite == "home_win" else home if favorite == "away_win" else None
    if underdog in AFRICA_TEAMS:
        score += 8
    if underdog in ASIA_TEAMS:
        score += 7
    if normalize_name(label_for_key(match, favorite)) in POPULAR_TEAMS:
        score += 5

    score = clamp(score)
    meaning = "高爆冷风险" if score >= 70 else "中等爆冷风险" if score >= 45 else "低爆冷风险"
    return {
        "score": score,
        "meaning": meaning,
        "reason": "小组赛阶段与弱势方属性提高了爆冷敏感度。",
    }


def recent_form_score(api_football_data):
    home_recent = (api_football_data or {}).get("home_recent") or []
    away_recent = (api_football_data or {}).get("away_recent") or []
    if not home_recent or not away_recent:
        return {
            "score": 50,
            "reason": "近期状态暂不可用，采用中性分。",
        }
    return {
        "score": 55,
        "reason": "近期状态可用，V1 框架给予轻微信号。",
    }


def injury_impact_score(api_football_data):
    injuries = (api_football_data or {}).get("injuries") or []
    if not injuries:
        return {
            "score": 50,
            "reason": "暂无公开伤病信息，采用中性分。",
        }
    return {
        "score": 60,
        "reason": "存在公开伤病信息，不确定性上升。",
    }


def placeholder_score(name):
    return {
        "score": 50,
        "reason": f"{name} 为 V1 框架占位，待后续接入可靠数据源。",
    }


def value_rating(score):
    if score >= 80:
        return "A+"
    if score >= 70:
        return "A"
    if score >= 55:
        return "B"
    if score >= 40:
        return "C"
    return "D"


def rating_meaning(rating, match):
    meanings = {
        "A+": f"市场可能明显错估{display_team(match['home_cn'])}。",
        "A": f"市场可能轻微高估{display_team(match['home_cn'])}。",
        "B": "存在一定价格张力，但优势并不极端。",
        "C": "市场分歧较小，暂不属于强机会。",
        "D": "暂未发现明确价值机会。",
    }
    return meanings.get(rating, "-")


def final_recommendation(match, betting_opinion, contrarian, upset):
    handicap = (betting_opinion or {}).get("asian_handicap", "No view").replace("Lean ", "")
    if handicap != "No view" and (contrarian["score"] >= 55 or upset["score"] >= 55):
        return {
            "bet": handicap,
            "reason": [
                f"市场共识明显支持{display_team(match['home_cn'])}",
                "逆向分数处于偏高区间",
                "爆冷指数高于基准水平",
                "让球盘相比独赢具备更好的风险收益比",
            ],
        }

    winner = (betting_opinion or {}).get("match_winner", "No view").replace("Lean ", "")
    return {
        "bet": winner if winner != "No view" else "观察为主",
        "reason": [
            "暂未发现强逆向让球机会",
            "当前仅将市场方向作为参考",
        ],
    }


def stake_suggestion(final_score):
    if final_score >= 70:
        return {"Conservative": 500, "Standard": 1000, "Aggressive": 1500}
    if final_score >= 55:
        return {"Conservative": 300, "Standard": 600, "Aggressive": 900}
    if final_score >= 40:
        return {"Conservative": 100, "Standard": 300, "Aggressive": 500}
    return {"Conservative": 0, "Standard": 0, "Aggressive": 0}


def build_decision_engine(match, odds, polymarket, api_football_data, betting_opinion):
    disagreement = market_disagreement(match, odds, polymarket)
    contrarian = contrarian_score(match, odds, polymarket)
    upset = upset_index(match, odds, polymarket, api_football_data)
    recent_form = recent_form_score(api_football_data)
    injury_impact = injury_impact_score(api_football_data)
    elo = placeholder_score("ELO评分")
    team_value = placeholder_score("球队身价")

    weighted = {
        "market_disagreement": disagreement["score"] * 0.25,
        "contrarian": contrarian["score"] * 0.20,
        "recent_form": recent_form["score"] * 0.15,
        "upset_index": upset["score"] * 0.15,
        "elo_rating": elo["score"] * 0.10,
        "injury_impact": injury_impact["score"] * 0.10,
        "team_value": team_value["score"] * 0.05,
    }
    final_score = clamp(sum(weighted.values()))
    rating = value_rating(final_score)

    return {
        "market_disagreement": disagreement,
        "contrarian": contrarian,
        "upset_index": upset,
        "recent_form": recent_form,
        "elo_rating": elo,
        "injury_impact": injury_impact,
        "team_value": team_value,
        "final_confidence_score": final_score,
        "value_rating": rating,
        "value_rating_meaning": rating_meaning(rating, match),
        "final_recommendation": final_recommendation(match, betting_opinion, contrarian, upset),
        "stake_suggestion": stake_suggestion(final_score),
        "weights": {
            "市场分歧": "25%",
            "逆向分数": "20%",
            "近期状态": "15%",
            "爆冷指数": "15%",
            "ELO评分": "10%",
            "伤病影响": "10%",
            "球队身价": "5%",
        },
    }
