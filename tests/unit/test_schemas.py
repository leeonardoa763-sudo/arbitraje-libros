"""Tests unitarios para schemas Pydantic.

Verifican que la validación de entrada/salida funcione correctamente:
datos válidos deben pasar, datos inválidos deben lanzar ValidationError.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.models.book import BookCategory, MetadataSource
from app.models.opportunity import OpportunityStatus
from app.models.publication import PublicationStatus
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.schemas.opportunity import (
    OpportunityAIUpdate,
    OpportunityCreate,
    OpportunityRead,
    OpportunityStatusUpdate,
)
from app.schemas.publication import PublicationCreate, PublicationStatusUpdate

# =============================================================================
# Helpers
# =============================================================================

NOW = datetime.now(tz=UTC)


def _book_data() -> dict[str, object]:
    """Datos válidos mínimos para crear un libro."""
    return {
        "isbn_13": "9786073829939",
        "title": "Clean Code",
        "authors": ["Robert C. Martin"],
        "category": BookCategory.TECH,
        "metadata_source": MetadataSource.GOOGLE_BOOKS,
    }


def _opportunity_data() -> dict[str, object]:
    """Datos válidos mínimos para crear una oportunidad."""
    return {
        "book_id": uuid.uuid4(),
        "source_url": "https://www.mercadolibre.com.mx/item/123",
        "source_seller": "vendedor_test",
        "source_price_cents": 15000,
        "source_condition": "used",
        "target_price_cents": 25000,
        "commission_cents": 3250,
        "shipping_cents": 1200,
        "iva_cents": 192,
        "net_margin_cents": 5358,
        "margin_pct": Decimal("21.43"),
        "detected_at": NOW,
        "expires_at": NOW,
    }


def _publication_data() -> dict[str, object]:
    """Datos válidos mínimos para crear una publicación."""
    return {
        "opportunity_id": uuid.uuid4(),
        "ml_item_id": "MLM123456789",
        "ml_permalink": "https://articulo.mercadolibre.com.mx/MLM-123456789",
        "published_title": "Clean Code - Robert Martin",
        "published_description": "Excelente estado, pocas marcas de uso.",
        "published_price_cents": 25000,
        "published_at": NOW,
    }


# =============================================================================
# Tests de BookCreate / BookRead / BookUpdate
# =============================================================================


@pytest.mark.unit
class TestBookCreate:
    """BookCreate debe aceptar ISBNs válidos y rechazar malformados."""

    def test_datos_validos(self) -> None:
        book = BookCreate(**_book_data())
        assert book.isbn_13 == "9786073829939"
        assert book.title == "Clean Code"
        assert book.category == BookCategory.TECH

    def test_isbn_13_invalido_longitud(self) -> None:
        data = {**_book_data(), "isbn_13": "97860738"}
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_isbn_13_invalido_no_digitos(self) -> None:
        data = {**_book_data(), "isbn_13": "978607382993X"}
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_isbn_10_opcional(self) -> None:
        book = BookCreate(**_book_data())
        assert book.isbn_10 is None

    def test_isbn_10_valido(self) -> None:
        data = {**_book_data(), "isbn_10": "0132350882"}
        book = BookCreate(**data)
        assert book.isbn_10 == "0132350882"

    def test_isbn_10_con_x_final(self) -> None:
        data = {**_book_data(), "isbn_10": "097522011X"}
        book = BookCreate(**data)
        assert book.isbn_10 == "097522011X"

    def test_isbn_10_invalido_longitud(self) -> None:
        data = {**_book_data(), "isbn_10": "013235088"}
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_titulo_vacio_rechazado(self) -> None:
        data = {**_book_data(), "title": ""}
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_anio_publicacion_invalido(self) -> None:
        data = {**_book_data(), "publication_year": 999}
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_anio_publicacion_futuro_invalido(self) -> None:
        data = {**_book_data(), "publication_year": 10000}
        with pytest.raises(ValidationError):
            BookCreate(**data)

    def test_autores_default_lista_vacia(self) -> None:
        data = {k: v for k, v in _book_data().items() if k != "authors"}
        book = BookCreate(**data)
        assert book.authors == []


@pytest.mark.unit
class TestBookRead:
    """BookRead debe construirse desde atributos de un modelo SQLAlchemy."""

    def test_from_attributes(self) -> None:
        book_id = uuid.uuid4()
        fake_book = SimpleNamespace(
            id=book_id,
            isbn_13="9786073829939",
            isbn_10=None,
            title="Clean Code",
            authors=["Robert C. Martin"],
            publisher=None,
            publication_year=2008,
            category=BookCategory.TECH,
            cover_url=None,
            metadata_source=MetadataSource.GOOGLE_BOOKS,
            created_at=NOW,
            updated_at=NOW,
        )

        read = BookRead.model_validate(fake_book, from_attributes=True)
        assert read.id == book_id
        assert read.isbn_13 == "9786073829939"
        assert read.created_at == NOW


@pytest.mark.unit
class TestBookUpdate:
    """BookUpdate acepta solo los campos que cambian (todos opcionales)."""

    def test_actualizacion_parcial(self) -> None:
        update = BookUpdate(title="Clean Code 2nd Edition")
        assert update.title == "Clean Code 2nd Edition"
        assert update.category is None

    def test_sin_campos_valido(self) -> None:
        update = BookUpdate()
        assert update.title is None
        assert update.authors is None


# =============================================================================
# Tests de OpportunityCreate / OpportunityRead
# =============================================================================


@pytest.mark.unit
class TestOpportunityCreate:
    """OpportunityCreate debe rechazar precios negativos."""

    def test_datos_validos(self) -> None:
        opp = OpportunityCreate(**_opportunity_data())
        assert opp.source_price_cents == 15000
        assert opp.net_margin_cents == 5358

    def test_precio_compra_negativo_rechazado(self) -> None:
        data = {**_opportunity_data(), "source_price_cents": -1}
        with pytest.raises(ValidationError):
            OpportunityCreate(**data)

    def test_comision_negativa_rechazada(self) -> None:
        data = {**_opportunity_data(), "commission_cents": -100}
        with pytest.raises(ValidationError):
            OpportunityCreate(**data)

    def test_margen_neto_puede_ser_negativo(self) -> None:
        data = {**_opportunity_data(), "net_margin_cents": -500}
        opp = OpportunityCreate(**data)
        assert opp.net_margin_cents == -500

    def test_margin_pct_fuera_de_rango(self) -> None:
        data = {**_opportunity_data(), "margin_pct": Decimal("200")}
        with pytest.raises(ValidationError):
            OpportunityCreate(**data)


@pytest.mark.unit
class TestOpportunityRead:
    """OpportunityRead incluye ai_score con rango validado (0-100)."""

    def test_ai_score_fuera_de_rango(self) -> None:
        data = {
            **_opportunity_data(),
            "id": uuid.uuid4(),
            "ai_score": 150,
            "status": OpportunityStatus.OPEN,
        }
        with pytest.raises(ValidationError):
            OpportunityRead(**data)

    def test_ai_score_negativo_rechazado(self) -> None:
        data = {
            **_opportunity_data(),
            "id": uuid.uuid4(),
            "ai_score": -1,
            "status": OpportunityStatus.OPEN,
        }
        with pytest.raises(ValidationError):
            OpportunityRead(**data)

    def test_ai_score_none_valido(self) -> None:
        data = {
            **_opportunity_data(),
            "id": uuid.uuid4(),
            "ai_score": None,
            "status": OpportunityStatus.OPEN,
        }
        opp = OpportunityRead(**data)
        assert opp.ai_score is None


@pytest.mark.unit
class TestOpportunityStatusUpdate:
    """OpportunityStatusUpdate solo permite estados válidos del enum."""

    def test_estado_valido(self) -> None:
        update = OpportunityStatusUpdate(status=OpportunityStatus.DISMISSED)
        assert update.status == OpportunityStatus.DISMISSED

    def test_estado_invalido(self) -> None:
        with pytest.raises(ValidationError):
            OpportunityStatusUpdate(status="invalid_status")  # type: ignore[arg-type]


@pytest.mark.unit
class TestOpportunityAIUpdate:
    """OpportunityAIUpdate valida el rango del score de IA."""

    def test_score_valido(self) -> None:
        update = OpportunityAIUpdate(ai_score=75, ai_reasoning="Buena oportunidad.")
        assert update.ai_score == 75

    def test_score_cero_valido(self) -> None:
        update = OpportunityAIUpdate(ai_score=0, ai_reasoning="Sin potencial.")
        assert update.ai_score == 0

    def test_score_cien_valido(self) -> None:
        update = OpportunityAIUpdate(ai_score=100, ai_reasoning="Oportunidad excelente.")
        assert update.ai_score == 100

    def test_score_mayor_a_100_rechazado(self) -> None:
        with pytest.raises(ValidationError):
            OpportunityAIUpdate(ai_score=101, ai_reasoning="Imposible.")


# =============================================================================
# Tests de PublicationCreate / PublicationRead
# =============================================================================


@pytest.mark.unit
class TestPublicationCreate:
    """PublicationCreate valida precios y campos requeridos."""

    def test_datos_validos(self) -> None:
        pub = PublicationCreate(**_publication_data())
        assert pub.ml_item_id == "MLM123456789"
        assert pub.published_price_cents == 25000

    def test_precio_negativo_rechazado(self) -> None:
        data = {**_publication_data(), "published_price_cents": -1}
        with pytest.raises(ValidationError):
            PublicationCreate(**data)

    def test_descripcion_vacia_rechazada(self) -> None:
        data = {**_publication_data(), "published_description": ""}
        with pytest.raises(ValidationError):
            PublicationCreate(**data)


@pytest.mark.unit
class TestPublicationStatusUpdate:
    """PublicationStatusUpdate permite registrar venta con margen final."""

    def test_marcar_como_vendida(self) -> None:
        update = PublicationStatusUpdate(
            status=PublicationStatus.SOLD,
            sold_at=NOW,
            final_margin_cents=4800,
        )
        assert update.status == PublicationStatus.SOLD
        assert update.final_margin_cents == 4800

    def test_pausar_sin_campos_opcionales(self) -> None:
        update = PublicationStatusUpdate(status=PublicationStatus.PAUSED)
        assert update.status == PublicationStatus.PAUSED
        assert update.sold_at is None
        assert update.final_margin_cents is None
