#!/usr/bin/env python3
"""Generate read-only golden risk contract v1 fixtures.

This script serializes existing saved golden v2 outputs into the canonical
risk_contract_v1 shape. It does not import app.py, Streamlit, or runtime modules,
and it does not mutate any input file.
"""

from __future__ import annotations

import json
import subprocess
import hashlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_V2_PATH = ROOT / "reports" / "golden_output_snapshot_v2.json"
OUTPUT_PATH = ROOT / "reports" / "golden_risk_contract_v1.json"
REPORT_PATH = ROOT / "reports" / "golden_risk_contract_v1_serializer_report.md"

CONTRACT_VERSION = "risk_contract_v1"
CONTRACT_STATUS = "observed"
ROUNDING_UNIT = 100
FLOAT_TOLERANCE = 1e-6


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def read_source_snapshot_check(source_path: str, expected_sha256: str | None) -> dict[str, Any]:
    path = ROOT / source_path
    result = {
        "source_path": source_path,
        "exists": path.exists(),
        "sha256": None,
        "matches_expected_sha256": None,
    }
    if not path.exists():
        return result
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    result["sha256"] = digest
    if expected_sha256:
        result["matches_expected_sha256"] = digest == expected_sha256
    return result


def get_path(data: Any, path: list[Any], default: Any = None) -> Any:
    current = data
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
            current = current[key]
        else:
            return default
    return current


def as_number(value: Any) -> float | int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return value
    return None


def rounded_ratio(numerator: Any, denominator: Any) -> float | None:
    num = as_number(numerator)
    den = as_number(denominator)
    if num is None or den in (None, 0):
        return None
    return num / den


def split_match_name(match_name: str | None) -> tuple[str | None, str | None]:
    if not match_name or " vs " not in match_name:
        return None, None
    home, away = match_name.split(" vs ", 1)
    return home, away


def item_amount(item: dict[str, Any]) -> float | int | None:
    return as_number(item.get("amount"))


def total_amount(items: list[dict[str, Any]]) -> float | int | None:
    amounts = [item_amount(item) for item in items]
    known = [amount for amount in amounts if amount is not None]
    if not items or len(known) != len(items):
        return None
    return sum(known)


def asset_types(items: list[dict[str, Any]]) -> list[str]:
    values = []
    for item in items:
        value = item.get("type")
        if isinstance(value, str) and value not in values:
            values.append(value)
    return values


def correct_score_stake(items: list[dict[str, Any]]) -> float | int | None:
    total = 0
    seen = False
    for item in items:
        if item.get("type") == "correct_score":
            amount = item_amount(item)
            if amount is None:
                return None
            total += amount
            seen = True
    return total if seen else 0


def dominant_asset_share(items: list[dict[str, Any]], total_stake: Any) -> float | None:
    total = as_number(total_stake)
    if total in (None, 0) or not items:
        return None
    amounts = [item_amount(item) for item in items]
    if any(amount is None for amount in amounts):
        return None
    return max(amounts) / total


def data_completeness(metadata: dict[str, Any]) -> str:
    if metadata.get("odds_found") is False:
        return "missing"
    if metadata.get("actual_odds_item_count") == 0:
        return "partial"
    if metadata.get("odds_found") is True:
        return "complete"
    return "unknown"


def source_field(value: Any, field_path: str, missing_fields: list[str]) -> Any:
    if value is None:
        missing_fields.append(field_path)
    return value


def invariant_counts(contracts: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    keys = [
        "allocation_total_equals_decision_stake",
        "loss_ratio_matches_max_loss_over_total_stake",
        "correct_score_share_within_limit",
        "rank1_eligibility_has_gate_payload",
    ]
    counts: dict[str, dict[str, int]] = {}
    for key in keys:
        counter: Counter[str] = Counter()
        for contract in contracts:
            value = contract["invariants"][key]
            if value is True:
                counter["true"] += 1
            elif value is False:
                counter["false"] += 1
            else:
                counter["null"] += 1
        counts[key] = dict(counter)
    return counts


def make_invariants(
    *,
    allocation_total: Any,
    decision_stake: Any,
    total_stake: Any,
    max_loss: Any,
    loss_ratio: Any,
    correct_score_share_value: Any,
    correct_score_limit: Any,
    rank_position: int,
    source_risk_gate: Any,
    missing_fields: list[str],
) -> dict[str, Any]:
    allocation_total_number = as_number(allocation_total)
    decision_stake_number = as_number(decision_stake)
    if allocation_total_number is None or decision_stake_number is None:
        allocation_check = None
    else:
        allocation_check = allocation_total_number == decision_stake_number

    total_stake_number = as_number(total_stake)
    max_loss_number = as_number(max_loss)
    loss_ratio_number = as_number(loss_ratio)
    if total_stake_number in (None, 0) or max_loss_number is None or loss_ratio_number is None:
        loss_ratio_check = None
    else:
        expected = max_loss_number / total_stake_number
        loss_ratio_check = abs(loss_ratio_number - expected) <= FLOAT_TOLERANCE

    correct_score_share_number = as_number(correct_score_share_value)
    correct_score_limit_number = as_number(correct_score_limit)
    if correct_score_share_number is None or correct_score_limit_number is None:
        correct_score_check = None
    else:
        correct_score_check = correct_score_share_number <= correct_score_limit_number

    if rank_position == 1:
        rank_gate_check = isinstance(source_risk_gate, dict) and source_risk_gate.get("rank1_eligible") is not None
    else:
        rank_gate_check = None

    return {
        "allocation_total_equals_decision_stake": allocation_check,
        "loss_ratio_matches_max_loss_over_total_stake": loss_ratio_check,
        "correct_score_share_within_limit": correct_score_check,
        "rank1_eligibility_has_gate_payload": rank_gate_check,
        "missing_required_fields": sorted(set(missing_fields)),
    }


def make_contract(
    *,
    source_snapshot_id: str,
    match_payload: dict[str, Any],
    strategy: dict[str, Any],
    rank_position: int,
    generated_at: str,
    code_ref: str,
) -> dict[str, Any]:
    metadata = match_payload["metadata"]
    decision = get_path(match_payload, ["final_recommendation", "decision"], {})
    match_info = get_path(match_payload, ["final_recommendation", "match_info"], {})
    items = strategy.get("items") if isinstance(strategy.get("items"), list) else []
    strategy_name = strategy.get("name") or strategy.get("rank_name") or "unknown"
    home_team, away_team = split_match_name(metadata.get("match"))
    total_stake = total_amount(items)
    max_loss = strategy.get("max_loss")
    loss_ratio = rounded_ratio(max_loss, total_stake)
    coverage_metrics = strategy.get("coverage_metrics") if isinstance(strategy.get("coverage_metrics"), dict) else {}
    portfolio_style = strategy.get("portfolio_style") if isinstance(strategy.get("portfolio_style"), dict) else {}
    portfolio_score_components = (
        strategy.get("portfolio_score_components")
        if isinstance(strategy.get("portfolio_score_components"), dict)
        else {}
    )
    score_components = strategy.get("score_components") if isinstance(strategy.get("score_components"), dict) else {}
    source_risk_gate = strategy.get("risk_gate")
    missing_fields: list[str] = []

    decision_stake = get_path(decision, ["recommended_stake", "amount"])
    correct_score_amount = correct_score_stake(items)
    correct_score_share_value = rounded_ratio(correct_score_amount, total_stake)
    correct_score_limit = None
    tail_share = portfolio_style.get("tail_share")
    tail_asset_stake = None
    if as_number(tail_share) is not None and as_number(total_stake) is not None:
        tail_asset_stake = tail_share * total_stake

    risk_gate = {
        "risk_level": "UNKNOWN",
        "rank1_eligible": None,
        "gate_reasons": [],
        "hard_blockers": [],
        "soft_warnings": [],
    }
    if isinstance(source_risk_gate, dict):
        risk_gate = {
            "risk_level": source_risk_gate.get("risk_level", "UNKNOWN"),
            "rank1_eligible": source_risk_gate.get("rank1_eligible"),
            "gate_reasons": source_risk_gate.get("gate_reasons", []),
            "hard_blockers": source_risk_gate.get("hard_blockers", []),
            "soft_warnings": source_risk_gate.get("soft_warnings", []),
        }

    market_disagreement = decision.get("market_disagreement") if isinstance(decision.get("market_disagreement"), dict) else {}
    direction_confidence = decision.get("direction_confidence") if isinstance(decision.get("direction_confidence"), dict) else {}
    upset_index = decision.get("upset_index") if isinstance(decision.get("upset_index"), dict) else {}

    allocation_total = total_stake
    stake_contract = {
        "decision_stake": source_field(decision_stake, "stake_contract.decision_stake", missing_fields),
        "decision_stake_source": "decision.recommended_stake.amount" if decision_stake is not None else "unknown",
        "display_stake": None,
        "rounding_unit": ROUNDING_UNIT,
        "rounding_residue_target": "largest_share_or_highest_weight_item",
        "allocation_total": source_field(allocation_total, "stake_contract.allocation_total", missing_fields),
        "allocation_matches_decision_stake": None,
    }
    if as_number(allocation_total) is not None and as_number(decision_stake) is not None:
        stake_contract["allocation_matches_decision_stake"] = allocation_total == decision_stake

    risk_inputs = {
        "total_stake": source_field(total_stake, "risk_inputs.total_stake", missing_fields),
        "max_loss": source_field(max_loss, "risk_inputs.max_loss", missing_fields),
        "loss_ratio": source_field(loss_ratio, "risk_inputs.loss_ratio", missing_fields),
        "volatility": source_field(strategy.get("volatility"), "risk_inputs.volatility", missing_fields),
        "concentration": source_field(strategy.get("concentration"), "risk_inputs.concentration", missing_fields),
        "risk_reward": source_field(strategy.get("risk_reward"), "risk_inputs.risk_reward", missing_fields),
        "expected_profit": strategy.get("expected_profit"),
        "expected_yield": strategy.get("expected_yield"),
        "sharpe_ratio": strategy.get("sharpe_ratio"),
        "stability_score": strategy.get("stability_score"),
    }

    scenario_risk = {
        "main_path_positive_coverage": source_field(
            coverage_metrics.get("main_coverage"),
            "scenario_risk.main_path_positive_coverage",
            missing_fields,
        ),
        "zero_loss_coverage": source_field(
            coverage_metrics.get("zero_risk"),
            "scenario_risk.zero_loss_coverage",
            missing_fields,
        ),
        "failed_scenario_probability": None,
        "adjacent_path_failure": None,
        "narrow_exact_score_dependency": None,
        "pressure_strictness": None,
        "scenario_consistency_score": strategy.get("consistency_score"),
        "shadow_verdict": get_path(strategy, ["shadow", "verdict"], "unknown"),
    }
    for key in [
        "failed_scenario_probability",
        "adjacent_path_failure",
        "narrow_exact_score_dependency",
        "pressure_strictness",
    ]:
        missing_fields.append(f"scenario_risk.{key}")

    market_risk = {
        "direction_confidence": source_field(
            direction_confidence.get("score"),
            "market_risk.direction_confidence",
            missing_fields,
        ),
        "market_disagreement": source_field(
            market_disagreement.get("score"),
            "market_risk.market_disagreement",
            missing_fields,
        ),
        "upset_index": source_field(upset_index.get("score"), "market_risk.upset_index", missing_fields),
        "value_rating": source_field(decision.get("value_rating"), "market_risk.value_rating", missing_fields),
        "liquidity_quality": "unknown",
        "data_completeness": data_completeness(metadata),
    }

    exposure_risk = {
        "correct_score_stake": source_field(
            correct_score_amount,
            "exposure_risk.correct_score_stake",
            missing_fields,
        ),
        "correct_score_share": source_field(
            correct_score_share_value,
            "exposure_risk.correct_score_share",
            missing_fields,
        ),
        "correct_score_limit": source_field(
            correct_score_limit,
            "exposure_risk.correct_score_limit",
            missing_fields,
        ),
        "correct_score_limit_source": "unknown",
        "tail_asset_stake": source_field(tail_asset_stake, "exposure_risk.tail_asset_stake", missing_fields),
        "tail_asset_share": source_field(tail_share, "exposure_risk.tail_asset_share", missing_fields),
        "dominant_asset_share": source_field(
            dominant_asset_share(items, total_stake),
            "exposure_risk.dominant_asset_share",
            missing_fields,
        ),
    }

    if not isinstance(source_risk_gate, dict):
        missing_fields.extend(
            [
                "risk_gate.risk_level",
                "risk_gate.rank1_eligible",
                "risk_gate.gate_reasons",
                "risk_gate.hard_blockers",
                "risk_gate.soft_warnings",
            ]
        )

    risk_score_components = {
        "strategy_risk_control": source_field(
            score_components.get("风险控制"),
            "risk_score_components.strategy_risk_control",
            missing_fields,
        ),
        "portfolio_risk_adjusted_value": portfolio_score_components.get("Risk-Adjusted Value"),
        "portfolio_drawdown_zero_risk": portfolio_score_components.get("Drawdown / Zero Risk"),
        "canonical_risk_score": None,
    }

    if risk_score_components["portfolio_risk_adjusted_value"] is None:
        missing_fields.append("risk_score_components.portfolio_risk_adjusted_value")
    if risk_score_components["portfolio_drawdown_zero_risk"] is None:
        missing_fields.append("risk_score_components.portfolio_drawdown_zero_risk")
    missing_fields.append("risk_score_components.canonical_risk_score")

    invariants = make_invariants(
        allocation_total=allocation_total,
        decision_stake=decision_stake,
        total_stake=total_stake,
        max_loss=max_loss,
        loss_ratio=loss_ratio,
        correct_score_share_value=correct_score_share_value,
        correct_score_limit=correct_score_limit,
        rank_position=rank_position,
        source_risk_gate=source_risk_gate,
        missing_fields=missing_fields,
    )

    return {
        "contract_version": CONTRACT_VERSION,
        "contract_status": CONTRACT_STATUS,
        "producer": {
            "name": "worldcup-analyzer",
            "mode": "golden_v2_read_only_serializer",
            "code_ref": code_ref,
        },
        "source_snapshot_id": source_snapshot_id,
        "generated_at": generated_at,
        "match": {
            "match_id": metadata.get("match_id"),
            "home_team": home_team or get_path(match_info, ["home_team"]),
            "away_team": away_team or get_path(match_info, ["away_team"]),
            "kickoff_time": get_path(match_info, ["kickoff_time"]),
            "snapshot_phase": "pre",
        },
        "strategy_identity": {
            "strategy_id": strategy.get("code") or f"{source_snapshot_id}::rank_{rank_position}",
            "strategy_name": strategy_name,
            "rank_position": rank_position,
            "asset_count": len(items),
            "asset_types": asset_types(items),
        },
        "risk_inputs": risk_inputs,
        "scenario_risk": scenario_risk,
        "market_risk": market_risk,
        "exposure_risk": exposure_risk,
        "risk_gate": risk_gate,
        "stake_contract": stake_contract,
        "risk_score_components": risk_score_components,
        "invariants": invariants,
        "post_match_risk_outcome": None,
    }


def select_strategies(strategies: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    selected = []
    if strategies:
        selected.append((1, strategies[0]))
    if len(strategies) > 1:
        selected.append((2, strategies[1]))
    return selected


def generate() -> tuple[dict[str, Any], str]:
    golden_v2 = read_json(GOLDEN_V2_PATH)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    code_ref = git_head()
    contracts: list[dict[str, Any]] = []
    source_files = [
        "reports/golden_output_snapshot_v2.json",
    ]
    source_snapshot_checks = []
    matches = golden_v2.get("matches", {})
    if not isinstance(matches, dict):
        raise ValueError("Expected reports/golden_output_snapshot_v2.json matches to be an object")

    for source_snapshot_id, match_payload in matches.items():
        metadata = match_payload.get("metadata", {})
        source_path = metadata.get("source_path")
        if source_path:
            source_files.append(source_path)
            source_snapshot_checks.append(
                read_source_snapshot_check(source_path, metadata.get("source_sha256"))
            )
        strategies = get_path(match_payload, ["strategy_ranking", "strategies"], [])
        if not isinstance(strategies, list):
            strategies = []
        for rank_position, strategy in select_strategies(strategies):
            contracts.append(
                make_contract(
                    source_snapshot_id=source_snapshot_id,
                    match_payload=match_payload,
                    strategy=strategy,
                    rank_position=rank_position,
                    generated_at=generated_at,
                    code_ref=code_ref,
                )
            )

    missing_summary: Counter[str] = Counter()
    missing_by_snapshot: dict[str, Counter[str]] = defaultdict(Counter)
    for contract in contracts:
        for field in contract["invariants"]["missing_required_fields"]:
            missing_summary[field] += 1
            missing_by_snapshot[contract["source_snapshot_id"]][field] += 1

    payload = {
        "schema_version": 1,
        "contract_version": CONTRACT_VERSION,
        "contract_status": CONTRACT_STATUS,
        "generated_at": generated_at,
        "generation_rule": "Read-only serialization from reports/golden_output_snapshot_v2.json; no ranking or allocation recomputation.",
        "source_files_read": sorted(set(source_files)),
        "match_count": len(matches),
        "contract_count": len(contracts),
        "source_snapshot_checks": source_snapshot_checks,
        "contracts": contracts,
        "summary": {
            "missing_fields": dict(sorted(missing_summary.items())),
            "invariants": invariant_counts(contracts),
        },
    }
    report = make_report(payload, missing_by_snapshot)
    return payload, report


def make_report(payload: dict[str, Any], missing_by_snapshot: dict[str, Counter[str]]) -> str:
    invariant_summary = payload["summary"]["invariants"]
    missing_fields = payload["summary"]["missing_fields"]
    lines = [
        "# Golden Risk Contract v1 Serializer Report",
        "",
        "This report was generated by `scripts/generate_golden_risk_contract_v1.py`.",
        "",
        "## Source Files Read",
        "",
    ]
    for source in payload["source_files_read"]:
        lines.append(f"- `{source}`")

    lines.extend(["", "## Source Snapshot Read Checks", ""])
    if payload["source_snapshot_checks"]:
        lines.extend(["| Source | Exists | SHA256 matches golden metadata |", "| --- | ---: | ---: |"])
        for check in payload["source_snapshot_checks"]:
            lines.append(
                f"| `{check['source_path']}` | {check['exists']} | {check['matches_expected_sha256']} |"
            )
    else:
        lines.append("- No referenced source snapshots were available in golden metadata.")

    lines.extend(
        [
            "",
            "## Output",
            "",
            "- `reports/golden_risk_contract_v1.json`",
            "",
            "## Counts",
            "",
            f"- Matches processed: {payload['match_count']}",
            f"- Risk contracts generated: {payload['contract_count']}",
            "",
            "## Missing Fields Summary",
            "",
        ]
    )
    if missing_fields:
        lines.extend(["| Field | Count |", "| --- | ---: |"])
        for field, count in missing_fields.items():
            lines.append(f"| `{field}` | {count} |")
    else:
        lines.append("- No missing required fields.")

    lines.extend(["", "## Missing Fields By Snapshot", ""])
    for source_snapshot_id, counter in sorted(missing_by_snapshot.items()):
        lines.append(f"### {source_snapshot_id}")
        if not counter:
            lines.append("")
            lines.append("- No missing required fields.")
        else:
            lines.append("")
            for field, count in sorted(counter.items()):
                lines.append(f"- `{field}`: {count}")
        lines.append("")

    lines.extend(["## Invariant Summary", ""])
    lines.extend(["| Invariant | True | False | Null |", "| --- | ---: | ---: | ---: |"])
    for key, counts in invariant_summary.items():
        lines.append(
            f"| `{key}` | {counts.get('true', 0)} | {counts.get('false', 0)} | {counts.get('null', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Coverage Gaps",
            "",
            "- Saved golden v2 strategies do not include full `risk_gate` payloads, so Rank #1 gate coverage remains false.",
            "- `correct_score_limit` is not stored in golden v2, so correct-score limit checks remain null.",
            "- `failed_scenario_probability`, `adjacent_path_failure`, `narrow_exact_score_dependency`, and `pressure_strictness` are not stored in golden v2.",
            "- `canonical_risk_score` remains null by design until a separately approved formula task exists.",
            "- Pre-match contracts keep `post_match_risk_outcome` as null.",
            "",
            "## Safety Confirmation",
            "",
            "- Runtime code modified: No.",
            "- Golden v1/v2 modified: No.",
            "- Data files modified: No.",
            "- Portfolio extraction remains blocked.",
            "- Backtest remains not ready.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload, report = generate()
    write_json(OUTPUT_PATH, payload)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")
    print(f"Contracts generated: {payload['contract_count']}")


if __name__ == "__main__":
    main()
