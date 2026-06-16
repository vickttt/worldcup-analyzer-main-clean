TEAM_CN = {
    "Argentina": "阿根廷",
    "Algeria": "阿尔及利亚",
    "Draw": "平局",
}

TEAM_PROFILES = {
    "Argentina": {
        "fifa_rank": "1",
        "elo": "世界顶级区间",
        "team_value": "约 €8.5亿",
        "average_age": "约 28岁",
        "coach": "Lionel Scaloni",
        "best_world_cup": "冠军 1978 / 1986 / 2022",
        "colors": ("#75aadb", "#f6c343"),
    },
    "Algeria": {
        "fifa_rank": "28",
        "elo": "非洲强队区间",
        "team_value": "约 €1.9亿",
        "average_age": "约 28岁",
        "coach": "Vladimir Petkovic",
        "best_world_cup": "16强 2014",
        "colors": ("#006233", "#d21034"),
    },
}

PREDICTED_LINEUPS = {
    "Argentina": {
        "formation": "4-3-3",
        "goalkeeper": ["E. Martinez"],
        "defenders": ["Molina", "Romero", "Otamendi", "Tagliafico"],
        "midfielders": ["De Paul", "Mac Allister", "Enzo Fernandez"],
        "forwards": ["Messi", "Lautaro Martinez", "Julian Alvarez"],
        "key_players": ["Messi", "Lautaro Martinez", "E. Martinez", "Mac Allister"],
    },
    "Algeria": {
        "formation": "4-2-3-1",
        "goalkeeper": ["Mandrea"],
        "defenders": ["Atal", "Mandi", "Touba", "Ait-Nouri"],
        "midfielders": ["Bennacer", "Zerrouki", "Mahrez", "Aouar", "Benrahma"],
        "forwards": ["Bounedjah"],
        "key_players": ["Mahrez", "Bennacer", "Bensebaini", "Bounedjah"],
    },
}

STATIC_RECENT_FORM = {
    "Argentina": [
        {"result": "W", "gf": 1, "ga": 0, "opponent": "Colombia"},
        {"result": "W", "gf": 2, "ga": 0, "opponent": "Canada"},
        {"result": "D", "gf": 1, "ga": 1, "opponent": "Ecuador"},
        {"result": "W", "gf": 2, "ga": 0, "opponent": "Peru"},
        {"result": "W", "gf": 1, "ga": 0, "opponent": "Chile"},
        {"result": "W", "gf": 2, "ga": 0, "opponent": "Canada"},
        {"result": "W", "gf": 4, "ga": 1, "opponent": "Guatemala"},
        {"result": "W", "gf": 1, "ga": 0, "opponent": "Ecuador"},
        {"result": "W", "gf": 3, "ga": 0, "opponent": "El Salvador"},
        {"result": "W", "gf": 2, "ga": 0, "opponent": "Brazil"},
    ],
    "Algeria": [
        {"result": "D", "gf": 1, "ga": 1, "opponent": "Sudan"},
        {"result": "D", "gf": 0, "ga": 0, "opponent": "Niger"},
        {"result": "W", "gf": 3, "ga": 0, "opponent": "Uganda"},
        {"result": "W", "gf": 2, "ga": 1, "opponent": "Guinea"},
        {"result": "W", "gf": 5, "ga": 1, "opponent": "Mozambique"},
        {"result": "W", "gf": 3, "ga": 1, "opponent": "Bolivia"},
        {"result": "D", "gf": 3, "ga": 3, "opponent": "South Africa"},
        {"result": "W", "gf": 2, "ga": 1, "opponent": "Togo"},
        {"result": "W", "gf": 1, "ga": 0, "opponent": "Togo"},
        {"result": "L", "gf": 0, "ga": 1, "opponent": "Guinea"},
    ],
}

BANNER_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/4/4d/Arrowhead_Stadium_exterior.jpg"


def team_cn(name):
    return TEAM_CN.get(name, name)


def bet_cn(value):
    text = str(value or "暂无观点")
    replacements = {
        "Lean ": "",
        "Neutral around 2.5": "暂无明显方向",
        "Neutral around": "暂无明显方向",
        "No view": "暂无明确方向",
        "Argentina": "阿根廷",
        "Algeria": "阿尔及利亚",
        "Draw": "平局",
        "Over": "大于",
        "Under": "小于",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def reason_cn(value):
    text = str(value or "-")
    replacements = {
        "Market consensus and Polymarket both favor Argentina.": "主流赔率市场与 Polymarket 观点一致，均认为阿根廷获胜概率明显高于阿尔及利亚。",
        "Handicap market suggests Algeria may cover the spread.": "让球盘显示，市场虽然支持阿根廷取胜，但对其大胜仍保持克制。",
        "Over and Under odds remain balanced.": "大小球盘口分歧不大，总进球预期较为中性。",
        "Under odds are slightly favored by the market.": "市场对小球方向略有倾向。",
        "Over odds are slightly favored by the market.": "市场对大球方向略有倾向。",
    }
    return replacements.get(text, text)


def profile_for(name):
    return TEAM_PROFILES.get(name, {
        "fifa_rank": "待接入",
        "elo": "后续扩展",
        "team_value": "待接入",
        "average_age": "待接入",
        "coach": "待接入",
        "best_world_cup": "待接入",
        "colors": ("#64748b", "#94a3b8"),
    })


def predicted_lineup_for(name):
    return PREDICTED_LINEUPS.get(name)


def static_recent_form_for(name):
    return STATIC_RECENT_FORM.get(name, [])


def disagreement_label(score):
    if score >= 67:
        return "🔴 高分歧"
    if score >= 34:
        return "🟡 中分歧"
    return "🟢 低分歧"


def build_storylines(match, betting_opinion, decision):
    recommendation = decision.get("final_recommendation", {}).get("bet", "观察为主")
    disagreement = decision.get("market_disagreement", {})
    contrarian = decision.get("contrarian", {})
    upset = decision.get("upset_index", {})

    return [
        "阿根廷作为卫冕冠军与本届世界杯热门球队，当前获得主流赔率市场和预测市场的共同支持。",
        "阿尔及利亚代表非洲足球力量，身体对抗、转换速度和受让盘保护是本场的主要看点。",
        f"目前最大市场分歧出现在{team_cn(disagreement.get('direction'))}方向，差异约为 {disagreement.get('difference', 0) * 100:.1f}%。",
        f"亚洲让球盘当前更值得关注：{bet_cn(betting_opinion.get('asian_handicap'))}。",
        f"逆向分数为 {contrarian.get('score', 0)} / 100，说明热门方向可能存在一定拥挤交易。",
        f"综合模型当前更倾向的投注选择是：{bet_cn(recommendation)}。",
        "本场比赛是否继续出现热门球队赢球但输盘的走势，值得重点观察。",
    ]


def build_risk_notes(match, decision):
    contrarian = decision.get("contrarian", {})
    upset = decision.get("upset_index", {})
    disagreement = decision.get("market_disagreement", {})

    notes = [
        "本届世界杯热门球队并非每场都能顺利打穿盘口，强弱差距不等于投注价值。",
        f"当前市场对{team_cn(match['home_cn'])}形成高度一致预期，需警惕热门球队被高估。",
        f"市场分歧为 {disagreement.get('score', 0)} / 100，属于{disagreement_label(disagreement.get('score', 0)).replace('🟢 ', '').replace('🟡 ', '').replace('🔴 ', '')}。",
        "当前未发现明显价值机会，临场盘口变化比赛前静态价格更重要。",
        f"逆向分数为 {contrarian.get('score', 0)} / 100，分数越高，越说明热门方向可能过热。",
        f"爆冷指数为 {upset.get('score', 0)} / 100，当前解读：{upset.get('meaning', '中性风险')}。",
    ]
    return notes
