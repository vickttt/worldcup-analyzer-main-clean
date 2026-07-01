# Validation Update Summary

Date: 2026-06-21

## Scope

- Updated post-match result snapshots for ended matches with existing pre-match snapshots.
- Ran `python3 scripts/generate_post_match_validation_report.py`.
- Regenerated `POST_MATCH_VALIDATION_REPORT.md`.
- Did not modify recommendation logic, ranking logic, Scenario Engine, Shadow Metadata, UI, or score functions.

## New Post-Match Files

- `data/history/2026_06_18_Canada_Qatar_post.json`
- `data/history/2026_06_19_Brazil_Haiti_post.json`
- `data/history/2026_06_19_Scotland_Morocco_post.json`
- `data/history/2026_06_19_Turkey_Paraguay_post.json`
- `data/history/2026_06_20_Brazil_Haiti_post.json`
- `data/history/2026_06_20_Ecuador_Cura_ao_post.json`
- `data/history/2026_06_20_Germany_Ivory_Coast_post.json`
- `data/history/2026_06_20_Netherlands_Sweden_post.json`
- `data/history/2026_06_20_Scotland_Morocco_post.json`
- `data/history/2026_06_20_T_rkiye_Paraguay_post.json`
- `data/history/2026_06_20_Tunisia_Japan_post.json`
- `data/history/2026_06_20_United_States_Australia_post.json`

## Result Source Notes

- Canada vs Qatar: Canada 6-0 Qatar.
- Brazil vs Haiti: Brazil 3-0 Haiti.
- Scotland vs Morocco: Scotland 0-1 Morocco.
- Turkey / Türkiye vs Paraguay: Turkey / Türkiye 0-1 Paraguay.
- Ecuador vs Curaçao: Ecuador 0-0 Curaçao.
- Germany vs Ivory Coast: Germany 2-1 Ivory Coast.
- Netherlands vs Sweden: Netherlands 5-1 Sweden.
- Tunisia vs Japan: Tunisia 0-4 Japan.
- United States vs Australia: United States 2-0 Australia, matching the existing canonical post-match validation.

## Validation Metrics

- Current valid validations: 12.
- Legacy Wins: 3.
- Scenario Wins: 3.
- Draws: 6.
- Legacy ROI: -40.8%.
- Scenario ROI: -2.1%.
- Promotion Status: `Enter Scenario Guardrails Phase`.
- 5-Match Promotion Rule reached: Yes.

## Important Interpretation

- The validation count is snapshot-based, not strictly unique-match based. Some fixtures have multiple pre-match snapshots and therefore multiple validation rows.
- Scenario ROI is still negative overall, but materially better than Legacy ROI in this validation run.
- The correct next step is Guardrails, not full replacement of Legacy Ranking.

## Safety Check

- `strategy_score(...)` changed: No.
- `evaluate_allocation(...)` changed: No.
- `strategy_comparison(...)` changed: No.
- Sorting logic changed: No.
- Recommendation logic changed: No.
- UI changed: No.
