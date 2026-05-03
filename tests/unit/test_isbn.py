from __future__ import annotations

import pytest

from app.core.exceptions import InvalidISBNError
from app.core.isbn import (
    extract_isbns,
    is_valid_isbn10,
    is_valid_isbn13,
    isbn10_to_isbn13,
    isbn13_to_isbn10,
    normalize_isbn,
)

# ---------------------------------------------------------------------------
# is_valid_isbn10
# ---------------------------------------------------------------------------


class TestIsValidIsbn10:
    def test_valid_numeric_check_digit(self) -> None:
        assert is_valid_isbn10("0306406152") is True

    def test_valid_with_x_check_digit(self) -> None:
        # 020161622X: suma=100, (100+10)%11=0 ✓
        assert is_valid_isbn10("020161622X") is True

    def test_valid_with_hyphens(self) -> None:
        assert is_valid_isbn10("0-306-40615-2") is True

    def test_valid_with_spaces(self) -> None:
        assert is_valid_isbn10("0 306 40615 2") is True

    def test_invalid_wrong_checksum(self) -> None:
        assert is_valid_isbn10("0306406153") is False

    def test_invalid_too_short(self) -> None:
        assert is_valid_isbn10("030640615") is False

    def test_invalid_too_long(self) -> None:
        assert is_valid_isbn10("03064061520") is False

    def test_invalid_x_in_middle(self) -> None:
        assert is_valid_isbn10("030X406152") is False

    def test_invalid_empty(self) -> None:
        assert is_valid_isbn10("") is False

    def test_lowercase_x_accepted(self) -> None:
        # La función debe normalizar a mayúsculas antes de validar
        assert is_valid_isbn10("020161622x") is True


# ---------------------------------------------------------------------------
# is_valid_isbn13
# ---------------------------------------------------------------------------


class TestIsValidIsbn13:
    def test_valid_978_prefix(self) -> None:
        assert is_valid_isbn13("9780306406157") is True

    def test_valid_979_prefix(self) -> None:
        # 979-10-90636-07-1 — editorial francesa
        assert is_valid_isbn13("9791090636071") is True

    def test_valid_with_hyphens(self) -> None:
        assert is_valid_isbn13("978-0-306-40615-7") is True

    def test_invalid_wrong_checksum(self) -> None:
        assert is_valid_isbn13("9780306406158") is False

    def test_invalid_prefix_000(self) -> None:
        assert is_valid_isbn13("0000000000000") is False

    def test_invalid_too_short(self) -> None:
        assert is_valid_isbn13("978030640615") is False

    def test_invalid_non_digit(self) -> None:
        assert is_valid_isbn13("978030640615X") is False

    def test_invalid_empty(self) -> None:
        assert is_valid_isbn13("") is False


# ---------------------------------------------------------------------------
# isbn10_to_isbn13
# ---------------------------------------------------------------------------


class TestIsbn10ToIsbn13:
    def test_basic_conversion(self) -> None:
        assert isbn10_to_isbn13("0306406152") == "9780306406157"

    def test_with_x_check_digit(self) -> None:
        result = isbn10_to_isbn13("020161622X")
        assert is_valid_isbn13(result)
        assert result.startswith("978")

    def test_with_hyphens(self) -> None:
        assert isbn10_to_isbn13("0-306-40615-2") == "9780306406157"

    def test_invalid_isbn10_raises(self) -> None:
        # Checksum correcto para esta base es 2, no 3
        with pytest.raises(InvalidISBNError, match="ISBN-10 inválido"):
            isbn10_to_isbn13("0306406153")

    def test_round_trip(self) -> None:
        """ISBN-10 → ISBN-13 → ISBN-10 debe producir el original."""
        original = "0306406152"
        isbn13 = isbn10_to_isbn13(original)
        recovered = isbn13_to_isbn10(isbn13)
        assert recovered == original


# ---------------------------------------------------------------------------
# isbn13_to_isbn10
# ---------------------------------------------------------------------------


class TestIsbn13ToIsbn10:
    def test_basic_conversion(self) -> None:
        assert isbn13_to_isbn10("9780306406157") == "0306406152"

    def test_979_prefix_returns_none(self) -> None:
        # ISBN-13 con prefijo 979 no tiene equivalente ISBN-10
        assert isbn13_to_isbn10("9791090636071") is None

    def test_with_hyphens(self) -> None:
        result = isbn13_to_isbn10("978-0-306-40615-7")
        assert result == "0306406152"

    def test_invalid_isbn13_raises(self) -> None:
        with pytest.raises(InvalidISBNError, match="ISBN-13 inválido"):
            isbn13_to_isbn10("9780000000000")

    def test_result_is_valid_isbn10(self) -> None:
        result = isbn13_to_isbn10("9780306406157")
        assert result is not None
        assert is_valid_isbn10(result)


# ---------------------------------------------------------------------------
# normalize_isbn
# ---------------------------------------------------------------------------


class TestNormalizeIsbn:
    def test_isbn13_passthrough(self) -> None:
        assert normalize_isbn("9780306406157") == "9780306406157"

    def test_isbn10_converted_to_isbn13(self) -> None:
        assert normalize_isbn("0306406152") == "9780306406157"

    def test_strips_hyphens(self) -> None:
        assert normalize_isbn("978-0-306-40615-7") == "9780306406157"

    def test_strips_spaces(self) -> None:
        assert normalize_isbn("978 0 306 40615 7") == "9780306406157"

    def test_isbn10_with_hyphens(self) -> None:
        assert normalize_isbn("0-306-40615-2") == "9780306406157"

    def test_empty_string_raises(self) -> None:
        with pytest.raises(InvalidISBNError, match="vacío"):
            normalize_isbn("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(InvalidISBNError, match="vacío"):
            normalize_isbn("   ")

    def test_invalid_string_raises(self) -> None:
        with pytest.raises(InvalidISBNError, match="inválido"):
            normalize_isbn("1234567890")

    def test_arbitrary_text_raises(self) -> None:
        with pytest.raises(InvalidISBNError):
            normalize_isbn("no es isbn")

    def test_979_prefix_isbn13(self) -> None:
        result = normalize_isbn("9791090636071")
        assert result == "9791090636071"


# ---------------------------------------------------------------------------
# extract_isbns
# ---------------------------------------------------------------------------


class TestExtractIsbns:
    def test_extracts_isbn13_from_text(self) -> None:
        text = "Libro excelente ISBN 9780306406157 en buen estado"
        assert extract_isbns(text) == ["9780306406157"]

    def test_extracts_isbn10_and_converts(self) -> None:
        text = "Código del libro: 0306406152"
        assert extract_isbns(text) == ["9780306406157"]

    def test_extracts_multiple_isbns(self) -> None:
        text = "9780306406157 y también 9791090636071"
        result = extract_isbns(text)
        assert "9780306406157" in result
        assert "9791090636071" in result
        assert len(result) == 2

    def test_deduplicates_same_isbn(self) -> None:
        text = "9780306406157 y otra vez 978-0-306-40615-7"
        assert extract_isbns(text) == ["9780306406157"]

    def test_ignores_invalid_candidates(self) -> None:
        text = "El número 9999999999999 no es ISBN válido"
        assert extract_isbns(text) == []

    def test_empty_text_returns_empty_list(self) -> None:
        assert extract_isbns("") == []

    def test_text_without_isbn_returns_empty_list(self) -> None:
        assert extract_isbns("Libro de matemáticas, sin código") == []

    def test_isbn_with_label_prefix(self) -> None:
        text = "ISBN-13: 978-0-306-40615-7"
        assert extract_isbns(text) == ["9780306406157"]

    def test_isbn10_with_x(self) -> None:
        text = "Referencia: ISBN 020161622X"
        result = extract_isbns(text)
        assert len(result) == 1
        assert is_valid_isbn13(result[0])
