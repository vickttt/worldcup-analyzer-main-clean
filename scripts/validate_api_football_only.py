import argparse
import json
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
RUNTIME_PATHS = [
    ROOT / "app.py",
    ROOT / "modules",
    ROOT / "scripts",
    ROOT / ".github",
]
LEGACY_PATTERNS = [
    "The " + "Odds " + "API",
    "Odds " + "API",
    "THE_" + "ODDS",
    "the_" + "odds",
    "api.the-" + "odds-api",
    "/v4/" + "sports",
    "fetch_" + "the" + "_" + "odds",
]


def iter_runtime_files():
    for path in RUNTIME_PATHS:
        if not path.exists():
            continue
        if path.is_file():
            yield path
            continue
        for child in path.rglob("*"):
            if not child.is_file():
                continue
            if child.resolve() == SELF:
                continue
            if child.suffix not in {".py", ".yml", ".yaml", ".md", ".sh", ".command"}:
                continue
            yield child


def scan_legacy_usage():
    findings = []
    for path in iter_runtime_files():
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError as error:
            findings.append({
                "file": str(path.relative_to(ROOT)),
                "line": 0,
                "pattern": "read_error",
                "text": str(error),
            })
            continue
        for line_number, line in enumerate(lines, start=1):
            for pattern in LEGACY_PATTERNS:
                if pattern in line:
                    findings.append({
                        "file": str(path.relative_to(ROOT)),
                        "line": line_number,
                        "pattern": pattern,
                        "text": line.strip()[:180],
                    })
    return findings


def compile_targets():
    targets = [
        "app.py",
        "modules/fixture_id_mapper.py",
        "modules/odds_client.py",
        "modules/team_resolver.py",
        "modules/team_profile_client.py",
        "modules/rating_model.py",
        "modules/value_model.py",
        "modules/worldcup_db.py",
        "modules/user_odds.py",
        "modules/report_generator.py",
        "scripts/refresh_today_odds.py",
        "scripts/refresh_match_prematch_snapshot.py",
        "scripts/build_worldcup_data_center.py",
    ]
    compiled = []
    for target in targets:
        path = ROOT / target
        py_compile.compile(str(path), doraise=True)
        compiled.append(target)
    return compiled


def validate_mapping_and_odds():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from modules.fixture_id_mapper import FixtureIDMapper
    from modules.odds_client import ASIAN_HANDICAP_BET_ID, request_json

    match = {
        "fixture_id": 74,
        "schedule_fixture_id": 74,
        "schedule_source": "WorldCup2026",
        "fixture_source": "WorldCup2026",
        "home_en": "Germany",
        "away_en": "Paraguay",
        "home_cn": "德国",
        "away_cn": "巴拉圭",
        "fixture_kickoff_utc": "2026-06-29T20:30:00+00:00",
    }
    FixtureIDMapper.reset()
    fixture_id = FixtureIDMapper.get(match)
    rows = request_json("/odds", {"fixture": fixture_id, "bet": ASIAN_HANDICAP_BET_ID}) if fixture_id else []
    return {
        "worldcup_match_id": match["schedule_fixture_id"],
        "resolved_fixture_id": fixture_id,
        "expected_fixture_id": 1565176,
        "endpoint": "/odds",
        "bet_id": ASIAN_HANDICAP_BET_ID,
        "response_count": len(rows),
        "odds_provider": "API-Football",
        "mapper_stats": FixtureIDMapper.stats(),
        "passed": fixture_id == 1565176 and len(rows) > 0,
    }


def validate_imports_and_fallbacks():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from modules.team_profile_client import fetch_team_profile

    unresolved = fetch_team_profile("Unknown Test Team")
    return {
        "app_compile": "ok",
        "team_profile_unresolved_status": unresolved.get("status"),
        "team_profile_unresolved_message": unresolved.get("message"),
        "passed": unresolved.get("status") == "unresolved",
    }


def write_report(round_name, payload):
    output_dir = ROOT / "reports" / "api_football_only"
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{round_name}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(path.relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", choices=["1", "2", "3", "all"], default="all")
    args = parser.parse_args()

    payload = {
        "round": args.round,
        "status": "PASS",
        "legacy_findings": [],
        "compiled": [],
        "mapping_validation": None,
        "import_validation": None,
    }

    try:
        if args.round in {"1", "all"}:
            payload["legacy_findings"] = scan_legacy_usage()
            if payload["legacy_findings"]:
                payload["status"] = "FAIL"
        if args.round in {"2", "all"}:
            payload["mapping_validation"] = validate_mapping_and_odds()
            if not payload["mapping_validation"]["passed"]:
                payload["status"] = "FAIL"
        if args.round in {"3", "all"}:
            payload["compiled"] = compile_targets()
            payload["import_validation"] = validate_imports_and_fallbacks()
            if not payload["import_validation"]["passed"]:
                payload["status"] = "FAIL"
    except Exception as error:
        payload["status"] = "FAIL"
        payload["error"] = f"{type(error).__name__}: {error}"

    payload["report_path"] = write_report(f"round_{args.round}", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
