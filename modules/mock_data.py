def get_mock_odds(match):
    return {
        "home_win": 1.22,
        "draw": 6.20,
        "away_win": 13.50,
        "over_under_line": 2.75,
        "source": "模拟国际赔率",
    }


def get_mock_polymarket(match):
    return {
        "home_win": 0.79,
        "draw": 0.14,
        "away_win": 0.07,
        "volume": 125000,
        "liquidity": 42000,
        "source": "模拟 Polymarket 市场",
    }


def get_mock_news_and_injuries(match):
    return {
        "home": [
            "德国整体阵容较完整，主力框架稳定。",
            "锋线存在轻微轮换可能，但核心中场预计首发。",
        ],
        "away": [
            "库拉索防守端预计采取低位阵型。",
            "暂无明确核心球员重伤信息，但整体阵容深度有限。",
        ],
        "risk_flags": [
            "强弱差距明显时，强队可能提前轮换或降低比赛节奏。",
            "如果德国迟迟无法进球，平局风险会上升。",
        ],
        "news_score_adjustment": -0.02,
    }

