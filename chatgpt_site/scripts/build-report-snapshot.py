from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = ROOT / "outputs" / "reports"
OUT = ROOT / "chatgpt_site" / "public" / "reports.json"

SENSITIVE_LINE = re.compile(
    r"(api[_\s-]?key|the_odds_api_key|anthropic_api_key|openai_api_key|"
    r"\.streamlit|secrets\.toml|\.env)",
    re.IGNORECASE,
)


def sanitize_report(text: str) -> str:
    lines: list[str] = []
    last_was_hidden = False
    for line in text.splitlines():
        if SENSITIVE_LINE.search(line):
            if not last_was_hidden:
                lines.append("配置提示：远端快照已隐藏本地密钥配置说明。")
            last_was_hidden = True
            continue
        lines.append(line)
        last_was_hidden = False
    return "\n".join(lines)


def parse_report(path: Path) -> dict[str, object] | None:
    match = re.match(r"(.+)_vs_(.+)_(\d{8})_(\d{6})$", path.stem)
    if not match:
        return None

    home = match.group(1).replace("_", " ")
    away = match.group(2).replace("_", " ")
    date = match.group(3)
    time = match.group(4)
    text = sanitize_report(path.read_text(encoding="utf-8", errors="replace"))
    if len(text) > 70000:
        text = text[:70000] + "\n\n[内容过长，已在网页快照中截断。]"

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    heading = next(
        (line.lstrip("#").strip() for line in lines if line.startswith("#")),
        f"{home} vs {away}",
    )
    return {
        "id": path.stem,
        "file": str(path.relative_to(ROOT)),
        "match": f"{home} vs {away}",
        "home": home,
        "away": away,
        "generatedDate": f"{date[:4]}-{date[4:6]}-{date[6:]}",
        "generatedTime": f"{time[:2]}:{time[2:4]}:{time[4:]}",
        "heading": heading,
        "modified": path.stat().st_mtime,
        "content": text,
    }


def main() -> None:
    reports = [
        report
        for path in REPORT_ROOT.glob("*.md")
        if (report := parse_report(path)) is not None
    ]
    reports.sort(key=lambda item: item["modified"], reverse=True)

    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, object]] = []
    for report in reports:
        key = (str(report["home"]).lower(), str(report["away"]).lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(report)
        if len(unique) >= 80:
            break

    payload = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "source": "outputs/reports/*.md latest sanitized snapshot per matchup",
        "reports": unique,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(unique)} reports to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
