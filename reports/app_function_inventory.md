# app.py Function Inventory

This inventory was generated from the top-level AST of `app.py`. It lists all top-level functions/classes and suggested future targets. No code was changed.

| Lines | Name | Type | Responsibility | Dependencies / globals | Suggested target |
|---:|---|---|---|---|---|
| 107-108 | `percent` | function | Formatting, parsing, flags, and small display utilities. | internal helpers / local values | `ui` |
| 111-116 | `fmt` | function | Formatting, parsing, flags, and small display utilities. | internal helpers / local values | `ui` |
| 119-125 | `fmt_odds` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `ui` |
| 128-129 | `clamp` | function | Formatting, parsing, flags, and small display utilities. | internal helpers / local values | `ui` |
| 132-143 | `money` | function | Formatting, parsing, flags, and small display utilities. | internal helpers / local values | `ui` |
| 146-154 | `parse_kickoff` | function | Formatting, parsing, flags, and small display utilities. | datetime, zoneinfo | `ui` |
| 157-162 | `flag_for_team` | function | Fixture, schedule, team, or match metadata support. | internal helpers / local values | `ui` |
| 165-170 | `risk_color` | function | Formatting, parsing, flags, and small display utilities. | internal helpers / local values | `ui` |
| 173-613 | `card_css` | function | CSS, card display, market consensus, team display helpers. | modules.pregame_content, st, streamlit | `ui` |
| 616-625 | `consensus_market` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `ui` |
| 628-632 | `format_team_line` | function | Fixture, schedule, team, or match metadata support. | modules.pregame_content | `ui` |
| 635-645 | `soft_card` | function | CSS, card display, market consensus, team display helpers. | st, streamlit | `ui` |
| 648-652 | `probability_bar` | function | Score/probability distribution or outcome-path support. | st, streamlit | `ui` |
| 655-659 | `comparison_bar` | function | CSS, card display, market consensus, team display helpers. | st, streamlit | `ui` |
| 662-663 | `official_name` | function | CSS, card display, market consensus, team display helpers. | modules.pregame_content | `ui` |
| 689-690 | `team_flag` | function | Fixture, schedule, team, or match metadata support. | internal helpers / local values | `ui` |
| 693-699 | `team_badge_html` | function | Fixture, schedule, team, or match metadata support. | html, modules.pregame_content | `unknown` |
| 702-721 | `selected_fixture_as_api_fixture` | function | Fixture, schedule, team, or match metadata support. | internal helpers / local values | `data/ui` |
| 724-739 | `same_fixture` | function | Fixture, schedule, team, or match metadata support. | modules.pregame_content, modules.schedule_client | `data/ui` |
| 742-750 | `fixture_needs_status_refresh` | function | Fixture, schedule, team, or match metadata support. | datetime, modules.schedule_client, zoneinfo | `data/ui` |
| 753-761 | `refresh_selected_fixture_if_needed` | function | Fixture, schedule, team, or match metadata support. | modules.schedule_client, st, streamlit | `data/ui` |
| 764-785 | `odds_date_key_from_fixture` | function | Odds, market, line, or candidate processing support. | datetime, zoneinfo | `data/ui` |
| 788-840 | `render_debug_panel` | function | Render Streamlit/UI section or display rows. | pandas, pd, st, streamlit | `ui/strategy` |
| 843-850 | `safe_render_market_section` | function | Odds, market, line, or candidate processing support. | st, streamlit | `ui/strategy` |
| 853-893 | `render_market_debug_summary` | function | Render Streamlit/UI section or display rows. | pandas, pd, st, streamlit | `ui/strategy` |
| 896-965 | `render_match_overview` | function | Render Streamlit/UI section or display rows. | html, modules.pregame_content, modules.weather_client, st, streamlit | `ui/strategy` |
| 968-998 | `render_betting_opinion` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `ui/strategy` |
| 1001-1005 | `render_score_card` | function | Render Streamlit/UI section or display rows. | st, streamlit | `ui/analysis/strategy` |
| 1008-1067 | `render_decision_engine` | function | Render Streamlit/UI section or display rows. | modules.decision_engine, modules.pregame_content, st, streamlit | `ui/analysis/strategy` |
| 1070-1093 | `render_result_distribution` | function | Render Streamlit/UI section or display rows. | st, streamlit | `ui/analysis/strategy` |
| 1096-1107 | `render_extreme_scenarios` | function | Render Streamlit/UI section or display rows. | modules.result_distribution, st, streamlit | `ui/analysis/strategy` |
| 1110-1119 | `render_betting_structure` | function | Render Streamlit/UI section or display rows. | modules.result_distribution, st, streamlit | `ui/analysis/strategy` |
| 1122-1123 | `recommendation_combo` | function | Decision engine rendering, result distribution, extreme scenarios, staking display. | modules.user_odds | `ui/analysis/strategy` |
| 1126-1127 | `round_to_hundred` | function | Decision engine rendering, result distribution, extreme scenarios, staking display. | internal helpers / local values | `ui/analysis/strategy` |
| 1130-1132 | `recommended_total_stake` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `ui/analysis/strategy` |
| 1135-1155 | `stake_amounts` | function | Decision engine rendering, result distribution, extreme scenarios, staking display. | internal helpers / local values | `ui/analysis/strategy` |
| 1158-1165 | `rating_class` | function | Decision engine rendering, result distribution, extreme scenarios, staking display. | internal helpers / local values | `ui/analysis/strategy` |
| 1168-1174 | `rating_badge` | function | Decision engine rendering, result distribution, extreme scenarios, staking display. | internal helpers / local values | `ui/analysis/strategy` |
| 1177-1188 | `combo_role` | function | Decision engine rendering, result distribution, extreme scenarios, staking display. | internal helpers / local values | `ui/analysis/strategy` |
| 1191-1193 | `score_stars` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `ui/analysis/strategy` |
| 1196-1205 | `render_recommended_combo` | function | Render Streamlit/UI section or display rows. | st, streamlit | `ui/analysis/strategy` |
| 1208-1213 | `confidence_reason` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1216-1221 | `market_disagreement_reason` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `portfolio/ui` |
| 1224-1229 | `profit_text` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1232-1239 | `profit_value` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1242-1243 | `combo_item` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1246-1247 | `combo_items` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1250-1262 | `total_known_profit` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `portfolio/ui` |
| 1265-1290 | `portfolio_metrics` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/ui` |
| 1293-1313 | `bet_correlation` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1316-1326 | `weighted_combo_correlation` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1329-1337 | `correlation_matrix_rows` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1340-1364 | `market_odds_overview_rows` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `portfolio/ui` |
| 1367-1378 | `actual_odds_completeness` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `portfolio/ui` |
| 1381-1415 | `actual_odds_completeness_for_match` | function | Odds, market, line, or candidate processing support. | modules.user_odds | `portfolio/ui` |
| 1418-1434 | `optimized_strategy_reason_rows` | function | Strategy construction, comparison, scoring, or explanation support. | modules.user_odds | `portfolio/ui` |
| 1437-1450 | `kelly_fraction` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1453-1470 | `kelly_reference_rows` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1473-1490 | `strategy_holdings_rows` | function | Strategy construction, comparison, scoring, or explanation support. | modules.user_odds | `portfolio/ui` |
| 1511-1517 | `role_entry` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1520-1528 | `normalize_role_weights` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1531-1586 | `betting_asset_roles` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | modules.pregame_content, modules.user_odds | `portfolio/ui` |
| 1589-1597 | `betting_asset_role` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1600-1602 | `insurance_asset_role` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1605-1606 | `asset_role_key` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1609-1632 | `role_allocation_rows` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1635-1645 | `role_exposure` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1648-1661 | `role_balance_adjustment` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1664-1674 | `role_constraint_adjustment` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1677-1694 | `role_constraint_rows` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1697-1732 | `portfolio_style` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/ui` |
| 1735-1745 | `strategy_path_rows` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `portfolio/ui` |
| 1748-1777 | `marginal_contribution_rows` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1780-1815 | `correct_score_marginal_ev_rows` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `portfolio/ui` |
| 1818-1825 | `numeric_text` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | internal helpers / local values | `portfolio/ui` |
| 1828-1833 | `chart_health_check` | function | Portfolio metrics, roles, Kelly references, charts, strategy detail display. | pandas, pd | `portfolio/ui` |
| 1836-1865 | `render_probability_profit_charts` | function | Render Streamlit/UI section or display rows. | pandas, pd, st, streamlit | `portfolio/ui` |
| 1868-1913 | `render_strategy_detail` | function | Render Streamlit/UI section or display rows. | pandas, pd, st, streamlit | `portfolio/ui` |
| 1916-1920 | `bet_identity` | function | Bet identity, score probability, return matrix, allocation optimization. | internal helpers / local values | `portfolio/strategy/analysis` |
| 1923-1936 | `discard_reason` | function | Bet identity, score probability, return matrix, allocation optimization. | internal helpers / local values | `portfolio/strategy/analysis` |
| 1939-1953 | `discarded_bet_rows` | function | Bet identity, score probability, return matrix, allocation optimization. | internal helpers / local values | `portfolio/strategy/analysis` |
| 1956-1971 | `score_path_label` | function | Score/probability distribution or outcome-path support. | modules.pregame_content | `portfolio/strategy/analysis` |
| 1974-1982 | `exact_score_probability` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `portfolio/strategy/analysis` |
| 1985-1991 | `reasonable_score_space` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `portfolio/strategy/analysis` |
| 1994-2011 | `score_probability_sort_key` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2014-2029 | `score_category` | function | Score/probability distribution or outcome-path support. | modules.pregame_content | `portfolio/strategy/analysis` |
| 2032-2044 | `distribution_category_probability` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2047-2057 | `scenario_probability` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2060-2068 | `scenario_probability_map` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2071-2093 | `asset_profit_per_unit` | function | Bet identity, score probability, return matrix, allocation optimization. | modules.portfolio_engine | `portfolio/strategy/analysis` |
| 2096-2099 | `build_score_distribution` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2102-2109 | `build_return_matrix` | function | Bet identity, score probability, return matrix, allocation optimization. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2112-2145 | `auto_correct_score_pool` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2148-2171 | `optimizer_asset_pool` | function | Bet identity, score probability, return matrix, allocation optimization. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2174-2191 | `allocation_vectors` | function | Bet identity, score probability, return matrix, allocation optimization. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2194-2207 | `portfolio_stability_score` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2210-2268 | `evaluate_allocation` | function | Bet identity, score probability, return matrix, allocation optimization. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2271-2293 | `optimize_betting_portfolio` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/analysis` |
| 2296-2302 | `parse_handicap_selection` | function | Odds, market, line, or candidate processing support. | modules.portfolio_engine, re | `backtest/portfolio/strategy` |
| 2305-2311 | `parse_total_selection` | function | Odds, market, line, or candidate processing support. | re | `backtest/portfolio/strategy` |
| 2314-2322 | `winner_outcome` | function | Outcome settlement, prediction audit, performance persistence, model error summaries. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2325-2333 | `handicap_outcome` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2336-2344 | `handicap_profit_value` | function | Odds, market, line, or candidate processing support. | modules.portfolio_engine | `backtest/portfolio/strategy` |
| 2347-2354 | `total_outcome` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2357-2358 | `correct_score_outcome` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2361-2391 | `score_profit_row` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2394-2404 | `score_candidates` | function | Score/probability distribution or outcome-path support. | re | `backtest/portfolio/strategy` |
| 2407-2427 | `path_analysis_rows` | function | Data path, cache, snapshot, load/save, or persistence support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2430-2435 | `worst_score_path` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2438-2443 | `best_score_path` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2446-2455 | `final_score_from_fixture` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2458-2506 | `settle_items` | function | Post-match settlement, audit, or validation support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2509-2533 | `settle_strategies` | function | Post-match settlement, audit, or validation support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2536-2548 | `audit_failure_reason` | function | Post-match settlement, audit, or validation support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2551-2588 | `prediction_audit` | function | Post-match settlement, audit, or validation support. | modules.user_odds | `backtest/portfolio/strategy` |
| 2591-2604 | `role_performance_summary` | function | Outcome settlement, prediction audit, performance persistence, model error summaries. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2607-2616 | `portfolio_items_summary` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2619-2640 | `portfolio_audit_detail_rows` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2643-2649 | `result_hit_summary` | function | Post-match settlement, audit, or validation support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2652-2668 | `result_failure_summary` | function | Post-match settlement, audit, or validation support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2671-2724 | `recommendation_audit` | function | Post-match settlement, audit, or validation support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2727-2728 | `style_performance_path` | function | Data path, cache, snapshot, load/save, or persistence support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2731-2732 | `portfolio_performance_path` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2735-2772 | `update_style_performance_database` | function | Outcome settlement, prediction audit, performance persistence, model error summaries. | datetime, json | `backtest/portfolio/strategy` |
| 2775-2805 | `update_portfolio_performance_database` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | datetime, json | `backtest/portfolio/strategy` |
| 2808-2837 | `role_contribution_rows` | function | Outcome settlement, prediction audit, performance persistence, model error summaries. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2840-2851 | `role_contribution_explanation` | function | Outcome settlement, prediction audit, performance persistence, model error summaries. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2854-2870 | `model_error_summary` | function | Outcome settlement, prediction audit, performance persistence, model error summaries. | internal helpers / local values | `backtest/portfolio/strategy` |
| 2873-2893 | `strategy_item_groups` | function | Strategy construction, comparison, scoring, or explanation support. | modules.portfolio_engine | `strategy/portfolio` |
| 2896-2902 | `correct_score_path_probability` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `strategy/portfolio` |
| 2905-2923 | `main_path_correct_scores` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `strategy/portfolio` |
| 2926-2955 | `build_strategy_library` | function | Strategy construction, comparison, scoring, or explanation support. | modules.portfolio_engine | `strategy/portfolio` |
| 2958-2975 | `build_auto_optimized_strategy` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 2978-2989 | `strategy_weight` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 2992-3000 | `correlation_adjusted_weight` | function | Strategy construction, scoring, comparison, frontier, conclusion helpers. | internal helpers / local values | `strategy/portfolio` |
| 3003-3027 | `correlation_penalty_rows` | function | Strategy construction, scoring, comparison, frontier, conclusion helpers. | internal helpers / local values | `strategy/portfolio` |
| 3030-3045 | `allocate_strategy_items` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 3048-3085 | `enforce_correct_score_floor` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `strategy/portfolio` |
| 3088-3112 | `item_direction_alignment` | function | Strategy construction, scoring, comparison, frontier, conclusion helpers. | modules.pregame_content, modules.user_odds | `strategy/portfolio` |
| 3115-3130 | `strategy_direction_alignment` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 3133-3147 | `item_strategic_value` | function | Strategy construction, scoring, comparison, frontier, conclusion helpers. | internal helpers / local values | `strategy/portfolio` |
| 3150-3158 | `strategy_strategic_value` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 3161-3169 | `item_path_consistency` | function | Data path, cache, snapshot, load/save, or persistence support. | internal helpers / local values | `strategy/portfolio` |
| 3172-3184 | `strategy_path_consistency` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 3187-3261 | `strategy_score` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 3264-3295 | `portfolio_constraint_variants` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | modules.portfolio_engine, modules.user_odds, re | `strategy/portfolio` |
| 3298-3417 | `evaluate_strategy` | function | Strategy construction, comparison, scoring, or explanation support. | modules.portfolio_engine | `strategy/portfolio` |
| 3420-3432 | `rank_key_with_eligibility` | function | Strategy construction, scoring, comparison, frontier, conclusion helpers. | internal helpers / local values | `strategy/portfolio` |
| 3435-3448 | `strategy_comparison` | function | Strategy construction, comparison, scoring, or explanation support. | modules.portfolio_engine | `strategy/portfolio` |
| 3451-3472 | `efficient_frontier_rows` | function | Strategy construction, scoring, comparison, frontier, conclusion helpers. | internal helpers / local values | `strategy/portfolio` |
| 3475-3502 | `strategy_table_rows` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 3505-3521 | `prematch_strategy_ranking_rows` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 3524-3535 | `insurance_cost_summary` | function | Strategy construction, scoring, comparison, frontier, conclusion helpers. | internal helpers / local values | `strategy/portfolio` |
| 3538-3558 | `settlement_preview_rows` | function | Post-match settlement, audit, or validation support. | modules.portfolio_engine, modules.user_odds | `strategy/portfolio` |
| 3561-3571 | `why_portfolio_rows` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | modules.user_odds | `strategy/portfolio` |
| 3574-3584 | `top_outcome_preview_rows` | function | Strategy construction, scoring, comparison, frontier, conclusion helpers. | internal helpers / local values | `strategy/portfolio` |
| 3587-3602 | `risk_path_rows` | function | Data path, cache, snapshot, load/save, or persistence support. | internal helpers / local values | `strategy/portfolio` |
| 3605-3612 | `strategy_component_rows` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 3615-3649 | `strategy_direct_comparison_rows` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 3652-3727 | `insurance_cost_rows` | function | Strategy construction, scoring, comparison, frontier, conclusion helpers. | internal helpers / local values | `strategy/portfolio` |
| 3730-3749 | `participation_with_portfolio` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `strategy/portfolio` |
| 3752-3770 | `strategy_conclusion` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 3773-3790 | `strategy_j_comparison` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `strategy/portfolio` |
| 3793-3823 | `path_analysis_rows_old` | function | Data path, cache, snapshot, load/save, or persistence support. | internal helpers / local values | `strategy/portfolio` |
| 3826-3848 | `render_rating_breakdown` | function | Render Streamlit/UI section or display rows. | st, streamlit | `odds/data/ui` |
| 3851-3856 | `actual_odds_example` | function | Odds, market, line, or candidate processing support. | modules.pregame_content | `odds/data/ui` |
| 3863-3866 | `user_odds_slug` | function | Odds, market, line, or candidate processing support. | re | `odds/data/ui` |
| 3869-3870 | `user_odds_cache_path` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `odds/data/ui` |
| 3873-3891 | `load_user_odds_cache` | function | Odds, market, line, or candidate processing support. | datetime, json | `odds/data/ui` |
| 3894-3919 | `save_user_odds_cache` | function | Odds, market, line, or candidate processing support. | datetime, json, modules.pregame_content | `odds/data/ui` |
| 3922-3925 | `clear_user_odds_cache` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `odds/data/ui` |
| 3928-3935 | `format_cache_time` | function | Data path, cache, snapshot, load/save, or persistence support. | datetime, zoneinfo | `odds/data/ui` |
| 3938-3961 | `normalize_portfolio_name` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | re | `odds/data/ui` |
| 3964-4020 | `render_actual_odds_input` | function | Render Streamlit/UI section or display rows. | modules.user_odds, pandas, pd, st, streamlit | `odds/data/ui` |
| 4023-4030 | `current_actual_odds` | function | Odds, market, line, or candidate processing support. | modules.user_odds, st, streamlit | `odds/data/ui` |
| 4037-4044 | `history_slug` | function | Data path, cache, snapshot, load/save, or persistence support. | modules.schedule_client, re | `odds/data/ui` |
| 4047-4048 | `snapshot_path` | function | Data path, cache, snapshot, load/save, or persistence support. | internal helpers / local values | `odds/data/ui` |
| 4051-4052 | `legacy_snapshot_path` | function | Data path, cache, snapshot, load/save, or persistence support. | internal helpers / local values | `odds/data/ui` |
| 4055-4056 | `pre_match_snapshot_path` | function | Data path, cache, snapshot, load/save, or persistence support. | internal helpers / local values | `odds/data/ui` |
| 4059-4060 | `post_match_snapshot_path` | function | Data path, cache, snapshot, load/save, or persistence support. | internal helpers / local values | `odds/data/ui` |
| 4063-4064 | `my_portfolio_path` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `odds/data/ui` |
| 4067-4078 | `json_safe` | function | Rating breakdown, actual odds cache, history paths, manual portfolio parsing/input. | datetime, pathlib | `odds/data/ui` |
| 4081-4099 | `save_match_snapshot` | function | Data path, cache, snapshot, load/save, or persistence support. | datetime, json, modules.pregame_content | `odds/data/ui` |
| 4102-4145 | `save_post_match_snapshot` | function | Data path, cache, snapshot, load/save, or persistence support. | datetime, json, modules.pregame_content | `odds/data/ui` |
| 4148-4159 | `load_match_snapshot` | function | Data path, cache, snapshot, load/save, or persistence support. | json | `odds/data/ui` |
| 4162-4169 | `load_post_match_snapshot` | function | Data path, cache, snapshot, load/save, or persistence support. | json | `odds/data/ui` |
| 4172-4177 | `my_portfolio_example` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `odds/data/ui` |
| 4180-4190 | `my_portfolio_market_key` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | re | `odds/data/ui` |
| 4204-4207 | `compact_text` | function | Rating breakdown, actual odds cache, history paths, manual portfolio parsing/input. | re | `odds/data/ui` |
| 4210-4222 | `team_alias_map` | function | Fixture, schedule, team, or match metadata support. | modules.pregame_content | `odds/data/ui` |
| 4225-4238 | `canonical_bet_text` | function | Rating breakdown, actual odds cache, history paths, manual portfolio parsing/input. | modules.pregame_content, re | `odds/data/ui` |
| 4241-4248 | `first_number` | function | Rating breakdown, actual odds cache, history paths, manual portfolio parsing/input. | re | `odds/data/ui` |
| 4251-4283 | `handicap_side_and_line` | function | Odds, market, line, or candidate processing support. | modules.portfolio_engine, modules.pregame_content, re | `odds/data/ui` |
| 4286-4298 | `handicap_candidate_matches` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `odds/data/ui` |
| 4301-4343 | `split_handicap_candidate` | function | Odds, market, line, or candidate processing support. | modules.portfolio_engine | `odds/data/ui` |
| 4346-4368 | `match_portfolio_candidate` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | modules.user_odds | `odds/data/ui` |
| 4371-4375 | `normalize_portfolio_line` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | re | `odds/data/ui` |
| 4378-4404 | `split_portfolio_amount` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | re | `odds/data/ui` |
| 4407-4416 | `outcome_selection_for_manual_item` | function | Rating breakdown, actual odds cache, history paths, manual portfolio parsing/input. | modules.portfolio_engine, modules.pregame_content | `odds/data/ui` |
| 4419-4449 | `infer_portfolio_type_and_selection` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | modules.user_odds, re | `odds/data/ui` |
| 4452-4489 | `parse_my_portfolio` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | modules.portfolio_engine | `odds/data/ui` |
| 4492-4587 | `portfolio_market_candidates` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | modules.portfolio_engine, modules.user_odds, re | `odds/data/ui` |
| 4590-4599 | `unmatched_portfolio_reason` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `odds/data/ui` |
| 4602-4609 | `load_my_portfolio` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | json | `odds/data/ui` |
| 4612-4623 | `save_my_portfolio` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | datetime, json, modules.pregame_content | `odds/data/ui` |
| 4626-4691 | `render_my_portfolio_input` | function | Render Streamlit/UI section or display rows. | html, pandas, pd, st, streamlit | `odds/data/ui` |
| 4694-4726 | `snapshot_portfolio_candidates` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | modules.pregame_content | `portfolio/strategy/ui` |
| 4729-4763 | `render_my_portfolio_settlement` | function | Render Streamlit/UI section or display rows. | pandas, pd, st, streamlit | `portfolio/strategy/ui` |
| 4766-4771 | `strategy_item_names` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `portfolio/strategy/ui` |
| 4774-4786 | `active_portfolio_items` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/ui` |
| 4789-4794 | `normalized_duplicate_value` | function | My portfolio settlement, duplicate display, ranking rows, hybrid metadata, decision cards. | internal helpers / local values | `portfolio/strategy/ui` |
| 4797-4798 | `portfolio_item_duplicate_key` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | modules.portfolio_engine | `portfolio/strategy/ui` |
| 4801-4803 | `portfolio_duplicate_key` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/ui` |
| 4806-4827 | `dedupe_portfolios_for_display` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/ui` |
| 4830-4844 | `strategy_difference` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `portfolio/strategy/ui` |
| 4847-4854 | `strategy_asset_names` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `portfolio/strategy/ui` |
| 4857-4876 | `strategy_main_script` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `portfolio/strategy/ui` |
| 4879-4911 | `portfolio_ranking_rows` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/ui` |
| 4914-4921 | `shadow_verdict_label` | function | My portfolio settlement, duplicate display, ranking rows, hybrid metadata, decision cards. | internal helpers / local values | `portfolio/strategy/ui` |
| 4924-4930 | `hybrid_v2_sleeve_share_label` | function | My portfolio settlement, duplicate display, ranking rows, hybrid metadata, decision cards. | internal helpers / local values | `portfolio/strategy/ui` |
| 4933-4941 | `hybrid_v2_status_label` | function | My portfolio settlement, duplicate display, ranking rows, hybrid metadata, decision cards. | internal helpers / local values | `portfolio/strategy/ui` |
| 4944-4945 | `portfolio_display_name` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/ui` |
| 4948-4961 | `hybrid_v2_sleeve_share` | function | My portfolio settlement, duplicate display, ranking rows, hybrid metadata, decision cards. | internal helpers / local values | `portfolio/strategy/ui` |
| 4964-4975 | `hybrid_v2_sleeve_status` | function | My portfolio settlement, duplicate display, ranking rows, hybrid metadata, decision cards. | internal helpers / local values | `portfolio/strategy/ui` |
| 4978-4991 | `hybrid_v2_sleeve_reason` | function | My portfolio settlement, duplicate display, ranking rows, hybrid metadata, decision cards. | internal helpers / local values | `portfolio/strategy/ui` |
| 4994-5022 | `attach_hybrid_v2_visible_metadata` | function | My portfolio settlement, duplicate display, ranking rows, hybrid metadata, decision cards. | internal helpers / local values | `portfolio/strategy/ui` |
| 5025-5122 | `match_betting_score` | function | Score/probability distribution or outcome-path support. | internal helpers / local values | `portfolio/strategy/ui` |
| 5125-5162 | `recommended_stake_mvp` | function | My portfolio settlement, duplicate display, ranking rows, hybrid metadata, decision cards. | internal helpers / local values | `portfolio/strategy/ui` |
| 5165-5186 | `render_match_decision_cards` | function | Render Streamlit/UI section or display rows. | modules.portfolio_engine, st, streamlit | `portfolio/strategy/ui` |
| 5189-5198 | `strategy_difference_rows` | function | Strategy construction, comparison, scoring, or explanation support. | internal helpers / local values | `portfolio/strategy/ui` |
| 5201-5228 | `portfolio_detail_rows` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/ui` |
| 5231-5234 | `render_portfolio_detail_bundle` | function | Render Streamlit/UI section or display rows. | pandas, pd, st, streamlit | `portfolio/strategy/ui` |
| 5237-5253 | `evaluated_my_portfolio_strategy` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/ui` |
| 5256-5260 | `portfolio_goal_text` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/ui` |
| 5263-5304 | `portfolio_downgrade_reason` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/ui` |
| 5307-5404 | `render_portfolio_detail_expanders` | function | Render Streamlit/UI section or display rows. | pandas, pd, st, streamlit | `portfolio/strategy/ui` |
| 5407-5440 | `render_portfolio_ranking` | function | Render Streamlit/UI section or display rows. | modules.perf_logger, modules.shadow_metadata, pandas, pd, st, streamlit | `portfolio/strategy/ui` |
| 5443-5463 | `render_actual_market_odds_summary` | function | Render Streamlit/UI section or display rows. | modules.perf_logger, pandas, pd, st, streamlit | `portfolio/strategy/ui` |
| 5466-5472 | `actual_odds_expander_title` | function | Odds, market, line, or candidate processing support. | internal helpers / local values | `portfolio/strategy/ui` |
| 5475-5479 | `actual_value_expander_title` | function | My portfolio settlement, duplicate display, ranking rows, hybrid metadata, decision cards. | internal helpers / local values | `portfolio/strategy/ui` |
| 5482-5487 | `my_portfolio_expander_title` | function | Portfolio parsing, scoring, ranking, settlement, or display support. | internal helpers / local values | `portfolio/strategy/ui` |
| 5490-5508 | `render_advanced_research` | function | Render Streamlit/UI section or display rows. | modules.perf_logger, pandas, pd, st, streamlit | `portfolio/strategy/ui` |
| 5511-5538 | `path_layer_summary` | function | Data path, cache, snapshot, load/save, or persistence support. | modules.market_utils | `analysis/odds/ui` |
| 5541-5549 | `render_path_layers` | function | Render Streamlit/UI section or display rows. | st, streamlit | `analysis/odds/ui` |
| 5552-5560 | `render_market_consensus_panel` | function | Render Streamlit/UI section or display rows. | st, streamlit | `analysis/odds/ui` |
| 5563-5573 | `render_core_risk_summary` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `analysis/odds/ui` |
| 5576-5587 | `pressure_type_cn` | function | Path layers, market consensus, qualification behavior, team/market/risk render sections. | internal helpers / local values | `analysis/odds/ui` |
| 5590-5596 | `pressure_score_text` | function | Score/probability distribution or outcome-path support. | modules.pregame_content | `analysis/odds/ui` |
| 5599-5627 | `render_qualification_behavior` | function | Render Streamlit/UI section or display rows. | st, streamlit | `analysis/odds/ui` |
| 5630-5674 | `render_core_decision` | function | Render Streamlit/UI section or display rows. | st, streamlit | `analysis/odds/ui` |
| 5677-5714 | `summarize_form` | function | Path layers, market consensus, qualification behavior, team/market/risk render sections. | internal helpers / local values | `analysis/odds/ui` |
| 5717-5731 | `summarize_static_form` | function | Path layers, market consensus, qualification behavior, team/market/risk render sections. | internal helpers / local values | `analysis/odds/ui` |
| 5734-5748 | `team_form_summary` | function | Fixture, schedule, team, or match metadata support. | modules.pregame_content | `analysis/odds/ui` |
| 5751-5792 | `render_recent_form` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `analysis/odds/ui` |
| 5795-5796 | `worldcup_data_match_dir` | function | Path layers, market consensus, qualification behavior, team/market/risk render sections. | modules.worldcup_db | `analysis/odds/ui` |
| 5799-5811 | `render_data_completeness` | function | Render Streamlit/UI section or display rows. | pandas, pd, st, streamlit | `analysis/odds/ui` |
| 5814-5834 | `standings_row_for_team` | function | Fixture, schedule, team, or match metadata support. | modules.schedule_client | `analysis/odds/ui` |
| 5837-5853 | `team_profile_metrics` | function | Fixture, schedule, team, or match metadata support. | internal helpers / local values | `analysis/odds/ui` |
| 5856-5873 | `lineup_rows_for_team` | function | Fixture, schedule, team, or match metadata support. | internal helpers / local values | `analysis/odds/ui` |
| 5876-5890 | `injury_rows_for_team` | function | Fixture, schedule, team, or match metadata support. | internal helpers / local values | `analysis/odds/ui` |
| 5893-5962 | `render_team_intelligence` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, modules.team_profile_client, pandas, pd, st, streamlit | `analysis/odds/ui` |
| 5965-5986 | `render_match_winner` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `analysis/odds/ui` |
| 5989-6025 | `render_handicap` | function | Render Streamlit/UI section or display rows. | modules.market_utils, pandas, pd, st, streamlit | `analysis/odds/ui` |
| 6028-6054 | `render_totals` | function | Render Streamlit/UI section or display rows. | modules.market_utils, st, streamlit | `analysis/odds/ui` |
| 6057-6093 | `render_correct_score_market` | function | Render Streamlit/UI section or display rows. | modules.market_utils, pandas, pd, st, streamlit | `analysis/odds/ui` |
| 6096-6112 | `render_value` | function | Render Streamlit/UI section or display rows. | st, streamlit | `analysis/odds/ui` |
| 6115-6131 | `render_polymarket` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `analysis/odds/ui` |
| 6134-6157 | `render_market_consistency` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `analysis/odds/ui` |
| 6160-6173 | `render_predicted_lineup_for_team` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `analysis/odds/ui` |
| 6176-6180 | `render_storylines` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `analysis/odds/ui` |
| 6183-6187 | `render_risk_notes` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `analysis/odds/ui` |
| 6190-6224 | `render_risk_analysis` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, modules.result_distribution, st, streamlit | `analysis/odds/ui` |
| 6227-6337 | `render_post_match_analysis_tab` | function | Render Streamlit/UI section or display rows. | modules.schedule_client, modules.user_odds, pandas, pd, st, streamlit | `backtest/ui/data` |
| 6340-6370 | `render_injuries_lineups` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `backtest/ui/data` |
| 6373-6385 | `render_technical_notes` | function | Render Streamlit/UI section or display rows. | st, streamlit | `backtest/ui/data` |
| 6388-6396 | `render_detail_data_source` | function | Render Streamlit/UI section or display rows. | st, streamlit | `ui/data` |
| 6399-6402 | `schedule_match_text` | function | Fixture, schedule, team, or match metadata support. | internal helpers / local values | `ui/data` |
| 6405-6411 | `fixture_time_text` | function | Fixture, schedule, team, or match metadata support. | modules.schedule_client | `ui/data` |
| 6414-6420 | `date_until_world_cup` | function | Schedule cards, search, date navigation, standings, teams, tournament info. | datetime, zoneinfo | `ui/data` |
| 6423-6453 | `team_visual` | function | Fixture, schedule, team, or match metadata support. | st, streamlit | `ui/data` |
| 6456-6464 | `fixture_status_text` | function | Fixture, schedule, team, or match metadata support. | modules.schedule_client | `ui/data` |
| 6467-6471 | `fixture_score_text` | function | Score/probability distribution or outcome-path support. | modules.schedule_client | `ui/data` |
| 6474-6478 | `open_fixture` | function | Fixture, schedule, team, or match metadata support. | modules.schedule_client, st, streamlit | `ui/data` |
| 6481-6517 | `render_schedule_card` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, modules.schedule_client, st, streamlit | `ui/data` |
| 6520-6525 | `render_schedule_section` | function | Render Streamlit/UI section or display rows. | st, streamlit | `ui/data` |
| 6528-6536 | `render_portal_banner` | function | Render Streamlit/UI section or display rows. | st, streamlit | `ui/data` |
| 6539-6561 | `render_search` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, modules.schedule_client, st, streamlit | `ui/data` |
| 6564-6566 | `render_today_matches` | function | Render Streamlit/UI section or display rows. | st, streamlit | `ui/data` |
| 6569-6622 | `render_date_nav` | function | Render Streamlit/UI section or display rows. | datetime, modules.schedule_client, st, streamlit, zoneinfo | `ui/data` |
| 6625-6634 | `render_focus_matches` | function | Render Streamlit/UI section or display rows. | modules.schedule_client, st, streamlit | `ui/data` |
| 6637-6646 | `render_match_status_sections` | function | Render Streamlit/UI section or display rows. | modules.schedule_client, st, streamlit | `ui/data` |
| 6649-6658 | `render_popular_matches` | function | Render Streamlit/UI section or display rows. | st, streamlit | `ui/data` |
| 6661-6665 | `render_full_schedule` | function | Render Streamlit/UI section or display rows. | modules.schedule_client, st, streamlit | `ui/data` |
| 6668-6725 | `render_standings` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, modules.schedule_client, pandas, pd, st, streamlit | `ui/data` |
| 6728-6743 | `render_teams` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `ui/data` |
| 6746-6754 | `render_market_center` | function | Render Streamlit/UI section or display rows. | st, streamlit | `ui/data` |
| 6757-6763 | `render_finished_matches` | function | Render Streamlit/UI section or display rows. | modules.schedule_client, st, streamlit | `ui/data` |
| 6766-6777 | `render_knockout_bracket` | function | Render Streamlit/UI section or display rows. | modules.pregame_content, st, streamlit | `ui/data` |
| 6780-6788 | `render_tournament_stats_center` | function | Render Streamlit/UI section or display rows. | modules.schedule_client, st, streamlit | `ui/data` |
| 6791-6803 | `render_cache_notes` | function | Render Streamlit/UI section or display rows. | st, streamlit | `ui/data` |
| 6806-6835 | `render_schedule_page` | function | Render Streamlit/UI section or display rows. | modules.perf_logger, modules.schedule_client, st, streamlit | `ui/data` |
| 6838-7010 | `render_analysis_page` | function | Render Streamlit/UI section or display rows. | modules.betting_opinion, modules.decision_engine, modules.game_behavior_engine, modules.match_parser, modules.mock_data, modules.odds_client, ... | `ui/data/strategy/portfolio` |
| 7013-7051 | `render_post_match_page` | function | Render Streamlit/UI section or display rows. | modules.match_parser, modules.pregame_content, st, streamlit | `ui/data/strategy/portfolio` |
| 7054-7057 | `load_config` | function | Data path, cache, snapshot, load/save, or persistence support. | pathlib, yaml | `ui` |

## Major Inline Blocks

| Lines | Name | Type | Responsibility | Dependencies / globals | Suggested target |
|---:|---|---|---|---|---|
| 1-104 | imports_and_globals | block | Imports external libraries and domain modules; defines `MODEL_VERSION_TRACKING`. | Streamlit, pandas, yaml, `modules.*` imports | `ui/data/orchestration` |
| 7059-7079 | runtime_streamlit_bootstrap | block | Loads config, sets Streamlit page config, initializes session state, dispatches current page. | `load_config`, `card_css`, `st.session_state`, render page functions | `ui` |

## Manual Review Notes

- No top-level classes were detected.
- Nested functions, if any, are not listed separately because this report focuses on top-level extraction boundaries.
- Dependency hints are static and approximate; runtime Streamlit state and global constants require manual review before extraction.
