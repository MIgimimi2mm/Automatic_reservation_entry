import re
from datetime import datetime


def normalize_date(raw_date, site="jalan"):
    if not raw_date:
        return ""

    text = raw_date.strip()

    try:
        if site == "koushiki":
            return text.split(" ")[0]

        match = re.search(r"(\d{4})[^\d](\d{1,2})[^\d](\d{1,2})", text)
        if match:
            year, month, day = match.groups()
            return f"{year}/{int(month):02d}/{int(day):02d}"

        match = re.search(r"(\d{4})(\d{2})(\d{2})", text)
        if match:
            year, month, day = match.groups()
            return f"{year}/{int(month):02d}/{int(day):02d}"

    except Exception as error:
        print(f"[日付変換エラー] {error}")
        return text

    return text
