"""Вычисления для режима 2: Mono Sniper."""
from typing import Optional

from src.config import config


def check_mono_eligibility(
    mono_score: float,
    price: float,
    floor: float,
    floor_margin: float
) -> bool:
    """
    Проверка, подходит ли лот для режима Mono Sniper.
    
    Args:
        mono_score: Оценка монохромности (0-1)
        price: Цена лота
        floor: Floor коллекции
        floor_margin: Допустимое отклонение от floor (0.10 = 10%)
    
    Returns:
        True если лот подходит
    """
    mode2_cfg = config.mode2
    threshold = mode2_cfg["mono_threshold"]
    
    # Проверка монохромности
    if mono_score < threshold:
        return False
    
    # Проверка цены относительно floor
    if floor <= 0:
        return False
    
    max_price = floor * (1 + floor_margin)
    if price > max_price:
        return False
    
    return True


def calculate_mono_score_stub(
    model_colors: list[dict],
    backdrop_colors: list[dict]
) -> float:
    """
    Заглушка для расчёта mono_score.
    
    В реальной версии:
    - Извлечь доминантные цвета изображения модели (k-means в OKLCH)
    - Извлечь цвета фона из атрибутов
    - Сравнить hue (±15°) и chroma
    - Вернуть долю пикселей модели в пределах цветового диапазона фона
    
    Args:
        model_colors: [{"l": 0.5, "c": 0.1, "h": 180}, ...]
        backdrop_colors: [{"l": 0.6, "c": 0.12, "h": 175}, ...]
    
    Returns:
        Оценка монохромности (0-1)
    """
    # TODO: Реализовать реальный цветовой анализ
    # 1. Загрузить изображение подарка (первый кадр анимации)
    # 2. k-means кластеризация в OKLCH
    # 3. Сравнение hue в пределах ±15° и low chroma diff
    # 4. Возврат доли совпадающих пикселей
    
    # Для MVP возвращаем предрасчитанное значение
    raise NotImplementedError(
        "Реальный цветовой анализ требует image processing. "
        "Используйте предрасчитанную таблицу attribute_colors."
    )


# TODO: Пример кода для реального анализа (требует PIL, sklearn)
"""
from PIL import Image
from sklearn.cluster import KMeans
import numpy as np

def extract_dominant_colors(image_path: str, n_colors: int = 5) -> list[dict]:
    '''Извлечение доминантных цветов из изображения.'''
    img = Image.open(image_path).convert('RGB')
    img = img.resize((150, 150))  # Уменьшение для скорости
    
    pixels = np.array(img).reshape(-1, 3)
    
    # k-means кластеризация
    kmeans = KMeans(n_clusters=n_colors, random_state=42)
    kmeans.fit(pixels)
    
    colors = kmeans.cluster_centers_.astype(int)
    
    # Конвертация RGB → OKLCH (нужна библиотека colorspacious или custom)
    oklch_colors = [rgb_to_oklch(c) for c in colors]
    
    return oklch_colors


def rgb_to_oklch(rgb: np.ndarray) -> dict:
    '''Конвертация RGB → OKLCH (упрощённая).'''
    # Реальная конвертация сложнее, требует colorspacious
    # Для примера используем placeholder
    return {"l": 0.5, "c": 0.1, "h": 180}


def calculate_mono_score_real(
    model_image_path: str,
    backdrop_colors: list[dict],
    hue_tolerance: float = 15.0
) -> float:
    '''Реальный расчёт mono_score.'''
    model_colors = extract_dominant_colors(model_image_path)
    
    # Подсчёт доли цветов модели в пределах hue фона
    matches = 0
    for mc in model_colors:
        for bc in backdrop_colors:
            hue_diff = abs(mc["h"] - bc["h"])
            # Учёт цикличности hue (0° = 360°)
            if hue_diff > 180:
                hue_diff = 360 - hue_diff
            
            chroma_diff = abs(mc["c"] - bc["c"])
            
            if hue_diff <= hue_tolerance and chroma_diff <= 0.15:
                matches += 1
                break
    
    return matches / len(model_colors)
"""
