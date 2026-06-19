import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.match_parser import parse_match
from modules.schedule_client import fetch_world_cup_schedule, fixture_local_datetime
from modules.worldcup_db import data_completeness, load_match_database, match_dir


LOCAL_TZ = ZoneInfo("Asia/Shanghai")
OUT = ROOT / "data" / "worldcup2026" / "index.json"


def fixture_match_text(fixture):
    home = ((fixture.get("home_team") or {}).get("name") or "").strip()
    away = ((fixture.get("away_team") or {}).get("name") or "").strip()
    return f"{home} vs {away}"


def status_text(fixture):
    return fixture.get("status_text") or fixture.get("status") or "-"


def main():
    schedule = fetch_world_cup_schedule(force_refresh=False)
    fixtures = schedule.get("fixtures") or []
    today = datetime.now(LOCAL_TZ).date()
    rows = []

    for fixture in fixtures:
        local_time = fixture_local_datetime(fixture)
        if local_time and local_time.date() > today:
            continue
        match_text = fixture_match_text(fixture)
        if " vs " not in match_text:
            continue
        match = parse_match(match_text)
        db = load_match_database(match, fixture)
        completeness = (db or {}).get("completeness") or {"score": 0, "checks": []}
        base = match_dir(match, fixture)
        rows.append({
            "fixture_id": fixture.get("fixture_id"),
            "date": local_time.strftime("%Y-%m-%d") if local_time else None,
            "match": match_text,
            "home": match.get("home_en"),
            "away": match.get("away_en"),
            "status": fixture.get("status"),
            "status_text": status_text(fixture),
            "database_dir": str(base.relative_to(ROOT)),
            "snapshot_exists": base.exists(),
            "data_completeness": completeness.get("score"),
            "checks": completeness.get("checks"),
        })

    payload = {
        "created_at": datetime.now(LOCAL_TZ).isoformat(),
        "source": schedule.get("source"),
        "schedule_updated_at": schedule.get("updated_at"),
        "matches": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Index: {OUT}")
    print(f"Matches indexed: {len(rows)}")


if __name__ == "__main__":
    main()
