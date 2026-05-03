"""Tests unitarios para modelos SQLAlchemy.

Verifican que los enums, clases y relaciones estén correctamente definidos
sin necesitar una conexión a la base de datos.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.models.book import Book, BookCategory, MetadataSource
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.price_history import Platform, PriceHistory
from app.models.publication import Publication, PublicationStatus

# =============================================================================
# Tests de enums
# =============================================================================


@pytest.mark.unit
class TestBookCategory:
    """BookCategory debe cubrir exactamente las categorías del dominio."""

    def test_valores_existentes(self) -> None:
        assert BookCategory.TECH == "TECH"
        assert BookCategory.MEDICINE == "MEDICINE"
        assert BookCategory.LAW == "LAW"
        assert BookCategory.BUSINESS == "BUSINESS"
        assert BookCategory.OTHER == "OTHER"

    def test_es_string_enum(self) -> None:
        assert isinstance(BookCategory.TECH, str)

    def test_total_de_categorias(self) -> None:
        assert len(BookCategory) == 5


@pytest.mark.unit
class TestMetadataSource:
    """MetadataSource debe representar todas las fuentes de datos de libros."""

    def test_valores_existentes(self) -> None:
        assert MetadataSource.GOOGLE_BOOKS == "google_books"
        assert MetadataSource.OPEN_LIBRARY == "open_library"
        assert MetadataSource.MANUAL == "manual"
        assert MetadataSource.ML_SCRAPE == "ml_scrape"

    def test_es_string_enum(self) -> None:
        assert isinstance(MetadataSource.GOOGLE_BOOKS, str)


@pytest.mark.unit
class TestOpportunityStatus:
    """OpportunityStatus cubre el ciclo de vida completo de una oportunidad."""

    def test_valores_existentes(self) -> None:
        assert OpportunityStatus.OPEN == "open"
        assert OpportunityStatus.PUBLISHED == "published"
        assert OpportunityStatus.DISMISSED == "dismissed"
        assert OpportunityStatus.EXPIRED == "expired"

    def test_total_de_estados(self) -> None:
        assert len(OpportunityStatus) == 4


@pytest.mark.unit
class TestPublicationStatus:
    """PublicationStatus cubre los estados posibles de un item en ML."""

    def test_valores_existentes(self) -> None:
        assert PublicationStatus.ACTIVE == "active"
        assert PublicationStatus.PAUSED == "paused"
        assert PublicationStatus.CLOSED == "closed"
        assert PublicationStatus.SOLD == "sold"


@pytest.mark.unit
class TestPlatform:
    """Platform — solo ML por ahora, pero permite extensión futura."""

    def test_valor_ml(self) -> None:
        assert Platform.ML == "ml"


# =============================================================================
# Tests de instanciación de modelos (sin BD)
# =============================================================================


@pytest.mark.unit
class TestBookModel:
    """Book debe poder instanciarse con datos válidos."""

    def test_instanciacion_basica(self) -> None:
        book = Book(
            isbn_13="9786073829939",
            title="Clean Code",
            authors=["Robert C. Martin"],
            category=BookCategory.TECH,
            metadata_source=MetadataSource.GOOGLE_BOOKS,
        )
        assert book.title == "Clean Code"
        assert book.category == BookCategory.TECH
        assert book.metadata_source == MetadataSource.GOOGLE_BOOKS

    def test_campos_opcionales_son_none(self) -> None:
        book = Book(
            isbn_13="9786073829939",
            title="Clean Code",
            authors=["Robert C. Martin"],
            category=BookCategory.TECH,
            metadata_source=MetadataSource.GOOGLE_BOOKS,
        )
        assert book.isbn_10 is None
        assert book.publisher is None
        assert book.publication_year is None
        assert book.cover_url is None

    def test_nombre_de_tabla(self) -> None:
        assert Book.__tablename__ == "books"

    def test_relaciones_definidas(self) -> None:
        assert hasattr(Book, "opportunities")
        assert hasattr(Book, "price_history")


@pytest.mark.unit
class TestOpportunityModel:
    """Opportunity debe instanciarse correctamente y respetar el default de status."""

    def test_instanciacion_basica(self) -> None:
        now = datetime.now(tz=UTC)
        opp = Opportunity(
            book_id=uuid.uuid4(),
            source_url="https://www.mercadolibre.com.mx/item/123",
            source_seller="vendedor_test",
            source_price_cents=15000,
            source_condition="used",
            target_price_cents=25000,
            commission_cents=3250,
            shipping_cents=1200,
            iva_cents=192,
            net_margin_cents=5358,
            margin_pct=Decimal("21.43"),
            detected_at=now,
            expires_at=now,
        )
        assert opp.source_price_cents == 15000
        assert opp.net_margin_cents == 5358

    def test_status_default_configurado(self) -> None:
        # El default se aplica en INSERT (nivel BD), no en construcción Python.
        # Verificamos que la columna tenga el default correcto configurado.
        col = Opportunity.__table__.c["status"]
        assert col.default is not None
        assert col.default.arg == OpportunityStatus.OPEN

    def test_nombre_de_tabla(self) -> None:
        assert Opportunity.__tablename__ == "opportunities"

    def test_constraint_deduplicacion_definida(self) -> None:
        constraint_names = {
            c.name for c in Opportunity.__table_args__ if hasattr(c, "name")
        }
        assert "uq_opportunity_dedup" in constraint_names


@pytest.mark.unit
class TestPublicationModel:
    """Publication debe instanciarse con el status activo por default."""

    def test_instanciacion_basica(self) -> None:
        now = datetime.now(tz=UTC)
        pub = Publication(
            opportunity_id=uuid.uuid4(),
            ml_item_id="MLM123456789",
            ml_permalink="https://articulo.mercadolibre.com.mx/MLM-123456789",
            published_title="Clean Code - Robert Martin",
            published_description="Excelente estado, pocas marcas de uso.",
            published_price_cents=25000,
            published_at=now,
        )
        assert pub.ml_item_id == "MLM123456789"
        assert pub.published_price_cents == 25000

    def test_status_default_configurado(self) -> None:
        # El default se aplica en INSERT (nivel BD), no en construcción Python.
        col = Publication.__table__.c["status"]
        assert col.default is not None
        assert col.default.arg == PublicationStatus.ACTIVE

    def test_nombre_de_tabla(self) -> None:
        assert Publication.__tablename__ == "publications"


@pytest.mark.unit
class TestPriceHistoryModel:
    """PriceHistory debe instanciarse con datos de precio válidos."""

    def test_instanciacion_basica(self) -> None:
        now = datetime.now(tz=UTC)
        history = PriceHistory(
            book_id=uuid.uuid4(),
            platform=Platform.ML,
            price_cents=18000,
            condition="used",
            seen_at=now,
        )
        assert history.price_cents == 18000
        assert history.platform == Platform.ML

    def test_nombre_de_tabla(self) -> None:
        assert PriceHistory.__tablename__ == "price_history"
