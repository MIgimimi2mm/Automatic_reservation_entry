import re
from datetime import datetime

def normalize_date(raw_date, site="jalan"):
    if not raw_date:
        return ""

    try:
        if site == "jalan" or site == "tabirai":
            match = re.search(r"(\d{4})年(\d{2})月(\d{2})日", raw_date)
            if match:
                year, month, day = match.groups()
                return f"{year}/{month}/{day}"

        elif site == "koushiki":
            return raw_date.strip().split(" ")[0]

    except Exception as e:
        print(f"[日付変換エラー] {e}")
        return raw_date

    return raw_date
