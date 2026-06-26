"""Shadow metadata helpers for portfolio ranking.

These helpers annotate already-ranked strategies with observational metadata.
They do not change legacy scores, ordering, allocations, or recommendations.
"""

from __future__ import annotations

from copy import copy
from typing import Any


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _role_exposure(strategy: dict[str, Any]) -> dict[str, float]:
    style = strategy.get("portfolio_style") or {}
    exposure = style.get("role_exposure") or {}
    if isinstance(exposure, dict):
        return {str(key): _num(value) for key, value in exposure.items()}
    return {}


def _active_items(strategy: dict[str, Any]) -> list[dict[str, Any]]:
    items = strategy.get("items") or []
    if not isinstance(items, list):
        return []
    active = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if _num(item.get("share")) > 0 or _num(item.get("amount")) > 0:
            active.append(item)
    return active


def _role_balance_score(strategy: dict[str, Any]) -> float:
    role_constraint = strategy.get("role_constraint") or {}
    adjustment = _num(role_constraint.get("adjustment"))
    exposure = _role_exposure(strategy)
    direction = exposure.get("方向资产", 0.0)
    insurance = exposure.get("保险资产", 0.0)
    return_share = exposure.get("收益资产", 0.0)
    tempo = exposure.get("节奏资产", 0.0)
    tail = exposure.get("尾部资产", 0.0)
    active_items = _active_items(strategy)
    active_types = {str(item.get("type") or "") for item in active_items}
    winner_only = bool(active_items) and active_types == {"winner"}
    correct_score_only = bool(active_items) and active_types == {"correct_score"}

    score = 50 + adjustment * 0.60
    if winner_only:
        score += 45
    if correct_score_only:
        score -= 18
    if direction >= 0.20:
        score += 10
    if 0.15 <= insurance <= 0.55:
        score += 8
    if 0.10 <= return_share <= 0.60:
        score += 8
    if tempo > 0.50 and direction < 0.20:
        score -= 18
    if tail > 0.20:
        score -= 16
    elif tail > 0.15:
        score -= 8
    return _clamp(score)


def _tail_exposure(strategy: dict[str, Any]) -> float:
    style = strategy.get("portfolio_style") or {}
    exposure = _num(style.get("tail_share"))
    if exposure:
        return exposure
    roles = _role_exposure(strategy)
    return roles.get("尾部资产", 0.0)


def _tail_warning(tail: float) -> str | None:
    if tail > 0.35:
        return "Not default-eligible in future v2"
    if tail > 0.20:
        return "Tail-heavy"
    if tail > 0.15:
        return "Watch"
    return None


def _scenario_score(strategy: dict[str, Any]) -> float:
    expected_yield = _num(strategy.get("expected_yield"))
    sharpe = _num(strategy.get("sharpe_ratio"))
    consistency = strategy.get("consistency_score")
    consistency_value = _num(consistency, 0.72 if consistency is None else 0.0)
    direction = _num(strategy.get("direction_alignment"))
    strategic = _num(strategy.get("strategic_value"))
    style = strategy.get("portfolio_style") or {}
    exposure = _role_exposure(strategy)
    tail = _tail_exposure(strategy)
    tempo = _num(style.get("tempo_share")) or exposure.get("节奏资产", 0.0)

    value_layer = _clamp(50 + expected_yield * 140 + max(0.0, sharpe) * 25) * 0.15
    consistency_layer = _clamp(consistency_value * 100) * 0.20
    role_layer = _role_balance_score(strategy) * 0.35
    direction_layer = _clamp((direction + strategic) / 2 if direction or strategic else 55) * 0.15
    coverage_layer = _clamp(_num(strategy.get("coverage")) * 100, 0, 100) * 0.10
    simplicity_layer = _clamp(100 - _num(strategy.get("concentration")) * 90) * 0.05

    penalty = 0.0
    if tail > 0.15:
        penalty += (tail - 0.15) * 70
    if tempo > 0.55 and exposure.get("方向资产", 0.0) < 0.20:
        penalty += 10

    return round(_clamp(value_layer + consistency_layer + role_layer + direction_layer + coverage_layer + simplicity_layer - penalty), 1)


def _verdict(rank_difference: int, tail_warning: str | None) -> str:
    if tail_warning in {"Tail-heavy", "Not default-eligible in future v2"} and abs(rank_difference) >= 2:
        return "Disagreement"
    if abs(rank_difference) >= 3:
        return "Disagreement"
    if abs(rank_difference) == 2:
        return "Watch"
    return "Agreement"


def _rank_reason(strategy: dict[str, Any], rank_difference: int, tail_warning: str | None) -> str:
    exposure = _role_exposure(strategy)
    tempo = exposure.get("节奏资产", 0.0)
    direction = exposure.get("方向资产", 0.0)
    insurance = exposure.get("保险资产", 0.0)
    return_share = exposure.get("收益资产", 0.0)

    if rank_difference > 0:
        if tail_warning:
            return f"Scenario ranking downgraded this portfolio because tail exposure is elevated ({tail_warning})."
        if tempo > 0.55 and direction < 0.20:
            return "Scenario ranking downgraded this portfolio because it is mainly a tempo asset and has weak direction coverage."
        if direction + return_share < 0.25:
            return "Scenario ranking downgraded this portfolio because it has limited main-scenario return coverage."
        return "Scenario ranking downgraded this portfolio because its scenario structure is weaker than alternatives."
    if rank_difference < 0:
        if direction >= 0.20 and insurance >= 0.15:
            return "Scenario ranking upgraded this portfolio because it combines direction coverage with insurance structure."
        if return_share >= 0.20:
            return "Scenario ranking upgraded this portfolio because it has clearer main-scenario return coverage."
        return "Scenario ranking upgraded this portfolio because it is more scenario-consistent than its legacy rank suggests."
    return "Legacy ranking and scenario ranking broadly agree."


def attach_shadow_metadata(
    strategies: list[dict[str, Any]],
    match: dict[str, Any] | None = None,
    distribution: dict[str, Any] | None = None,
    scenario_engine: dict[str, Any] | None = None,
    recommendation_audit: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return strategies in the same legacy order with strategy['shadow'] added.

    The optional arguments are accepted for future Scenario Engine and Auditor
    integration. v0.1 intentionally relies only on existing strategy fields.
    """

    annotated: list[dict[str, Any]] = []
    shadow_rows: list[tuple[int, float, dict[str, Any]]] = []

    for legacy_rank, strategy in enumerate(strategies or [], start=1):
        copied = copy(strategy)
        scenario_score = _scenario_score(copied)
        shadow_rows.append((legacy_rank, scenario_score, copied))
        annotated.append(copied)

    scenario_order = sorted(shadow_rows, key=lambda row: (-row[1], row[0]))
    scenario_rank_by_legacy_rank = {
        legacy_rank: scenario_rank
        for scenario_rank, (legacy_rank, _score, _strategy) in enumerate(scenario_order, start=1)
    }

    for legacy_rank, scenario_score, strategy in shadow_rows:
        scenario_rank = scenario_rank_by_legacy_rank[legacy_rank]
        rank_difference = scenario_rank - legacy_rank
        tail = _tail_exposure(strategy)
        tail_warning = _tail_warning(tail)
        verdict = _verdict(rank_difference, tail_warning)
        strategy["shadow"] = {
            "enabled": True,
            "mode": "shadow",
            "legacy_authoritative": True,
            "legacy_rank": legacy_rank,
            "legacy_score": strategy.get("score"),
            "scenario_rank": scenario_rank,
            "scenario_score": scenario_score,
            "rank_difference": rank_difference,
            "shadow_verdict": verdict,
            "scenario_rank_reason": _rank_reason(strategy, rank_difference, tail_warning),
        }

    return annotated
