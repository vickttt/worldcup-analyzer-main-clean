from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.portfolio_engine import (
    build_bet_id,
    build_score_scenario_grid,
    classify_scenario,
    compute_coverage_efficiency,
    compute_directional_odds_value,
    compute_match_investment_score,
    compute_portfolio_marginal_utility,
    compute_portfolio_pnl_by_score,
    compute_portfolio_score,
    correct_score_exposure_control,
    dedupe_bets,
    dedupe_portfolios,
    generate_style_portfolios,
    normalize_handicap_line,
    portfolio_risk_gate,
    rank1_eligibility_check,
    strategy_pressure_fit,
    settle_asian_handicap,
)
from modules.game_behavior_engine import build_match_context, game_behavior_engine, seed_pressure_context
from modules.market_utils import identify_handicap_center, identify_total_center
from modules.result_distribution import build_result_distribution


def assert_close(left, right, tolerance=0.001):
    assert abs(left - right) <= tolerance, f"{left} != {right}"


def test_handicap_normalization():
    cases = {
        "-1/2": (-0.5, [-0.5]),
        "-0.5/1": (-0.75, [-0.5, -1.0]),
        "-1/1.5": (-1.25, [-1.0, -1.5]),
        "-1.5/2": (-1.75, [-1.5, -2.0]),
        "-2/2.5": (-2.25, [-2.0, -2.5]),
        "-2.5/3": (-2.75, [-2.5, -3.0]),
        "+1/1.5": (1.25, [1.0, 1.5]),
        "+0.5/1": (0.75, [0.5, 1.0]),
        "+1/2": (0.5, [0.5]),
        "+1.5/2": (1.75, [1.5, 2.0]),
        "+2/2.5": (2.25, [2.0, 2.5]),
        "+2.5/3": (2.75, [2.5, 3.0]),
    }
    for raw, (expected, legs) in cases.items():
        parsed = normalize_handicap_line(raw)
        assert_close(parsed["decimal_line"], expected)
        assert len(parsed["split_legs"]) == len(legs)
        for left, right in zip(parsed["split_legs"], legs):
            assert_close(left, right)


def test_asian_handicap_settlement():
    line = normalize_handicap_line("-1/1.5")
    assert_close(settle_asian_handicap("2:0", "home", line["split_legs"], 2.05, 100), 105)
    assert_close(settle_asian_handicap("1:0", "home", line["split_legs"], 2.05, 100), -50)
    assert_close(settle_asian_handicap("0:0", "home", line["split_legs"], 2.05, 100), -100)

    deep = normalize_handicap_line("-2.5/3")
    assert_close(settle_asian_handicap("4:0", "home", deep["split_legs"], 2.01, 100), 101)
    assert_close(settle_asian_handicap("3:0", "home", deep["split_legs"], 2.01, 100), 50.5)
    assert_close(settle_asian_handicap("2:0", "home", deep["split_legs"], 2.01, 100), -100)

    away = normalize_handicap_line("+2/2.5")
    assert_close(settle_asian_handicap("2:0", "away", away["split_legs"], 1.90, 100), 45)
    assert_close(settle_asian_handicap("3:0", "away", away["split_legs"], 1.90, 100), -100)


def test_bet_and_portfolio_dedupe():
    first = {"type": "handicap", "selection": "Home -1/1.5", "standard_odds": 2.0, "score": 60, "roles": ["direction"]}
    second = {"type": "handicap", "selection": "Home -1.25", "standard_odds": 2.0, "score": 70, "roles": ["insurance"]}
    assert build_bet_id(first) == build_bet_id(second)
    deduped_bets = dedupe_bets([first, second])
    assert len(deduped_bets) == 1
    assert set(deduped_bets[0]["roles"]) == {"direction", "insurance"}
    portfolios = [
        {"name": "A", "items": [first], "score": 60},
        {"name": "B", "items": [second], "score": 80},
    ]
    deduped = dedupe_portfolios(portfolios)
    assert len(deduped) == 1
    assert deduped[0]["name"] == "B"


def test_portfolio_score_not_always_100_and_noise_filter():
    match = {"home_cn": "主队", "away_cn": "客队"}
    distribution = {"favorite": "主队", "main_path": "热门方赢2球"}
    items = [
        {"type": "handicap", "selection": "Home -1/1.5", "standard_odds": 2.0, "odds": 2.0, "amount": 800},
        {"type": "correct_score", "selection": "2:0", "standard_odds": 6.0, "odds": 6.2, "amount": 200, "edge": 0.03},
        {"type": "correct_score", "selection": "1:4", "standard_odds": 80.0, "odds": 120.0, "amount": 100, "edge": 0.50},
    ]
    score_rows = [
        {"比分": "2:0", "_total": 760, "_probability": 0.32},
        {"比分": "1:0", "_total": -500, "_probability": 0.18},
        {"比分": "3:0", "_total": 800, "_probability": 0.16},
        {"比分": "1:4", "_total": 11900, "_probability": 0.01},
    ]
    strategy = {
        "items": items,
        "score_rows": score_rows,
        "expected_yield": 0.04,
        "volatility": 550,
        "max_loss": 1100,
        "consistency_score": 0.70,
        "direction_alignment": 0.80,
        "strategic_value": 0.75,
    }
    result = compute_portfolio_score(strategy, match, distribution)
    assert 0 < result["score"] < 100
    assert result["directional_odds_value"]["weighted_edge"] < 0.20


def test_score_grid_and_candidate_efficiency():
    match_context = {
        "match": {"home_cn": "Spain", "away_cn": "Saudi Arabia"},
        "distribution": {"favorite": "Spain", "main_path": "热门方3球以上"},
    }
    odds_data = {
        "correct_score": {
            "rows": [
                {"score": "3:0", "odd": 6.0},
                {"score": "4:0", "odd": 8.0},
                {"score": "2:0", "odd": 9.0},
                {"score": "2:3", "odd": 80.0},
            ]
        }
    }
    grid = build_score_scenario_grid(match_context, odds_data)
    assert grid
    assert classify_scenario("3:0", match_context)["is_main_scenario"]
    assert classify_scenario("2:0", match_context)["is_adjacent_scenario"]
    assert classify_scenario("2:3", match_context)["is_noise_scenario"]
    base = [
        {"type": "handicap", "selection": "Home -2.5", "standard_odds": 2.0, "amount": 800},
        {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "amount": 100},
        {"type": "correct_score", "selection": "4:0", "standard_odds": 8.0, "amount": 100},
    ]
    pnl_rows = compute_portfolio_pnl_by_score({"items": base}, grid)
    assert any(row["score"] == "2:0" and row["profit"] < 0 for row in pnl_rows)
    candidate = {"type": "handicap", "selection": "Home -2", "standard_odds": 1.70, "amount": 200}
    efficiency = compute_coverage_efficiency(base, candidate, grid)
    assert efficiency["score"] >= 0
    assert efficiency["recommendation"] in {"Add", "Replace", "Add Small Stake", "Do Not Add"}
    assert efficiency["ev_delta"] is not None
    assert efficiency["roi_delta"] is not None


def _spain_context():
    return {
        "match": {"home_cn": "Spain", "away_cn": "Saudi Arabia"},
        "distribution": {"favorite": "Spain", "main_path": "热门方3球以上"},
    }


def _score_grid():
    odds_data = {
        "correct_score": {
            "rows": [
                {"score": "3:0", "odd": 6.0},
                {"score": "4:0", "odd": 8.0},
                {"score": "2:0", "odd": 9.0},
                {"score": "3:1", "odd": 10.0},
                {"score": "2:3", "odd": 80.0},
            ]
        },
        "handicap": {"line": -2.5},
        "totals": {"line": 3.5, "side": "over"},
    }
    return build_score_scenario_grid(_spain_context(), odds_data)


def _portfolio_score(name, items, expected_yield=0.04):
    context = _spain_context()
    grid = _score_grid()
    pnl_rows = compute_portfolio_pnl_by_score({"items": items}, grid)
    score_rows = [
        {"score": row["score"], "比分": row["score"], "_total": row["profit"], "_probability": row["scenario_weight"]}
        for row in pnl_rows
    ]
    strategy = {
        "name": name,
        "items": items,
        "score_rows": score_rows,
        "expected_yield": expected_yield,
        "volatility": 520,
        "max_loss": abs(min([row["profit"] for row in pnl_rows] or [0])),
        "consistency_score": 0.78,
        "direction_alignment": 0.82,
        "strategic_value": 0.78,
    }
    result = compute_portfolio_score(strategy, context["match"], context["distribution"])
    return {"name": name, **result}


def test_coverage_efficiency_cases():
    grid = _score_grid()
    cases = [
        (
            "Spain deep handicap insurance",
            [
                {"type": "handicap", "selection": "Home -2.5", "standard_odds": 2.0, "amount": 800},
                {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "amount": 100},
                {"type": "correct_score", "selection": "4:0", "standard_odds": 8.0, "amount": 100},
            ],
            {"type": "handicap", "selection": "Home -2", "standard_odds": 1.70, "amount": 200},
            {"Add", "Replace", "Add Small Stake"},
        ),
        (
            "Germany one-goal tolerance",
            [
                {"type": "handicap", "selection": "Home -1.5", "standard_odds": 2.0, "amount": 700},
                {"type": "correct_score", "selection": "2:0", "standard_odds": 6.0, "amount": 100},
                {"type": "correct_score", "selection": "3:0", "standard_odds": 8.0, "amount": 100},
                {"type": "correct_score", "selection": "3:1", "standard_odds": 9.0, "amount": 100},
            ],
            {"type": "handicap", "selection": "Home -1", "standard_odds": 1.65, "amount": 200},
            {"Add", "Replace", "Add Small Stake"},
        ),
        (
            "Noise correct score",
            [
                {"type": "handicap", "selection": "Home -2.5", "standard_odds": 2.0, "amount": 800},
                {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "amount": 100},
                {"type": "correct_score", "selection": "4:0", "standard_odds": 8.0, "amount": 100},
            ],
            {"type": "correct_score", "selection": "2:3", "standard_odds": 80.0, "amount": 100},
            {"Do Not Add"},
        ),
    ]
    print("\nCoverage Efficiency Cases")
    for name, base, candidate, expected in cases:
        result = compute_coverage_efficiency(base, candidate, grid)
        print(
            name,
            {
                "recommendation": result["recommendation"],
                "ev_delta": round(result["ev_delta"], 2),
                "roi_delta": round(result["roi_delta"], 4),
                "zero_risk_delta": round(result["zero_risk_delta"], 4),
                "one_goal_reduction": round(result["one_goal_deviation_risk_reduction"], 4),
                "score": result["coverage_efficiency_score"],
            },
        )
        assert result["ev_delta"] is not None
        assert result["roi_delta"] is not None
        assert result["recommendation"] in expected


def test_actual_odds_ab_ranking():
    main_plain = _portfolio_score(
        "Main Scenario Portfolio",
        [
            {"type": "handicap", "selection": "Home -2.5", "standard_odds": 2.0, "amount": 700, "edge": -0.02},
            {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "amount": 150, "edge": -0.03},
            {"type": "correct_score", "selection": "4:0", "standard_odds": 8.0, "amount": 150, "edge": 0.00},
        ],
        expected_yield=0.02,
    )
    conservative_plain = _portfolio_score(
        "Conservative Portfolio",
        [
            {"type": "handicap", "selection": "Home -2", "standard_odds": 1.70, "amount": 900, "edge": 0.00},
            {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "amount": 100, "edge": 0.00},
        ],
        expected_yield=0.03,
    )
    before = sorted([main_plain, conservative_plain], key=lambda row: row["score"], reverse=True)

    main_better = _portfolio_score(
        "Main Scenario Portfolio",
        [
            {"type": "handicap", "selection": "Home -2.5", "standard_odds": 2.0, "amount": 700, "edge": 0.10, "actual_odds": 2.20},
            {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "amount": 150, "edge": -0.03},
            {"type": "correct_score", "selection": "4:0", "standard_odds": 8.0, "amount": 150, "edge": 0.00},
        ],
        expected_yield=0.08,
    )
    conservative_after = _portfolio_score(
        "Conservative Portfolio",
        [
            {"type": "handicap", "selection": "Home -2", "standard_odds": 1.70, "amount": 900, "edge": 0.00},
            {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "amount": 100, "edge": 0.00},
        ],
        expected_yield=0.03,
    )
    after = sorted([main_better, conservative_after], key=lambda row: row["score"], reverse=True)

    noise_strategy = _portfolio_score(
        "Noise Saudi Portfolio",
        [
            {"type": "correct_score", "selection": "2:3", "standard_odds": 80.0, "amount": 300, "edge": 0.60, "actual_odds": 128},
            {"type": "winner", "selection": "Saudi win", "standard_odds": 20.0, "amount": 300, "edge": 0.45, "actual_odds": 29},
        ],
        expected_yield=0.10,
    )
    directional = compute_directional_odds_value(noise_strategy["items"], _spain_context()["match"], _spain_context()["distribution"])
    print("\nA/B Ranking Cases")
    print("Before:", [(row["name"], row["score"]) for row in before])
    print("After:", [(row["name"], row["score"]) for row in after])
    print("Noise:", noise_strategy["score"], directional["weighted_edge"], directional["ignored_noise_edges"])
    assert before[0]["name"] != after[0]["name"] or after[0]["score"] > before[0]["score"]
    assert directional["weighted_edge"] < 0.05
    assert directional["ignored_noise_edges"]


def test_correct_score_max_four_and_user_penalty():
    context = _spain_context()
    combo = [
        {"type": "winner", "selection": "Spain", "name": "Spain Win", "recommended": True, "standard_odds": 1.20, "score": 80},
        {"type": "handicap", "selection": "Home -2.5", "name": "Spain -2.5", "recommended": True, "standard_odds": 2.0, "score": 82},
        {"type": "total", "selection": "Over 3.5", "name": "Over 3.5", "recommended": True, "standard_odds": 1.90, "score": 76},
    ]
    for score, value in [("3:0", 85), ("4:0", 80), ("2:0", 78), ("3:1", 75), ("5:0", 70), ("4:1", 68)]:
        combo.append({"type": "correct_score", "selection": score, "name": score, "recommended": True, "standard_odds": 8.0, "score": value})
    portfolios = generate_style_portfolios(combo, context["match"], context["distribution"])
    print("\nCorrect Score Count Scan")
    for portfolio in portfolios:
        count = len([item for item in portfolio["items"] if item.get("type") == "correct_score"])
        print(portfolio["name"], count, "PASS" if count <= 4 else "FAIL")
        assert count <= 4
    user_strategy = _portfolio_score(
        "User Five Correct Scores",
        [
            {"type": "correct_score", "selection": score, "standard_odds": 8.0, "amount": 100, "edge": 0.02}
            for score in ["3:0", "4:0", "2:0", "3:1", "5:0"]
        ],
        expected_yield=0.02,
    )
    assert user_strategy["score_components"]["Simplicity"] < 100


def test_match_investment_score_data_quality():
    strategy = _portfolio_score(
        "Main Scenario Portfolio",
        [
            {"type": "handicap", "selection": "Home -2.5", "standard_odds": 2.0, "amount": 700, "edge": 0.05, "actual_odds": 2.10},
            {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "amount": 150, "edge": 0.02, "actual_odds": 6.20},
        ],
        expected_yield=0.06,
    )
    complete = compute_match_investment_score(
        [strategy],
        _spain_context()["match"],
        _spain_context()["distribution"],
        {
            "polymarket": {"found": True, "home_win": 0.78, "draw": 0.14, "away_win": 0.08},
            "odds": {"home_win": 1.25, "draw": 6.0, "away_win": 15.0, "over_under": [{"line": 3.5}]},
            "api_football_data": {
                "asian_handicap": {"rows": [{"line": -2.5}]},
                "correct_score": {"rows": [{"score": "3:0"}]},
            },
        },
    )
    incomplete = compute_match_investment_score(
        [strategy],
        _spain_context()["match"],
        _spain_context()["distribution"],
        {
            "polymarket": {"found": True, "home_win": 0.78},
            "odds": {"home_win": 1.25, "draw": 6.0, "away_win": 15.0},
            "api_football_data": {"asian_handicap": {"rows": []}, "correct_score": {"rows": []}},
        },
    )
    print("\nMatch Investment Score")
    print("Complete:", complete)
    print("Incomplete:", incomplete)
    assert complete["components"]["External Risk"] <= 100
    assert complete["weights"]["External Risk"] == "10%"
    assert complete["weights"]["Data Quality / Timing"] == "5%"
    assert incomplete["components"]["Data Quality / Timing"] < complete["components"]["Data Quality / Timing"]


def _row_probability(distribution, keyword):
    for row in distribution.get("rows") or []:
        if keyword in row.get("label", ""):
            return row.get("probability", 0)
    return 0


def test_game_behavior_engine_pressure_adjustments():
    odds = {
        "found": True,
        "implied_probabilities": {"home_win": 0.70, "draw": 0.18, "away_win": 0.12},
        "asian_handicap": [{"line": -1.5}],
        "over_under": [{"line": 2.5, "over_odds": 1.95, "under_odds": 1.95}],
    }
    poly = {"found": False}
    match = {"home_cn": "Spain", "away_cn": "Saudi Arabia"}
    neutral = build_result_distribution(match, odds, poly, {"team_a_pressure": 3, "team_b_pressure": 3, "group_stage": True})
    rotation = build_result_distribution(
        match,
        odds,
        poly,
        {"team_a_pressure": 1, "team_b_pressure": 3, "group_stage": True, "qualified_already": True},
    )
    must_win = build_result_distribution(
        match,
        odds,
        poly,
        {"team_a_pressure": 5, "team_b_pressure": 4, "group_stage": True, "goal_difference_pressure": 0.8},
    )
    print("\nGame Behavior Engine")
    print("Rotation:", rotation["game_behavior"])
    print("Must win:", must_win["game_behavior"])
    assert rotation["game_behavior"]["expected_handicap_movement_bias"].startswith("reduce deep favorite handicap")
    assert _row_probability(rotation, "小胜") > _row_probability(neutral, "小胜")
    assert _row_probability(rotation, "3球以上") < _row_probability(neutral, "3球以上")
    assert must_win["game_behavior"]["expected_game_tempo"] in {"high variance / open", "slightly open"}
    assert _row_probability(must_win, "3球以上") >= _row_probability(neutral, "3球以上")
    behavior = game_behavior_engine({"team_a_pressure": 0, "team_b_pressure": 5, "group_stage": True})
    assert behavior["expected_upset_probability_change"] > 0


def test_qualification_seed_germany_ecuador():
    match = {"home_en": "Ecuador", "away_en": "Germany", "home_cn": "Ecuador", "away_cn": "Germany"}
    context = build_match_context({}, match=match)
    behavior = game_behavior_engine(context)
    assert context["home_pressure_score"] == 4
    assert context["away_pressure_score"] == 1
    assert context["match_pressure_type"] == "qualified_favorite_vs_must_win_underdog"
    assert behavior["behavior_adjustments"]["deep_handicap_risk_delta"] == 2
    assert behavior["behavior_adjustments"]["underdog_goal_weight_delta"] == 2
    assert behavior["behavior_adjustments"]["favorite_small_win_weight_delta"] == 2
    odds = {
        "found": True,
        "implied_probabilities": {"home_win": 0.18, "draw": 0.18, "away_win": 0.64},
        "asian_handicap": [{"line": 1.5}],
        "over_under": [{"line": 2.5, "over_odds": 1.95, "under_odds": 1.95}],
    }
    pressured = build_result_distribution(match, odds, {"found": False}, context)
    neutral = build_result_distribution(match, odds, {"found": False}, {"team_a_pressure": 3, "team_b_pressure": 3})
    assert _row_probability(pressured, "小胜") > _row_probability(neutral, "小胜")
    assert _row_probability(pressured, "不败") >= _row_probability(neutral, "不败")
    conservative = strategy_pressure_fit(
        [
            {"type": "handicap", "selection": "Away -1", "amount": 800},
            {"type": "correct_score", "selection": "1:2", "amount": 100},
        ],
        match,
        pressured,
    )
    aggressive = strategy_pressure_fit(
        [
            {"type": "handicap", "selection": "Away -2.5", "amount": 800},
            {"type": "correct_score", "selection": "0:4", "amount": 100},
        ],
        match,
        pressured,
    )
    assert conservative["score"] > aggressive["score"]


def test_qualification_seed_switzerland_canada_draw_under():
    match = {"home_en": "Switzerland", "away_en": "Canada", "home_cn": "Switzerland", "away_cn": "Canada"}
    context = build_match_context({}, match=match)
    behavior = game_behavior_engine(context)
    assert context["match_pressure_type"] == "both_draw_acceptable"
    assert behavior["behavior_adjustments"]["draw_weight_delta"] == 2
    assert behavior["behavior_adjustments"]["under_weight_delta"] == 2
    odds = {
        "found": True,
        "implied_probabilities": {"home_win": 0.36, "draw": 0.32, "away_win": 0.32},
        "asian_handicap": [{"line": -0.25}],
        "over_under": [{"line": 2.5, "over_odds": 2.05, "under_odds": 1.82}],
    }
    distribution = build_result_distribution(match, odds, {"found": False}, context)
    assert _row_probability(distribution, "平局") >= 0.30
    fit = strategy_pressure_fit(
        [
            {"type": "total", "selection": "Under 2.5", "amount": 600},
            {"type": "correct_score", "selection": "1:1", "amount": 100},
        ],
        match,
        distribution,
    )
    assert fit["label"] == "High"


def test_qualification_seed_bosnia_qatar_must_win():
    match = {"home_en": "Bosnia and Herzegovina", "away_en": "Qatar", "home_cn": "Bosnia", "away_cn": "Qatar"}
    context = build_match_context({}, match=match)
    behavior = game_behavior_engine(context)
    assert context["match_pressure_type"] == "must_win_vs_must_win"
    assert behavior["behavior_adjustments"]["draw_weight_delta"] == -1
    assert behavior["behavior_adjustments"]["late_goal_volatility_delta"] == 2
    assert behavior["behavior_adjustments"]["chaos_risk_delta"] == 2


def test_qualification_seed_morocco_haiti_keeps_main_direction():
    match = {"home_en": "Morocco", "away_en": "Haiti", "home_cn": "Morocco", "away_cn": "Haiti"}
    context = build_match_context({}, match=match)
    odds = {
        "found": True,
        "implied_probabilities": {"home_win": 0.78, "draw": 0.14, "away_win": 0.08},
        "asian_handicap": [{"line": -2.0}],
        "over_under": [{"line": 3.0, "over_odds": 1.96, "under_odds": 1.90}],
    }
    distribution = build_result_distribution(match, odds, {"found": False}, context)
    assert distribution["favorite"] in {"Morocco", "摩洛哥"}
    assert _row_probability(distribution, "赢3球以上") < 0.40
    assert _row_probability(distribution, "赢2球") > 0.15


def test_qualification_seed_japan_sweden_and_england_panama():
    japan = {"home_en": "Japan", "away_en": "Sweden", "home_cn": "Japan", "away_cn": "Sweden"}
    japan_context = build_match_context({}, match=japan)
    assert japan_context["match_pressure_type"] == "direct_second_place_battle"
    japan_behavior = game_behavior_engine(japan_context)
    assert japan_behavior["behavior_adjustments"]["draw_weight_delta"] == 1
    assert japan_behavior["behavior_adjustments"]["underdog_goal_weight_delta"] == 1

    england = {"home_en": "Panama", "away_en": "England", "home_cn": "Panama", "away_cn": "England"}
    england_context = build_match_context({}, match=england)
    england_behavior = game_behavior_engine(england_context)
    assert england_context["match_pressure_type"] == "favorite_must_win"
    assert england_behavior["behavior_adjustments"]["favorite_small_win_weight_delta"] == 1
    assert england_behavior["behavior_adjustments"]["underdog_goal_weight_delta"] == 1


def test_match_context_from_api_football_standings():
    api_football_data = {
        "fixture": {
            "raw": {
                "league": {
                    "round": "Group Stage - 3",
                    "id": 1,
                    "season": 2026,
                }
            }
        },
        "fixture_result": {
            "home_team": {"id": 10, "name": "Team A"},
            "away_team": {"id": 20, "name": "Team B"},
        },
        "standings": {
            "found": True,
            "source": "API-Football / Standings",
            "groups": [
                {
                    "name": "Group A",
                    "rows": [
                        {"rank": 1, "team": {"id": 10, "name": "Team A"}, "points": 6, "goals_diff": 4, "goals_for": 5, "played": 2},
                        {"rank": 2, "team": {"id": 30, "name": "Team C"}, "points": 4, "goals_diff": 1, "goals_for": 3, "played": 2},
                        {"rank": 3, "team": {"id": 20, "name": "Team B"}, "points": 1, "goals_diff": -2, "goals_for": 1, "played": 2},
                        {"rank": 4, "team": {"id": 40, "name": "Team D"}, "points": 0, "goals_diff": -3, "goals_for": 0, "played": 2},
                    ],
                }
            ],
        },
    }
    context = build_match_context(api_football_data)
    print("\nStandings Pressure Context", context)
    assert context["team_a_pressure"] == 1
    assert context["team_b_pressure"] == 5
    assert context["elimination_risk"]
    assert context["standings_source"] == "API-Football / Standings"


def test_match_context_eliminated_from_standings():
    api_football_data = {
        "fixture": {"raw": {"league": {"round": "Group Stage - 3"}}},
        "fixture_result": {
            "home_team": {"id": 10, "name": "Team A"},
            "away_team": {"id": 20, "name": "Team B"},
        },
        "standings": {
            "found": True,
            "source": "API-Football / Standings",
            "groups": [
                {
                    "name": "Group A",
                    "rows": [
                        {"rank": 1, "team": {"id": 30, "name": "Team C"}, "points": 7, "goals_diff": 5, "goals_for": 6, "played": 2},
                        {"rank": 2, "team": {"id": 40, "name": "Team D"}, "points": 6, "goals_diff": 2, "goals_for": 4, "played": 2},
                        {"rank": 3, "team": {"id": 10, "name": "Team A"}, "points": 0, "goals_diff": -4, "goals_for": 1, "played": 2},
                        {"rank": 4, "team": {"id": 20, "name": "Team B"}, "points": 0, "goals_diff": -3, "goals_for": 1, "played": 2},
                    ],
                }
            ],
        },
    }
    context = build_match_context(api_football_data)
    assert context["team_a_pressure"] == 0
    assert context["team_b_pressure"] == 0
    assert context["elimination_risk"]


def test_zero_risk_gate_blocks_fragile_deep_handicap():
    context = _spain_context()
    items = [
        {"type": "handicap", "selection": "Home -2.5", "standard_odds": 2.0, "odds": 2.0, "amount": 800},
        {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "odds": 6.0, "amount": 100},
        {"type": "correct_score", "selection": "4:0", "standard_odds": 8.0, "odds": 8.0, "amount": 100},
    ]
    score_rows = [
        {"score": "3:0", "scenario_type": "main", "scenario_weight": 0.25, "profit": 1000},
        {"score": "4:0", "scenario_type": "main", "scenario_weight": 0.16, "profit": 1200},
        {"score": "2:0", "scenario_type": "adjacent", "scenario_weight": 0.24, "profit": -1000},
        {"score": "3:1", "scenario_type": "adjacent", "scenario_weight": 0.18, "profit": -1000},
        {"score": "2:1", "scenario_type": "tail", "scenario_weight": 0.17, "profit": -1000},
    ]
    gate = portfolio_risk_gate({"items": items}, score_rows, context)
    assert not gate["passed"]
    assert gate["risk_level"] in {"HIGH", "CRITICAL"}
    assert "2:0" in gate["failed_paths"]


def test_correct_score_exposure_control_and_rank1_eligibility():
    context = _spain_context()
    items = [
        {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "odds": 6.0, "amount": 400},
        {"type": "correct_score", "selection": "4:0", "standard_odds": 8.0, "odds": 8.0, "amount": 400},
        {"type": "winner", "selection": "Spain win", "standard_odds": 1.30, "odds": 1.30, "amount": 200},
    ]
    score_rows = [
        {"score": "3:0", "scenario_type": "main", "scenario_weight": 0.25, "profit": 1600},
        {"score": "2:0", "scenario_type": "adjacent", "scenario_weight": 0.25, "profit": -600},
        {"score": "3:1", "scenario_type": "adjacent", "scenario_weight": 0.20, "profit": -600},
        {"score": "1:0", "scenario_type": "tail", "scenario_weight": 0.10, "profit": -600},
    ]
    strategy = {"items": items, "score_rows": score_rows, "score": 90}
    strategy["risk_gate"] = portfolio_risk_gate(strategy, score_rows, context)
    strategy["correct_score_exposure"] = correct_score_exposure_control(strategy)
    strategy["pressure_fit"] = strategy_pressure_fit(items, context["match"], context["distribution"])
    eligibility = rank1_eligibility_check(strategy, context["match"], context["distribution"])
    assert not strategy["correct_score_exposure"]["passed"]
    assert strategy["correct_score_exposure"]["stake_share"] > 0.30
    assert not eligibility["rank1_eligible"]


def test_pressure_templates_change_candidate_generation():
    match = {"home_cn": "Ecuador", "away_cn": "Germany", "home_en": "Ecuador", "away_en": "Germany"}
    distribution = {
        "favorite": "Germany",
        "main_path": "热门方赢2球",
        "game_behavior": {
            "match_pressure_type": "qualified_favorite_vs_must_win_underdog",
            "behavior_adjustments": {
                "deep_handicap_risk_delta": 2,
                "underdog_goal_weight_delta": 2,
                "favorite_small_win_weight_delta": 1,
            },
        },
    }
    combo = [
        {"type": "winner", "selection": "Germany win", "name": "Germany独赢", "recommended": True, "standard_odds": 1.4, "amount": 500},
        {"type": "handicap", "selection": "Away -1.5", "name": "Away -1.5", "recommended": True, "standard_odds": 2.0, "amount": 500},
        {"type": "handicap", "selection": "Away -1", "name": "Away -1", "recommended": True, "standard_odds": 1.7, "amount": 500},
        {"type": "correct_score", "selection": "0:2", "name": "波胆 0:2", "recommended": True, "standard_odds": 7.0, "amount": 100},
        {"type": "correct_score", "selection": "1:2", "name": "波胆 1:2", "recommended": True, "standard_odds": 8.0, "amount": 100},
    ]
    portfolios = generate_style_portfolios(combo, match, distribution)
    pressure = [item for item in portfolios if item.get("pressure_template")]
    assert pressure
    assert any("underdog" in item["pressure_template"] or "lower handicap" in item["pressure_template"] for item in pressure)
    assert any(any(asset.get("selection") == "1:2" for asset in item["items"]) for item in pressure)


def test_portfolio_marginal_utility_recommends_safer_replacement():
    grid = _score_grid()
    base = {
        "score": 75,
        "items": [
            {"type": "handicap", "selection": "Home -2.5", "standard_odds": 2.0, "odds": 2.0, "amount": 800},
            {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "odds": 6.0, "amount": 100},
            {"type": "correct_score", "selection": "4:0", "standard_odds": 8.0, "odds": 8.0, "amount": 100},
        ],
    }
    replacement = {
        "name": "Replace Home -2.5 with Home -2",
        "items": [
            {"type": "handicap", "selection": "Home -2", "standard_odds": 1.7, "odds": 1.7, "amount": 800},
            {"type": "correct_score", "selection": "3:0", "standard_odds": 6.0, "odds": 6.0, "amount": 100},
            {"type": "correct_score", "selection": "4:0", "standard_odds": 8.0, "odds": 8.0, "amount": 100},
        ],
    }
    rows = compute_portfolio_marginal_utility(base, [replacement], grid)
    assert rows
    assert rows[0]["recommendation"] in {"Replace", "Review", "Add"}
    assert rows[0]["base_zero_risk"] >= rows[0]["new_zero_risk"]


def test_market_center_identification_separates_direction_and_coverage():
    match = {"home_cn": "Turkey", "away_cn": "United States"}
    odds = {"home_win": 3.5, "draw": 3.9, "away_win": 1.9}
    rows = [
        {"bookmaker": "A", "value": "Away -0.5", "odd": 1.48},
        {"bookmaker": "B", "value": "Away -0.25", "odd": 1.35},
        {"bookmaker": "C", "value": "Home +0.5", "odd": 1.95},
        {"bookmaker": "Outlier", "value": "Away -1.25", "odd": 1.10},
    ]
    summary = identify_handicap_center(rows, odds=odds, match=match)
    assert summary["available"]
    assert "美国" in summary["center_label"]
    assert summary["coverage_label"] == "土耳其 +0.5"
    assert summary["outlier_count"] == 1


def test_total_center_identification_uses_range_not_mechanical_over():
    rows = [
        {"line": 2.5, "bookmaker": "A", "over_odds": 1.67, "under_odds": 2.15},
        {"line": 2.5, "bookmaker": "B", "over_odds": 1.68, "under_odds": 2.20},
        {"line": 2.75, "bookmaker": "A", "over_odds": 1.88, "under_odds": 1.98},
        {"line": 2.75, "bookmaker": "B", "over_odds": 1.90, "under_odds": 2.00},
        {"line": 3.0, "bookmaker": "A", "over_odds": 2.20, "under_odds": 1.70},
    ]
    summary = identify_total_center(rows)
    assert summary["available"]
    assert summary["center_label"] == "2.5-2.75"
    assert "2.5 盘口略偏大球" in summary["market_bias"]


if __name__ == "__main__":
    test_handicap_normalization()
    test_asian_handicap_settlement()
    test_bet_and_portfolio_dedupe()
    test_portfolio_score_not_always_100_and_noise_filter()
    test_score_grid_and_candidate_efficiency()
    test_coverage_efficiency_cases()
    test_actual_odds_ab_ranking()
    test_correct_score_max_four_and_user_penalty()
    test_match_investment_score_data_quality()
    test_game_behavior_engine_pressure_adjustments()
    test_qualification_seed_germany_ecuador()
    test_qualification_seed_switzerland_canada_draw_under()
    test_qualification_seed_bosnia_qatar_must_win()
    test_qualification_seed_morocco_haiti_keeps_main_direction()
    test_qualification_seed_japan_sweden_and_england_panama()
    test_match_context_from_api_football_standings()
    test_match_context_eliminated_from_standings()
    test_zero_risk_gate_blocks_fragile_deep_handicap()
    test_correct_score_exposure_control_and_rank1_eligibility()
    test_pressure_templates_change_candidate_generation()
    test_portfolio_marginal_utility_recommends_safer_replacement()
    test_market_center_identification_separates_direction_and_coverage()
    test_total_center_identification_uses_range_not_mechanical_over()
    print("portfolio_engine tests passed")
