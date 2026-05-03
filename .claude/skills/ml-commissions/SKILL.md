---
name: ml-commissions
description: Use this skill whenever calculating margins, commissions, shipping costs, or fees for Mercado Libre Mexico publications. Triggers include any code in app/services/margin_calculator.py, app/services/ml_commissions.py, modeling sales economics, or when a task mentions "comisión ML", "Mercado Envíos", "modalidad Clásica/Premium", or "IVA en envío". Provides up-to-date commission tables for MLM (Mercado Libre Mexico) book category, shipping cost rules, IVA application, and frontier zone surcharges.
---

# Mercado Libre México — Comisiones y Costos

> **Esta información cambia.** Si detectas discrepancia con la realidad, avisa a Leo y actualiza esta skill.
> **Última verificación:** Sprint 0. Verificar contra https://www.mercadolibre.com.mx/vender al menos cada 3 meses.

## Categoría: Libros (MLM > Libros, Música y Películas > Libros)

### Comisión por modalidad

Para venta de libros (categoría `MLM1132`):

| Modalidad | Comisión sobre precio venta | Notas |
|-----------|------------------------------|-------|
| Clásica   | ~13% | Sin envío gratis garantizado |
| Premium   | ~16% | Mejor exposición + meses sin intereses + envío gratis para >$299 |

**Cargo fijo adicional:** $0–$50 MXN dependiendo del precio del producto:
- Producto < $299: cargo fijo de ~$50
- Producto ≥ $299: solo el porcentaje

> **Implementación:** parametrizar en BD o config, no hardcodear. Estructura sugerida:
> ```python
> {
>     "MLM1132": {
>         "classic": {"pct": 0.13, "fixed_below_threshold": 5000, "threshold_cents": 29900},
>         "premium": {"pct": 0.16, "fixed_below_threshold": 5000, "threshold_cents": 29900},
>     }
> }
> ```

## Mercado Envíos (envío)

### Quién paga el envío
- **Producto < $299 MXN:** comprador paga el envío.
- **Producto ≥ $299 MXN en modalidad Premium:** vendedor paga (descuento parcial según reputación).

### Costo aproximado para libros (peso típico 0.5-1 kg)

| Reputación vendedor | Subsidio ML | Costo aprox al vendedor (libro 0.7kg) |
|---------------------|-------------|----------------------------------------|
| Verde / Líder       | Alto        | $40–$60 MXN |
| Amarillo            | Medio       | $70–$100 MXN |
| Rojo / Sin reputación | Nulo      | $90–$140 MXN (precio completo) |

**Frontera (Tijuana, Mexicali, Cd. Juárez, etc.):** sumar ~$30 MXN al costo base.

### Heurística para estimación (cuando no tenemos datos exactos)

```python
def estimate_shipping_cents(
    weight_grams: int = 700,
    is_frontier: bool = False,
    seller_reputation: str = "green",
    item_price_cents: int = 0,
) -> int:
    """Estimación conservadora (sobre-estima un poco para no engañarnos)."""
    base = {"green": 5500, "yellow": 8500, "red": 12000}[seller_reputation]
    if weight_grams > 1000:
        base += 2000
    if is_frontier:
        base += 3000
    if item_price_cents < 29900:
        return 0  # comprador paga
    return base
```

## IVA (Impuesto al Valor Agregado)

- **Tasa:** 16% en general; 8% en zona fronteriza norte (estímulo fiscal).
- **Sobre qué se aplica:** ML retiene IVA por la **comisión** que cobra (no sobre el precio del libro).
  - Si comisión = $50, ML retiene $50 * 16% = $8 adicional.
- **Para vendedores con RFC registrado en ML:** la retención del IVA es total.
- **Para vendedores sin RFC:** retención del 16% adicional sobre comisión + ISR del 1% sobre venta.

### Implementación

```python
def calculate_iva_on_commission(
    commission_cents: int,
    is_frontier_seller: bool = False,
) -> int:
    rate = 0.08 if is_frontier_seller else 0.16
    return int(commission_cents * rate)
```

## ISR (Impuesto Sobre la Renta) — solo personas físicas sin RFC

- ML retiene 1% sobre el precio de venta cuando el vendedor no tiene RFC registrado.
- **Para Leo:** registrar RFC en su perfil de ML para evitar esta retención.

## Fórmula completa de margen neto

```python
def net_margin_cents(
    target_price_cents: int,        # precio que pondremos
    source_price_cents: int,         # precio al que compramos
    commission_pct: float,            # 0.13 o 0.16
    fixed_fee_cents: int,             # cargo fijo si aplica
    shipping_cents: int,              # subsidio que pagamos al enviar
    iva_on_commission_cents: int,
    isr_cents: int = 0,               # solo si no hay RFC
) -> int:
    """Devuelve margen neto en centavos. Puede ser negativo."""
    commission = int(target_price_cents * commission_pct) + fixed_fee_cents
    total_costs = source_price_cents + commission + shipping_cents + iva_on_commission_cents + isr_cents
    return target_price_cents - total_costs
```

## Casos límite a considerar en tests

1. **Precio < $299:** cargo fijo aplica, comprador paga envío.
2. **Precio = $299 exacto:** límite del cargo fijo.
3. **Precio = $0:** debe lanzar `ValueError`.
4. **Precio negativo:** debe lanzar `ValueError`.
5. **Vendedor en frontera:** IVA 8%.
6. **Sin RFC:** sumar 1% ISR.
7. **Reputación roja:** envío costoso.
8. **Modalidad Premium con producto ≥ $299:** envío subsidiado parcialmente.

## Referencias oficiales

- [Comisiones por categoría — ML México](https://www.mercadolibre.com.mx/ayuda/comisiones-y-tarifas_1416)
- [Mercado Envíos — Tarifas](https://www.mercadolibre.com.mx/ayuda/mercado-envios_1448)
- [Ayuda fiscal — RFC y retenciones](https://www.mercadolibre.com.mx/ayuda/datos-fiscales_8979)
