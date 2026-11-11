"""Обработчик /modes."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from src.bot.keyboards.main import get_modes_keyboard
from src.database.connection import db
from src.database.models import UserSettings


router = Router()


@router.message(Command("modes"))
async def cmd_modes(message: Message):
    """Управление режимами."""
    user_id = message.from_user.id
    
    async with db.session() as session:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await session.execute(stmt)
        settings = result.scalar_one_or_none()
        
        if not settings:
            await message.answer("Сначала выполни /start")
            return
        
        settings_dict = {
            "mode1_enabled": settings.mode1_enabled,
            "mode2_enabled": settings.mode2_enabled,
            "mode3_enabled": settings.mode3_enabled,
        }
    
    text = (
        "<b>Режимы поиска:</b>\n\n"
        "• Flip Radar: арбитраж между маркетами\n"
        "• Mono Sniper: монохромные подарки по цене floor\n"
        "• Красивые номера: редкие порядковые номера"
    )
    
    await message.answer(text, reply_markup=get_modes_keyboard(settings_dict))
