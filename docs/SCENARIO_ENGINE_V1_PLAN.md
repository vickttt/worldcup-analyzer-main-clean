# Scenario Engine v1 Plan

## Goal

Scenario Engine v1 is the core reasoning layer for WorldCup Analyzer. It makes every recommendation portfolio serve a match scenario first, then use odds metrics second.

The engine must prevent assets from competing against each other without explanation. A portfolio is valid only when its Direction, Tempo, Return, Insurance, and Tail assets support a coherent scenario structure.

Scenario Engine v1 is a design plan only. It does not modify business code, create branches, commit Git changes, run the app, or refresh API data.

## Scenario System

Scenario Engine v1 must produce at least three scenario layers for every match:

## 1. Main Scenario

The highest-confidence match script.

Required fields:

- Probability: expected likelihood of this scenario.
- Expected score: one or more representative scores.
- Expected goal range: expected total-goals interval.
- Expected tempo: low, medium, high, or unstable.
- Match direction: favorite win, underdog win, draw, or uncertain.
- Supporting evidence: team strength, lineup, injuries, form, market signal, odds movement, historical pattern, tactical matchup, and data completeness.
- Risk notes: what would break this scenario.

Purpose:

- Main recommendation assets must primarily serve this scenario.
- Primary Direction, Tempo, and Return assets should align with this scenario.

## 2. Secondary Scenario

A plausible alternative script that does not fully overturn the Main Scenario.

Required fields:

- Probability.
- Expected score.
- Expected goal range.
- Expected tempo.
- Match direction.
- Supporting evidence.
- Difference from Main Scenario.
- Risk notes.

Purpose:

- Insurance assets usually serve this scenario.
- Some Return assets may serve it if they improve portfolio robustness without contradicting the Main Scenario.
- Secondary Scenario cannot silently become the real driver of the main recommendation.

## 3. Upset Scenario

A lower-probability but high-impact script where the expected direction or tempo breaks.

Required fields:

- Probability.
- Expected score.
- Expected goal range.
- Expected tempo.
- Match direction.
- Supporting evidence.
- Upset trigger: red card risk, weak lineup, tactical mismatch, market mispricing, fatigue, injury, weather, or high variance.
- Risk notes.

Purpose:

- Tail assets serve this scenario.
- Upset assets must be labeled as tail or hedge.
- Upset Scenario assets must not be mixed into the main recommendation as if they support the Main Scenario.

## Scenario Probability Rules

- Scenario probabilities should sum to approximately 100.
- Main Scenario should normally have the highest probability.
- Secondary Scenario should explain the most realistic deviation from Main.
- Upset Scenario should explain the most important low-probability risk.
- If probabilities are uncertain, the engine must mark data confidence as low instead of pretending precision.

## Scenario Output Schema

Scenario Engine v1 should output this conceptual structure:

```yaml
match:
  home:
  away:
  date:
scenarios:
  main:
    name:
    probability:
    expected_scores:
    goal_range:
    tempo:
    direction:
    supporting_evidence:
    risk_notes:
    data_confidence:
  secondary:
    name:
    probability:
    expected_scores:
    goal_range:
    tempo:
    direction:
    supporting_evidence:
    difference_from_main:
    risk_notes:
    data_confidence:
  upset:
    name:
    probability:
    expected_scores:
    goal_range:
    tempo:
    direction:
    upset_triggers:
    supporting_evidence:
    risk_notes:
    data_confidence:
```

## Asset Mapping Rules

Assets must serve scenarios. Assets must not be selected only because their standalone EV, ROI, or Sharpe is high.

## Direction Asset

Purpose:

- Expresses match direction: winner, draw avoidance, handicap side, or dominant team thesis.

Mapping rule:

- Must map to Main Scenario unless explicitly labeled as Secondary or Upset hedge.
- Must not conflict with the main expected score path.

Examples:

- Main Scenario: favorite controlled win.
- Direction Asset: favorite moneyline or favorite handicap.

## Tempo Asset

Purpose:

- Expresses expected match pace and scoring environment.

Mapping rule:

- Must map to the scenario goal range and expected tempo.
- Over assets must align with medium/high tempo scenarios.
- Under assets must align with low/control scenarios.

Conflict example:

- Over3.5 cannot serve a Main Scenario with expected score 1:0 or 2:0.

## Return Asset

Purpose:

- Monetizes the central scenario with efficient payout.

Mapping rule:

- Should usually map to Main Scenario.
- Can map to Secondary Scenario only when clearly labeled and not presented as the main thesis.
- Must explain why it improves portfolio return without breaking scenario consistency.

Examples:

- Correct score 2:0 as Return Asset for a controlled favorite win.
- Handicap win as Return Asset for a dominance scenario.

## Insurance Asset

Purpose:

- Protects against a named failure path of the Main Scenario.

Mapping rule:

- Must map to Secondary Scenario or a defined risk note.
- Must explain which Main Scenario failure it covers.
- Must not be counted as proof that the Main Scenario is stronger.

Examples:

- Draw coverage when Main Scenario is narrow favorite win.
- Under bet when Main Scenario has direction confidence but tempo uncertainty.

## Tail Asset

Purpose:

- Covers a low-probability, high-impact Upset Scenario.

Mapping rule:

- Must map to Upset Scenario.
- Must be small, explicit, and labeled as tail or upset protection.
- Must not drive the main recommendation ranking.

Examples:

- Underdog exact score.
- High-odds upset winner.
- Late-game volatility score path.

## Scenario Consistency Score

Scenario Consistency Score is a 0-100 score measuring whether a portfolio tells one coherent match story.

Recommended scoring model:

| Component | Points | Rule |
| --- | ---: | --- |
| Scenario assignment coverage | 20 | Every asset maps to Main, Secondary, or Upset Scenario. |
| Direction alignment | 20 | Direction assets align with the scenario match direction. |
| Tempo and score alignment | 20 | Totals and correct scores match expected goal range and tempo. |
| Role coherence | 15 | Direction, Tempo, Return, Insurance, and Tail assets each have a clear purpose. |
| Conflict penalty control | 15 | No obvious path conflicts, or conflicts are explicitly labeled as hedge/tail. |
| Evidence support | 10 | Scenario has clear supporting evidence and data confidence. |

Score interpretation:

- 90-100: Strong scenario consistency. Portfolio is coherent and audit-ready.
- 75-89: Usable. Minor explanation or role clarity issues.
- 60-74: Warning. Portfolio may be usable but contains weak links or unclear hedges.
- 40-59: High risk. Scenario logic is unstable or metric-driven.
- 0-39: Fail. Portfolio contains major scenario conflicts.

Critical conflict override:

- If Over3.5 and 1:0 or 2:0 both appear as primary drivers, maximum score is 40.
- If assets point to opposite match winners without hedge labels, maximum score is 50.
- If no scenario labels exist, maximum score is 60 even if EV/ROI/Sharpe are high.
- If a Tail Asset drives first place ranking without explanation, maximum score is 65.

## Relationship With Recommendation Auditor

Scenario Engine outputs the scenario structure and asset mapping.

Recommendation Auditor checks whether the output is logically consistent.

Scenario Engine must output:

- Main Scenario.
- Secondary Scenario.
- Upset Scenario.
- Probability for each scenario.
- Expected scores.
- Goal ranges.
- Tempo labels.
- Supporting evidence.
- Risk notes.
- Asset-to-scenario mapping.
- Asset role labels.
- Scenario Consistency Score.
- Any known conflict flags.

Recommendation Auditor must check:

- Whether the scenarios are internally coherent.
- Whether assets actually serve their assigned scenario.
- Whether Over3.5 conflicts with 1:0, 2:0, or other low-score paths.
- Whether Insurance and Tail assets are properly labeled.
- Whether Portfolio Ranking respected the Scenario Consistency Score.
- Whether user and system portfolios use the same scenario logic.

Collaboration rule:

- Scenario Engine is the producer.
- Recommendation Auditor is the reviewer.
- A recommendation should not be considered ready if Recommendation Auditor reports High or Critical scenario conflict.

## Relationship With Portfolio Ranking

Portfolio Ranking must move from metric-first to scenario-first ranking.

Future Ranking should use:

- EV.
- ROI.
- Sharpe.
- Scenario Consistency Score.

Recommended v1 ranking principle:

- EV/ROI/Sharpe measure value.
- Scenario Consistency Score measures whether the value belongs in the same match story.
- A portfolio with lower EV but higher consistency may outrank a high-EV contradictory portfolio.

Recommended conceptual formula:

```text
Portfolio Score =
  Value Score from EV/ROI/Sharpe
  + Scenario Consistency Score impact
  + Role Balance impact
  - Path Conflict penalty
  - User Decision Complexity penalty
```

Minimum ranking guardrails:

- Critical scenario conflict cannot rank first.
- Main recommendation must have Scenario Consistency Score >= 75.
- Score below 60 must be marked as audit warning.
- Tail-heavy portfolios cannot rank first unless explicitly labeled as aggressive/upset portfolio.
- User portfolio and system portfolio must be scored with the same consistency logic.

## Report Format

Future Scenario Engine reports should use this structure:

```markdown
# Scenario Engine Report

## Match

- Match:
- Date:
- Data source:
- Data confidence:

## Main Scenario

- Probability:
- Expected score:
- Goal range:
- Tempo:
- Direction:
- Supporting evidence:
- Risk notes:

## Secondary Scenario

- Probability:
- Expected score:
- Goal range:
- Tempo:
- Direction:
- Supporting evidence:
- Difference from Main:
- Risk notes:

## Upset Scenario

- Probability:
- Expected score:
- Goal range:
- Tempo:
- Direction:
- Upset triggers:
- Supporting evidence:
- Risk notes:

## Asset Mapping

| Asset | Role | Scenario | Reason | Conflict Risk |
| --- | --- | --- | --- | --- |

## Scenario Consistency Score

- Score:
- Grade:
- Main drivers:
- Penalties:
- Critical flags:

## Portfolio Ranking Inputs

- EV:
- ROI:
- Sharpe:
- Consistency Score:
- Ranking notes:
```

## Prohibited Actions

Scenario Engine v1 design must not:

- Modify `app.py`.
- Modify recommendation algorithms.
- Modify data processing scripts.
- Modify UI pages.
- Create branches.
- Commit Git changes.
- Push to GitHub.
- Run the Streamlit app.
- Refresh API data.
- Modify historical data.
- Delete files without explicit user approval.

## Future Automation Path

Automation should be read-only first.

Phases:

1. Static design validation: confirm reports include Main, Secondary, and Upset scenarios.
2. Snapshot parser: read saved pre-match snapshots without modifying them.
3. Asset mapper: classify assets into Direction, Tempo, Return, Insurance, and Tail.
4. Consistency scorer: calculate Scenario Consistency Score from saved recommendation output.
5. Auditor integration: pass Scenario Engine output to Recommendation Auditor.
6. Ranking integration: add Consistency Score to Portfolio Ranking after audit rules are stable.

Automation constraints:

- No API refresh.
- No data mutation.
- No app run required.
- No Git operations.
- Reports must be reproducible from saved snapshots.

## Acceptance Criteria

Scenario Engine v1 design is ready when:

- Main, Secondary, and Upset Scenario structures are defined.
- Each scenario includes probability, expected score, goal range, tempo, and evidence.
- Asset mapping rules are defined for Direction, Tempo, Return, Insurance, and Tail assets.
- Scenario Consistency Score is defined from 0 to 100.
- Critical conflict overrides are explicit.
- Recommendation Auditor relationship is clear.
- Portfolio Ranking relationship is clear.
- Prohibited actions and read-only automation path are defined.

