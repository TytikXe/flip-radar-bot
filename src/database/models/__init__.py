"""Модели базы данных."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON, BigInteger, Boolean, DateTime, Float, ForeignKey,
    Index, Integer, String, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


__all__ = [
    "Base",
    "Collection",
    "AttributeColor",
    "Listing",
    "ListingEvent",
    "Sale",
    "Floor",
    "User",
    "UserSettings",
    "Subscription",
    "AlertSent",
    "UserDeal",
]


class Collection(Base):
    """Коллекция NFT-подарков."""
    
    __tablename__ = "collections"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    supply: Mapped[int] = mapped_column(Integer, nullable=False)
    floor_cache: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    floor_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    listings = relationship("Listing", back_populates="collection")
    sales = relationship("Sale", back_populates="collection")
    floors = relationship("Floor", back_populates="collection")


class AttributeColor(Base):
    """Цветовой анализ атрибутов для режима Mono Sniper."""
    
    __tablename__ = "attribute_colors"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id"), nullable=False)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    backdrop_id: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Доминантные цвета в формате OKLCH [{"l": 0.5, "c": 0.1, "h": 180}, ...]
    dominant_colors: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Оценка монохромности (0-1)
    mono_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    __table_args__ = (
        UniqueConstraint("collection_id", "model_id", "backdrop_id", name="uq_color_combo"),
        Index("ix_mono_score", "mono_score"),
    )


class Listing(Base):
    """Листинг (активное предложение) на маркете."""
    
    __tablename__ = "listings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Идентификация
    market: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id"), nullable=False)
    
    # Атрибуты подарка
    gift_number: Mapped[int] = mapped_column(Integer, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    backdrop: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Цена
    price_ton: Mapped[float] = mapped_column(Float, nullable=False)
    price_raw: Mapped[float] = mapped_column(Float, nullable=False)  # в оригинальной валюте
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # URL
    url: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Временные метки
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Статус
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    
    # Relationships
    collection = relationship("Collection", back_populates="listings")
    events = relationship("ListingEvent", back_populates="listing")
    alerts = relationship("AlertSent", back_populates="listing")
    
    __table_args__ = (
        UniqueConstraint("market", "external_id", name="uq_market_listing"),
        Index("ix_status", "status"),
        Index("ix_collection_model", "collection_id", "model"),
        Index("ix_last_seen", "last_seen"),
    )


class ListingEvent(Base):
    """События изменения листинга (смена цены и т.п.)."""
    
    __tablename__ = "listing_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    listing = relationship("Listing", back_populates="events")
    
    __table_args__ = (
        Index("ix_listing_events", "listing_id", "created_at"),
    )


class Sale(Base):
    """Продажа подарка."""
    
    __tablename__ = "sales"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    market: Mapped[str] = mapped_column(String(50), nullable=False)
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id"), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    backdrop: Mapped[str] = mapped_column(String(100), nullable=False)
    gift_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Цена
    price_ton: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Временные метки
    listed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sold_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Источник данных
    source: Mapped[str] = mapped_column(String(20), nullable=False)  # 'api' или 'inferred'
    
    # Relationships
    collection = relationship("Collection", back_populates="sales")
    
    __table_args__ = (
        Index("ix_sales_collection_model", "collection_id", "model", "backdrop"),
        Index("ix_sold_at", "sold_at"),
    )


class Floor(Base):
    """Снимок floor цены."""
    
    __tablename__ = "floors"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id"), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    market: Mapped[str] = mapped_column(String(50), nullable=False)
    
    floor_price: Mapped[float] = mapped_column(Float, nullable=False)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    collection = relationship("Collection", back_populates="floors")
    
    __table_args__ = (
        Index("ix_floors_lookup", "collection_id", "model", "market", "snapshot_at"),
    )


class User(Base):
    """Пользователь бота."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user_id
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Тариф
    tier: Mapped[str] = mapped_column(String(20), nullable=False, default="free")
    
    # Relationships
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    subscriptions = relationship("Subscription", back_populates="user")
    alerts = relationship("AlertSent", back_populates="user")
    deals = relationship("UserDeal", back_populates="user")


class UserSettings(Base):
    """Настройки пользователя."""
    
    __tablename__ = "user_settings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    
    # Режимы (включены/выключены)
    mode1_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    mode2_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mode3_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Настройки режима 1
    mode1_min_profit_pct: Mapped[float] = mapped_column(Float, default=10.0)
    mode1_min_profit_ton: Mapped[float] = mapped_column(Float, default=2.0)
    mode1_max_time_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mode1_max_buy_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Настройки режима 2
    mode2_floor_margin: Mapped[float] = mapped_column(Float, default=0.10)
    
    # Настройки режима 3
    mode3_min_tier: Mapped[str] = mapped_column(String(1), default="A")
    
    # Фильтры
    excluded_collections: Mapped[list] = mapped_column(JSON, default=list)
    
    # Лимиты
    alerts_per_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    silence_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Профиль
    profile: Mapped[str] = mapped_column(String(20), default="balanced")
    budget_ton: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="settings")


class Subscription(Base):
    """Подписка Pro."""
    
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    payment_stars: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    __table_args__ = (
        Index("ix_user_active", "user_id", "is_active"),
    )


class AlertSent(Base):
    """Отправленные алерты (дедупликация)."""
    
    __tablename__ = "alerts_sent"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price_at_send: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    listing = relationship("Listing", back_populates="alerts")
    
    __table_args__ = (
        Index("ix_user_mode", "user_id", "mode", "sent_at"),
    )


class UserDeal(Base):
    """Ручной учёт сделок пользователя (/mydeals)."""
    
    __tablename__ = "user_deals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    gift_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gift_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    bought_price: Mapped[float] = mapped_column(Float, nullable=False)
    sold_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    bought_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sold_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    profit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="deals")
    
    __table_args__ = (
        Index("ix_user_deals", "user_id", "created_at"),
    )
