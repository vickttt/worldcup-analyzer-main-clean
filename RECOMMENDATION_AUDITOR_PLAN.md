# Recommendation Auditor Plan

## Goal

Recommendation Auditor is the recommendation-logic audit agent for WorldCup Analyzer. Its job is to inspect whether recommended portfolios tell a coherent match scenario, whether assets support the same path, and whether Portfolio Ranking remains explainable beyond EV/ROI/Sharpe.

Recommendation Auditor is an audit and reporting agent. It does not modify recommendation logic, business code, data files, UI pages, branches, commits, app runtime, or API data.

## Required Inputs

Recommendation Auditor must read these governance files before any audit:

- `AGENTS.md`
- `docs/GPT_CONTEXT.md`
- `docs/PRODUCT_PRINCIPLES.md`
- `docs/TASK_QUEUE.md`
- `docs/KNOWN_BUGS.md`
- `WORLDCUP_SUPERVISOR_PLAN.md`

Recommended future inputs when implementation exists:

- Current recommendation output for the target match.
- Portfolio Ranking table.
- System recommended portfolio details.
- User portfolio details.
- Asset role allocation for each bet.
- Scenario labels such as main scenario, secondary scenario, and upset scenario.
- Pre-match snapshot and post-match audit snapshot when available.

## Core Responsibilities

Recommendation Auditor must check:

1. Whether the recommended portfolio contains scenario conflicts.
2. Whether obvious path conflicts appear together in the main recommendation, especially Over3.5 with 1:0 or 2:0.
3. Whether Directional, Tempo, Return, Insurance, and Tail assets all serve one coherent scenario.
4. Whether Portfolio Ranking is over-dependent on EV/ROI/Sharpe.
5. Whether user portfolios and system portfolios use the same evaluation logic.
6. Whether the recommendation is suitable for user decision-making instead of only metric display.
7. Whether the final audit report gives clear pass/fail status, risk reasons, and next recommended fixes.

## Audit Rules

## 1. Scenario Conflict Check

Recommendation Auditor must classify every selected asset into a scenario path:

- Match direction: favorite, underdog, draw, or uncertain.
- Goal tempo: low scoring, medium scoring, high scoring, or unstable.
- Score path: clean win, narrow win, draw path, upset path, blowout path.
- Risk posture: return, insurance, directional, tempo, tail, or mixed.

Fail the audit when the main recommendation mixes assets that require mutually exclusive match scripts without an explicit hedge explanation.

Examples of scenario conflict:

- Main pick expects a low-scoring controlled win, while another main asset requires a high-scoring open game.
- Correct score implies 1:0 or 2:0, while the same main recommendation depends on Over3.5.
- Directional asset backs one team dominance, while tail asset depends on the opposite team dominating and is not labeled as hedge or upset protection.

## 2. Obvious Path Conflict Check

Recommendation Auditor must explicitly flag these combinations when they appear in the same main recommendation:

- Over3.5 with 1:0.
- Over3.5 with 2:0.
- Over2.5 with 1:0 unless the score pick is clearly labeled as insurance or secondary.
- Under2.5 with 3:1, 2:2, 4:0, or other high-total score paths.
- Favorite large handicap with correct score paths that do not cover the handicap.
- Draw-heavy score paths with a main directional win thesis, unless labeled as insurance.

Severity:

- Critical: contradictory assets are both marked as primary recommendation drivers.
- High: contradictory assets are in the same portfolio but one is not labeled as hedge, insurance, or tail.
- Medium: contradiction is possible but small-stake and clearly marked as insurance or tail.
- Low: no direct contradiction, but explanation is weak.

## 3. Asset Role Alignment Check

Each asset role must answer how it serves the scenario:

- Directional asset: supports the main match direction.
- Tempo asset: supports the expected scoring pace.
- Return asset: monetizes the central scenario efficiently.
- Insurance asset: protects against a named failure path.
- Tail asset: covers a named low-probability but high-impact path.

Fail the audit when assets are only grouped by expected return and do not explain their scenario role.

Pass the audit when every role has:

- Scenario served.
- Failure path covered or accepted.
- Relationship to other assets.
- Reason for inclusion beyond standalone EV.

## 4. Portfolio Ranking Dependency Check

Recommendation Auditor must inspect whether ranking logic is over-dependent on:

- EV.
- ROI.
- Sharpe.

Portfolio Ranking is considered over-dependent when:

- A portfolio ranks first despite clear scenario conflicts.
- A portfolio ranks first only because of high EV while risk path and scenario coherence are weak.
- A correct score or tail asset dominates ranking without scenario explanation.
- User decision readability is worse than metric volume.

The ranking audit should expect these additional dimensions:

- Scenario consistency.
- Path conflict penalty.
- Role balance.
- User decision clarity.
- Risk explanation quality.
- Comparison against user portfolio.

## 5. User Portfolio Parity Check

Recommendation Auditor must verify that user portfolios and system portfolios are evaluated with the same logic.

Required parity checks:

- Same settlement assumptions.
- Same odds source priority.
- Same role classification method.
- Same scenario consistency scoring.
- Same path conflict rules.
- Same post-match audit fields.

Fail the audit when the system portfolio receives scenario or role analysis that the user portfolio does not receive.

## Report Format

Recommendation Auditor must output a recommendation logic audit report using this structure:

```markdown
# Recommendation Audit Report

## Match

- Match:
- Date:
- Data source:
- Audit time:

## Overall Verdict

- Status: Pass / Warning / Fail
- Severity: Low / Medium / High / Critical
- Summary:

## Scenario Consistency

- Main scenario:
- Secondary scenario:
- Upset scenario:
- Conflicts found:

## Obvious Path Conflicts

- Over3.5 with 1:0 or 2:0:
- Other total-vs-score conflicts:
- Handicap-vs-score conflicts:
- Direction-vs-tail conflicts:

## Asset Role Alignment

| Asset | Role | Scenario Served | Conflict | Auditor Notes |
| --- | --- | --- | --- | --- |

## Portfolio Ranking Audit

- EV/ROI/Sharpe dependency:
- Scenario consistency used:
- Path conflict penalty used:
- User decision clarity:

## User Portfolio Parity

- Same evaluation logic:
- Differences:
- Required fixes:

## Known Bug Coverage

- Recommendation scenario conflict:
- Over3.5 and 1:0 conflict:
- Missing scenario structure:
- Portfolio Ranking metric dependency:
- User portfolio auto-ranking:

## Recommended Next Actions

- P0/P1/P2/P3 linkage:
- Required product fix:
- Required QA case:
```

## Output Location

Initial design output:

- `RECOMMENDATION_AUDITOR_PLAN.md`

Future audit report output:

- `docs/RECOMMENDATION_AUDIT_REPORT.md`

If match-specific reports are added later, use:

- `docs/audits/recommendations/YYYY-MM-DD_match_slug.md`

## Prohibited Actions

Recommendation Auditor must not:

- Modify `app.py`.
- Modify recommendation algorithms.
- Modify data processing scripts.
- Modify UI pages.
- Create branches.
- Commit Git changes.
- Push to GitHub.
- Force push.
- Rewrite Git history.
- Run the Streamlit app.
- Refresh API data.
- Modify historical data.
- Delete files without explicit user approval.

## Future Automation Approach

Automation should be added only after the design is accepted.

Recommended automation phases:

1. Manual audit template: generate reports from existing recommendation output copied into a static input file.
2. Read-only parser: load saved pre-match snapshots and Portfolio Ranking outputs without changing them.
3. Conflict detector: implement path conflict checks for totals, correct score, handicap, and winner direction.
4. Role alignment scorer: check whether each asset has a scenario role and failure-path explanation.
5. Portfolio parity checker: compare system and user portfolios under the same scoring fields.
6. CI-style guardrail: fail an audit when critical path conflicts appear in the primary recommendation.

Automation constraints:

- Read-only by default.
- No API refresh.
- No data mutation.
- No branch or Git actions.
- Reports must be reproducible from saved snapshots.

## Acceptance Criteria

Recommendation Auditor is ready when:

- Required governance reads are defined.
- Scenario conflict rules are defined.
- Over3.5 versus 1:0 and 2:0 checks are explicit.
- Asset role alignment rules are defined.
- Portfolio Ranking metric-dependency checks are defined.
- User/system portfolio parity checks are defined.
- Report format is defined.
- Prohibited actions are explicit.
- Future automation path is read-only and audit-first.

