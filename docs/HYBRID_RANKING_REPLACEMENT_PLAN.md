# Hybrid Ranking Replacement Plan

Date: 2026-06-21

Scope: design only. This plan does not modify code, change sorting, change recommendation logic, update UI, modify data files, create branches, commit, or push.

## 1. Background

Post-Match Validation has reached 12 valid validations:

- Legacy ROI: -40.8%.
- Scenario ROI: -2.1%.
- Legacy Wins: 3.
- Scenario Wins: 3.
- Draws: 6.
- Promotion Status: `Enter Scenario Guardrails Phase`.

Conclusion:

- Legacy Ranking should no longer remain the only ranking authority.
- Scenario Ranking should not fully replace Legacy immediately because Scenario ROI is better but still negative.
- The next ranking system should combine value metrics and scenario discipline into a Hybrid Ranking.

## 2. Product Goal

Hybrid Ranking should become the future main Portfolio Ranking order.

It must preserve the useful parts of Legacy Ranking while adding scenario-based guardrails:

- Keep EV / ROI / Sharpe as value inputs.
- Add Scenario Rank and Scenario Consistency as first-class inputs.
- Penalize tail-heavy, pure-tempo, and main-scenario-conflicting portfolios.
- Reward portfolios that clearly serve the Main Scenario and carry named Secondary Insurance.
- Keep Legacy Ranking available as a fallback and reference.

## 3. Hybrid Score Inputs

Hybrid Score should use at least these fields:

| Input | Purpose |
| --- | --- |
| EV | Expected value signal from existing value model. |
| ROI | Capital efficiency signal. |
| Sharpe | Stability / risk-adjusted return signal. |
| Scenario Rank | Relative scenario-aware rank. |
| Shadow Verdict | Agreement / Watch / Disagreement / Blocker Candidate guardrail. |
| Scenario Consistency Score | 0-100 score for whether the portfolio serves a coherent script. |
| Tail Exposure | Penalizes excessive correct-score / extreme upside dependence. |
| Pure Tempo Asset Penalty | Prevents pure pace bets from becoming default recommendations alone. |
| Main Scenario Coverage | Rewards portfolios that pay or remain valid when Main Scenario happens. |
| Secondary Insurance Coverage | Rewards portfolios that survive named failure paths. |
| Max Loss | Penalizes unacceptable downside. |

## 4. Conceptual Hybrid Score Formula

Recommended v0.1 formula:

```text
Hybrid Score =
  Value Layer
  + Scenario Layer
  + Coverage Layer
  + Stability Layer
  - Conflict Penalty
  - Tail / Pure Tempo Penalty
  - Max Loss Penalty
  - Decision Complexity Penalty
```

Suggested weights:

| Layer | Weight | Inputs |
| --- | ---: | --- |
| Value Layer | 30 | EV, ROI, Sharpe |
| Scenario Layer | 30 | Scenario Rank, Scenario Consistency Score, Shadow Verdict |
| Coverage Layer | 20 | Main Scenario Coverage, Secondary Insurance Coverage |
| Stability Layer | 10 | Max Loss, Sharpe stability adjustment |
| Penalties | -10 to -50 | Tail exposure, pure tempo, conflict flags, decision complexity |

Suggested split:

```text
Value Layer, max 30:
  EV: 10
  ROI: 10
  Sharpe: 10

Scenario Layer, max 30:
  Scenario Rank bonus: 10
  Scenario Consistency Score: 15
  Shadow Verdict adjustment: 5

Coverage Layer, max 20:
  Main Scenario Coverage: 12
  Secondary Insurance Coverage: 8

Stability Layer, max 10:
  Max Loss control: 6
  Sharpe stability adjustment: 4
```

Shadow Verdict adjustment:

| Shadow Verdict | Adjustment |
| --- | ---: |
| Agreement | +5 |
| Watch | +1 |
| Disagreement | -8 |
| Blocker Candidate | -20 and default-ineligible |

Scenario Rank bonus:

| Scenario Rank | Bonus |
| --- | ---: |
| 1 | +10 |
| 2 | +6 |
| 3 | +3 |
| 4+ | 0 |

## 5. Main Sorting Logic

Future Portfolio Ranking should sort by:

```text
Hybrid Score desc
then Scenario Consistency Score desc
then lower Max Loss
then Legacy Score desc
```

Important change:

```text
Legacy score no longer independently decides the main Portfolio Ranking order.
```

Legacy score becomes:

- a component in the Value Layer,
- a tie-breaker,
- a fallback reference,
- and a diagnostic signal.

## 6. Guardrails

Hard guardrails:

- `Shadow Verdict = Blocker Candidate` cannot be default recommendation.
- Critical scenario conflict cannot rank first.
- Pure Tempo Asset cannot become default recommendation by itself.
- Tail-heavy portfolio cannot become default recommendation unless explicitly selected as aggressive/upset exposure.
- Portfolio that conflicts with the Main Scenario must be downgraded.
- Scenario Consistency Score below 60 cannot be default recommendation.

Soft guardrails:

- `Shadow Verdict = Disagreement` cannot default to rank 1 unless Hybrid Score is clearly superior and the risk explanation is explicit.
- Scenario Rank 1 receives a weighted reward.
- Scenario Consistency Score below 75 should show warning and lose Hybrid points.
- Main Scenario Coverage below target should reduce rank even when EV is strong.
- Secondary Insurance Coverage should improve stable portfolios over all-or-nothing portfolios.
- Max Loss should reduce Hybrid Score when downside is not compensated by scenario quality.

Suggested Disagreement exception:

```text
A Disagreement portfolio may rank first only if:
  Hybrid Score lead >= 8 points,
  Scenario Consistency Score >= 80,
  no Critical or High conflict exists,
  Tail Exposure is not heavy,
  and the ranking explanation says why the disagreement is acceptable.
```

## 7. Migration Plan

### Phase A: Hybrid Report Only

Goal: prove Hybrid Ranking without changing UI or production ranking.

Actions:

- Add a read-only Hybrid Ranking report generator.
- Output `HYBRID_RANKING_REPORT.md`.
- Show Legacy Rank, Scenario Rank, Hybrid Rank, Hybrid Score, and downgrade reasons.
- Compare top portfolio differences across at least 5 additional matches.
- Do not change `strategy_score(...)`.
- Do not change `strategy_comparison(...)` production order.
- Do not change UI.

Exit criteria:

- Hybrid Rank explains current Legacy/Scenario disagreement better than either alone.
- No obvious Hybrid top pick violates hard guardrails.
- Hybrid results remain stable across multiple match types.

Risk: LOW.

### Phase B: Visible Hybrid Shadow

Goal: expose Hybrid Rank while Legacy remains operationally available.

Actions:

- UI displays Legacy Rank / Scenario Rank / Hybrid Rank.
- Add `Hybrid Score` only in detail view or advanced section.
- Keep production recommendation unchanged at first.
- Highlight when Hybrid Rank 1 differs from Legacy Rank 1.
- Keep Legacy rollback switch available.

Exit criteria:

- Users can understand why Hybrid Rank differs.
- Hybrid top picks pass post-match and manual review.
- No increase in decision confusion.

Risk: MEDIUM.

### Phase C: Hybrid Rank Main Sorting

Goal: make Hybrid Rank the default Portfolio Ranking order.

Actions:

- Portfolio Ranking table sorts by Hybrid Score.
- Legacy Rank becomes a reference column.
- Scenario Rank remains visible as a scenario-quality signal.
- Default recommendation eligibility uses Hybrid guardrails.
- Legacy Ranking remains available through a fallback flag.

Exit criteria:

- Hybrid Rank has passed enough post-match validation.
- Guardrails are implemented and tested.
- Fallback path has been verified.

Risk: HIGH.

## 8. Safety Rollback

Hybrid Ranking must have a one-step fallback to Legacy sorting.

Recommended runtime flag:

```text
RANKING_MODE = legacy | hybrid_shadow | hybrid_primary
```

Behavior:

| Mode | Sorting | Recommendation authority | UI |
| --- | --- | --- | --- |
| legacy | Legacy Score | Legacy | Current production behavior |
| hybrid_shadow | Legacy Score | Legacy | Shows Hybrid Rank as observation |
| hybrid_primary | Hybrid Score | Hybrid with guardrails | Legacy Rank shown as reference |

Rollback rule:

```text
If Hybrid sorting produces an obviously contradictory top portfolio, switch RANKING_MODE back to legacy without deleting Hybrid metadata or reports.
```

Rollback should not require deleting files or rewriting history.

## 9. Affected Functions

| Function | Phase A | Phase B | Phase C | Risk |
| --- | --- | --- | --- | --- |
| `strategy_score(...)` | No change | No change | Possible component refactor only if needed | HIGH |
| `strategy_comparison(...)` | No production sort change | Attach/display Hybrid metadata only | Main sorting changes to Hybrid Score | HIGH |
| `portfolio_ranking_rows(...)` | No change | Add Hybrid Rank fields if needed | Use Hybrid order and fields | MEDIUM |
| `render_portfolio_ranking(...)` | No change | Show Hybrid columns/warnings | Make Hybrid the primary table order | MEDIUM |

Recommended implementation principle:

```text
Do not rewrite `strategy_score(...)` first.
Add Hybrid scoring as an independent helper after existing strategy evaluation, then migrate sorting only after validation.
```

Candidate helper:

```text
attach_hybrid_ranking_metadata(strategies, scenario_context, audit_context)
```

This helper should:

- preserve existing strategy objects and Legacy fields,
- compute `strategy["hybrid"]`,
- assign `hybrid_rank`,
- return the original order in Phase A/B,
- return Hybrid order only in Phase C.

## 10. Proposed `strategy["hybrid"]` Metadata

```python
strategy["hybrid"] = {
    "enabled": True,
    "mode": "hybrid_shadow",
    "legacy_rank": 1,
    "legacy_score": 91.2,
    "scenario_rank": 4,
    "scenario_score": 72.5,
    "hybrid_rank": 2,
    "hybrid_score": 84.6,
    "shadow_verdict": "Watch",
    "scenario_consistency_score": 82,
    "tail_exposure": 0.18,
    "pure_tempo_penalty": 0,
    "main_scenario_coverage": 0.78,
    "secondary_insurance_coverage": 0.35,
    "max_loss": 1500,
    "guardrail_status": "eligible",
    "guardrail_flags": [],
    "hybrid_rank_reason": "Strong value and adequate scenario coverage with controlled tail exposure."
}
```

## 11. Implementation Risk Level

Overall implementation risk: HIGH.

Reason:

- Changing the main Portfolio Ranking sort directly affects user decisions.
- Existing production logic was built around Legacy score order.
- UI currently assumes Legacy score is the primary ranking basis.
- Recommendation eligibility must not silently change without clear guardrails.

Recommended risk path:

- Phase A risk: LOW.
- Phase B risk: MEDIUM.
- Phase C risk: HIGH.

## 12. Recommended Next Step

Start with Phase A only:

```text
Build a read-only Hybrid Ranking report generator.
```

Do not modify UI or production sorting until Hybrid report results have been reviewed against recent post-match validation data.
