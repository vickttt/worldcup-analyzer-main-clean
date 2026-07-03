from modules.pregame_content import team_cn
from modules.probability_base import true_probability_base


ALLOWED_MARKETS = {"胜平负", "让球", "大小球", "波胆", "其他"}


def _clean_text(value):
    return str(value or "").strip()


def _normalized(value):
    return _clean_text(value).lower().replace(" ", "")


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


def parse_user_portfolio_text(raw_text):
    positions = []
    errors = []
    for line_number, raw_line in enumerate(str(raw_text or "").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 4:
            errors.append("第 %s 行字段不足，请使用：市场,选择,盘口,赔率,金额。" % line_number)
            continue
        if len(parts) > 5:
            errors.append("第 %s 行字段过多，请确认没有多余逗号。" % line_number)
            continue

        market, selection, line_value, odds_text = parts[:4]
        amount_text = parts[4] if len(parts) == 5 else ""
        if not market or not selection:
            errors.append("第 %s 行市场和选择不能为空。" % line_number)
            continue
        if market not in ALLOWED_MARKETS:
            market = "其他"

        odds, odds_error = _parse_number(odds_text, "赔率", line_number)
        if odds_error:
            errors.append(odds_error)
            continue
        if odds is None or odds <= 0:
            errors.append("第 %s 行赔率必须大于 0。" % line_number)
            continue

        amount, amount_error = _parse_number(amount_text, "金额", line_number)
        if amount_error:
            errors.append(amount_error)
            continue
        if amount is not None and amount < 0:
            errors.append("第 %s 行金额不能为负数。" % line_number)
            continue

        positions.append({
            "line_number": line_number,
            "market": market,
            "selection": selection,
            "line": line_value,
            "odds": odds,
            "amount": amount,
        })
    return positions, errors


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


def _classify_position(position, direction, match):
    market = position.get("market")
    selection = position.get("selection")
    odds = position.get("odds") or 0
    line = _clean_text(position.get("line"))

    if market == "波胆":
        return "尾部", "波胆属于精确比分路径，作为尾部风险观察。"
    if market == "大小球":
        if _normalized(selection).startswith("under"):
            return "防守", "小球倾向通常更偏防守路径。"
        if _normalized(selection).startswith("over"):
            return "激进", "大球倾向通常更偏进攻或尾部路径。"
        return "混合", "大小球不直接对应 TPB 主方向。"
    if market == "胜平负":
        if _selection_matches_tpb(selection, direction, match):
            return "主方向", "选择与 TPB 主方向一致。"
        if _normalized(selection) in {"平局", "draw", "x"}:
            return "覆盖", "平局选择更接近覆盖/防守路径。"
        if _selection_is_opposite(selection, direction, match):
            return "冲突", "选择与 TPB 主方向相反。"
        return "混合", "无法直接映射到 TPB 主方向。"
    if market == "让球":
        if _selection_matches_tpb(selection, direction, match):
            if line.startswith("+"):
                return "覆盖", "主方向受让更接近防守参考。"
            return "主方向", "让球选择与 TPB 主方向一致。"
        if _selection_is_opposite(selection, direction, match) or line.startswith("+"):
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
    total_amount = sum(position.get("amount") or 0 for position in positions)
    if total_amount > 0:
        largest = max(position.get("amount") or 0 for position in positions)
        if largest / total_amount >= 0.7:
            score -= 8
    return max(0, min(100, round(score)))


def _risk_warnings(positions, classifications):
    warnings = []
    if "冲突" in classifications:
        warnings.append("存在与 TPB 主方向冲突的选择。")
    if "尾部" in classifications:
        warnings.append("包含波胆或高赔率尾部路径，波动较大。")
    total_amount = sum(position.get("amount") or 0 for position in positions)
    if total_amount > 0:
        largest = max(position.get("amount") or 0 for position in positions)
        if largest / total_amount >= 0.7:
            warnings.append("投入过度集中在单笔选择。")
    if not warnings:
        warnings.append("未发现明显组合冲突；仍仅供人工复盘。")
    return warnings


def build_user_portfolio_comparison(raw_text, match=None, odds=None, betting_opinion=None, distribution=None):
    positions, errors = parse_user_portfolio_text(raw_text)
    direction = _tpb_direction(odds, match)
    enriched = []
    classifications = []
    for position in positions:
        classification, note = _classify_position(position, direction, match)
        classifications.append(classification)
        enriched.append({
            **position,
            "amount_text": "未填金额" if position.get("amount") is None else f"{position.get('amount'):g}元",
            "classification": classification,
            "note": note,
        })

    total_amount = sum(position.get("amount") or 0 for position in positions)
    compatibility_score = _compatibility_score(positions, classifications)
    has_input = bool(str(raw_text or "").strip())
    relation = _relation(classifications)
    portfolio_type = _portfolio_type(classifications)

    ranking_rows = [{
        "对象": "系统 TPB 输出",
        "类型": "baseline",
        "关系": "系统主链",
        "对比分": "基准",
        "说明": "TPB 输出仍是唯一系统决策，不受用户组合影响。",
    }]
    if positions:
        ranking_rows.append({
            "对象": "我的实盘组合",
            "类型": portfolio_type,
            "关系": relation,
            "对比分": f"{compatibility_score} / 100",
            "说明": "仅用于人工复盘，不参与 TPB、比赛投资分或推荐金额。",
        })

    return {
        "has_input": has_input,
        "positions": enriched,
        "errors": errors,
        "total_count": len(enriched),
        "total_amount": total_amount,
        "total_amount_text": f"{total_amount:g}元" if total_amount else "0元",
        "tpb_direction": direction,
        "portfolio_type": portfolio_type,
        "relation": relation,
        "compatibility_score": compatibility_score,
        "risk_warnings": _risk_warnings(enriched, classifications) if enriched else [],
        "ranking_rows": ranking_rows,
        "disclaimer": "我的实盘组合仅用于人工复盘和 display-only 对比，不参与 TPB、比赛投资分、推荐金额、coverage 或系统主方向。",
    }
