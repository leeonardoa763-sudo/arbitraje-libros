"""Schemas Pydantic para validación de I/O de la API."""

from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.schemas.opportunity import (
    OpportunityAIUpdate,
    OpportunityCreate,
    OpportunityRead,
    OpportunityStatusUpdate,
)
from app.schemas.publication import (
    PublicationCreate,
    PublicationRead,
    PublicationStatusUpdate,
)

__all__ = [
    "BookCreate",
    "BookRead",
    "BookUpdate",
    "OpportunityAIUpdate",
    "OpportunityCreate",
    "OpportunityRead",
    "OpportunityStatusUpdate",
    "PublicationCreate",
    "PublicationRead",
    "PublicationStatusUpdate",
]
