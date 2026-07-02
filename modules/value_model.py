from modules.probability_base import true_probability_base


def normalize(values):
    total = sum(values.values())
    if total <= 0:
        return None
    return {key: value / total for key, value in values.items()}


def odds_probabilities(odds):
    return true_probability_base(odds).get("probabilities")


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
