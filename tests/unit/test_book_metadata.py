from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.core.exceptions import BookMetadataNotFoundError, InvalidISBNError
from app.models.book import BookCategory, MetadataSource
from app.services.book_metadata import (
    BookMetadata,
    BookMetadataService,
    GoogleBooksClient,
    OpenLibraryClient,
    _classify_category,
    _parse_year,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_fixture(name: str) -> Any:
    return json.loads((FIXTURES_DIR / name).read_text())


def _make_mock_http(json_data: Any) -> AsyncMock:
    """Crea un httpx.AsyncClient mock que retorna json_data en .get()."""
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    mock_response.raise_for_status.return_value = None

    mock_http = AsyncMock(spec=httpx.AsyncClient)
    mock_http.get.return_value = mock_response
    return mock_http


# =============================================================================
# Tests de helpers puros
# =============================================================================


class TestClassifyCategory:
    def test_tech_from_title(self) -> None:
        assert _classify_category("Python Programming", []) == BookCategory.TECH

    def test_tech_from_subject(self) -> None:
        assert _classify_category("Mi libro", ["computers"]) == BookCategory.TECH

    def test_medicine_from_title(self) -> None:
        assert _classify_category("Anatomía Humana", []) == BookCategory.MEDICINE

    def test_medicine_from_subject(self) -> None:
        assert _classify_category("Manual", ["medical"]) == BookCategory.MEDICINE

    def test_law_from_title(self) -> None:
        assert _classify_category("Derecho Penal Mexicano", []) == BookCategory.LAW

    def test_business_from_title(self) -> None:
        assert _classify_category("Administración de Empresas", []) == BookCategory.BUSINESS

    def test_other_when_no_match(self) -> None:
        assert _classify_category("Historia del Arte", ["painting"]) == BookCategory.OTHER

    def test_case_insensitive(self) -> None:
        assert _classify_category("PYTHON ADVANCED", []) == BookCategory.TECH


class TestParseYear:
    def test_full_date(self) -> None:
        assert _parse_year("2008-05-08") == 2008

    def test_year_only(self) -> None:
        assert _parse_year("2008") == 2008

    def test_month_year(self) -> None:
        assert _parse_year("May 2008") == 2008

    def test_text_with_day(self) -> None:
        assert _parse_year("January 15, 1999") == 1999

    def test_empty_string(self) -> None:
        assert _parse_year("") is None

    def test_no_year_in_string(self) -> None:
        assert _parse_year("sin fecha") is None


# =============================================================================
# Tests de GoogleBooksClient
# =============================================================================


class TestGoogleBooksClient:
    @pytest.mark.asyncio
    async def test_fetch_found(self) -> None:
        data = _load_fixture("google_books_9780596517748.json")
        client = GoogleBooksClient(http_client=_make_mock_http(data))

        result = await client.fetch("9780596517748")

        assert result is not None
        assert result.isbn_13 == "9780596517748"
        assert result.isbn_10 == "0596517742"
        assert result.title == "JavaScript: The Good Parts"
        assert result.authors == ["Douglas Crockford"]
        assert result.publisher == "O'Reilly Media"
        assert result.publication_year == 2008
        assert result.category == BookCategory.TECH
        assert result.cover_url is not None
        assert result.metadata_source == MetadataSource.GOOGLE_BOOKS

    @pytest.mark.asyncio
    async def test_fetch_not_found_returns_none(self) -> None:
        data = _load_fixture("google_books_not_found.json")
        client = GoogleBooksClient(http_client=_make_mock_http(data))

        result = await client.fetch("9780000000000")

        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_subtitle_concatenated(self) -> None:
        data = _load_fixture("google_books_9780596517748.json")
        client = GoogleBooksClient(http_client=_make_mock_http(data))

        result = await client.fetch("9780596517748")

        assert result is not None
        assert ": " in result.title
        assert result.title == "JavaScript: The Good Parts"

    @pytest.mark.asyncio
    async def test_fetch_no_subtitle(self) -> None:
        data = _load_fixture("google_books_9780596517748.json")
        data["items"][0]["volumeInfo"].pop("subtitle")
        client = GoogleBooksClient(http_client=_make_mock_http(data))

        result = await client.fetch("9780596517748")

        assert result is not None
        assert result.title == "JavaScript"

    @pytest.mark.asyncio
    async def test_fetch_includes_api_key_when_set(self) -> None:
        data = _load_fixture("google_books_not_found.json")
        mock_http = _make_mock_http(data)
        client = GoogleBooksClient(api_key="my-key", http_client=mock_http)

        await client.fetch("9780596517748")

        call_kwargs = mock_http.get.call_args
        params: dict[str, str] = call_kwargs.kwargs.get(
            "params", call_kwargs.args[1] if len(call_kwargs.args) > 1 else {}
        )
        assert params.get("key") == "my-key"

    @pytest.mark.asyncio
    async def test_fetch_no_api_key_when_empty(self) -> None:
        data = _load_fixture("google_books_not_found.json")
        mock_http = _make_mock_http(data)
        client = GoogleBooksClient(api_key="", http_client=mock_http)

        await client.fetch("9780596517748")

        call_kwargs = mock_http.get.call_args
        params: dict[str, str] = call_kwargs.kwargs.get("params", {})
        assert "key" not in params


# =============================================================================
# Tests de OpenLibraryClient
# =============================================================================


class TestOpenLibraryClient:
    @pytest.mark.asyncio
    async def test_fetch_found(self) -> None:
        data = _load_fixture("open_library_9780596517748.json")
        client = OpenLibraryClient(http_client=_make_mock_http(data))

        result = await client.fetch("9780596517748")

        assert result is not None
        assert result.isbn_13 == "9780596517748"
        assert result.isbn_10 == "0596517742"
        assert result.title == "JavaScript: The Good Parts"
        assert result.authors == ["Douglas Crockford"]
        assert result.publisher == "O'Reilly Media"
        assert result.publication_year == 2008
        assert result.category == BookCategory.TECH
        assert result.cover_url == "https://covers.openlibrary.org/b/id/8091016-L.jpg"
        assert result.metadata_source == MetadataSource.OPEN_LIBRARY

    @pytest.mark.asyncio
    async def test_fetch_not_found_returns_none(self) -> None:
        data = _load_fixture("open_library_not_found.json")
        client = OpenLibraryClient(http_client=_make_mock_http(data))

        result = await client.fetch("9780000000000")

        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_uses_correct_bibkey(self) -> None:
        data = _load_fixture("open_library_not_found.json")
        mock_http = _make_mock_http(data)
        client = OpenLibraryClient(http_client=mock_http)

        await client.fetch("9780596517748")

        call_kwargs = mock_http.get.call_args
        params: dict[str, str] = call_kwargs.kwargs.get("params", {})
        assert params.get("bibkeys") == "ISBN:9780596517748"


# =============================================================================
# Tests de BookMetadataService
# =============================================================================


class TestBookMetadataService:
    def _make_service(
        self,
        google_result: BookMetadata | None,
        open_library_result: BookMetadata | None,
    ) -> BookMetadataService:
        google_mock = AsyncMock(spec=GoogleBooksClient)
        google_mock.fetch.return_value = google_result

        ol_mock = AsyncMock(spec=OpenLibraryClient)
        ol_mock.fetch.return_value = open_library_result

        return BookMetadataService(google_books=google_mock, open_library=ol_mock)

    def _dummy_metadata(self, source: MetadataSource) -> BookMetadata:
        return BookMetadata(
            isbn_13="9780596517748",
            title="Test",
            authors=["Autor"],
            category=BookCategory.OTHER,
            metadata_source=source,
        )

    @pytest.mark.asyncio
    async def test_uses_google_books_first(self) -> None:
        gb_result = self._dummy_metadata(MetadataSource.GOOGLE_BOOKS)
        service = self._make_service(gb_result, None)

        result = await service.fetch_by_isbn("9780596517748")

        assert result.metadata_source == MetadataSource.GOOGLE_BOOKS

    @pytest.mark.asyncio
    async def test_falls_back_to_open_library(self) -> None:
        ol_result = self._dummy_metadata(MetadataSource.OPEN_LIBRARY)
        service = self._make_service(None, ol_result)

        result = await service.fetch_by_isbn("9780596517748")

        assert result.metadata_source == MetadataSource.OPEN_LIBRARY

    @pytest.mark.asyncio
    async def test_open_library_not_called_when_google_succeeds(self) -> None:
        gb_result = self._dummy_metadata(MetadataSource.GOOGLE_BOOKS)
        google_mock = AsyncMock(spec=GoogleBooksClient)
        google_mock.fetch.return_value = gb_result
        ol_mock = AsyncMock(spec=OpenLibraryClient)

        service = BookMetadataService(google_books=google_mock, open_library=ol_mock)
        await service.fetch_by_isbn("9780596517748")

        ol_mock.fetch.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_when_both_fail(self) -> None:
        service = self._make_service(None, None)

        with pytest.raises(BookMetadataNotFoundError):
            await service.fetch_by_isbn("9780596517748")

    @pytest.mark.asyncio
    async def test_normalizes_isbn10_input(self) -> None:
        gb_result = self._dummy_metadata(MetadataSource.GOOGLE_BOOKS)
        google_mock = AsyncMock(spec=GoogleBooksClient)
        google_mock.fetch.return_value = gb_result
        ol_mock = AsyncMock(spec=OpenLibraryClient)

        service = BookMetadataService(google_books=google_mock, open_library=ol_mock)
        # ISBN-10 de "JavaScript: The Good Parts"
        await service.fetch_by_isbn("0596517742")

        # Debe llamar a fetch con el ISBN-13 normalizado
        google_mock.fetch.assert_called_once_with("9780596517748")

    @pytest.mark.asyncio
    async def test_raises_on_invalid_isbn(self) -> None:
        service = self._make_service(None, None)

        with pytest.raises(InvalidISBNError):
            await service.fetch_by_isbn("isbn-invalido-123")
