"""Обработчики /deals и /mydeals."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


@router.message(Command("deals"))
async def cmd_deals(message: Message):
    """Топ-10 актуальных сделок."""
    # TODO: реальная выборка из БД по score
    text = (
        "<b>Топ-10 актуальных сделок:</b>\n\n"
        "1. Jolly Chimp #4821 — 82/100\n"
        "2. Green Star #3 — 95/100 (tier S)\n"
        "3. Red Ruby #777 — 88/100 (tier S)\n"
        "...\n\n"
        "Полный список в алертах по мере появления."
    )
    await message.answer(text)


@router.message(Command("mydeals"))
async def cmd_mydeals(message: Message):
    """Учёт сделок пользователя."""
    # TODO: интеграция с UserDeal
    text = (
        "<b>Твои сделки:</b>\n\n"
        "Купил: Jolly Chimp #123 за 40 TON\n"
        "Продал: — (ждёт продажи)\n\n"
        "Общая прибыль: 0 TON"
    )
    await message.answer(text)
