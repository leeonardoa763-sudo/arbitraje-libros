from __future__ import annotations

import dataclasses
import re
from typing import Any

import httpx
import structlog
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.core.exceptions import BookMetadataNotFoundError
from app.core.isbn import normalize_isbn
from app.models.book import BookCategory, MetadataSource

logger = structlog.get_logger()

_YEAR_PATTERN = re.compile(r"\b(\d{4})\b")

_TECH_KEYWORDS: frozenset[str] = frozenset(
    {
        "programming",
        "software",
        "computer",
        "computers",
        "python",
        "java",
        "javascript",
        "algorithm",
        "machine learning",
        "data science",
        "computing",
        "network",
        "tecnología",
        "informática",
        "programación",
        "código",
        "database",
        "web",
        "linux",
        "unix",
    }
)

_MEDICINE_KEYWORDS: frozenset[str] = frozenset(
    {
        "medicine",
        "medical",
        "anatomy",
        "physiology",
        "pharmacology",
        "surgery",
        "clinical",
        "hospital",
        "diagnosis",
        "medicina",
        "médico",
        "anatomía",
        "fisiología",
        "farmacología",
        "cirugía",
        "enfermería",
        "salud",
        "health",
    }
)

_LAW_KEYWORDS: frozenset[str] = frozenset(
    {
        "law",
        "legal",
        "derecho",
        "jurídico",
        "constitución",
        "constitution",
        "court",
        "judicial",
        "attorney",
        "abogado",
        "criminal",
        "penal",
        "fiscal",
        "tributario",
    }
)

_BUSINESS_KEYWORDS: frozenset[str] = frozenset(
    {
        "business",
        "management",
        "marketing",
        "finance",
        "accounting",
        "economics",
        "economy",
        "administration",
        "empresa",
        "negocio",
        "administración",
        "finanzas",
        "contabilidad",
        "economía",
        "gerencia",
        "liderazgo",
        "leadership",
        "entrepreneur",
    }
)


@dataclasses.dataclass
class BookMetadata:
    """Metadata normalizada de un libro, independiente de la fuente."""

    isbn_13: str
    title: str
    authors: list[str]
    category: BookCategory
    metadata_source: MetadataSource
    isbn_10: str | None = None
    publisher: str | None = None
    publication_year: int | None = None
    cover_url: str | None = None


def _classify_category(title: str, subjects: list[str]) -> BookCategory:
    """Clasifica un libro en una categoría basado en título y materias.

    Args:
        title: Título del libro.
        subjects: Lista de materias o categorías.

    Returns:
        Categoría detectada, o OTHER si no hay coincidencia clara.
    """
    text = " ".join([title, *subjects]).lower()
    if any(kw in text for kw in _TECH_KEYWORDS):
        return BookCategory.TECH
    if any(kw in text for kw in _MEDICINE_KEYWORDS):
        return BookCategory.MEDICINE
    if any(kw in text for kw in _LAW_KEYWORDS):
        return BookCategory.LAW
    if any(kw in text for kw in _BUSINESS_KEYWORDS):
        return BookCategory.BUSINESS
    return BookCategory.OTHER


def _parse_year(date_str: str) -> int | None:
    """Extrae el año de publicación de un string de fecha.

    Acepta formatos: "2023", "2023-01", "2023-01-15", "January 2023", "May 8, 2008".

    Args:
        date_str: String con la fecha en cualquier formato.

    Returns:
        Año como entero, o None si no se puede extraer.
    """
    if not date_str:
        return None
    match = _YEAR_PATTERN.search(date_str)
    if match:
        year = int(match.group(1))
        if 1000 <= year <= 9999:
            return year
    return None


def _is_retryable_http_error(exc: BaseException) -> bool:
    """Determina si un error HTTP o de red es reintentable."""
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in {429, 500, 502, 503, 504}
    return False


class GoogleBooksClient:
    """Cliente para la API de Google Books con retry automático."""

    _BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    _TIMEOUT = 10.0

    def __init__(
        self,
        api_key: str = "",
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._http = http_client or httpx.AsyncClient(timeout=self._TIMEOUT)

    @retry(
        retry=retry_if_exception(_is_retryable_http_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def fetch(self, isbn_13: str) -> BookMetadata | None:
        """Busca metadata de un libro en Google Books por ISBN-13.

        Args:
            isbn_13: ISBN-13 normalizado (13 dígitos, sin guiones).

        Returns:
            BookMetadata si se encontró, None si no hay resultados.

        Raises:
            httpx.HTTPStatusError: Si la respuesta es un error no reintentable.
            httpx.TransportError: Si hay error de red (se reintenta automáticamente).
        """
        params: dict[str, str] = {"q": f"isbn:{isbn_13}"}
        if self._api_key:
            params["key"] = self._api_key

        response = await self._http.get(self._BASE_URL, params=params)
        response.raise_for_status()
        data: dict[str, Any] = response.json()

        items: list[dict[str, Any]] = data.get("items", [])
        if not items:
            logger.debug("google_books_not_found", isbn_13=isbn_13)
            return None

        volume_info: dict[str, Any] = items[0].get("volumeInfo", {})
        return self._parse_volume_info(isbn_13, volume_info)

    def _parse_volume_info(
        self,
        isbn_13: str,
        volume_info: dict[str, Any],
    ) -> BookMetadata:
        """Parsea el campo volumeInfo de un item de Google Books.

        Args:
            isbn_13: ISBN-13 del libro buscado.
            volume_info: Diccionario volumeInfo de la respuesta de Google Books.

        Returns:
            BookMetadata normalizado.
        """
        title: str = volume_info.get("title", "")
        subtitle: str = volume_info.get("subtitle", "")
        if subtitle:
            title = f"{title}: {subtitle}"

        authors: list[str] = volume_info.get("authors", [])
        publisher: str | None = volume_info.get("publisher") or None
        published_date: str = volume_info.get("publishedDate", "")
        categories: list[str] = volume_info.get("categories", [])

        isbn_10: str | None = None
        identifiers: list[dict[str, str]] = volume_info.get("industryIdentifiers", [])
        for identifier in identifiers:
            if identifier.get("type") == "ISBN_10":
                isbn_10 = identifier.get("identifier")
                break

        image_links: dict[str, str] = volume_info.get("imageLinks", {})
        cover_url: str | None = image_links.get("thumbnail") or None

        logger.info("google_books_found", isbn_13=isbn_13, title=title)

        return BookMetadata(
            isbn_13=isbn_13,
            isbn_10=isbn_10,
            title=title,
            authors=authors,
            publisher=publisher,
            publication_year=_parse_year(published_date),
            category=_classify_category(title, categories),
            cover_url=cover_url,
            metadata_source=MetadataSource.GOOGLE_BOOKS,
        )

    async def aclose(self) -> None:
        """Cierra el cliente HTTP subyacente."""
        await self._http.aclose()


class OpenLibraryClient:
    """Cliente para la API de Open Library (fallback) con retry automático."""

    _BASE_URL = "https://openlibrary.org/api/books"
    _TIMEOUT = 10.0

    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        self._http = http_client or httpx.AsyncClient(timeout=self._TIMEOUT)

    @retry(
        retry=retry_if_exception(_is_retryable_http_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def fetch(self, isbn_13: str) -> BookMetadata | None:
        """Busca metadata de un libro en Open Library por ISBN-13.

        Args:
            isbn_13: ISBN-13 normalizado.

        Returns:
            BookMetadata si se encontró, None si no hay resultados.

        Raises:
            httpx.HTTPStatusError: Si la respuesta es un error no reintentable.
            httpx.TransportError: Si hay error de red (se reintenta automáticamente).
        """
        bibkey = f"ISBN:{isbn_13}"
        params: dict[str, str] = {"bibkeys": bibkey, "format": "json", "jscmd": "data"}

        response = await self._http.get(self._BASE_URL, params=params)
        response.raise_for_status()
        data: dict[str, Any] = response.json()

        if bibkey not in data:
            logger.debug("open_library_not_found", isbn_13=isbn_13)
            return None

        book_data: dict[str, Any] = data[bibkey]
        return self._parse_book_data(isbn_13, book_data)

    def _parse_book_data(
        self,
        isbn_13: str,
        book_data: dict[str, Any],
    ) -> BookMetadata:
        """Parsea la respuesta de Open Library para un libro.

        Args:
            isbn_13: ISBN-13 del libro buscado.
            book_data: Datos del libro en formato Open Library (jscmd=data).

        Returns:
            BookMetadata normalizado.
        """
        title: str = book_data.get("title", "")
        subtitle: str = book_data.get("subtitle", "")
        if subtitle:
            title = f"{title}: {subtitle}"

        raw_authors: list[dict[str, str]] = book_data.get("authors", [])
        authors: list[str] = [a["name"] for a in raw_authors if a.get("name")]

        raw_publishers: list[dict[str, str]] = book_data.get("publishers", [])
        publisher: str | None = raw_publishers[0].get("name") if raw_publishers else None

        publish_date: str = book_data.get("publish_date", "")

        isbn_10: str | None = None
        identifiers: dict[str, list[str]] = book_data.get("identifiers", {})
        isbn10_list: list[str] = identifiers.get("isbn_10", [])
        if isbn10_list:
            isbn_10 = isbn10_list[0]

        cover: dict[str, str] = book_data.get("cover", {})
        cover_url: str | None = cover.get("large") or cover.get("medium") or None

        raw_subjects: list[dict[str, str]] = book_data.get("subjects", [])
        subject_names: list[str] = [s.get("name", "") for s in raw_subjects]

        logger.info("open_library_found", isbn_13=isbn_13, title=title)

        return BookMetadata(
            isbn_13=isbn_13,
            isbn_10=isbn_10,
            title=title,
            authors=authors,
            publisher=publisher,
            publication_year=_parse_year(publish_date),
            category=_classify_category(title, subject_names),
            cover_url=cover_url,
            metadata_source=MetadataSource.OPEN_LIBRARY,
        )

    async def aclose(self) -> None:
        """Cierra el cliente HTTP subyacente."""
        await self._http.aclose()


class BookMetadataService:
    """Servicio para obtener metadata de libros desde múltiples fuentes."""

    def __init__(
        self,
        google_books: GoogleBooksClient | None = None,
        open_library: OpenLibraryClient | None = None,
    ) -> None:
        settings = get_settings()
        self._google = google_books or GoogleBooksClient(api_key=settings.google_books_api_key)
        self._open_library = open_library or OpenLibraryClient()

    async def fetch_by_isbn(self, isbn: str) -> BookMetadata:
        """Obtiene metadata de un libro por ISBN, intentando varias fuentes.

        Intenta Google Books primero; si no hay resultado, recurre a Open Library.

        Args:
            isbn: ISBN-10 o ISBN-13 (con o sin guiones).

        Returns:
            BookMetadata normalizado de la primera fuente disponible.

        Raises:
            InvalidISBNError: Si el ISBN no es válido.
            BookMetadataNotFoundError: Si ninguna fuente tiene datos para el ISBN.
        """
        isbn_13 = normalize_isbn(isbn)

        result = await self._google.fetch(isbn_13)
        if result is not None:
            return result

        result = await self._open_library.fetch(isbn_13)
        if result is not None:
            return result

        logger.warning("book_metadata_not_found", isbn_13=isbn_13)
        raise BookMetadataNotFoundError(f"Libro no encontrado en ninguna fuente: {isbn_13}")

    async def aclose(self) -> None:
        """Cierra todos los clientes HTTP."""
        await self._google.aclose()
        await self._open_library.aclose()
