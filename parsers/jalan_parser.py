import re
from utils.date_utils import normalize_date
from utils.shop_map import normalize_shop_name
from utils.class_conversion import convert_input_class

def parse_jalan_email(body_text):
    result = {}

    result["予約状況"] = "キャンセル" if "キャンセル通知" in body_text else "予約成立"
    result["予約元"] = "jalan"

    name_match = re.search(r"運転者氏名：\s*(.+?)\s*様", body_text)
    name_kana_match = re.search(r"運転者氏名カナ：\s*(.+?)\s*様", body_text)
    phone_match = re.search(r"運転者電話番号：\s*([\d\-]+)", body_text)
    start_match = re.search(r"貸出日時：\s*([\d/年月日\s:]+)", body_text)
    end_match = re.search(r"返却日時：\s*([\d/年月日\s:]+)", body_text)
    shop_match = re.search(r"貸出営業所：\s*(.+?)\s", body_text)
    class_match = re.search(r"車両クラス：\s*(.+?)\s", body_text)
    number_match = re.search(r"予約番号：\s*(\S+)", body_text)
    y_class_match = re.search(r"\｜([A-Z]+\d*[A-Z]*)クラス\｜", body_text)
    raw_start = start_match.group(1) if start_match else ""
    raw_end = end_match.group(1) if end_match else ""

    result["予約番号"] = number_match.group(1) if number_match else ""
    result["予約者氏名"] = name_match.group(1) if name_match else ""
    result["カナ（かな）"] = name_kana_match.group(1) if name_kana_match else ""
    result["貸出日"] = normalize_date(raw_start, site="jalan")
    result["返却日"] = normalize_date(raw_end, site="jalan")
    result["貸出店舗"] = normalize_shop_name(shop_match.group(1), site="jalan") if shop_match else ""
    result["電話番号"] = phone_match.group(1) if phone_match else ""
    result["クラス"] = class_match.group(1) if class_match else ""
    result["予約クラス"] = y_class_match.group(1) if y_class_match else ""
    result["変更後クラス"] =convert_input_class(result["予約クラス"])

    return result