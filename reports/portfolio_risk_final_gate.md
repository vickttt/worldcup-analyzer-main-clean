# Portfolio Risk Final Gate

This report classifies whether portfolio logic is safe to extract after the shadow assertion gate.

## Dependency Classification

- strategy scoring dependency: BLOCKED
  - reason: portfolio ranking still depends on `strategy_score`, `rank_key_with_eligibility`, and score fields produced across app/strategy context.
- odds formatting/value dependency: MEDIUM RISK
  - reason: portfolio display, settlement, and candidate fields use odds display/value fields; formatting itself is not the main blocker, but odds-derived values affect stake and explanation fields.
- app.py UI state dependency: BLOCKED
  - reason: portfolio orchestration still sits near Streamlit rendering and session-state-controlled match/portfolio input paths.
- implicit global dependency: BLOCKED
  - reason: history paths, selected fixture context, and module-level helpers are still shared by snapshot, UI, and post-match flows.
- runtime shadow import: SAFE
  - reason: shadow module is not currently imported by runtime code.

## Final Classification

BLOCKED (must fix before extraction)

## Required Before Extraction

- Add a recomputation-based golden assertion runner that can run without Streamlit UI state.
- Add post-match/backtest settlement golden checks.
- Make portfolio input/output schemas explicit before moving functions.
- Keep `modules/portfolio/shadow.py` unimported by runtime until the above checks pass.