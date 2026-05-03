# Stage 1: builder — instala dependencias con uv
FROM python:3.12-slim AS builder

WORKDIR /app

# Copiar uv desde imagen oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Instalar solo dependencias de producción
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --frozen --no-cache

# Stage 2: runtime — imagen final liviana
FROM python:3.12-slim

WORKDIR /app

# Copiar virtualenv del builder
COPY --from=builder /app/.venv /app/.venv

# Copiar código fuente
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Agregar el venv al PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Railway healthcheck: pinguea /health cada 30s
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
