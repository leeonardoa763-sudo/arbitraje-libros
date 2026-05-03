from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.publication import Publication


class OpportunityStatus(enum.StrEnum):
    """Estado del ciclo de vida de una oportunidad detectada."""

    OPEN = "open"
    PUBLISHED = "published"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class Opportunity(Base):
    """Libro detectado en ML que cumple los criterios mínimos de margen.

    La llave de deduplicación es (book_id, source_url, source_price_cents):
    si el mismo scraper corre 100 veces, no se crean duplicados mientras
    la URL y el precio no cambien.
    """

    __tablename__ = "opportunities"
    __table_args__ = (
        UniqueConstraint(
            "book_id",
            "source_url",
            "source_price_cents",
            name="uq_opportunity_dedup",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id"))
    source_url: Mapped[str] = mapped_column(String(2048))
    source_seller: Mapped[str] = mapped_column(String(300))
    source_price_cents: Mapped[int] = mapped_column(Integer)
    source_condition: Mapped[str] = mapped_column(String(100))
    target_price_cents: Mapped[int] = mapped_column(Integer)
    commission_cents: Mapped[int] = mapped_column(Integer)
    shipping_cents: Mapped[int] = mapped_column(Integer)
    iva_cents: Mapped[int] = mapped_column(Integer)
    net_margin_cents: Mapped[int] = mapped_column(Integer)
    margin_pct: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    ai_score: Mapped[int | None] = mapped_column(Integer)
    ai_reasoning: Mapped[str | None] = mapped_column(Text)
    status: Mapped[OpportunityStatus] = mapped_column(
        Enum(OpportunityStatus, name="opportunity_status"),
        default=OpportunityStatus.OPEN,
    )
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    book: Mapped[Book] = relationship("Book", back_populates="opportunities", lazy="select")
    publication: Mapped[Publication | None] = relationship(
        "Publication", back_populates="opportunity", uselist=False, lazy="select"
    )
