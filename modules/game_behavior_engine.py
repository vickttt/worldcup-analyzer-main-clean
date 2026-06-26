import json
import unicodedata
from pathlib import Path


TEAM_PRESSURE_SCORE = {
    0: "already eliminated / no motivation",
    1: "already qualified (rotation risk)",
    2: "draw acceptable",
    3: "must avoid loss",
    4: "must win",
    5: "must win big / depends on others",
}

ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_SEED_PATH = ROOT / "data" / "worldcup2026" / "qualification_context_2026_06_24.json"


def normalize_name(value):
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(
        ascii_text.lower()
        .replace("&", "and")
        .replace("turkiye", "turkey")
        .replace("united states", "usa")
        .replace("cote divoire", "ivory coast")
        .replace("cotedivoire", "ivory coast")
        .split()
    )


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value, low=-1.0, high=1.0):
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return max(low, min(high, number))


def pressure_label(score):
    try:
        value = int(score)
    except (TypeError, ValueError):
        value = 3
    return TEAM_PRESSURE_SCORE.get(value, TEAM_PRESSURE_SCORE[3])


def default_match_context(group_stage=True):
    return {
        "team_a_pressure": 3,
        "team_b_pressure": 3,
        "home_pressure_score": 3,
        "away_pressure_score": 3,
        "group_stage": bool(group_stage),
        "qualified_already": False,
        "elimination_risk": False,
        "goal_difference_pressure": 0.0,
        "team_a_pressure_reason": "No standings context; neutral pressure.",
        "team_b_pressure_reason": "No standings context; neutral pressure.",
        "standings_source": None,
        "qualification_source": "default_neutral",
        "home_context": None,
        "away_context": None,
        "match_pressure_type": "neutral_group_context",
        "behavior_adjustments": zero_behavior_adjustments(),
        "behavior_notes": ["No qualification seed found; neutral match behavior."],
    }


def zero_behavior_adjustments():
    return {
        "deep_handicap_risk_delta": 0,
        "favorite_small_win_weight_delta": 0,
        "underdog_goal_weight_delta": 0,
        "draw_weight_delta": 0,
        "over_weight_delta": 0,
        "under_weight_delta": 0,
        "late_goal_volatility_delta": 0,
        "rotation_risk_delta": 0,
        "tempo_control_delta": 0,
        "chaos_risk_delta": 0,
        "recommended_coverage_shift": [],
    }


def load_qualification_seed():
    if not QUALIFICATION_SEED_PATH.exists():
        return {}
    try:
        return json.loads(QUALIFICATION_SEED_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def seed_team_lookup(seed):
    lookup = {}
    for group_name, group in (seed.get("groups") or {}).items():
        for team_name, row in (group.get("teams") or {}).items():
            item = {
                "team": team_name,
                "group": group_name,
                "points": row.get("points"),
                "rank": row.get("rank"),
                "goal_difference": row.get("goal_difference", row.get("gd")),
                "goals_for": row.get("goals_for"),
                "goals_against": row.get("goals_against"),
                "matches_played": row.get("matches_played", 2),
                "pressure_score": row.get("pressure_score", 3),
                "pressure_label": row.get("pressure_label") or pressure_label(row.get("pressure_score", 3)),
                "qualification_note": row.get("qualification_note") or "",
                "motivation_tags": row.get("motivation_tags") or [],
                "source": seed.get("source", "manual_seed"),
            }
            lookup[normalize_name(team_name)] = item
    return lookup


def seed_match_lookup(seed):
    lookup = {}
    for item in seed.get("matches") or []:
        home = normalize_name(item.get("home"))
        away = normalize_name(item.get("away"))
        if home and away:
            lookup[(home, away)] = item
            lookup[(away, home)] = {
                **item,
                "home": item.get("away"),
                "away": item.get("home"),
                "home_pressure_score": item.get("away_pressure_score"),
                "away_pressure_score": item.get("home_pressure_score"),
            }
    return lookup


def team_id_from_fixture(api_football_data, side):
    fixture_result = (api_football_data or {}).get("fixture_result") or {}
    team = fixture_result.get(f"{side}_team") or {}
    if team.get("id"):
        return team.get("id")
    fixture = (api_football_data or {}).get("fixture") or {}
    return ((fixture.get(f"{side}_team") or {}).get("id"))


def group_rows_for_team(standings, team_id):
    if not standings or not standings.get("found") or not team_id:
        return []
    for group in standings.get("groups") or []:
        rows = group.get("rows") or []
        for row in rows:
            if ((row.get("team") or {}).get("id")) == team_id:
                return sorted(
                    rows,
                    key=lambda item: (
                        -safe_int(item.get("points")),
                        -safe_int(item.get("goals_diff")),
                        -safe_int(item.get("goals_for")),
                        safe_int(item.get("rank"), 99),
                    ),
                )
    return []


def standing_row_for_team(group_rows, team_id):
    for row in group_rows or []:
        if ((row.get("team") or {}).get("id")) == team_id:
            return row
    return None


def pressure_from_standing(row, group_rows):
    if not row or not group_rows:
        return 3, "No matching standings row; neutral pressure.", 0.0
    group_size = max(4, len(group_rows))
    max_group_matches = max(3, group_size - 1)
    played = safe_int(row.get("played"))
    remaining = max(0, max_group_matches - played)
    points = safe_int(row.get("points"))
    rank = safe_int(row.get("rank"), 99)
    goals_diff = safe_int(row.get("goals_diff"))
    max_points = points + remaining * 3
    sorted_rows = sorted(
        group_rows,
        key=lambda item: (
            -safe_int(item.get("points")),
            -safe_int(item.get("goals_diff")),
            -safe_int(item.get("goals_for")),
            safe_int(item.get("rank"), 99),
        ),
    )
    second = sorted_rows[1] if len(sorted_rows) > 1 else None
    third = sorted_rows[2] if len(sorted_rows) > 2 else None
    second_points = safe_int((second or {}).get("points"))
    third_points = safe_int((third or {}).get("points"))
    second_gd = safe_int((second or {}).get("goals_diff"))
    third_gd = safe_int((third or {}).get("goals_diff"))
    if remaining <= 0:
        if rank <= 2:
            return 1, "Group finished and team is in a qualifying position.", 0.0
        return 0, "Group finished and team is outside qualification positions.", 0.0
    if rank <= 2 and third and points > third_points + remaining * 3:
        return 1, "Mathematically qualified; rotation risk increases.", -0.2
    if rank <= 2:
        cushion = points - third_points
        if remaining <= 1 and cushion >= 1:
            return 2, "A draw is likely enough to protect qualification position.", 0.1
        if remaining <= 1 and cushion == 0 and goals_diff >= third_gd:
            return 2, "Qualification position is protected by goal difference; draw is acceptable.", 0.2
        return 3, "Must avoid loss to protect current qualification path.", 0.2
    if second and max_points < second_points:
        return 0, "Cannot catch the top two on points.", 0.0
    if second and max_points == second_points and goals_diff < second_gd - 2:
        return 5, "Must win big and needs help from other results.", 0.9
    if rank > 2:
        gap = second_points - points
        gd_gap = second_gd - goals_diff
        if remaining <= 1 and (gap >= 2 or gd_gap >= 2):
            return 5, "Must win and goal difference pressure is high.", 0.8
        if remaining <= 1 or gap > 0:
            return 4, "Must win to move into qualification position.", 0.5
    return 3, "Still alive; must avoid loss while waiting for other group results.", 0.2


def standings_pressure_context(api_football_data):
    standings = (api_football_data or {}).get("standings") or {}
    home_id = team_id_from_fixture(api_football_data, "home")
    away_id = team_id_from_fixture(api_football_data, "away")
    home_group = group_rows_for_team(standings, home_id)
    away_group = group_rows_for_team(standings, away_id)
    if not home_group or not away_group:
        return None
    home_row = standing_row_for_team(home_group, home_id)
    away_row = standing_row_for_team(away_group, away_id)
    home_pressure, home_reason, home_gd_pressure = pressure_from_standing(home_row, home_group)
    away_pressure, away_reason, away_gd_pressure = pressure_from_standing(away_row, away_group)
    gd_pressure = max(home_gd_pressure, away_gd_pressure, key=abs)
    return {
        "team_a_pressure": home_pressure,
        "team_b_pressure": away_pressure,
        "home_pressure_score": home_pressure,
        "away_pressure_score": away_pressure,
        "qualified_already": home_pressure == 1 or away_pressure == 1,
        "elimination_risk": home_pressure >= 4 or away_pressure >= 4 or home_pressure == 0 or away_pressure == 0,
        "goal_difference_pressure": clamp(gd_pressure, -1, 1),
        "team_a_pressure_reason": home_reason,
        "team_b_pressure_reason": away_reason,
        "standings_source": standings.get("source") or "API-Football / Standings",
        "qualification_source": standings.get("source") or "API-Football / Standings",
    }


def seed_pressure_context(match):
    if not match:
        return None
    seed = load_qualification_seed()
    teams = seed_team_lookup(seed)
    matches = seed_match_lookup(seed)
    home_name = match.get("home_en") or match.get("home_cn")
    away_name = match.get("away_en") or match.get("away_cn")
    home_key = normalize_name(home_name)
    away_key = normalize_name(away_name)
    home_context = teams.get(home_key)
    away_context = teams.get(away_key)
    match_seed = matches.get((home_key, away_key)) or {}
    if not home_context or not away_context:
        return None
    home_pressure = safe_int(match_seed.get("home_pressure_score", home_context.get("pressure_score", 3)), 3)
    away_pressure = safe_int(match_seed.get("away_pressure_score", away_context.get("pressure_score", 3)), 3)
    home_context = {**home_context, "remaining_opponent": away_name, "pressure_score": home_pressure, "pressure_label": pressure_label(home_pressure)}
    away_context = {**away_context, "remaining_opponent": home_name, "pressure_score": away_pressure, "pressure_label": pressure_label(away_pressure)}
    match_pressure_type = match_seed.get("match_pressure_type") or classify_match_pressure(home_context, away_context)
    adjustments = compute_behavior_adjustments(match_pressure_type, home_context, away_context)
    behavior_notes = match_seed.get("behavior_notes") or default_behavior_notes(match_pressure_type, home_context, away_context)
    return {
        "team_a_pressure": home_pressure,
        "team_b_pressure": away_pressure,
        "home_pressure_score": home_pressure,
        "away_pressure_score": away_pressure,
        "qualified_already": home_pressure == 1 or away_pressure == 1,
        "elimination_risk": home_pressure >= 4 or away_pressure >= 4 or home_pressure == 0 or away_pressure == 0,
        "goal_difference_pressure": safe_float(match_seed.get("goal_difference_pressure"), 0),
        "team_a_pressure_reason": home_context.get("qualification_note") or pressure_label(home_pressure),
        "team_b_pressure_reason": away_context.get("qualification_note") or pressure_label(away_pressure),
        "standings_source": seed.get("source", "Manual qualification seed"),
        "qualification_source": seed.get("source", "Manual qualification seed"),
        "home_context": home_context,
        "away_context": away_context,
        "match_pressure_type": match_pressure_type,
        "behavior_adjustments": adjustments,
        "behavior_notes": behavior_notes,
    }


def compute_qualification_pressure(team, group_context=None, remaining_match=None):
    seed = load_qualification_seed()
    context = seed_team_lookup(seed).get(normalize_name(team))
    if context:
        return context
    return {
        "team": team,
        "group": (group_context or {}).get("group"),
        "pressure_score": 3,
        "pressure_label": pressure_label(3),
        "qualification_note": "No seed data; neutral must-avoid-loss pressure.",
        "motivation_tags": ["neutral"],
        "remaining_opponent": remaining_match,
    }


def classify_match_pressure(home_context, away_context):
    home = safe_int((home_context or {}).get("pressure_score"), 3)
    away = safe_int((away_context or {}).get("pressure_score"), 3)
    if home <= 0 and away <= 1 or away <= 0 and home <= 1:
        return "dead_rubber_or_low_motivation"
    if home == 1 and away == 1:
        return "qualified_vs_qualified"
    if home == 1 and away >= 3 or away == 1 and home >= 3:
        return "qualified_favorite_vs_must_win_underdog"
    if home == 2 and away == 2:
        return "both_draw_acceptable"
    if home >= 4 and away >= 4:
        return "must_win_vs_must_win"
    if {home, away} & {2, 3} and {home, away} & {4}:
        return "direct_second_place_battle"
    if home >= 4 or away >= 4:
        return "favorite_must_win"
    if home <= 1 or away <= 1:
        return "dead_rubber_or_low_motivation"
    return "direct_second_place_battle"


def default_behavior_notes(match_pressure_type, home_context, away_context):
    home_team = (home_context or {}).get("team", "Home")
    away_team = (away_context or {}).get("team", "Away")
    notes = {
        "qualified_favorite_vs_must_win_underdog": [
            "Qualified side may rotate and control tempo.",
            "Must-win opponent can lift underdog goal and late chaos paths.",
            "Deep handicap should be treated as less reliable than usual.",
        ],
        "both_draw_acceptable": [
            "Both teams can accept a draw; draw and under paths rise.",
            "Aggressive one-sided portfolios should be downgraded.",
        ],
        "direct_second_place_battle": [
            "Both sides carry qualification risk; early caution and late volatility coexist.",
            "Narrow-score coverage is more important than blowout concentration.",
        ],
        "must_win_vs_must_win": [
            "Draw value falls because both teams need maximum points.",
            "Late volatility and chaotic score paths rise.",
        ],
        "qualified_vs_qualified": [
            "Both teams may prioritize health and energy over margin.",
            "Under, draw, and narrow-score paths gain relevance.",
        ],
        "favorite_must_win": [
            "Favorite direction remains valid, but pressure can create inefficient attacks.",
            "One-goal wins and underdog scoring tails should stay covered.",
        ],
        "dead_rubber_or_low_motivation": [
            "Motivation is unclear or low; Match Investment Score should be conservative.",
        ],
    }
    return notes.get(match_pressure_type, [f"{home_team} vs {away_team}: neutral qualification context."])


def compute_behavior_adjustments(match_pressure_type, home_context=None, away_context=None):
    adjustments = zero_behavior_adjustments()
    if match_pressure_type == "qualified_favorite_vs_must_win_underdog":
        adjustments.update({
            "deep_handicap_risk_delta": 2,
            "favorite_small_win_weight_delta": 2,
            "underdog_goal_weight_delta": 2,
            "draw_weight_delta": 0,
            "over_weight_delta": 1,
            "late_goal_volatility_delta": 2,
            "rotation_risk_delta": 2,
            "tempo_control_delta": 1,
            "chaos_risk_delta": 1,
            "recommended_coverage_shift": ["降低深盘权重", "提高强队小胜路径", "提高弱队进球尾部", "增加1球偏差覆盖"],
        })
    elif match_pressure_type == "both_draw_acceptable":
        adjustments.update({
            "deep_handicap_risk_delta": 1,
            "favorite_small_win_weight_delta": 1,
            "draw_weight_delta": 2,
            "over_weight_delta": -1,
            "under_weight_delta": 2,
            "late_goal_volatility_delta": -1,
            "tempo_control_delta": 2,
            "chaos_risk_delta": -1,
            "recommended_coverage_shift": ["提高平局权重", "提高小球权重", "降低强攻剧本", "谨慎参与"],
        })
    elif match_pressure_type == "direct_second_place_battle":
        adjustments.update({
            "deep_handicap_risk_delta": 1,
            "favorite_small_win_weight_delta": 1,
            "underdog_goal_weight_delta": 1,
            "draw_weight_delta": 1,
            "under_weight_delta": 1,
            "late_goal_volatility_delta": 1,
            "chaos_risk_delta": 1,
            "recommended_coverage_shift": ["提高窄比分覆盖", "保留平局路径", "防后段开放", "避免单边大胜过度集中"],
        })
    elif match_pressure_type == "must_win_vs_must_win":
        adjustments.update({
            "underdog_goal_weight_delta": 1,
            "draw_weight_delta": -1,
            "over_weight_delta": 1,
            "late_goal_volatility_delta": 2,
            "tempo_control_delta": -1,
            "chaos_risk_delta": 2,
            "recommended_coverage_shift": ["降低平局价值", "提高后期开放风险", "提高2:1/1:2/2:2路径", "不要只覆盖单边小胜"],
        })
    elif match_pressure_type == "qualified_vs_qualified":
        adjustments.update({
            "deep_handicap_risk_delta": 1,
            "favorite_small_win_weight_delta": 1,
            "draw_weight_delta": 1,
            "over_weight_delta": -1,
            "under_weight_delta": 2,
            "rotation_risk_delta": 1,
            "tempo_control_delta": 2,
            "recommended_coverage_shift": ["提高小球和平局", "降低深盘", "降低大比分波胆", "控制投入"],
        })
    elif match_pressure_type == "favorite_must_win":
        adjustments.update({
            "favorite_small_win_weight_delta": 1,
            "underdog_goal_weight_delta": 1,
            "over_weight_delta": 1,
            "late_goal_volatility_delta": 1,
            "chaos_risk_delta": 1,
            "recommended_coverage_shift": ["保留强队方向", "防只赢一球", "防弱队偷一个", "谨慎使用深盘"],
        })
    elif match_pressure_type == "dead_rubber_or_low_motivation":
        adjustments.update({
            "deep_handicap_risk_delta": 1,
            "draw_weight_delta": 1,
            "under_weight_delta": 1,
            "tempo_control_delta": 1,
            "chaos_risk_delta": 1,
            "recommended_coverage_shift": ["降低比赛投资分", "减少深盘暴露", "等待更清晰赔率价值"],
        })
    return adjustments


def build_match_context(api_football_data=None, standings_context=None, match=None):
    fixture = (api_football_data or {}).get("fixture") or {}
    raw = fixture.get("raw") or {}
    league = raw.get("league") or {}
    round_name = str(league.get("round") or fixture.get("round") or "").lower()
    context = default_match_context(group_stage=("group" in round_name or not round_name))
    seed_context = seed_pressure_context(match)
    pressure_context = standings_pressure_context(api_football_data)
    if seed_context:
        context.update(seed_context)
    if pressure_context and not seed_context:
        home_context = {"team": "Home", "pressure_score": pressure_context["home_pressure_score"], "qualification_note": pressure_context["team_a_pressure_reason"]}
        away_context = {"team": "Away", "pressure_score": pressure_context["away_pressure_score"], "qualification_note": pressure_context["team_b_pressure_reason"]}
        match_pressure_type = classify_match_pressure(home_context, away_context)
        context.update(pressure_context)
        context.update({
            "home_context": home_context,
            "away_context": away_context,
            "match_pressure_type": match_pressure_type,
            "behavior_adjustments": compute_behavior_adjustments(match_pressure_type, home_context, away_context),
            "behavior_notes": default_behavior_notes(match_pressure_type, home_context, away_context),
        })
    if standings_context:
        context.update({key: value for key, value in standings_context.items() if key in context})
    return context


def pressure_tempo_bias(pressure):
    if pressure <= 0:
        return -0.18
    if pressure == 1:
        return -0.12
    if pressure == 2:
        return -0.08
    if pressure == 3:
        return 0.00
    if pressure == 4:
        return 0.10
    return 0.18


def game_behavior_engine(match_context):
    context = {**default_match_context(), **(match_context or {})}
    a_pressure = int(context.get("team_a_pressure", 3))
    b_pressure = int(context.get("team_b_pressure", 3))
    if context.get("match_pressure_type") == "neutral_group_context":
        home_context = context.get("home_context") or {"team": "Home", "pressure_score": a_pressure}
        away_context = context.get("away_context") or {"team": "Away", "pressure_score": b_pressure}
        inferred_type = classify_match_pressure(home_context, away_context)
        if inferred_type != "neutral_group_context":
            context["match_pressure_type"] = inferred_type
            context["home_context"] = home_context
            context["away_context"] = away_context
            context["behavior_adjustments"] = compute_behavior_adjustments(inferred_type, home_context, away_context)
            context["behavior_notes"] = default_behavior_notes(inferred_type, home_context, away_context)
    avg_pressure = (a_pressure + b_pressure) / 2
    goal_difference_pressure = clamp(context.get("goal_difference_pressure", 0), -1, 1)
    behavior_adjustments = {**zero_behavior_adjustments(), **(context.get("behavior_adjustments") or {})}
    tempo_shift = pressure_tempo_bias(a_pressure) + pressure_tempo_bias(b_pressure)
    tempo_shift += behavior_adjustments.get("late_goal_volatility_delta", 0) * 0.05
    tempo_shift -= behavior_adjustments.get("tempo_control_delta", 0) * 0.04
    tempo_shift += goal_difference_pressure * 0.10
    tempo_shift = clamp(tempo_shift, -0.35, 0.35)
    if tempo_shift >= 0.20:
        expected_tempo = "high variance / open"
    elif tempo_shift >= 0.06:
        expected_tempo = "slightly open"
    elif tempo_shift <= -0.18:
        expected_tempo = "controlled / rotation risk"
    elif tempo_shift <= -0.06:
        expected_tempo = "cautious"
    else:
        expected_tempo = "balanced"
    if behavior_adjustments.get("rotation_risk_delta", 0) >= 2:
        goal_shift = "favorite conservative"
        handicap_bias = "reduce deep favorite handicap; prefer win by 1 / 2-0 / 2-1"
    elif behavior_adjustments.get("late_goal_volatility_delta", 0) >= 2:
        goal_shift = "late volatility up"
        handicap_bias = "avoid single-path portfolio; add chaos coverage"
    elif behavior_adjustments.get("draw_weight_delta", 0) >= 2:
        goal_shift = "draw and under paths up"
        handicap_bias = "reduce aggressive handicap exposure"
    elif avg_pressure <= 2:
        goal_shift = "low urgency"
        handicap_bias = "shallow handicap and draw paths gain weight"
    else:
        goal_shift = "neutral"
        handicap_bias = "no strong pressure adjustment"
    upset_change = clamp(
        behavior_adjustments.get("underdog_goal_weight_delta", 0) * 0.035
        + behavior_adjustments.get("rotation_risk_delta", 0) * 0.02
        + behavior_adjustments.get("chaos_risk_delta", 0) * 0.025,
        -0.08,
        0.14,
    )
    adjustments = {
        "small_win_shift": behavior_adjustments.get("favorite_small_win_weight_delta", 0) * 0.06,
        "two_goal_shift": -max(0, behavior_adjustments.get("deep_handicap_risk_delta", 0)) * 0.015,
        "big_win_shift": (
            -behavior_adjustments.get("deep_handicap_risk_delta", 0) * 0.045
            + behavior_adjustments.get("over_weight_delta", 0) * 0.02
        ),
        "draw_shift": behavior_adjustments.get("draw_weight_delta", 0) * 0.04,
        "underdog_shift": (
            behavior_adjustments.get("underdog_goal_weight_delta", 0) * 0.04
            + behavior_adjustments.get("chaos_risk_delta", 0) * 0.02
        ),
    }
    return {
        "team_pressure_score": TEAM_PRESSURE_SCORE,
        "input": context,
        "team_a_pressure_label": pressure_label(a_pressure),
        "team_b_pressure_label": pressure_label(b_pressure),
        "home_pressure_score": a_pressure,
        "away_pressure_score": b_pressure,
        "home_context": context.get("home_context"),
        "away_context": context.get("away_context"),
        "qualification_source": context.get("qualification_source"),
        "match_pressure_type": context.get("match_pressure_type"),
        "behavior_adjustments": behavior_adjustments,
        "expected_game_tempo": expected_tempo,
        "expected_goal_distribution_shift": goal_shift,
        "expected_upset_probability_change": upset_change,
        "expected_handicap_movement_bias": handicap_bias,
        "adjustments": adjustments,
        "notes": [
            f"Home pressure {a_pressure}: {pressure_label(a_pressure)}",
            str(context.get("team_a_pressure_reason") or ""),
            f"Away pressure {b_pressure}: {pressure_label(b_pressure)}",
            str(context.get("team_b_pressure_reason") or ""),
            f"Pressure type: {context.get('match_pressure_type')}",
            f"Tempo: {expected_tempo}",
            f"Handicap bias: {handicap_bias}",
            *[str(note) for note in (context.get("behavior_notes") or [])],
        ],
    }


def apply_behavior_to_distribution(rows, behavior):
    if not rows:
        return rows
    adjustments = (behavior or {}).get("adjustments") or {}
    adjusted = []
    for row in rows:
        label = str(row.get("label") or "")
        probability = float(row.get("probability") or 0)
        delta = 0.0
        if "小胜" in label or "1球" in label:
            delta = adjustments.get("small_win_shift", 0)
        elif "赢2球" in label:
            delta = adjustments.get("two_goal_shift", 0)
        elif "3球以上" in label:
            delta = adjustments.get("big_win_shift", 0)
        elif "平局" in label:
            delta = adjustments.get("draw_shift", 0)
        elif "不败" in label:
            delta = adjustments.get("underdog_shift", 0)
        adjusted.append({**row, "probability": max(0.01, probability + delta), "behavior_shift": delta})
    total = sum(row["probability"] for row in adjusted) or 1
    for row in adjusted:
        row["probability"] = row["probability"] / total
    adjusted.sort(key=lambda row: row["probability"], reverse=True)
    return adjusted
