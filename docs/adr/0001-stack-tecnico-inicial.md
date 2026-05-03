# ADR 0001: Stack técnico inicial del proyecto

- **Estado:** Aceptado
- **Fecha:** Sprint 0
- **Decididores:** Leo (supervisor), Claude (asistente)

## Contexto

El proyecto es una aplicación web personal para detectar oportunidades de arbitraje de libros usados en Mercado Libre México. El usuario único es Leo, que supervisará el desarrollo, pero el código será generado por Claude Code en VS Code.

Necesitamos un stack que sea:
1. Mantenible por una IA con consistencia entre sesiones
2. Verificable automáticamente (CI estricto)
3. Profesional y moderno (mejores prácticas 2026)
4. Económico de operar (single user, low traffic)

## Decisión

### Backend
- **Python 3.12+** con type hints estrictos.
- **FastAPI** + **SQLAlchemy 2.0 async** + **PostgreSQL 16**.
- **Alembic** para migraciones desde el día 1.
- **Pydantic v2** para validación.
- **structlog** para logging estructurado.

### Tooling
- **uv** como gestor de paquetes (10-100x más rápido que pip).
- **ruff** para lint y format (reemplaza black, flake8, isort).
- **mypy en strict mode** para type checking.
- **pytest** + **pytest-asyncio** + **pytest-cov** para tests.
- **pre-commit** para hooks locales.

### Frontend
- **Jinja2 + HTMX + Tailwind**, sin SPA. Suficiente para un dashboard interno.

### Operaciones
- **Docker + docker-compose** para desarrollo reproducible.
- **GitHub Actions** para CI (lint, typecheck, tests, security).
- **Railway** para deploy (gratis, soporta BD persistente y scheduler).

### Tareas asíncronas
- **APScheduler embebido** en FastAPI (no Celery+Redis).

## Alternativas consideradas

### SQLite vs PostgreSQL
- SQLite tiene cero configuración, pero en producción real (Railway gratuito) PostgreSQL viene incluido.
- Mantener un único motor entre dev y prod evita bugs sutiles.
- **Decisión:** PostgreSQL desde el inicio.

### Celery + Redis vs APScheduler
- Celery agrega 2 servicios extra (Redis broker + worker process).
- Para un único usuario corriendo escaneos cada 4h, APScheduler embebido en FastAPI es suficiente.
- **Decisión:** APScheduler. Migrar a Celery solo si volumen lo justifica.

### Async vs sync SQLAlchemy
- Inicialmente se consideró sync para reducir complejidad para un programador humano.
- Como el código lo genera una IA, la complejidad async no es un problema.
- Async permite scraping concurrente eficiente.
- **Decisión:** SQLAlchemy 2.0 async.

### React frontend vs Jinja+HTMX
- Leo tiene experiencia con React Native, pero un SPA es overkill para un dashboard de uso personal.
- HTMX + Jinja permite respuestas server-side rendered con interactividad ligera.
- **Decisión:** Jinja + HTMX + Tailwind.

### pip vs uv
- uv es notablemente más rápido y maneja lockfiles deterministas.
- Es el estándar moderno (2024+) para proyectos Python nuevos.
- **Decisión:** uv.

## Consecuencias

### Positivas
- CI bloquea PRs con problemas antes de que Leo los revise.
- Type checking strict atrapa muchos bugs en desarrollo.
- Stack moderno sin deuda técnica heredada.
- Reproducibilidad total con Docker.

### Negativas
- Curva de aprendizaje mayor si Leo quiere tocar código manualmente.
- async tiene mayor complejidad conceptual que sync.
- mypy strict puede frenar prototipado rápido.

### Mitigaciones
- `CLAUDE.md` documenta todas las decisiones para que Claude Code sea consistente.
- Tests obligatorios para lógica crítica reducen miedo al cambio.
- PRs pequeños permiten que Leo revise sin tener que entender cada detalle.

## Referencias

- [uv](https://docs.astral.sh/uv/)
- [ruff](https://docs.astral.sh/ruff/)
- [SQLAlchemy 2.0 async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [structlog](https://www.structlog.org/)
- [HTMX](https://htmx.org/)
