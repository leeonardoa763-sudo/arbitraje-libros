from __future__ import annotations

from app.core.exceptions import (
    AIServiceError,
    ArbitrajeError,
    BookMetadataNotFoundError,
    InvalidISBNError,
    MarginCalculationError,
    MercadoLibreAPIError,
    MLPermanentError,
    MLTokenExpiredError,
    MLTransientError,
    PublicationError,
    ScrapingError,
)


class TestExceptionHierarchy:
    def test_base_exception(self) -> None:
        exc = ArbitrajeError("base")
        assert isinstance(exc, Exception)
        assert str(exc) == "base"

    def test_mercadolibre_api_error_is_base(self) -> None:
        assert issubclass(MercadoLibreAPIError, ArbitrajeError)

    def test_ml_token_expired_is_ml_error(self) -> None:
        assert issubclass(MLTokenExpiredError, MercadoLibreAPIError)

    def test_ml_transient_is_ml_error(self) -> None:
        assert issubclass(MLTransientError, MercadoLibreAPIError)

    def test_ml_permanent_is_ml_error(self) -> None:
        assert issubclass(MLPermanentError, MercadoLibreAPIError)

    def test_book_metadata_not_found_is_base(self) -> None:
        assert issubclass(BookMetadataNotFoundError, ArbitrajeError)

    def test_invalid_isbn_is_base(self) -> None:
        assert issubclass(InvalidISBNError, ArbitrajeError)

    def test_margin_calculation_is_base(self) -> None:
        assert issubclass(MarginCalculationError, ArbitrajeError)

    def test_scraping_is_base(self) -> None:
        assert issubclass(ScrapingError, ArbitrajeError)

    def test_publication_is_base(self) -> None:
        assert issubclass(PublicationError, ArbitrajeError)

    def test_ai_service_is_base(self) -> None:
        assert issubclass(AIServiceError, ArbitrajeError)


class TestExceptionRaisable:
    def test_raise_invalid_isbn(self) -> None:
        import pytest

        with pytest.raises(InvalidISBNError) as exc_info:
            raise InvalidISBNError("ISBN inválido: 123")
        assert "123" in str(exc_info.value)

    def test_raise_ml_token_expired_caught_as_ml_error(self) -> None:
        import pytest

        with pytest.raises(MercadoLibreAPIError):
            raise MLTokenExpiredError("token expirado")

    def test_raise_ml_transient_caught_as_base(self) -> None:
        import pytest

        with pytest.raises(ArbitrajeError):
            raise MLTransientError("rate limit")

    def test_raise_margin_calculation_error(self) -> None:
        import pytest

        with pytest.raises(MarginCalculationError, match="negativo"):
            raise MarginCalculationError("precio negativo")
