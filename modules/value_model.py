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
    return None


def analyze_value(match, odds, polymarket):
    odds_probs = odds_probabilities(odds)
    if not odds_probs:
        return {
            "available": False,
            "message": "API-Football odds are unavailable.",
            "rows": [],
            "has_value": False,
        }

    return {
        "available": False,
        "message": "API-Football single-source mode does not run secondary market value comparison.",
        "rows": [],
        "has_value": False,
    }
