# Deployment a Railway

## Por qué Railway

- Plan gratuito generoso ($5 USD de crédito mensual).
- PostgreSQL incluido en mismo proyecto.
- Soporta procesos long-running (necesario para APScheduler).
- Deploy con `git push`.
- Logs y métricas integrados.

## Setup inicial (una vez)

### 1. Crear cuenta en Railway
https://railway.app — login con GitHub.

### 2. Crear proyecto
- New Project → Deploy from GitHub repo.
- Seleccionar repo `arbitraje-libros`.

### 3. Agregar Postgres
- En el proyecto → New → Database → PostgreSQL.
- Railway crea variable `DATABASE_URL` automáticamente.

### 4. Configurar variables de entorno
En el servicio web, ir a Variables y agregar todo lo de `.env.example`:

```
APP_ENV=production
APP_USERNAME=leo
APP_PASSWORD=<password fuerte>
SECRET_KEY=<generar nueva>
DATABASE_URL=${{Postgres.DATABASE_URL}}    # referencia al servicio
ANTHROPIC_API_KEY=<clave real>
ML_CLIENT_ID=<cuando tengas>
ML_CLIENT_SECRET=<cuando tengas>
ML_REFRESH_TOKEN=<cuando tengas>
LOG_JSON=true
LOG_LEVEL=INFO
```

> ⚠️ **Convertir `DATABASE_URL`** de `postgresql://` a `postgresql+asyncpg://` con un init step si Railway no lo hace automáticamente.

### 5. Configurar build
Railway detecta `Dockerfile` automáticamente. Si quieres usar `pyproject.toml` con uv directamente:

- Settings → Builder: Dockerfile.
- Start Command: ya está en el Dockerfile (`CMD ["uvicorn", ...]`).

### 6. Custom domain (opcional)
- Settings → Networking → Generate domain.
- Para dominio propio: agregar CNAME desde tu DNS.

## Deploy

```bash
git push origin main
```

Railway hace build y deploy automáticamente. Ver logs en dashboard.

## Migraciones en producción

### Opción 1: Manual (recomendado al inicio)
```bash
railway run alembic upgrade head
```

### Opción 2: Pre-deploy hook
Agregar a `Dockerfile` un entrypoint que corra `alembic upgrade head` antes de `uvicorn`.

⚠️ Si la migración es destructiva, hacer manual con Leo presente.

## Healthcheck

Railway pinguea `/health` cada 30s. Si falla 3 veces seguidas, reinicia el contenedor.

Asegurar que `app/api/v1/health.py` no toque BD ni servicios externos (puede causar restart loop).

## Logs

- Dashboard → Logs tab.
- Estructurados en JSON (con `LOG_JSON=true`).
- Para grep: descargar y procesar localmente, o conectar Datadog/Better Stack.

## Costos

| Recurso | Plan free | Estimado proyecto |
|---------|-----------|-------------------|
| App web | 500 hrs/mes | ~720 hrs (24/7) → upgradeas a $5/mes |
| Postgres | 1GB | <500MB primer año |
| Egress | 100GB/mes | <1GB/mes |

**Realista:** $5–10 USD/mes con tráfico personal.

## Rollback

```bash
# Desde dashboard: Deployments → click en deploy anterior → Redeploy
```

O bien:
```bash
git revert HEAD
git push origin main
```

## Límites a considerar

- **Sleep inactividad:** Railway free puede dormir contenedores. **Para nuestro caso esto rompe APScheduler.** Considerar plan Hobby ($5/mes) que mantiene proceso vivo.
- **CPU bursts:** scraping concurrente puede gatillar throttling. Bajar concurrencia si pasa.

## Alternativas a Railway

Si Railway no funciona:
- **Fly.io** — similar, también free tier.
- **Render** — más caro, más estable.
- **Hetzner VPS** — €4/mes, más control pero más mantenimiento.
