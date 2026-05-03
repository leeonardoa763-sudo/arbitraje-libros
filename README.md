# Arbitraje de Libros 📚

[![CI](https://github.com/leo/arbitraje-libros/actions/workflows/ci.yml/badge.svg)](https://github.com/leo/arbitraje-libros/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Aplicación web personal para detectar libros usados subvalorados en **Mercado Libre México**, calcular márgenes netos reales (comisiones + envío + IVA) y publicarlos en mi cuenta de vendedor con un clic.

## Stack

- **Python 3.12** + **FastAPI** + **SQLAlchemy 2.0 async**
- **PostgreSQL 16** + **Alembic**
- **Jinja2 + HTMX + Tailwind** (dashboard server-side)
- **APScheduler** (tareas programadas)
- **Anthropic Claude API** (evaluación de oportunidades, generación de listings)
- **uv** + **ruff** + **mypy strict** + **pytest**
- **Docker** + **GitHub Actions** + **Railway**

Ver [`CLAUDE.md`](./CLAUDE.md) para arquitectura completa y decisiones técnicas.

## Quickstart (desarrollo local)

### Prerrequisitos
- Python 3.12+
- Docker + docker-compose
- [uv](https://docs.astral.sh/uv/) instalado

### Setup

```bash
# 1. Clonar
git clone https://github.com/leo/arbitraje-libros.git
cd arbitraje-libros

# 2. Variables de entorno
cp .env.example .env
# Editar .env con valores reales

# 3. Levantar Postgres
docker compose up -d postgres

# 4. Instalar dependencias
uv sync

# 5. Migrar BD
uv run alembic upgrade head

# 6. Pre-commit hooks
uv run pre-commit install

# 7. Correr la app
uv run uvicorn app.main:app --reload
```

Abrir [http://localhost:8000](http://localhost:8000).

## Comandos comunes

```bash
# Tests
uv run pytest
uv run pytest --cov=app --cov-report=html

# Lint + format
uv run ruff check .
uv run ruff format .

# Type check
uv run mypy app/

# Migraciones
uv run alembic revision --autogenerate -m "descripción"
uv run alembic upgrade head
uv run alembic downgrade -1

# Levantar todo con Docker
docker compose up
```

## Estructura

```
app/
├── api/          # Endpoints FastAPI
├── core/         # Utilidades transversales (auth, isbn, money)
├── models/       # SQLAlchemy
├── schemas/      # Pydantic
├── services/     # Lógica de negocio (incluye AI)
├── scrapers/     # Scraping de ML
├── tasks/        # Cron jobs (APScheduler)
├── templates/    # Jinja2
└── static/

tests/
├── unit/
├── integration/
└── fixtures/

docs/
├── adr/          # Architecture Decision Records
├── ml_api_setup.md
├── deployment.md
└── runbook.md
```

## Desarrollo con Claude Code

Este proyecto está diseñado para que **Claude Code** sea el programador principal y **Leo** el supervisor.

- **Antes de cada sesión**, Claude debe leer [`CLAUDE.md`](./CLAUDE.md) completo.
- **Cada tarea** = un PR pequeño (<400 líneas) con tests, types, y docstrings.
- **CI bloquea** PRs que no pasen lint, types, tests y security scan.
- Leo revisa PRs en GitHub antes de hacer merge.

## Documentación

- [`CLAUDE.md`](./CLAUDE.md) — Reglas operacionales (LECTURA OBLIGATORIA antes de programar)
- [`docs/adr/`](./docs/adr/) — Decisiones arquitectónicas
- [`docs/ml_api_setup.md`](./docs/ml_api_setup.md) — Configuración de Mercado Libre Developers
- [`docs/deployment.md`](./docs/deployment.md) — Deploy a Railway
- [`docs/runbook.md`](./docs/runbook.md) — Troubleshooting operacional
- [`CHANGELOG.md`](./CHANGELOG.md) — Historial de cambios

## Licencia

Proprietary. Proyecto personal de Leo.
