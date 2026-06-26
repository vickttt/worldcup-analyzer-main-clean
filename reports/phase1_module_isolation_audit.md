# Phase 1 Module Isolation Audit

This audit reviews `modules/odds/core.py` and `modules/strategy/core.py` after Phase 1 extraction. It is report-only; no implementation changes are made here.

## modules/odds/core.py

- Dependency list:
  - Standard library: `re`
  - Internal modules:
    - `modules.portfolio_engine.normalize_handicap_line`
    - `modules.portfolio_engine.settle_asian_handicap`
    - `modules.user_odds.build_market_candidates`
    - `modules.user_odds.candidate_with_actual`
- Hidden global state usage:
  - No direct `st.session_state`.
  - No direct Streamlit import.
  - No module-level mutable runtime state.
- Implicit coupling:
  - Depends on dict-shaped market candidate objects produced by `modules.user_odds`.
  - Depends on portfolio-engine handicap settlement semantics.
  - `modules.user_odds` imports `modules.team_resolver`, which can require runtime dependencies such as `requests`.
- Cross-module calls:
  - Odds -> Strategy: No.
  - Strategy -> Odds: No.
- Coupling risk: Medium.
- Explanation:
  - The odds module is independent of UI and strategy, but still relies on portfolio helper behavior for Asian handicap settlement and line normalization.
  - It also pulls in `modules.user_odds`, which brings in broader data/team resolution dependencies.
- Mitigation suggestion, not implemented:
  - Later move pure line parsing/settlement helpers into a small neutral market math module, or expose a narrow adapter from `modules.portfolio_engine`.
  - Keep `modules.user_odds` dependency under review before odds package becomes a pure market-processing layer.

## modules/strategy/core.py

- Dependency list:
  - No external imports.
  - No internal module imports.
- Hidden global state usage:
  - No direct `st.session_state`.
  - No direct Streamlit import.
  - No file system access.
  - No module-level mutable runtime state.
- Implicit coupling:
  - Depends on existing strategy dictionaries and keys:
    - `shadow.shadow_verdict`
    - `hybrid_v2.sleeve_status`
    - `max_loss`
    - `score`
    - `consistency_score`
    - `rank1_eligibility`
    - `risk_gate`
    - `correct_score_exposure`
  - Uses the same implicit data contracts that existed when these functions lived in `app.py`.
- Cross-module calls:
  - Strategy -> Odds: No.
  - Odds -> Strategy: No.
- Coupling risk: Low to Medium.
- Explanation:
  - The module is code-isolated and deterministic for a given input dict.
  - Risk remains from implicit dict contracts rather than imports or runtime state.
- Mitigation suggestion, not implemented:
  - Introduce typed data contracts or fixture examples before moving deeper strategy/ranking logic.
  - Add golden-output tests for `match_betting_score`, `recommended_stake_mvp`, and `strategy_score`.

## Coupling Control Result

- Odds module depends on strategy: No.
- Strategy module depends on odds: No.
- Odds module depends on UI layer: No direct dependency.
- Strategy module depends on UI layer: No.
- Circular imports introduced by Phase 1: None detected by static import inspection.

## Readiness Decision

- READY FOR PORTFOLIO EXTRACTION: NO.
  - Reason: `modules/odds/core.py` still relies on `modules.portfolio_engine`, and `app.py` still contains substantial ranking/allocation logic. Portfolio extraction should wait for a narrow test harness around protected ranking functions.
- READY FOR BACKTEST MODULE SPLIT: NO.
  - Reason: Post-match settlement and audit logic still share implicit snapshot and strategy structures in `app.py`. Backtest split should wait until portfolio contracts are stabilized.
