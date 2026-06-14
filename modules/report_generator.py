from datetime import datetime
from pathlib import Path


def percent(value):
    return f"{value * 100:.1f}%"


def build_report(match, odds, polymarket, news, probabilities, scores, rating):
    if polymarket.get("found", True):
        polymarket_lines = [
            f"- Polymarket来源：{polymarket['source']}",
            f"- Polymarket事件：{polymarket.get('event_title')}",
            f"- Polymarket链接：{polymarket.get('event_url')}",
            f"- {match['home_cn']}胜价格：{polymarket['home_win']}",
            f"- 平局价格：{polymarket['draw']}",
            f"- {match['away_cn']}胜价格：{polymarket['away_win']}",
            f"- 成交量：{polymarket['volume']}",
            f"- 流动性：{polymarket['liquidity']}",
        ]
    else:
        polymarket_lines = [
            f"- Polymarket来源：{polymarket['source']}",
            f"- 状态：{polymarket['message']}",
            "- 主胜价格：无",
            "- 平局价格：无",
            "- 客胜价格：无",
            "- 成交量：无",
            "- 流动性：无",
        ]

    lines = [
        f"# {match['display_name']} 分析报告",
        "",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 一、结论",
        "",
        f"机会评级：{rating['grade']}级",
        f"冷门风险：{rating['risk_level']}",
        f"核心判断：{rating['summary']}",
        "",
        "## 二、胜平负概率",
        "",
        f"- {match['home_cn']}胜：{percent(probabilities['home_win'])}",
        f"- 平局：{percent(probabilities['draw'])}",
        f"- {match['away_cn']}胜：{percent(probabilities['away_win'])}",
        "",
        "## 三、市场数据",
        "",
        f"- 国际赔率来源：{odds['source']}",
        f"- {match['home_cn']}胜赔率：{odds['home_win']}",
        f"- 平局赔率：{odds['draw']}",
        f"- {match['away_cn']}胜赔率：{odds['away_win']}",
        f"- 大小球参考线：{odds['over_under_line']}",
        "",
        *polymarket_lines,
        "",
        "## 四、新闻与伤病",
        "",
        f"{match['home_cn']}：",
        *[f"- {item}" for item in news["home"]],
        "",
        f"{match['away_cn']}：",
        *[f"- {item}" for item in news["away"]],
        "",
        "## 五、推荐比分",
        "",
        f"- 主比分：{scores['main']}",
        f"- 次比分：{scores['secondary']}",
        f"- 风险比分：{scores['risk']}",
        "",
        "## 六、风险提示",
        "",
        *[f"- {item}" for item in news["risk_flags"]],
        "",
        "说明：当前 MVP V1 的 Polymarket 数据来自真实公开 API；国际赔率、新闻和伤病仍为模拟数据，结果不构成真实投注建议。",
    ]
    return "\n".join(lines)


def save_report(report, match, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    safe_name = match["display_name"].replace(" ", "_").replace("/", "_")
    path = Path(output_dir) / f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path.write_text(report, encoding="utf-8")
    return path
