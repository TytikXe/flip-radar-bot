"""Модуль отправки алертов (notifier)."""
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
from src.database.models import AlertSent, User, UserSettings


class Deduplication:
    """Дедупликация алертов."""
    
    @staticmethod
    async def should_send_alert(
        session: AsyncSession,
        user_id: int,
        listing_id: int,
        mode: str,
        current_price: float
    ) -> bool:
        """
        Проверка, можно ли отправить алерт.
        
        Returns:
            True если можно отправить
        """
        # Поиск предыдущего алерта
        stmt = select(AlertSent).where(
            AlertSent.user_id == user_id,
            AlertSent.listing_id == listing_id,
            AlertSent.mode == mode
        ).order_by(AlertSent.sent_at.desc()).limit(1)
        
        result = await session.execute(stmt)
        prev_alert = result.scalar_one_or_none()
        
        if prev_alert is None:
            # Первый раз
            return True
        
        # Проверка падения цены
        min_drop_pct = config.get("deduplication.min_price_drop_pct", 5)
        price_drop_pct = ((prev_alert.price_at_send - current_price) / prev_alert.price_at_send) * 100
        
        if price_drop_pct >= min_drop_pct:
            # Цена упала достаточно
            return True
        
        return False
    
    @staticmethod
    async def mark_sent(
        session: AsyncSession,
        user_id: int,
        listing_id: int,
        mode: str,
        price: float
    ):
        """Отметить алерт как отправленный."""
        alert = AlertSent(
            user_id=user_id,
            listing_id=listing_id,
            mode=mode,
            sent_at=datetime.utcnow(),
            price_at_send=price
        )
        session.add(alert)
        await session.commit()


class RateLimiter:
    """Контроль лимитов алертов."""
    
    @staticmethod
    async def check_limit(
        session: AsyncSession,
        user_id: int,
        mode: str
    ) -> bool:
        """
        Проверка лимита алертов в час.
        
        Returns:
            True если лимит не превышен
        """
        # Получение настроек пользователя
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await session.execute(stmt)
        settings = result.scalar_one_or_none()
        
        if settings and settings.silence_mode:
            return False
        
        # Получение тарифа
        user_stmt = select(User).where(User.id == user_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            return False
        
        tier_config = config.tiers.get(user.tier, {})
        
        # Проверка дневного лимита для режима 1
        if mode == "mode1":
            daily_limit = tier_config.get("mode1_alerts_per_day")
            if daily_limit is not None:
                # Подсчёт алертов за сегодня
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                
                count_stmt = select(AlertSent).where(
                    AlertSent.user_id == user_id,
                    AlertSent.mode == mode,
                    AlertSent.sent_at >= today_start
                )
                count_result = await session.execute(count_stmt)
                count = len(count_result.scalars().all())
                
                if count >= daily_limit:
                    return False
        
        # Проверка почасового лимита
        hourly_limit = settings.alerts_per_hour if settings else None
        if hourly_limit is None:
            hourly_limit = tier_config.get("alerts_per_hour")
        
        if hourly_limit is not None:
            hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            count_stmt = select(AlertSent).where(
                AlertSent.user_id == user_id,
                AlertSent.sent_at >= hour_ago
            )
            count_result = await session.execute(count_stmt)
            count = len(count_result.scalars().all())
            
            if count >= hourly_limit:
                return False
        
        return True


class AlertFormatter:
    """Форматирование алертов."""
    
    @staticmethod
    def format_mode1_alert(
        gift_name: str,
        gift_number: int,
        model: str,
        backdrop: str,
        buy_price: float,
        buy_market: str,
        sell_price: float,
        sell_market: str,
        net_profit: float,
        profit_pct: float,
        time_to_sell: dict,
        score: int,
        confidence: str,
        url: str
    ) -> str:
        """Форматирование алерта режима 1."""
        # Эмодзи по score
        emoji = "🔥" if score >= 80 else "⚡" if score >= 60 else "💡"
        
        # Диапазон прибыли (±10%)
        net_min = net_profit * 0.9
        net_max = net_profit * 1.1
        
        # Время продажи
        if time_to_sell["has_enough_data"]:
            median_h = int(time_to_sell["median_hours"])
            p80_h = int(time_to_sell["p75_hours"])
            sales_count = time_to_sell["count"]
            time_str = f"~{median_h} ч (80% за {p80_h} ч), продаж/7д: {sales_count}"
        else:
            time_str = "мало данных"
        
        # Доверие
        conf_emoji = {"high": "✅", "mid": "⚠️", "low": "❓"}
        conf_str = conf_emoji.get(confidence, "❓")
        
        text = f"""
{emoji} {gift_name} #{gift_number}
Модель / Фон: {model} / {backdrop}

Купить: {buy_price:.1f} TON ({buy_market})
Продать: ~{sell_price:.1f} TON ({sell_market})
Чистая прибыль: +{net_min:.1f}…{net_max:.1f} TON (≈{profit_pct:.0f}%)

Обычно уходит: {time_str}
Оценка: {score}/100 · доверие: {conf_str}
""".strip()
        
        return text
    
    @staticmethod
    def format_mode2_alert(
        gift_name: str,
        gift_number: int,
        price: float,
        floor: float,
        deviation_pct: float,
        mono_score: float,
        model_color: str,
        backdrop_color: str,
        url: str
    ) -> str:
        """Форматирование алерта режима 2."""
        text = f"""
🎨 {gift_name} #{gift_number}

Цена: {price:.1f} TON
Floor: {floor:.1f} TON (отклонение: {deviation_pct:+.0f}%)

Монохромность: {mono_score:.2f}
Цвета: {model_color} / {backdrop_color}
""".strip()
        
        return text
    
    @staticmethod
    def format_mode3_alert(
        gift_name: str,
        gift_number: int,
        tier: str,
        tags: list[str],
        price: float,
        floor: float,
        ratio: float,
        is_undervalued: bool,
        url: str
    ) -> str:
        """Форматирование алерта режима 3."""
        tier_emoji = {"S": "💎", "A": "⭐", "B": "✨", "C": "🌟"}
        emoji = tier_emoji.get(tier, "")
        
        tags_str = ", ".join(tags)
        undervalue_mark = "🟢 похоже на недооценку" if is_undervalued else ""
        
        text = f"""
{emoji} #{gift_number} · tier: {tier}
Теги: {tags_str}

Цена: {price:.1f} TON
Floor: {floor:.1f} TON
Ratio: {ratio:.1f}× {undervalue_mark}
""".strip()
        
        return text
