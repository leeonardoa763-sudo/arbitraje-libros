from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.book import Book


class Platform(enum.StrEnum):
    """Plataforma en la que se detectó el precio."""

    ML = "ml"


class PriceHistory(Base):
    """Histórico de precios detectados por el scraper para análisis de tendencias."""

    __tablename__ = "price_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id"))
    platform: Mapped[Platform] = mapped_column(
        Enum(Platform, name="platform"),
    )
    price_cents: Mapped[int] = mapped_column(Integer)
    condition: Mapped[str] = mapped_column(String(100))
    seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    book: Mapped[Book] = relationship("Book", back_populates="price_history", lazy="select")
