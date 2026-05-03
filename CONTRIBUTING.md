# Contribuyendo

Este es un proyecto personal de **Leo**, programado por **Claude Code** bajo supervisión de Leo.

## Flujo de trabajo

1. Leo abre un issue describiendo la tarea.
2. Claude Code implementa en una rama feature (`feat/descripcion`, `fix/descripcion`, etc.).
3. Leo revisa el PR en GitHub.
4. Merge a `main` solo después de que todos los checks de CI pasen.

## Estándares

Ver [CLAUDE.md](./CLAUDE.md) para:
- Coding standards (typing, docstrings, naming)
- Definition of Done
- Conventional Commits
- Anti-patterns prohibidos
- Decisiones arquitectónicas cerradas

## Comandos locales

```bash
# Instalar dependencias
uv sync

# Lint + format
uv run ruff check .
uv run ruff format .

# Type check
uv run mypy app/

# Tests
uv run pytest
uv run pytest --cov=app --cov-report=html

# Pre-commit (corre todo lo anterior)
uv run pre-commit run --all-files

# Levantar app
docker compose up -d postgres
uv run uvicorn app.main:app --reload
```
