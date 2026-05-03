---
name: isbn-handling
description: Use this skill when working with ISBNs in any form — validating, normalizing, converting between ISBN-10 and ISBN-13, extracting ISBNs from raw text (titles, descriptions, scraped content), or building ISBN-related database queries. Triggers include any code touching app/core/isbn.py, fields named isbn_10 or isbn_13, parsing book titles or descriptions for identifiers, or when matching books across data sources (Google Books, Open Library, ML scraped content). Provides validation algorithms, conversion formulas, regex patterns, and common pitfalls.
---

# ISBN — Validación, Conversión y Extracción

## Conceptos clave

### ISBN-10 (legacy, libros pre-2007)
- 10 dígitos. El último puede ser `X` (representa 10 en el checksum).
- Formato común: `0-306-40615-2` o `0306406152`.

### ISBN-13 (estándar moderno)
- 13 dígitos. Empieza con `978` o `979`.
- Compatible con código de barras EAN-13.
- Formato común: `978-0-306-40615-7` o `9780306406157`.

### Regla canónica del proyecto
**ISBN-13 es la clave.** Siempre convertir ISBN-10 → ISBN-13 al guardar en BD.
Mantener `isbn_10` como columna opcional para referencia.

## Algoritmos

### Validación de ISBN-10 (checksum)

```python
def is_valid_isbn10(isbn: str) -> bool:
    """Valida ISBN-10 con su checksum."""
    isbn = isbn.replace("-", "").replace(" ", "").upper()
    if len(isbn) != 10:
        return False
    if not isbn[:9].isdigit():
        return False
    if not (isbn[9].isdigit() or isbn[9] == "X"):
        return False
    total = sum(int(d) * (10 - i) for i, d in enumerate(isbn[:9]))
    check = 10 if isbn[9] == "X" else int(isbn[9])
    return (total + check) % 11 == 0
```

### Validación de ISBN-13 (checksum EAN)

```python
def is_valid_isbn13(isbn: str) -> bool:
    """Valida ISBN-13 con checksum EAN-13."""
    isbn = isbn.replace("-", "").replace(" ", "")
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    if not (isbn.startswith("978") or isbn.startswith("979")):
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(isbn[:12]))
    check = (10 - (total % 10)) % 10
    return check == int(isbn[12])
```

### Conversión ISBN-10 → ISBN-13

```python
def isbn10_to_isbn13(isbn10: str) -> str:
    """Convierte ISBN-10 a ISBN-13. Asume ISBN-10 válido."""
    isbn10 = isbn10.replace("-", "").replace(" ", "").upper()
    base = "978" + isbn10[:9]
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(base))
    check = (10 - (total % 10)) % 10
    return base + str(check)
```

### Conversión ISBN-13 → ISBN-10 (solo si empieza con 978)

```python
def isbn13_to_isbn10(isbn13: str) -> str | None:
    """Convierte ISBN-13 a ISBN-10. Retorna None si empieza con 979 (no convertible)."""
    isbn13 = isbn13.replace("-", "").replace(" ", "")
    if not isbn13.startswith("978"):
        return None
    base = isbn13[3:12]
    total = sum(int(d) * (10 - i) for i, d in enumerate(base))
    check_num = (11 - (total % 11)) % 11
    check = "X" if check_num == 10 else str(check_num)
    return base + check
```

### Normalización (input → ISBN-13 limpio)

```python
def normalize_isbn(raw: str) -> str:
    """Toma ISBN en cualquier formato y devuelve ISBN-13 sin guiones.

    Raises:
        InvalidISBNError: si no es un ISBN válido.
    """
    cleaned = raw.replace("-", "").replace(" ", "").upper()
    if is_valid_isbn13(cleaned):
        return cleaned
    if is_valid_isbn10(cleaned):
        return isbn10_to_isbn13(cleaned)
    raise InvalidISBNError(f"ISBN inválido: {raw}")
```

## Extracción desde texto (scraping)

### Regex robusto

```python
ISBN_PATTERN = re.compile(
    r"""(?ix)                              # ignore case + verbose
    (?:ISBN[-\s]?(?:1[03])?[:\s-]*)?       # opcional prefijo "ISBN", "ISBN-13:", etc.
    (
        97[89][-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?\d   # ISBN-13
        |
        \d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?[\dXx]            # ISBN-10
    )
    """
)

def extract_isbns(text: str) -> list[str]:
    """Extrae todos los ISBN válidos de un texto. Útil para parsing de descripciones de ML."""
    candidates = ISBN_PATTERN.findall(text)
    valid = []
    for c in candidates:
        try:
            valid.append(normalize_isbn(c))
        except InvalidISBNError:
            continue
    return list(set(valid))  # dedup
```

### Estrategia de extracción en ML (en orden de prioridad)

1. **Título:** muchos vendedores lo incluyen ("Libro X — ISBN 978...").
2. **Descripción del item:** segundo lugar más común.
3. **Imágenes de la portada/contraportada:** OCR si llegamos a necesitarlo (futuro).
4. **Atributos estructurados:** ML a veces tiene `attributes` con `id="ISBN"`.

## Errores comunes a evitar

1. **No validar checksum.** Hay strings de 13 dígitos que no son ISBN válidos.
2. **No remover guiones/espacios** antes de validar.
3. **Asumir que ISBN es siempre numérico.** ISBN-10 puede terminar en `X`.
4. **Confundir EAN-13 de productos generales con ISBN-13.** Solo `978`/`979` son libros.
5. **Perder ceros a la izquierda** convirtiendo a `int`. Mantener siempre como `str`.

## Tests obligatorios

Para `app/core/isbn.py`, los tests deben cubrir:

- ✅ ISBN-10 válido con dígito final numérico
- ✅ ISBN-10 válido con dígito final `X`
- ✅ ISBN-10 inválido (checksum incorrecto)
- ✅ ISBN-13 válido con prefijo `978`
- ✅ ISBN-13 válido con prefijo `979`
- ✅ ISBN-13 inválido (prefijo incorrecto)
- ✅ Conversión ISBN-10 → ISBN-13 round-trip
- ✅ ISBN-13 con prefijo `979` no se puede convertir a ISBN-10
- ✅ Normalización con guiones/espacios
- ✅ Normalización con string vacío → error
- ✅ Extracción de múltiples ISBNs en un mismo texto
- ✅ Extracción ignora candidatos inválidos
- ✅ Texto sin ISBN → lista vacía

## Referencias

- [ISO 2108 (estándar ISBN)](https://www.iso.org/standard/65483.html)
- [Wikipedia: International Standard Book Number](https://en.wikipedia.org/wiki/ISBN)
