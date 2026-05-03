"""Modelos SQLAlchemy (tablas de la BD).

Importar todos los modelos aquí es necesario para que SQLAlchemy registre
las tablas en Base.metadata antes de que Alembic genere migraciones.
"""

from app.models.base import Base, TimestampMixin
from app.models.book import Book, BookCategory, MetadataSource
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.price_history import Platform, PriceHistory
from app.models.publication import Publication, PublicationStatus

__all__ = [
    "Base",
    "Book",
    "BookCategory",
    "MetadataSource",
    "Opportunity",
    "OpportunityStatus",
    "Platform",
    "PriceHistory",
    "Publication",
    "PublicationStatus",
    "TimestampMixin",
]
