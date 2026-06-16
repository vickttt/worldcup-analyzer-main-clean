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
        "home": ["No news available"],
        "away": ["No news available"],
        "risk_flags": [],
        "news_score_adjustment": 0,
    }
