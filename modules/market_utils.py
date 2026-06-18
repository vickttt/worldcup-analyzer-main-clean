import re
from collections import Counter, defaultdict


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def mean(values):
    clean = [value for value in values if value is not None]
    return sum(clean) / len(clean) if clean else None


def parse_handicap_value(value):
    text = str(value or "").strip()
    match = re.search(r"\b(Home|Away)\b\s*([+-]?\d+(?:\.\d+)?)", text, re.I)
    if not match:
        return None
    side = match.group(1).lower()
    line = safe_float(match.group(2))
    if line is None:
        return None
    return {
        "side": "home" if side == "home" else "away",
        "line": line,
        "abs_line": abs(line),
        "label": f"{match.group(1).title()} {line:+g}",
    }


def asian_handicap_summary(rows):
    parsed_rows = []
    for row in rows or []:
        parsed = parse_handicap_value(row.get("value"))
        odd = safe_float(row.get("odd"))
        if not parsed or odd is None:
            continue
        parsed_rows.append({**row, **parsed, "odd": odd})

    if not parsed_rows:
        return {
            "available": False,
            "main_value": None,
            "main_side": None,
            "main_line": None,
            "avg_odds": None,
            "best_odds": None,
            "bookmakers": [],
            "rows": [],
        }

    counts = Counter(row["label"] for row in parsed_rows)
    main_value = counts.most_common(1)[0][0]
    selected = [row for row in parsed_rows if row["label"] == main_value]
    odds = [row["odd"] for row in selected]
    first = selected[0]
    return {
        "available": True,
        "main_value": main_value,
        "main_side": first["side"],
        "main_line": first["line"],
        "avg_odds": mean(odds),
        "best_odds": max(odds) if odds else None,
        "bookmakers": sorted({row.get("bookmaker") for row in selected if row.get("bookmaker")}),
        "rows": selected,
    }


def correct_score_summary(rows, limit=5):
    grouped = defaultdict(list)
    for row in rows or []:
        score = row.get("score")
        odd = safe_float(row.get("odd"))
        if not score or odd is None:
            continue
        grouped[score].append({**row, "odd": odd})

    scores = []
    for score, score_rows in grouped.items():
        odds = [row["odd"] for row in score_rows]
        scores.append({
            "score": score,
            "avg_odds": mean(odds),
            "best_odds": max(odds),
            "min_odds": min(odds),
            "bookmakers": sorted({row.get("bookmaker") for row in score_rows if row.get("bookmaker")}),
            "rows": score_rows,
        })

    scores.sort(key=lambda item: (item["avg_odds"] or 999, item["score"]))
    return {
        "available": bool(scores),
        "hot": scores[:limit],
        "all": scores,
    }


def bookmaker_margin(odds):
    prices = [safe_float(odds.get(key)) for key in ["home_win", "draw", "away_win"]]
    if any(price is None or price <= 1 for price in prices):
        return None
    return sum(1 / price for price in prices) - 1


def totals_summary(markets):
    if not markets:
        return {"available": False}
    counts = Counter(market.get("line") for market in markets)
    main_line = counts.most_common(1)[0][0]
    selected = [market for market in markets if market.get("line") == main_line]
    over = [safe_float(market.get("over_odds")) for market in selected]
    under = [safe_float(market.get("under_odds")) for market in selected]
    return {
        "available": True,
        "line": main_line,
        "avg_over": mean(over),
        "avg_under": mean(under),
        "best_over": max([value for value in over if value is not None], default=None),
        "best_under": max([value for value in under if value is not None], default=None),
        "rows": selected,
    }
