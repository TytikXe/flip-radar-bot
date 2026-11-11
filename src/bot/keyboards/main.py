"""Клавиатуры для бота."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для /start: выбор профиля."""
    buttons = [
        [InlineKeyboardButton(text="🛡️ Осторожный", callback_data="profile:cautious")],
        [InlineKeyboardButton(text="⚖️ Баланс", callback_data="profile:balanced")],
        [InlineKeyboardButton(text="🚀 Агрессивный", callback_data="profile:aggressive")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_budget_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора бюджета."""
    buttons = [
        [
            InlineKeyboardButton(text="50 TON", callback_data="budget:50"),
            InlineKeyboardButton(text="100 TON", callback_data="budget:100"),
        ],
        [
            InlineKeyboardButton(text="200 TON", callback_data="budget:200"),
            InlineKeyboardButton(text="500 TON", callback_data="budget:500"),
        ],
        [InlineKeyboardButton(text="Без ограничений", callback_data="budget:0")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_modes_keyboard(settings: dict) -> InlineKeyboardMarkup:
    """Клавиатура управления режимами."""
    mode1_status = "✅" if settings.get("mode1_enabled") else "❌"
    mode2_status = "✅" if settings.get("mode2_enabled") else "❌"
    mode3_status = "✅" if settings.get("mode3_enabled") else "❌"
    
    buttons = [
        [InlineKeyboardButton(
            text=f"{mode1_status} Flip Radar",
            callback_data="toggle:mode1"
        )],
        [InlineKeyboardButton(
            text=f"{mode2_status} Mono Sniper",
            callback_data="toggle:mode2"
        )],
        [InlineKeyboardButton(
            text=f"{mode3_status} Красивые номера",
            callback_data="toggle:mode3"
        )],
        [InlineKeyboardButton(text="⚙️ Настройки режимов", callback_data="settings:modes")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_alert_keyboard(listing_id: int, collection: str) -> InlineKeyboardMarkup:
    """Клавиатура для алерта."""
    buttons = [
        [InlineKeyboardButton(text="Купить", url="https://example.com/listing")],
        [
            InlineKeyboardButton(text="Не интересно", callback_data=f"hide:listing:{listing_id}"),
            InlineKeyboardButton(text="Скрыть коллекцию", callback_data=f"hide:collection:{collection}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_mode1_settings_keyboard() -> InlineKeyboardMarkup:
    """Настройки режима 1."""
    buttons = [
        [InlineKeyboardButton(text="Мин. прибыль %", callback_data="set:mode1:profit_pct")],
        [InlineKeyboardButton(text="Мин. прибыль TON", callback_data="set:mode1:profit_ton")],
        [InlineKeyboardButton(text="Макс. время продажи", callback_data="set:mode1:time")],
        [InlineKeyboardButton(text="← Назад", callback_data="back:modes")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_mode2_settings_keyboard() -> InlineKeyboardMarkup:
    """Настройки режима 2."""
    buttons = [
        [InlineKeyboardButton(text="Отклонение от floor: 3%", callback_data="set:mode2:margin:0.03")],
        [InlineKeyboardButton(text="Отклонение от floor: 5%", callback_data="set:mode2:margin:0.05")],
        [InlineKeyboardButton(text="Отклонение от floor: 10%", callback_data="set:mode2:margin:0.10")],
        [InlineKeyboardButton(text="Отклонение от floor: 15%", callback_data="set:mode2:margin:0.15")],
        [InlineKeyboardButton(text="← Назад", callback_data="back:modes")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_mode3_settings_keyboard() -> InlineKeyboardMarkup:
    """Настройки режима 3."""
    buttons = [
        [InlineKeyboardButton(text="Tier: S", callback_data="set:mode3:tier:S")],
        [InlineKeyboardButton(text="Tier: A", callback_data="set:mode3:tier:A")],
        [InlineKeyboardButton(text="Tier: B", callback_data="set:mode3:tier:B")],
        [InlineKeyboardButton(text="← Назад", callback_data="back:modes")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
