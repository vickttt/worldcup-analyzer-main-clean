from modules.market_utils import asian_handicap_summary


def format_line(team, line):
    if line is None:
        return team
    sign = "+" if line > 0 else ""
    return f"{team} {sign}{line:g}"


def format_api_handicap_line(match, summary):
    line = summary.get("main_line")
    if line is None:
        return "No view"
    team = match["home_cn"] if summary.get("main_side") == "home" else match["away_cn"]
    return format_line(team, line)


def consensus_market(markets, line_key="line"):
    if not markets:
        return None

    counts = {}
    for market in markets:
        line = market.get(line_key)
        counts[line] = counts.get(line, 0) + 1

    main_line = max(counts, key=counts.get)
    selected = [market for market in markets if market.get(line_key) == main_line]
    return {
        "line": main_line,
        "markets": selected,
        "bookmakers": [market.get("bookmaker") for market in selected if market.get("bookmaker")],
    }


def strongest_match_winner(odds, match):
    if not odds.get("found"):
        return None

    prices = {
        match["home_cn"]: odds.get("home_win"),
        "Draw": odds.get("draw"),
        match["away_cn"]: odds.get("away_win"),
    }
    prices = {key: value for key, value in prices.items() if value}
    if not prices:
        return None

    # Lower decimal odds imply higher market confidence.
    return min(prices, key=prices.get)


def value_direction(value_analysis):
    if not value_analysis or not value_analysis.get("available"):
        return None

    value_rows = [row for row in value_analysis.get("rows", []) if row.get("is_value")]
    if not value_rows:
        return None

    best = max(value_rows, key=lambda row: abs(row.get("difference", 0)))
    return best.get("label")


def handicap_opinion(odds, match):
    markets = odds.get("asian_handicap") or []
    if not markets:
        return "No view"

    consensus = consensus_market(markets)
    line = consensus["line"]
    selected = consensus["markets"]
    best_home = max((market.get("home_odds") for market in selected if market.get("home_odds")), default=None)
    best_away = max((market.get("away_odds") for market in selected if market.get("away_odds")), default=None)

    if best_home and best_away and abs(best_home - best_away) <= 0.08:
        return f"Neutral around {format_line(match['home_cn'], line)}"
    if best_home and best_away and best_home < best_away:
        return f"Lean {format_line(match['home_cn'], line)}"

    away_line = -line if line is not None else None
    return f"Lean {format_line(match['away_cn'], away_line)}"


def api_handicap_opinion(api_football_data, match):
    summary = asian_handicap_summary(((api_football_data or {}).get("asian_handicap") or {}).get("rows") or [])
    if not summary.get("available"):
        return "No view"
    return f"Lean {format_api_handicap_line(match, summary)}"


def totals_opinion(odds):
    markets = odds.get("over_under") or []
    if not markets:
        return "No view"

    consensus = consensus_market(markets)
    line = consensus["line"]
    selected = consensus["markets"]
    best_over = max((market.get("over_odds") for market in selected if market.get("over_odds")), default=None)
    best_under = max((market.get("under_odds") for market in selected if market.get("under_odds")), default=None)

    if best_over and best_under and abs(best_over - best_under) <= 0.08:
        return f"Neutral around {line:g}"
    if best_over and best_under and best_over < best_under:
        return f"Lean Over {line:g}"

    return f"Lean Under {line:g}"


def favored_by_polymarket(polymarket, match):
    if not polymarket.get("found"):
        return None

    prices = {
        match["home_cn"]: polymarket.get("home_win"),
        "Draw": polymarket.get("draw"),
        match["away_cn"]: polymarket.get("away_win"),
    }
    prices = {key: value for key, value in prices.items() if value is not None}
    if not prices:
        return None
    return max(prices, key=prices.get)


def winner_reason(winner, polymarket, match):
    if not winner:
        return "Insufficient market data for a winner view."

    polymarket_winner = favored_by_polymarket(polymarket, match)
    if polymarket_winner == winner:
        return f"Market consensus and Polymarket both favor {winner}."
    if polymarket_winner:
        return f"The Odds API favors {winner}, while Polymarket is less aligned."
    return f"Match Winner market favors {winner}."


def handicap_reason(handicap, match):
    if handicap == "No view":
        return "Handicap market is not available."
    if "Neutral" in handicap:
        return "Handicap pricing is balanced around the main line."
    if match["away_cn"] in handicap:
        return f"Handicap market suggests {match['away_cn']} may cover the spread."
    return f"Handicap market supports {match['home_cn']} against the spread."


def totals_reason(goals):
    if goals == "No view":
        return "Goals market is not available."
    if "Neutral" in goals:
        return "Over and Under odds remain balanced."
    if "Under" in goals:
        return "Under odds are slightly favored by the market."
    return "Over odds are slightly favored by the market."


def risk_level(odds, polymarket, value_analysis):
    missing_markets = 0
    if not odds.get("found"):
        missing_markets += 1
    if not polymarket.get("found"):
        missing_markets += 1
    if not odds.get("asian_handicap"):
        missing_markets += 1
    if not odds.get("over_under"):
        missing_markets += 1

    if missing_markets >= 2:
        return "High"
    if value_analysis and value_analysis.get("has_value"):
        return "Medium"
    return "Low"


def confidence_score(risk):
    return {
        "Low": 72,
        "Medium": 58,
        "High": 42,
    }.get(risk, 50)


def build_betting_opinion(match, odds, polymarket, value_analysis, api_football_data=None):
    winner = strongest_match_winner(odds, match)
    value = value_direction(value_analysis)

    if not winner:
        match_winner = "No view"
    elif value:
        match_winner = f"Lean {winner}"
    else:
        match_winner = f"Lean {winner}"

    handicap = api_handicap_opinion(api_football_data, match)
    if handicap == "No view":
        handicap = handicap_opinion(odds, match)
    goals = totals_opinion(odds)
    risk = risk_level(odds, polymarket, value_analysis)
    confidence = confidence_score(risk)

    if value:
        summary = f"Market supports {winner}; value analysis shows a notable gap around {value}."
    elif handicap != "No view" and match["away_cn"] in handicap:
        summary = (
            f"Market generally supports {winner}, but handicap market gives some support "
            f"to {match['away_cn']} covering the spread."
        )
    elif handicap != "No view":
        summary = f"Market generally supports {winner}; handicap pricing is aligned with that view."
    else:
        summary = f"Market generally supports {winner}." if winner else "Insufficient market data for a view."

    return {
        "match_winner": match_winner,
        "asian_handicap": handicap,
        "over_under": goals,
        "risk_level": risk,
        "confidence": confidence,
        "match_winner_reason": winner_reason(winner, polymarket, match),
        "asian_handicap_reason": handicap_reason(handicap, match),
        "over_under_reason": totals_reason(goals),
        "summary": summary,
    }
