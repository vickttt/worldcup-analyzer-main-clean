import re
from pathlib import Path

import yaml


def load_team_aliases():
    path = Path(__file__).resolve().parents[1] / "data" / "team_aliases.yaml"
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def parse_match(match_text):
    aliases = load_team_aliases()
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
        "home_en": aliases.get(home_cn, home_cn),
        "away_en": aliases.get(away_cn, away_cn),
        "display_name": f"{home_cn} vs {away_cn}",
    }

