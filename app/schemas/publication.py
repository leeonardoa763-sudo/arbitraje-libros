from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.publication import PublicationStatus


class PublicationCreate(BaseModel):
    """Datos necesarios para registrar una publicación en ML."""

    opportunity_id: uuid.UUID
    ml_item_id: str = Field(..., max_length=100)
    ml_permalink: str = Field(..., max_length=2048)
    published_title: str = Field(..., min_length=1, max_length=500)
    published_description: str = Field(..., min_length=1)
    published_price_cents: int = Field(..., ge=0)
    published_at: datetime


class PublicationRead(PublicationCreate):
    """Representación completa de una publicación, incluyendo estado y resultado de venta."""

    id: uuid.UUID
    status: PublicationStatus
    sold_at: datetime | None = None
    final_margin_cents: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PublicationStatusUpdate(BaseModel):
    """Actualización de estado de una publicación (ej: pausar, marcar como vendida)."""

    status: PublicationStatus
    sold_at: datetime | None = None
    final_margin_cents: int | None = None
