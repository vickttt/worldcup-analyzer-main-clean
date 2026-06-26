# app.py Coupling Hotspots

This report marks coupling risk only. No refactor was performed.

## Tightly Coupled Logic Blocks

- `render_analysis_page` lines 6838-7010
  - Mixes data loading, fixture refresh, model assembly, market rendering, snapshot handling, and tab orchestration.
  - Future target: orchestration wrapper plus `modules/ui/analysis_page.py`.
- Portfolio ranking cluster lines 2873-3823 and 4694-5508
  - Strategy construction, Portfolio Score, eligibility, ranking rows, UI detail expanders, Hybrid v0.2 metadata, and decision cards are colocated.
  - Future target: split strategy/portfolio computation from UI rows.
- Actual odds and manual portfolio cluster lines 3826-4691
  - UI input, cache files, parsing, market matching, and candidate resolution are colocated.
  - Future target: odds parser/service plus UI adapter.
- Post-match cluster lines 2296-2870 and 6227-6337
  - Settlement, audit, persistence, and Streamlit display share data structures.
  - Future target: backtest/audit service plus UI renderer.
- Schedule portal cluster lines 6388-6835
  - Schedule data, navigation state, search, cards, standings, and tournament stats are mixed.
  - Future target: schedule data facade plus UI components.

## Mixed Responsibilities

- `app.py` owns runtime entry, page routing, UI components, cache paths, snapshot persistence, and several domain calculations.
- Data clients import Streamlit cache decorators, so pure data access and UI/runtime cache behavior are coupled outside `app.py` too.
- Portfolio and strategy logic appear both in `modules.portfolio_engine` and in `app.py` helper functions.

## Repeated Or Overlapping Computations

- Score/path helpers exist in multiple forms: `path_analysis_rows`, `path_analysis_rows_old`, score probability helpers, and result distribution functions.
- Portfolio display/ranking helpers repeat naming, role, and duplicate-key normalization logic.
- Odds completeness and actual-vs-market comparison are computed in several UI-facing helpers.
- Snapshot path and history slug helpers are local to `app.py` but also overlap with report/backtest scripts.

## Global State Usage

- `MODEL_VERSION_TRACKING` is global metadata used by snapshot/report paths.
- `config` is loaded globally at runtime and used for Streamlit page setup.
- `st.session_state` is read and written in route control, forms, fixture selection, odds input, and page transitions.
- Path globals are imported or derived repeatedly through `Path(__file__)`, history helpers, and data directories.

## Hidden Coupling Warnings

- Dict contracts are implicit for fixtures, market candidates, strategy items, snapshots, and portfolio rows.
- UI row functions assume Chinese display labels and specific key names from upstream domain objects.
- Ranking-sensitive functions in `app.py` must remain protected until explicit extraction tests exist.
- Streamlit rerun behavior means extraction can alter control flow even if calculations are unchanged.
