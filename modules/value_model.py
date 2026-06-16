def normalize(values):
    total = sum(values.values())
    if total <= 0:
        return None
    return {key: value / total for key, value in values.items()}


def odds_probabilities(odds):
    if not odds.get("found"):
        return None
    if odds.get("implied_probabilities"):
        return odds["implied_probabilities"]
    if all(odds.get(key) for key in ["home_win", "draw", "away_win"]):
        return normalize({
            "home_win": 1 / odds["home_win"],
            "draw": 1 / odds["draw"],
            "away_win": 1 / odds["away_win"],
        })
    return None


def polymarket_probabilities(polymarket):
    if not polymarket.get("found"):
        return None
    if not all(polymarket.get(key) is not None for key in ["home_win", "draw", "away_win"]):
        return None
    return normalize({
        "home_win": polymarket["home_win"],
        "draw": polymarket["draw"],
        "away_win": polymarket["away_win"],
    })


def analyze_value(match, odds, polymarket):
    odds_probs = odds_probabilities(odds)
    polymarket_probs = polymarket_probabilities(polymarket)

    if not odds_probs or not polymarket_probs:
        return {
            "available": False,
            "message": "Value Analysis requires both The Odds API and Polymarket probabilities.",
            "rows": [],
            "has_value": False,
        }

    labels = {
        "home_win": match["home_cn"],
        "draw": "Draw",
        "away_win": match["away_cn"],
    }
    rows = []
    has_value = False

    for key in ["home_win", "draw", "away_win"]:
        difference = polymarket_probs[key] - odds_probs[key]
        if abs(difference) >= 0.05:
            has_value = True
        rows.append({
            "label": labels[key],
            "odds_api": odds_probs[key],
            "polymarket": polymarket_probs[key],
            "difference": difference,
            "is_value": abs(difference) >= 0.05,
        })

    return {
        "available": True,
        "message": "Potential Value Opportunity" if has_value else "No major value gap detected",
        "rows": rows,
        "has_value": has_value,
    }

