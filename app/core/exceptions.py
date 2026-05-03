from __future__ import annotations


class ArbitrajeError(Exception):
    """Excepción base del proyecto. Todas las excepciones custom heredan de aquí."""


# --- Mercado Libre ---


class MercadoLibreAPIError(ArbitrajeError):
    """Error al llamar a la API oficial de Mercado Libre."""


class MLTokenExpiredError(MercadoLibreAPIError):
    """access_token de ML expirado — se debe hacer refresh."""


class MLTransientError(MercadoLibreAPIError):
    """Error transitorio de ML: rate limit (429) o servidor caído (5xx). Reintentar."""


class MLPermanentError(MercadoLibreAPIError):
    """Error permanente de ML: payload inválido (400), sin permiso (403). No reintentar."""


# --- Libros y metadata ---


class BookMetadataNotFoundError(ArbitrajeError):
    """Metadata del libro no encontrada en Google Books ni Open Library."""


class InvalidISBNError(ArbitrajeError):
    """El string provisto no es un ISBN-10 ni ISBN-13 válido."""


# --- Cálculos de negocio ---


class MarginCalculationError(ArbitrajeError):
    """Error al calcular márgenes (precios negativos, configuración inválida, etc.)."""


# --- Scraping ---


class ScrapingError(ArbitrajeError):
    """Error durante scraping de Mercado Libre."""


# --- Publicaciones ---


class PublicationError(ArbitrajeError):
    """Error al crear o actualizar una publicación en Mercado Libre."""


# --- IA ---


class AIServiceError(ArbitrajeError):
    """Error al llamar al servicio de IA (Anthropic Claude)."""
