
import re

_JAPANESE_CHAR_PATTERN = re.compile(r"[一-龥ぁ-ゖァ-ヶー々〆〤]")
_CLOSE_TO_OPEN = {')': '(', '）': '（'}
_OPENING_PARENS = set(_CLOSE_TO_OPEN.values())
_ALLOWED_SYMBOLS = set('（）()【】「」『』・／-ー_ 　')


def _extract_japanese_variant(text: str) -> str:
    if not text:
        return ''

    stack: list[tuple[str, int]] = []
    candidates: list[str] = []

    for index, char in enumerate(text):
        if char in _OPENING_PARENS:
            stack.append((char, index))
            continue

        if char in _CLOSE_TO_OPEN:
            expected_open = _CLOSE_TO_OPEN[char]
            for stack_index in range(len(stack) - 1, -1, -1):
                open_char, start_index = stack[stack_index]
                if open_char == expected_open:
                    segment = text[start_index : index + 1]
                    del stack[stack_index:]
                    if _JAPANESE_CHAR_PATTERN.search(segment):
                        candidates.append(segment.strip())
                    break
            continue

    if candidates:
        return max(candidates, key=len)

    if _JAPANESE_CHAR_PATTERN.search(text):
        filtered = ''.join(
            char for char in text if _JAPANESE_CHAR_PATTERN.search(char) or char in _ALLOWED_SYMBOLS
        )
        return filtered.strip() or text

    return text


_TABIRAI_CLASS_MAP = {
    '（【SCL】【禁煙車】8人乗りセレナ指定）': 'M2',
    '（【SCL】【禁煙車】コンパクト無指定）': 'C2',
    '（【SCL】【禁煙車】ライズ指定）': 'SUV1',
    '（【禁煙車】8人乗りセレナ指定）': 'M2',
    '（【禁煙車】8人乗りセレナ指定（インバウンド））': 'M2',
    '（【禁煙車】コンパクト無指定）': 'コンパクト無指定',
    '（【禁煙車】コンパクト無指定（インバウンド））': 'コンパクト無指定',
    '（【禁煙車】シエンタ指定）': 'M1',
    '（【禁煙車】シエンタ指定（インバウンド））': 'M1',
    '（【禁煙車】タンク指定）': 'C2T',
    '（【禁煙車】タンク指定（インバウンド））': 'C2T',
    '（【禁煙車】トール指定）': 'C2T',
    '（【禁煙車】トール指定（インバウンド））': 'C2T',
    '（【禁煙車】トール同クラス）': 'C2T',
    '（【禁煙車】トール同クラス（インバウンド））': 'C2T',
    '（【禁煙車】ノート指定）': 'C2',
    '（【禁煙車】ノート指定（インバウンド））': 'C2',
    '（【禁煙車】ヤリスクロス指定）': 'SUV',
    '（【禁煙車】ヤリスクロス指定_NOCコミ）': 'SUV',
    '（【禁煙車】ヤリスクロス指定（インバウンド））': 'SUV',
    '（【禁煙車】ライズ指定）': 'SUV1',
    '（【禁煙車】ライズ同クラス）': 'SUV2',
    '（【禁煙車】ライズ同クラス（インバウンド））': 'SUV2',
    '（【禁煙車】ルーミー指定）': 'C2T',
    '（【禁煙車】ルーミー同クラス）': 'C2T',
    '（【禁煙車】ルーミー同クラス（インバウンド））': 'C2T',
}


def convert_tabirai_class(reservation_class: str) -> str:
    if not reservation_class:
        return ''

    normalized = reservation_class.strip().strip('。').strip()
    japanese_variant = _extract_japanese_variant(normalized)

    for candidate in filter(None, (japanese_variant, normalized)):
        candidate = candidate.strip().strip('。').strip()
        if candidate in _TABIRAI_CLASS_MAP:
            return _TABIRAI_CLASS_MAP[candidate]

    target = (japanese_variant or normalized).replace('　', '').strip()

    if not target:
        return normalized

    if 'セレナ' in target or '8人乗り' in target:
        return 'M2'
    if 'シエンタ' in target:
        return 'M1'
    if 'コンパクト' in target and '無指定' in target:
        return 'コンパクト無指定'
    if any(keyword in target for keyword in ('タンク', 'トール', 'ルーミー')):
        return 'C2T'
    if 'ライズ同クラス' in target:
        return 'SUV2'
    if 'ライズ' in target:
        return 'SUV1'
    if 'ヤリスクロス' in target:
        return 'SUV'

    return normalized


def convert_koushiki_class(reservation_class: str) -> str:
    class_map = {
        '【1台限定】≪公式限定！≫おまかせ格安プラン♪｜車種完全お任せ｜どんな車がくるかは当日のお楽しみに！': '完全無指定',
    }
    return class_map.get(reservation_class, reservation_class)


def convert_input_class(reservation_class: str) -> str:
    base_class = re.sub(r'(SD|HV)$', '', reservation_class)
    class_map = {
        'SUV': 'SUV1',
        'コンパクト無指定': 'C2',
        '完全無指定': 'C0',
    }
    return class_map.get(base_class, base_class)
