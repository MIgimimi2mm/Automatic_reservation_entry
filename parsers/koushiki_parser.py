import re
from utils.date_utils import normalize_date
from utils.shop_map import normalize_shop_name
from utils.class_conversion import  convert_input_class

def parse_koushiki_email(body_text):
    result = {}

    result["予約状況"] = "予約成立"  # キャンセル通知がないと想定
    result["予約元"] = "koushiki"  # 予約元を追加

    

    number_match = re.search(r"貸渡No\s*(\S+)", body_text)
    name_kana_match = re.search(r"お名前\s*(.+?)（(.+?)）", body_text)


    phone_match = re.search(r"TEL\s*([\d\-]+)", body_text)
    datetime_match = re.search(r"ご予約日時\s*(\d{4}/\d{2}/\d{2} \d{2}:\d{2})\s*〜\s*(\d{4}/\d{2}/\d{2} \d{2}:\d{2})", body_text)
    shop_match = re.search(r"ご利用店舗\s*(.+?)\n", body_text)
    class_match = re.search(r"車種\s*(.+)", body_text)
    y_class_match = re.search(r"\｜([A-Z]+\d*[A-Z]*)クラス\｜", body_text)

   

    result["予約番号"] = number_match.group(1).strip() if number_match else ""
    result["予約者氏名"] = name_kana_match.group(1).strip() if name_kana_match else ""
    result["カナ（かな）"] = name_kana_match.group(2).strip() if name_kana_match else ""
    start_raw = datetime_match.group(1) if datetime_match else ""
    end_raw = datetime_match.group(2) if datetime_match else ""
    result["貸出日"] = normalize_date(start_raw, site="koushiki")
    result["返却日"] = normalize_date(end_raw, site="koushiki")
    result["貸出店舗"] = normalize_shop_name(shop_match.group(1), site="koushiki") if shop_match else ""
    result["電話番号"] = phone_match.group(1).strip() if phone_match else ""
    result["クラス"] = class_match.group(1).strip() if class_match else ""

    if class_match and "車種完全無指定" in class_match.group(1):
        result["予約クラス"] = "完全無指定"
    else:
        result["予約クラス"] = y_class_match.group(1) if y_class_match else ""

    result["変更後クラス"] =convert_input_class(result["予約クラス"])

    return result
