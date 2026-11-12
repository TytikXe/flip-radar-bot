"""Минимальная версия бота для быстрого тестирования без БД."""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "9054803178:AAEzqn1M4d2iZFDM6yfqEBAmeEN8Bqfgu5E")

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработка команды /start."""
    await message.answer(
        "🎉 <b>Добро пожаловать в Flip Radar!</b>\n\n"
        "Это тестовая версия бота. Основные функции:\n\n"
        "🔍 <b>Flip Radar</b> — арбитраж между маркетами\n"
        "🎨 <b>Mono Sniper</b> — монохромные подарки\n"
        "💎 <b>Красивые номера</b> — редкие порядковые номера\n\n"
        "Используй команды:\n"
        "/modes — включить/выключить режимы\n"
        "/help — справка",
        parse_mode="HTML"
    )


@dp.message(Command("modes"))
async def cmd_modes(message: types.Message):
    """Обработка команды /modes."""
    await message.answer(
        "⚙️ <b>Режимы поиска</b>\n\n"
        "🔍 <b>Flip Radar</b> — арбитраж (выключен)\n"
        "🎨 <b>Mono Sniper</b> — монохромы (выключен)\n"
        "💎 <b>Красивые номера</b> — tier S/A/B/C (выключен)\n\n"
        "⚠️ Полная версия требует PostgreSQL и Redis.\n"
        "Эта версия работает без БД для тестирования.",
        parse_mode="HTML"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработка команды /help."""
    await message.answer(
        "ℹ️ <b>Справка</b>\n\n"
        "Это минимальная тестовая версия бота Flip Radar.\n\n"
        "<b>Доступные команды:</b>\n"
        "/start — начало работы\n"
        "/modes — управление режимами\n"
        "/help — эта справка\n\n"
        "<b>Что реализовано:</b>\n"
        "✅ Базовые команды\n"
        "✅ Логика расчётов (40 тестов)\n"
        "✅ Архитектура кода\n\n"
        "<b>Что требует настройки:</b>\n"
        "⚠️ PostgreSQL (для хранения сделок)\n"
        "⚠️ Redis (для FSM storage)\n"
        "⚠️ API маркетов (MRKT, Portals, Tonnel)\n"
        "⚠️ MTProto (для внутреннего маркета Telegram)",
        parse_mode="HTML"
    )


@dp.message()
async def echo_handler(message: types.Message):
    """Обработка всех остальных сообщений."""
    await message.answer(
        "Я понимаю только команды:\n"
        "/start — начало\n"
        "/modes — режимы\n"
        "/help — справка"
    )


async def main():
    """Запуск бота."""
    logger.info("🚀 Бот запущен (минимальная версия без БД)")
    logger.info(f"Токен: {BOT_TOKEN[:10]}...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
