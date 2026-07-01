def normalize_probabilities(probabilities):
    total = sum(probabilities.values())
    return {key: value / total for key, value in probabilities.items()}


def odds_to_probabilities(odds):
    if odds.get("implied_probabilities"):
        return odds["implied_probabilities"]

    raw = {
        "home_win": 1 / odds["home_win"],
        "draw": 1 / odds["draw"],
        "away_win": 1 / odds["away_win"],
    }
    return normalize_probabilities(raw)


def combine_probabilities(odds, polymarket, news, config):
    has_odds = all(odds.get(key) is not None for key in ["home_win", "draw", "away_win"])

    if has_odds:
        odds_probs = odds_to_probabilities(odds)
    else:
        odds_probs = {"home_win": 1 / 3, "draw": 1 / 3, "away_win": 1 / 3}

    odds_weight = config["model"]["odds_weight"] if has_odds else 0
    news_weight = config["model"]["news_weight"]
    adjustment = news["news_score_adjustment"]

    combined = {}
    for key in ["home_win", "draw", "away_win"]:
        combined[key] = odds_probs[key] * odds_weight

    unused_market_weight = 1 - odds_weight - news_weight
    for key in ["home_win", "draw", "away_win"]:
        combined[key] += odds_probs[key] * unused_market_weight

    combined["home_win"] += adjustment * news_weight
    combined["draw"] -= adjustment * news_weight / 2
    combined["away_win"] -= adjustment * news_weight / 2

    return normalize_probabilities(combined)
