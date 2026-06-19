import json
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "data" / "performance_logs"
LOG_PATH = LOG_DIR / "app_performance.jsonl"


def write_perf_event(page, module, elapsed_ms, meta=None):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "page": page,
        "module": module,
        "elapsed_ms": round(elapsed_ms, 2),
        "meta": meta or {},
    }
    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


@contextmanager
def perf_timer(page, module, meta=None):
    started = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000
        write_perf_event(page, module, elapsed_ms, meta)


def read_recent_events(limit=200):
    if not LOG_PATH.exists():
        return []
    lines = LOG_PATH.read_text(encoding="utf-8").splitlines()[-limit:]
    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events
