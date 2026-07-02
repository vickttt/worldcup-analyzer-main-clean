import re
from collections import Counter, defaultdict

from modules.pregame_content import team_cn
from modules.probability_base import true_probability_base


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def mean(values):
    clean = [value for value in values if value is not None]
    return sum(clean) / len(clean) if clean else None


def _fmt_line(value):
    if value is None:
        return "-"
    return f"{float(value):+g}"


def _team_label(match, side):
    if not match:
        return side.title()
    value = match.get("home_cn" if side == "home" else "away_cn") or match.get("home" if side == "home" else "away") or side.title()
    return team_cn(value)


def favorite_side_from_winner_odds(odds):
    if not odds:
        return None
    home = safe_float(odds.get("home_win"))
    away = safe_float(odds.get("away_win"))
    if home is None or away is None:
        return None
    if abs(home - away) < 0.03:
        return None
    return "home" if home < away else "away"


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


def _parsed_handicap_rows(rows):
    parsed_rows = []
    for row in rows or []:
        parsed = parse_handicap_value(row.get("value"))
        odd = safe_float(row.get("odd"))
        if not parsed or odd is None:
            continue
        parsed_rows.append({**row, **parsed, "odd": odd})
    return parsed_rows


def identify_handicap_center(handicap_rows, user_odds=None, odds=None, match=None):
    """Identify the market handicap center without treating coverage as direction."""
    parsed_rows = _parsed_handicap_rows(handicap_rows)
    tpb = true_probability_base(odds)
    probabilities = tpb.get("probabilities") or {}
    draw_probability = probabilities.get("draw", 0)
    if not parsed_rows:
        coverage_needed = bool(probabilities) and draw_probability >= 0.22
        return {
            "available": False,
            "center_label": "No handicap center",
            "direction_label": "No view",
            "coverage_label": "平局对冲" if coverage_needed else "No coverage candidate",
            "outlier_count": 0,
            "coverage_basis": {
                "draw_probability": draw_probability,
                "upset_probability": 0,
                "favorite_gap": 0,
                "coverage_needed": coverage_needed,
                "source": "TPB draw/upset thresholds",
            },
            "coverage_trace": {
                "raw_rows": len(handicap_rows or []),
                "parsed_rows": 0,
                "filtered_rows": 0,
                "secondary_handicap_rows": 0,
                "fallback_used": "draw_based_hedge" if coverage_needed else "no_parsed_rows",
            },
            "warning": "No Asian handicap rows were available.",
        }

    favorite_side = favorite_side_from_winner_odds(odds)
    normalized_same_sign = 0
    if favorite_side:
        by_book_line = defaultdict(dict)
        for row in parsed_rows:
            if row["line"] > 0:
                by_book_line[(row.get("bookmaker"), row["line"])][row["side"]] = row
        for pair in by_book_line.values():
            favorite_row = pair.get(favorite_side)
            other_row = pair.get("away" if favorite_side == "home" else "home")
            if favorite_row and other_row and favorite_row["odd"] < other_row["odd"]:
                favorite_row["line"] = -abs(favorite_row["line"])
                favorite_row["abs_line"] = abs(favorite_row["line"])
                favorite_row["label"] = f"{favorite_row['side'].title()} {favorite_row['line']:+g}"
                normalized_same_sign += 1

    outliers = [
        row for row in parsed_rows
        if row["odd"] < 1.18 or row["odd"] > 5.8 or row["abs_line"] > 2.5
    ]
    center_rows = [
        row for row in parsed_rows
        if 1.18 <= row["odd"] <= 5.8 and row["abs_line"] <= 1.25
    ]
    if not center_rows:
        center_rows = parsed_rows

    favorite_rows = []
    if favorite_side:
        favorite_rows = [
            row for row in center_rows
            if row["side"] == favorite_side and row["line"] <= 0 and row["abs_line"] <= 0.75
        ]
    if not favorite_rows:
        favorite_rows = [
            row for row in center_rows
            if row["abs_line"] <= 0.75 and 1.25 <= row["odd"] <= 2.6
        ]

    grouped = defaultdict(list)
    for row in favorite_rows or center_rows:
        grouped[(row["side"], row["line"])].append(row)

    def group_score(item):
        (side, line), rows = item
        avg_odd = mean([row["odd"] for row in rows]) or 9
        shallow_score = max(0, 1.0 - abs(abs(line) - 0.5))
        balance_score = max(0, 1.0 - min(abs(avg_odd - 1.9), 1.2) / 1.2)
        favorite_score = 0.35 if favorite_side and side == favorite_side and line <= 0 else 0
        return len(rows) * 0.2 + shallow_score + balance_score + favorite_score

    best_key, best_rows = max(grouped.items(), key=group_score)
    center_side, center_line = best_key

    center_lines = sorted({
        row["line"] for row in favorite_rows
        if row["side"] == center_side and row["line"] <= 0 and row["abs_line"] <= 0.75
    }, key=lambda line: (abs(abs(line) - 0.5), abs(line)))
    if len(center_lines) >= 2:
        display_lines = sorted(center_lines[:2])
        line_text = " / ".join(f"{_team_label(match, center_side)} {_fmt_line(line)}" for line in display_lines)
    else:
        line_text = f"{_team_label(match, center_side)} {_fmt_line(center_line)}"

    coverage_side = "away" if center_side == "home" else "home"
    upset_probability = (
        probabilities.get("away_win", 0)
        if coverage_side == "away"
        else probabilities.get("home_win", 0)
    )
    favorite_gap = 0
    if probabilities:
        ordered_probabilities = sorted(probabilities.values(), reverse=True)
        favorite_gap = ordered_probabilities[0] - ordered_probabilities[1]
    coverage_needed = bool(probabilities) and (
        draw_probability >= 0.22
        or upset_probability >= 0.18
        or favorite_gap >= 0.25
    )
    secondary_handicap_rows = [
        row for row in center_rows
        if row["side"] == coverage_side and row["line"] >= 0 and row["abs_line"] <= 0.75
    ]
    relaxed_secondary_handicap_rows = [
        row for row in center_rows
        if row["side"] == coverage_side and row["abs_line"] <= 1.5
    ]
    if coverage_needed and draw_probability >= 0.22:
        coverage_line = None
        coverage_label = "平局对冲"
        fallback_used = "draw_based_hedge"
    elif coverage_needed and upset_probability >= 0.18:
        coverage_line = None
        coverage_label = f"{_team_label(match, coverage_side)}不败对冲"
        fallback_used = "upset_probability_hedge"
    elif coverage_needed:
        coverage_line = None
        coverage_label = f"{_team_label(match, coverage_side)}受让保护"
        fallback_used = "favorite_gap_hedge"
    else:
        coverage_line = None
        coverage_label = "No coverage candidate"
        fallback_used = "none"

    secondary_handicap_label = None
    if secondary_handicap_rows:
        coverage_line = sorted(
            {row["line"] for row in secondary_handicap_rows},
            key=lambda value: (abs(abs(value) - 0.5), -value),
        )[0]
        secondary_handicap_label = f"{_team_label(match, coverage_side)} {_fmt_line(coverage_line)}"
    elif relaxed_secondary_handicap_rows:
        coverage_line = sorted(
            {row["line"] for row in relaxed_secondary_handicap_rows},
            key=lambda value: (value < 0, abs(abs(value) - 0.5), abs(value)),
        )[0]
        secondary_handicap_label = f"{_team_label(match, coverage_side)} {_fmt_line(coverage_line)}"
    coverage_trace = {
        "raw_rows": len(handicap_rows or []),
        "parsed_rows": len(parsed_rows),
        "filtered_rows": len(center_rows),
        "secondary_handicap_rows": len(secondary_handicap_rows),
        "relaxed_secondary_handicap_rows": len(relaxed_secondary_handicap_rows),
        "fallback_used": fallback_used,
    }

    avg_odds = mean([row["odd"] for row in best_rows])
    warning = ""
    if outliers:
        warning = f"{len(outliers)} possible outlier handicap rows were filtered from center detection."
    if normalized_same_sign:
        suffix = f"{normalized_same_sign} same-sign favorite handicap rows were normalized for center detection."
        warning = f"{warning} {suffix}".strip()

    return {
        "available": True,
        "favorite_side": favorite_side,
        "center_side": center_side,
        "center_line": center_line,
        "center_label": line_text,
        "direction_label": f"盘口中心：{line_text}",
        "coverage_side": coverage_side,
        "coverage_line": coverage_line,
        "coverage_label": coverage_label,
        "secondary_handicap_label": secondary_handicap_label,
        "coverage_basis": {
            "draw_probability": draw_probability,
            "upset_probability": upset_probability,
            "favorite_gap": favorite_gap,
            "coverage_needed": coverage_needed,
            "source": "TPB draw/upset thresholds",
        },
        "coverage_trace": coverage_trace,
        "avg_odds": avg_odds,
        "best_odds": max([row["odd"] for row in best_rows], default=None),
        "bookmakers": sorted({row.get("bookmaker") for row in best_rows if row.get("bookmaker")}),
        "rows": best_rows,
        "outlier_count": len(outliers),
        "normalized_same_sign_count": normalized_same_sign,
        "warning": warning,
    }


def asian_handicap_summary(rows):
    parsed_rows = _parsed_handicap_rows(rows)

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


def identify_total_center(total_rows, user_odds=None):
    if not total_rows:
        return {
            "available": False,
            "center_label": "No totals center",
            "market_bias": "Totals market is not available.",
            "recommended_interpretation": "Do not infer goals direction without a totals market.",
        }

    grouped = defaultdict(list)
    for row in total_rows:
        line = safe_float(row.get("line"))
        over = safe_float(row.get("over_odds"))
        under = safe_float(row.get("under_odds"))
        if line is None or over is None or under is None:
            continue
        if over < 1.03 or under < 1.03 or over > 20 or under > 20:
            continue
        grouped[line].append({**row, "line": line, "over_odds": over, "under_odds": under})

    summaries = []
    for line, rows in grouped.items():
        avg_over = mean([row["over_odds"] for row in rows])
        avg_under = mean([row["under_odds"] for row in rows])
        if avg_over is None or avg_under is None:
            continue
        balance = abs(avg_over - avg_under)
        summaries.append({
            "line": line,
            "rows": rows,
            "avg_over": avg_over,
            "avg_under": avg_under,
            "balance": balance,
            "count": len(rows),
        })

    if not summaries:
        return {
            "available": False,
            "center_label": "No totals center",
            "market_bias": "Totals rows were present but could not be parsed.",
            "recommended_interpretation": "Validate the totals market before using it.",
        }

    summaries.sort(key=lambda item: (item["balance"], -item["count"], abs(item["line"] - 2.5)))
    center = summaries[0]
    line_25 = next((item for item in summaries if abs(item["line"] - 2.5) < 0.001), None)
    nearby = []
    if line_25 and abs(center["line"] - 2.5) <= 0.25:
        nearby = [line_25]
    else:
        nearby = [
            item for item in summaries
            if item is not center and abs(item["line"] - center["line"]) <= 0.25 and item["count"] >= 2
        ]
    if nearby:
        lines = sorted({center["line"], nearby[0]["line"]})
        center_label = f"{lines[0]:g}-{lines[-1]:g}"
    else:
        center_label = f"{center['line']:g}"

    if line_25 and line_25["avg_over"] < line_25["avg_under"]:
        market_bias = f"2.5 盘口略偏大球，但在 {center_label} 附近趋于均衡。"
    elif center["avg_over"] < center["avg_under"] and center["balance"] > 0.08:
        market_bias = f"{center_label} 附近略偏大球，但不是激进大球信号。"
    elif center["avg_under"] < center["avg_over"] and center["balance"] > 0.08:
        market_bias = f"{center_label} 附近略偏小球，但不是激进小球信号。"
    else:
        market_bias = f"市场在 {center_label} 附近趋于均衡。"

    return {
        "available": True,
        "center_line": center["line"],
        "center_label": center_label,
        "avg_over": center["avg_over"],
        "avg_under": center["avg_under"],
        "bookmakers": sorted({row.get("bookmaker") for row in center["rows"] if row.get("bookmaker")}),
        "rows": center["rows"],
        "market_bias": market_bias,
        "game_behavior_note": "如果出线形势提示轮换或控节奏风险，应降低激进大球信心。",
        "recommended_interpretation": "存在大球尾部，但进球数观点应以盘口中心为准，不能机械追大 2.5。",
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
