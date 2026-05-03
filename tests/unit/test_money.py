from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.exceptions import MarginCalculationError
from app.core.money import (
    calculate_margin_pct,
    cents_to_pesos,
    format_mxn,
    pesos_to_cents,
)

# ---------------------------------------------------------------------------
# pesos_to_cents
# ---------------------------------------------------------------------------


class TestPesosToCents:
    def test_integer_pesos(self) -> None:
        assert pesos_to_cents(10) == 1000

    def test_decimal_pesos(self) -> None:
        assert pesos_to_cents(Decimal("12.50")) == 1250

    def test_string_pesos(self) -> None:
        assert pesos_to_cents("99.99") == 9999

    def test_zero(self) -> None:
        assert pesos_to_cents(0) == 0

    def test_rounding_half_up(self) -> None:
        # 10.005 → 1000.5 centavos → redondea a 1001
        assert pesos_to_cents("10.005") == 1001

    def test_rounding_down(self) -> None:
        # 10.004 → 1000.4 centavos → redondea a 1000
        assert pesos_to_cents("10.004") == 1000

    def test_large_amount(self) -> None:
        assert pesos_to_cents(1_000_000) == 100_000_000

    def test_negative_raises(self) -> None:
        with pytest.raises(MarginCalculationError, match="negativo"):
            pesos_to_cents(-1)

    def test_negative_decimal_raises(self) -> None:
        with pytest.raises(MarginCalculationError, match="negativo"):
            pesos_to_cents(Decimal("-0.01"))

    def test_invalid_string_raises(self) -> None:
        with pytest.raises(MarginCalculationError, match="inválido"):
            pesos_to_cents("no es un número")  # type: ignore[arg-type]

    def test_decimal_string_with_only_cents(self) -> None:
        assert pesos_to_cents("0.99") == 99


# ---------------------------------------------------------------------------
# cents_to_pesos
# ---------------------------------------------------------------------------


class TestCentsToPesos:
    def test_basic(self) -> None:
        assert cents_to_pesos(1000) == Decimal("10.00")

    def test_zero(self) -> None:
        assert cents_to_pesos(0) == Decimal("0.00")

    def test_negative_cents(self) -> None:
        # Márgenes negativos son válidos
        assert cents_to_pesos(-500) == Decimal("-5.00")

    def test_returns_decimal(self) -> None:
        result = cents_to_pesos(123)
        assert isinstance(result, Decimal)

    def test_two_decimal_places(self) -> None:
        result = cents_to_pesos(1)
        assert result == Decimal("0.01")

    def test_large_amount(self) -> None:
        assert cents_to_pesos(100_000_000) == Decimal("1000000.00")

    def test_float_raises(self) -> None:
        with pytest.raises(MarginCalculationError, match="debe ser int"):
            cents_to_pesos(10.5)  # type: ignore[arg-type]

    def test_string_raises(self) -> None:
        with pytest.raises(MarginCalculationError, match="debe ser int"):
            cents_to_pesos("100")  # type: ignore[arg-type]

    def test_round_trip_with_pesos_to_cents(self) -> None:
        original = Decimal("123.45")
        assert cents_to_pesos(pesos_to_cents(original)) == original


# ---------------------------------------------------------------------------
# format_mxn
# ---------------------------------------------------------------------------


class TestFormatMxn:
    def test_basic_format(self) -> None:
        assert format_mxn(123456) == "$1,234.56 MXN"

    def test_zero(self) -> None:
        assert format_mxn(0) == "$0.00 MXN"

    def test_cents_only(self) -> None:
        assert format_mxn(99) == "$0.99 MXN"

    def test_negative_amount(self) -> None:
        assert format_mxn(-50000) == "-$500.00 MXN"

    def test_thousands_separator(self) -> None:
        assert format_mxn(1_000_000_00) == "$1,000,000.00 MXN"

    def test_exact_pesos_no_cents(self) -> None:
        assert format_mxn(10000) == "$100.00 MXN"

    def test_small_amount(self) -> None:
        assert format_mxn(1) == "$0.01 MXN"

    def test_negative_large(self) -> None:
        assert format_mxn(-1_234_567) == "-$12,345.67 MXN"

    def test_float_raises(self) -> None:
        with pytest.raises(MarginCalculationError):
            format_mxn(100.5)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# calculate_margin_pct
# ---------------------------------------------------------------------------


class TestCalculateMarginPct:
    def test_basic_margin(self) -> None:
        # 25 de 100 = 25%
        assert calculate_margin_pct(25_00, 100_00) == Decimal("25.00")

    def test_negative_margin(self) -> None:
        # Pérdida
        result = calculate_margin_pct(-10_00, 100_00)
        assert result == Decimal("-10.00")

    def test_zero_margin(self) -> None:
        assert calculate_margin_pct(0, 100_00) == Decimal("0.00")

    def test_fractional_result(self) -> None:
        # 1/3 de 300 ≈ 33.33%
        result = calculate_margin_pct(100_00, 300_00)
        assert result == Decimal("33.33")

    def test_zero_target_raises(self) -> None:
        with pytest.raises(MarginCalculationError, match="positivo"):
            calculate_margin_pct(100, 0)

    def test_negative_target_raises(self) -> None:
        with pytest.raises(MarginCalculationError, match="positivo"):
            calculate_margin_pct(100, -1)

    def test_returns_decimal(self) -> None:
        result = calculate_margin_pct(500, 2000)
        assert isinstance(result, Decimal)

    def test_100_pct_margin(self) -> None:
        # Vender al doble del costo, margen sobre precio = 50%
        assert calculate_margin_pct(50_00, 100_00) == Decimal("50.00")

    def test_realistic_book_margin(self) -> None:
        # Compro en $150, vendo en $350, comisión $50, envío $30 → margen = $120 / $350 ≈ 34.29%
        result = calculate_margin_pct(120_00, 350_00)
        assert result == Decimal("34.29")
