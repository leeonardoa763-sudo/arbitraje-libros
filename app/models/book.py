from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.price_history import PriceHistory


class BookCategory(enum.StrEnum):
    """Categoría temática del libro."""

    TECH = "TECH"
    MEDICINE = "MEDICINE"
    LAW = "LAW"
    BUSINESS = "BUSINESS"
    OTHER = "OTHER"


class MetadataSource(enum.StrEnum):
    """Fuente de donde obtuvimos los metadatos del libro."""

    GOOGLE_BOOKS = "google_books"
    OPEN_LIBRARY = "open_library"
    MANUAL = "manual"
    ML_SCRAPE = "ml_scrape"


class Book(Base, TimestampMixin):
    """Catálogo único de libros normalizado por ISBN-13.

    ISBN-13 es la clave canónica. Todos los ISBN-10 se convierten a ISBN-13
    antes de almacenarlos (ver app/core/isbn.py).
    """

    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    isbn_13: Mapped[str] = mapped_column(String(13), unique=True)
    isbn_10: Mapped[str | None] = mapped_column(String(10))
    title: Mapped[str] = mapped_column(String(500))
    authors: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    publisher: Mapped[str | None] = mapped_column(String(300))
    publication_year: Mapped[int | None] = mapped_column(Integer)
    category: Mapped[BookCategory] = mapped_column(
        Enum(BookCategory, name="book_category"),
    )
    cover_url: Mapped[str | None] = mapped_column(String(2048))
    metadata_source: Mapped[MetadataSource] = mapped_column(
        Enum(MetadataSource, name="metadata_source"),
    )

    opportunities: Mapped[list[Opportunity]] = relationship(
        "Opportunity", back_populates="book", lazy="select"
    )
    price_history: Mapped[list[PriceHistory]] = relationship(
        "PriceHistory", back_populates="book", lazy="select"
    )
