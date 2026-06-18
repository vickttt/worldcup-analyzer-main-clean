# Changelog

## 2026-06-19

- Added `scripts/refresh_today_odds.py` to refresh and verify today's odds cache.
- Refreshed The Odds API Match Winner and Over/Under cache for today's matches.
- Expanded team aliases for Bosnia-Herzegovina, Australia, Scotland, and Morocco.
- Confirmed API-Football live refresh is blocked by account suspension, not by local matching logic.
- Split permanent history snapshots into pre-match `*_pre.json` and post-match `*_post.json`.
- Added automatic post-match snapshot saving after strategy settlement.
- Added project rule that API refreshes should be run through terminal scripts and then cached.
- Added Prediction Audit to connect pre-match recommendations with post-match outcomes.
- Added Recommendation Audit rows for strategy-level hit/miss and failure reasons.
- Added Portfolio Style classification: Aggressive, Balanced, Conservative.
- Added Style Performance Database under `data/history/style_performance.json`.
- Added model version tracking to new pre-match and post-match snapshots.
- Moved post-match style decision structure into pre-match Core Decision: strategy ranking, asset role allocation, settlement preview, risk paths, and top outcome preview.
- Simplified finished-match page to focus on Post Match Analysis and strategy settlement only.
- Upgraded Betting Asset Role Framework from single-role labels to multi-role weighted asset roles.
- Asset allocation and post-match role contribution now split stake and profit across multiple roles.
- Fixed stale match status refresh so ended matches can route into Post Match Analysis.
- Replaced HTML-based profit visualization with native Streamlit charts to prevent raw code display.
- Added Betting Asset Role Framework as the strategy core.
- Added role labels for Return, Insurance, Directional, Tempo, and Tail assets.
- Added role-driven optimizer adjustment and post-match asset role contribution analysis.
- Added `GPT_CONTEXT.md` as the current project state file.
- Added `scripts/update_gpt_context.py` to refresh GPT context after major changes.
- Historical notes should be kept here instead of expanding `GPT_CONTEXT.md`.
