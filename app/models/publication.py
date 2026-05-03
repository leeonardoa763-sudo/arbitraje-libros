from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity


class PublicationStatus(enum.StrEnum):
    """Estado del listing en Mercado Libre."""

    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    SOLD = "sold"


class Publication(Base):
    """Registro de una oportunidad que se publicó en nuestra cuenta de ML."""

    __tablename__ = "publications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("opportunities.id"))
    ml_item_id: Mapped[str] = mapped_column(String(100), unique=True)
    ml_permalink: Mapped[str] = mapped_column(String(2048))
    published_title: Mapped[str] = mapped_column(String(500))
    published_description: Mapped[str] = mapped_column(Text)
    published_price_cents: Mapped[int] = mapped_column(Integer)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[PublicationStatus] = mapped_column(
        Enum(PublicationStatus, name="publication_status"),
        default=PublicationStatus.ACTIVE,
    )
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    final_margin_cents: Mapped[int | None] = mapped_column(Integer)

    opportunity: Mapped[Opportunity] = relationship(
        "Opportunity", back_populates="publication", lazy="select"
    )
