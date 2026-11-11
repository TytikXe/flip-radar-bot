"""Обработчик команды /start."""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from src.bot.keyboards.main import get_start_keyboard, get_budget_keyboard
from src.config import config
from src.database.connection import db
from src.database.models import User, UserSettings


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработка команды /start."""
    user_id = message.from_user.id
    
    # Создание/обновление пользователя
    async with db.session() as session:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                tier="free"
            )
            session.add(user)
            
            # Создание настроек по умолчанию
            settings = UserSettings(
                user_id=user_id,
                profile="balanced"
            )
            session.add(settings)
            
            await session.commit()
    
    # Дисклеймер
    disclaimer = (
        "⚠️ <b>Важно:</b> Сигналы не являются финансовой рекомендацией. "
        "Проверяйте лот перед покупкой. Бот не совершает покупки и не хранит ключи.\n\n"
    )
    
    welcome_text = (
        f"{disclaimer}"
        "Привет! Я помогу находить выгодные сделки с NFT-подарками Telegram.\n\n"
        "Выбери профиль риска:"
    )
    
    await message.answer(welcome_text, reply_markup=get_start_keyboard())


@router.callback_query(F.data.startswith("profile:"))
async def process_profile(callback: CallbackQuery):
    """Выбор профиля."""
    await callback.answer()
    
    profile = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    # Сохранение профиля
    async with db.session() as session:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await session.execute(stmt)
        settings = result.scalar_one_or_none()
        
        if settings:
            settings.profile = profile
            
            # Применение пресета
            profile_cfg = config.mode1["profiles"].get(profile, {})
            settings.mode1_min_profit_pct = profile_cfg.get("min_profit_pct", 10.0)
            settings.mode1_min_profit_ton = profile_cfg.get("min_profit_ton", 2.0)
            settings.mode1_max_time_hours = profile_cfg.get("max_time_hours")
            settings.mode1_max_buy_price = profile_cfg.get("max_buy_price_ton")
            
            await session.commit()
    
    text = f"Профиль <b>{profile}</b> применён. Теперь выбери бюджет:"
    await callback.message.edit_text(text, reply_markup=get_budget_keyboard())


@router.callback_query(F.data.startswith("budget:"))
async def process_budget(callback: CallbackQuery):
    """Выбор бюджета."""
    await callback.answer()
    
    budget_str = callback.data.split(":")[1]
    budget = float(budget_str) if budget_str != "0" else None
    user_id = callback.from_user.id
    
    # Сохранение бюджета
    async with db.session() as session:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await session.execute(stmt)
        settings = result.scalar_one_or_none()
        
        if settings:
            settings.budget_ton = budget
            await session.commit()
    
    budget_text = f"{budget} TON" if budget else "без ограничений"
    
    text = (
        f"Бюджет установлен: <b>{budget_text}</b>\n\n"
        "Готово! Используй команды:\n"
        "/modes — включить/выключить режимы\n"
        "/deals — топ-10 актуальных сделок\n"
        "/mydeals — учёт твоих сделок\n"
        "/pro — оформить Pro подписку\n"
        "/help — справка"
    )
    
    await callback.message.edit_text(text)
