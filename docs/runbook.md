# Runbook — Arbitraje de Libros

> Qué hacer cuando algo falla en producción.

## La app no arranca

### Síntomas
- `docker compose up` se cae
- En Railway: build OK pero deploy falla

### Causas comunes
1. **Falta variable de entorno obligatoria.** Pydantic Settings falla al arrancar.
   - Verificar `.env` vs `.env.example`.
   - Logs muestran qué variable falta.

2. **No puede conectar a Postgres.**
   - Verificar `DATABASE_URL`.
   - En Railway: usar la variable interna del servicio, no la pública.

3. **Migraciones pendientes.**
   - Correr `alembic upgrade head`.

## Scraping retorna 0 resultados

### Síntomas
- Logs muestran `scraper_completed` pero `items_found: 0`.
- Dashboard sin nuevas oportunidades.

### Causas comunes
1. **ML cambió HTML.** Selectolax selectors rotos.
   - Inspeccionar HTML actual de ML.
   - Actualizar selectors en `app/scrapers/mercadolibre.py`.
   - **Siempre actualizar fixtures de tests** con HTML nuevo.

2. **Rate limiting.** ML está retornando 429.
   - Logs mostrarían `rate_limited` warnings.
   - Bajar `MAX_REQUESTS_PER_MINUTE`.

3. **IP bloqueada.** Para scraping desde Railway.
   - Considerar proxies rotativos (último recurso).

## La IA está costando demasiado

### Síntomas
- Bill de Anthropic crece más rápido que ventas.

### Acciones
1. Verificar logs de tokens por llamada.
2. Verificar que cache de evaluaciones esté funcionando (`opportunity_evaluations` table).
3. Considerar mover `category_classifier` de Sonnet a Haiku.
4. Limitar a evaluar solo oportunidades con margen ≥ percentil 75.

## Migration de Alembic falla

### Síntomas
- `alembic upgrade head` da error.
- Producción no puede arrancar después de deploy.

### Acciones
1. **Nunca borrar migración aplicada en producción.**
2. Si la migración tiene bug:
   ```bash
   # Crear una migración de "fix"
   alembic revision -m "fix bug en migración X"
   ```
3. Si necesitas downgrade urgente: `alembic downgrade -1`.
4. Para datos corruptos: snapshot de Postgres antes de tocar.

## Refresh token de ML expirado

### Síntomas
- Logs muestran `ML_TOKEN_REFRESH_FAILED`.
- Publicaciones nuevas fallan con 401.

### Acción
1. Re-autorizar manualmente:
   ```
   https://auth.mercadolibre.com.mx/authorization?response_type=code&client_id=XXX&redirect_uri=YYY
   ```
2. Capturar `code` del callback.
3. Intercambiar por nuevo `refresh_token`.
4. Actualizar `.env` o variable de Railway.

## Backup de BD

### Setup
Railway hace backups automáticos diarios para Postgres.

### Restore manual
1. Desde dashboard de Railway → Database → Backups → Restore.
2. **Antes de restaurar**, hacer snapshot del estado actual.

### Backup local manual
```bash
docker compose exec postgres pg_dump -U postgres arbitraje_libros > backup_$(date +%Y%m%d).sql
```

## Logs no aparecen

### En Railway
- Dashboard → Logs tab.
- Filtrar por `level: error`.
- Si no hay nada, verificar que `LOG_LEVEL` no esté en `WARNING`.

### Localmente
- Output del proceso de Docker: `docker compose logs -f app`.

## Contactos / escalación

- Anthropic API status: https://status.anthropic.com/
- Mercado Libre dev status: https://developers.mercadolibre.com.mx/devcenter
- Railway status: https://status.railway.app/
