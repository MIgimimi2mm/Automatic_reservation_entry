import re
from utils.date_utils import normalize_date
from utils.shop_map import normalize_shop_name
from utils.class_conversion import convert_tabirai_class, convert_input_class


def parse_tabirai_email(body_text):
    result = {}

    result["予約状況"] = "キャンセル" if "キャンセルの通知" in body_text else "予約成立"
    result["予約元"] = "tabirai"

    # 正規表現でマッチング（安全な処理）
    name_match = re.search(r"お名前：(.+)", body_text)
    phone_match = re.search(r"電話番号：([\d\-]+)", body_text)
    start_match = re.search(r"貸出日時：(.+?)\s", body_text)
    end_match = re.search(r"返却日時：(.+?)\s", body_text)
    shop_match = re.search(r"出発店舗：(.+)", body_text)
    class_match = re.search(r"車種：(.+)", body_text)
    kana_match = re.search(r"フリガナ：(.+)", body_text)
    number_match = re.search(r"予約番号\s*：\s*(\d+)", body_text)
    
    # 安全に値を取得
    raw_start = start_match.group(1) if start_match else ""
    raw_end = end_match.group(1) if end_match else ""

    result["予約番号"] = number_match.group(1).strip() if number_match else ""
    result["予約者氏名"] = name_match.group(1).strip() if name_match else ""
    result["カナ（かな）"] = kana_match.group(1).strip() if kana_match else ""
    result["貸出日"] = normalize_date(raw_start, site="tabirai")
    result["返却日"] = normalize_date(raw_end, site="tabirai")
    result["貸出店舗"] = normalize_shop_name(shop_match.group(1), site="tabirai") if shop_match else ""
    result["電話番号"] = phone_match.group(1).strip() if phone_match else ""
    result["クラス"] = class_match.group(1).strip() if class_match else ""
    
    # クラス変換を安全に行う
    try:
        result["予約クラス"] = convert_tabirai_class(result["クラス"])
        result["変更後クラス"] = convert_input_class(result["予約クラス"])
    except Exception as e:
        print(f"クラス変換エラー: {e}")
        result["予約クラス"] = result["クラス"]
        result["変更後クラス"] = result["クラス"]

    return result
