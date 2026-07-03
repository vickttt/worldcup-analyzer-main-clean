from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.portfolio_engine import (
    build_core_decision_layers,
    compute_match_investment_score,
    compute_portfolio_score,
    generate_style_portfolios,
    portfolio_risk_gate,
    portfolio_style_name,
    rank1_eligibility_check,
)
from modules.market_intelligence import build_market_intelligence
from modules.probability_base import stake_from_investment_score
from modules.scenario_engine import SCENARIO_TAXONOMY, build_scenario_engine
from modules.user_portfolio_compare import build_user_portfolio_comparison, parse_user_portfolio_text


def sample_fixture():
    odds = {
        "found": True,
        "home_win": 1.80,
        "draw": 3.40,
        "away_win": 4.60,
        "match_winner_rows": [
            {"home_win": 1.80, "draw": 3.40, "away_win": 4.60},
            {"home_win": 1.85, "draw": 3.35, "away_win": 4.50},
        ],
        "over_under": [
            {"line": 2.5, "over_odds": 1.95, "under_odds": 1.90},
        ],
    }
    api_football_data = {
        "asian_handicap": {
            "status": "ok",
            "rows": [{"value": "Home -0.5", "odd": "1.91"}],
        },
        "correct_score": {
            "status": "ok",
            "rows": [{"score": "1:0", "odd": "7.5"}],
        },
    }
    return {
        "strategies": [],
        "match": {"home_cn": "主队", "away_cn": "客队"},
        "distribution": {"rows": []},
        "context": {
            "odds": odds,
            "api_football_data": api_football_data,
        },
    }


def assert_probability_contract(tpb):
    probabilities = tpb.get("probabilities") or {}
    assert tpb.get("available") is True
    assert set(probabilities) == {"home_win", "draw", "away_win"}
    assert abs(sum(probabilities.values()) - 1.0) < 0.000001
    assert tpb.get("source") == "API-Football 胜平负博彩公司共识概率"


def test_core_decision_layers_contract():
    fixture = sample_fixture()
    layers = build_core_decision_layers(
        fixture["strategies"],
        fixture["match"],
        fixture["distribution"],
        fixture["context"],
    )
    assert set(layers) == {"score_layer", "execution_layer", "explanation_layer"}

    score_layer = layers["score_layer"]
    execution_layer = layers["execution_layer"]
    explanation_layer = layers["explanation_layer"]

    assert_probability_contract(score_layer["tpb"])
    assert 0 <= score_layer["betting_confidence"] <= 100
    assert 0 <= score_layer["investment_score"] <= 100
    assert score_layer["confidence_breakdown"]["formula"] == "35 + (1 - TPB entropy) * 65"

    expected_stake = stake_from_investment_score(score_layer["investment_score"])
    assert execution_layer["stake"] == expected_stake
    assert execution_layer["recommended_bet_size"] == expected_stake["amount"]
    assert execution_layer["risk_decision"] in {"可下注", "观察", "不下注"}

    coverage = explanation_layer["coverage"]
    assert coverage["type"] in {"draw", "upset", "balanced", "none"}
    assert explanation_layer["coverage_explanation"] == coverage["reason"]
    assert "TPB信心" in explanation_layer["components"]
    assert "博彩公司一致性" in explanation_layer["components"]


def test_match_investment_score_contract():
    fixture = sample_fixture()
    result = compute_match_investment_score(
        fixture["strategies"],
        fixture["match"],
        fixture["distribution"],
        fixture["context"],
    )
    assert_probability_contract(result["true_probability_base"])
    assert 0 <= result["score"] <= 100
    assert result["coverage"]["type"] in {"draw", "upset", "balanced", "none"}
    assert result["confidence_breakdown"]["formula"] == "35 + (1 - TPB entropy) * 65"
    assert result["weights"]["TPB信心"] == "55%"
    assert result["weights"]["博彩公司一致性"] == "扣分项"


def test_legacy_portfolio_helpers_are_disabled_stubs():
    fixture = sample_fixture()
    legacy_strategy = {"items": [{"type": "legacy", "selection": "old", "amount": 100}]}

    disabled_score = compute_portfolio_score(
        legacy_strategy,
        fixture["match"],
        fixture["distribution"],
    )
    assert disabled_score["score"] == 0
    assert "旧组合评分已停用" in " ".join(disabled_score["why"])

    assert generate_style_portfolios({}, fixture["match"], fixture["distribution"]) == []
    assert portfolio_style_name({}) == "Multi-layer baseline"

    gate = portfolio_risk_gate(legacy_strategy)
    assert gate["passed"] is True
    assert gate["risk_level"] == "诊断"
    assert gate["failed_paths"] == []

    eligibility = rank1_eligibility_check(legacy_strategy)
    assert eligibility["eligible"] is True
    assert eligibility["rank1_blockers"] == []


def test_market_intelligence_contract():
    fixture = sample_fixture()
    intelligence = build_market_intelligence(
        match=fixture["match"],
        odds=fixture["context"]["odds"],
        api_football_data=fixture["context"]["api_football_data"],
    )
    assert intelligence["available"] is True
    metrics = intelligence["metrics"]
    assert metrics["directional_strength"] in {
        "Strong Direction",
        "Medium Direction",
        "Weak Direction",
    }
    assert 0 <= metrics["market_conflict_index"] <= 100
    assert metrics["market_conflict_label"] in {"低冲突", "中冲突", "高不确定性市场"}
    assert 0 <= metrics["market_efficiency_score"] <= 100
    assert metrics["volatility_index"] in {"Low", "Medium", "High"}
    assert metrics["upset_probability"] in {"Low", "Medium", "High"}

    portfolio = intelligence["system_portfolio"]
    assert set(portfolio) == {
        "main_position",
        "defensive_position",
        "tail_risk_position",
        "ranking",
    }
    assert [item["rank"] for item in portfolio["ranking"]] == [1, 2, 3]


def test_scenario_engine_contract():
    fixture = sample_fixture()
    intelligence = build_market_intelligence(
        match=fixture["match"],
        odds=fixture["context"]["odds"],
        api_football_data=fixture["context"]["api_football_data"],
    )
    scenario = build_scenario_engine(
        match=fixture["match"],
        odds=fixture["context"]["odds"],
        market_intelligence=intelligence,
    )
    assert scenario["version"] == "scenario_engine_v1"
    assert [item["code"] for item in scenario["taxonomy"]] == [code for code, _name in SCENARIO_TAXONOMY]
    distribution = scenario["probability_distribution"]
    assert [item["code"] for item in distribution] == ["S1", "S2", "S3", "S4", "S5", "S6"]
    assert abs(sum(item["probability"] for item in distribution) - 1.0) < 0.0001
    assert set(scenario["risk_surface"]) == {
        "tail_risk_concentration",
        "tail_risk_value",
        "market_fragility",
        "market_fragility_value",
        "upset_exposure",
        "upset_exposure_value",
        "draw_dependency",
        "draw_dependency_value",
    }
    assert set(scenario["coverage_map"]) == {
        "primary_coverage",
        "defensive_coverage",
        "tail_optionality",
    }
    assert set(scenario["portfolio_mapping_explanation"]) == {
        "main_position_coverage",
        "defensive_position_coverage",
        "tail_exposure",
    }
    assert "scenario-driven recommendation" in scenario["portfolio_mapping_explanation"]["main_position_coverage"]["explanation"]
    assert set(scenario["scenario_market_mapping"]) == {"S1", "S2", "S3", "S4", "S5", "S6"}
    assert 0 <= scenario["coverage_efficiency_score"] <= 100
    assert "不影响 TPB" in scenario["disclaimer"]


def test_user_portfolio_comparison_is_display_only():
    fixture = sample_fixture()
    raw_text = "独赢，主队，1.80\n让球,主队,-0.5/1,0.91\n大小球,Under,2.5/3,0.92\n波胆,1:1,6.00"
    positions, errors = parse_user_portfolio_text(raw_text)
    assert not errors
    assert len(positions) == 4
    assert positions[0]["market"] == "独赢"
    assert positions[0]["selection"] == "主队"
    assert positions[0]["handicap"] is None
    assert positions[0]["split_handicap"] is None
    assert positions[0]["is_split_line"] is False
    assert positions[0]["odds"] == 1.8
    assert positions[1]["split_handicap"] == [-0.5, -1.0]
    assert positions[1]["is_split_line"] is True
    assert positions[2]["selection"] == "Under"
    assert positions[2]["split_handicap"] == [2.5, 3.0]

    comparison = build_user_portfolio_comparison(
        raw_text,
        match=fixture["match"],
        odds=fixture["context"]["odds"],
        betting_opinion={},
        distribution=fixture["distribution"],
        api_football_data=fixture["context"]["api_football_data"],
    )
    assert comparison["has_input"] is True
    assert comparison["total_count"] == 4
    assert comparison["positions"][0]["api_reference_odds"] == 1.8
    assert comparison["positions"][0]["price_difference_pct_text"] == "+0.00%"
    assert comparison["positions"][0]["price_judgment"] == "用户赔率接近（neutral）"
    assert comparison["positions"][1]["handicap_display"] == "-0.5 / -1"
    assert comparison["positions"][2]["handicap_display"] == "2.5 / 3"
    assert comparison["positions"][2]["price_judgment"] == "无API可比（unknown）"
    assert "不参与 TPB" in comparison["disclaimer"]

    layers = build_core_decision_layers(
        fixture["strategies"],
        fixture["match"],
        fixture["distribution"],
        fixture["context"],
    )
    assert set(layers) == {"score_layer", "execution_layer", "explanation_layer"}


def test_architecture_guardrails():
    repo_root = Path(__file__).resolve().parents[1]
    agents_text = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    assert "Decision Authority Hierarchy" in agents_text
    assert "TPB Baseline Probability (anchor)" in agents_text
    assert "Market Structure Intelligence (signal layer)" in agents_text
    assert "Scenario Engine Layer (probability space decomposition and portfolio" in agents_text
    assert "System Portfolio Layer (synthesis + ranking)" in agents_text
    assert "Execution Layer (display/evaluation only)" in agents_text

    rubric_text = (repo_root / "reports" / "claude_reviews" / "CLAUDE_REVIEW_RUBRIC.md").read_text(encoding="utf-8")
    assert "TPB is not the sole system anymore" in rubric_text
    assert "System Portfolio is synthesis-based" in rubric_text
    assert "Execution Layer does not affect any upstream layer" in rubric_text
    assert "Scenario Engine is integrated into the System Portfolio explanation flow" in rubric_text
    assert "Scenario Engine is not an isolated UI module" in rubric_text

    report_text = (repo_root / "modules" / "report_generator.py").read_text(encoding="utf-8")
    for heading in [
        "## 1. Core Decision Layer",
        "## 2. Market Structure Layer",
        "## 3. Scenario Engine Layer",
        "## 4. System Portfolio Layer",
        "## 5. System Ranking",
        "## 6. Execution Layer",
    ]:
        assert heading in report_text
    assert "Scenario → Portfolio Mapping Explanation" in report_text
    assert "System Portfolio = TPB baseline + Market Structure + Scenario Engine explanation synthesis" in report_text
    assert "Ranking incorporates scenario coverage signals as explanation only" in report_text

    core_files = [
        repo_root / "modules" / "probability_base.py",
        repo_root / "modules" / "portfolio_engine.py",
        repo_root / "modules" / "market_intelligence.py",
    ]
    for file_path in core_files:
        text = file_path.read_text(encoding="utf-8")
        assert "from modules.user_portfolio_compare" not in text
        assert "build_user_portfolio_comparison" not in text
        assert "expected_value" not in text.lower()
        assert "roi_" not in text.lower()
        assert "portfolio_optimizer" not in text.lower()
        assert "scenario_engine" not in text
        assert "override_tpb" not in text.lower()
        assert "tpb_override" not in text.lower()

    intelligence_text = (repo_root / "modules" / "market_intelligence.py").read_text(encoding="utf-8")
    assert "true_probability_base" in intelligence_text
    assert "stake_from_investment_score" not in intelligence_text
    assert "recommended_stake" not in intelligence_text
    assert "user_portfolio" not in intelligence_text
    assert "System 层才综合 TPB baseline 与结构信号" in intelligence_text

    scenario_text = (repo_root / "modules" / "scenario_engine.py").read_text(encoding="utf-8")
    assert "SCENARIO_TAXONOMY" in scenario_text
    assert "portfolio_mapping_explanation" in scenario_text
    assert "stake_from_investment_score" not in scenario_text
    assert "build_user_portfolio_comparison" not in scenario_text
    assert "expected_value" not in scenario_text.lower()
    assert "roi_" not in scenario_text.lower()
    assert "portfolio_optimizer" not in scenario_text.lower()

    user_layer_text = (repo_root / "modules" / "user_portfolio_compare.py").read_text(encoding="utf-8")
    assert "true_probability_base" not in user_layer_text
    assert "investment_score" not in user_layer_text
    assert "stake_from_investment_score" not in user_layer_text


def run():
    test_core_decision_layers_contract()
    test_match_investment_score_contract()
    test_legacy_portfolio_helpers_are_disabled_stubs()
    test_market_intelligence_contract()
    test_scenario_engine_contract()
    test_user_portfolio_comparison_is_display_only()
    test_architecture_guardrails()
    print("Multi-layer betting intelligence smoke tests passed.")


if __name__ == "__main__":
    run()
