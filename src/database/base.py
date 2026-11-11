"""Базовый класс для всех моделей SQLAlchemy."""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Naming convention для constraint'ов (чтобы Alembic генерировал читаемые имена)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    
    metadata = metadata
    
    # Общие поля для всех таблиц
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Конвертация модели в словарь."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
