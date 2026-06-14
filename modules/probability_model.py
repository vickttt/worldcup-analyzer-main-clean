def normalize_probabilities(probabilities):
    total = sum(probabilities.values())
    return {key: value / total for key, value in probabilities.items()}


def odds_to_probabilities(odds):
    raw = {
        "home_win": 1 / odds["home_win"],
        "draw": 1 / odds["draw"],
        "away_win": 1 / odds["away_win"],
    }
    return normalize_probabilities(raw)


def combine_probabilities(odds, polymarket, news, config):
    odds_probs = odds_to_probabilities(odds)
    has_polymarket = all(
        polymarket.get(key) is not None for key in ["home_win", "draw", "away_win"]
    )
    if has_polymarket:
        market_probs = {
            "home_win": polymarket["home_win"],
            "draw": polymarket["draw"],
            "away_win": polymarket["away_win"],
        }
        market_probs = normalize_probabilities(market_probs)
    else:
        market_probs = odds_probs

    odds_weight = config["model"]["odds_weight"]
    polymarket_weight = config["model"]["polymarket_weight"] if has_polymarket else 0
    news_weight = config["model"]["news_weight"]
    adjustment = news["news_score_adjustment"]

    combined = {}
    for key in ["home_win", "draw", "away_win"]:
        combined[key] = odds_probs[key] * odds_weight + market_probs[key] * polymarket_weight

    if not has_polymarket:
        for key in ["home_win", "draw", "away_win"]:
            combined[key] += odds_probs[key] * config["model"]["polymarket_weight"]

    combined["home_win"] += adjustment * news_weight
    combined["draw"] -= adjustment * news_weight / 2
    combined["away_win"] -= adjustment * news_weight / 2

    return normalize_probabilities(combined)
