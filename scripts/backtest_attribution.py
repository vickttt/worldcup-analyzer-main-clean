import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS_CSV = ROOT / "reports" / "backtests" / "backtest_results_20260625.csv"
SUMMARY_MD = ROOT / "reports" / "backtests" / "backtest_summary_20260625.md"
HISTORY_DIR = ROOT / "data" / "history"
REPORT_DIR = ROOT / "reports" / "backtests"


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def normalize_text(value):
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", str(value or "").lower())


def number(value, default=0.0):
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value or "").replace(",", ""))
    return float(match.group(0)) if match else default


def boolish(value):
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_rows():
    if not RESULTS_CSV.exists():
        raise FileNotFoundError(f"Missing {RESULTS_CSV}")
    with RESULTS_CSV.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def post_snapshots():
    by_match = {}
    for path in HISTORY_DIR.glob("*_post.json"):
        data = load_json(path)
        if not data:
            continue
        match = data.get("match") or {}
        names = {
            match.get("display"),
            f"{match.get('home')} vs {match.get('away')}",
            path.stem.replace("_post", "").replace("_", " "),
        }
        for name in names:
            key = normalize_text(name)
            if key:
                by_match[key] = data
    return by_match


def find_post(row, posts):
    key = normalize_text(row.get("match_name"))
    if key in posts:
        return posts[key]
    for post_key, post in posts.items():
        if key and (key in post_key or post_key in key):
            return post
    return {}


def portfolio_detail(post, portfolio_name):
    details = (post or {}).get("portfolio_audit_details") or {}
    if portfolio_name in details:
        return details[portfolio_name]
    for key, value in details.items():
        if normalize_text(key) == normalize_text(portfolio_name):
            return value
    return {}


def audit_row(post, portfolio_name):
    for row in (post or {}).get("recommendation_audit") or []:
        if normalize_text(row.get("组合名称")) == normalize_text(portfolio_name):
            return row
    return {}


def item_texts(detail, audit):
    items = []
    for item in (detail or {}).get("items") or []:
        items.append(str(item.get("投注") or ""))
    text = audit.get("具体投注")
    if text:
        items.extend([part.strip() for part in str(text).split("；") if part.strip()])
    return items


def parse_score(score):
    try:
        return [int(part) for part in str(score).split(":", 1)]
    except (TypeError, ValueError):
        return [None, None]


def correct_scores_from_items(items):
    scores = []
    for text in items:
        if "波胆" in text or re.search(r"\b\d+:\d+\b", text):
            match = re.search(r"(\d+)\s*[:：]\s*(\d+)", text)
            if match:
                scores.append(f"{int(match.group(1))}:{int(match.group(2))}")
    return scores


def handicap_from_items(items):
    for text in items:
        if re.search(r"\b(Home|Away)\s*[+-]\d", text, re.I) or "让球" in text:
            match = re.search(r"(Home|Away)?\s*([+-]\d+(?:\.\d+)?)", text, re.I)
            if match:
                return f"{match.group(1) or ''} {match.group(2)}".strip()
    return ""


def handicap_depth(handicap):
    match = re.search(r"([+-]\d+(?:\.\d+)?)", str(handicap or ""))
    return abs(float(match.group(1))) if match else 0.0


def total_from_items(items):
    for text in items:
        if "Over" in text or "Under" in text or "大" in text or "小" in text:
            return text
    return ""


def score_has_underdog_goal(score, favorite_home=True):
    home, away = parse_score(score)
    if home is None:
        return False
    return away > 0 if favorite_home else home > 0


def favorite_is_home(post):
    distribution = (post or {}).get("probability_distribution") or {}
    favorite = normalize_text(distribution.get("favorite"))
    match = (post or {}).get("match") or {}
    home_values = {
        normalize_text(match.get("home")),
        normalize_text(match.get("home_cn")),
        normalize_text(match.get("home_en")),
    }
    away_values = {
        normalize_text(match.get("away")),
        normalize_text(match.get("away_cn")),
        normalize_text(match.get("away_en")),
    }
    if favorite and favorite in home_values:
        return True
    if favorite and favorite in away_values:
        return False
    return None


def favorite_won(post, score):
    home, away = parse_score(score)
    if home is None:
        return False
    fav_home = favorite_is_home(post)
    if fav_home is True:
        return home > away
    if fav_home is False:
        return away > home
    return False


def draw_score(score):
    home, away = parse_score(score)
    return home is not None and home == away


def draw_path_included(items):
    text = " ".join(items).lower()
    if "draw" in text or "平" in text:
        return True
    return any(score in text for score in ["0:0", "1:1", "2:2", "3:3"])


def underdog_goal_tail_included(items, favorite_home=True):
    scores = correct_scores_from_items(items)
    if not scores:
        return False
    return any(score_has_underdog_goal(score, favorite_home=favorite_home) for score in scores)


def failure_patterns(row, items, post):
    profit = number(row.get("net_profit"))
    if profit >= 0:
        return ["profitable"]
    patterns = []
    actual_score = row.get("actual_score")
    detail_text = " ".join(items).lower()
    correct_scores = correct_scores_from_items(items)
    handicap = handicap_from_items(items)
    depth = handicap_depth(handicap)
    if draw_score(actual_score):
        patterns.append("draw_path_missed")
    fav_won = favorite_won(post, actual_score)
    if boolish(row.get("one_goal_deviation_failure")) and fav_won:
        patterns.append("favorite_won_but_failed_handicap")
        patterns.append("adjacent_score_not_covered")
    if boolish(row.get("one_goal_deviation_failure")) and not fav_won:
        patterns.append("market_direction_wrong")
    if depth >= 1.5 and profit < 0 and fav_won:
        patterns.append("favorite_won_but_failed_handicap")
    home, away = parse_score(actual_score)
    fav_home = favorite_is_home(post)
    if fav_home is None:
        fav_home = True
    if score_has_underdog_goal(actual_score, fav_home) and correct_scores and not any(score_has_underdog_goal(score, fav_home) for score in correct_scores):
        patterns.append("underdog_goal_broke_clean_sheet")
    if correct_scores and profit < 0:
        patterns.append("correct_score_over_concentrated")
    if ("over" in detail_text or "under" in detail_text or "大" in detail_text or "小" in detail_text) and profit < 0:
        patterns.append("over_under_wrong")
    pressure_type = (((post or {}).get("probability_distribution") or {}).get("game_behavior") or {}).get("match_pressure_type")
    if pressure_type and pressure_type not in {"neutral_group_context", None} and profit < 0:
        patterns.append("qualification_pressure_misread")
    if boolish(row.get("zero_risk_triggered")):
        patterns.append("low_odds_false_safety")
    if not patterns:
        patterns.append("market_direction_wrong")
    return sorted(set(patterns))


def style_name(row):
    if row.get("portfolio_style") and row["portfolio_style"] != "System":
        return row["portfolio_style"]
    name = str(row.get("portfolio_name") or "")
    if name == "推荐组合" or str(row.get("pre_match_rank")) == "1":
        return "Recommendation / Rank #1"
    return row.get("portfolio_style") or "System"


def aggregate(rows, key_fn):
    groups = defaultdict(list)
    for row in rows:
        groups[key_fn(row)].append(row)
    result = []
    for key, group in groups.items():
        stake = sum(number(r.get("total_stake")) for r in group)
        profit = sum(number(r.get("net_profit")) for r in group)
        wins = sum(1 for r in group if number(r.get("net_profit")) > 0)
        best = max(group, key=lambda r: number(r.get("net_profit")))
        worst = min(group, key=lambda r: number(r.get("net_profit")))
        result.append({
            "portfolio_style": key,
            "matches_count": len(set(r.get("match_name") for r in group)),
            "rows_count": len(group),
            "total_stake": stake,
            "total_profit": profit,
            "roi": profit / stake if stake else 0,
            "win_rate": wins / len(group) if group else 0,
            "average_profit": profit / len(group) if group else 0,
            "max_loss": min(number(r.get("net_profit")) for r in group),
            "best_match": best.get("match_name"),
            "worst_match": worst.get("match_name"),
        })
    return sorted(result, key=lambda item: item["total_profit"], reverse=True)


def attribution_rows(rows, posts):
    output = []
    for row in rows:
        post = find_post(row, posts)
        detail = portfolio_detail(post, row.get("portfolio_name"))
        audit = audit_row(post, row.get("portfolio_name"))
        items = item_texts(detail, audit)
        patterns = failure_patterns(row, items, post)
        handicap = handicap_from_items(items)
        fav_home = favorite_is_home(post)
        if fav_home is None:
            fav_home = True
        pressure_type = (((post or {}).get("probability_distribution") or {}).get("game_behavior") or {}).get("match_pressure_type") or ""
        output.append({
            "match_name": row.get("match_name"),
            "actual_score": row.get("actual_score"),
            "portfolio_name": row.get("portfolio_name"),
            "portfolio_style": style_name(row),
            "pre_match_rank": row.get("pre_match_rank") or ("1" if row.get("portfolio_name") == "推荐组合" else ""),
            "profit": row.get("net_profit"),
            "roi": row.get("roi"),
            "failure_pattern": ";".join(patterns),
            "favorite_margin": row.get("actual_score_path"),
            "handicap_depth": handicap_depth(handicap),
            "actual_score_covered": row.get("covered_actual_score"),
            "underdog_goal_tail_included": underdog_goal_tail_included(items, fav_home),
            "draw_path_included": draw_path_included(items),
            "qualification_pressure_type": pressure_type,
            "recommended_fix": recommend_fix(patterns),
            "_items": items,
            "_post": post,
        })
    return output


def recommend_fix(patterns):
    if "underdog_goal_broke_clean_sheet" in patterns:
        return "Add or reweight underdog-goal adjacent score paths."
    if "draw_path_missed" in patterns:
        return "Review draw/under coverage in pressure-sensitive games."
    if "favorite_won_but_failed_handicap" in patterns:
        return "Review deep handicap; test shallower line and one-goal protection."
    if "correct_score_over_concentrated" in patterns:
        return "Limit clean-sheet correct-score concentration."
    if "over_under_wrong" in patterns:
        return "Check totals signal against score grid and pressure context."
    if "low_odds_false_safety" in patterns:
        return "Reduce false safety from low-odds single-path assets."
    return "No tuning action from this row alone."


def pct(value):
    return f"{value * 100:.1f}%"


def money(value):
    return f"{value:+.0f}" if value < 0 else f"{value:.0f}"


def markdown_table(rows, headers):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def rank1_rows(attrib):
    return [row for row in attrib if row["portfolio_name"] == "推荐组合" or str(row.get("pre_match_rank")) == "1"]


def rank1_failures(attrib):
    return [row for row in rank1_rows(attrib) if number(row["profit"]) < 0]


def my_vs_system(attrib):
    groups = defaultdict(list)
    for row in attrib:
        groups[row["match_name"]].append(row)
    rows = []
    for match, group in groups.items():
        mine = [r for r in group if r["portfolio_style"] == "My Portfolio"]
        system = [r for r in group if r["portfolio_name"] == "推荐组合" or str(r.get("pre_match_rank")) == "1"]
        if not mine or not system:
            continue
        my_profit = max(number(r["profit"]) for r in mine)
        sys_profit = max(number(r["profit"]) for r in system)
        rows.append({
            "match_name": match,
            "my_portfolio_profit": money(my_profit),
            "system_rank1_profit": money(sys_profit),
            "difference": money(my_profit - sys_profit),
            "winner": "My Portfolio" if my_profit > sys_profit else "System",
            "reason": "用户组合收益更高" if my_profit > sys_profit else "系统首选更高或相同",
        })
    return rows


def pressure_summary(attrib):
    groups = defaultdict(list)
    for row in attrib:
        pressure = row.get("qualification_pressure_type") or "unknown"
        groups[pressure].append(row)
    output = []
    for pressure, group in groups.items():
        rank1 = [r for r in group if r["portfolio_name"] == "推荐组合" or str(r.get("pre_match_rank")) == "1"]
        conservative = [r for r in group if r["portfolio_style"] == "Conservative"]
        aggressive = [r for r in group if r["portfolio_style"] == "Aggressive"]
        tail = [r for r in group if r["portfolio_style"] == "Tail Hedge"]
        patterns = Counter()
        for r in group:
            if number(r["profit"]) < 0:
                patterns.update(r["failure_pattern"].split(";"))
        output.append({
            "match_pressure_type": pressure,
            "matches": len(set(r["match_name"] for r in group)),
            "rank1_roi": group_roi(rank1),
            "conservative_roi": group_roi(conservative),
            "aggressive_roi": group_roi(aggressive),
            "tail_hedge_roi": group_roi(tail),
            "common_failure_pattern": patterns.most_common(1)[0][0] if patterns else "-",
        })
    return output


def group_roi(rows):
    stake = sum(number(r.get("total_stake", 0)) for r in rows)
    profit = sum(number(r.get("profit", 0)) for r in rows)
    return pct(profit / stake) if stake else "-"


def write_csv(attrib, path):
    public = [
        "match_name",
        "actual_score",
        "portfolio_name",
        "portfolio_style",
        "pre_match_rank",
        "profit",
        "roi",
        "failure_pattern",
        "favorite_margin",
        "handicap_depth",
        "actual_score_covered",
        "underdog_goal_tail_included",
        "draw_path_included",
        "qualification_pressure_type",
        "recommended_fix",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=public)
        writer.writeheader()
        for row in attrib:
            writer.writerow({key: row.get(key, "") for key in public})


def write_md(rows, attrib, path):
    total_stake = sum(number(r["total_stake"]) for r in rows)
    total_profit = sum(number(r["net_profit"]) for r in rows)
    win_rate = sum(1 for r in rows if number(r["net_profit"]) > 0) / len(rows) if rows else 0
    rank_fail = rank1_failures(attrib)
    style_rows = aggregate(rows, style_name)
    style_table = [
        {
            "portfolio_style": item["portfolio_style"],
            "matches_count": item["matches_count"],
            "total_stake": f"{item['total_stake']:.0f}",
            "total_profit": money(item["total_profit"]),
            "roi": pct(item["roi"]),
            "win_rate": pct(item["win_rate"]),
            "average_profit": money(item["average_profit"]),
            "max_loss": money(item["max_loss"]),
            "best_match": item["best_match"],
            "worst_match": item["worst_match"],
        }
        for item in style_rows
    ]
    pattern_counts = Counter()
    for row in attrib:
        if number(row["profit"]) < 0:
            pattern_counts.update(row["failure_pattern"].split(";"))
    rank_failure_table = []
    for row in rank_fail:
        rank_failure_table.append({
            "match_name": row["match_name"],
            "actual_score": row["actual_score"],
            "portfolio": row["portfolio_name"],
            "style": row["portfolio_style"],
            "profit": row["profit"],
            "roi": row["roi"],
            "patterns": row["failure_pattern"],
        })
    deep_failures = [
        row for row in rank_fail
        if "favorite_won_but_failed_handicap" in row["failure_pattern"]
    ]
    underdog_goal = [
        row for row in rank_fail
        if "underdog_goal_broke_clean_sheet" in row["failure_pattern"]
    ]
    draw_fail = [
        row for row in rank_fail
        if "draw_path_missed" in row["failure_pattern"]
    ]
    pressure_rows = pressure_summary(attrib)
    my_rows = my_vs_system(attrib)
    best_style = style_rows[0]["portfolio_style"] if style_rows else "-"
    worst_style = sorted(style_rows, key=lambda x: x["total_profit"])[0]["portfolio_style"] if style_rows else "-"
    lines = [
        "# Backtest Attribution Review 20260625",
        "",
        "## Executive Summary",
        "",
        f"- Reviewed: `{SUMMARY_MD}` and `{RESULTS_CSV}`",
        f"- Total matches: {len(set(r['match_name'] for r in rows))}",
        f"- Portfolio rows: {len(rows)}",
        f"- Total stake: {total_stake:.0f}",
        f"- Net profit: {money(total_profit)}",
        f"- Total ROI: {pct(total_profit / total_stake if total_stake else 0)}",
        f"- Win rate: {pct(win_rate)}",
        f"- Rank #1 losing rows: {len(rank_fail)}",
        f"- Best style by total profit: {best_style}",
        f"- Worst style by total profit: {worst_style}",
        "",
        "Main conclusion: the first negative ROI is mainly explained by zero-risk portfolio collapse, one-goal handicap deviation, and draw/adjacent paths not being covered. This report is attribution only; no weights were changed.",
        "",
        "## Overall Results",
        "",
        "- Backtest matches: 17",
        "- Portfolio rows: 161",
        "- Overall ROI from source summary: -13.8%",
        "- Recomputed total ROI from CSV: " + pct(total_profit / total_stake if total_stake else 0),
        "",
        "## Portfolio Style Performance",
        "",
        markdown_table(style_table, ["portfolio_style", "matches_count", "total_stake", "total_profit", "roi", "win_rate", "average_profit", "max_loss", "best_match", "worst_match"]),
        "",
        "## Rank #1 Failure Review",
        "",
        markdown_table(rank_failure_table, ["match_name", "actual_score", "portfolio", "style", "profit", "roi", "patterns"]) if rank_failure_table else "- No Rank #1 failures.",
        "",
        "## Strong Favorite Not Covering Review",
        "",
        f"- Rank #1 deep/handicap related failures: {len(deep_failures)}",
        "- This pattern indicates that deep or margin-sensitive assets need review before any further score tuning.",
        "",
        "Affected rows:",
        "",
        markdown_table(deep_failures[:20], ["match_name", "actual_score", "portfolio_name", "profit", "handicap_depth", "actual_score_covered", "recommended_fix"]) if deep_failures else "- None.",
        "",
        "## Underdog Goal Tail Review",
        "",
        f"- Rank #1 failures with clean-sheet score exposure broken by underdog goal: {len(underdog_goal)}",
        "- Recommendation direction: review 2:1 / 3:1 / 1:1 tails when the underdog has must-score motivation or late volatility.",
        "",
        markdown_table(underdog_goal[:20], ["match_name", "actual_score", "portfolio_name", "profit", "underdog_goal_tail_included", "recommended_fix"]) if underdog_goal else "- None.",
        "",
        "## Draw Path Review",
        "",
        f"- Rank #1 draw-path failures: {len(draw_fail)}",
        "- Recommendation direction: review draw / under / 1:1 / 0:0 coverage in both-draw-acceptable and direct qualification battle matches.",
        "",
        markdown_table(draw_fail[:20], ["match_name", "actual_score", "portfolio_name", "profit", "draw_path_included", "recommended_fix"]) if draw_fail else "- None.",
        "",
        "## Qualification Pressure Review",
        "",
        markdown_table(pressure_rows, ["match_pressure_type", "matches", "rank1_roi", "conservative_roi", "aggressive_roi", "tail_hedge_roi", "common_failure_pattern"]),
        "",
        "Current evidence is partial because many historical snapshots were generated before full pressure metadata was saved. Where pressure type is missing, the report marks it as `unknown`.",
        "",
        "## My Portfolio vs System",
        "",
        markdown_table(my_rows, ["match_name", "my_portfolio_profit", "system_rank1_profit", "difference", "winner", "reason"]) if my_rows else "- No comparable My Portfolio rows found.",
        "",
        "## Failure Pattern Frequency",
        "",
    ]
    for name, count in pattern_counts.most_common():
        lines.append(f"- {name}: {count}")
    lines += [
        "",
        "## Tuning Recommendations",
        "",
        "1. Reduce deep handicap preference when a favorite is already qualified, draw acceptable, or favorite win margin is not required.",
        "   Evidence: one-goal deviation and handicap-related failures appear repeatedly in Rank #1 losing rows.",
        "",
        "2. Increase underdog-goal tail review when the underdog must win or the favorite may rotate/control tempo.",
        "   Evidence: clean-sheet correct-score concentration can lose when actual score includes an underdog goal.",
        "",
        "3. Improve draw coverage when both teams can accept a draw or qualification battle incentives reduce early tempo.",
        "   Evidence: draw-path failures exist and current pressure metadata is incomplete in older snapshots.",
        "",
        "4. Limit correct-score concentration when the portfolio contains only clean-sheet favorite scores.",
        "   Evidence: correct-score over-concentration appears as a recurring losing-row label.",
        "",
        "5. Review Coverage Efficiency thresholds only after inspecting per-match rows, not from aggregate ROI alone.",
        "",
        "## What Not To Change Yet",
        "",
        "- Do not change Portfolio Score weights from this report alone.",
        "- Do not remove Tail Hedge or Aggressive portfolios before comparing per-pressure-type samples.",
        "- Do not assume Qualification Pressure failed where historical pressure metadata is missing.",
        "- Do not tune correct-score probabilities until more post-match samples are reviewed.",
        "- Do not add new data sources for this attribution round.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    rows = read_rows()
    posts = post_snapshots()
    attrib = attribution_rows(rows, posts)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORT_DIR / "backtest_attribution_20260625.csv"
    md_path = REPORT_DIR / "backtest_attribution_20260625.md"
    write_csv(attrib, csv_path)
    write_md(rows, attrib, md_path)
    rank_fail = rank1_failures(attrib)
    pattern_counts = Counter()
    for row in attrib:
        if number(row["profit"]) < 0:
            pattern_counts.update(row["failure_pattern"].split(";"))
    style_rows = aggregate(rows, style_name)
    print(f"Attribution rows: {len(attrib)}")
    print(f"Rank #1 failures: {len(rank_fail)}")
    print("Top failure patterns:")
    for name, count in pattern_counts.most_common(8):
        print(f"- {name}: {count}")
    if style_rows:
        print(f"Best style: {style_rows[0]['portfolio_style']} ({style_rows[0]['total_profit']:.0f})")
        worst = sorted(style_rows, key=lambda item: item["total_profit"])[0]
        print(f"Worst style: {worst['portfolio_style']} ({worst['total_profit']:.0f})")
    print(f"Report: {md_path}")
    print(f"CSV: {csv_path}")


if __name__ == "__main__":
    main()
