"""Обработчики callback_query (кнопки)."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.bot.keyboards.main import get_modes_keyboard
from src.database.connection import db
from src.database.models import UserSettings


router = Router()


@router.callback_query(F.data.startswith("toggle:"))
async def toggle_mode(callback: CallbackQuery):
    """Переключение режима."""
    await callback.answer()
    
    mode = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    async with db.session() as session:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await session.execute(stmt)
        settings = result.scalar_one_or_none()
        
        if not settings:
            await callback.answer("Ошибка: настройки не найдены", show_alert=True)
            return
        
        # Переключение
        if mode == "mode1":
            settings.mode1_enabled = not settings.mode1_enabled
        elif mode == "mode2":
            settings.mode2_enabled = not settings.mode2_enabled
        elif mode == "mode3":
            settings.mode3_enabled = not settings.mode3_enabled
        
        await session.commit()
        
        settings_dict = {
            "mode1_enabled": settings.mode1_enabled,
            "mode2_enabled": settings.mode2_enabled,
            "mode3_enabled": settings.mode3_enabled,
        }
    
    await callback.message.edit_reply_markup(reply_markup=get_modes_keyboard(settings_dict))


@router.callback_query(F.data.startswith("hide:listing:"))
async def hide_listing(callback: CallbackQuery):
    """Скрыть конкретный лот."""
    await callback.answer("Лот скрыт")
    await callback.message.delete()


@router.callback_query(F.data.startswith("hide:collection:"))
async def hide_collection(callback: CallbackQuery):
    """Скрыть коллекцию."""
    collection = callback.data.split(":")[2]
    user_id = callback.from_user.id
    
    async with db.session() as session:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await session.execute(stmt)
        settings = result.scalar_one_or_none()
        
        if settings:
            excluded = settings.excluded_collections or []
            if collection not in excluded:
                excluded.append(collection)
                settings.excluded_collections = excluded
                await session.commit()
    
    await callback.answer(f"Коллекция {collection} скрыта")
    await callback.message.delete()
