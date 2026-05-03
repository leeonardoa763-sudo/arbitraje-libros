from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from app.core.exceptions import MarginCalculationError

# Constante para operaciones intermedias con Decimal.
_TWO_PLACES = Decimal("0.01")


def pesos_to_cents(pesos: Decimal | str | int) -> int:
    """Convierte pesos MXN a centavos enteros.

    Redondea al centavo más cercano (ROUND_HALF_UP) para evitar
    truncado silencioso de fracciones de centavo.

    Args:
        pesos: Cantidad en pesos. Acepta Decimal, str o int.

    Returns:
        Equivalente en centavos como int.

    Raises:
        MarginCalculationError: Si el valor no se puede convertir o es negativo.
    """
    try:
        amount = Decimal(str(pesos))
    except Exception as exc:
        raise MarginCalculationError(f"Valor de pesos inválido: {pesos!r}") from exc
    if amount < 0:
        raise MarginCalculationError(f"El monto no puede ser negativo: {pesos!r}")
    cents = (amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(cents)


def cents_to_pesos(cents: int) -> Decimal:
    """Convierte centavos enteros a pesos MXN como Decimal.

    Args:
        cents: Cantidad en centavos. Puede ser negativo (márgenes negativos).

    Returns:
        Equivalente en pesos con exactamente dos decimales.

    Raises:
        MarginCalculationError: Si cents no es un entero.
    """
    if not isinstance(cents, int):
        raise MarginCalculationError(
            f"cents debe ser int, recibido {type(cents).__name__}: {cents!r}"
        )
    return (Decimal(cents) / 100).quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)


def format_mxn(cents: int) -> str:
    """Formatea centavos como string de pesos MXN con separador de miles.

    Ejemplo: 123456 → "$1,234.56 MXN"
             -50000 → "-$500.00 MXN"

    Args:
        cents: Cantidad en centavos. Puede ser negativo.

    Returns:
        String formateado con signo pesos, separadores de miles y sufijo MXN.

    Raises:
        MarginCalculationError: Si cents no es un entero.
    """
    pesos = cents_to_pesos(cents)
    negative = pesos < 0
    abs_pesos = abs(pesos)

    # Separar parte entera y decimal
    parts = f"{abs_pesos:.2f}".split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    # Insertar separador de miles
    formatted_integer = ""
    for i, digit in enumerate(reversed(integer_part)):
        if i > 0 and i % 3 == 0:
            formatted_integer = "," + formatted_integer
        formatted_integer = digit + formatted_integer

    sign = "-" if negative else ""
    return f"{sign}${formatted_integer}.{decimal_part} MXN"


def calculate_margin_pct(net_margin_cents: int, target_price_cents: int) -> Decimal:
    """Calcula el porcentaje de margen neto sobre el precio de venta.

    Args:
        net_margin_cents: Margen neto en centavos (puede ser negativo).
        target_price_cents: Precio de venta objetivo en centavos (> 0).

    Returns:
        Porcentaje de margen con dos decimales (ej. Decimal("23.45")).

    Raises:
        MarginCalculationError: Si target_price_cents es cero o negativo.
    """
    if target_price_cents <= 0:
        raise MarginCalculationError(
            f"target_price_cents debe ser positivo, recibido: {target_price_cents}"
        )
    return (Decimal(net_margin_cents) / Decimal(target_price_cents) * 100).quantize(
        _TWO_PLACES, rounding=ROUND_HALF_UP
    )
