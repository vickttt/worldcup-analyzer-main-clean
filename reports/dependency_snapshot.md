# Dependency Snapshot

This is a lightweight static import snapshot. It is intended for module planning only and does not imply any code move.

## high-level import relationships

### app.py

`app.py` imports:

- `modules.betting_opinion`
- `modules.decision_engine`
- `modules.game_behavior_engine`
- `modules.market_utils`
- `modules.match_parser`
- `modules.mock_data`
- `modules.odds_client`
- `modules.perf_logger`
- `modules.polymarket_client`
- `modules.portfolio_engine`
- `modules.pregame_content`
- `modules.probability_model`
- `modules.rating_model`
- `modules.report_generator`
- `modules.result_distribution`
- `modules.schedule_client`
- `modules.score_model`
- `modules.shadow_metadata`
- `modules.team_profile_client`
- `modules.the_odds_client`
- `modules.user_odds`
- `modules.value_model`
- `modules.weather_client`
- `modules.worldcup_db`

### modules

- `modules.odds.core` -> `modules.portfolio_engine`, `modules.user_odds`
- `modules.strategy.core` -> no local module imports
- `modules.betting_opinion` -> `modules.market_utils`, `modules.pregame_content`
- `modules.decision_engine` -> `modules.market_utils`, `modules.pregame_content`, `modules.user_odds`
- `modules.market_utils` -> `modules.pregame_content`
- `modules.match_parser` -> `modules.team_resolver`
- `modules.odds_client` -> `modules.cache_config`, `modules.team_resolver`
- `modules.polymarket_client` -> `modules.cache_config`, `modules.team_resolver`
- `modules.report_generator` -> `modules.market_utils`, `modules.pregame_content`
- `modules.result_distribution` -> `modules.game_behavior_engine`, `modules.pregame_content`
- `modules.team_profile_client` -> `modules.cache_config`, `modules.odds_client`, `modules.pregame_content`
- `modules.team_resolver` -> `modules.cache_config`
- `modules.the_odds_client` -> `modules.cache_config`, `modules.team_resolver`
- `modules.user_odds` -> `modules.market_utils`, `modules.portfolio_engine`, `modules.pregame_content`, `modules.team_resolver`
- `modules.worldcup_db` -> `modules.schedule_client`

### scripts

- Data scripts import `modules.match_parser`, `modules.odds_client`, `modules.schedule_client`, `modules.team_resolver`, `modules.the_odds_client`, `modules.user_odds`, `modules.weather_client`, and `modules.worldcup_db`.
- Backtest and validation scripts import `modules.portfolio_engine`, `modules.result_distribution`, `modules.shadow_metadata`, and settlement helpers from validation scripts.
- Report validation imports `modules.betting_opinion`, `modules.market_utils`, `modules.report_generator`, `modules.value_model`, and `modules.worldcup_db`.

## circular dependency warnings

- No direct circular imports were detected among current `modules/*.py` files by static import inspection.
- A later move must still check runtime import behavior because Streamlit cache decorators and script-level imports can create hidden ordering assumptions.
- After Phase 1 extraction, `modules.odds.core` imports `modules.user_odds`, which imports `modules.team_resolver` and therefore requires the normal runtime dependency set.

## heavy coupling modules

- `app.py`
  - Remains the primary runtime entry point.
  - Imports nearly every domain module.
  - Combines UI, routing, data assembly, portfolio presentation, and post-match display.
- `modules.odds.core.py`
  - New extracted odds boundary.
  - Contains moved odds formatting, actual odds completeness, handicap/total parsing, and outcome helpers.
- `modules.strategy.core.py`
  - New extracted strategy boundary.
  - Contains moved confidence text, match betting score, recommended stake, path consistency, score, and rank key helpers.
- `modules.portfolio_engine.py`
  - 1605 lines.
  - Core Portfolio Ranking / allocation logic.
  - Must not be edited during structural mapping.
- `modules.decision_engine.py`
  - 1060 lines.
  - Strategy/decision interpretation layer.
- `modules.user_odds.py`
  - 990 lines.
  - Odds parsing plus dependency on portfolio helpers.
- `modules.odds_client.py`
  - 975 lines.
  - API-Football client, cache behavior, and Streamlit cache decorators.
- `modules.report_generator.py`
  - 811 lines.
  - Report formatting and export behavior.
- `modules.schedule_client.py`
  - 695 lines.
  - Schedule data access and Streamlit cache decorators.

## Streamlit coupling notes

The following non-UI modules import Streamlit directly today:

- `modules.odds_client.py`
- `modules.polymarket_client.py`
- `modules.schedule_client.py`
- `modules.team_profile_client.py`
- `modules.team_resolver.py`
- `modules.the_odds_client.py`
- `modules.weather_client.py`

These imports are mostly cache-related. Later modularization should separate data client logic from UI/cache adapters.

## recommended extraction order

1. Keep `portfolio_engine.py` stable and wrap it last.
2. Create adapter modules around odds/data clients before moving implementation.
3. Extract UI sections from `app.py` into `modules/ui/` only after reports confirm no behavior change.
4. Move backtest scripts after the production runtime path is stable.
