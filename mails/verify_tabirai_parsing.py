
from __future__ import annotations

import json
from pathlib import Path
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from parsers.tabirai_parser import parse_tabirai_email
from parsers.jalan_parser import parse_jalan_email


REQUIRED_KEYS = [
    "予約番号",
    "予約者氏名",
    "貸出日",
    "返却日",
    "貸出店舗",
    "電話番号",
]


def _read_mail(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _summarize(result: dict[str, str]) -> dict[str, str]:
    summary = {key: result.get(key, "") for key in REQUIRED_KEYS}
    summary["予約状況"] = result.get("予約状況", "")
    summary["予約元"] = result.get("予約元", "")
    summary["クラス"] = result.get("クラス", "")
    summary["予約クラス"] = result.get("予約クラス", "")
    summary["変更後クラス"] = result.get("変更後クラス", "")
    return summary


def verify_mail(path: Path) -> dict[str, str]:
    body = _read_mail(path)
    if not body.strip():
        return {"error": "mail body is empty"}

    result = parse_jalan_email(body)
    missing = [key for key in REQUIRED_KEYS if not result.get(key)]

    payload = _summarize(result)
    if missing:
        payload["missing"] = ", ".join(missing)
    return payload


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    files = sorted(base_dir.glob("*.txt"))

    if not files:
        print("no mail samples found")
        return

    for path in files:
        print(f"=== {path.name} ===")
        report = verify_mail(path)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        print()


if __name__ == "__main__":
    main()
