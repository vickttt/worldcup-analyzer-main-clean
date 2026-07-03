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
from modules.probability_base import stake_from_investment_score
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
    assert portfolio_style_name({}) == "TPB 单一决策"

    gate = portfolio_risk_gate(legacy_strategy)
    assert gate["passed"] is True
    assert gate["risk_level"] == "诊断"
    assert gate["failed_paths"] == []

    eligibility = rank1_eligibility_check(legacy_strategy)
    assert eligibility["eligible"] is True
    assert eligibility["rank1_blockers"] == []


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
    assert comparison["observation_rows"][0]["对象"] == "系统 TPB 输出"
    assert comparison["positions"][0]["api_reference_odds"] == 1.8
    assert comparison["positions"][0]["price_judgment"] == "接近"
    assert comparison["positions"][1]["handicap_display"] == "-0.5 / -1"
    assert comparison["positions"][2]["handicap_display"] == "2.5 / 3"
    assert comparison["positions"][2]["price_judgment"] == "暂无可比 API 赔率"
    assert "不参与 TPB" in comparison["disclaimer"]

    layers = build_core_decision_layers(
        fixture["strategies"],
        fixture["match"],
        fixture["distribution"],
        fixture["context"],
    )
    assert set(layers) == {"score_layer", "execution_layer", "explanation_layer"}


def run():
    test_core_decision_layers_contract()
    test_match_investment_score_contract()
    test_legacy_portfolio_helpers_are_disabled_stubs()
    test_user_portfolio_comparison_is_display_only()
    print("TPB-only portfolio engine smoke tests passed.")


if __name__ == "__main__":
    run()
