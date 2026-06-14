from pathlib import Path

import streamlit as st
import yaml

from modules.match_parser import parse_match
from modules.mock_data import get_mock_news_and_injuries, get_mock_odds
from modules.polymarket_client import fetch_polymarket
from modules.probability_model import combine_probabilities
from modules.rating_model import rate_opportunity
from modules.report_generator import build_report, save_report
from modules.score_model import recommend_scores


def load_config():
    path = Path(__file__).resolve().parent / "config.yaml"
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


config = load_config()

st.set_page_config(page_title=config["app"]["title"], layout="centered")
st.title("世界杯分析器 MVP V1")
st.caption("当前版本：Polymarket 使用真实公开数据；国际赔率、新闻和伤病仍使用模拟数据。")

match_text = st.text_input("请输入比赛名称", value="德国 vs 库拉索")

if st.button("生成测试分析报告", type="primary"):
    try:
        match = parse_match(match_text)
        odds = get_mock_odds(match)
        polymarket = fetch_polymarket(match)
        news = get_mock_news_and_injuries(match)
        probabilities = combine_probabilities(odds, polymarket, news, config)
        scores = recommend_scores(match, probabilities, odds)
        rating = rate_opportunity(probabilities, polymarket, news)
        report = build_report(match, odds, polymarket, news, probabilities, scores, rating)
        report_path = save_report(report, match, config["report"]["output_dir"])

        st.success("测试分析报告已生成")
        st.markdown(report)
        st.download_button(
            "下载 Markdown 报告",
            data=report,
            file_name=report_path.name,
            mime="text/markdown",
        )
    except Exception as error:
        st.error(str(error))
