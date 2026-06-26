#!/usr/bin/env python3
"""Read-only validation for the generated golden risk contract v1 fixture."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "reports" / "golden_risk_contract_v1.json"


def walk_missing(value: Any, prefix: str = "") -> Counter[str]:
    missing: Counter[str] = Counter()
    if isinstance(value, dict):
        if isinstance(value.get("invariants"), dict):
            for field in value["invariants"].get("missing_required_fields") or []:
                missing[str(field)] += 1
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            missing.update(walk_missing(child, child_prefix))
    elif isinstance(value, list):
        for child in value:
            missing.update(walk_missing(child, prefix))
    return missing


def main() -> int:
    if not CONTRACT_PATH.is_file():
        print("GOLDEN_RISK_CONTRACT_VALIDATION: FAIL")
        print(f"Missing file: {CONTRACT_PATH.relative_to(ROOT)}")
        return 1

    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contracts = payload.get("contracts") or []
    missing = walk_missing(contracts)
    post_outcome_missing = sum(1 for contract in contracts if contract.get("post_match_risk_outcome") is None)

    print("GOLDEN_RISK_CONTRACT_VALIDATION: PASS")
    print(f"Contracts: {len(contracts)}")
    print(f"Missing/null field instances: {sum(missing.values())}")
    print(f"post_match_risk_outcome null contracts: {post_outcome_missing}")
    print("PORTFOLIO_EXTRACTION: BLOCKED")
    print("BACKTEST_READY: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
