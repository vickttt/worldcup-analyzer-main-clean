from modules.market_utils import parse_handicap_value, safe_float
from modules.pregame_content import team_cn
from modules.probability_base import true_probability_base


ALLOWED_MARKETS = {"独赢", "胜平负", "让球", "大小球", "波胆", "其他"}


def _clean_text(value):
    return str(value or "").strip()


def _normalized(value):
    return _clean_text(value).lower().replace(" ", "")


def _normalize_market(value):
    text = _clean_text(value)
    if "独赢" in text or "胜平负" in text or text.lower() in {"1x2", "matchwinner"}:
        return "独赢"
    if "让球" in text or "handicap" in text.lower():
        return "让球"
    if "大小" in text or "over" in text.lower() or "under" in text.lower():
        return "大小球"
    if "波胆" in text or "比分" in text or "correct" in text.lower():
        return "波胆"
    return text if text in ALLOWED_MARKETS else "其他"


def _split_enabled_market(market):
    return _normalize_market(market) in {"让球", "大小球"}


def _team_label(match, side):
    if not match:
        return side
    key = "home_cn" if side == "home" else "away_cn"
    fallback = "home_en" if side == "home" else "away_en"
    return team_cn(match.get(key) or match.get(fallback) or side)


def _tpb_direction(odds, match):
    probabilities = (true_probability_base(odds or {}).get("probabilities") or {})
    if not probabilities:
        return {
            "outcome": None,
            "label": "无法判断",
            "probability": None,
        }
    outcome = max(probabilities, key=lambda key: probabilities.get(key, 0))
    labels = {
        "home_win": _team_label(match, "home"),
        "draw": "平局",
        "away_win": _team_label(match, "away"),
    }
    return {
        "outcome": outcome,
        "label": labels.get(outcome, outcome),
        "probability": probabilities.get(outcome),
    }


def _parse_number(value, field_name, line_number):
    text = _clean_text(value)
    if not text:
        return None, None
    try:
        number = float(text)
    except ValueError:
        return None, f"第 {line_number} 行 {field_name} 必须是数字。"
    return number, None


def _is_score_text(value):
    text = _clean_text(value).replace("-", ":").replace("–", ":")
    if ":" not in text:
        return False
    left, right = text.split(":", 1)
    return left.strip().isdigit() and right.strip().isdigit()


def _is_handicap_text(value, market=None):
    text = _clean_text(value)
    if not text:
        return False
    if "/" in text and _split_enabled_market(market):
        return bool(_parse_split_handicap(text))
    if _normalize_market(market) == "波胆" and _is_score_text(text):
        return True
    if text.startswith(("+", "-")) and safe_float(text) is not None:
        return True
    if _normalize_market(market) == "大小球" and safe_float(text) is not None:
        return True
    return False


def _parse_split_handicap(value):
    text = _clean_text(value)
    if "/" not in text:
        return None
    parts = [part.strip() for part in text.split("/") if part.strip()]
    if len(parts) < 2:
        return None
    sign_multiplier = -1 if parts[0].startswith("-") else 1
    parsed = []
    for index, part in enumerate(parts):
        token = part
        if index > 0 and sign_multiplier < 0 and not part.startswith(("+", "-")):
            token = f"-{part}"
        number = safe_float(token)
        if number is None:
            return None
        parsed.append(float(number))
    return parsed


def _line_display(handicap, split_handicap=None):
    if split_handicap:
        return " / ".join(f"{value:g}" for value in split_handicap)
    return _clean_text(handicap)


def _split_total_selection(selection):
    text = _clean_text(selection)
    parts = text.split()
    if len(parts) >= 2 and _normalized(parts[0]) in {"under", "over", "小", "大", "小球", "大球"}:
        line = parts[1]
        if safe_float(line) is not None:
            return parts[0], line
    return selection, None


def _parse_position_parts(parts, line_number):
    if len(parts) < 3:
        return None, f"第 {line_number} 行字段不足，请使用：市场,选择,盘口(可选),赔率。"
    if len(parts) > 4:
        return None, f"第 {line_number} 行字段过多，请确认没有多余分隔符。"

    market = _normalize_market(parts[0])
    selection = _clean_text(parts[1])
    if not market or not selection:
        return None, f"第 {line_number} 行市场和选择不能为空。"

    remaining = [_clean_text(part) for part in parts[2:] if _clean_text(part)]
    if not remaining:
        return None, f"第 {line_number} 行缺少赔率，已跳过。"

    odds = None
    handicap = None
    if len(remaining) == 1:
        odds, odds_error = _parse_number(remaining[0], "赔率", line_number)
        if odds_error or odds is None or odds <= 0:
            return None, f"第 {line_number} 行缺少有效赔率，已跳过。"
    else:
        first, second = remaining
        first_number = safe_float(first)
        second_number = safe_float(second)
        if second_number is not None and second_number > 0:
            odds = second_number
            handicap = first if _is_handicap_text(first, market) else None
        elif first_number is not None and first_number > 0:
            odds = first_number
            handicap = second if _is_handicap_text(second, market) else None
        else:
            return None, f"第 {line_number} 行缺少有效赔率，已跳过。"

    if market == "大小球" and handicap is None:
        parsed_selection, parsed_line = _split_total_selection(selection)
        selection = parsed_selection
        handicap = parsed_line
    if market == "波胆":
        handicap = None
    split_handicap = _parse_split_handicap(handicap) if _split_enabled_market(market) else None

    return {
        "line_number": line_number,
        "market": market,
        "selection": selection,
        "handicap": handicap,
        "split_handicap": split_handicap,
        "is_split_line": bool(split_handicap),
        "odds": float(odds),
    }, None


def parse_user_portfolio_text(raw_text):
    positions = []
    warnings = []
    for line_number, raw_line in enumerate(str(raw_text or "").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.replace("，", ",").split(",")]
        position, warning = _parse_position_parts(parts, line_number)
        if warning:
            warnings.append(warning)
        if position:
            positions.append(position)
    return positions, warnings


def _selection_matches_tpb(selection, direction, match):
    selected = _normalized(selection)
    if not selected or not direction.get("outcome"):
        return False
    candidates = {
        "home_win": {_normalized(_team_label(match, "home")), "主胜", "home", "homewin"},
        "draw": {"平局", "draw", "x"},
        "away_win": {_normalized(_team_label(match, "away")), "客胜", "away", "awaywin"},
    }
    return selected in candidates.get(direction.get("outcome"), set())


def _selection_matches_side(selection, side, match):
    selected = _normalized(selection)
    candidates = {
        "home": {_normalized(_team_label(match, "home")), "主胜", "home", "homewin"},
        "away": {_normalized(_team_label(match, "away")), "客胜", "away", "awaywin"},
    }
    return selected in candidates.get(side, set())


def _selection_outcome(selection, match):
    selected = _normalized(selection)
    if selected in {_normalized(_team_label(match, "home")), "主胜", "home", "homewin"}:
        return "home_win"
    if selected in {"平局", "draw", "x"}:
        return "draw"
    if selected in {_normalized(_team_label(match, "away")), "客胜", "away", "awaywin"}:
        return "away_win"
    return None


def _selection_is_opposite(selection, direction, match):
    selected = _normalized(selection)
    if not selected or direction.get("outcome") not in {"home_win", "away_win"}:
        return False
    opposite = "away_win" if direction["outcome"] == "home_win" else "home_win"
    candidates = {
        "home_win": {_normalized(_team_label(match, "home")), "主胜", "home", "homewin"},
        "away_win": {_normalized(_team_label(match, "away")), "客胜", "away", "awaywin"},
    }
    return selected in candidates.get(opposite, set())


def _price_judgment(user_odds, api_odds):
    if api_odds is None:
        return {
            "api_odds": None,
            "difference": None,
            "difference_text": "-",
            "judgment": "暂无可比 API 赔率",
        }
    difference = round(float(user_odds) - float(api_odds), 3)
    if difference > 0.03:
        judgment = "用户赔率更好"
    elif difference < -0.03:
        judgment = "用户赔率更差"
    else:
        judgment = "接近"
    return {
        "api_odds": float(api_odds),
        "difference": difference,
        "difference_text": f"{difference:+.2f}",
        "judgment": judgment,
    }


def _match_winner_api_odds(position, match, odds):
    outcome = _selection_outcome(position.get("selection"), match)
    if not outcome:
        return None
    return safe_float((odds or {}).get(outcome))


def _handicap_api_odds(position, match, api_football_data):
    if position.get("is_split_line"):
        return None
    target_line = safe_float(position.get("handicap"))
    if target_line is None:
        return None
    rows = (((api_football_data or {}).get("asian_handicap") or {}).get("rows") or [])
    for row in rows:
        parsed = parse_handicap_value(row.get("value"))
        if not parsed:
            continue
        if not _selection_matches_side(position.get("selection"), parsed.get("side"), match):
            continue
        if safe_float(parsed.get("line")) is None:
            continue
        if abs(float(parsed["line"]) - target_line) <= 0.001:
            return safe_float(row.get("odd"))
    return None


def _total_api_odds(position, odds):
    if position.get("is_split_line"):
        return None
    target_line = safe_float(position.get("handicap"))
    if target_line is None:
        return None
    selection = _normalized(position.get("selection"))
    rows = (odds or {}).get("over_under") or []
    for row in rows:
        row_line = safe_float(row.get("line"))
        if row_line is None or abs(row_line - target_line) > 0.001:
            continue
        if selection in {"under", "小", "小球", "under球"}:
            return safe_float(row.get("under_odds"))
        if selection in {"over", "大", "大球", "over球"}:
            return safe_float(row.get("over_odds"))
    return None


def _correct_score_api_odds(position, api_football_data):
    target_score = _clean_text(position.get("selection")).replace("-", ":").replace("–", ":")
    if not target_score:
        return None
    rows = (((api_football_data or {}).get("correct_score") or {}).get("rows") or [])
    for row in rows:
        row_score = _clean_text(row.get("score")).replace("-", ":").replace("–", ":")
        if row_score == target_score:
            return safe_float(row.get("odd"))
    return None


def _api_reference_for_position(position, match, odds, api_football_data):
    market = position.get("market")
    api_odds = None
    if market in {"独赢", "胜平负"}:
        api_odds = _match_winner_api_odds(position, match, odds)
    elif market == "让球":
        api_odds = _handicap_api_odds(position, match, api_football_data)
    elif market == "大小球":
        api_odds = _total_api_odds(position, odds)
    elif market == "波胆":
        api_odds = _correct_score_api_odds(position, api_football_data)
    return _price_judgment(position.get("odds"), api_odds)


def _classify_position(position, direction, match):
    market = position.get("market")
    selection = position.get("selection")
    odds = position.get("odds") or 0
    handicap = _clean_text(position.get("handicap"))

    if market == "波胆":
        return "尾部", "波胆属于精确比分路径，作为尾部风险观察。"
    if market == "大小球":
        if _normalized(selection).startswith("under"):
            return "防守", "小球倾向通常更偏防守路径。"
        if _normalized(selection).startswith("over"):
            return "激进", "大球倾向通常更偏进攻或尾部路径。"
        return "混合", "大小球不直接对应 TPB 主方向。"
    if market in {"独赢", "胜平负"}:
        if _selection_matches_tpb(selection, direction, match):
            return "主方向", "选择与 TPB 主方向一致。"
        if _normalized(selection) in {"平局", "draw", "x"}:
            return "覆盖", "平局选择更接近覆盖/防守路径。"
        if _selection_is_opposite(selection, direction, match):
            return "冲突", "选择与 TPB 主方向相反。"
        return "混合", "无法直接映射到 TPB 主方向。"
    if market == "让球":
        if _selection_matches_tpb(selection, direction, match):
            if handicap.startswith("+"):
                return "覆盖", "主方向受让更接近防守参考。"
            return "主方向", "让球选择与 TPB 主方向一致。"
        if _selection_is_opposite(selection, direction, match) or handicap.startswith("+"):
            return "防守", "让球选择更偏覆盖或对冲路径。"
        return "混合", "让球选择与 TPB 主方向关系不明确。"
    if odds >= 8:
        return "尾部", "高赔率选择更偏尾部风险路径。"
    return "混合", "其他市场仅用于人工复盘。"


def _portfolio_type(classifications):
    if not classifications:
        return "未输入"
    counts = {label: classifications.count(label) for label in set(classifications)}
    if counts.get("冲突"):
        return "混合 / 含冲突"
    for label in ["主方向", "覆盖", "防守", "激进", "尾部"]:
        if counts.get(label) == len(classifications):
            return label
    if counts.get("主方向") and (counts.get("覆盖") or counts.get("防守")):
        return "主方向 + 防守"
    return "混合"


def _relation(classifications):
    if not classifications:
        return "未输入"
    if "冲突" in classifications:
        return "冲突"
    if all(item == "主方向" for item in classifications):
        return "一致"
    if "主方向" in classifications:
        return "部分一致"
    if any(item in {"覆盖", "防守"} for item in classifications):
        return "对冲"
    return "无法判断"


def _compatibility_score(positions, classifications):
    if not positions:
        return None
    score = 50
    for classification in classifications:
        if classification == "主方向":
            score += 15
        elif classification in {"覆盖", "防守"}:
            score += 6
        elif classification == "冲突":
            score -= 20
        elif classification == "尾部":
            score -= 12
        elif classification == "激进":
            score -= 6
    return max(0, min(100, round(score)))


def _risk_warnings(positions, classifications):
    warnings = []
    if "冲突" in classifications:
        warnings.append("存在与 TPB 主方向冲突的选择。")
    if "尾部" in classifications:
        warnings.append("包含波胆或高赔率尾部路径，波动较大。")
    if not warnings:
        warnings.append("未发现明显组合冲突；仍仅供人工复盘。")
    return warnings


def build_user_portfolio_comparison(
    raw_text,
    match=None,
    odds=None,
    betting_opinion=None,
    distribution=None,
    api_football_data=None,
):
    positions, errors = parse_user_portfolio_text(raw_text)
    direction = _tpb_direction(odds, match)
    enriched = []
    classifications = []
    for position in positions:
        classification, note = _classify_position(position, direction, match)
        price_reference = _api_reference_for_position(position, match, odds, api_football_data)
        classifications.append(classification)
        enriched.append({
            **position,
            "handicap_display": _line_display(position.get("handicap"), position.get("split_handicap")),
            "classification": classification,
            "note": note,
            "user_odds": position.get("odds"),
            "api_reference_odds": price_reference.get("api_odds"),
            "price_difference": price_reference.get("difference"),
            "price_difference_text": price_reference.get("difference_text"),
            "price_judgment": price_reference.get("judgment"),
        })

    compatibility_score = _compatibility_score(positions, classifications)
    has_input = bool(str(raw_text or "").strip())
    relation = _relation(classifications)
    portfolio_type = _portfolio_type(classifications)

    observation_rows = [{
        "对象": "系统 TPB 输出",
        "类型": "baseline",
        "关系": "系统主链",
        "TPB一致性": "基准",
        "说明": "TPB 输出仍是唯一系统决策，不受用户组合影响。",
    }]
    if positions:
        observation_rows.append({
            "对象": "我的实盘组合",
            "类型": portfolio_type,
            "关系": relation,
            "TPB一致性": f"{compatibility_score} / 100",
            "说明": "仅用于人工复盘，不参与 TPB、比赛投资分或推荐金额。",
        })

    return {
        "has_input": has_input,
        "positions": enriched,
        "errors": errors,
        "warnings": errors,
        "total_count": len(enriched),
        "tpb_direction": direction,
        "portfolio_type": portfolio_type,
        "relation": relation,
        "compatibility_score": compatibility_score,
        "risk_warnings": _risk_warnings(enriched, classifications) if enriched else [],
        "observation_rows": observation_rows,
        "disclaimer": "我的实盘组合仅用于人工复盘和 display-only 对比，不参与 TPB、比赛投资分、推荐金额、coverage 或系统主方向。",
    }
