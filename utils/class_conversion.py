import re

def convert_tabirai_class(reservation_class: str) -> str:
    class_map = {
        
    "(【SCL】【禁煙車】8人乗りセレナ指定)": "M2",
    "(【SCL】【禁煙車】コンパクト無指定)": "C2",
    "(【SCL】【禁煙車】ライズ指定)": "SUV1",
    "(【禁煙車】8人乗りセレナ指定)": "M2",
    "(【禁煙車】8人乗りセレナ指定（インバウンド）)": "M2",
    "(【禁煙車】コンパクト無指定)": "コンパクト無指定",
    "(【禁煙車】コンパクト無指定（インバウンド）)": "コンパクト無指定",
    "(【禁煙車】シエンタ指定)": "M1",
    "(【禁煙車】シエンタ指定（インバウンド）)": "M1",
    "(【禁煙車】タンク指定)": "C2T",
    "(【禁煙車】タンク指定（インバウンド）)": "C2T",
    "(【禁煙車】トール指定)": "C2T",
    "(【禁煙車】トール指定（インバウンド）)": "C2T",
    "(【禁煙車】トール同クラス)": "C2T",
    "(【禁煙車】トール同クラス（インバウンド）)": "C2T",
    "(【禁煙車】ノート指定)": "C2",
    "(【禁煙車】ノート指定（インバウンド）)": "C2",
    "(【禁煙車】ヤリスクロス指定)": "SUV",
    "(【禁煙車】ヤリスクロス指定_NOCコミ)": "SUV",
    "(【禁煙車】ヤリスクロス指定（インバウンド）)": "SUV",
    "(【禁煙車】ライズ指定)": "SUV1",
    "(【禁煙車】ライズ同クラス（インバウンド）)": "SUV2",
    "(【禁煙車】ルーミー指定)": "C2T",
    "(【禁煙車】ルーミー同クラス)": "C2T"
        
    }
    return class_map.get(reservation_class, reservation_class)

def convert_koushiki_class(reservation_class: str) -> str:
    class_map = {
        "【1台限定】≪公式限定！！≫おまかせ格安プラン♪｜車種完全無指定｜どんな車がくるかは当日のお楽しみに！": "完全無指定",
    }
    return class_map.get(reservation_class, reservation_class)

def convert_input_class(reservation_class: str) -> str:
    base_class = re.sub(r"(SD|HV)$", "", reservation_class)
    class_map = {
        "SUV": "SUV1",
        "コンパクト無指定": "C2",
        "完全無指定": "C0"
    }
    return class_map.get(base_class, base_class)
