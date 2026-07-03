"""Actual-odds parsing compatibility helpers.

The TPB decision path no longer consumes user-entered odds signals. This module
is intentionally limited to parsing legacy text inputs and returning empty
compatibility payloads for old utility scripts.
"""

import csv
import re
from io import StringIO

from modules.team_resolver import canonical_name


def parse_float(value):
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return number if number > 1 else None


def normalize(value):
    return " ".join(str(value or "").strip().lower().replace("-", " ").split())


def normalize_team(value):
    return normalize(canonical_name(str(value or "").strip()))


def normalize_score(value):
    text = str(value or "").strip()
    text = text.replace("：", ":").replace(" - ", ":").replace("-", ":")
    text = re.sub(r"\s+", "", text)
    match = re.search(r"(\d+):(\d+)", text)
    if not match:
        return text
    return f"{int(match.group(1))}:{int(match.group(2))}"


def parse_score(value):
    match = re.search(r"(\d+)\s*[:：-]\s*(\d+)", str(value or ""))
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def total_side_and_line(value):
    text = str(value or "").strip()
    match = re.search(r"(Under|Over|小于|大于)\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
    if not match:
        return None, None
    side = "under" if match.group(1).lower() in {"under", "小于"} else "over"
    return side, float(match.group(2))


def standardize_selection(item_type, selection):
    text = str(selection or "").strip()
    if item_type == "winner":
        return canonical_name(text)
    if item_type == "correct_score":
        return normalize_score(text)
    if item_type == "total":
        side, line = total_side_and_line(text)
        if side and line is not None:
            return f"{side.title()} {line:g}"
    return re.sub(r"\s+", " ", text)


def market_key(label):
    text = normalize(label)
    if "match winner" in text or "winner" in text or "胜平负" in text or "独赢" in text:
        return "winner"
    if "asian" in text or "handicap" in text or "让球" in text:
        return "handicap"
    if "over under" in text or "over/under" in text or "total" in text or "大小球" in text:
        return "total"
    if "correct score" in text or "exact score" in text or "波胆" in text:
        return "correct_score"
    return None


def parse_actual_odds(raw_text):
    text = str(raw_text or "").strip()
    if not text:
        return {"items": [], "by_type": {}, "raw": ""}

    items = parse_csv_odds(text) or parse_block_odds(text)
    by_type = {}
    for item in items:
        key = item["type"]
        if key == "correct_score":
            by_type.setdefault(key, {})[normalize_score(item["selection"])] = item
        else:
            by_type[key] = item
        by_type.setdefault(f"{key}_items", []).append(item)
    return {"items": items, "by_type": by_type, "raw": text}


def parse_csv_odds(text):
    if "," not in text:
        return []
    rows = []
    try:
        reader = csv.reader(StringIO(text))
        for raw in reader:
            parts = [part.strip() for part in raw if part.strip()]
            if len(parts) < 3:
                continue
            key = market_key(parts[0])
            odds = parse_float(parts[-1])
            if key and odds:
                selection = parts[1] if key != "handicap" or len(parts) < 4 else f"{parts[1]} {parts[2]}"
                rows.append({"type": key, "selection": standardize_selection(key, selection), "odds": odds})
    except csv.Error:
        return []
    return rows


def parse_block_odds(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    rows = []
    index = 0
    while index + 2 < len(lines):
        key = market_key(lines[index])
        odds = parse_float(lines[index + 2])
        if key and odds:
            rows.append({"type": key, "selection": standardize_selection(key, lines[index + 1]), "odds": odds})
            index += 3
        else:
            index += 1
    return rows


def number_in_text(value):
    match = re.search(r"([+-]?\d+(?:\.\d+)?)", str(value or ""))
    return float(match.group(1)) if match else None


def candidate_with_actual(candidate, actual_odds=None):
    item = dict(candidate or {})
    item["actual_odds"] = None
    item["edge"] = None
    return item


def build_market_candidates(*args, **kwargs):
    return []


def build_recommendation_slots(*args, **kwargs):
    return []


def enrich_candidate(candidate, *args, **kwargs):
    return candidate_with_actual(candidate)


def apply_path_consistency(candidates, *args, **kwargs):
    return list(candidates or [])


def recommendation_reason(candidate):
    return "实际赔率推荐已停用；用户赔率仅用于执行复盘，不进入系统推荐。"
