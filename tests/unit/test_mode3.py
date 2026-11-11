"""Unit-тесты для режима 3: Красивые номера."""
import pytest

from src.engine.mode3 import beauty_tier, calculate_beauty_ratio


class TestBeautyTier:
    """Тесты функции beauty_tier."""
    
    # Tier S тесты
    def test_tier_s_low_numbers(self):
        """Tier S: номера 1-10."""
        assert beauty_tier(1, 10000) == ("S", ["топ_1"])
        assert beauty_tier(5, 10000) == ("S", ["топ_5"])
        assert beauty_tier(10, 10000) == ("S", ["топ_10"])
    
    def test_tier_s_power_of_10(self):
        """Tier S: степени десяти."""
        assert beauty_tier(100, 10000) == ("S", ["степень_10"])
        assert beauty_tier(1000, 10000) == ("S", ["степень_10"])
        assert beauty_tier(10000, 100000) == ("S", ["степень_10"])
    
    def test_tier_s_repeating_3plus(self):
        """Tier S: повтор 3+ цифр."""
        assert beauty_tier(111, 10000) == ("S", ["повтор_3"])
        assert beauty_tier(777, 10000) == ("S", ["повтор_3"])
        assert beauty_tier(8888, 10000) == ("S", ["повтор_4"])
    
    # Tier A тесты
    def test_tier_a_max_100(self):
        """Tier A: номера до 100 (без повторов и мемов)."""
        assert beauty_tier(50, 10000) == ("A", ["низкий_50"])
        assert beauty_tier(98, 10000) == ("A", ["низкий_98"])  # 99 это повтор_2
    
    def test_tier_a_repeating_2(self):
        """Tier A: повтор 2 цифр."""
        assert beauty_tier(11, 10000) == ("A", ["повтор_2"])
        assert beauty_tier(33, 10000) == ("A", ["повтор_2"])
        assert beauty_tier(99, 10000) == ("A", ["повтор_2"])  # 99 это повтор_2
    
    def test_tier_a_meme_numbers(self):
        """Tier A: мем-числа."""
        assert beauty_tier(69, 10000) == ("A", ["мем"])
        assert beauty_tier(420, 10000) == ("A", ["мем"])
        assert beauty_tier(1337, 10000) == ("A", ["мем"])
    
    def test_tier_a_palindromes_4plus(self):
        """Tier A: палиндромы от 4 цифр."""
        assert beauty_tier(1221, 10000) == ("A", ["палиндром"])
        assert beauty_tier(12321, 100000) == ("A", ["палиндром"])
    
    def test_tier_a_ladders_4plus(self):
        """Tier A: лесенки от 4 цифр."""
        assert beauty_tier(1234, 10000) == ("A", ["лесенка"])
        assert beauty_tier(4321, 10000) == ("A", ["лесенка"])
        assert beauty_tier(5678, 10000) == ("A", ["лесенка"])
    
    # Tier B тесты
    def test_tier_b_max_1000(self):
        """Tier B: номера до 1000."""
        assert beauty_tier(500, 10000) == ("B", ["круглая_сотня"])
        assert beauty_tier(998, 10000) == ("B", ["средний_998"])  # 999 это повтор_3 (tier S)
    
    def test_tier_b_palindromes_3(self):
        """Tier B: палиндромы из 3 цифр."""
        assert beauty_tier(121, 10000) == ("B", ["палиндром"])
        assert beauty_tier(131, 10000) == ("B", ["палиндром"])
    
    def test_tier_b_ladders_3(self):
        """Tier B: лесенки из 3 цифр."""
        assert beauty_tier(123, 10000) == ("B", ["лесенка"])
        assert beauty_tier(789, 10000) == ("B", ["лесенка"])
        assert beauty_tier(987, 10000) == ("B", ["лесенка"])
    
    def test_tier_b_round_hundreds(self):
        """Tier B: круглые сотни."""
        assert beauty_tier(200, 10000) == ("B", ["круглая_сотня"])
        assert beauty_tier(500, 10000) == ("B", ["круглая_сотня"])
    
    def test_tier_b_repeating_blocks(self):
        """Tier B: повторяющиеся блоки."""
        assert beauty_tier(1212, 10000) == ("B", ["повтор_блок"])
        assert beauty_tier(123123, 1000000) == ("B", ["повтор_блок"])
    
    # Tier C тесты
    def test_tier_c_endings(self):
        """Tier C: окончания 000, 777, 888, 999."""
        assert beauty_tier(5000, 100000) == ("C", ["окончание_000"])  # 5000 > 1000, не попадает в B
        assert beauty_tier(3777, 10000) == ("C", ["окончание_777"])
        assert beauty_tier(4888, 10000) == ("C", ["окончание_888"])
    
    # None тесты
    def test_none_tier(self):
        """Не красивые номера."""
        assert beauty_tier(1357, 10000) == (None, [])
        assert beauty_tier(2468, 10000) == (None, [])


class TestCalculateBeautyRatio:
    """Тесты расчёта ratio и недооценки."""
    
    def test_exact_premium(self):
        """Tier S: цена = 5× floor → точная оценка."""
        tier = "S"
        price = 50.0
        floor = 10.0
        
        ratio, is_undervalued = calculate_beauty_ratio(price, floor, tier)
        
        assert ratio == 5.0
        assert not is_undervalued  # ratio = expected, не недооценка
    
    def test_undervalued(self):
        """Tier A: ratio < 0.5 × expected → недооценка."""
        tier = "A"
        price = 10.0
        floor = 10.0
        
        ratio, is_undervalued = calculate_beauty_ratio(price, floor, tier)
        
        # Expected premium для A = 2.5, threshold = 0.5
        # ratio = 1.0, expected * threshold = 2.5 * 0.5 = 1.25
        # 1.0 < 1.25 → undervalued
        assert ratio == 1.0
        assert is_undervalued
    
    def test_overvalued(self):
        """Tier B: ratio > expected → переоценка."""
        tier = "B"
        price = 20.0
        floor = 10.0
        
        ratio, is_undervalued = calculate_beauty_ratio(price, floor, tier)
        
        # Expected premium для B = 1.3
        # ratio = 2.0 > 1.3 * 0.5 → не undervalued
        assert ratio == 2.0
        assert not is_undervalued
    
    def test_zero_floor(self):
        """Floor = 0 → ratio = 0."""
        ratio, is_undervalued = calculate_beauty_ratio(50.0, 0.0, "S")
        
        assert ratio == 0.0
        assert not is_undervalued
