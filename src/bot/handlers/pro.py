"""Обработчик /pro (подписка)."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_invoice_content import InputInvoiceContent

from src.config import config


router = Router()


@router.message(Command("pro"))
async def cmd_pro(message: Message):
    """Информация о Pro подписке."""
    tier_cfg = config.tiers["pro"]
    price_stars = tier_cfg["price_stars"]
    
    text = (
        "<b>🌟 Pro подписка</b>\n\n"
        f"Цена: {price_stars} Stars (≈ {price_stars * 0.20:.1f} USD)\n"
        f"Срок: {tier_cfg['duration_days']} дней\n\n"
        "<b>Преимущества:</b>\n"
        "✅ Flip Radar: без лимитов\n"
        "✅ Mono Sniper: мгновенные алерты (без задержки 5 мин)\n"
        "✅ Красивые номера: мгновенные алерты\n"
        "✅ Настройка всех порогов\n\n"
        "Оплата через Telegram Stars"
    )
    
    await message.answer(text)
    # TODO: реальный инвойс Stars при наличии провайдера


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """Подтверждение платежа."""
    await pre_checkout_query.answer(ok=True)
