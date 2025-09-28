import re

# 貸出店舗変換マップ
JALAN_SHOP_MAP = {
    "伊丹空港店（大阪空港）": "伊丹",
    "函館空港店": "函館",
    "川西能勢口店≪無料送迎バスあり≫": "伊丹",
}

TABIRAI_SHOP_MAP = {
    "伊丹空港店": "伊丹",
    "函館空港店": "函館",
}

KOUSHIKI_SHOP_MAP = {
    "J-Trip Car Rentals 伊丹空港店": "伊丹",
    "J-Trip Car Rentals 函館空港店": "函館",
}

# 貸出店舗変換関数
def normalize_shop_name(original_name, site="jalan"):
    """
    店舗名を正規化する関数
    文字列内に「函館」や「伊丹」が含まれている場合に適切に変換
    """
    if not original_name:
        return original_name
    
    shop_name = original_name.strip()
    
    # 正規表現で店舗名を判定
    if re.search(r'函館', shop_name):
        return "函館"
    elif re.search(r'伊丹', shop_name):
        return "伊丹"
    elif re.search(r'川西', shop_name):
        return "川西"
    
    # 該当する店舗が見つからない場合は元の名前を返す
    return shop_name
