def api_probabilities(odds):
    odds = odds or {}
    probabilities = odds.get("implied_probabilities")
    if probabilities:
        return {
            "home_win": probabilities.get("home_win"),
            "draw": probabilities.get("draw"),
            "away_win": probabilities.get("away_win"),
        }
    required = [odds.get("home_win"), odds.get("draw"), odds.get("away_win")]
    if any(value in (None, 0) for value in required):
        return None
    raw = {
        "home_win": 1 / odds["home_win"],
        "draw": 1 / odds["draw"],
        "away_win": 1 / odds["away_win"],
    }
    total = sum(raw.values())
    if total <= 0:
        return None
    return {key: value / total for key, value in raw.items()}


def polymarket_probabilities(polymarket):
    polymarket = polymarket or {}
    if not polymarket.get("found"):
        return None
    values = {
        "home_win": polymarket.get("home_win"),
        "draw": polymarket.get("draw"),
        "away_win": polymarket.get("away_win"),
    }
    if any(value is None for value in values.values()):
        return None
    total = sum(values.values())
    if total <= 0:
        return None
    return {key: value / total for key, value in values.items()}


def comparison_rows(api_probs, poly_probs):
    labels = {
        "home_win": "Home",
        "draw": "Draw",
        "away_win": "Away",
    }
    rows = []
    for key in ["home_win", "draw", "away_win"]:
        api_value = (api_probs or {}).get(key)
        poly_value = (poly_probs or {}).get(key)
        if api_value is None or poly_value is None:
            continue
        rows.append({
            "key": key,
            "label": labels[key],
            "api_football_probability": api_value,
            "polymarket_probability": poly_value,
            "deviation": poly_value - api_value,
            "absolute_deviation": abs(poly_value - api_value),
        })
    return rows


def build_market_data(odds, api_football_data, polymarket):
    odds = odds or {}
    api_football_data = api_football_data or {}
    polymarket = polymarket or {}
    api_probs = api_probabilities(odds)
    poly_probs = polymarket_probabilities(polymarket)
    rows = comparison_rows(api_probs, poly_probs)
    average_deviation = (
        sum(row["absolute_deviation"] for row in rows) / len(rows)
        if rows
        else None
    )
    max_deviation = max((row["absolute_deviation"] for row in rows), default=None)
    agreement_score = (
        max(0, round(100 - average_deviation * 100))
        if average_deviation is not None
        else None
    )

    return {
        "api_football_odds": {
            "one_x_two": {
                "found": bool(odds.get("found")),
                "home_win": odds.get("home_win"),
                "draw": odds.get("draw"),
                "away_win": odds.get("away_win"),
                "implied_probabilities": api_probs,
                "source": odds.get("source"),
            },
            "asian_handicap": (api_football_data.get("asian_handicap") or {}),
            "correct_score": (api_football_data.get("correct_score") or {}),
            "over_under": {
                "found": bool(odds.get("over_under")),
                "rows": odds.get("over_under") or [],
                "bookmakers": odds.get("over_under_bookmakers") or [],
                "source": odds.get("over_under_source") or "API-Football / Goals Over/Under",
                "line": odds.get("over_under_line"),
                "message": odds.get("over_under_message") or odds.get("message"),
            },
        },
        "polymarket_reference": {
            "found": bool(polymarket.get("found")) and bool(poly_probs),
            "win_probability_home": (poly_probs or {}).get("home_win"),
            "win_probability_draw": (poly_probs or {}).get("draw"),
            "win_probability_away": (poly_probs or {}).get("away_win"),
            "source": polymarket.get("source") or "Polymarket Gamma API",
            "event_title": polymarket.get("event_title"),
            "event_url": polymarket.get("event_url"),
            "message": polymarket.get("message"),
        },
        "comparison_metrics": {
            "available": bool(rows),
            "rows": rows,
            "average_deviation": average_deviation,
            "max_deviation": max_deviation,
            "market_agreement_score": agreement_score,
            "message": (
                "API-Football and Polymarket probabilities compared."
                if rows
                else "Polymarket comparison unavailable; API-Football remains primary."
            ),
        },
    }
