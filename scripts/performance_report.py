import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "data" / "performance_logs" / "app_performance.jsonl"


def load_events():
    if not LOG_PATH.exists():
        return []
    events = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def main():
    events = load_events()
    if not events:
        print("No performance logs found.")
        return

    latest = events[-300:]
    by_page = defaultdict(list)
    for event in latest:
        by_page[event.get("page")].append(event)

    print(f"Log: {LOG_PATH}")
    print(f"Events analyzed: {len(latest)}")
    for page in ["home", "detail", "post_match"]:
        rows = by_page.get(page) or []
        if not rows:
            continue
        total_rows = [row for row in rows if row.get("module") in {"total", "pre_tab_total"}]
        if total_rows:
            print(f"{page} latest total: {total_rows[-1]['elapsed_ms']}ms ({total_rows[-1]['module']})")

    print("\nSlowest modules Top10:")
    for row in sorted(latest, key=lambda item: item.get("elapsed_ms", 0), reverse=True)[:10]:
        print(f"{row.get('page')} / {row.get('module')}: {row.get('elapsed_ms')}ms {row.get('meta') or ''}")


if __name__ == "__main__":
    main()
