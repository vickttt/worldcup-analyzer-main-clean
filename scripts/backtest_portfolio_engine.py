import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.portfolio_engine import (
    handicap_line_from_text,
    normalize_score,
    settle_asian_handicap,
    total_side_and_line,
)


HISTORY_DIR = ROOT / "data" / "history"
WORLDCUP_DIR = ROOT / "data" / "worldcup2026"
REPORT_DIR = ROOT / "reports" / "backtests"


TARGET_MATCHES = [
    "Germany vs Ivory Coast",
    "Spain vs Saudi Arabia",
    "South Africa vs South Korea",
    "Morocco vs Haiti",
    "Scotland vs Brazil",
    "Switzerland vs Canada",
    "Bosnia and Herzegovina vs Qatar",
    "Czechia vs Mexico",
    "Colombia vs DR Congo",
    "England vs Ghana",
    "Portugal vs Uzbekistan",
]


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def stem_key(path):
    name = path.name
    if name.endswith("_pre.json"):
        return name[:-9]
    if name.endswith("_post.json"):
        return name[:-10]
    return path.parent.name


def money_value(value):
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value or "")
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text.replace(",", ""))
    return float(match.group(0)) if match else 0.0


def percent_value(value):
    text = str(value or "")
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text)
    return float(match.group(0)) / 100 if match else 0.0


def match_name(data):
    match = (data or {}).get("match") or {}
    if match.get("display"):
        return match["display"]
    if match.get("display_name"):
        return match["display_name"]
    home = match.get("home") or match.get("home_en") or match.get("home_cn") or "Home"
    away = match.get("away") or match.get("away_en") or match.get("away_cn") or "Away"
    return f"{home} vs {away}"


def match_key_name(name):
    return re.sub(r"[^a-z0-9]+", " ", str(name).lower()).strip()


def kickoff(data):
    fixture = (data or {}).get("fixture") or {}
    match_info = (data or {}).get("match_info") or {}
    return (
        fixture.get("kickoff_display")
        or fixture.get("kickoff_utc")
        or match_info.get("kickoff")
        or (data or {}).get("created_at")
        or "-"
    )


def final_score(post):
    score = (post or {}).get("final_score")
    if score:
        return normalize_score(score)
    result = (post or {}).get("final_result") or {}
    if result.get("home") is not None and result.get("away") is not None:
        return f"{int(result['home'])}:{int(result['away'])}"
    fixture_score = ((post or {}).get("fixture") or {}).get("score") or {}
    if fixture_score.get("home") is not None and fixture_score.get("away") is not None:
        return f"{int(fixture_score['home'])}:{int(fixture_score['away'])}"
    return None


def parse_score(score):
    try:
        return [int(part) for part in str(score).split(":", 1)]
    except (TypeError, ValueError):
        return [None, None]


def item_odds(item):
    try:
        odds = float(item.get("actual_odds") or item.get("effective_odds") or item.get("odds") or item.get("standard_odds"))
    except (TypeError, ValueError):
        return None
    return odds if odds > 1 else None


def item_stake(item):
    try:
        return float(item.get("amount") or item.get("stake") or 0)
    except (TypeError, ValueError):
        return 0.0


def home_names(match):
    return {
        str(match.get("home") or "").lower(),
        str(match.get("home_en") or "").lower(),
        str(match.get("home_cn") or "").lower(),
        "home",
    }


def away_names(match):
    return {
        str(match.get("away") or "").lower(),
        str(match.get("away_en") or "").lower(),
        str(match.get("away_cn") or "").lower(),
        "away",
    }


def winner_profit(item, match, score):
    home_goals, away_goals = parse_score(score)
    if home_goals is None:
        return 0, "no_score"
    odds = item_odds(item)
    stake = item_stake(item)
    if not odds:
        return 0, "no_odds"
    selection = str(item.get("selection") or item.get("name") or "").lower()
    if "draw" in selection or "平" in selection:
        hit = home_goals == away_goals
    elif any(name and name in selection for name in home_names(match)):
        hit = home_goals > away_goals
    elif any(name and name in selection for name in away_names(match)):
        hit = away_goals > home_goals
    else:
        hit = False
    return (stake * (odds - 1), "win") if hit else (-stake, "lose")


def handicap_profit(item, match, score):
    odds = item_odds(item)
    stake = item_stake(item)
    if not odds:
        return 0, "no_odds"
    selection = str(item.get("selection") or item.get("name") or "")
    side = str(item.get("handicap_side") or "").lower()
    lower = selection.lower()
    if not side:
        if "away" in lower or any(name and name in lower for name in away_names(match)):
            side = "away"
        else:
            side = "home"
    line_info = item.get("handicap_line") or handicap_line_from_text(selection)
    profit = settle_asian_handicap(score, side, line_info.get("split_legs"), odds, stake)
    if profit > 0:
        return profit, "win"
    if profit < 0:
        return profit, "lose"
    return 0, "push"


def total_profit(item, score):
    home_goals, away_goals = parse_score(score)
    if home_goals is None:
        return 0, "no_score"
    odds = item_odds(item)
    stake = item_stake(item)
    if not odds:
        return 0, "no_odds"
    side, line = total_side_and_line(item.get("selection") or item.get("name"))
    if side is None or line is None:
        return -stake, "lose"
    total = home_goals + away_goals
    if abs(total - line) < 0.001:
        return 0, "push"
    hit = total > line if side == "over" else total < line
    return (stake * (odds - 1), "win") if hit else (-stake, "lose")


def correct_score_profit(item, score):
    odds = item_odds(item)
    stake = item_stake(item)
    if not odds:
        return 0, "no_odds"
    hit = normalize_score(item.get("selection") or item.get("name")) == normalize_score(score)
    return (stake * (odds - 1), "win") if hit else (-stake, "lose")


def settle_item(item, match, score):
    item_type = str(item.get("type") or "").lower()
    if item_type == "winner":
        return winner_profit(item, match, score)
    if item_type == "handicap":
        return handicap_profit(item, match, score)
    if item_type == "total":
        return total_profit(item, score)
    if item_type == "correct_score":
        return correct_score_profit(item, score)
    return -item_stake(item), "lose"


def settle_strategy(strategy, match, score):
    total_stake = 0.0
    total_profit = 0.0
    hit = loss = push = 0
    detail = []
    for item in strategy.get("items") or []:
        stake = item_stake(item)
        profit, outcome = settle_item(item, match, score)
        total_stake += stake
        total_profit += profit
        if outcome == "win":
            hit += 1
        elif outcome == "push":
            push += 1
        else:
            loss += 1
        detail.append({"item": item.get("name") or item.get("selection"), "profit": profit, "outcome": outcome})
    return {
        "stake": total_stake,
        "profit": total_profit,
        "roi": total_profit / total_stake if total_stake else 0,
        "hit_count": hit,
        "loss_count": loss,
        "push_count": push,
        "detail": detail,
    }


def settlement_from_saved(row):
    detail = row.get("_detail") or []
    hit = sum(1 for item in detail if item.get("结果") == "赢")
    loss = sum(1 for item in detail if item.get("结果") == "输")
    push = sum(1 for item in detail if item.get("结果") == "走水")
    stake = money_value(row.get("投入"))
    profit = money_value(row.get("盈亏"))
    roi = percent_value(row.get("ROI")) if row.get("ROI") else (profit / stake if stake else 0)
    return {"stake": stake, "profit": profit, "roi": roi, "hit_count": hit, "loss_count": loss, "push_count": push}


def strategy_style(name):
    text = str(name or "").lower()
    if "conservative" in text:
        return "Conservative"
    if "aggressive" in text:
        return "Aggressive"
    if "tail" in text:
        return "Tail Hedge"
    if "main" in text:
        return "Main Scenario"
    if "我的" in text or "my portfolio" in text:
        return "My Portfolio"
    return "System"


def score_rows_for_strategy(strategy):
    rows = strategy.get("score_rows") or []
    return rows if isinstance(rows, list) else []


def actual_score_covered(strategy, score):
    rows = score_rows_for_strategy(strategy)
    normalized = normalize_score(score)
    for row in rows:
        if normalize_score(row.get("比分")) == normalized:
            return money_value(row.get("组合收益") or row.get("_total")) > 0
    return None


def best_score_path(strategy):
    rows = score_rows_for_strategy(strategy)
    if not rows:
        return "-"
    best = max(rows, key=lambda row: money_value(row.get("_total") if row.get("_total") is not None else row.get("组合收益")))
    return str(best.get("比分") or "-")


def actual_score_path(distribution, score):
    rows = (distribution or {}).get("rows") or []
    home_goals, away_goals = parse_score(score)
    if home_goals is None:
        return "-"
    margin = abs(home_goals - away_goals)
    if home_goals == away_goals:
        return "draw"
    if margin == 1:
        return "one_goal_win"
    if margin == 2:
        return "two_goal_win"
    return "three_plus_goal_win"


def one_goal_deviation_failure(distribution, score, profit):
    return actual_score_path(distribution, score) == "one_goal_win" and profit < 0


def collect_history_pairs():
    pairs = {}
    for pre in HISTORY_DIR.glob("*_pre.json"):
        pairs.setdefault(stem_key(pre), {})["pre"] = pre
    for post in HISTORY_DIR.glob("*_post.json"):
        pairs.setdefault(stem_key(post), {})["post"] = post
    for folder in WORLDCUP_DIR.glob("20*"):
        if not folder.is_dir():
            continue
        pre = folder / "pre_match.json"
        post = folder / "post_match.json"
        entry = pairs.setdefault(folder.name, {})
        if pre.exists() and "pre" not in entry:
            entry["pre"] = pre
        if post.exists() and "post" not in entry:
            entry["post"] = post
    return pairs


def strategy_rank_map(pre):
    strategies = (((pre or {}).get("strategy_snapshot") or {}).get("strategies") or [])
    rank = {}
    for index, strategy in enumerate(strategies, start=1):
        names = {
            strategy.get("rank_name"),
            strategy.get("name"),
            strategy.get("original_name"),
            strategy.get("code"),
        }
        for name in names:
            if name:
                rank[str(name)] = {
                    "rank": index,
                    "score": strategy.get("score"),
                    "strategy": strategy,
                }
    return rank


def result_rows_from_pair(key, paths, skipped):
    pre_path = paths.get("pre")
    post_path = paths.get("post")
    if not pre_path or not post_path:
        skipped.append({"match_id": key, "reason": "missing pre or post snapshot"})
        return []
    pre = load_json(pre_path)
    post = load_json(post_path)
    if not pre or not post:
        skipped.append({"match_id": key, "reason": "invalid JSON"})
        return []
    score = final_score(post)
    if not score:
        skipped.append({"match_id": key, "match_name": match_name(pre), "reason": "missing final score"})
        return []
    match = (pre.get("match") or post.get("match") or {})
    distribution = pre.get("probability_distribution") or post.get("probability_distribution") or {}
    rank_map = strategy_rank_map(pre)
    rows = []
    saved = post.get("strategy_settlement") or []
    if saved:
        for row in saved:
            settlement = settlement_from_saved(row)
            name = row.get("组合") or row.get("来源") or "-"
            source = row.get("来源") or name
            pre_info = rank_map.get(str(source)) or rank_map.get(str(name)) or {}
            rows.append({
                "match_id": key,
                "match_name": match_name(pre),
                "kickoff": kickoff(pre),
                "actual_score": score,
                "portfolio_name": name,
                "portfolio_style": strategy_style(source),
                "pre_match_rank": pre_info.get("rank") or "",
                "pre_match_score": pre_info.get("score") or "",
                "total_stake": round(settlement["stake"], 2),
                "net_profit": round(settlement["profit"], 2),
                "roi": round(settlement["roi"], 4),
                "hit_count": settlement["hit_count"],
                "loss_count": settlement["loss_count"],
                "push_count": settlement["push_count"],
                "best_score_path": best_score_path(pre_info.get("strategy") or {}),
                "actual_score_path": actual_score_path(distribution, score),
                "covered_actual_score": actual_score_covered(pre_info.get("strategy") or {}, score),
                "zero_risk_triggered": settlement["stake"] > 0 and settlement["profit"] <= -settlement["stake"],
                "one_goal_deviation_failure": one_goal_deviation_failure(distribution, score, settlement["profit"]),
                "recomputed_with_current_model": False,
            })
        return rows

    strategies = (((pre or {}).get("strategy_snapshot") or {}).get("strategies") or [])
    if not strategies:
        skipped.append({"match_id": key, "match_name": match_name(pre), "reason": "missing saved strategies and settlements"})
        return []
    for index, strategy in enumerate(strategies, start=1):
        settlement = settle_strategy(strategy, match, score)
        rows.append({
            "match_id": key,
            "match_name": match_name(pre),
            "kickoff": kickoff(pre),
            "actual_score": score,
            "portfolio_name": strategy.get("rank_name") or strategy.get("name") or f"Portfolio {index}",
            "portfolio_style": strategy_style(strategy.get("name")),
            "pre_match_rank": index,
            "pre_match_score": strategy.get("score") or "",
            "total_stake": round(settlement["stake"], 2),
            "net_profit": round(settlement["profit"], 2),
            "roi": round(settlement["roi"], 4),
            "hit_count": settlement["hit_count"],
            "loss_count": settlement["loss_count"],
            "push_count": settlement["push_count"],
            "best_score_path": best_score_path(strategy),
            "actual_score_path": actual_score_path(distribution, score),
            "covered_actual_score": actual_score_covered(strategy, score),
            "zero_risk_triggered": settlement["stake"] > 0 and settlement["profit"] <= -settlement["stake"],
            "one_goal_deviation_failure": one_goal_deviation_failure(distribution, score, settlement["profit"]),
            "recomputed_with_current_model": True,
        })
    return rows


def add_post_ranks(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["match_id"]].append(row)
    for group_rows in grouped.values():
        ranked = sorted(group_rows, key=lambda row: row["net_profit"], reverse=True)
        for index, row in enumerate(ranked, start=1):
            row["actual_profit_rank_post_match"] = index
    return rows


def summarize(rows):
    if not rows:
        return {}
    match_ids = sorted(set(row["match_id"] for row in rows))
    rank_one = [row for row in rows if str(row.get("pre_match_rank")) == "1" or row.get("portfolio_name") == "推荐组合"]
    total_profit = sum(row["net_profit"] for row in rows)
    total_stake = sum(row["total_stake"] for row in rows)
    style_profit = defaultdict(float)
    style_count = defaultdict(int)
    for row in rows:
        style_profit[row["portfolio_style"]] += row["net_profit"]
        style_count[row["portfolio_style"]] += 1
    style_roi = {
        style: style_profit[style] / sum(r["total_stake"] for r in rows if r["portfolio_style"] == style)
        for style in style_profit
        if sum(r["total_stake"] for r in rows if r["portfolio_style"] == style)
    }
    return {
        "tested_matches": len(match_ids),
        "rows": len(rows),
        "overall_profit": round(total_profit, 2),
        "overall_stake": round(total_stake, 2),
        "overall_roi": round(total_profit / total_stake, 4) if total_stake else 0,
        "win_rate": round(sum(1 for row in rows if row["net_profit"] > 0) / len(rows), 4),
        "rank_one_profit_rate": round(sum(1 for row in rank_one if row["net_profit"] > 0) / len(rank_one), 4) if rank_one else 0,
        "best_style": max(style_profit, key=style_profit.get) if style_profit else "-",
        "worst_style": min(style_profit, key=style_profit.get) if style_profit else "-",
        "style_roi": style_roi,
    }


def failure_patterns(rows):
    patterns = defaultdict(int)
    for row in rows:
        if row["net_profit"] >= 0:
            continue
        if row["one_goal_deviation_failure"]:
            patterns["强队赢但一球偏差导致失败"] += 1
        if "Tail" in row["portfolio_style"] or "波胆" in row["portfolio_name"]:
            patterns["波胆路径过度集中或比分偏离"] += 1
        if row["actual_score_path"] == "draw":
            patterns["打平路径造成组合失效"] += 1
        if row["zero_risk_triggered"]:
            patterns["组合归零风险触发"] += 1
        if not patterns:
            patterns["一般方向或赔率路径失败"] += 1
    return patterns


def markdown_report(rows, skipped, summary, csv_path):
    today = datetime.now().strftime("%Y%m%d")
    lines = [
        f"# Backtest Summary {today}",
        "",
        "## Model Version",
        "",
        "Current model from saved snapshots when available; current replay script only settles missing saved settlements.",
        "",
        "## Data Source",
        "",
        "- Primary: `data/history/*_pre.json` and `data/history/*_post.json`",
        "- Secondary: `data/worldcup2026/*/pre_match.json` and `post_match.json`",
        "- My Portfolio: included when present in saved post-match settlement",
        "",
        "## Overall PnL",
        "",
        f"- Tested Matches: {summary.get('tested_matches', 0)}",
        f"- Portfolio Rows: {summary.get('rows', 0)}",
        f"- Total Stake: {summary.get('overall_stake', 0)}",
        f"- Net Profit: {summary.get('overall_profit', 0)}",
        f"- Average ROI: {summary.get('overall_roi', 0) * 100:.1f}%",
        f"- Win Rate: {summary.get('win_rate', 0) * 100:.1f}%",
        f"- Rank #1 Profit Rate: {summary.get('rank_one_profit_rate', 0) * 100:.1f}%",
        f"- Best Portfolio Style: {summary.get('best_style', '-')}",
        f"- Worst Portfolio Style: {summary.get('worst_style', '-')}",
        "",
        "## Tested Matches",
        "",
    ]
    for match in sorted(set(row["match_name"] for row in rows)):
        lines.append(f"- {match}")
    lines += [
        "",
        "## Matches Where Rank #1 Failed",
        "",
    ]
    failures = [
        row for row in rows
        if (str(row.get("pre_match_rank")) == "1" or row.get("portfolio_name") == "推荐组合") and row["net_profit"] <= 0
    ]
    if failures:
        for row in failures:
            lines.append(f"- {row['match_name']} / {row['portfolio_name']} / {row['actual_score']} / {row['net_profit']}")
    else:
        lines.append("- None in tested rows.")
    lines += [
        "",
        "## Matches Where My Portfolio Beat System",
        "",
    ]
    my_wins = []
    for match_id in sorted(set(row["match_id"] for row in rows)):
        group = [row for row in rows if row["match_id"] == match_id]
        mine = [row for row in group if row["portfolio_style"] == "My Portfolio"]
        system = [row for row in group if row.get("portfolio_name") == "推荐组合" or str(row.get("pre_match_rank")) == "1"]
        if mine and system and max(r["net_profit"] for r in mine) > max(r["net_profit"] for r in system):
            my_wins.append(mine[0]["match_name"])
    if my_wins:
        for name in my_wins:
            lines.append(f"- {name}")
    else:
        lines.append("- None detected.")
    lines += [
        "",
        "## Common Failure Patterns",
        "",
    ]
    patterns = failure_patterns(rows)
    if patterns:
        for name, count in sorted(patterns.items(), key=lambda item: item[1], reverse=True):
            lines.append(f"- {name}: {count}")
    else:
        lines.append("- No losing rows found.")
    lines += [
        "",
        "## Skipped Matches / Missing Data",
        "",
    ]
    if skipped:
        for item in skipped:
            lines.append(f"- {item.get('match_name') or item.get('match_id')}: {item.get('reason')}")
    else:
        lines.append("- None.")
    lines += [
        "",
        "## Recommended Model Fixes",
        "",
        "- Do not tune weights from this report alone; first review per-match details.",
        "- Compare third-round matches with Qualification Pressure enabled versus prior saved rankings.",
        "- Check whether Tail Hedge lowers max loss or only adds correct-score noise.",
        "- Check whether Conservative portfolios outperform Aggressive portfolios in draw-acceptable and qualified-favorite matches.",
        "- Add more settled matches before changing Portfolio Score weights.",
        "",
        f"CSV: `{csv_path}`",
    ]
    return "\n".join(lines) + "\n"


def write_outputs(rows, skipped):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows = add_post_ranks(rows)
    today = datetime.now().strftime("%Y%m%d")
    csv_path = REPORT_DIR / f"backtest_results_{today}.csv"
    md_path = REPORT_DIR / f"backtest_summary_{today}.md"
    fieldnames = [
        "match_id",
        "match_name",
        "kickoff",
        "actual_score",
        "portfolio_name",
        "portfolio_style",
        "pre_match_rank",
        "pre_match_score",
        "total_stake",
        "net_profit",
        "roi",
        "hit_count",
        "loss_count",
        "push_count",
        "best_score_path",
        "actual_score_path",
        "covered_actual_score",
        "zero_risk_triggered",
        "one_goal_deviation_failure",
        "recommendation_rank_pre_match",
        "actual_profit_rank_post_match",
        "recomputed_with_current_model",
    ]
    for row in rows:
        row["recommendation_rank_pre_match"] = row.get("pre_match_rank")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    summary = summarize(rows)
    md_path.write_text(markdown_report(rows, skipped, summary, csv_path), encoding="utf-8")
    return md_path, csv_path, summary


def main():
    pairs = collect_history_pairs()
    rows = []
    skipped = []
    for key, paths in sorted(pairs.items()):
        rows.extend(result_rows_from_pair(key, paths, skipped))
    target_found = []
    normalized_rows = {match_key_name(row["match_name"]) for row in rows}
    for target in TARGET_MATCHES:
        if not any(match_key_name(target).replace("dr congo", "congo dr") in name or name in match_key_name(target) for name in normalized_rows):
            target_found.append({"match_id": target, "reason": "target match not found as complete pre/post pair"})
    skipped.extend(target_found)
    md_path, csv_path, summary = write_outputs(rows, skipped)
    print(f"Backtest matches: {summary.get('tested_matches', 0)}")
    print(f"Portfolio rows: {summary.get('rows', 0)}")
    print(f"Overall ROI: {summary.get('overall_roi', 0) * 100:.1f}%")
    print(f"Report: {md_path}")
    print(f"CSV: {csv_path}")
    if skipped:
        print("Skipped:")
        for item in skipped[:20]:
            print(f"- {item.get('match_name') or item.get('match_id')}: {item.get('reason')}")


if __name__ == "__main__":
    main()
