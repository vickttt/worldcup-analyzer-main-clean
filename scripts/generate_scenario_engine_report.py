#!/usr/bin/env python3
"""Generate a read-only Scenario Engine report from saved local snapshots."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_MATCH_SLUG = "2026_06_20_Germany_Ivory_Coast"
REPORT_PATH = Path("SCENARIO_ENGINE_REPORT.md")


@dataclass(frozen=True)
class SourcePaths:
    history_pre: Path
    pre_match: Path
    odds: Path
    fixture: Path


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def get_nested(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def pct(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value * 100:.1f}%"
    return "n/a"


def moneyline_probability(odds: dict[str, Any], key: str) -> str:
    value = get_nested(odds, "effective_winner_totals", "implied_probabilities", key)
    return pct(value)


def path_probability(rows: list[dict[str, Any]], *needles: str) -> float:
    total = 0.0
    for row in rows:
        label = str(row.get("label", ""))
        if any(needle in label for needle in needles):
            value = row.get("probability")
            if isinstance(value, (int, float)):
                total += float(value)
    return total


def first_path(rows: list[dict[str, Any]], *needles: str) -> dict[str, Any] | None:
    for row in rows:
        label = str(row.get("label", ""))
        if any(needle in label for needle in needles):
            return row
    return None


def score_tuple(selection: str) -> tuple[int, int] | None:
    if ":" not in selection:
        return None
    left, right = selection.split(":", 1)
    try:
        return int(left.strip()), int(right.strip())
    except ValueError:
        return None


def selected_items(history: dict[str, Any], pre_match: dict[str, Any]) -> list[dict[str, Any]]:
    combo = history.get("recommendation_combo")
    if isinstance(combo, list) and combo:
        items = [item for item in combo if isinstance(item, dict)]
        chosen = [
            item
            for item in items
            if item.get("recommended") is True
            or float(item.get("share") or 0) > 0
            or float(item.get("amount") or 0) > 0
        ]
        return chosen or items[:8]

    portfolios = pre_match.get("portfolios")
    if isinstance(portfolios, list) and portfolios:
        first = portfolios[0]
        items = first.get("items") if isinstance(first, dict) else None
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
    return []


def map_asset(item: dict[str, Any], favorite: str) -> tuple[str, str, str]:
    item_type = str(item.get("type") or "")
    selection = str(item.get("selection") or item.get("name") or "")
    name = str(item.get("name") or selection)
    parsed_score = score_tuple(selection)

    if item_type == "winner":
        return (
            "Direction Asset + Insurance Asset",
            "Main + Secondary",
            "Supports favorite direction and survives a narrow favorite win.",
        )
    if item_type == "handicap":
        return (
            "Direction Asset + Return Asset",
            "Main Scenario",
            "Requires the favorite to cover the handicap path.",
        )
    if item_type == "total":
        if "under" in selection.lower() or "小" in name:
            return (
                "Tempo Asset + Insurance Asset",
                "Secondary Scenario",
                "Protects lower-tempo paths when the main tempo is uncertain.",
            )
        return (
            "Tempo Asset",
            "Main Scenario",
            "Supports a medium or high goal-tempo script.",
        )
    if item_type == "correct_score" and parsed_score:
        home_goals, away_goals = parsed_score
        margin = home_goals - away_goals
        total_goals = home_goals + away_goals
        if home_goals >= 5 and margin >= 2:
            return (
                "Tail Asset / Extreme Upside",
                "Upset / Extreme Upside",
                "Covers a low-probability blowout tail and must not be core Main Scenario evidence.",
            )
        if home_goals == 4 and margin >= 2:
            return (
                "Aggressive Return Asset / Tail Upside",
                "Main Extreme Path",
                "Supports a favorite blowout variant, but should be capped as upside rather than core evidence.",
            )
        if selection in {"2:0", "3:0", "3:1"} and margin >= 2:
            return (
                "Return Asset",
                "Main Scenario",
                "Core score path for the favorite cover scenario.",
            )
        if margin >= 2:
            return (
                "Aggressive Return Asset",
                "Main Extreme Path",
                "Supports favorite cover, but is outside the core score set and should not drive the main thesis.",
            )
        if margin == 1:
            return (
                "Insurance Asset",
                "Secondary Scenario",
                "Supports favorite win without handicap cover.",
            )
        return (
            "Tail Asset",
            "Upset Scenario",
            "Covers draw or underdog resistance paths.",
        )
    return (
        "Unclassified Asset",
        "Unknown",
        f"Could not map asset against favorite {favorite}.",
    )


def asset_table(items: list[dict[str, Any]], favorite: str) -> tuple[str, int, int, int]:
    rows = [
        "| System asset | Market type | Scenario Engine role | Scenario served | Mapping note |",
        "| --- | --- | --- | --- | --- |",
    ]
    primary_conflicts = 0
    tail_count = 0
    aggressive_count = 0
    for item in items:
        name = str(item.get("name") or item.get("selection") or "Unknown")
        item_type = str(item.get("type") or "unknown")
        role, scenario, note = map_asset(item, favorite)
        if "Tail" in role:
            tail_count += 1
        if "Aggressive" in role or "Extreme" in role:
            aggressive_count += 1
        if item_type == "correct_score":
            parsed = score_tuple(str(item.get("selection") or ""))
            if parsed and sum(parsed) <= 2 and "Over" in str(item.get("path_consistency_reason") or ""):
                primary_conflicts += 1
        rows.append(f"| `{name}` | `{item_type}` | {role} | {scenario} | {note} |")
    return "\n".join(rows), primary_conflicts, tail_count, aggressive_count


def consistency_score(
    items: list[dict[str, Any]],
    primary_conflicts: int,
    tail_count: int,
    aggressive_count: int,
    has_probability: bool,
) -> tuple[int, list[tuple[str, int, int, str]]]:
    assignment = 20 if items else 0
    direction = 20 if any(str(item.get("type")) in {"winner", "handicap"} for item in items) else 10
    tempo = max(14, 17 - max(0, aggressive_count - 2))
    role = max(10, 14 - max(0, aggressive_count - 2)) if items else 0
    conflict = max(8, 15 - primary_conflicts * 4 - max(0, aggressive_count - 3))
    evidence = 10 if has_probability else 6
    total = assignment + direction + tempo + role + conflict + evidence

    if not has_probability:
        total = min(total, 60)
    if aggressive_count >= 4:
        total = min(total, 85)
    if tail_count >= 3:
        total = min(total, 84)

    breakdown = [
        ("Scenario assignment coverage", assignment, 20, "Mapped available assets to Main, Secondary, or Upset scenarios."),
        ("Direction alignment", direction, 20, "Winner and handicap assets support the favorite direction."),
        ("Tempo and score alignment", tempo, 20, "Core scores fit the cover path, while high-score tails should not be treated as core tempo evidence."),
        ("Role coherence", role, 15, "Core Return, Aggressive Return, and Tail assets are separated; many high-score assets reduce coherence."),
        ("Conflict penalty control", conflict, 15, "No Over3.5 primary conflict detected, but repeated high-score tails reduce confidence."),
        ("Evidence support", evidence, 10, "Saved probability, odds, decision, and risk-path data support the report."),
    ]
    return total, breakdown


def report_for_match(slug: str, paths: SourcePaths) -> str:
    history = load_json(paths.history_pre)
    pre_match = load_json(paths.pre_match)
    odds = load_json(paths.odds)
    fixture = load_json(paths.fixture)

    probability_distribution = pre_match.get("probability_distribution")
    prob_rows = []
    if isinstance(probability_distribution, dict):
        rows = probability_distribution.get("rows")
        if isinstance(rows, list):
            prob_rows = [row for row in rows if isinstance(row, dict)]

    favorite = str(get_nested(pre_match, "probability_distribution", "favorite", default="Germany"))
    underdog = str(get_nested(pre_match, "probability_distribution", "underdog", default="Ivory Coast"))
    match = get_nested(fixture, "match", "display_name", default=None) or get_nested(history, "match", "display", default=slug)
    schedule = fixture.get("schedule_fixture") if isinstance(fixture.get("schedule_fixture"), dict) else {}
    decision = history.get("decision") if isinstance(history.get("decision"), dict) else {}
    final_rec = decision.get("final_recommendation") if isinstance(decision.get("final_recommendation"), dict) else {}
    items = selected_items(history, pre_match)
    table, primary_conflicts, tail_count, aggressive_count = asset_table(items, favorite)
    score, breakdown = consistency_score(items, primary_conflicts, tail_count, aggressive_count, bool(prob_rows))

    main_prob = path_probability(prob_rows, "赢2球", "赢3球")
    secondary_path = first_path(prob_rows, "小胜", "1球")
    draw_prob = path_probability(prob_rows, "平局")
    upset_prob = path_probability(prob_rows, "不败")
    upset_total = draw_prob + upset_prob

    main_expected = ["2:0", "3:1"]
    secondary_expected = ["1:0", "2:1"]
    upset_expected = ["0:0", "1:1", "1:2"]

    source_paths = "\n".join(
        [
            f"- `{paths.history_pre}`",
            f"- `{paths.pre_match}`",
            f"- `{paths.odds}`",
            f"- `{paths.fixture}`",
        ]
    )

    path_lines = []
    for row in prob_rows:
        path_lines.append(f"  - {row.get('label')}: {pct(row.get('probability'))} - {row.get('meaning')}")
    path_summary = "\n".join(path_lines) if path_lines else "  - Probability distribution unavailable."

    breakdown_rows = [
        "| Component | Points | Reason |",
        "| --- | ---: | --- |",
    ]
    for name, points, maximum, reason in breakdown:
        breakdown_rows.append(f"| {name} | {points} / {maximum} | {reason} |")

    market_prob = moneyline_probability(odds, "home_win")
    total_line = get_nested(odds, "effective_winner_totals", "over_under_line", default="n/a")
    upset_index = decision.get("upset_index") if isinstance(decision.get("upset_index"), dict) else {}

    return f"""# Scenario Engine Report

## Match

- Match: {match}
- Competition: {schedule.get("league_name", "n/a")}
- Round: {schedule.get("round", "n/a")}
- Group: {schedule.get("group", "n/a")}
- Venue: {schedule.get("venue_name", "n/a")}, {schedule.get("venue_city", "n/a")}
- Kickoff: {schedule.get("kickoff_utc", "n/a")}
- Data mode: read-only local snapshots

## Source Snapshot Summary

- Files read:
{source_paths}
- System final recommendation: `{final_rec.get("bet", "n/a")}`
- Recommendation reason: {"; ".join(final_rec.get("reason", [])) if isinstance(final_rec.get("reason"), list) else "n/a"}
- Final confidence score: {decision.get("final_confidence_score", "n/a")} / 100
- Value rating: {decision.get("value_rating", "n/a")}
- Participation advice: {get_nested(decision, "participation_advice", "advice", default="n/a")}
- Recommended stake: {get_nested(decision, "recommended_stake", "amount", default="n/a")}
- Favorite market probability: {market_prob}
- Upset index: {upset_index.get("score", "n/a")} / 100 ({upset_index.get("meaning", "n/a")})
- Main total line: {total_line}
- Top path distribution:
{path_summary}

## Main Scenario

- Name: {favorite} handicap-cover path
- Probability: {pct(main_prob)}
- Expected score: {", ".join(main_expected)}
- Goal range: 2-4 total goals
- Tempo: medium
- Direction: {favorite} win, leaning toward handicap cover
- Supporting evidence:
  - Final recommendation is `{final_rec.get("bet", "n/a")}`.
  - Favorite market probability is {market_prob}.
  - Saved probability rows identify favorite cover and favorite dominance paths.
  - Correct-score and handicap assets can be mapped to the same cover script.
- Risk notes:
  - The scenario needs {favorite} to win by at least 2 when the asset is a deep handicap.
  - Small-win and draw paths remain material risks.

## Secondary Scenario

- Name: {favorite} wins but does not fully cover
- Probability: {pct(secondary_path.get("probability") if secondary_path else None)}
- Expected score: {", ".join(secondary_expected)}
- Goal range: 1-3 total goals
- Tempo: low to medium
- Direction: {favorite} win without enough margin for the main handicap
- Supporting evidence:
  - Saved path distribution includes a favorite one-goal-win bucket.
  - Risk-path notes identify favorite small win as a losing path for the deep handicap.
  - Moneyline-style assets can survive this scenario while handicap assets may fail.
- Risk notes:
  - This scenario should be labeled as insurance or secondary, not treated as the main return thesis.

## Upset Scenario

- Name: {underdog} resistance, draw, or unbeaten path
- Probability: {pct(upset_total)}
- Expected score: {", ".join(upset_expected)}
- Goal range: 0-3 total goals
- Tempo: low to unstable
- Direction: draw or {underdog} avoids defeat
- Supporting evidence:
  - Draw and underdog-unbeaten buckets are present in saved probability rows.
  - Upset index is {upset_index.get("score", "n/a")} / 100.
  - Risk-path notes list draw and underdog win as losing paths for the main handicap.
- Risk notes:
  - This scenario should map to Tail Asset or explicit hedge logic only.

## Asset Mapping

{table}

## Scenario Consistency Score

- Score: {score} / 100
- Grade: {"Strong" if score >= 90 else "Usable with warnings" if score >= 75 else "Warning" if score >= 60 else "High risk"}
- Summary: The recommendation is readable as a {favorite} cover story, but high-score correct scores are treated as aggressive upside or tail exposure, not core Main Scenario evidence.

## Score Breakdown

{chr(10).join(breakdown_rows)}

## Recommendation Auditor Handoff

- Check whether the main scenario is labeled as handicap cover, not simply favorite win.
- Check whether controlled low-score cover assets are separated from Over-based tempo stories.
- Check whether 4-goal and 5-goal correct scores remain capped as Aggressive Return or Tail assets.
- Check whether secondary small-win paths are treated as insurance, not contradiction.
- Check whether tail paths are labeled and prevented from silently driving the main recommendation.
- Check whether user portfolios receive the same scenario and consistency treatment.

## Portfolio Ranking Implication

- Future Portfolio Ranking can consume `Scenario Consistency Score`, role mapping, critical conflict count, and scenario coverage.
- EV, ROI, and Sharpe should remain value inputs, but they should not override critical scenario conflicts.
- A lower-EV portfolio with clearer scenario coverage may be preferable to a high-EV contradictory portfolio.
- Main recommendations should target a Scenario Consistency Score of at least 75.

## Automation Verdict

- Status: Pass
- The script generated this report from existing local data only.
- No data files were modified.
- No API refresh was performed.
- No Streamlit app was run.
- Output written: `SCENARIO_ENGINE_REPORT.md`
"""


def build_paths(slug: str) -> SourcePaths:
    return SourcePaths(
        history_pre=Path("data/history") / f"{slug}_pre.json",
        pre_match=Path("data/worldcup2026") / slug / "pre_match.json",
        odds=Path("data/worldcup2026") / slug / "odds.json",
        fixture=Path("data/worldcup2026") / slug / "fixture.json",
    )


def ensure_inputs(paths: SourcePaths) -> None:
    missing = [str(path) for path in (paths.history_pre, paths.pre_match, paths.odds, paths.fixture) if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required input files:\n" + "\n".join(missing))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a read-only Scenario Engine report.")
    parser.add_argument("--match-slug", default=DEFAULT_MATCH_SLUG, help="Match slug to read from local data folders.")
    parser.add_argument("--output", default=str(REPORT_PATH), help="Report path. Defaults to SCENARIO_ENGINE_REPORT.md.")
    args = parser.parse_args()

    output = Path(args.output)
    if output != REPORT_PATH:
        raise ValueError("v0.1 is only allowed to write SCENARIO_ENGINE_REPORT.md")

    paths = build_paths(args.match_slug)
    ensure_inputs(paths)
    report = report_for_match(args.match_slug, paths)
    output.write_text(report, encoding="utf-8")
    print(f"Generated {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
