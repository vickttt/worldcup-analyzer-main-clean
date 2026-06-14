def recommend_scores(match, probabilities, odds):
    home = match["home_cn"]
    away = match["away_cn"]
    home_prob = probabilities["home_win"]
    draw_prob = probabilities["draw"]

    if home_prob >= 0.72:
        main_score = f"{home} 2-0 {away}"
        secondary_score = f"{home} 3-0 {away}"
        risk_score = f"{home} 1-1 {away}"
    elif home_prob >= 0.58:
        main_score = f"{home} 2-1 {away}"
        secondary_score = f"{home} 1-0 {away}"
        risk_score = f"{home} 1-1 {away}"
    elif draw_prob >= 0.30:
        main_score = f"{home} 1-1 {away}"
        secondary_score = f"{home} 0-0 {away}"
        risk_score = f"{home} 0-1 {away}"
    else:
        main_score = f"{home} 1-0 {away}"
        secondary_score = f"{home} 1-1 {away}"
        risk_score = f"{home} 0-1 {away}"

    return {
        "main": main_score,
        "secondary": secondary_score,
        "risk": risk_score,
    }

