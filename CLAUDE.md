# CLAUDE.md

> **Lee este archivo COMPLETO al inicio de cada sesión.** Define cómo trabajamos en este proyecto.
> El programador eres tú (Claude Code). El supervisor es Leo. Tu trabajo es entregar código que pase CI y que Leo pueda revisar en PRs pequeños.

---

## 🎯 Mission Statement

Aplicación web personal para detectar libros usados subvalorados en **Mercado Libre México**, calcular márgenes netos reales (comisiones + envío + IVA) y publicarlos automáticamente en mi cuenta de vendedor.

**Usuario único:** Leo (el dueño). No hay multi-tenant.
**Modo de operación:** scraping cada N horas → enriquecimiento con metadata + IA → dashboard de oportunidades → publicación con un clic en ML.

---

## 🚫 Out of Scope (NO intentes implementar esto)

- Ropa, sneakers, otras categorías que no sean libros
- Multi-marketplace (solo ML por ahora; no Amazon, no Linio, no Shopee)
- Multi-usuario, registro, recuperación de contraseña
- Análisis de imágenes con IA
- Mobile app nativa
- Notificaciones push, email marketing
- Pasarela de pago propia (ML maneja eso)

Si Leo pide algo de esta lista, **detente y confirma** antes de implementarlo.

---

## ✅ Architectural Decisions (CERRADAS — no debatir sin pedir permiso)

Estas decisiones ya se tomaron. **No propongas cambiarlas a menos que Leo lo pida explícitamente.** Si una nueva tarea entra en conflicto con una decisión, detente y pregunta.

| Decisión | Elegido | Por qué |
|----------|---------|---------|
| Lenguaje | Python 3.12+ | Estándar moderno |
| Web framework | FastAPI | Async nativo, validación con Pydantic, OpenAPI |
| ORM | SQLAlchemy 2.0 **async** | Eficiencia para scraping concurrente |
| BD | PostgreSQL 16+ | Robusto, gratis en Railway |
| Migraciones | Alembic | Estándar con SQLAlchemy |
| Validación | Pydantic v2 | Estricto, rápido |
| Templates | Jinja2 + HTMX + Tailwind | Sin SPA, dashboard interno |
| Tareas programadas | APScheduler embebido | No necesitamos Celery para 1 usuario |
| HTTP client | httpx async | Moderno |
| Scraping | httpx + selectolax (más rápido que BS4) | Performance |
| IA | Anthropic Claude API | `claude-sonnet-4-6` por default |
| Auth | HTTP Basic + secret en `.env` | 1 usuario, máxima simplicidad |
| Logging | structlog (JSON) | Logs parseables, observable |
| Gestor de paquetes | **uv** | 10-100x más rápido que pip |
| Lint + format | **ruff** | Reemplaza black + flake8 + isort |
| Type checker | **mypy strict mode** | Catch errors temprano |
| Testing | pytest + pytest-asyncio + coverage | Estándar |
| Pre-commit | pre-commit + ruff + mypy | No commitear basura |
| CI/CD | GitHub Actions | Gratis, integrado |
| Containerización | Docker + docker-compose | Reproducibilidad |
| Deploy | Railway | Gratis, soporta BD + scheduler |
| Versionado | Conventional Commits | Changelog automático |

### Decisiones específicas del dominio

- **ISBN-13 es la clave canónica** de un libro. Siempre normalizar ISBN-10 → ISBN-13.
- **Precios en centavos (`int`)**, nunca floats. Evita errores de redondeo.
- **Timezone:** todo en UTC en BD. Convertir a `America/Mexico_City` solo en presentación.
- **Idempotencia:** los scrapers deben poder correr 100 veces sin duplicar oportunidades. Usar `(book_id, source_url, source_price)` como llave de deduplicación.

---

## 📁 Estructura del proyecto

```
arbitraje-libros/
├── app/
│   ├── __init__.py
│   ├── main.py                       # Entry point FastAPI + scheduler lifespan
│   ├── config.py                     # Settings con Pydantic BaseSettings
│   ├── database.py                   # Async engine + session factory
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                   # Auth, get_db, etc.
│   │   ├── dashboard.py              # Routes que sirven HTML
│   │   └── v1/                       # API JSON versionada
│   │       ├── __init__.py
│   │       ├── opportunities.py
│   │       ├── books.py
│   │       └── publications.py
│   │
│   ├── core/
│   │   ├── auth.py                   # HTTP Basic
│   │   ├── logging_config.py         # structlog setup
│   │   ├── isbn.py                   # Validación, ISBN-10 ↔ ISBN-13
│   │   ├── exceptions.py             # Excepciones custom del dominio
│   │   └── money.py                  # Helpers para manejo de centavos
│   │
│   ├── models/                       # SQLAlchemy (tablas)
│   │   ├── base.py                   # DeclarativeBase + mixins
│   │   ├── book.py
│   │   ├── opportunity.py
│   │   ├── publication.py
│   │   └── price_history.py
│   │
│   ├── schemas/                      # Pydantic (I/O)
│   │   ├── book.py
│   │   ├── opportunity.py
│   │   └── publication.py
│   │
│   ├── services/                     # Lógica de negocio
│   │   ├── margin_calculator.py
│   │   ├── book_metadata.py          # Google Books + Open Library
│   │   ├── ml_commissions.py         # Tabla parametrizada
│   │   ├── opportunity_finder.py     # Orquesta todo
│   │   ├── ml_publisher.py           # API oficial de ML
│   │   └── ai/
│   │       ├── client.py
│   │       ├── opportunity_evaluator.py
│   │       ├── listing_generator.py
│   │       └── prompts.py            # Prompts versionados como constantes
│   │
│   ├── scrapers/
│   │   ├── base.py                   # Cliente con rate limit + UA rotation
│   │   └── mercadolibre.py
│   │
│   ├── tasks/
│   │   ├── scheduler.py              # APScheduler setup
│   │   └── jobs.py                   # Funciones del cron
│   │
│   ├── templates/                    # Jinja2 + HTMX
│   └── static/
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                     # Migraciones generadas
│
├── tests/
│   ├── conftest.py
│   ├── unit/                         # Sin BD, sin red
│   ├── integration/                  # Con BD de test, sin red externa (mocks)
│   └── fixtures/                     # JSON de respuestas de APIs reales
│
├── scripts/                          # One-off scripts (seeds, debug)
│
├── docs/
│   ├── adr/                          # Architecture Decision Records
│   ├── ml_api_setup.md
│   ├── deployment.md
│   └── runbook.md                    # Qué hacer cuando algo falla
│
├── .claude/
│   └── skills/                       # Skills custom del proyecto
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
│
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml                    # uv + ruff + mypy + pytest config
├── alembic.ini
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── CLAUDE.md                         # Este archivo
```

---

## 🧱 Modelo de datos

### `books`
Catálogo único de libros normalizado por ISBN-13.

```python
id: UUID (pk)
isbn_13: str (unique, indexed, NOT NULL)
isbn_10: str | None
title: str (NOT NULL)
authors: list[str]                    # JSONB en Postgres
publisher: str | None
publication_year: int | None
category: str (enum: TECH, MEDICINE, LAW, BUSINESS, OTHER)
cover_url: str | None
metadata_source: enum (google_books, open_library, manual, ml_scrape)
created_at: datetime
updated_at: datetime
```

### `opportunities`
Cada vez que detecto un libro candidato.

```python
id: UUID (pk)
book_id: UUID (fk -> books)
source_url: str (unique con book_id)
source_seller: str
source_price_cents: int               # En centavos, NUNCA float
source_condition: str
target_price_cents: int                # Precio al que vamos a vender
commission_cents: int
shipping_cents: int
iva_cents: int
net_margin_cents: int                  # target - source - commission - shipping - iva
margin_pct: Decimal                   # net_margin / target_price
ai_score: int | None                   # 0-100
ai_reasoning: str | None
status: enum (open, published, dismissed, expired)
detected_at: datetime
expires_at: datetime
```

### `publications`
Cuando publico una oportunidad en ML.

```python
id: UUID (pk)
opportunity_id: UUID (fk -> opportunities)
ml_item_id: str (unique)
ml_permalink: str
published_title: str
published_description: str
published_price_cents: int
published_at: datetime
status: enum (active, paused, closed, sold)
sold_at: datetime | None
final_margin_cents: int | None         # Margen real cuando se vende
```

### `price_history`
Histórico de precios (para tendencias).

```python
id: UUID (pk)
book_id: UUID (fk)
platform: enum (ml)
price_cents: int
condition: str
seen_at: datetime
```

---

## 📐 Coding Standards (estricto)

### Type hints
- **Toda función pública** debe tener type hints en parámetros y retorno.
- Usa `from __future__ import annotations` en cada archivo.
- `mypy --strict` debe pasar. Si no pasa, el código no se mergea.

### Naming
- **Variables, funciones, clases en inglés.** Ejemplo: `calculate_net_margin`, `BookMetadata`.
- **Comentarios y docstrings en español.** Ejemplo: `"""Calcula el margen neto de una oportunidad."""`.
- **UI / textos visibles en español.** Es un proyecto personal de Leo en México.
- **Nombres descriptivos.** `data` no es un nombre. `ml_listing` sí.

### Docstrings
Estilo Google. Obligatorios en funciones públicas y clases:

```python
def calculate_net_margin(
    target_price_cents: int,
    source_price_cents: int,
    commission_cents: int,
    shipping_cents: int,
) -> int:
    """Calcula el margen neto en centavos.

    Args:
        target_price_cents: Precio de venta planeado (centavos).
        source_price_cents: Precio de compra en ML (centavos).
        commission_cents: Comisión estimada de ML (centavos).
        shipping_cents: Costo de envío estimado (centavos).

    Returns:
        Margen neto en centavos. Puede ser negativo.

    Raises:
        ValueError: Si algún precio es negativo.
    """
```

### Manejo de errores
- **Excepciones específicas siempre.** Nunca `except Exception:` salvo en el top level con logging.
- Define excepciones custom en `app/core/exceptions.py` por dominio:
  - `MercadoLibreAPIError`, `BookMetadataNotFoundError`, `InvalidISBNError`, etc.
- Los servicios externos (ML, Google Books, Anthropic) **siempre** dentro de try/except específico, con log estructurado, y reintentos con backoff (usa `tenacity`).

### Async
- Todos los endpoints FastAPI son `async def`.
- Toda llamada a BD usa `AsyncSession`.
- Toda llamada HTTP usa `httpx.AsyncClient`.
- No mezclar sync y async (no `requests.get` en código async).

### Dinero
- **Siempre `int` en centavos.** Nunca `float`. Nunca `Decimal` en BD (sí en cálculos intermedios).
- Helpers en `app/core/money.py`:
  ```python
  def pesos_to_cents(pesos: Decimal | str) -> int: ...
  def cents_to_pesos(cents: int) -> Decimal: ...
  def format_mxn(cents: int) -> str: ...  # "$1,234.56 MXN"
  ```

### Logging
- Usa `structlog`, nunca `print` ni `logging` directo.
- Estructura: `logger.info("event_name", key1=value1, key2=value2)`.
- Eventos importantes a loggear: cada scraping run, cada oportunidad detectada, cada llamada a ML/Anthropic, cada error.

### Imports
- Orden (ruff lo hace automático): stdlib → terceros → primera-parte (`app.*`) → relativos.
- No uses imports relativos profundos (`from ...services`). Usa absolutos (`from app.services`).

---

## ✅ Definition of Done

Una tarea NO está terminada hasta que:

- [ ] El código compila y la app arranca sin errores
- [ ] `ruff check .` pasa sin warnings
- [ ] `ruff format --check .` pasa
- [ ] `mypy app/` pasa en strict mode
- [ ] Todos los tests existentes pasan: `pytest`
- [ ] Si la tarea es lógica de negocio, hay **al menos un test nuevo**
- [ ] Si la tarea toca dinero (margen, comisiones, precios), hay tests con casos límite (cero, negativos, valores muy grandes)
- [ ] Si la tarea toca un servicio externo, hay test con mock de la respuesta
- [ ] Si la tarea agrega un endpoint, está documentado (FastAPI lo hace automático con docstrings)
- [ ] Si la tarea cambia el modelo de datos, hay migración de Alembic generada y revisada
- [ ] Si la tarea cambia comportamiento observable, está actualizado el `CHANGELOG.md`
- [ ] Si la tarea introduce una decisión arquitectónica, está documentada como ADR en `docs/adr/`
- [ ] El commit sigue Conventional Commits
- [ ] El PR tiene título descriptivo y descripción que explica QUÉ y POR QUÉ
- [ ] El PR tiene **menos de 400 líneas modificadas** (excluyendo lockfiles y migraciones autogeneradas)

---

## 🔧 Verification commands (correr antes de cerrar tarea)

```bash
# Lint + format
ruff check .
ruff format --check .

# Type check
mypy app/

# Tests
pytest
pytest --cov=app --cov-report=term-missing  # con coverage

# Levantar app local
uvicorn app.main:app --reload

# Migraciones
alembic upgrade head                  # aplicar
alembic revision --autogenerate -m "descripción"  # generar nueva

# Pre-commit (corre todo lo de arriba)
pre-commit run --all-files
```

---

## 🚦 Commit & PR Conventions

### Conventional Commits

Formato: `<type>(<scope>): <descripción en español>`

Tipos permitidos:
- `feat`: nueva funcionalidad
- `fix`: corrección de bug
- `refactor`: cambio de código sin cambiar comportamiento
- `docs`: solo documentación
- `test`: solo tests
- `chore`: tareas de mantenimiento (deps, config)
- `perf`: mejora de performance
- `ci`: cambios en CI/CD

Ejemplos:
```
feat(scraper): agregar extracción de ISBN desde imágenes de portada
fix(margin): corregir cálculo de IVA en envíos a frontera
refactor(api): extraer dependencia de auth a módulo dedicado
test(margin): agregar casos límite para precios negativos
docs(adr): documentar decisión de usar centavos en lugar de Decimal
```

### Scope de PRs

**Una tarea = un PR.** Un PR debe poder describirse en una frase.

❌ Mal: "Sprint 3: scraping + metadata + tests"
✅ Bien: "feat(scraper): scraper inicial de listados de libros usados ML"

Si una tarea da más de 400 líneas, **divídela** en sub-tareas y crea PRs encadenados.

### Plantilla de PR

(ver `.github/pull_request_template.md`)

---

## 🛡️ Anti-patterns (NO hacer en este proyecto)

- ❌ **No uses `print()`.** Usa el logger.
- ❌ **No uses `requests` en código async.** Usa `httpx`.
- ❌ **No uses `float` para dinero.** Centavos en `int`.
- ❌ **No commitees `.env`.** Solo `.env.example`.
- ❌ **No agregues dependencias sin actualizar `pyproject.toml`** y justificar en el PR.
- ❌ **No uses `SELECT *` ni equivalentes en SQLAlchemy.** Selecciona columnas específicas.
- ❌ **No hagas llamadas a APIs externas sin timeout y sin retry con backoff.**
- ❌ **No hardcodees comisiones de ML, IVA, ni umbrales.** Todo en config o BD.
- ❌ **No agregues endpoints sin auth** (todos pasan por la dependencia de Basic Auth).
- ❌ **No catches `Exception` genérico** salvo en el top-level con logging.
- ❌ **No mezclas business logic en endpoints.** Endpoints son thin: validan, llaman servicios, retornan.
- ❌ **No abstraigas prematuramente.** Si solo hay una implementación, no hagas ABC.
- ❌ **No agregues TODOs sin issue de GitHub.** Formato: `# TODO(#42): descripción`.
- ❌ **No hagas migraciones manuales.** Siempre `alembic revision --autogenerate` y revisa el resultado.
- ❌ **No hagas scraping sin respetar `robots.txt` ni rate limit.**
- ❌ **No expongas información de error interna al usuario.** Logs sí, response no.

---

## 🤖 Funcionalidades de IA (Claude API)

Tres usos concretos. Si Leo pide más, evalúa primero si vale la pena el costo de tokens.

### 1. `opportunity_evaluator`
Input: libro + precio actual + categoría + histórico de precios.
Output: `{ "score": 0-100, "reasoning": "...", "risks": [...] }`.
Ejemplo: "Edición vieja de un libro técnico, demanda baja, score 35".

### 2. `listing_generator`
Input: libro (título, autor, año, descripción cruda).
Output: `{ "title": "...", "description": "...", "tags": [...] }` optimizado para SEO de ML.

### 3. `category_classifier`
Input: título + descripción.
Output: categoría interna del proyecto (TECH, MEDICINE, etc.).

### Reglas de IA

- Prompts viven como constantes en `app/services/ai/prompts.py`, versionados con número.
- **Siempre usar tool_use estructurado** (forzar JSON), no parsing de texto libre.
- Cachear resultados por `(book_id, prompt_version)` durante 30 días.
- Logear tokens usados por llamada para monitorear costo.
- Modelo por default: `claude-sonnet-4-6`. Para evaluaciones simples, considerar `claude-haiku-4-5` (más barato).

---

## 🔐 Variables de entorno

Ver `.env.example` para la lista completa. Las críticas:

- `APP_USERNAME`, `APP_PASSWORD` — HTTP Basic Auth
- `SECRET_KEY` — para firmar sesiones (genera con `openssl rand -hex 32`)
- `DATABASE_URL` — Postgres connection string
- `ANTHROPIC_API_KEY` — Claude
- `ML_CLIENT_ID`, `ML_CLIENT_SECRET`, `ML_REFRESH_TOKEN` — Mercado Libre
- `GOOGLE_BOOKS_API_KEY` — opcional
- `MIN_MARGIN_CENTS`, `MIN_MARGIN_PCT` — umbrales de oportunidad
- `SCAN_INTERVAL_HOURS` — frecuencia del scheduler

Validación: `app/config.py` usa `pydantic_settings.BaseSettings` y **falla al arrancar** si falta alguna variable obligatoria.

---

## 🗺️ Roadmap por sprints

Cada sprint = una rama feature, idealmente 1 PR por sub-tarea.

### Sprint 0: Foundation
- [ ] `pyproject.toml` con uv, ruff, mypy, pytest configurados
- [ ] Pre-commit hooks instalados
- [ ] FastAPI con `/health` y `/version`
- [ ] structlog configurado
- [ ] Pydantic Settings con `.env`
- [ ] HTTP Basic Auth funcional
- [ ] Docker + docker-compose con Postgres
- [ ] GitHub Actions con lint + typecheck + tests

### Sprint 1: Modelos y migraciones
- [ ] DeclarativeBase + TimestampMixin
- [ ] Modelos: Book, Opportunity, Publication, PriceHistory
- [ ] Schemas Pydantic correspondientes
- [ ] Alembic configurado, primera migración
- [ ] Tests de modelos con factory_boy o factories propias

### Sprint 2: Core utilities
- [ ] `core/isbn.py` con validación + conversión + tests exhaustivos
- [ ] `core/money.py` con helpers + tests
- [ ] `core/exceptions.py` con jerarquía del dominio

### Sprint 3: Metadata service
- [ ] Cliente Google Books con retry + timeout
- [ ] Cliente Open Library como fallback
- [ ] Servicio `book_metadata.py` con normalización
- [ ] Tests con fixtures reales (en `tests/fixtures/`)

### Sprint 4: Scraping ML
- [ ] `scrapers/base.py`: rate limiter + rotación UA + respeto robots.txt
- [ ] `scrapers/mercadolibre.py`: extracción de listados
- [ ] Heurística de extracción de ISBN (título → descripción → fallback)
- [ ] Tests con HTML fixtures de ML

### Sprint 5: Cálculo de margen
- [ ] `services/ml_commissions.py`: tabla parametrizada por categoría/modalidad
- [ ] `services/margin_calculator.py` con tests exhaustivos (incluir IVA, frontera, etc.)
- [ ] Integración: scraper → metadata → margen → opportunity

### Sprint 6: Dashboard
- [ ] Layout base Tailwind + HTMX
- [ ] Lista de oportunidades paginada con filtros (status, categoría, margen mínimo)
- [ ] Detalle de oportunidad
- [ ] Acción "descartar"
- [ ] Tests E2E con httpx

### Sprint 7: IA
- [ ] Cliente Anthropic con retry y logging de tokens
- [ ] `opportunity_evaluator` con tool_use estructurado
- [ ] `listing_generator`
- [ ] Cache de resultados (30 días) en BD
- [ ] Botón en dashboard "Evaluar con IA"

### Sprint 8: Scheduler + Deploy
- [ ] APScheduler con job cada `SCAN_INTERVAL_HOURS`
- [ ] Lifespan handler de FastAPI
- [ ] Deploy en Railway
- [ ] Logs accesibles, healthchecks

### Sprint 9: Integración ML (cuando Leo tenga app aprobada)
- [ ] OAuth flow ML
- [ ] `ml_publisher` con creación de items
- [ ] Botón "Publicar" en dashboard
- [ ] Manejo de errores específicos de ML
- [ ] Tests con respuestas mockeadas

### Sprint 10: Hardening
- [ ] Coverage mínimo 70% en `services/`
- [ ] Healthchecks + métricas básicas (Prometheus opcional)
- [ ] Runbook con troubleshooting común
- [ ] Backup automático de BD

---

## 🎓 Reglas operacionales para Claude Code

### Al inicio de cada sesión
1. **Lee este `CLAUDE.md` completo.**
2. Lee `CHANGELOG.md` para saber qué se hizo recientemente.
3. Si vas a tocar un módulo, **lee primero los tests existentes** de ese módulo.
4. Pregunta a Leo qué tarea atacar si no está claro.

### Antes de escribir código
1. Identifica si la tarea afecta una decisión arquitectónica cerrada.
2. Si va a haber cambio de modelo, planea la migración.
3. Si vas a agregar dependencia, justifica por qué.
4. Si la tarea es grande (>400 líneas estimadas), **divídela** en sub-tareas y propone el plan a Leo.

### Mientras escribes código
1. Tipado estricto, docstrings, sin `print`.
2. Tests junto con el código (TDD opcional, tests obligatorio).
3. Si descubres que necesitas hacer algo no planeado, **detente y pregunta**.

### Antes de cerrar
1. Corre todos los verification commands.
2. Actualiza `CHANGELOG.md` si aplica.
3. Crea ADR si tomaste decisión arquitectónica nueva.
4. Commit con Conventional Commits.
5. Crea PR con plantilla llena.

### Cuando algo no está claro
**Pregunta a Leo.** No inventes. Es preferible una pausa para clarificar que un PR de 500 líneas que hay que tirar.

### Cuando un test falla
1. **No deshabilites el test** para hacer pasar el código.
2. Entiende por qué falla.
3. Decide si el test está mal o el código está mal, y arregla la causa raíz.

### Cuando un servicio externo cambia
1. Aísla el cambio en su capa (cliente HTTP).
2. Actualiza fixtures de tests.
3. Documenta el cambio en `CHANGELOG.md`.
4. Si el cambio rompe contrato, **avisa a Leo**.

---

## 📚 Domain Glossary

- **ISBN-10 / ISBN-13:** identificadores de libros. ISBN-13 es estándar moderno. Conversión es determinística.
- **Oportunidad (`Opportunity`):** un libro detectado en ML que cumple criterios mínimos de margen.
- **Publicación (`Publication`):** una oportunidad que efectivamente publicamos en mi cuenta de ML.
- **Comisión ML:** porcentaje que ML cobra por venta. Varía por categoría (libros: ~13-16%) y modalidad (Clásica vs Premium).
- **Modalidad Clásica:** comisión menor, sin envío gratis garantizado.
- **Modalidad Premium:** comisión mayor, mejor exposición y meses sin intereses.
- **Mercado Envíos:** sistema de envíos de ML. Costo varía por peso, dimensiones, distancia.
- **Reputación ML:** verde/amarillo/rojo. Afecta costo de envío y exposición.
- **Margen neto:** `target_price - source_price - commission - shipping - iva`.
- **Frontera:** envíos a Tijuana/Mexicali tienen tarifas distintas.
- **`source_price`:** precio al que **compraríamos** el libro en ML.
- **`target_price`:** precio al que **revenderíamos** el libro en ML.

---

## 🔗 Recursos clave

- **API Mercado Libre:** https://developers.mercadolibre.com.mx/
- **Google Books API:** https://developers.google.com/books
- **Open Library API:** https://openlibrary.org/developers/api
- **Anthropic API:** https://docs.claude.com/
- **FastAPI:** https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0:** https://docs.sqlalchemy.org/en/20/
- **Railway:** https://docs.railway.app/

---

**Última actualización:** Sprint 0 (estructura inicial)
**Versión del CLAUDE.md:** 1.0
