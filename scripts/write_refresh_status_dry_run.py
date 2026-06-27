#!/usr/bin/env python3
"""Write a local-only refresh status report without calling external APIs."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / ".runtime" / "ui_refresh_status.json"
HISTORY_DIR = ROOT / "data" / "history"
WORLDCUP_INDEX_PATH = ROOT / "data" / "worldcup2026" / "index.json"
STALE_AFTER = timedelta(hours=24)


def repo_relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def iso_mtime(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds")
    except OSError:
        return None


def newest_top_level_pre_snapshot() -> Path | None:
    if not HISTORY_DIR.exists():
        return None
    snapshots = [path for path in HISTORY_DIR.glob("*_pre.json") if path.is_file()]
    if not snapshots:
        return None
    return max(snapshots, key=lambda path: path.stat().st_mtime)


def build_status() -> dict:
    now = datetime.now().astimezone()
    latest_snapshot = newest_top_level_pre_snapshot()
    latest_mtime = iso_mtime(latest_snapshot)
    index_mtime = iso_mtime(WORLDCUP_INDEX_PATH if WORLDCUP_INDEX_PATH.exists() else None)
    warnings = [
        "No external API refresh was performed.",
        "Freshness is based on local file metadata only.",
        "Use a manual approved refresh before relying on time-sensitive market data.",
    ]

    status = "unknown"
    stale_data_risk = "unknown"
    manual_refresh_needed = True
    snapshot_age_hours = None
    if latest_snapshot and latest_mtime:
        snapshot_dt = datetime.fromisoformat(latest_mtime)
        snapshot_age = now - snapshot_dt
        snapshot_age_hours = round(snapshot_age.total_seconds() / 3600, 2)
        if snapshot_age <= STALE_AFTER:
            status = "ok"
            stale_data_risk = "possible"
            manual_refresh_needed = False
        else:
            status = "warning"
            stale_data_risk = "high"
            warnings.append("Latest local snapshot metadata is older than 24 hours.")
    else:
        warnings.append("No top-level local pre-match snapshot was found.")

    return {
        "schema_version": 1,
        "generated_at": now.isoformat(timespec="seconds"),
        "mode": "dry_run",
        "api_called": False,
        "network_calls_allowed": False,
        "api_quota_protected": True,
        "refresh_available": "local-only",
        "data_source": "local_snapshot",
        "last_local_snapshot_mtime": latest_mtime,
        "last_local_snapshot_path": repo_relative(latest_snapshot),
        "worldcup_index_mtime": index_mtime,
        "worldcup_index_path": repo_relative(WORLDCUP_INDEX_PATH) if WORLDCUP_INDEX_PATH.exists() else None,
        "snapshot_age_hours": snapshot_age_hours,
        "stale_after_hours": int(STALE_AFTER.total_seconds() / 3600),
        "stale_data_risk": stale_data_risk,
        "manual_refresh_needed": manual_refresh_needed,
        "status": status,
        "warnings": warnings,
        "checked_paths": [
            "data history top-level pre-match snapshots",
            "worldcup2026 local index metadata",
        ],
        "write_scope": ".runtime/ui_refresh_status.json only",
    }


def main() -> int:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    status = build_status()
    REPORT_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"REFRESH_STATUS_DRY_RUN: wrote {repo_relative(REPORT_PATH)}")
    print(f"MODE: {status['mode']}")
    print(f"API_CALLED: {str(status['api_called']).lower()}")
    print(f"STATUS: {status['status']}")
    print(f"LAST_LOCAL_SNAPSHOT: {status.get('last_local_snapshot_path') or '-'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
