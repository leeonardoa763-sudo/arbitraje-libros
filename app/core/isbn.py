from __future__ import annotations

import re

from app.core.exceptions import InvalidISBNError

# Patrón para extraer candidatos ISBN de texto libre.
# Acepta ISBN-13 (978/979) e ISBN-10 con separadores opcionales.
ISBN_PATTERN = re.compile(
    r"""(?ix)
    (?:ISBN[-\s]?(?:1[03])?[:\s-]*)?
    (
        97[89][-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?\d
        |
        \d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?[\dXx]
    )
    """
)


def is_valid_isbn10(isbn: str) -> bool:
    """Valida un ISBN-10 usando su checksum módulo 11.

    Args:
        isbn: String con el ISBN-10 (con o sin guiones/espacios).

    Returns:
        True si el checksum es válido.
    """
    cleaned = isbn.replace("-", "").replace(" ", "").upper()
    if len(cleaned) != 10:
        return False
    if not cleaned[:9].isdigit():
        return False
    if not (cleaned[9].isdigit() or cleaned[9] == "X"):
        return False
    total = sum(int(d) * (10 - i) for i, d in enumerate(cleaned[:9]))
    check = 10 if cleaned[9] == "X" else int(cleaned[9])
    return (total + check) % 11 == 0


def is_valid_isbn13(isbn: str) -> bool:
    """Valida un ISBN-13 usando su checksum EAN-13.

    Args:
        isbn: String con el ISBN-13 (con o sin guiones/espacios).

    Returns:
        True si el checksum es válido y el prefijo es 978 o 979.
    """
    cleaned = isbn.replace("-", "").replace(" ", "")
    if len(cleaned) != 13 or not cleaned.isdigit():
        return False
    if not (cleaned.startswith("978") or cleaned.startswith("979")):
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(cleaned[:12]))
    check = (10 - (total % 10)) % 10
    return check == int(cleaned[12])


def isbn10_to_isbn13(isbn10: str) -> str:
    """Convierte un ISBN-10 válido a ISBN-13.

    Args:
        isbn10: ISBN-10 válido (con o sin guiones/espacios).

    Returns:
        ISBN-13 sin guiones como string de 13 dígitos.

    Raises:
        InvalidISBNError: Si el ISBN-10 no es válido.
    """
    cleaned = isbn10.replace("-", "").replace(" ", "").upper()
    if not is_valid_isbn10(cleaned):
        raise InvalidISBNError(f"ISBN-10 inválido: {isbn10}")
    base = "978" + cleaned[:9]
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(base))
    check = (10 - (total % 10)) % 10
    return base + str(check)


def isbn13_to_isbn10(isbn13: str) -> str | None:
    """Convierte un ISBN-13 a ISBN-10.

    Solo es posible para ISBN-13 con prefijo 978. Los prefijos 979 no tienen
    equivalente en ISBN-10.

    Args:
        isbn13: ISBN-13 válido (con o sin guiones/espacios).

    Returns:
        ISBN-10 sin guiones, o None si el prefijo es 979.

    Raises:
        InvalidISBNError: Si el ISBN-13 no es válido.
    """
    cleaned = isbn13.replace("-", "").replace(" ", "")
    if not is_valid_isbn13(cleaned):
        raise InvalidISBNError(f"ISBN-13 inválido: {isbn13}")
    if not cleaned.startswith("978"):
        return None
    base = cleaned[3:12]
    total = sum(int(d) * (10 - i) for i, d in enumerate(base))
    check_num = (11 - (total % 11)) % 11
    check = "X" if check_num == 10 else str(check_num)
    return base + check


def normalize_isbn(raw: str) -> str:
    """Normaliza cualquier ISBN a ISBN-13 canónico sin guiones.

    Acepta ISBN-10 o ISBN-13 con o sin guiones/espacios. Convierte ISBN-10
    a ISBN-13 automáticamente.

    Args:
        raw: String con el ISBN en cualquier formato.

    Returns:
        ISBN-13 como string de 13 dígitos sin guiones.

    Raises:
        InvalidISBNError: Si el string no es un ISBN válido.
    """
    if not raw or not raw.strip():
        raise InvalidISBNError("ISBN vacío")
    cleaned = raw.replace("-", "").replace(" ", "").upper()
    if is_valid_isbn13(cleaned):
        return cleaned
    if is_valid_isbn10(cleaned):
        return isbn10_to_isbn13(cleaned)
    raise InvalidISBNError(f"ISBN inválido: {raw!r}")


def extract_isbns(text: str) -> list[str]:
    """Extrae todos los ISBN válidos de un texto libre.

    Útil para parsear títulos y descripciones de listados de Mercado Libre.
    Los duplicados se eliminan; el orden no está garantizado.

    Args:
        text: Texto libre que puede contener uno o más ISBNs.

    Returns:
        Lista de ISBN-13 únicos encontrados en el texto.
    """
    candidates = ISBN_PATTERN.findall(text)
    valid: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        try:
            isbn13 = normalize_isbn(candidate)
        except InvalidISBNError:
            continue
        if isbn13 not in seen:
            seen.add(isbn13)
            valid.append(isbn13)
    return valid
