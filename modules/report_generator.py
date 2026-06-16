from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def percent(value):
    return f"{value * 100:.1f}%"


def money(value):
    if value is None:
        return "-"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number >= 1_000_000:
        return f"${number / 1_000_000:.2f}M"
    if number >= 1_000:
        return f"${number / 1_000:.1f}K"
    return f"${number:.0f}"


def format_value(value):
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def format_kickoff(value):
    if not value:
        return "-"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    local_time = parsed.astimezone(ZoneInfo("Asia/Shanghai"))
    return local_time.strftime("%Y-%m-%d %H:%M CST")


def summarize_form(fixtures, team_id):
    results = []
    goals_for = 0
    goals_against = 0

    for item in (fixtures or [])[:5]:
        teams = item.get("teams", {})
        goals = item.get("goals", {})
        home = teams.get("home", {})
        home_goals = goals.get("home")
        away_goals = goals.get("away")
        if home_goals is None or away_goals is None:
            continue

        is_home = home.get("id") == team_id
        team_goals = home_goals if is_home else away_goals
        opponent_goals = away_goals if is_home else home_goals
        goals_for += team_goals
        goals_against += opponent_goals

        if team_goals > opponent_goals:
            results.append("W")
        elif team_goals < opponent_goals:
            results.append("L")
        else:
            results.append("D")

    return {
        "form": results,
        "gf": goals_for,
        "ga": goals_against,
    }


def format_fixture_lines(api_football_data):
    fixture = (api_football_data or {}).get("fixture")
    if not fixture:
        return [
            "## Match Overview",
            "",
            "Match fixture not available.",
        ]

    raw = fixture.get("raw", {})
    fixture_info = raw.get("fixture", {})
    league = raw.get("league", {})
    venue = fixture_info.get("venue", {}) or {}
    home_name = format_value(fixture.get("home_team", {}).get("name"))
    away_name = format_value(fixture.get("away_team", {}).get("name"))
    competition = " ".join(
        str(part)
        for part in [league.get("name"), league.get("season")]
        if part
    )

    return [
        "## Match Overview",
        "",
        f"### {home_name} vs {away_name}",
        "",
        f"- Competition: {competition or '-'}",
        f"- Stage: {format_value(league.get('round'))}",
        f"- Kickoff: {format_kickoff(fixture_info.get('date'))}",
        f"- Venue: {format_value(venue.get('name'))}, {format_value(venue.get('city'))}",
    ]


def format_match_winner_lines(odds):
    if not odds.get("found", True):
        return [
            "## Match Winner",
            "",
            f"- 状态：{odds.get('message')}",
        ]

    implied = odds.get("implied_probabilities") or {}
    raw = odds.get("raw_probabilities") or {}
    return [
        "## Match Winner",
        "",
        f"- Home：{format_value(odds['home_win'])}",
        f"- Draw：{format_value(odds['draw'])}",
        f"- Away：{format_value(odds['away_win'])}",
        f"- Home 去水前概率：{percent(raw.get('home_win', 0))}",
        f"- Draw 去水前概率：{percent(raw.get('draw', 0))}",
        f"- Away 去水前概率：{percent(raw.get('away_win', 0))}",
        f"- Home 隐含概率：{percent(implied.get('home_win', 0))}",
        f"- Draw 隐含概率：{percent(implied.get('draw', 0))}",
        f"- Away 隐含概率：{percent(implied.get('away_win', 0))}",
    ]


def format_injuries_lines(api_football_data):
    injuries = (api_football_data or {}).get("injuries")
    error = (api_football_data or {}).get("injuries_error")
    lines = ["## Injuries", ""]

    if error:
        return lines + [f"- 状态：{error}"]

    if not injuries:
        return lines + ["No Reported Injuries"]

    for item in injuries:
        team = item.get("team", {}).get("name")
        player = item.get("player", {}).get("name")
        reason = item.get("player", {}).get("reason")
        injury_type = item.get("player", {}).get("type")
        lines.append(
            f"- {format_value(team)} / {format_value(player)} / "
            f"{format_value(injury_type)} / {format_value(reason)}"
        )

    return lines


def format_lineups_lines(api_football_data):
    lineups = (api_football_data or {}).get("lineups")
    error = (api_football_data or {}).get("lineups_error")
    lines = ["## Lineups", ""]

    if error:
        return lines + [f"- 状态：{error}"]

    if not lineups:
        return lines + ["Official Lineups Not Released"]

    for lineup in lineups:
        team = lineup.get("team", {}).get("name")
        formation = lineup.get("formation")
        start_players = lineup.get("startXI", [])
        names = [
            item.get("player", {}).get("name")
            for item in start_players
            if item.get("player", {}).get("name")
        ]
        lines.append(f"- {format_value(team)} 阵型：{format_value(formation)}")
        lines.append(f"  首发：{', '.join(names) if names else '无'}")

    return lines


def format_opportunity_lines(rating):
    return [
        "## 机会评级",
        "",
        f"- 评级：{rating.get('grade', '放弃')}",
        f"- 推荐方向：{rating.get('recommendation', 'No bet')}",
        f"- 风险等级：{rating.get('risk_level', '高')}",
        f"- 价值信号：{rating.get('value_signal', 'No')}",
        f"- 推荐理由：{rating.get('reason') or rating.get('summary')}",
    ]


def format_value_analysis_lines(value_analysis):
    lines = ["## Value Analysis", ""]

    if not value_analysis or not value_analysis.get("available"):
        message = (value_analysis or {}).get(
            "message",
            "Value Analysis requires both The Odds API and Polymarket probabilities.",
        )
        return lines + [f"- 状态：{message}"]

    rows = value_analysis.get("rows", [])
    main = max(rows, key=lambda row: abs(row.get("difference", 0))) if rows else None
    if value_analysis.get("has_value"):
        lines.append("Potential Value Opportunity Detected")
    else:
        lines.append("No Significant Market Disagreement")

    if main:
        lines.extend([
            "",
            f"Odds API: {percent(main['odds_api'])}",
            "",
            f"Polymarket: {percent(main['polymarket'])}",
            "",
            f"Difference: {percent(abs(main['difference']))}",
        ])

    return lines


def format_asian_handicap_lines(odds):
    lines = ["## Asian Handicap", ""]
    markets = odds.get("asian_handicap") if odds else None
    if not markets:
        return lines + ["The Odds API did not return this market"]

    for market in markets:
        lines.extend([
            f"- Line：{format_value(market.get('line'))}",
            f"  Home Odds：{format_value(market.get('home_odds'))}",
            f"  Away Odds：{format_value(market.get('away_odds'))}",
            f"  Source：{format_value(market.get('bookmaker'))}",
        ])
    return lines


def format_over_under_lines(odds):
    lines = ["## Over/Under", ""]
    markets = odds.get("over_under") if odds else None
    if not markets:
        return lines + ["The Odds API did not return this market"]

    for market in markets:
        lines.extend([
            f"- Line：{format_value(market.get('line'))} Goals",
            f"  Over Odds：{format_value(market.get('over_odds'))}",
            f"  Under Odds：{format_value(market.get('under_odds'))}",
            f"  Source：{format_value(market.get('bookmaker'))}",
        ])
    return lines


def format_betting_opinion_lines(betting_opinion):
    opinion = betting_opinion or {}
    return [
        "## Betting Opinion",
        "",
        "Match Winner:",
        opinion.get("match_winner", "No view"),
        "",
        "Reason:",
        opinion.get("match_winner_reason", "-"),
        "",
        "Asian Handicap:",
        opinion.get("asian_handicap", "No view"),
        "",
        "Reason:",
        opinion.get("asian_handicap_reason", "-"),
        "",
        "Goals:",
        opinion.get("over_under", "No view"),
        "",
        "Reason:",
        opinion.get("over_under_reason", "-"),
        "",
        f"Confidence: {opinion.get('confidence', 50)} / 100",
    ]


def format_recent_form_lines(api_football_data):
    data = api_football_data or {}
    fixture_result = data.get("fixture_result") or {}
    fixture = data.get("fixture") or {}
    teams = [
        (
            fixture_result.get("home_team") or fixture.get("home_team") or {},
            data.get("home_recent") or [],
        ),
        (
            fixture_result.get("away_team") or fixture.get("away_team") or {},
            data.get("away_recent") or [],
        ),
    ]

    lines = ["## Recent Form", ""]
    has_team = False
    for team, fixtures in teams:
        team_name = team.get("name")
        team_id = team.get("id")
        if not team_name or not team_id:
            continue
        has_team = True
        summary = summarize_form(fixtures, team_id)
        lines.extend([
            team_name,
            "",
            " ".join(summary["form"]) if summary["form"] else "Recent Form Unavailable",
            "",
            f"GF: {summary['gf']}",
            f"GA: {summary['ga']}",
            "",
        ])

    return lines if has_team else []


def format_polymarket_lines(match, polymarket):
    lines = ["## Polymarket", ""]
    if not polymarket.get("found", True):
        return lines + [
            f"Source: {polymarket.get('source', '-')}",
            f"Status: {polymarket.get('message', '-')}",
        ]

    return lines + [
        f"{match['home_cn']}: {percent(polymarket.get('home_win', 0))}",
        "",
        f"Draw: {percent(polymarket.get('draw', 0))}",
        "",
        f"{match['away_cn']}: {percent(polymarket.get('away_win', 0))}",
        "",
        f"Volume: {money(polymarket.get('volume'))}",
        "",
        f"Liquidity: {money(polymarket.get('liquidity'))}",
    ]


def build_report(
    match,
    odds,
    polymarket,
    news,
    probabilities,
    scores,
    rating,
    api_football_data=None,
    value_analysis=None,
    betting_opinion=None,
):
    lines = [
        f"# {match['display_name']} 分析报告",
        "",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        *format_fixture_lines(api_football_data),
        "",
        *format_betting_opinion_lines(betting_opinion),
        "",
        *format_recent_form_lines(api_football_data),
        "",
        *format_match_winner_lines(odds),
        "",
        *format_asian_handicap_lines(odds),
        "",
        *format_over_under_lines(odds),
        "",
        *format_polymarket_lines(match, polymarket),
        "",
        *format_value_analysis_lines(value_analysis),
        "",
        *format_injuries_lines(api_football_data),
        "",
        *format_lineups_lines(api_football_data),
    ]
    return "\n".join(lines)


def save_report(report, match, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    safe_name = match["display_name"].replace(" ", "_").replace("/", "_")
    path = Path(output_dir) / f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path.write_text(report, encoding="utf-8")
    return path
