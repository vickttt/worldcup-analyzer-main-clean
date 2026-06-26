import re
from copy import deepcopy


def clamp(value, low=0, high=100):
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    return max(low, min(high, round(number)))


def _fmt_line(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value or "")
    if abs(number) < 0.001:
        return "0"
    text = f"{number:+g}"
    return text


def _parse_line_number(value, inherited_sign=None):
    text = str(value or "").strip()
    if not text:
        return None
    sign = -1 if text.startswith("-") else 1 if text.startswith("+") else inherited_sign or 1
    number_text = text.lstrip("+-")
    try:
        number = float(number_text)
    except ValueError:
        return None
    return sign * abs(number)


def normalize_handicap_line(raw_line):
    """Normalize Asian handicap strings while preserving split-leg settlement data."""
    text = str(raw_line or "").strip()
    text = text.replace("－", "-").replace("＋", "+").replace("—", "-").replace("–", "-")
    text = text.replace(" ", "")
    match = re.search(r"([+-]?\d+(?:\.\d+)?(?:/[+-]?\d+(?:\.\d+)?)?)", text)
    token = match.group(1) if match else text
    if not token:
        return {
            "original_line": "",
            "decimal_line": None,
            "split_legs": [],
            "display_line": "",
            "is_split": False,
        }

    if "/" in token:
        left, right = token.split("/", 1)
        left_value = _parse_line_number(left)
        inherited_sign = -1 if str(left).startswith("-") else 1
        right_value = _parse_line_number(right, inherited_sign=inherited_sign)
        if left_value is None or right_value is None:
            decimal_line = None
            split_legs = []
        elif abs(abs(left_value) - 1.0) < 0.001 and abs(abs(right_value) - 2.0) < 0.001:
            # Asian shorthand: -1/2 means -0.5, +1/2 means +0.5.
            decimal_line = inherited_sign * 0.5
            split_legs = [decimal_line]
        else:
            split_legs = [left_value, right_value]
            decimal_line = sum(split_legs) / 2
    else:
        decimal_line = _parse_line_number(token)
        split_legs = [decimal_line] if decimal_line is not None else []

    is_split = len(split_legs) == 2 and abs(split_legs[0] - split_legs[1]) > 0.001
    display_line = token
    if decimal_line is not None:
        display_line = f"{token} ({_fmt_line(decimal_line)})" if is_split else _fmt_line(decimal_line)
    return {
        "original_line": token,
        "decimal_line": decimal_line,
        "split_legs": split_legs,
        "display_line": display_line,
        "is_split": is_split,
    }


def handicap_line_from_text(value):
    text = str(value or "")
    match = re.search(r"([+-]?\d+(?:\.\d+)?(?:/[+-]?\d+(?:\.\d+)?)?)", text.replace(" ", ""))
    return normalize_handicap_line(match.group(1)) if match else normalize_handicap_line("")


def settle_asian_handicap(score, side, split_legs, odds, stake=1):
    """Return profit for an Asian handicap bet, supporting split lines."""
    try:
        home_goals, away_goals = [int(part) for part in str(score).split(":", 1)]
        price = float(odds)
        amount = float(stake)
    except (TypeError, ValueError):
        return 0
    legs = [float(line) for line in (split_legs or []) if line is not None]
    if not legs:
        return -amount
    leg_stake = amount / len(legs)
    profit = 0
    for line in legs:
        adjusted = home_goals + line if side == "home" else away_goals + line
        opponent = away_goals if side == "home" else home_goals
        diff = adjusted - opponent
        if diff > 0.001:
            profit += leg_stake * (price - 1)
        elif diff < -0.001:
            profit -= leg_stake
    return profit


def _safe_odds(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 1 else None


def normalize_score(value):
    text = str(value or "").strip().replace("：", ":").replace(" - ", ":").replace("-", ":")
    text = re.sub(r"\s+", "", text)
    match = re.search(r"(\d+):(\d+)", text)
    return f"{int(match.group(1))}:{int(match.group(2))}" if match else text


def total_side_and_line(value):
    text = str(value or "").lower()
    line_match = re.search(r"(\d+(?:\.\d+)?)", text)
    line = float(line_match.group(1)) if line_match else None
    if "under" in text or "小" in text:
        return "under", line
    if "over" in text or "大" in text:
        return "over", line
    return None, line


def build_bet_id(bet):
    bet_type = str(bet.get("type") or "unknown").strip().lower()
    odds = _safe_odds(bet.get("effective_odds") or bet.get("odds") or bet.get("standard_odds"))
    odds_part = f"{odds:.4f}" if odds else "no_odds"
    selection = str(bet.get("selection") or bet.get("name") or "").strip().lower()
    if bet_type == "handicap":
        line_info = bet.get("handicap_line") or handicap_line_from_text(selection)
        side = str(bet.get("handicap_side") or ("home" if "home" in selection else "away" if "away" in selection else "")).lower()
        line = line_info.get("decimal_line")
        line_part = f"{line:+.4f}" if line is not None else "no_line"
        return f"handicap|{side}|{line_part}|{odds_part}"
    if bet_type == "total":
        side, line = total_side_and_line(selection)
        line_part = f"{line:.4f}" if line is not None else "no_line"
        return f"total|{side or 'unknown'}|{line_part}|{odds_part}"
    if bet_type == "correct_score":
        return f"correct_score|{normalize_score(selection)}|{odds_part}"
    return f"{bet_type}|{selection}|{odds_part}"


def dedupe_bets(bets):
    seen = {}
    for bet in bets or []:
        key = build_bet_id(bet)
        current_score = float((seen.get(key) or {}).get("score") or 0)
        new_score = float(bet.get("score") or 0)
        if key not in seen or new_score >= current_score:
            enriched = deepcopy(bet)
            enriched["bet_id"] = key
            merged_roles = []
            if key in seen:
                merged_roles.extend(seen[key].get("roles") or seen[key].get("role_tags") or [])
            merged_roles.extend(enriched.get("roles") or enriched.get("role_tags") or [])
            if merged_roles:
                enriched["roles"] = list(dict.fromkeys(str(role) for role in merged_roles if role))
            seen[key] = enriched
        else:
            merged_roles = []
            merged_roles.extend(seen[key].get("roles") or seen[key].get("role_tags") or [])
            merged_roles.extend(bet.get("roles") or bet.get("role_tags") or [])
            if merged_roles:
                seen[key]["roles"] = list(dict.fromkeys(str(role) for role in merged_roles if role))
    return list(seen.values())


def portfolio_id(strategy):
    return "|".join(sorted(build_bet_id(item) for item in (strategy.get("items") or []) if item.get("type") != "empty"))


def dedupe_portfolios(portfolios):
    best = {}
    ordered = []
    for strategy in portfolios or []:
        key = portfolio_id(strategy)
        if not key:
            ordered.append(strategy)
            continue
        score = float(strategy.get("score") or 0)
        if key not in best:
            best[key] = strategy
            ordered.append(strategy)
        elif score > float(best[key].get("score") or 0):
            previous = best[key]
            best[key] = strategy
            for index, item in enumerate(ordered):
                if item is previous:
                    ordered[index] = strategy
                    break
    return ordered


def favorite_is_home(match, distribution):
    favorite = str((distribution or {}).get("favorite") or "")
    home_names = {
        str((match or {}).get("home_cn") or ""),
        str((match or {}).get("home_en") or ""),
        str((match or {}).get("home") or ""),
    }
    return not favorite or favorite in home_names


def scenario_category(score, match, distribution):
    try:
        home_goals, away_goals = [int(part) for part in str(score).split(":", 1)]
    except (TypeError, ValueError):
        return "noise"
    fav_home = favorite_is_home(match, distribution)
    fav_margin = home_goals - away_goals if fav_home else away_goals - home_goals
    total = home_goals + away_goals
    if total >= 8 or abs(home_goals - away_goals) >= 6:
        return "noise"
    main_path = str((distribution or {}).get("main_path") or "")
    if "3球以上" in main_path:
        main_margins = {3, 4}
    elif "赢2球" in main_path:
        main_margins = {2}
    elif "小胜" in main_path or "1球" in main_path:
        main_margins = {1}
    else:
        main_margins = {1, 2} if fav_margin > 0 else {0}
    if fav_margin in main_margins:
        return "main"
    if fav_margin > 0 and any(abs(fav_margin - margin) == 1 for margin in main_margins):
        return "adjacent"
    if fav_margin == 0 or (fav_margin > 0 and fav_margin <= 4):
        return "tail"
    return "noise"


def classify_scenario(score, market_context):
    """Classify a score into main, adjacent, tail, or noise scenario buckets."""
    match = (market_context or {}).get("match") or market_context or {}
    distribution = (market_context or {}).get("distribution") or market_context or {}
    category = scenario_category(score, match, distribution)
    try:
        home_goals, away_goals = [int(part) for part in str(score).split(":", 1)]
    except (TypeError, ValueError):
        home_goals, away_goals = 0, 0
    fav_home = favorite_is_home(match, distribution)
    favorite_goals = home_goals if fav_home else away_goals
    underdog_goals = away_goals if fav_home else home_goals
    return {
        "score": str(score),
        "home_goals": home_goals,
        "away_goals": away_goals,
        "favorite_goals": favorite_goals,
        "underdog_goals": underdog_goals,
        "margin": favorite_goals - underdog_goals,
        "total_goals": home_goals + away_goals,
        "winner": "home" if home_goals > away_goals else "away" if away_goals > home_goals else "draw",
        "scenario_type": category,
        "is_main_scenario": category == "main",
        "is_adjacent_scenario": category == "adjacent",
        "is_tail_scenario": category == "tail",
        "is_noise_scenario": category == "noise",
        "plausibility_score": {"main": 0.95, "adjacent": 0.75, "tail": 0.35, "noise": 0.10}.get(category, 0.10),
    }


def _line_alignment(score, line):
    try:
        home_goals, away_goals = [int(part) for part in str(score).split(":", 1)]
        value = float(line)
    except (TypeError, ValueError):
        return 0.60
    margin = home_goals - away_goals
    if value < 0:
        required = abs(value)
        if margin > required:
            return 1.00
        if margin >= required - 1:
            return 0.72
        return 0.36
    if value > 0:
        if margin < value:
            return 0.90
        if margin <= value + 1:
            return 0.65
        return 0.35
    return 0.60


def _total_alignment(score, line, side=None):
    try:
        home_goals, away_goals = [int(part) for part in str(score).split(":", 1)]
        value = float(line)
    except (TypeError, ValueError):
        return 0.60
    total = home_goals + away_goals
    if side == "over":
        if total > value:
            return 1.00
        if total >= value - 1:
            return 0.68
        return 0.38
    if side == "under":
        if total < value:
            return 1.00
        if total <= value + 1:
            return 0.68
        return 0.38
    return max(0.35, 1 - min(3, abs(total - value)) * 0.20)


def _market_context_lines(odds_data):
    handicap_line = None
    total_line = None
    total_side = None
    handicap = (odds_data or {}).get("handicap") or (odds_data or {}).get("asian_handicap") or {}
    if isinstance(handicap, dict):
        handicap_line = handicap.get("line") or handicap.get("main_line")
    totals = (odds_data or {}).get("totals") or (odds_data or {}).get("over_under") or {}
    if isinstance(totals, dict):
        total_line = totals.get("line") or totals.get("main_line")
        total_side = totals.get("side") or totals.get("lean")
    if isinstance(totals, list) and totals:
        first = totals[0]
        total_line = first.get("line") if isinstance(first, dict) else None
        total_side = first.get("side") if isinstance(first, dict) else None
    return handicap_line, total_line, str(total_side or "").lower() or None


def _score_probability_from_market(score, odds_rows):
    score_key = normalize_score(score)
    prices = []
    for row in odds_rows or []:
        raw_score = normalize_score(row.get("score") or row.get("value") or row.get("selection"))
        if raw_score != score_key:
            continue
        price = _safe_odds(row.get("odd") or row.get("odds") or row.get("price"))
        if price:
            prices.append(price)
    if not prices:
        return None
    avg_price = sum(prices) / len(prices)
    return 1 / avg_price


def qualification_score_multiplier(score, match, distribution):
    behavior = (distribution or {}).get("game_behavior") or {}
    adjustments = behavior.get("behavior_adjustments") or {}
    goals = _score_goals(normalize_score(score))
    if not goals or not adjustments:
        return 1.0
    home_goals, away_goals = goals
    goal_diff = abs(home_goals - away_goals)
    total_goals = home_goals + away_goals
    multiplier = 1.0
    if adjustments.get("draw_weight_delta", 0) > 0 and home_goals == away_goals:
        multiplier += 0.12 * adjustments.get("draw_weight_delta", 0)
    if adjustments.get("under_weight_delta", 0) > 0 and total_goals <= 2:
        multiplier += 0.08 * adjustments.get("under_weight_delta", 0)
    if adjustments.get("over_weight_delta", 0) > 0 and total_goals >= 3:
        multiplier += 0.07 * adjustments.get("over_weight_delta", 0)
    if adjustments.get("favorite_small_win_weight_delta", 0) > 0 and goal_diff == 1:
        multiplier += 0.08 * adjustments.get("favorite_small_win_weight_delta", 0)
    if adjustments.get("deep_handicap_risk_delta", 0) > 0 and goal_diff >= 3:
        multiplier -= 0.08 * adjustments.get("deep_handicap_risk_delta", 0)
    if adjustments.get("underdog_goal_weight_delta", 0) > 0:
        favorite = str((distribution or {}).get("favorite") or "")
        home_name = str((match or {}).get("home_cn") or (match or {}).get("home_en") or "")
        favorite_home = favorite in {home_name, str((match or {}).get("home_en") or "")}
        underdog_goal = away_goals > 0 if favorite_home else home_goals > 0
        if underdog_goal:
            multiplier += 0.08 * adjustments.get("underdog_goal_weight_delta", 0)
    if adjustments.get("late_goal_volatility_delta", 0) > 0 and total_goals >= 3:
        multiplier += 0.05 * adjustments.get("late_goal_volatility_delta", 0)
    return max(0.45, min(1.65, multiplier))


def build_score_scenario_grid(match_data, odds_data=None):
    """Build a score grid with required scenario fields and market-implied weights when available."""
    match = (match_data or {}).get("match") or match_data or {}
    distribution = (match_data or {}).get("distribution") or {}
    rows = []
    market_rows = (
        ((odds_data or {}).get("correct_score") or {}).get("rows")
        or (odds_data or {}).get("correct_score_rows")
        or (odds_data or {}).get("rows")
        or []
    )
    scores = []
    for row in market_rows:
        score = normalize_score(row.get("score") or row.get("value") or row.get("selection"))
        if re.match(r"^\d+:\d+$", score) and score not in scores:
            scores.append(score)
    if not scores:
        scores = [f"{home}:{away}" for home in range(0, 8) for away in range(0, 4)]
    implied_probs = {}
    for score in scores:
        implied_probs[score] = _score_probability_from_market(score, market_rows)
    implied_total = sum(value for value in implied_probs.values() if value is not None) or 0
    handicap_line, total_line, total_side = _market_context_lines(odds_data or {})
    raw_weights = {}
    confidence_penalties = []
    for score in scores:
        implied = implied_probs.get(score)
        category = scenario_category(score, match, distribution)
        devig = implied / implied_total if implied is not None and implied_total else None
        fallback = {"main": 0.08, "adjacent": 0.045, "tail": 0.02, "noise": 0.004}.get(category, 0.004)
        handicap_alignment = _line_alignment(score, handicap_line) if handicap_line is not None else 0.60
        total_alignment = _total_alignment(score, total_line, total_side) if total_line is not None else 0.60
        if category in {"main", "adjacent"} and (handicap_alignment < 0.45 or total_alignment < 0.45):
            confidence_penalties.append(score)
        raw_weights[score] = (
            (devig if devig is not None else fallback)
            * (0.65 + handicap_alignment * 0.20 + total_alignment * 0.15)
            * qualification_score_multiplier(score, match, distribution)
        )
    total = sum(raw_weights.values()) or 1
    for score in scores:
        classified = classify_scenario(score, {"match": match, "distribution": distribution})
        raw_implied = implied_probs.get(score)
        devig = raw_implied / implied_total if raw_implied is not None and implied_total else None
        handicap_alignment = _line_alignment(score, handicap_line) if handicap_line is not None else 0.60
        total_alignment = _total_alignment(score, total_line, total_side) if total_line is not None else 0.60
        final_weight = raw_weights[score] / total
        classified.update({
            "classification": "reasonable_tail" if classified["scenario_type"] == "tail" else "noise_tail" if classified["scenario_type"] == "noise" else classified["scenario_type"],
            "raw_implied_probability": raw_implied,
            "devig_probability": devig,
            "handicap_alignment": handicap_alignment,
            "total_alignment": total_alignment,
            "final_scenario_weight": final_weight,
            "scenario_weight": final_weight,
            "confidence": 0.75 if confidence_penalties else 0.90,
            "calibration_note": "波胆隐含概率已去水，并按让球/大小球方向做轻量校准。" if implied_total else "波胆数据不足，使用让球/大小球启发式权重。",
        })
        rows.append(classified)
    rows.sort(key=lambda row: row.get("scenario_weight", 0), reverse=True)
    return rows


def _row_probability(row):
    if row.get("_probability") is not None:
        return float(row.get("_probability") or 0)
    text = str(row.get("比分概率") or "").replace("%", "")
    try:
        return float(text) / 100
    except (TypeError, ValueError):
        return 0


def compute_coverage_metrics(items, score_rows, match, distribution, total_stake=None):
    total_stake = total_stake or sum(float(item.get("amount") or 0) for item in items or [])
    buckets = {
        "main": {"prob": 0, "covered": 0, "loss": 0},
        "adjacent": {"prob": 0, "covered": 0, "loss": 0},
        "tail": {"prob": 0, "covered": 0, "loss": 0},
        "noise": {"prob": 0, "covered": 0, "loss": 0},
    }
    covered_scores = []
    not_covered_scores = []
    zero_prob = 0
    one_goal_prob = 0
    for row in score_rows or []:
        score = row.get("比分") or row.get("score")
        probability = _row_probability(row)
        profit = float(row.get("_total") or 0)
        category = scenario_category(score, match, distribution)
        bucket = buckets.setdefault(category, {"prob": 0, "covered": 0, "loss": 0})
        bucket["prob"] += probability
        if profit > 0:
            bucket["covered"] += probability
            covered_scores.append(str(score))
        else:
            bucket["loss"] += probability
            if category != "noise":
                not_covered_scores.append(str(score))
        if category in {"main", "adjacent", "tail"} and profit <= 0:
            zero_prob += probability
        if category == "adjacent" and profit <= 0:
            one_goal_prob += probability

    def rate(name):
        data = buckets.get(name) or {}
        return data.get("covered", 0) / data.get("prob", 0) if data.get("prob", 0) else 0

    main = rate("main")
    adjacent = rate("adjacent")
    tail = rate("tail")
    zero_risk = min(1, zero_prob)
    one_goal_risk = min(1, one_goal_prob)
    coverage_score = clamp(main * 45 + adjacent * 30 + tail * 10 + (1 - zero_risk) * 10 + (1 - one_goal_risk) * 5)
    zero_score = clamp((1 - zero_risk) * 100)
    return {
        "main_coverage": main,
        "adjacent_coverage": adjacent,
        "tail_coverage": tail,
        "zero_risk": zero_risk,
        "one_goal_deviation_risk": one_goal_risk,
        "coverage_score": coverage_score,
        "zero_risk_score": zero_score,
        "covered_scores": list(dict.fromkeys(covered_scores))[:8],
        "not_covered_scores": list(dict.fromkeys(not_covered_scores))[:8],
        "summary": f"主剧本{main * 100:.0f}% / 邻近{adjacent * 100:.0f}% / 尾部{tail * 100:.0f}%",
    }


def scenario_alignment_for_bet(bet, match, distribution):
    bet_type = bet.get("type")
    if bet_type == "winner":
        selection = str(bet.get("selection") or bet.get("name") or "").lower()
        favorite = str((distribution or {}).get("favorite") or "").lower()
        home_names = {
            str((match or {}).get("home_cn") or "").lower(),
            str((match or {}).get("home_en") or "").lower(),
            str((match or {}).get("home") or "").lower(),
        }
        away_names = {
            str((match or {}).get("away_cn") or "").lower(),
            str((match or {}).get("away_en") or "").lower(),
            str((match or {}).get("away") or "").lower(),
        }
        favorite_home = favorite in home_names or favorite_is_home(match, distribution)
        if "draw" in selection or "平" in selection:
            return 0.35, 0.45
        def selected(names):
            for name in names:
                if not name:
                    continue
                tokens = [token for token in re.split(r"[\s&.-]+", name) if len(token) >= 3]
                if name in selection or any(token in selection for token in tokens):
                    return True
            return False

        home_selected = selected(home_names) or "home" in selection
        away_selected = selected(away_names) or "away" in selection
        if (favorite_home and home_selected) or ((not favorite_home) and away_selected):
            return 0.95, 0.90
        if home_selected or away_selected:
            return 0.10, 0.15
        return 0.50, 0.50
    if bet_type == "handicap":
        return 0.90, 0.90
    if bet_type == "total":
        return 0.55, 0.70
    if bet_type == "correct_score":
        category = scenario_category(bet.get("selection"), match, distribution)
        if category == "main":
            return 1.0, 0.95
        if category == "adjacent":
            return 0.80, 0.75
        if category == "tail":
            return 0.45, 0.35
        return 0.05, 0.10
    return 0.25, 0.25


def compute_directional_odds_value(items, match, distribution):
    weighted = []
    noise = []
    details = []
    for item in items or []:
        edge = item.get("edge")
        if edge is None:
            edge = item.get("ev_lift")
        if edge is None:
            continue
        alignment, plausibility = scenario_alignment_for_bet(item, match, distribution)
        name = item.get("name") or item.get("selection") or "-"
        market_support = clamp(item.get("market_center_score", 55), 0, 100) / 100 if item.get("type") == "correct_score" else 0.75
        noise_penalty = 0
        decision = "Included"
        if plausibility < 0.25 or alignment < 0.25:
            noise_penalty = 1
            decision = "Noise"
        elif plausibility < 0.45 or alignment < 0.45:
            noise_penalty = 0.5
            decision = "Low Weight"
        if decision == "Noise":
            noise.append(f"{name}: 偏离主剧本，作为噪音价值剔除")
            details.append({
                "bet": name,
                "user_odds": item.get("actual_odds") or item.get("odds") or item.get("effective_odds"),
                "market_avg": item.get("standard_odds"),
                "price_edge": float(edge),
                "scenario_alignment_score": alignment,
                "plausibility_score": plausibility,
                "market_support_score": market_support,
                "noise_penalty": noise_penalty,
                "weighted_edge": 0,
                "decision": decision,
            })
            continue
        weight = alignment * plausibility * market_support * (1 - noise_penalty * 0.65)
        capped_edge = max(-0.12, min(0.12, float(edge)))
        weighted_edge = capped_edge * weight
        details.append({
            "bet": name,
            "user_odds": item.get("actual_odds") or item.get("odds") or item.get("effective_odds"),
            "market_avg": item.get("standard_odds"),
            "price_edge": float(edge),
            "scenario_alignment_score": alignment,
            "plausibility_score": plausibility,
            "market_support_score": market_support,
            "noise_penalty": noise_penalty,
            "weighted_edge": weighted_edge,
            "decision": decision,
        })
        weighted.append((weighted_edge, weight, name, edge))
    if not weighted:
        return {
            "score": 45,
            "weighted_edge": 0,
            "notes": noise or ["没有录入主方向真实赔率，按中性处理。"],
            "noise_notes": noise,
            "details": details,
            "top_positive_edges": [],
            "ignored_noise_edges": noise,
        }
    weighted_edge = sum(value for value, _, _, _ in weighted) / sum(weight for _, weight, _, _ in weighted)
    score = clamp(50 + weighted_edge * 450)
    notes = [f"{name}: 主方向权重后价差 {edge * 100:+.1f}%" for _, _, name, edge in weighted[:4]]
    notes.extend(noise[:2])
    return {
        "score": score,
        "weighted_edge": weighted_edge,
        "notes": notes,
        "noise_notes": noise,
        "details": details,
        "top_positive_edges": [
            item for item in sorted(details, key=lambda row: row.get("weighted_edge", 0), reverse=True)
            if item.get("decision") != "Noise"
        ][:5],
        "ignored_noise_edges": [item for item in details if item.get("decision") == "Noise"],
    }


def _portfolio_profit_for_score(items, score):
    profit = 0
    for item in items or []:
        stake = float(item.get("amount") or 0)
        odds = _safe_odds(item.get("odds") or item.get("effective_odds") or item.get("standard_odds"))
        if not stake or not odds:
            continue
        bet_type = item.get("type")
        try:
            home_goals, away_goals = [int(part) for part in str(score).split(":", 1)]
        except (TypeError, ValueError):
            continue
        if bet_type == "handicap":
            side = item.get("handicap_side") or ("home" if "home" in str(item.get("selection") or "").lower() else "away")
            line_info = item.get("handicap_line") or handicap_line_from_text(item.get("selection") or item.get("name"))
            profit += settle_asian_handicap(score, side, line_info.get("split_legs"), odds, stake)
        elif bet_type == "correct_score":
            profit += stake * (odds - 1) if normalize_score(item.get("selection")) == normalize_score(score) else -stake
        elif bet_type == "total":
            side, line = total_side_and_line(item.get("selection") or item.get("name"))
            total_goals = home_goals + away_goals
            win = (side == "over" and total_goals > line) or (side == "under" and total_goals < line)
            profit += stake * (odds - 1) if win else -stake
        elif bet_type == "winner":
            selection = str(item.get("selection") or item.get("name") or "").lower()
            winner = "home" if home_goals > away_goals else "away" if away_goals > home_goals else "draw"
            win = winner in selection or ("平局" in selection and winner == "draw")
            profit += stake * (odds - 1) if win else -stake
    return profit


def compute_portfolio_pnl_by_score(portfolio, score_grid):
    items = portfolio.get("items") if isinstance(portfolio, dict) else portfolio
    rows = []
    for scenario in score_grid or []:
        score = scenario.get("score")
        profit = _portfolio_profit_for_score(items, score)
        rows.append({**scenario, "profit": profit})
    return rows


def _scenario_probability(row):
    if row.get("_probability") is not None:
        try:
            return float(row.get("_probability") or 0)
        except (TypeError, ValueError):
            return 0
    for key in ("scenario_weight", "final_scenario_weight", "probability"):
        if row.get(key) is not None:
            try:
                return float(row.get(key) or 0)
            except (TypeError, ValueError):
                return 0
    return _row_probability(row)


def _scenario_profit(row):
    for key in ("_total", "profit", "组合收益"):
        value = row.get(key)
        if value is None:
            continue
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value).replace(",", ""))
        if match:
            return float(match.group(0))
    return 0


def _scenario_score_text(row):
    return str(row.get("比分") or row.get("score") or "")


def _risk_gate_strictness(distribution):
    behavior = (distribution or {}).get("game_behavior") or {}
    pressure_type = behavior.get("match_pressure_type")
    adjustments = behavior.get("behavior_adjustments") or {}
    strict = 1.0
    if pressure_type in {
        "qualified_favorite_vs_must_win_underdog",
        "both_draw_acceptable",
        "direct_second_place_battle",
        "must_win_vs_must_win",
        "qualified_vs_qualified",
        "favorite_must_win",
    }:
        strict += 0.25
    if adjustments.get("deep_handicap_risk_delta", 0) > 0:
        strict += 0.15
    if adjustments.get("draw_weight_delta", 0) >= 2 or adjustments.get("chaos_risk_delta", 0) >= 2:
        strict += 0.15
    return strict


def portfolio_risk_gate(portfolio, score_grid=None, match_context=None):
    """Hard zero-risk gate used before selecting the Rank #1 recommendation."""
    items = (portfolio or {}).get("items") if isinstance(portfolio, dict) else portfolio
    items = [item for item in (items or []) if item.get("type") != "empty"]
    rows = score_grid or ((portfolio or {}).get("score_rows") if isinstance(portfolio, dict) else []) or []
    match = (match_context or {}).get("match") or {}
    distribution = (match_context or {}).get("distribution") or match_context or {}
    strictness = _risk_gate_strictness(distribution)
    relevant = [
        row for row in rows
        if (row.get("scenario_type") or scenario_category(_scenario_score_text(row), match, distribution)) in {"main", "adjacent", "tail"}
    ]
    if not relevant:
        return {
            "passed": True,
            "reason": "No scenario grid available; risk gate treated as neutral.",
            "failed_paths": [],
            "risk_level": "LOW",
        }

    total_prob = sum(_scenario_probability(row) for row in relevant) or 1
    failed = [row for row in relevant if _scenario_profit(row) <= 0]
    failed_prob = sum(_scenario_probability(row) for row in failed) / total_prob
    adjacent = [
        row for row in relevant
        if (row.get("scenario_type") or scenario_category(_scenario_score_text(row), match, distribution)) == "adjacent"
    ]
    adjacent_total = sum(_scenario_probability(row) for row in adjacent) or 0
    adjacent_failed_prob = (
        sum(_scenario_probability(row) for row in adjacent if _scenario_profit(row) <= 0) / adjacent_total
        if adjacent_total
        else 0
    )
    main = [
        row for row in relevant
        if (row.get("scenario_type") or scenario_category(_scenario_score_text(row), match, distribution)) == "main"
    ]
    main_total = sum(_scenario_probability(row) for row in main) or 0
    main_positive = (
        sum(_scenario_probability(row) for row in main if _scenario_profit(row) > 0) / main_total
        if main_total
        else 1
    )
    score_items = [item for item in items if item.get("type") == "correct_score"]
    core_items = [item for item in items if item.get("type") in {"winner", "handicap", "total"}]
    score_stake = sum(float(item.get("amount") or 0) for item in score_items)
    total_stake = sum(float(item.get("amount") or 0) for item in items) or 1
    profitable_paths = [row for row in relevant if _scenario_profit(row) > 0]
    only_narrow_scores_profit = bool(score_items) and not core_items and len(profitable_paths) <= max(2, len(score_items))

    blockers = []
    if failed_prob >= 0.42 / strictness:
        blockers.append(f"reasonable scenario loss probability {failed_prob * 100:.0f}%")
    if adjacent_failed_prob >= 0.70 / strictness:
        blockers.append(f"adjacent path failure {adjacent_failed_prob * 100:.0f}%")
    if main_positive < 0.50:
        blockers.append(f"main path positive coverage only {main_positive * 100:.0f}%")
    if score_stake / total_stake > 0.45 and failed_prob >= 0.25:
        blockers.append("correct-score exposure creates narrow-path dependency")
    if only_narrow_scores_profit:
        blockers.append("portfolio profits only in narrow exact-score paths")

    if failed_prob >= 0.60 or adjacent_failed_prob >= 0.85 or only_narrow_scores_profit:
        risk_level = "CRITICAL"
    elif failed_prob >= 0.38 or adjacent_failed_prob >= 0.65 or blockers:
        risk_level = "HIGH"
    elif failed_prob >= 0.22:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    passed = risk_level in {"LOW", "MEDIUM"} and not any("only" in blocker for blocker in blockers)
    if strictness > 1.2 and risk_level == "MEDIUM" and adjacent_failed_prob >= 0.45:
        passed = False
        blockers.append("qualification pressure makes adjacent-path failure unacceptable")
        risk_level = "HIGH"

    failed_paths = [
        _scenario_score_text(row)
        for row in sorted(failed, key=lambda item: _scenario_probability(item), reverse=True)
    ][:6]
    return {
        "passed": passed,
        "reason": "Passed zero-risk gate." if passed else "High EV but failed risk gate: " + "; ".join(blockers[:3]),
        "failed_paths": failed_paths,
        "risk_level": risk_level,
        "failed_probability": failed_prob,
        "adjacent_failed_probability": adjacent_failed_prob,
        "main_positive_coverage": main_positive,
    }


def correct_score_exposure_control(portfolio, style=None):
    items = (portfolio or {}).get("items") if isinstance(portfolio, dict) else portfolio
    items = [item for item in (items or []) if item.get("type") != "empty"]
    total_stake = sum(float(item.get("amount") or 0) for item in items) or 0
    score_items = [item for item in items if item.get("type") == "correct_score"]
    score_stake = sum(float(item.get("amount") or 0) for item in score_items)
    stake_share = score_stake / total_stake if total_stake else 0
    style_text = str(style or (portfolio or {}).get("name") or (portfolio or {}).get("portfolio_style_label") or "")
    limit = 0.30
    if "Aggressive" in style_text or "激进" in style_text:
        limit = 0.40
    if "Conservative" in style_text or "保守" in style_text:
        limit = 0.20

    scores = [normalize_score(item.get("selection") or item.get("name")) for item in score_items]
    parsed = [_score_goals(score) for score in scores]
    parsed = [goals for goals in parsed if goals]
    clean_sheet = [goals for goals in parsed if min(goals) == 0]
    high_margin = [goals for goals in parsed if abs(goals[0] - goals[1]) >= 3]
    balanced = [goals for goals in parsed if min(goals) > 0 or abs(goals[0] - goals[1]) <= 1]
    if score_items and len(clean_sheet) >= max(2, len(score_items) - 1):
        cluster = "clean_sheet_cluster"
    elif score_items and len(high_margin) >= max(2, len(score_items) - 1):
        cluster = "high_margin_cluster"
    elif score_items:
        cluster = "balanced_cluster" if balanced else "mixed_cluster"
    else:
        cluster = "none"

    core_items = [item for item in items if item.get("type") in {"winner", "handicap", "total"}]
    dependent = bool(score_items) and (stake_share > limit or not core_items)
    warnings = []
    if stake_share > limit:
        warnings.append(f"correct score stake share {stake_share * 100:.0f}% exceeds {limit * 100:.0f}% limit")
    if dependent:
        warnings.append("correct_score_dependent")
    if cluster in {"clean_sheet_cluster", "high_margin_cluster"} and len(score_items) >= 2:
        warnings.append("clean_sheet_score_cluster_risk" if cluster == "clean_sheet_cluster" else "high_margin_cluster_risk")
    return {
        "count": len(score_items),
        "stake_share": stake_share,
        "limit": limit,
        "passed": not warnings,
        "dependent": dependent,
        "cluster_type": cluster,
        "warning": "; ".join(warnings) if warnings else "Correct score exposure controlled.",
    }


def rank1_eligibility_check(portfolio, match=None, distribution=None):
    risk_gate = (portfolio or {}).get("risk_gate") or portfolio_risk_gate(
        portfolio,
        (portfolio or {}).get("score_rows") or [],
        {"match": match or {}, "distribution": distribution or {}},
    )
    exposure = (portfolio or {}).get("correct_score_exposure") or correct_score_exposure_control(portfolio)
    pressure_fit = (portfolio or {}).get("pressure_fit") or strategy_pressure_fit(
        (portfolio or {}).get("items") or [],
        match or {},
        distribution or {},
    )
    blockers = []
    if not risk_gate.get("passed"):
        blockers.append(risk_gate.get("reason") or "failed zero-risk gate")
    if not exposure.get("passed"):
        blockers.append(exposure.get("warning") or "correct-score exposure failed")
    if pressure_fit.get("label") == "Low":
        blockers.append("qualification pressure fit is LOW")
    coverage = (portfolio or {}).get("coverage_metrics") or {}
    if coverage:
        if coverage.get("main_coverage", 0) <= 0 and coverage.get("adjacent_coverage", 0) <= 0:
            blockers.append("does not cover main or adjacent path")
    directional = (portfolio or {}).get("directional_odds_value") or {}
    if directional.get("score", 50) < 25 and exposure.get("dependent"):
        blockers.append("odds value is mainly narrow exact-score noise")
    return {
        "rank1_eligible": not blockers,
        "eligible": not blockers,
        "rank1_blockers": blockers,
        "summary": "Eligible for Rank #1." if not blockers else "Not Rank #1 eligible: " + "; ".join(blockers[:3]),
    }


def compute_portfolio_marginal_utility(base_portfolio, candidate_variants, score_grid):
    base_items = (base_portfolio or {}).get("items") or []
    base_stake = sum(float(item.get("amount") or 0) for item in base_items)
    base_rows = compute_portfolio_pnl_by_score({"items": base_items}, score_grid or [])
    base_stats = _weighted_stats(base_rows, base_stake)
    rows = []
    for variant in candidate_variants or []:
        variant_items = variant.get("items") or base_items
        stake = sum(float(item.get("amount") or 0) for item in variant_items)
        variant_rows = compute_portfolio_pnl_by_score({"items": variant_items}, score_grid or [])
        stats = _weighted_stats(variant_rows, stake)
        zero_gain = base_stats["zero_risk"] - stats["zero_risk"]
        loss_gain = base_stats["max_loss"] - stats["max_loss"]
        ev_delta = stats["ev"] - base_stats["ev"]
        roi_delta = stats["roi"] - base_stats["roi"]
        complexity_delta = len(variant_items) - len(base_items)
        if zero_gain > 0.08 and loss_gain >= 0 and ev_delta > -base_stake * 0.03:
            recommendation = "Replace"
        elif zero_gain > 0.04 or loss_gain > base_stake * 0.08:
            recommendation = "Review"
        elif ev_delta > 0 and stats["zero_risk"] <= base_stats["zero_risk"]:
            recommendation = "Add"
        else:
            recommendation = "Do Not Add"
        rows.append({
            "variant": variant.get("name") or "Variant",
            "base_score": (base_portfolio or {}).get("score"),
            "new_score": None,
            "base_expected_profit": base_stats["ev"],
            "new_expected_profit": stats["ev"],
            "base_zero_risk": base_stats["zero_risk"],
            "new_zero_risk": stats["zero_risk"],
            "base_max_loss": base_stats["max_loss"],
            "new_max_loss": stats["max_loss"],
            "coverage_gain": zero_gain,
            "ev_roi_delta": roi_delta,
            "ev_delta": ev_delta,
            "complexity_delta": complexity_delta,
            "recommendation": recommendation,
        })
    rows.sort(key=lambda row: (row["recommendation"] == "Replace", row["coverage_gain"], row["ev_delta"]), reverse=True)
    return rows


def _score_goals(score):
    try:
        return [int(part) for part in str(score).split(":", 1)]
    except (TypeError, ValueError):
        return None


def _handicap_depth(item):
    if item.get("type") != "handicap":
        return 0
    parsed = normalize_handicap_line(str(item.get("selection") or item.get("name") or ""))
    try:
        return abs(float(parsed.get("decimal_line") or 0))
    except (TypeError, ValueError):
        return 0


def _score_has_underdog_goal(item, match, distribution):
    if item.get("type") != "correct_score":
        return False
    goals = _score_goals(normalize_score(item.get("selection")))
    if not goals:
        return False
    home_goals, away_goals = goals
    favorite = str((distribution or {}).get("favorite") or "")
    home_name = str((match or {}).get("home_cn") or (match or {}).get("home_en") or "")
    favorite_home = favorite in {home_name, str((match or {}).get("home_en") or "")}
    return away_goals > 0 if favorite_home else home_goals > 0


def _score_is_narrow(item):
    if item.get("type") != "correct_score":
        return False
    goals = _score_goals(normalize_score(item.get("selection")))
    if not goals:
        return False
    return abs(goals[0] - goals[1]) <= 1 and sum(goals) <= 3


def _score_is_blowout(item):
    if item.get("type") != "correct_score":
        return False
    goals = _score_goals(normalize_score(item.get("selection")))
    if not goals:
        return False
    return abs(goals[0] - goals[1]) >= 3 or sum(goals) >= 5


def _total_side(item):
    if item.get("type") != "total":
        return None
    text = str(item.get("selection") or item.get("name") or "").lower()
    if "under" in text or "小" in text:
        return "under"
    if "over" in text or "大" in text:
        return "over"
    return None


def strategy_pressure_fit(items, match, distribution):
    behavior = (distribution or {}).get("game_behavior") or {}
    adjustments = behavior.get("behavior_adjustments") or {}
    if not adjustments:
        return {"score": 70, "label": "Medium", "reason": "暂无明确出线压力，按中性处理。", "matched": [], "missing": []}

    score = 70
    matched = []
    missing = []
    items = [item for item in items or [] if item.get("type") != "empty"]
    has_deep = any(_handicap_depth(item) >= 1.5 for item in items)
    has_shallow = any(item.get("type") == "handicap" and 0 < _handicap_depth(item) <= 1.25 for item in items)
    has_under = any(_total_side(item) == "under" for item in items)
    has_over = any(_total_side(item) == "over" for item in items)
    has_drawish = any(item.get("type") == "winner" and "draw" in str(item.get("selection") or item.get("name") or "").lower() for item in items)
    has_narrow_score = any(_score_is_narrow(item) for item in items)
    has_blowout = any(_score_is_blowout(item) for item in items)
    has_underdog_goal = any(_score_has_underdog_goal(item, match, distribution) for item in items)

    if adjustments.get("deep_handicap_risk_delta", 0) >= 1:
        if has_deep:
            score -= 18
            missing.append("出线压力提示深盘风险，但组合仍含深盘。")
        if has_shallow or has_narrow_score:
            score += 12
            matched.append("组合使用浅盘/窄比分响应深盘风险。")
    if adjustments.get("underdog_goal_weight_delta", 0) >= 1:
        if has_underdog_goal:
            score += 10
            matched.append("组合覆盖弱队进球尾部。")
        else:
            score -= 10
            missing.append("弱队抢分动机提升，但组合缺少弱队进球尾部。")
    if adjustments.get("draw_weight_delta", 0) >= 2:
        if has_drawish or has_under or has_narrow_score:
            score += 12
            matched.append("组合响应平局/小比分压力。")
        if has_blowout or has_over:
            score -= 12
            missing.append("双方可接受平局时，组合仍偏大胜/大球。")
    if adjustments.get("under_weight_delta", 0) >= 1:
        if has_under or has_narrow_score:
            score += 8
            matched.append("组合响应小球/控节奏倾向。")
        if has_over and not has_under:
            score -= 8
            missing.append("控节奏倾向下组合仍偏大球。")
    if adjustments.get("late_goal_volatility_delta", 0) >= 2 or adjustments.get("chaos_risk_delta", 0) >= 2:
        if has_over or has_underdog_goal:
            score += 8
            matched.append("组合覆盖后段开放或混乱路径。")
        elif has_under and not has_underdog_goal:
            score -= 8
            missing.append("后段开放风险升高，但组合缺少混乱路径覆盖。")
    if adjustments.get("favorite_small_win_weight_delta", 0) >= 1:
        if has_shallow or has_narrow_score:
            score += 8
            matched.append("组合覆盖热门小胜路径。")
        if has_blowout:
            score -= 8
            missing.append("小胜路径升权时，组合仍偏大比分。")

    score = clamp(score)
    label = "High" if score >= 78 else "Medium" if score >= 58 else "Low"
    return {
        "score": score,
        "label": label,
        "reason": "；".join(matched[:2] or missing[:2] or ["组合与当前出线压力大致匹配。"]),
        "matched": matched,
        "missing": missing,
        "match_pressure_type": behavior.get("match_pressure_type"),
    }


def _weighted_stats(rows, stake):
    total_weight = sum(float(row.get("scenario_weight") or row.get("final_scenario_weight") or 0) for row in rows) or 1
    ev = sum(float(row.get("profit") or 0) * float(row.get("scenario_weight") or row.get("final_scenario_weight") or 0) for row in rows) / total_weight
    roi = ev / stake if stake else 0
    max_loss = abs(min(0, min((float(row.get("profit") or 0) for row in rows), default=0)))
    zero_risk = sum(
        float(row.get("scenario_weight") or row.get("final_scenario_weight") or 0)
        for row in rows
        if float(row.get("profit") or 0) <= 0
    ) / total_weight
    coverage = {}
    for bucket in ["main", "adjacent", "tail", "noise"]:
        bucket_rows = [row for row in rows if row.get("scenario_type") == bucket]
        bucket_weight = sum(float(row.get("scenario_weight") or row.get("final_scenario_weight") or 0) for row in bucket_rows)
        if bucket_weight:
            coverage[bucket] = sum(
                float(row.get("scenario_weight") or row.get("final_scenario_weight") or 0)
                for row in bucket_rows
                if float(row.get("profit") or 0) > 0
            ) / bucket_weight
        else:
            coverage[bucket] = 0
    one_goal_risk = sum(
        float(row.get("scenario_weight") or row.get("final_scenario_weight") or 0)
        for row in rows
        if row.get("scenario_type") == "adjacent" and float(row.get("profit") or 0) <= 0
    ) / total_weight
    return {
        "ev": ev,
        "roi": roi,
        "max_loss": max_loss,
        "zero_risk": zero_risk,
        "coverage": coverage,
        "one_goal_deviation_risk": one_goal_risk,
    }


def compute_coverage_efficiency(items, metrics, expected_yield=0):
    if isinstance(metrics, dict) and metrics.get("type") and isinstance(expected_yield, list):
        base_items = list(items or [])
        candidate = metrics
        grid = expected_yield or []
        candidate_stake = float(candidate.get("amount") or 0)
        base_rows = compute_portfolio_pnl_by_score({"items": base_items}, grid)
        with_rows = compute_portfolio_pnl_by_score({"items": base_items + [candidate]}, grid)
        base_stake = sum(float(item.get("amount") or 0) for item in base_items)
        new_stake = base_stake + candidate_stake
        base_stats = _weighted_stats(base_rows, base_stake)
        new_stats = _weighted_stats(with_rows, new_stake)
        base_coverage = base_stats["coverage"]
        new_coverage = new_stats["coverage"]
        gain = max(0, sum(new_coverage.values()) - sum(base_coverage.values())) / 4
        zero_reduction = max(0, base_stats["zero_risk"] - new_stats["zero_risk"])
        one_goal_reduction = max(0, base_stats["one_goal_deviation_risk"] - new_stats["one_goal_deviation_risk"])
        alignment, plausibility = scenario_alignment_for_bet(candidate, {}, {"main_path": ""})
        if candidate.get("type") == "correct_score":
            candidate_score = normalize_score(candidate.get("selection"))
            grid_match = next((row for row in grid if normalize_score(row.get("score")) == candidate_score), None)
            if grid_match:
                plausibility = float(grid_match.get("plausibility_score") or plausibility)
                if grid_match.get("is_noise_scenario"):
                    alignment = min(alignment, 0.10)
        noise_penalty = 30 if plausibility < 0.25 or alignment < 0.25 else 12 if plausibility < 0.45 else 0
        complexity_penalty = 5 if len(base_items) >= 5 else 0
        ev_delta = new_stats["ev"] - base_stats["ev"]
        roi_delta = new_stats["roi"] - base_stats["roi"]
        max_loss_delta = new_stats["max_loss"] - base_stats["max_loss"]
        main_gain = new_coverage.get("main", 0) - base_coverage.get("main", 0)
        adjacent_gain = new_coverage.get("adjacent", 0) - base_coverage.get("adjacent", 0)
        tail_gain = new_coverage.get("tail", 0) - base_coverage.get("tail", 0)
        score = clamp(
            max(0, main_gain) * 180
            + max(0, adjacent_gain) * 160
            + max(0, tail_gain) * 40
            + zero_reduction * 180
            + one_goal_reduction * 220
            + max(-20, min(20, ev_delta / max(1, candidate_stake) * 100))
            + max(-15, min(15, roi_delta * 120))
            - max(0, max_loss_delta / max(1, new_stake) * 35)
            - noise_penalty
            - complexity_penalty
        )
        replace_stats = None
        replace_delta = {}
        if candidate.get("type") == "handicap":
            replaced = False
            replace_items = []
            for item in base_items:
                if not replaced and item.get("type") == "handicap":
                    replacement = deepcopy(candidate)
                    if not replacement.get("amount"):
                        replacement["amount"] = item.get("amount")
                    replace_items.append(replacement)
                    replaced = True
                else:
                    replace_items.append(item)
            if replaced:
                replace_rows = compute_portfolio_pnl_by_score({"items": replace_items}, grid)
                replace_stats = _weighted_stats(replace_rows, sum(float(item.get("amount") or 0) for item in replace_items))
                replace_delta = {
                    "replace_ev_delta": replace_stats["ev"] - base_stats["ev"],
                    "replace_roi_delta": replace_stats["roi"] - base_stats["roi"],
                    "replace_max_loss_delta": replace_stats["max_loss"] - base_stats["max_loss"],
                    "replace_zero_risk_delta": replace_stats["zero_risk"] - base_stats["zero_risk"],
                    "replace_one_goal_risk_reduction": max(0, base_stats["one_goal_deviation_risk"] - replace_stats["one_goal_deviation_risk"]),
                }
                replace_score = clamp(
                    max(-20, min(25, replace_delta["replace_ev_delta"] / max(1, candidate_stake or 100) * 100))
                    + max(-15, min(20, replace_delta["replace_roi_delta"] * 160))
                    + max(0, -replace_delta["replace_max_loss_delta"] / max(1, candidate_stake or 100) * 45)
                    + replace_delta["replace_one_goal_risk_reduction"] * 260
                    - noise_penalty
                )
                if replace_score > score:
                    score = replace_score
        recommendation = "Add"
        if replace_stats and score >= 45 and (
            replace_delta.get("replace_ev_delta", 0) > 0
            or replace_delta.get("replace_max_loss_delta", 0) < 0
            or replace_delta.get("replace_one_goal_risk_reduction", 0) > 0
        ):
            recommendation = "Replace"
        elif score < 35:
            recommendation = "Do Not Add"
        elif score < 60:
            recommendation = "Add Small Stake"
        return {
            "score": score,
            "coverage_efficiency_score": score,
            "base_ev": base_stats["ev"],
            "new_ev": new_stats["ev"],
            "ev_delta": ev_delta,
            "base_roi": base_stats["roi"],
            "new_roi": new_stats["roi"],
            "roi_delta": roi_delta,
            "base_max_loss": base_stats["max_loss"],
            "new_max_loss": new_stats["max_loss"],
            "max_loss_delta": max_loss_delta,
            "base_zero_risk": base_stats["zero_risk"],
            "new_zero_risk": new_stats["zero_risk"],
            "zero_risk_delta": new_stats["zero_risk"] - base_stats["zero_risk"],
            "coverage_gain": gain,
            "main_coverage_gain": main_gain,
            "adjacent_coverage_gain": adjacent_gain,
            "tail_coverage_gain": tail_gain,
            "zero_risk_reduction": zero_reduction,
            "one_goal_deviation_risk_reduction": one_goal_reduction,
            "added_stake_cost": candidate_stake,
            "ev_change": ev_delta,
            "roi_change": roi_delta,
            "complexity_change": complexity_penalty,
            "complexity_penalty": complexity_penalty,
            "noise_penalty": noise_penalty,
            "noise_tail_penalty": noise_penalty,
            "recommendation": recommendation,
            **replace_delta,
            "notes": [
                f"EV变化 {ev_delta:+.1f}，ROI变化 {roi_delta * 100:+.1f}%。",
                f"主剧本覆盖 {main_gain * 100:+.1f}%，邻近覆盖 {adjacent_gain * 100:+.1f}%，尾部覆盖 {tail_gain * 100:+.1f}%。",
                f"归零风险变化 {(new_stats['zero_risk'] - base_stats['zero_risk']) * 100:+.1f}%，一球偏差风险下降 {one_goal_reduction * 100:.1f}%。",
            ],
        }

    item_count = len([item for item in items or [] if item.get("type") != "empty"])
    correct_count = len([item for item in items or [] if item.get("type") == "correct_score"])
    duplicate_penalty = max(0, correct_count - 4) * 12
    complexity_penalty = max(0, item_count - 5) * 6
    coverage_gain = (
        metrics.get("main_coverage", 0) * 0.35
        + metrics.get("adjacent_coverage", 0) * 0.30
        + metrics.get("tail_coverage", 0) * 0.10
        + (1 - metrics.get("zero_risk", 1)) * 0.15
        + (1 - metrics.get("one_goal_deviation_risk", 1)) * 0.10
    )
    ev_penalty = 0 if expected_yield >= 0 else min(20, abs(expected_yield) * 250)
    score = clamp(coverage_gain * 100 - complexity_penalty - duplicate_penalty - ev_penalty)
    notes = []
    if metrics.get("one_goal_deviation_risk", 0) >= 0.35:
        notes.append("一球偏差风险偏高，建议增加邻近路径或降低让球深度。")
    if correct_count > 4:
        notes.append("波胆超过4个，复杂度过高。")
    if metrics.get("main_coverage", 0) >= 0.65 and metrics.get("adjacent_coverage", 0) >= 0.45:
        notes.append("主剧本与邻近剧本覆盖较均衡。")
    if not notes:
        notes.append("覆盖成本与收益基本匹配。")
    return {"score": score, "notes": notes}


def compute_portfolio_score(strategy, match, distribution):
    items = dedupe_bets(strategy.get("items") or [])
    total_stake = sum(float(item.get("amount") or 0) for item in items)
    score_rows = strategy.get("score_rows") or []
    coverage = compute_coverage_metrics(items, score_rows, match, distribution, total_stake)
    expected_yield = float(strategy.get("expected_yield") or 0)
    volatility = float(strategy.get("volatility") or 0)
    max_loss = float(strategy.get("max_loss") or total_stake or 0)
    risk_adjusted = clamp(55 + expected_yield * 260 - (volatility / total_stake * 22 if total_stake else 20))
    pressure_fit = strategy_pressure_fit(items, match, distribution)
    base_consistency = clamp((strategy.get("consistency_score") or 0) * 65 + (strategy.get("direction_alignment") or 0) * 25 + (strategy.get("strategic_value") or 0) * 10)
    consistency = clamp(base_consistency * 0.85 + pressure_fit.get("score", 70) * 0.15)
    directional = compute_directional_odds_value(items, match, distribution)
    efficiency = compute_coverage_efficiency(items, coverage, expected_yield)
    coverage_quality = clamp(coverage.get("coverage_score", 0) * 0.90 + pressure_fit.get("score", 70) * 0.10)
    loss_ratio = max_loss / total_stake if total_stake else 1
    drawdown = clamp((1 - min(1, loss_ratio)) * 55 + coverage.get("zero_risk_score", 0) * 0.45)
    correct_count = len([item for item in items if item.get("type") == "correct_score"])
    item_count = len(items)
    simplicity = clamp(100 - max(0, item_count - 4) * 10 - max(0, correct_count - 4) * 25)
    final = clamp(
        risk_adjusted * 0.15
        + consistency * 0.20
        + coverage_quality * 0.20
        + efficiency.get("score", 0) * 0.15
        + directional.get("score", 0) * 0.10
        + drawdown * 0.10
        + simplicity * 0.10
    )
    return {
        "score": final,
        "items": items,
        "coverage": coverage,
        "coverage_efficiency": efficiency,
        "directional_odds_value": directional,
        "pressure_fit": pressure_fit,
        "score_components": {
            "Risk-Adjusted Value": risk_adjusted,
            "Scenario Consistency": consistency,
            "Coverage Quality": coverage_quality,
            "Coverage Efficiency": efficiency.get("score", 0),
            "Directional Odds Value": directional.get("score", 0),
            "Pressure Fit": pressure_fit.get("score", 70),
            "Drawdown / Zero Risk": drawdown,
            "Simplicity": simplicity,
        },
        "why": [
            f"主剧本覆盖 {coverage.get('main_coverage', 0) * 100:.0f}%，邻近剧本覆盖 {coverage.get('adjacent_coverage', 0) * 100:.0f}%。",
            f"一球偏差风险 {coverage.get('one_goal_deviation_risk', 0) * 100:.0f}%，归零风险 {coverage.get('zero_risk', 0) * 100:.0f}%。",
            f"主方向赔率价值 {directional.get('weighted_edge', 0) * 100:+.1f}%。",
            f"出线压力适配：{pressure_fit.get('label')}，{pressure_fit.get('reason')}",
        ],
    }


def portfolio_style_name(strategy, metrics=None):
    items = strategy.get("items") or []
    correct_count = len([item for item in items if item.get("type") == "correct_score"])
    has_handicap = any(item.get("type") == "handicap" for item in items)
    has_total = any(item.get("type") == "total" for item in items)
    zero_risk = ((metrics or {}).get("coverage") or {}).get("zero_risk", 0)
    if zero_risk < 0.25 and has_handicap:
        return "Conservative"
    if correct_count >= 3 and has_handicap:
        return "Main Scenario"
    if has_total and correct_count >= 2:
        return "Aggressive"
    if correct_count and not has_handicap:
        return "Tail Hedge"
    return "Main Scenario"


def generate_style_portfolios(combo, match, distribution):
    items = dedupe_bets([item for item in combo or [] if item.get("recommended") and item.get("type") != "empty"])
    winners = [item for item in items if item.get("type") == "winner"][:1]
    all_handicaps = [item for item in items if item.get("type") == "handicap"]
    shallow_handicaps = [item for item in all_handicaps if 0 < _handicap_depth(item) <= 1.25]
    deep_handicaps = [item for item in all_handicaps if _handicap_depth(item) >= 1.5]
    handicaps = (shallow_handicaps or all_handicaps)[:1]
    totals = [item for item in items if item.get("type") == "total"][:1]
    under_totals = [item for item in items if item.get("type") == "total" and _total_side(item) == "under"][:1]
    over_totals = [item for item in items if item.get("type") == "total" and _total_side(item) == "over"][:1]
    scores = [item for item in items if item.get("type") == "correct_score"][:4]
    underdog_goal_scores = [item for item in scores if _score_has_underdog_goal(item, match, distribution)]
    narrow_scores = [item for item in scores if _score_is_narrow(item)]
    blowout_scores = [item for item in scores if _score_is_blowout(item)]
    adjacent_scores = [
        item for item in scores
        if scenario_category(item.get("selection"), match, distribution) in {"main", "adjacent"}
    ][:4] or scores[:2]
    portfolios = [
        {"code": "style_conservative", "name": "Conservative Portfolio", "items": dedupe_bets(winners + handicaps + adjacent_scores[:2])},
        {"code": "style_main", "name": "Main Scenario Portfolio", "items": dedupe_bets(winners + handicaps + totals + adjacent_scores[:4])},
        {"code": "style_aggressive", "name": "Aggressive Portfolio", "items": dedupe_bets((deep_handicaps or handicaps)[:1] + totals + scores[:4])},
        {"code": "style_tail", "name": "Tail Hedge Portfolio", "items": dedupe_bets(winners + scores[:4])},
    ]
    portfolios.extend(generate_portfolio_templates_by_pressure({
        "winners": winners,
        "handicaps": all_handicaps,
        "shallow_handicaps": shallow_handicaps,
        "deep_handicaps": deep_handicaps,
        "totals": totals,
        "under_totals": under_totals,
        "over_totals": over_totals,
        "scores": scores,
        "adjacent_scores": adjacent_scores,
        "underdog_goal_scores": underdog_goal_scores,
        "narrow_scores": narrow_scores,
        "blowout_scores": blowout_scores,
    }, match, distribution))
    return portfolios


def generate_portfolio_templates_by_pressure(market_context, match, distribution):
    pressure_type = (((distribution or {}).get("game_behavior") or {}).get("match_pressure_type") or "neutral_group_context")
    winners = market_context.get("winners") or []
    shallow = market_context.get("shallow_handicaps") or []
    handicaps = market_context.get("handicaps") or []
    totals = market_context.get("totals") or []
    under = market_context.get("under_totals") or []
    over = market_context.get("over_totals") or []
    adjacent = market_context.get("adjacent_scores") or []
    narrow = market_context.get("narrow_scores") or []
    underdog_goal = market_context.get("underdog_goal_scores") or []
    blowout = market_context.get("blowout_scores") or []
    scores = market_context.get("scores") or []
    templates = []

    def add(code, name, selected, template):
        selected = dedupe_bets([item for item in selected if item])
        if selected:
            templates.append({
                "code": code,
                "name": name,
                "items": selected,
                "pressure_template": template,
            })

    if pressure_type == "qualified_favorite_vs_must_win_underdog":
        add(
            "pressure_qualified_favorite",
            "Pressure Template: Shallow Favorite + Underdog Tail",
            winners + (shallow or handicaps)[:1] + (underdog_goal[:2] or narrow[:2] or adjacent[:2]),
            "qualified favorite: lower handicap depth and add underdog-goal/small-win coverage",
        )
    elif pressure_type == "both_draw_acceptable":
        add(
            "pressure_draw_acceptable",
            "Pressure Template: Draw/Under/Narrow",
            (under or totals)[:1] + (narrow[:3] or adjacent[:2]),
            "both draw acceptable: lift draw/under/narrow-score coverage",
        )
    elif pressure_type == "direct_second_place_battle":
        add(
            "pressure_second_place",
            "Pressure Template: Narrow + Late Volatility",
            (under or totals)[:1] + (narrow[:2] or adjacent[:2]) + underdog_goal[:1],
            "direct second-place battle: avoid one-sided blowout and cover narrow paths",
        )
    elif pressure_type == "must_win_vs_must_win":
        add(
            "pressure_both_must_win",
            "Pressure Template: Both-Teams-Need-Goal",
            (over or totals)[:1] + (underdog_goal[:2] or adjacent[:2]) + narrow[:2],
            "must-win vs must-win: raise late volatility and scoring-tail coverage",
        )
    elif pressure_type == "favorite_must_win":
        add(
            "pressure_favorite_must_win",
            "Pressure Template: Favorite Direction + Goal Tail",
            winners + (shallow or handicaps)[:1] + (underdog_goal[:2] or adjacent[:2]),
            "favorite must win: keep direction but avoid clean-sheet-only exposure",
        )
    elif pressure_type == "qualified_vs_qualified":
        add(
            "pressure_qualified_both",
            "Pressure Template: Conservative Qualified Teams",
            (under or totals)[:1] + (narrow[:3] or adjacent[:2]),
            "qualified vs qualified: avoid aggressive deep handicap and big over",
        )
    if not templates and pressure_type != "neutral_group_context":
        add(
            "pressure_generic",
            "Pressure Template: Qualification-Aware Balanced",
            winners + (shallow or handicaps)[:1] + (narrow[:2] or adjacent[:2]),
            f"{pressure_type}: balanced pressure-aware template",
        )
    return templates


def _polymarket_quality(polymarket):
    if not polymarket:
        return 0, "Polymarket 未提供数据。"
    if not polymarket.get("found"):
        return 20, polymarket.get("message") or "Polymarket 未找到对应市场。"
    keys = ["home_win", "draw", "away_win"]
    complete = [key for key in keys if polymarket.get(key) is not None]
    if len(complete) == 3:
        return 100, "Polymarket 主胜/平/客胜价格完整。"
    if complete:
        return 55, "Polymarket 只返回部分价格，数据质量降权。"
    return 35, "Polymarket 找到事件但缺少完整主胜/平/客胜价格，数据质量降权。"


def _api_quality(odds=None, api_football_data=None):
    checks = []
    odds = odds or {}
    api_football_data = api_football_data or {}
    checks.append(("胜平负", bool(odds.get("home_win") and odds.get("draw") and odds.get("away_win"))))
    checks.append(("大小球", bool(odds.get("over_under"))))
    checks.append(("亚洲盘", bool(((api_football_data.get("asian_handicap") or {}).get("rows")))))
    checks.append(("波胆", bool(((api_football_data.get("correct_score") or {}).get("rows")))))
    passed = [label for label, ok in checks if ok]
    missing = [label for label, ok in checks if not ok]
    score = round(len(passed) / len(checks) * 100) if checks else 0
    if missing:
        return score, f"API赔率缺少：{'、'.join(missing)}。"
    return score, "API赔率完整：胜平负、大小球、亚洲盘、波胆均可用。"


def _user_odds_quality(strategy):
    items = [item for item in (strategy or {}).get("items") or [] if item.get("type") != "empty"]
    if not items:
        return 0, "没有可评估投注项。"
    entered = [item for item in items if item.get("actual_odds")]
    if len(entered) == len(items):
        return 100, "用户真实赔率已覆盖当前组合。"
    if entered:
        return 70, f"用户真实赔率覆盖 {len(entered)} / {len(items)}，最终排序可信度中等。"
    return 40, "用户未输入真实赔率，最终排序可信度较低。"


def _data_quality_score(strategy, context=None):
    context = context or {}
    poly_score, poly_note = _polymarket_quality(context.get("polymarket"))
    api_score, api_note = _api_quality(context.get("odds"), context.get("api_football_data"))
    user_score, user_note = _user_odds_quality(strategy)
    timing_note = "数据时点未提供，按中性处理。"
    timing_score = 70
    score = clamp(poly_score * 0.25 + api_score * 0.35 + user_score * 0.30 + timing_score * 0.10)
    return {
        "score": score,
        "polymarket_score": poly_score,
        "api_score": api_score,
        "user_odds_score": user_score,
        "timing_score": timing_score,
        "note": " ".join([poly_note, api_note, user_note, timing_note]),
    }


def compute_match_investment_score(strategies, match=None, distribution=None, context=None):
    if not strategies:
        return {
            "score": 0,
            "rating": "不建议下注",
            "main_reason": "没有足够真实盘口形成组合。",
            "key_risk": "数据不足。",
            "data_quality_note": "没有组合，无法评估数据质量。",
            "components": {},
        }
    best = strategies[0]
    components = best.get("portfolio_score_components") or best.get("score_components") or {}
    coverage = best.get("coverage_metrics") or {}
    scenario_clarity = components.get("Scenario Consistency", 55)
    direction_alignment = best.get("direction_alignment")
    if direction_alignment is None:
        direction_alignment = scenario_clarity / 100
    market_clarity = clamp(direction_alignment * 100)
    directional_value = components.get("Directional Odds Value", 45)
    coverage_quality = components.get("Coverage Quality", coverage.get("coverage_score", 50))
    behavior = ((distribution or {}).get("game_behavior") or {})
    behavior_adjustments = behavior.get("behavior_adjustments") or {}
    pressure_risk_penalty = max(0, behavior_adjustments.get("deep_handicap_risk_delta", 0)) * 5
    pressure_risk_penalty += max(0, behavior_adjustments.get("chaos_risk_delta", 0)) * 4
    pressure_risk_penalty += max(0, behavior_adjustments.get("late_goal_volatility_delta", 0)) * 3
    external_risk = clamp(100 - coverage.get("one_goal_deviation_risk", 0.35) * 100 - pressure_risk_penalty)
    data_quality_info = _data_quality_score(best, context)
    data_quality = data_quality_info["score"]
    score = clamp(
        market_clarity * 0.20
        + scenario_clarity * 0.25
        + directional_value * 0.20
        + coverage_quality * 0.20
        + external_risk * 0.10
        + data_quality * 0.05
    )
    if score >= 80:
        rating = "值得重点研究"
    elif score >= 65:
        rating = "可小仓参与"
    elif score >= 50:
        rating = "谨慎观察"
    else:
        rating = "不建议下注"
    main_reason = f"主方向清晰度 {market_clarity}，覆盖质量 {coverage_quality}。"
    key_risk = "一球偏差可能造成组合回撤。" if coverage.get("one_goal_deviation_risk", 0) >= 0.30 else "主要风险在赔率波动和临场信息。"
    if behavior.get("match_pressure_type"):
        key_risk += f" 出线压力类型：{behavior.get('match_pressure_type')}。"
    qualification_source = behavior.get("qualification_source") or "not provided"
    return {
        "score": score,
        "rating": rating,
        "main_reason": main_reason,
        "key_risk": key_risk,
        "data_quality_note": data_quality_info["note"] + f" Qualification context: {qualification_source}.",
        "components": {
            "Market Clarity": market_clarity,
            "Scenario Clarity": scenario_clarity,
            "Directional Odds Value": directional_value,
            "Coverage Quality": coverage_quality,
            "External Risk": external_risk,
            "Data Quality / Timing": data_quality,
        },
        "weights": {
            "Market Clarity": "20%",
            "Scenario Clarity": "25%",
            "Directional Odds Value": "20%",
            "Coverage Quality": "20%",
            "External Risk": "10%",
            "Data Quality / Timing": "5%",
        },
    }
