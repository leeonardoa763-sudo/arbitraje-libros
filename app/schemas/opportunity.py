from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.opportunity import OpportunityStatus


class OpportunityCreate(BaseModel):
    """Datos necesarios para registrar una oportunidad detectada por el scraper."""

    book_id: uuid.UUID
    source_url: str = Field(..., max_length=2048)
    source_seller: str = Field(..., max_length=300)
    source_price_cents: int = Field(..., ge=0)
    source_condition: str = Field(..., max_length=100)
    target_price_cents: int = Field(..., ge=0)
    commission_cents: int = Field(..., ge=0)
    shipping_cents: int = Field(..., ge=0)
    iva_cents: int = Field(..., ge=0)
    net_margin_cents: int
    margin_pct: Decimal = Field(..., ge=Decimal("-100"), le=Decimal("100"))
    detected_at: datetime
    expires_at: datetime


class OpportunityRead(OpportunityCreate):
    """Representación completa de una oportunidad, incluyendo campos calculados y de IA."""

    id: uuid.UUID
    ai_score: int | None = Field(default=None, ge=0, le=100)
    ai_reasoning: str | None = None
    status: OpportunityStatus

    model_config = ConfigDict(from_attributes=True)


class OpportunityStatusUpdate(BaseModel):
    """Actualización de estado de una oportunidad (ej: descartar, publicar)."""

    status: OpportunityStatus


class OpportunityAIUpdate(BaseModel):
    """Resultado del evaluador de IA para enriquecer una oportunidad existente."""

    ai_score: int = Field(..., ge=0, le=100)
    ai_reasoning: str
