from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.book import BookCategory, MetadataSource


class BookBase(BaseModel):
    """Campos compartidos entre creación y lectura de un libro."""

    isbn_13: str = Field(..., min_length=13, max_length=13, pattern=r"^\d{13}$")
    isbn_10: str | None = Field(
        default=None, min_length=10, max_length=10, pattern=r"^\d{9}[\dX]$"
    )
    title: str = Field(..., min_length=1, max_length=500)
    authors: list[Any] = Field(default_factory=list)
    publisher: str | None = None
    publication_year: int | None = Field(default=None, ge=1000, le=9999)
    category: BookCategory
    cover_url: str | None = None
    metadata_source: MetadataSource


class BookCreate(BookBase):
    """Datos necesarios para registrar un libro nuevo en el catálogo."""

    pass


class BookRead(BookBase):
    """Representación completa de un libro, incluyendo campos generados por la BD."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookUpdate(BaseModel):
    """Campos actualizables de un libro (todos opcionales)."""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    authors: list[Any] | None = None
    publisher: str | None = None
    publication_year: int | None = Field(default=None, ge=1000, le=9999)
    category: BookCategory | None = None
    cover_url: str | None = None
    metadata_source: MetadataSource | None = None
