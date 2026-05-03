# Changelog

Todo cambio notable se documenta aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versiones siguen [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
