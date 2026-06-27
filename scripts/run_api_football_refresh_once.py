#!/usr/bin/env python3
"""Run one bounded API-Football refresh and write an auditable runtime status."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
API_FOOTBALL_BASE = "https://v3.football.api-sports.io"
API_FOOTBALL_KEY_NAME = "API_FOOTBALL_KEY"
DEFAULT_FIXTURE_ID = "1489393"
REQUEST_TIMEOUT_SECONDS = 10

RUNTIME_DIR = ROOT / ".runtime" / "api_football_refresh"
UI_REFRESH_STATUS_PATH = ROOT / ".runtime" / "ui_refresh_status.json"
GATE_REPORT_PATH = ROOT / "reports" / "api_football_refresh_gate.md"
REFRESH_REPORT_PATH = ROOT / "reports" / "api_football_one_time_refresh_report.md"
MARKER_PATH = RUNTIME_DIR / "one_time_refresh_marker.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def repo_relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2, sort_keys=True)
        file.write("\n")
    tmp_path.replace(path)


def write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def key_value_present(value: Any) -> bool:
    return bool(str(value or "").strip())


def dotenv_key_value(key_name: str) -> str | None:
    dotenv_path = ROOT / ".env"
    if not dotenv_path.exists():
        return None
    try:
        lines = dotenv_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        name = name.strip().removeprefix("export ").strip()
        if name == key_name:
            cleaned = value.strip().strip("\"'")
            return cleaned if key_value_present(cleaned) else None
    return None


def streamlit_secret_key_value(key_name: str) -> str | None:
    secrets_path = ROOT / ".streamlit" / "secrets.toml"
    if not secrets_path.exists():
        return None
    try:
        with secrets_path.open("rb") as file:
            secrets = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return None
    value = secrets.get(key_name) or secrets.get(key_name.lower())
    return str(value).strip() if key_value_present(value) else None


def load_api_football_key() -> tuple[str | None, str]:
    env_value = os.getenv(API_FOOTBALL_KEY_NAME)
    if key_value_present(env_value):
        return str(env_value).strip(), "process_env"
    secrets_value = streamlit_secret_key_value(API_FOOTBALL_KEY_NAME)
    if secrets_value:
        return secrets_value, "streamlit_secrets"
    dotenv_value = dotenv_key_value(API_FOOTBALL_KEY_NAME)
    if dotenv_value:
        return dotenv_value, "dotenv"
    return None, "missing"


def git_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or "unknown"


def git_ignored(path: Path) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", repo_relative(path) or str(path)],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0


def marker_blocks_refresh() -> bool:
    if not MARKER_PATH.exists():
        return False
    try:
        marker = json.loads(MARKER_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True
    return bool(marker.get("api_call_attempted") or marker.get("api_called"))


def runtime_payload_path(fixture_id: str) -> Path:
    return RUNTIME_DIR / f"fixture_{fixture_id}_status.json"


def api_football_get_fixture(fixture_id: str, api_key: str) -> tuple[int | None, dict[str, Any]]:
    query = urllib.parse.urlencode({"id": fixture_id})
    request = urllib.request.Request(
        f"{API_FOOTBALL_BASE}/fixtures?{query}",
        headers={
            "x-apisports-key": api_key,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            http_status = response.status
            body = response.read()
    except urllib.error.HTTPError as error:
        http_status = error.code
        body = error.read()
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            payload = {"errors": [f"HTTP {http_status}"]}
        raise RuntimeError(api_error_message(payload, f"HTTP {http_status}")) from error

    payload = json.loads(body.decode("utf-8"))
    errors = payload.get("errors")
    if isinstance(errors, dict) and errors:
        raise RuntimeError("; ".join(str(value) for value in errors.values()))
    if isinstance(errors, list) and errors:
        raise RuntimeError("; ".join(str(value) for value in errors))
    return http_status, payload


def api_error_message(payload: dict[str, Any], fallback: str) -> str:
    errors = payload.get("errors")
    if isinstance(errors, dict) and errors:
        return "; ".join(str(value) for value in errors.values())
    if isinstance(errors, list) and errors:
        return "; ".join(str(value) for value in errors)
    return fallback


def gate_report(fixture_id: str, key_present: bool, key_source: str) -> str:
    return f"""# API-Football One-Time Refresh Gate

Generated before any Task 5 real API call.

## Gate Decision

- Branch: `{git_branch()}`.
- API provider: API-Football only.
- Key present: `{str(key_present).lower()}`; value redacted.
- Key source: `{key_source}`.
- The Odds API required: `false`.
- Polymarket refresh: `not used`.
- Real API call performed by this gate report: `false`.

## Planned Endpoint

- Function/script: `scripts/run_api_football_refresh_once.py --execute`.
- Endpoint: `GET https://v3.football.api-sports.io/fixtures`.
- Parameters: `id={fixture_id}`.
- Estimated API calls: `1`.

## Why This Is Bounded

- The request targets one explicit fixture ID.
- The script has no loop and no retry path.
- A runtime marker blocks a second accidental execution unless a future task explicitly overrides it.
- The script does not call The Odds API, Polymarket, WorldCup2026 schedule APIs, or broad all-league/date endpoints.

## Files Written

- Ignored runtime API payload: `.runtime/api_football_refresh/fixture_{fixture_id}_status.json`.
- Ignored runtime one-time marker: `.runtime/api_football_refresh/one_time_refresh_marker.json`.
- Ignored UI status: `.runtime/ui_refresh_status.json`.
- Tracked audit report: `reports/api_football_one_time_refresh_report.md`.

## Protected Areas

- `data/history` will not be read or written by the script.
- Golden JSON will not be read or written by the script.
- Recommendation, ranking, portfolio, strategy, odds settlement, and backtest logic are not touched.
- No product model outputs are mutated.

## Secret Safety

- `API_FOOTBALL_KEY` is loaded from process environment, Streamlit secrets, or repo `.env`.
- The key value is used only in the request header.
- The script prints and records only present/missing state and source label, never the key value.
- `.env` remains ignored and must not be staged.
"""


def status_payload(
    *,
    fixture_id: str,
    key_present: bool,
    key_source: str,
    started_at: str | None,
    finished_at: str,
    status: str,
    api_called: bool,
    api_call_count: int,
    files_written: list[str],
    error: str | None = None,
    http_status: int | None = None,
    response_count: int | None = None,
) -> dict[str, Any]:
    warnings = [
        "This only reflects the last controlled API-Football refresh.",
        "API-Football key value is never displayed.",
        "Odds API is disabled and not required for the current UI-CACHE-API phase.",
        "Polymarket is not part of this refresh.",
        "No data/history or golden JSON files are written.",
    ]
    if error:
        warnings.append("Controlled API-Football refresh failed safely; inspect the audit report.")

    return {
        "schema_version": 1,
        "generated_at": finished_at,
        "mode": "controlled_api_football_one_time_refresh",
        "api_provider_policy": "api_football_only",
        "api_provider": "API-Football",
        "api_endpoint": "/fixtures",
        "api_endpoint_params": {"id": fixture_id},
        "api_called": api_called,
        "api_call_count": api_call_count,
        "real_api_refresh_performed": api_called,
        "network_calls_allowed": api_called,
        "api_quota_protected": True,
        "api_football_key_present": key_present,
        "api_football_key_status": "present" if key_present else "missing",
        "api_football_key_source": key_source,
        "refresh_gate_status": (
            "completed_controlled_api_football_refresh"
            if status == "success"
            else "failed_controlled_api_football_refresh"
            if api_called
            else "blocked_missing_api_football_key"
        ),
        "refresh_started_at": started_at,
        "refresh_finished_at": finished_at,
        "last_api_refresh_at": finished_at if api_called else None,
        "http_status": http_status,
        "response_count": response_count,
        "status": status,
        "error": error,
        "files_written": files_written,
        "odds_api_enabled": False,
        "odds_api_required": False,
        "odds_api_status": "disabled_not_used_current_phase",
        "polymarket_policy": "not_part_of_task_5",
        "worldcup2026_schedule_policy": "not_called_by_task_5",
        "refresh_available": "controlled-one-time",
        "data_source": "api_football_fixture_status",
        "manual_refresh_needed": "only by explicit terminal command",
        "warnings": warnings,
        "write_scope": ".runtime only plus tracked audit reports",
    }


def refresh_report(
    *,
    branch: str,
    fixture_id: str,
    key_present: bool,
    key_source: str,
    started_at: str | None,
    finished_at: str,
    status: str,
    api_called: bool,
    api_call_count: int,
    files_written: list[str],
    http_status: int | None,
    response_count: int | None,
    error: str | None,
) -> str:
    runtime_files = [path for path in files_written if path.startswith(".runtime/")]
    tracked_files = [path for path in files_written if not path.startswith(".runtime/")]
    return f"""# API-Football One-Time Refresh Report

## Summary

- Branch: `{branch}`.
- Script/function used: `scripts/run_api_football_refresh_once.py --execute`.
- API provider: API-Football only.
- `API_FOOTBALL_KEY`: {'present' if key_present else 'missing'}, value redacted.
- API key source: `{key_source}`.
- `THE_ODDS_API_KEY`: not required.
- Endpoint/function called: `GET /fixtures` with `id={fixture_id}`.
- API call count: `{api_call_count}`.
- Refresh run exactly once: `{str(api_called and api_call_count == 1).lower()}`.
- Started at: `{started_at or '-'}`.
- Finished at: `{finished_at}`.
- Status: `{status}`.
- HTTP status: `{http_status if http_status is not None else '-'}`.
- Response item count: `{response_count if response_count is not None else '-'}`.

## Files Written

- Files written: `{', '.join(files_written) if files_written else '-'}`.
- Runtime/ignored files: `{', '.join(runtime_files) if runtime_files else '-'}`.
- Tracked audit files: `{', '.join(tracked_files) if tracked_files else '-'}`.
- `.runtime/` ignored by Git: `{str(git_ignored(ROOT / '.runtime')).lower()}`.

## Safety Results

- `data/history` unchanged by script design.
- Golden JSON unchanged by script design.
- Recommendation, ranking, portfolio, strategy, odds settlement, and backtest logic unchanged.
- The Odds API was not called.
- Polymarket was not called.
- No API key value was printed or written.
- One-time marker path: `.runtime/api_football_refresh/one_time_refresh_marker.json`.

## Failure Details

- Error: `{error or 'none'}`.

## Next Safe Task Recommendation

- Add a read-only UI note or report validator for the controlled refresh artifact before adding any refresh button.
- Do not perform another real API call without a new explicit human checkpoint.
"""


def run_execute(fixture_id: str, allow_repeat: bool) -> int:
    api_key, key_source = load_api_football_key()
    key_present = api_key is not None
    branch = git_branch()
    started_at = utc_now()
    finished_at = started_at
    status = "failed"
    error = None
    http_status = None
    response_count = None
    api_called = False
    api_call_count = 0
    payload_path = runtime_payload_path(fixture_id)
    files_written: list[str] = []

    if not key_present:
        finished_at = utc_now()
        error = "API_FOOTBALL_KEY missing"
    elif marker_blocks_refresh() and not allow_repeat:
        finished_at = utc_now()
        error = "one-time refresh marker already exists; refusing second API call"
        status = "blocked"
    else:
        try:
            api_call_count = 1
            http_status, payload = api_football_get_fixture(fixture_id, api_key)
            api_called = True
            response_items = payload.get("response") or []
            response_count = len(response_items) if isinstance(response_items, list) else None
            status = "success"
            finished_at = utc_now()
            write_json_atomic(
                payload_path,
                {
                    "schema_version": 1,
                    "generated_at": finished_at,
                    "api_provider": "API-Football",
                    "endpoint": "/fixtures",
                    "params": {"id": fixture_id},
                    "http_status": http_status,
                    "response_count": response_count,
                    "response": response_items,
                },
            )
            files_written.append(repo_relative(payload_path) or str(payload_path))
        except Exception as exc:  # noqa: BLE001 - error must be captured in audit report.
            api_called = api_call_count == 1
            finished_at = utc_now()
            error = str(exc)
            status = "failed"

    marker_payload = {
        "schema_version": 1,
        "fixture_id": fixture_id,
        "api_provider": "API-Football",
        "api_call_attempted": api_call_count == 1,
        "api_called": api_called,
        "api_call_count": api_call_count,
        "status": status,
        "started_at": started_at,
        "finished_at": finished_at,
    }
    write_json_atomic(MARKER_PATH, marker_payload)
    files_written.append(repo_relative(MARKER_PATH) or str(MARKER_PATH))

    status = "success" if status == "success" else status
    status_files_written = files_written + [repo_relative(UI_REFRESH_STATUS_PATH) or str(UI_REFRESH_STATUS_PATH)]
    status_doc = status_payload(
        fixture_id=fixture_id,
        key_present=key_present,
        key_source=key_source,
        started_at=started_at,
        finished_at=finished_at,
        status=status,
        api_called=api_called,
        api_call_count=api_call_count,
        files_written=status_files_written,
        error=error,
        http_status=http_status,
        response_count=response_count,
    )
    write_json_atomic(UI_REFRESH_STATUS_PATH, status_doc)
    files_written = status_files_written

    report = refresh_report(
        branch=branch,
        fixture_id=fixture_id,
        key_present=key_present,
        key_source=key_source,
        started_at=started_at,
        finished_at=finished_at,
        status=status,
        api_called=api_called,
        api_call_count=api_call_count,
        files_written=files_written + [repo_relative(REFRESH_REPORT_PATH) or str(REFRESH_REPORT_PATH)],
        http_status=http_status,
        response_count=response_count,
        error=error,
    )
    write_text_atomic(REFRESH_REPORT_PATH, report)

    print("API_FOOTBALL_REFRESH_ONCE: complete")
    print(f"API_PROVIDER: API-Football")
    print(f"API_FOOTBALL_KEY_PRESENT: {str(key_present).lower()}")
    print(f"ENDPOINT: /fixtures")
    print(f"FIXTURE_ID: {fixture_id}")
    print(f"API_CALLED: {str(api_called).lower()}")
    print(f"API_CALL_COUNT: {api_call_count}")
    print(f"STATUS: {status}")
    print(f"REPORT: {repo_relative(REFRESH_REPORT_PATH)}")
    return 0 if status == "success" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-id", default=DEFAULT_FIXTURE_ID)
    parser.add_argument("--write-gate", action="store_true", help="write pre-call gate report only")
    parser.add_argument("--execute", action="store_true", help="perform the one allowed API-Football call")
    parser.add_argument("--allow-repeat", action="store_true", help="manual override for a future approved task")
    args = parser.parse_args()

    if args.write_gate:
        api_key, key_source = load_api_football_key()
        write_text_atomic(
            GATE_REPORT_PATH,
            gate_report(args.fixture_id, api_key is not None, key_source),
        )
        print(f"API_FOOTBALL_REFRESH_GATE: wrote {repo_relative(GATE_REPORT_PATH)}")
        print(f"API_FOOTBALL_KEY_PRESENT: {str(api_key is not None).lower()}")
        print("REAL_API_REFRESH_PERFORMED: false")
        return 0

    if args.execute:
        return run_execute(args.fixture_id, args.allow_repeat)

    print("No API call performed. Use --write-gate for the pre-call report or --execute for the approved one-time refresh.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
