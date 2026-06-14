def rate_opportunity(probabilities, polymarket, news):
    home_prob = probabilities["home_win"]
    liquidity = polymarket.get("liquidity") or 0
    risk_count = len(news["risk_flags"])

    if not polymarket.get("found", True):
        return {
            "grade": "C",
            "risk_level": "中高",
            "summary": "未找到对应 Polymarket 市场，市场验证不足。",
        }

    if home_prob >= 0.75 and liquidity >= 30000 and risk_count <= 2:
        return {
            "grade": "A",
            "risk_level": "中低",
            "summary": "强队优势明显，赔率与预测市场方向基本一致。",
        }

    if home_prob >= 0.62:
        return {
            "grade": "B",
            "risk_level": "中",
            "summary": "方向较清晰，但仍存在轮换、节奏或盘口过热风险。",
        }

    return {
        "grade": "C",
        "risk_level": "中高",
        "summary": "优势不够明确，更适合观察或小仓位试探。",
    }
