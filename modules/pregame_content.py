import base64
from pathlib import Path


TEAM_CN = {
    "Argentina": "阿根廷",
    "Algeria": "阿尔及利亚",
    "Austria": "奥地利",
    "Jordan": "约旦",
    "France": "法国",
    "England": "英格兰",
    "Germany": "德国",
    "Spain": "西班牙",
    "Brazil": "巴西",
    "Japan": "日本",
    "Australia": "澳大利亚",
    "Belgium": "比利时",
    "Bosnia and Herzegovina": "波黑",
    "Canada": "加拿大",
    "Cape Verde": "佛得角",
    "Colombia": "哥伦比亚",
    "Croatia": "克罗地亚",
    "Curaçao": "库拉索",
    "Curacao": "库拉索",
    "Czech Republic": "捷克",
    "Czechia": "捷克",
    "Ecuador": "厄瓜多尔",
    "Egypt": "埃及",
    "Ghana": "加纳",
    "Haiti": "海地",
    "Iran": "伊朗",
    "Iraq": "伊拉克",
    "Ivory Coast": "科特迪瓦",
    "Mexico": "墨西哥",
    "Morocco": "摩洛哥",
    "Netherlands": "荷兰",
    "New Zealand": "新西兰",
    "Norway": "挪威",
    "Panama": "巴拿马",
    "Paraguay": "巴拉圭",
    "Portugal": "葡萄牙",
    "Qatar": "卡塔尔",
    "Saudi Arabia": "沙特阿拉伯",
    "Scotland": "苏格兰",
    "Senegal": "塞内加尔",
    "South Africa": "南非",
    "South Korea": "韩国",
    "Sweden": "瑞典",
    "Switzerland": "瑞士",
    "Tunisia": "突尼斯",
    "Turkey": "土耳其",
    "Türkiye": "土耳其",
    "Uruguay": "乌拉圭",
    "Uzbekistan": "乌兹别克斯坦",
    "Democratic Republic of the Congo": "刚果（金）",
    "Democratic Republic of Congo": "刚果（金）",
    "DR Congo": "刚果（金）",
    "Congo DR": "刚果（金）",
    "United States": "美国",
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
        "world_cup_appearances": "18次",
        "team_value_number": 850,
        "colors": ("#75aadb", "#f6c343"),
    },
    "Algeria": {
        "fifa_rank": "28",
        "elo": "非洲强队区间",
        "team_value": "约 €1.9亿",
        "average_age": "约 28岁",
        "coach": "Vladimir Petkovic",
        "best_world_cup": "16强 2014",
        "world_cup_appearances": "5次",
        "team_value_number": 190,
        "colors": ("#006233", "#d21034"),
    },
    "Portugal": {
        "fifa_rank": "6",
        "elo": "欧洲顶级区间",
        "team_value": "约 €10亿",
        "average_age": "约 27岁",
        "coach": "Roberto Martinez",
        "best_world_cup": "季军 1966",
        "world_cup_appearances": "9次",
        "team_value_number": 1000,
        "colors": ("#006600", "#ff0000"),
    },
    "Democratic Republic of the Congo": {
        "fifa_rank": "60",
        "elo": "非洲竞争区间",
        "team_value": "约 €1.1亿",
        "average_age": "约 27岁",
        "coach": "Sebastien Desabre",
        "best_world_cup": "小组赛 1974",
        "world_cup_appearances": "1次",
        "team_value_number": 110,
        "colors": ("#007fff", "#f7d618"),
    },
    "DR Congo": {
        "fifa_rank": "60",
        "elo": "非洲竞争区间",
        "team_value": "约 €1.1亿",
        "average_age": "约 27岁",
        "coach": "Sebastien Desabre",
        "best_world_cup": "小组赛 1974",
        "world_cup_appearances": "1次",
        "team_value_number": 110,
        "colors": ("#007fff", "#f7d618"),
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

def banner_image_url():
    path = Path(__file__).resolve().parents[1] / "assets" / "worldcup_usa_banner.png"
    if path.exists():
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    return "https://upload.wikimedia.org/wikipedia/commons/4/4d/Arrowhead_Stadium_exterior.jpg"


BANNER_IMAGE_URL = banner_image_url()


def group_letter_cn(letter):
    return f"{letter}组"


def team_cn(name):
    text = str(name or "")
    if text in TEAM_CN:
        return TEAM_CN[text]
    if text.startswith("Winner Group "):
        return f"{group_letter_cn(text.replace('Winner Group ', ''))}第1名"
    if text.startswith("Runner-up Group "):
        return f"{group_letter_cn(text.replace('Runner-up Group ', ''))}第2名"
    if text.startswith("3rd Group "):
        groups = text.replace("3rd Group ", "").replace("/", " / ")
        return f"{groups}组第三名"
    if text.startswith("Winner Match "):
        return f"第{text.replace('Winner Match ', '')}场胜者"
    if text.startswith("Loser Match "):
        return f"第{text.replace('Loser Match ', '')}场负者"
    return text


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
    for old, new in sorted(TEAM_CN.items(), key=lambda item: len(item[0]), reverse=True):
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
        "world_cup_appearances": "待接入",
        "team_value_number": 0,
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
    upset = decision.get("upset_index", {})
    home = team_cn(match["home_cn"])
    away = team_cn(match["away_cn"])

    return [
        f"{home}是市场更支持的一方，核心问题不是是否被看好，而是盘口是否支持其打穿让球。",
        f"当前各方对{team_cn(disagreement.get('direction'))}的看法差异不大，说明主流赔率与预测市场整体态度较一致。",
        f"爆冷风险为 {upset.get('score', 0)} / 100，当前组合更适合围绕{bet_cn(recommendation)}展开，同时关注平局和弱势方不败路径。",
    ]


def build_risk_notes(match, decision):
    contrarian = decision.get("contrarian", {})
    upset = decision.get("upset_index", {})
    disagreement = decision.get("market_disagreement", {})

    notes = [
        "本届世界杯热门球队并非每场都能顺利打穿盘口，强弱差距不等于投注价值。",
        f"当前需要警惕{team_cn(match['home_cn'])}或{team_cn(match['away_cn'])}任一方向被市场过度拥挤。",
        f"市场分歧为 {disagreement.get('score', 0)} / 100，属于{disagreement_label(disagreement.get('score', 0)).replace('🟢 ', '').replace('🟡 ', '').replace('🔴 ', '')}。",
        "当前未发现明显价值机会，临场盘口变化比赛前静态价格更重要。",
        f"逆向分数为 {contrarian.get('score', 0)} / 100，分数越高，越说明热门方向可能过热。",
        f"爆冷指数为 {upset.get('score', 0)} / 100，当前解读：{upset.get('meaning', '中性风险')}。",
    ]
    return notes
