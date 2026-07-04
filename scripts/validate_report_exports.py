from datetime import datetime
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.betting_opinion import build_betting_opinion
from modules.market_utils import identify_handicap_center, identify_total_center
from modules.report_generator import build_report, save_report, fixture_metadata
from modules.value_model import analyze_value
from modules.worldcup_db import db_api_football_data, db_odds, db_polymarket, load_match_database


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "validation"
MATCHES = [
    {"home_cn": "Turkey", "away_cn": "United States", "home_en": "Turkiye", "away_en": "USA", "display_name": "Turkey vs United States"},
    {"home_cn": "Ecuador", "away_cn": "Germany", "home_en": "Ecuador", "away_en": "Germany", "display_name": "Ecuador vs Germany"},
    {"home_cn": "Curaçao", "away_cn": "Ivory Coast", "home_en": "Curacao", "away_en": "Ivory Coast", "display_name": "Curaçao vs Ivory Coast"},
    {"home_cn": "Japan", "away_cn": "Sweden", "home_en": "Japan", "away_en": "Sweden", "display_name": "Japan vs Sweden"},
    {"home_cn": "Tunisia", "away_cn": "Netherlands", "home_en": "Tunisia", "away_en": "Netherlands", "display_name": "Tunisia vs Netherlands"},
    {"home_cn": "Paraguay", "away_cn": "Australia", "home_en": "Paraguay", "away_en": "Australia", "display_name": "Paraguay vs Australia"},
]


def ok(value):
    return "PASS" if value else "FAIL"


def contains_any(text, values):
    return any(value in text for value in values)


def validate_match(match):
    db = load_match_database(match, full=True)
    if not db:
        return {"match_name": match["display_name"], "issues_found": "No local database folder found."}

    api_data = db_api_football_data(db)
    odds = db_odds(db) or {}
    polymarket = db_polymarket(db) or {}
    value = analyze_value(match, odds, polymarket)
    opinion = build_betting_opinion(match, odds, polymarket, value, api_data)
    portfolio_summary = portfolio_from_database(db)
    actual_odds = (db.get("pre_match") or {}).get("actual_odds") or {}
    report = build_report(
        match=match,
        odds=odds,
        polymarket=polymarket,
        news={},
        probabilities={},
        scores=[],
        rating={},
        api_football_data=api_data,
        value_analysis=value,
        betting_opinion=opinion,
        portfolio_summary=portfolio_summary,
        actual_odds=actual_odds,
    )
    report_path = save_report(report, match, ROOT / "outputs" / "reports")

    meta = fixture_metadata(api_data, match)
    handicap = identify_handicap_center(((api_data or {}).get("asian_handicap") or {}).get("rows") or [], odds=odds, match=match)
    total = identify_total_center((odds or {}).get("over_under") or [])
    issues = []

    overview_ok = bool(meta.get("home_name") and meta.get("away_name") and not meta.get("missing"))
    if not overview_ok:
        issues.append("overview metadata incomplete: " + ",".join(meta.get("missing") or []))
    if "- vs -" in report:
        issues.append("report contains - vs -")

    checks = {
        "match_name": match["display_name"],
        "report_path": str(report_path.relative_to(ROOT)),
        "match_direction": opinion.get("match_direction"),
        "handicap_center": handicap.get("center_label"),
        "coverage_candidate": handicap.get("coverage_label"),
        "outlier_rows_filtered": handicap.get("outlier_count", 0),
        "total_center": total.get("center_label"),
        "market_bias": total.get("market_bias"),
        "overview_ok": ok(overview_ok),
        "chinese_ui_ok": ok(contains_any(report, ["## 投注观点", "## 比赛概览", "## 价值分析", "## 数据质量提示"])),
        "betting_opinion_ok": ok(contains_any(report, ["### 比赛主方向", "### 覆盖 / 保险候选", "### 进球数观点"])),
        "handicap_center_ok": ok(bool(handicap.get("available") and handicap.get("center_label"))),
        "total_center_ok": ok(bool(total.get("available") and total.get("center_label"))),
        "value_analysis_ok": ok("### 胜平负市场价值" in report and "No Significant Market Disagreement" not in report),
        "confidence_split_ok": ok("市场方向置信度" in report and "投注信心" in report and "Data Quality:" not in report),
        "data_quality_notes_ok": ok("## 数据质量提示" in report),
        "portfolio_eligibility_ok": ok("## 组合推荐资格" in report and "Available in Portfolio Ranking details" not in report),
        "portfolio_name_ok": ok("推荐组合：推荐组合" not in report and "推荐组合名称：" in report),
        "portfolio_core_bets_ok": ok("核心投注：" in report),
        "risk_gate_split_ok": ok("风险门槛结果：" in report and "风险等级：" in report),
        "handicap_name_mapping_ok": ok("盘口：Home " not in visible_handicap_section(report) and "盘口：Away " not in visible_handicap_section(report)),
        "market_details_ok": ok("<summary>完整亚洲让球明细</summary>" in report and "<summary>完整大小球明细</summary>" in report),
        "user_odds_note_ok": ok("用户真实赔率" in report),
        "issues_found": "; ".join(issues) if issues else "None",
    }
    return checks


def portfolio_from_database(db):
    pre_match = (db or {}).get("pre_match") or {}
    strategies = ((pre_match.get("strategy_snapshot") or {}).get("strategies")) or []
    if strategies:
        return strategies[0]
    portfolios = pre_match.get("portfolios") or []
    if not portfolios:
        return None
    portfolio = dict(portfolios[0])
    portfolio.setdefault("rank_name", portfolio.get("name") or "数据库推荐组合")
    portfolio.setdefault("portfolio_style_label", "本地快照组合")
    portfolio.setdefault("score", portfolio.get("score") or portfolio.get("rank_score"))
    portfolio.setdefault("risk_gate", {
        "passed": True,
        "risk_level": "MEDIUM",
        "reason": "验证脚本使用本地 pre_match 快照；完整风险门槛以网页运行时组合为准。",
    })
    portfolio.setdefault("rank1_eligibility", {
        "rank1_eligible": True,
        "blockers": [],
        "summary": "Readable report validation fallback portfolio.",
    })
    return portfolio


def visible_handicap_section(report):
    start = report.find("## 亚洲让球")
    if start < 0:
        return ""
    end = report.find("<details>", start)
    if end < 0:
        end = report.find("## 大小球", start)
    return report[start:end if end > start else len(report)]


def markdown_table(rows, columns):
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "-")).replace("\n", " ") for column in columns) + " |")
    return "\n".join(lines)


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [validate_match(match) for match in MATCHES]
    columns = [
        "match_name",
        "overview_ok",
        "chinese_ui_ok",
        "betting_opinion_ok",
        "handicap_center_ok",
        "total_center_ok",
        "value_analysis_ok",
        "confidence_split_ok",
        "data_quality_notes_ok",
        "portfolio_eligibility_ok",
        "portfolio_name_ok",
        "portfolio_core_bets_ok",
        "risk_gate_split_ok",
        "handicap_name_mapping_ok",
        "market_details_ok",
        "user_odds_note_ok",
        "match_direction",
        "handicap_center",
        "coverage_candidate",
        "outlier_rows_filtered",
        "total_center",
        "issues_found",
        "report_path",
    ]
    content = [
        "# Report Export Validation",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        markdown_table(rows, columns),
        "",
    ]
    path = REPORT_DIR / f"report_export_validation_{datetime.now().strftime('%Y%m%d')}.md"
    path.write_text("\n".join(content), encoding="utf-8")
    readability_path = REPORT_DIR / "report_readability_validation_20260625.md"
    readability_path.write_text("\n".join(content), encoding="utf-8")
    print(path)
    print(readability_path)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
