import re
from typing import Iterable

from utils.date_utils import normalize_date
from utils.shop_map import normalize_shop_name
from utils.class_conversion import convert_tabirai_class, convert_input_class


_COLON_PATTERN = r"[:\uff1a]"


def _first_match(body_text: str, patterns: Iterable[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, body_text, re.MULTILINE)
        if match:
            return match.group(1).strip()
    return ""


def _clean_phone(raw_phone: str) -> str:
    if not raw_phone:
        return ""
    return re.sub(r"\s+", "", raw_phone)


def _extract_shop_name(raw_value: str) -> str:
    if not raw_value:
        return ""

    candidate = raw_value.strip()
    paren = re.search(r"（([^（）]+)）", candidate)
    if paren:
        inner = paren.group(1).strip()
        if re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", inner):
            candidate = inner

    candidate = re.sub(r"\s+", " ", candidate)
    return normalize_shop_name(candidate, site="tabirai")


_RESERVATION_NUMBER_PATTERNS = [
    rf"(?:予約番号|ご予約番号|預約番号|預約編號|預約號碼|予約No|예약번호)[^:\uff1a\n]*{_COLON_PATTERN}\s*(\S+)",
]

_NAME_PATTERNS = [
    rf"(?:お名前|ご予約者名|お客様名|姓名|姓名（お名前）|姓名（顧客名）|이름)[^:\uff1a\n]*{_COLON_PATTERN}\s*(.+)",
]

_KANA_PATTERNS = [
    rf"(?:フリガナ|カナ|姓名（英文）|姓名（フリガナ）|英文名|英文姓名|英文姓名（フリガナ）|姓名（英語表記）|姓名（英語）|姓名（拼音）|이름（英語표記）)[^:\uff1a\n]*{_COLON_PATTERN}\s*(.+)",
]

_PHONE_PATTERNS = [
    rf"(?:電話番号|電話號碼|電話号码|電話番号（ご連絡先）|聯絡電話|聯絡電話號碼|電話號碼（電話番号）|전화번호)[^:\uff1a\n]*{_COLON_PATTERN}\s*([+\d][\d\-\s]*)",
]

_START_DATETIME_PATTERNS = [
    rf"(?:貸出日時|貸渡日時|出発日時|出発日|ご利用日時|利用日|取車日時|取車日|取車日期|取车日|取车日期|取車時間|출発日時|出發日期|출発日|출발日時|출발日|출발日시|출발일시)[^:\uff1a\n]*{_COLON_PATTERN}\s*(.+)",
]

_END_DATETIME_PATTERNS = [
    rf"(?:返却日時|返却日|返車日時|返車日|返却予定日時|還車日時|還車日|還車日期|还车日|还车日期|出庫終了日時|取車終了日時|반납日時|반납日|반납일시)[^:\uff1a\n]*{_COLON_PATTERN}\s*(.+)",
]

_START_SHOP_PATTERNS = [
    rf"(?:出発店舗|貸出店舗|貸出店|貸出営業所|出発営業所|出発店|出発店舖|取車店舗|取車店舖|取車店鋪|取車門市|取车门市|取车门店|出發門市|出發門店|出発/貸出店舗|出発/貸出店|출발점포|출発店舗|출発店)[^:\uff1a\n]*{_COLON_PATTERN}\s*(.+)",
]

_END_SHOP_PATTERNS = [
    rf"(?:返却店舗|返却店|返却営業所|返却予定店舗|返却予定店|返却店舖|返却店鋪|還車店舗|還車店舖|還車店鋪|還車門市|還車門店|还车门市|还车门店|出庫店舗|返却/還車店舗|返却/還車店|출발店舗（返却）|반납점포|반납店舗|반납営業所)[^:\uff1a\n]*{_COLON_PATTERN}\s*(.+)",
]

_CLASS_PATTERNS = [
    rf"(?:車種|車両クラス|車型|車種タイプ|クラス名|等級|車種タイプ（クラス名）|차종|차종 타입|차량 등급)[^:\uff1a\n]*{_COLON_PATTERN}\s*(.+)",
]

_DATETIME_FALLBACK_PATTERN = re.compile(r"\d{4}[^\d]\d{1,2}[^\d]\d{1,2}[^\n]{0,16}\d{2}:\d{2}")


def parse_tabirai_email(body_text: str) -> dict[str, str]:
    result: dict[str, str] = {}

    cancel_keywords = ["キャンセル", "取消", "取消し", "取消通知", "취소"]
    result["予約状況"] = "キャンセル" if any(keyword in body_text for keyword in cancel_keywords) else "予約成立"
    result["予約元"] = "tabirai"

    result["予約番号"] = _first_match(body_text, _RESERVATION_NUMBER_PATTERNS)
    result["予約者氏名"] = _first_match(body_text, _NAME_PATTERNS)
    result["カナ（かな）"] = _first_match(body_text, _KANA_PATTERNS)

    raw_start = _first_match(body_text, _START_DATETIME_PATTERNS)
    raw_end = _first_match(body_text, _END_DATETIME_PATTERNS)

    if not raw_start or not raw_end:
        candidates = _DATETIME_FALLBACK_PATTERN.findall(body_text)
        if not raw_start and len(candidates) >= 1:
            raw_start = candidates[0].strip()
        if not raw_end and len(candidates) >= 2:
            raw_end = candidates[1].strip()

    result["貸出日"] = normalize_date(raw_start, site="tabirai")
    result["返却日"] = normalize_date(raw_end, site="tabirai")

    result["貸出店舗"] = _extract_shop_name(_first_match(body_text, _START_SHOP_PATTERNS))
    result["電話番号"] = _clean_phone(_first_match(body_text, _PHONE_PATTERNS))
    result["クラス"] = _first_match(body_text, _CLASS_PATTERNS)

    try:
        reservation_class = convert_tabirai_class(result["クラス"])
        result["予約クラス"] = reservation_class
        result["変更後クラス"] = convert_input_class(reservation_class)
    except Exception as error:  # noqa: BLE001
        print(f"クラス変換エラー: {error}")
        result["予約クラス"] = result["クラス"]
        result["変更後クラス"] = result["クラス"]

    return result
