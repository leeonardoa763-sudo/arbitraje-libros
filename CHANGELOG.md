# Changelog

Todo cambio notable se documenta aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versiones siguen [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Agregado — Sprint 3: Metadata Service

- `app/services/book_metadata.py`: servicio completo de metadata con `GoogleBooksClient` y `OpenLibraryClient`
- `BookMetadata` dataclass como modelo de transferencia normalizado (agnóstico a la fuente)
- `GoogleBooksClient`: cliente async para la API de Google Books con retry tenacity (3 intentos, backoff exponencial), timeout 10 s, inyección de `api_key` opcional
- `OpenLibraryClient`: cliente async para Open Library (fallback) con misma estrategia de retry
- `BookMetadataService.fetch_by_isbn()`: orquesta Google Books → Open Library, normaliza ISBN-10/13, lanza `BookMetadataNotFoundError` si ambas fuentes fallan
- Clasificación de categoría por keyword-matching (`_classify_category`) contra TECH / MEDICINE / LAW / BUSINESS
- Extracción de año desde formatos de fecha heterogéneos (`_parse_year`)
- 4 fixtures JSON en `tests/fixtures/` (respuestas reales de ambas APIs, casos found/not-found)
- 29 tests unitarios nuevos en `tests/unit/test_book_metadata.py` (cobertura `book_metadata.py`: 94%)

### Agregado — Sprint 2: Core Utilities

- `app/core/isbn.py`: validación ISBN-10/ISBN-13 con checksum, conversión bidireccional, normalización a ISBN-13 canónico y extracción de ISBNs desde texto libre con regex
- `app/core/money.py`: helpers de centavos — `pesos_to_cents`, `cents_to_pesos`, `format_mxn` (formato `$1,234.56 MXN`), `calculate_margin_pct`
- 100 tests nuevos en `tests/unit/test_isbn.py`, `tests/unit/test_money.py`, `tests/unit/test_exceptions.py` (162 total)
- Regla de redondeo ROUND_HALF_UP en `pesos_to_cents` para evitar truncado silencioso

### Agregado — Sprint 1: Modelos y Schemas

- Modelos SQLAlchemy 2.0 async: `Book`, `Opportunity`, `Publication`, `PriceHistory`
- Enums de dominio: `BookCategory`, `MetadataSource`, `OpportunityStatus`, `PublicationStatus`, `Platform`
- Constraint de deduplicación `uq_opportunity_dedup` en `Opportunity` (book_id + source_url + source_price_cents)
- Schemas Pydantic v2: `BookCreate/Read/Update`, `OpportunityCreate/Read/StatusUpdate/AIUpdate`, `PublicationCreate/Read/StatusUpdate`
- Validación de ISBN-13 (13 dígitos), ISBN-10 (10 chars con posible X final), ai_score (0-100), precios no negativos
- `alembic/env.py` actualizado para registrar todos los modelos en `Base.metadata`
- 50+ tests unitarios para modelos (enums, instanciación, constraints) y schemas (validación de campos)

### Agregado — Sprint 0: Fundación

- FastAPI con endpoints `/health` y `/version`
- HTTP Basic Auth (usuario único: Leo)
- Pydantic Settings con validación estricta de variables de entorno
- structlog para logging estructurado (JSON en producción, consola en dev)
- SQLAlchemy 2.0 async con PostgreSQL 16 + Alembic
- Docker + docker-compose (app + postgres)
- GitHub Actions CI: lint (ruff), typecheck (mypy strict), tests (pytest), security (gitleaks), PR size check
- Pre-commit hooks: ruff + mypy + gitleaks
- Jerarquía de excepciones custom del dominio en `app/core/exceptions.py`
- Estructura completa de módulos (stubs para sprints futuros)
- ADR 0001: Stack técnico inicial
- Skills custom: `isbn-handling`, `ml-commissions`, `ml-api`
- Documentación: deployment, runbook, ml_api_setup
