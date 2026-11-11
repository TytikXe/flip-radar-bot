"""Вычисления для режима 3: Красивые номера."""
import re
from typing import Optional

from src.config import config


def beauty_tier(number: int, supply: int) -> tuple[Optional[str], list[str]]:
    """
    Определение tier красивого номера.
    
    Args:
        number: Порядковый номер подарка
        supply: Общий supply коллекции
    
    Returns:
        (tier, tags)
        tier: 'S' / 'A' / 'B' / 'C' / None
        tags: ['палиндром', 'повтор_3', 'лесенка', ...]
    """
    mode3_cfg = config.mode3
    num_str = str(number)
    tags = []
    
    # Tier S: самые редкие
    tier_s = mode3_cfg["tier_s"]
    
    if number in tier_s["low_numbers"]:
        tags.append(f"топ_{number}")
        return ("S", tags)
    
    if number in tier_s["power_of_10"]:
        tags.append("степень_10")
        return ("S", tags)
    
    if tier_s["repeating_3plus"] and _is_repeating(num_str, min_count=3):
        tags.append(f"повтор_{len(num_str)}")
        return ("S", tags)
    
    # Tier A: редкие
    tier_a = mode3_cfg["tier_a"]
    
    # Мем-числа (приоритет выше, чем "низкий номер")
    if number in tier_a["meme_numbers"]:
        tags.append("мем")
        return ("A", tags)
    
    # Палиндромы от 4 цифр
    if len(num_str) >= tier_a["palindromes_min_digits"] and _is_palindrome(num_str):
        tags.append("палиндром")
        return ("A", tags)
    
    # Лесенки от 4 цифр
    if len(num_str) >= tier_a["ladders_min_digits"] and _is_ladder(num_str):
        tags.append("лесенка")
        return ("A", tags)
    
    # Повтор 2 цифр (11, 22, 33...)
    if tier_a["repeating_2"] and _is_repeating(num_str, min_count=2):
        tags.append("повтор_2")
        return ("A", tags)
    
    # Номера до 100 (после проверки на мемы и повторы)
    if number <= tier_a["max_number"]:
        tags.append(f"низкий_{number}")
        return ("A", tags)
    
    # Tier B: интересные
    tier_b = mode3_cfg["tier_b"]
    
    # Палиндромы из 3 цифр
    if len(num_str) >= tier_b["palindromes_min_digits"] and _is_palindrome(num_str):
        tags.append("палиндром")
        return ("B", tags)
    
    # Лесенки из 3 цифр
    if len(num_str) >= tier_b["ladders_min_digits"] and _is_ladder(num_str):
        tags.append("лесенка")
        return ("B", tags)
    
    # Повторяющиеся блоки (1212, 123123)
    if tier_b["repeating_blocks"] and _is_repeating_block(num_str):
        tags.append("повтор_блок")
        return ("B", tags)
    
    # Круглые сотни (200, 500, но не 100, 1000 — они в S, только до 1000)
    if tier_b["round_hundreds"] and number % 100 == 0 and number > 0 and number <= tier_b["max_number"]:
        if number not in tier_s["power_of_10"]:
            tags.append("круглая_сотня")
            return ("B", tags)
    
    # Номера до 1000 (после всех специальных проверок)
    if number <= tier_b["max_number"]:
        tags.append(f"средний_{number}")
        return ("B", tags)
    
    # Tier C: приятные окончания
    tier_c = mode3_cfg["tier_c"]
    
    for ending in tier_c["endings"]:
        if num_str.endswith(ending):
            tags.append(f"окончание_{ending}")
            return ("C", tags)
    
    # Не красивый номер
    return (None, [])


def _is_repeating(num_str: str, min_count: int = 2) -> bool:
    """Проверка на повторяющиеся цифры (111, 77, 8888)."""
    if len(num_str) < min_count:
        return False
    
    # Все символы одинаковые
    return len(set(num_str)) == 1


def _is_palindrome(num_str: str) -> bool:
    """Проверка на палиндром (121, 1221, 12321)."""
    return num_str == num_str[::-1]


def _is_ladder(num_str: str) -> bool:
    """Проверка на лесенку (1234, 4321, 567, 987)."""
    if len(num_str) < 3:
        return False
    
    digits = [int(d) for d in num_str]
    
    # Возрастающая лесенка
    is_ascending = all(
        digits[i] + 1 == digits[i + 1]
        for i in range(len(digits) - 1)
    )
    
    # Убывающая лесенка
    is_descending = all(
        digits[i] - 1 == digits[i + 1]
        for i in range(len(digits) - 1)
    )
    
    return is_ascending or is_descending


def _is_repeating_block(num_str: str) -> bool:
    """Проверка на повторяющийся блок (1212, 123123, 5656)."""
    length = len(num_str)
    
    # Проверяем все возможные длины блока (от 1 до половины числа)
    for block_len in range(1, length // 2 + 1):
        if length % block_len == 0:
            block = num_str[:block_len]
            repetitions = length // block_len
            
            if block * repetitions == num_str and repetitions >= 2:
                return True
    
    return False


def calculate_beauty_ratio(
    price: float,
    floor: float,
    tier: str
) -> tuple[float, bool]:
    """
    Расчёт ratio и определение недооценки.
    
    Args:
        price: Цена лота
        floor: Floor модели+фона
        tier: Tier номера
    
    Returns:
        (ratio, is_undervalued)
    """
    if floor <= 0:
        return (0.0, False)
    
    ratio = price / floor
    
    expected_premiums = config.mode3["expected_premiums"]
    expected = expected_premiums.get(tier, 1.0)
    
    threshold = config.mode3["undervalue_threshold"]
    is_undervalued = ratio < (expected * threshold)
    
    return (ratio, is_undervalued)
