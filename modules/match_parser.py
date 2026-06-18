import re

from modules.team_resolver import canonical_name


def parse_match(match_text):
    cleaned = match_text.strip()
    parts = re.split(r"\s+(?:vs|VS|v|V|对|vs\.)\s+|\\s*-\s*|\\s+VS\\s+", cleaned)

    if len(parts) < 2:
        parts = re.split(r"\s*vs\s*", cleaned, flags=re.IGNORECASE)

    if len(parts) < 2:
        raise ValueError("请输入类似“德国 vs 库拉索”的比赛名称。")

    home_cn = parts[0].strip()
    away_cn = parts[1].strip()

    return {
        "home_cn": home_cn,
        "away_cn": away_cn,
        "home_en": canonical_name(home_cn),
        "away_en": canonical_name(away_cn),
        "display_name": f"{home_cn} vs {away_cn}",
    }
