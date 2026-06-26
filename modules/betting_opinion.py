from modules.market_utils import (
    asian_handicap_summary,
    identify_handicap_center,
    identify_total_center,
)
from modules.pregame_content import team_cn


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
        team_cn(match["home_cn"]): odds.get("home_win"),
        "平局": odds.get("draw"),
        team_cn(match["away_cn"]): odds.get("away_win"),
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


def handicap_market_view(api_football_data, odds, match):
    rows = ((api_football_data or {}).get("asian_handicap") or {}).get("rows") or []
    center = identify_handicap_center(rows, odds=odds, match=match)
    if not center.get("available"):
        return {
            "market_direction": "No view",
            "coverage_candidate": "No coverage candidate",
            "recommended_use": "Handicap market is not available.",
            "reason": center.get("warning") or "Handicap market is not available.",
            "center": center,
        }

    favorite_team = team_cn(match.get("home_cn") if center.get("center_side") == "home" else match.get("away_cn"))
    coverage = center.get("coverage_label") or "No coverage candidate"
    reason = (
        "胜平负市场、Polymarket 和浅盘结构均显示，"
        f"{favorite_team} 仍是实力优势方。"
    )
    if center.get("outlier_count"):
        reason += f" 已过滤 {center.get('outlier_count')} 条可能异常盘口。"

    return {
        "market_direction": center.get("direction_label", "No view"),
        "coverage_candidate": coverage,
        "recommended_use": (
            f"{coverage} 应视为保险 / 覆盖资产，用于防范热门方未打穿，"
            "不是比赛主方向投注。"
        ),
        "reason": reason,
        "center": center,
    }


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


def _translate_total_text(text):
    text = str(text or "")
    if any(token in text for token in ["盘口", "附近", "均衡", "信号"]):
        return text
    text = text.replace("Slight Over at 2.5, balanced around", "2.5 盘口略偏大球，但在")
    text = text.replace("Slight Over around", "在")
    text = text.replace(", but not an aggressive over signal.", "附近略偏大球，但不是激进大球信号。")
    text = text.replace("Slight Under around", "在")
    text = text.replace(", but not an aggressive under signal.", "附近略偏小球，但不是激进小球信号。")
    text = text.replace("Balanced around", "市场在")
    text = text.replace(".", "附近趋于均衡。")
    return text


def totals_market_view(odds):
    center = identify_total_center((odds or {}).get("over_under") or [])
    if not center.get("available"):
        return {
            "goals_view": "暂无观点",
            "total_center": "-",
            "market_bias": "大小球盘口不可用。",
            "game_behavior_note": "-",
            "recommended_interpretation": "缺少大小球盘口时，不应推断进球数方向。",
            "center": center,
        }

    return {
        "goals_view": f"总进球盘口中心：{center.get('center_label')}",
        "total_center": center.get("center_label"),
        "market_bias": _translate_total_text(center.get("market_bias")),
        "game_behavior_note": "如果出线形势提示轮换或控节奏风险，应降低激进大球信心。",
        "recommended_interpretation": "存在大球尾部，但进球数观点应以盘口中心为准，不能机械追大 2.5。",
        "center": center,
    }


def favored_by_polymarket(polymarket, match):
    if not polymarket.get("found"):
        return None

    prices = {
        team_cn(match["home_cn"]): polymarket.get("home_win"),
        "平局": polymarket.get("draw"),
        team_cn(match["away_cn"]): polymarket.get("away_win"),
    }
    prices = {key: value for key, value in prices.items() if value is not None}
    if not prices:
        return None
    return max(prices, key=prices.get)


def winner_reason(winner, polymarket, match):
    if not winner:
        return "胜平负市场数据不足，暂不形成明确主方向。"

    polymarket_winner = favored_by_polymarket(polymarket, match)
    if polymarket_winner == winner:
        return f"胜平负市场和 Polymarket 均倾向 {winner}。"
    if polymarket_winner:
        return f"胜平负赔率倾向 {winner}，但 Polymarket 观点不完全一致。"
    return f"胜平负市场倾向 {winner}。"


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


def split_confidence(odds, polymarket, handicap_view, totals_view, api_football_data=None):
    market_direction = 50
    if odds.get("found"):
        implied = odds.get("implied_probabilities") or {}
        home = implied.get("home_win", 0)
        away = implied.get("away_win", 0)
        draw = implied.get("draw", 0)
        top = max(home, away, draw)
        second = sorted([home, away, draw], reverse=True)[1]
        market_direction = int(max(50, min(82, 58 + (top - second) * 100)))
    if polymarket.get("found"):
        market_direction = min(85, market_direction + 5)

    notes = []
    betting_confidence = market_direction - 10
    lineups = (api_football_data or {}).get("lineups") or []
    if not lineups:
        betting_confidence -= 5
        notes.append("官方首发尚未公布。")
    if handicap_view.get("center", {}).get("outlier_count"):
        betting_confidence -= 5
        notes.append("API 亚洲盘存在可能异常盘口；最终下注排序应优先参考用户真实赔率。")
    if polymarket.get("found"):
        notes.append("Polymarket 对比仅支持胜平负市场；亚洲盘、大小球和波胆需要单独验证。")
    else:
        betting_confidence -= 5
        notes.append("Polymarket 胜平负市场缺失。")
    if totals_view.get("total_center") in (None, "-", "No totals center"):
        betting_confidence -= 3
        notes.append("大小球盘口中心不可用。")
    injuries = (api_football_data or {}).get("injuries")
    if not injuries and not lineups:
        notes.append("暂无公开伤病信息不等于确认全员可用，需等待首发。")

    betting_confidence = int(max(35, min(75, betting_confidence)))
    data_quality = "High"
    if len(notes) >= 3:
        data_quality = "Medium"
    if not odds.get("found") or not handicap_view.get("center", {}).get("available"):
        data_quality = "Medium"

    return {
        "market_direction_confidence": market_direction,
        "betting_confidence": betting_confidence,
        "data_quality": data_quality,
        "data_quality_notes": notes,
    }


def build_betting_opinion(match, odds, polymarket, value_analysis, api_football_data=None):
    winner = strongest_match_winner(odds, match)
    value = value_direction(value_analysis)

    if not winner:
        match_winner = "No view"
    elif value:
        match_winner = f"倾向：{winner}"
    else:
        match_winner = f"倾向：{winner}"

    handicap_view = handicap_market_view(api_football_data, odds, match)
    handicap = handicap_view["market_direction"]
    goals_view = totals_market_view(odds)
    goals = goals_view["goals_view"]
    risk = risk_level(odds, polymarket, value_analysis)
    confidence = split_confidence(odds, polymarket, handicap_view, goals_view, api_football_data)

    if value:
        summary = f"市场主方向支持 {winner}；价值分析显示 {value} 附近存在明显差异。"
    elif handicap_view.get("coverage_candidate") not in (None, "No coverage candidate"):
        summary = f"比赛主方向支持 {winner}；{handicap_view['coverage_candidate']} 是覆盖资产，不是主方向。"
    elif handicap != "No view":
        summary = f"市场整体支持 {winner}；让球盘口方向与主方向基本一致。"
    else:
        summary = f"市场整体支持 {winner}。" if winner else "市场数据不足，暂不形成明确观点。"

    return {
        "match_winner": match_winner,
        "match_direction": match_winner,
        "asian_handicap": handicap,
        "handicap_market_direction": handicap,
        "coverage_candidate": handicap_view.get("coverage_candidate"),
        "coverage_reason": (
            f"{handicap_view.get('coverage_candidate')} 不是主方向投注，而是防守型覆盖资产，"
            "用于防范平局、低节奏、热门方轮换或出线压力导致的不积极推进风险。"
            if handicap_view.get("coverage_candidate") not in (None, "No coverage candidate")
            else "未识别到覆盖候选。"
        ),
        "recommended_use": handicap_view.get("recommended_use"),
        "over_under": goals,
        "total_center": goals_view.get("total_center"),
        "goals_market_bias": goals_view.get("market_bias"),
        "goals_game_behavior_note": goals_view.get("game_behavior_note"),
        "goals_recommended_interpretation": goals_view.get("recommended_interpretation"),
        "risk_level": risk,
        "confidence": confidence.get("market_direction_confidence", confidence_score(risk)),
        "market_direction_confidence": confidence.get("market_direction_confidence"),
        "betting_confidence": confidence.get("betting_confidence"),
        "data_quality": confidence.get("data_quality"),
        "data_quality_notes": confidence.get("data_quality_notes", []),
        "match_winner_reason": winner_reason(winner, polymarket, match),
        "asian_handicap_reason": handicap_view.get("reason"),
        "over_under_reason": goals_view.get("market_bias"),
        "summary": summary,
        "handicap_center": handicap_view.get("center"),
        "total_center_detail": goals_view.get("center"),
    }
