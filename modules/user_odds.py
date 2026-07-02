import csv
import re
from io import StringIO

from modules.market_utils import asian_handicap_summary, correct_score_summary, totals_summary
from modules.portfolio_engine import handicap_line_from_text, normalize_handicap_line
from modules.team_resolver import canonical_name


AI_OPTIMIZATION_INTERFACE = {
    "enabled": False,
    "description": "预留接口：未来可用历史赛果自动调整方向、盘口、波胆和EV权重。",
    "weights": {
        "path_match": 1.0,
        "ev": 1.0,
        "market_value": 1.0,
        "coverage": 1.0,
    },
}


def parse_float(value):
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return number if number > 1 else None


def normalize(value):
    return " ".join(str(value or "").strip().lower().replace("-", " ").split())


def normalize_team(value):
    return normalize(canonical_name(str(value or "").strip()))


def normalize_score(value):
    text = str(value or "").strip()
    text = text.replace("：", ":").replace(" - ", ":").replace("-", ":")
    text = re.sub(r"\s+", "", text)
    match = re.search(r"(\d+):(\d+)", text)
    if not match:
        return text
    return f"{int(match.group(1))}:{int(match.group(2))}"


def standardize_selection(item_type, selection):
    text = str(selection or "").strip()
    if item_type == "winner":
        return canonical_name(text)
    if item_type == "correct_score":
        return normalize_score(text)
    if item_type == "total":
        side, line = total_side_and_line(text)
        if side and line is not None:
            return f"{side.title()} {line:g}"
    if item_type == "handicap":
        line = handicap_line_from_text(text)
        if line.get("decimal_line") is not None:
            return re.sub(r"([+-]?\d+(?:\.\d+)?(?:/[+-]?\d+(?:\.\d+)?)?)", line.get("display_line"), text, count=1)
        return re.sub(r"\s+", " ", text)
    return text


def market_key(label):
    text = normalize(label)
    if "match winner" in text or "winner" in text or "胜平负" in text or "独赢" in text:
        return "winner"
    if "asian" in text or "handicap" in text or "让球" in text:
        return "handicap"
    if "over under" in text or "over/under" in text or "total" in text or "大小球" in text:
        return "total"
    if "correct score" in text or "exact score" in text or "波胆" in text:
        return "correct_score"
    return None


def parse_actual_odds(raw_text):
    text = str(raw_text or "").strip()
    if not text:
        return {"items": [], "by_type": {}, "raw": ""}

    items = parse_csv_odds(text)
    if not items:
        items = parse_block_odds(text)

    by_type = {}
    for item in items:
        key = item["type"]
        if key == "correct_score":
            by_type.setdefault(key, {})[normalize_score(item["selection"])] = item
        else:
            by_type[key] = item
        by_type.setdefault(f"{key}_items", []).append(item)
    return {"items": items, "by_type": by_type, "raw": text}


def parse_csv_odds(text):
    if "," not in text:
        return []
    rows = []
    try:
        reader = csv.reader(StringIO(text))
        for raw in reader:
            parts = [part.strip() for part in raw if part.strip()]
            if len(parts) < 3:
                continue
            key = market_key(parts[0])
            odds = parse_float(parts[-1])
            if key and odds:
                selection = parts[1]
                if key == "handicap" and len(parts) >= 4:
                    selection = f"{parts[1]} {parts[2]}"
                rows.append({"type": key, "selection": standardize_selection(key, selection), "odds": odds})
    except csv.Error:
        return []
    return rows


def parse_block_odds(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    rows = []
    index = 0
    while index + 2 < len(lines):
        key = market_key(lines[index])
        odds = parse_float(lines[index + 2])
        if key and odds:
            rows.append({"type": key, "selection": standardize_selection(key, lines[index + 1]), "odds": odds})
            index += 3
        else:
            index += 1
    return rows


def number_in_text(value):
    match = re.search(r"([+-]?\d+(?:\.\d+)?)", str(value or ""))
    return float(match.group(1)) if match else None


def handicap_decimal_in_text(value):
    line = handicap_line_from_text(value)
    return line.get("decimal_line")


def total_side_and_line(value):
    text = normalize(value)
    side = None
    if "under" in text or "小于" in text:
        side = "under"
    if "over" in text or "大于" in text:
        side = "over"
    return side, number_in_text(value)


def selection_matches(candidate, item):
    item_type = candidate.get("type")
    candidate_selection = candidate.get("selection")
    actual_selection = item.get("selection")
    if item_type == "winner":
        left = normalize_team(candidate_selection)
        right = normalize_team(actual_selection)
        return left in right or right in left
    if item_type == "total":
        candidate_side, candidate_line = total_side_and_line(candidate_selection)
        actual_side, actual_line = total_side_and_line(actual_selection)
        return candidate_side == actual_side and candidate_line == actual_line
    if item_type == "handicap":
        candidate_line = handicap_decimal_in_text(candidate_selection)
        actual_line = handicap_decimal_in_text(actual_selection)
        if candidate_line is None or actual_line is None:
            return False
        return abs(candidate_line - actual_line) < 0.001
    if item_type == "correct_score":
        return normalize_score(candidate_selection) == normalize_score(actual_selection)
    return normalize(candidate_selection) == normalize(actual_selection)


def actual_for_candidate(candidate, actual_odds):
    by_type = (actual_odds or {}).get("by_type") or {}
    item_type = candidate.get("type")
    if item_type == "correct_score":
        return (by_type.get("correct_score") or {}).get(normalize_score(candidate.get("selection")))
    candidates = by_type.get(f"{item_type}_items") or []
    for item in candidates:
        if selection_matches(candidate, item):
            return item
    return None


def odds_edge(actual_odds, standard_odds):
    actual = parse_float(actual_odds)
    standard = parse_float(standard_odds)
    if not actual or not standard:
        return None
    return actual / standard - 1


def candidate_with_actual(candidate, actual_odds):
    actual = actual_for_candidate(candidate, actual_odds)
    actual_price = actual.get("odds") if actual else None
    edge = odds_edge(actual_price, candidate.get("standard_odds"))
    return {
        **candidate,
        "actual_odds": actual_price,
        "effective_odds": actual_price or candidate.get("standard_odds"),
        "edge": edge,
        "actual_selection": actual.get("selection") if actual else None,
    }


def market_probability(candidate):
    probability = candidate.get("probability")
    if probability is not None:
        return probability
    standard = parse_float(candidate.get("standard_odds"))
    return 1 / standard if standard else None


def expected_value(probability, odds_value):
    price = parse_float(odds_value)
    if probability is None or not price:
        return None
    return probability * price - 1


def market_value_factor(candidate):
    item_type = candidate.get("type")
    if item_type == "handicap":
        return 1.35
    if item_type == "winner":
        return 1.00
    if item_type == "total":
        return 0.55
    if item_type == "correct_score":
        return 0.85
    return 0.70


def build_market_candidates(match, odds, api_football_data):
    candidates = []
    from modules.probability_base import true_probability_base

    implied = (true_probability_base(odds).get("probabilities") or {})
    if odds.get("found") and implied:
        options = [
            ("home_win", match["home_cn"], odds.get("home_win"), implied.get("home_win", 0)),
            ("draw", "平局", odds.get("draw"), implied.get("draw", 0)),
            ("away_win", match["away_cn"], odds.get("away_win"), implied.get("away_win", 0)),
        ]
        key, label, price, probability = max(options, key=lambda item: item[3])
        if price:
            candidates.append({
                "slot": "独赢",
                "type": "winner",
                "selection": label,
                "name": f"{label}独赢",
                "standard_odds": price,
                "probability": probability,
                "base_score": 58 + probability * 20,
                "source": "市场胜平负赔率",
            })

    handicap = asian_handicap_summary(((api_football_data or {}).get("asian_handicap") or {}).get("rows") or [])
    if handicap.get("available") and handicap.get("avg_odds"):
        candidates.append({
            "slot": "让球",
            "type": "handicap",
            "selection": handicap.get("main_value"),
            "name": handicap.get("main_value"),
            "standard_odds": handicap.get("avg_odds"),
            "base_score": 74,
            "source": "API-Football 亚洲盘均值",
        })

    totals = totals_summary(odds.get("over_under") or [])
    if totals.get("available"):
        avg_over = totals.get("avg_over")
        avg_under = totals.get("avg_under")
        if avg_over and avg_under:
            for side, price, label_cn in [
                ("Under", avg_under, "小于"),
                ("Over", avg_over, "大于"),
            ]:
                market_favored = price <= (avg_over if side == "Under" else avg_under)
                candidates.append({
                    "slot": "大小球",
                    "type": "total",
                    "selection": f"{side} {totals.get('line')}",
                    "name": f"{label_cn} {totals.get('line')} 球",
                    "standard_odds": price,
                    "base_score": 50 if market_favored and abs(avg_over - avg_under) > 0.08 else 40,
                    "source": "The Odds API 大小球均值",
                })

    correct = correct_score_summary(((api_football_data or {}).get("correct_score") or {}).get("rows") or [], limit=200)
    correct_scores = []
    for score in correct.get("all") or correct.get("hot") or []:
        parsed_score = parse_score(score.get("score"))
        if not parsed_score:
            continue
        home_goals, away_goals = parsed_score
        if home_goals > 5 or away_goals > 5:
            continue
        correct_scores.append(score)

    for idx, score in enumerate(correct_scores, start=1):
        if idx <= 3:
            market_center_score = 20
            market_center_label = "核心波胆"
        elif idx <= 5:
            market_center_score = 12
            market_center_label = "市场中心附近"
        elif idx <= 10:
            market_center_score = 4
            market_center_label = "次级路径"
        else:
            market_center_score = -12
            market_center_label = "边缘路径"
        candidates.append({
            "slot": f"波胆{idx}",
            "type": "correct_score",
            "selection": score.get("score"),
            "name": f"波胆 {score.get('score')}",
            "standard_odds": score.get("avg_odds"),
            "base_score": max(30, 56 - idx),
            "market_center_rank": idx,
            "market_center_score": market_center_score,
            "market_center_label": market_center_label,
            "source": "API-Football 波胆均值",
        })

    return candidates


def score_candidate(candidate):
    edge = candidate.get("edge")
    ev_lift = candidate.get("ev_lift")
    factor = candidate.get("market_value_factor", 1)
    path_match = candidate.get("path_match_score", 0)
    market_center_score = candidate.get("market_center_score", 0)
    consistency_score = candidate.get("path_consistency_score", 0)
    conflict_penalty = candidate.get("path_conflict_penalty", 0)
    coverage = candidate.get("coverage_rate", 0)
    direction_alignment = candidate.get("direction_alignment_score", 0)
    edge_points = 0
    if edge is not None:
        weighted_edge = edge * factor
        if weighted_edge >= 0.08:
            edge_points = 30
        elif weighted_edge >= 0.05:
            edge_points = 22
        elif weighted_edge >= 0.02:
            edge_points = 12
        elif weighted_edge >= -0.02:
            edge_points = 0
        elif weighted_edge >= -0.05:
            edge_points = -18
        else:
            edge_points = -35
    ev_points = 0
    if ev_lift is not None:
        if ev_lift >= 0.04:
            ev_points = 18
        elif ev_lift >= 0.02:
            ev_points = 10
        elif ev_lift >= 0:
            ev_points = 3
        elif ev_lift >= -0.02:
            ev_points = -8
        else:
            ev_points = -18
    if edge is None and ev_lift is None:
        edge_points = -6
    coverage_points = min(12, round(coverage * 18))
    if candidate.get("type") == "correct_score" and candidate.get("market_center_rank", 99) > 5:
        if not ((edge or 0) >= 0.08 or (ev_lift or 0) >= 0.05):
            market_center_score = min(market_center_score, -12)
    return round(
        candidate.get("base_score", 0)
        + edge_points
        + ev_points
        + path_match
        + market_center_score
        + consistency_score
        - conflict_penalty
        + coverage_points
        + direction_alignment
    )


def parse_score(score):
    try:
        home_goals, away_goals = [int(part) for part in str(score or "").split(":", 1)]
    except (TypeError, ValueError):
        return None
    return home_goals, away_goals


def distribution_probability(distribution, predicate):
    total = 0
    for row in (distribution or {}).get("rows") or []:
        label = str(row.get("label") or "")
        if predicate(label):
            total += row.get("probability", 0)
    return total


def favorite_is_home(match, distribution):
    favorite = str((distribution or {}).get("favorite") or "")
    if not favorite:
        return True
    home_names = {
        str(match.get("home_cn") or ""),
        str(match.get("home") or ""),
        canonical_name(str(match.get("home_cn") or "")),
    }
    try:
        from modules.pregame_content import team_cn
        home_names.add(team_cn(match.get("home_cn") or ""))
    except Exception:
        pass
    return favorite in home_names


def selection_line(selection):
    match = re.search(r"([+-]?\d+(?:\.\d+)?)", str(selection or ""))
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def total_side_line(selection):
    text = str(selection or "").lower()
    line_match = re.search(r"(\d+(?:\.\d+)?)", text)
    line = float(line_match.group(1)) if line_match else None
    if "under" in text or "小" in text:
        return "under", line
    if "over" in text or "大" in text:
        return "over", line
    return None, line


def primary_path_profile(candidates, match, distribution):
    handicap = max(
        [item for item in candidates if item.get("type") == "handicap"],
        key=lambda item: item.get("score", item.get("base_score", 0)),
        default=None,
    )
    total = max(
        [item for item in candidates if item.get("type") == "total"],
        key=lambda item: item.get("score", item.get("base_score", 0)),
        default=None,
    )
    total_side, total_line = total_side_line((total or {}).get("selection"))
    return {
        "favorite_home": favorite_is_home(match, distribution),
        "favorite": (distribution or {}).get("favorite"),
        "handicap_selection": (handicap or {}).get("selection"),
        "handicap_line": selection_line((handicap or {}).get("selection")),
        "total_selection": (total or {}).get("selection"),
        "total_side": total_side,
        "total_line": total_line,
    }


def required_favorite_margin(handicap_line):
    if handicap_line is None:
        return None
    line = float(handicap_line)
    if line >= 0:
        return 0
    abs_line = abs(line)
    if abs_line <= 0.5:
        return 1
    if abs_line <= 1:
        return 1
    if abs_line <= 1.5:
        return 2
    if abs_line <= 2:
        return 2
    if abs_line <= 2.5:
        return 3
    return int(abs_line) + 1


def correct_score_path_consistency(candidate, profile):
    if candidate.get("type") != "correct_score":
        return 0, 0, ""
    parsed = parse_score(candidate.get("selection"))
    if not parsed:
        return 0, 30, "比分格式无法识别。"

    home_goals, away_goals = parsed
    total_goals = home_goals + away_goals
    fav_diff = home_goals - away_goals if profile.get("favorite_home") else away_goals - home_goals
    required_margin = required_favorite_margin(profile.get("handicap_line"))
    total_side = profile.get("total_side")
    total_line = profile.get("total_line")

    score = 0
    penalty = 0
    reasons = []

    if fav_diff > 0:
        score += 10
        reasons.append("方向一致")
    else:
        penalty += 45
        reasons.append("与主胜方向冲突")

    if required_margin is not None:
        if fav_diff >= required_margin:
            score += 14
            reasons.append(f"符合让球主线{profile.get('handicap_selection')}")
        else:
            penalty += 35
            reasons.append(f"未覆盖让球主线{profile.get('handicap_selection')}")

    if total_side and total_line is not None:
        if total_side == "over":
            if total_goals > total_line:
                score += 12
                reasons.append(f"符合{profile.get('total_selection')}")
            else:
                if candidate.get("market_center_rank", 99) <= 3 and (required_margin is None or fav_diff >= required_margin):
                    penalty += 18
                    reasons.append(f"低于{profile.get('total_selection')}，但属于市场中心且打穿让球")
                else:
                    penalty += 38
                    reasons.append(f"与{profile.get('total_selection')}冲突")
        elif total_side == "under":
            if total_goals < total_line:
                score += 12
                reasons.append(f"符合{profile.get('total_selection')}")
            else:
                if candidate.get("market_center_rank", 99) <= 3 and fav_diff > 0:
                    penalty += 18
                    reasons.append(f"高于{profile.get('total_selection')}，但属于市场中心且方向一致")
                else:
                    penalty += 38
                    reasons.append(f"与{profile.get('total_selection')}冲突")

    if candidate.get("market_center_rank", 99) <= 5 and penalty <= 20:
        score += 8
        reasons.append("位于波胆市场中心")
    elif candidate.get("market_center_rank", 99) > 10:
        penalty += 10
        reasons.append("偏离波胆市场中心")

    return score, penalty, "；".join(reasons)


def apply_path_consistency(candidates, match, distribution):
    profile = primary_path_profile(candidates, match, distribution)
    for item in candidates:
        if item.get("type") != "correct_score":
            continue
        consistency, penalty, reason = correct_score_path_consistency(item, profile)
        item["path_consistency_score"] = consistency
        item["path_conflict_penalty"] = penalty
        item["path_consistency_reason"] = reason
        item["score"] = score_candidate(item)
        if penalty >= 35:
            item["recommended"] = False
            item["not_recommended_reason"] = f"路径冲突：{reason}"
            item["reason"] = f"未进入主路径：{reason}"
        else:
            item["recommended"] = item["score"] >= 55
            if item["recommended"]:
                item.pop("not_recommended_reason", None)
            else:
                item["not_recommended_reason"] = not_recommended_reason(item)
    return profile


def path_match_score(candidate, match, distribution):
    if candidate.get("type") != "correct_score":
        return 0, ""
    parsed = parse_score(candidate.get("selection"))
    if not parsed:
        return 0, "波胆比分格式无法识别。"
    home_goals, away_goals = parsed
    diff = home_goals - away_goals
    fav_home = favorite_is_home(match, distribution)
    fav_diff = diff if fav_home else -diff

    main_path = str((distribution or {}).get("main_path") or "")
    if fav_diff == 1 and ("小胜" in main_path or "1球" in main_path):
        return 12, "匹配主胜1球路径。"
    if fav_diff == 2 and "赢2球" in main_path:
        return 15, "匹配赢2球主路径。"
    if fav_diff >= 3 and "3球以上" in main_path:
        return 15, "匹配大胜主路径。"
    if fav_diff == 1:
        return 8, "覆盖热门方小胜路径。"
    if fav_diff == 2:
        return 10, "覆盖盘口边界路径。"
    if fav_diff >= 3:
        return 8, "覆盖极端大胜路径。"
    if fav_diff == 0:
        return 6, "覆盖平局冷门路径。"
    return 2, "覆盖弱势方爆冷路径，命中要求较高。"


def direction_alignment_score(candidate, match, distribution):
    item_type = candidate.get("type")
    favorite = str((distribution or {}).get("favorite") or "")
    selection = str(candidate.get("selection") or candidate.get("name") or "")
    if item_type == "winner":
        return 20 if favorite and favorite in selection else 8
    if item_type == "handicap":
        return 22
    if item_type == "correct_score":
        center_bonus = 4 if candidate.get("market_center_rank", 99) <= 5 else -4
        return max(0, (12 if candidate.get("path_match_score", 0) >= 10 else 4) + center_bonus)
    if item_type == "total":
        ev_lift = candidate.get("ev_lift") or 0
        return 0 if ev_lift >= 0.05 else -12
    return 0


def coverage_rate(candidate, distribution):
    item_type = candidate.get("type")
    if item_type == "winner":
        return distribution_probability(
            distribution,
            lambda label: ("小胜" in label or "赢2球" in label or "3球以上" in label),
        )
    if item_type == "handicap":
        selection = str(candidate.get("selection") or "")
        if "-1.5" in selection or "-1.25" in selection:
            return distribution_probability(distribution, lambda label: "赢2球" in label or "3球以上" in label)
        if "-1" in selection or "-0.75" in selection:
            return distribution_probability(distribution, lambda label: "小胜" in label or "赢2球" in label or "3球以上" in label)
        return distribution_probability(distribution, lambda label: "小胜" in label or "赢2球" in label or "3球以上" in label)
    if item_type == "total":
        selection = str(candidate.get("selection") or "").lower()
        if "under" in selection or "小于" in selection:
            return distribution_probability(distribution, lambda label: "平局" in label or "小胜" in label)
        return distribution_probability(distribution, lambda label: "赢2球" in label or "3球以上" in label)
    if item_type == "correct_score":
        standard = parse_float(candidate.get("standard_odds"))
        if not standard:
            return 0
        return min(0.25, (1 / standard) * 1.2)
    return 0


def enrich_candidate(candidate, actual_odds, match=None, distribution=None):
    enriched = candidate_with_actual(candidate, actual_odds)
    probability = market_probability(enriched)
    factor = market_value_factor(enriched)
    standard_ev = expected_value(probability, enriched.get("standard_odds"))
    actual_ev = expected_value(probability, enriched.get("effective_odds"))
    ev_lift = None
    if actual_ev is not None and standard_ev is not None:
        ev_lift = actual_ev - standard_ev
    path_points, path_reason = path_match_score(enriched, match or {}, distribution or {})
    coverage = coverage_rate(enriched, distribution or {})
    enriched.update({
        "probability": probability,
        "market_value_factor": factor,
        "standard_ev": standard_ev,
        "actual_ev": actual_ev,
        "ev_lift": ev_lift,
        "path_match_score": path_points,
        "path_match_reason": path_reason,
        "coverage_rate": coverage,
        "market_center_reason": market_center_reason(enriched),
    })
    enriched["direction_alignment_score"] = direction_alignment_score(enriched, match or {}, distribution or {})
    enriched["score"] = score_candidate(enriched)
    enriched["reason"] = odds_edge_reason(enriched)
    enriched["recommended"] = enriched["score"] >= 55
    if not enriched["recommended"]:
        enriched["not_recommended_reason"] = not_recommended_reason(enriched)
    return enriched


def force_min_correct_scores(candidates, minimum=2):
    correct_scores = [
        item for item in candidates
        if item.get("type") == "correct_score" and item.get("path_conflict_penalty", 0) < 35
    ]
    if not correct_scores:
        return
    recommended_count = sum(1 for item in correct_scores if item.get("recommended"))
    if recommended_count >= min(minimum, len(correct_scores)):
        return
    sorted_scores = sorted(
        correct_scores,
        key=lambda item: (
            item.get("recommended", False),
            item.get("market_center_score", 0),
            -item.get("market_center_rank", 999),
            item.get("path_consistency_score", 0),
            -item.get("path_conflict_penalty", 0),
            item.get("path_match_score", 0),
            item.get("score", 0),
        ),
        reverse=True,
    )
    for item in sorted_scores:
        if recommended_count >= min(minimum, len(correct_scores)):
            break
        if item.get("recommended"):
            continue
        item["recommended"] = True
        item["forced_recommendation"] = True
        item["score"] = max(item.get("score", 0), 55 if recommended_count == 0 else 45)
        item.pop("not_recommended_reason", None)
        item["reason"] = f"低金额保留波胆候选；{item.get('market_center_reason') or item.get('path_match_reason') or '用于覆盖最可能比分路径。'}"
        recommended_count += 1


def allocation_cap(item):
    item_type = item.get("type")
    if item_type == "winner":
        return 0.45
    if item_type == "handicap":
        return 0.42
    if item_type == "total":
        return 0.18
    if item_type == "correct_score":
        return 0.16
    return 0


def allocation_floor(item):
    if not item.get("recommended"):
        return 0
    if item.get("type") == "correct_score":
        return 0.04 if item.get("forced_recommendation") else 0.06
    return 0.04


def allocation_raw_weight(item):
    score_part = max(item.get("score", 0), 1) / 100
    coverage_part = 0.35 + min(item.get("coverage_rate") or 0, 0.80)
    ev_part = 1 + max(item.get("ev_lift") or 0, 0) * 6
    if item.get("type") == "correct_score":
        ev_part *= 0.70
    if item.get("type") == "total":
        ev_part *= 0.55
    if item.get("type") == "handicap":
        ev_part *= 1.25
    if item.get("type") == "correct_score":
        ev_part *= 1 + max(item.get("market_center_score", 0), 0) / 35
        ev_part *= 1 + max(item.get("path_consistency_score", 0), 0) / 50
        ev_part *= max(0.10, 1 - item.get("path_conflict_penalty", 0) / 70)
    return score_part * coverage_part * ev_part


def normalize_shares(items):
    total = sum(item.get("share", 0) for item in items)
    if total <= 0:
        return
    for item in items:
        item["share"] = item.get("share", 0) / total


def apply_individual_caps(items):
    for _ in range(5):
        over = [item for item in items if item.get("share", 0) > allocation_cap(item)]
        if not over:
            break
        overflow = 0
        for item in over:
            cap = allocation_cap(item)
            overflow += item["share"] - cap
            item["share"] = cap
        receivers = [item for item in items if item not in over and item.get("share", 0) < allocation_cap(item)]
        receiver_total = sum(item.get("share", 0) for item in receivers)
        if not receivers or receiver_total <= 0:
            break
        for item in receivers:
            room = allocation_cap(item) - item.get("share", 0)
            item["share"] += min(room, overflow * item.get("share", 0) / receiver_total)
    normalize_shares(items)


def apply_correlation_caps(items):
    correct_items = [item for item in items if item.get("type") == "correct_score"]
    correct_total = sum(item.get("share", 0) for item in correct_items)
    if correct_total > 0.26:
        scale = 0.26 / correct_total
        released = 0
        for item in correct_items:
            old = item["share"]
            item["share"] = old * scale
            released += old - item["share"]
        receivers = [item for item in items if item.get("type") != "correct_score"]
        receiver_total = sum(item.get("share", 0) for item in receivers)
        if receiver_total:
            for item in receivers:
                item["share"] += released * item["share"] / receiver_total

    path_items = [item for item in items if item.get("type") in {"winner", "handicap", "correct_score"}]
    path_total = sum(item.get("share", 0) for item in path_items)
    total_items = [item for item in items if item.get("type") == "total"]
    if path_total > 0.86 and total_items:
        scale = 0.86 / path_total
        released = 0
        for item in path_items:
            old = item["share"]
            item["share"] = old * scale
            released += old - item["share"]
        total_weight = sum(item.get("share", 0) for item in total_items)
        for item in total_items:
            item["share"] += released * item["share"] / total_weight if total_weight else released / len(total_items)
    normalize_shares(items)


def assign_portfolio_shares(slots):
    recommended = [item for item in slots if item.get("recommended")]
    if not recommended:
        for item in slots:
            item["share"] = 0
        return

    raw_total = sum(allocation_raw_weight(item) for item in recommended)
    for item in slots:
        if item.get("recommended") and raw_total:
            item["share"] = allocation_raw_weight(item) / raw_total
        else:
            item["share"] = 0

    for item in recommended:
        item["share"] = max(item["share"], allocation_floor(item))
    normalize_shares(recommended)
    apply_individual_caps(recommended)
    apply_correlation_caps(recommended)
    for item in slots:
        if not item.get("recommended"):
            item["share"] = 0


def build_recommendation_slots(match, odds, api_football_data, actual_odds, distribution=None):
    candidates = [
        enrich_candidate(candidate, actual_odds, match, distribution)
        for candidate in build_market_candidates(match, odds, api_football_data)
    ]
    apply_path_consistency(candidates, match, distribution or {})
    force_min_correct_scores(candidates, minimum=2)
    candidates.sort(key=lambda item: (item.get("recommended", False), item.get("score", 0)), reverse=True)
    ev_sorted = sorted(
        [item for item in candidates if item.get("ev_lift") is not None],
        key=lambda item: item.get("ev_lift", -999),
        reverse=True,
    )
    for rank, item in enumerate(ev_sorted, start=1):
        item["ev_rank"] = rank

    core_candidates = [item for item in candidates if item.get("type") != "correct_score"]
    correct_candidates = [item for item in candidates if item.get("type") == "correct_score"]
    correct_candidates.sort(
        key=lambda item: (
            item.get("recommended", False),
            item.get("market_center_score", 0),
            -item.get("market_center_rank", 999),
            item.get("path_consistency_score", 0),
            -item.get("path_conflict_penalty", 0),
            item.get("path_match_score", 0),
            item.get("coverage_rate", 0),
            item.get("score", 0),
        ),
        reverse=True,
    )
    slots = core_candidates[:8] + correct_candidates[:24]
    while len(slots) < min(5, max(5, len(slots))):
        slots.append({
            "slot": f"空位{len(slots) + 1}",
            "type": "empty",
            "recommended": False,
            "name": "不推荐",
            "score": 0,
            "share": 0,
            "reason": "没有可用的真实盘口数据。",
            "not_recommended_reason": "没有可用的真实盘口数据。",
        })

    assign_portfolio_shares(slots)
    return slots


def recommendation_reason(candidate):
    if candidate.get("forced_recommendation"):
        return candidate.get("reason", "硬规则保留至少一个波胆。")
    item_type = candidate.get("type")
    if item_type == "winner":
        return "覆盖率最高，用于承接主方向判断。"
    if item_type == "handicap":
        return "市场主盘口，决定赢球路径是否打穿。"
    if item_type == "total":
        return "节奏资产，只辅助判断进球数，不代表比赛主逻辑。"
    if item_type == "correct_score":
        return candidate.get("market_center_reason") or candidate.get("path_match_reason") or "用于覆盖最可能比分路径。"
    return "综合评分进入前列。"


def odds_edge_reason(candidate):
    edge = candidate.get("edge")
    ev_lift = candidate.get("ev_lift")
    ev_text = ""
    if ev_lift is not None:
        ev_text = f" EV提升 {ev_lift * 100:+.1f}%。"
    if edge is None:
        return "未输入实际赔率，暂按市场标准赔率评估。"
    if edge >= 0.05:
        return f"实际赔率高于市场标准 {edge * 100:.1f}%，价值提升。{ev_text}"
    if edge >= 0.02:
        return f"实际赔率高于市场标准 {edge * 100:.1f}%，略有优势。{ev_text}"
    if edge >= -0.02:
        return f"实际赔率与市场标准接近，差异 {edge * 100:+.1f}%。{ev_text}"
    return f"实际赔率低于市场标准 {abs(edge) * 100:.1f}%，价值下降。{ev_text}"


def not_recommended_reason(candidate):
    if not candidate.get("standard_odds"):
        return "缺少市场标准赔率，无法评估。"
    edge = candidate.get("edge")
    ev_lift = candidate.get("ev_lift")
    score = candidate.get("score", 0)
    if edge is not None and edge < -0.02:
        return f"实际赔率低于市场标准 {abs(edge) * 100:.1f}%，不划算。"
    if ev_lift is not None and ev_lift < 0:
        return f"EV为负，长期期望收益下降 {abs(ev_lift) * 100:.1f}%。"
    if candidate.get("type") == "correct_score":
        return "波胆命中要求高，当前分数不足。"
    return f"综合分 {score}，未达到推荐阈值 55。"


def market_center_reason(candidate):
    if candidate.get("type") != "correct_score":
        return ""
    rank = candidate.get("market_center_rank")
    label = candidate.get("market_center_label")
    if not rank:
        return ""
    if rank <= 5:
        return f"{candidate.get('selection')} 是波胆市场第{rank}低赔率路径，属于{label}。"
    return f"{candidate.get('selection')} 是波胆市场第{rank}路径，偏离市场中心；除非EV优势明显，否则降低优先级。"


def actual_odds_summary(slots):
    recommended = [slot for slot in slots if slot.get("recommended")]
    if not recommended:
        return {
            "avg_edge": 0,
            "best_edge": None,
            "avg_ev_lift": 0,
            "best_ev_lift": None,
            "positive_ev_count": 0,
            "negative_ev_count": 0,
            "core_positive_count": 0,
            "weighted_ev_lift": 0,
            "recommended_count": 0,
        }
    edges = [slot.get("edge") for slot in recommended if slot.get("edge") is not None]
    ev_lifts = [slot.get("ev_lift") for slot in recommended if slot.get("ev_lift") is not None]
    positive_ev = [value for value in ev_lifts if value > 0]
    negative_ev = [value for value in ev_lifts if value < 0]
    core_positive = [
        slot for slot in recommended
        if slot.get("type") in {"winner", "handicap", "total"} and (slot.get("ev_lift") or 0) > 0
    ]
    weights = [
        max(0.05, slot.get("coverage_rate") or 0)
        * (1.25 if slot.get("type") in {"winner", "handicap"} else 1.10 if slot.get("type") == "total" else 0.40)
        for slot in recommended
        if slot.get("ev_lift") is not None
    ]
    weighted_values = [
        (slot.get("ev_lift") or 0) * weight
        for slot, weight in zip([slot for slot in recommended if slot.get("ev_lift") is not None], weights)
    ]
    weighted_ev = sum(weighted_values) / sum(weights) if weights else 0
    return {
        "avg_edge": sum(edges) / len(edges) if edges else 0,
        "best_edge": max(edges) if edges else None,
        "avg_ev_lift": sum(ev_lifts) / len(ev_lifts) if ev_lifts else 0,
        "best_ev_lift": max(ev_lifts) if ev_lifts else None,
        "positive_ev_count": len(positive_ev),
        "negative_ev_count": len(negative_ev),
        "core_positive_count": len(core_positive),
        "weighted_ev_lift": weighted_ev,
        "recommended_count": len(recommended),
    }
