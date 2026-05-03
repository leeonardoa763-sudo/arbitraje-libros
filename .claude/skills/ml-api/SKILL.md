---
name: ml-api
description: Use this skill when working with Mercado Libre Mexico's official API — OAuth flows, publishing items, fetching listings, managing categories, or handling rate limits. Triggers include any code in app/services/ml_publisher.py, app/scrapers/mercadolibre.py (when distinguishing API calls from scraping), or tasks mentioning "publicar en ML", "OAuth ML", "ml_item_id", or "categoría MLM". Provides endpoint references, authentication flow, common payload schemas, error codes, and testing strategies.
---

# Mercado Libre API (Site MLM = México)

> **Documentación oficial:** https://developers.mercadolibre.com.mx/
> Esta skill resume lo necesario para el proyecto. Para detalles, consultar siempre la doc oficial.

## Setup inicial (prerrequisitos)

1. Tener cuenta de **vendedor** en ML (no solo comprador).
2. Crear app en https://developers.mercadolibre.com.mx/devcenter
3. Obtener `client_id` y `client_secret`.
4. Configurar `redirect_uri` (debe coincidir exactamente con `.env`).
5. Pasar OAuth flow para obtener `access_token` (corto, ~6h) y `refresh_token` (largo).

## OAuth 2.0 Flow

### Paso 1: redirección a ML
```
https://auth.mercadolibre.com.mx/authorization?
  response_type=code
  &client_id={ML_CLIENT_ID}
  &redirect_uri={ML_REDIRECT_URI}
```

### Paso 2: callback recibe `code`
```python
@router.get("/auth/ml/callback")
async def ml_callback(code: str) -> RedirectResponse:
    # Intercambiar code por tokens
    tokens = await ml_client.exchange_code(code)
    # Guardar refresh_token en BD/secrets seguro
    ...
```

### Paso 3: intercambiar `code` por tokens
```http
POST https://api.mercadolibre.com/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&client_id={ML_CLIENT_ID}
&client_secret={ML_CLIENT_SECRET}
&code={code}
&redirect_uri={ML_REDIRECT_URI}
```

Respuesta:
```json
{
  "access_token": "APP_USR-...",
  "token_type": "bearer",
  "expires_in": 21600,
  "refresh_token": "TG-...",
  "scope": "offline_access read write",
  "user_id": 123456789
}
```

### Paso 4: refresh cuando access_token expira
```http
POST https://api.mercadolibre.com/oauth/token

grant_type=refresh_token
&client_id={ML_CLIENT_ID}
&client_secret={ML_CLIENT_SECRET}
&refresh_token={ML_REFRESH_TOKEN}
```

> ⚠️ **El refresh_token también expira** después de 6 meses sin uso. Implementar alerta.

## Endpoints principales

### Crear publicación
```http
POST https://api.mercadolibre.com/items
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Clean Code - Robert C. Martin (Usado, buen estado)",
  "category_id": "MLM1132",
  "price": 250,
  "currency_id": "MXN",
  "available_quantity": 1,
  "buying_mode": "buy_it_now",
  "listing_type_id": "gold_special",   // gold_special = Premium, gold = Clásica
  "condition": "used",
  "pictures": [{"source": "https://..."}],
  "description": {"plain_text": "..."},
  "attributes": [
    {"id": "ISBN", "value_name": "9780132350884"},
    {"id": "AUTHOR", "value_name": "Robert C. Martin"},
    {"id": "PUBLISHER", "value_name": "Prentice Hall"}
  ],
  "shipping": {
    "mode": "me2",                     // Mercado Envíos
    "local_pick_up": false,
    "free_shipping": false
  }
}
```

### Modalidades (`listing_type_id`)
- `gold_special` — Premium (16% comisión, mejor exposición)
- `gold` — Clásica (13% comisión)
- `gold_premium` — Solo en algunos casos
- `silver` — DEPRECADO, no usar
- `bronze` — DEPRECADO, no usar

### Categoría de libros en MLM
- `MLM1132` — Libros (raíz). Usar siempre que aplique.
- ML puede sugerir subcategoría con: `GET /sites/MLM/category_predictor/predict?title=...`

### Predecir categoría desde título
```http
GET https://api.mercadolibre.com/sites/MLM/category_predictor/predict
  ?title=Clean Code Robert Martin Programming Book
```

### Consultar publicación
```http
GET https://api.mercadolibre.com/items/{ml_item_id}
```

### Pausar / cerrar publicación
```http
PUT https://api.mercadolibre.com/items/{ml_item_id}
{
  "status": "paused"     // paused | closed | active
}
```

### Búsqueda en site (sin auth, para scraping ético)
```http
GET https://api.mercadolibre.com/sites/MLM/search?category=MLM1132&condition=used&sort=price_asc&limit=50
```

## Rate Limiting

- **Llamadas autenticadas:** ~5,000/hora por app.
- **Búsquedas sin auth:** ~1,000/hora por IP.
- **Nuestra heurística:** máximo 30 requests/min para no llamar la atención.
- **Backoff:** si recibimos 429, esperar 60s y reintentar con `tenacity`.

## Errores comunes

| HTTP | Código ML | Significado | Acción |
|------|-----------|-------------|--------|
| 400 | `validation_error` | Payload inválido (categoría incorrecta, atributos faltantes) | Loggear + no reintentar |
| 401 | `invalid_token` | access_token expirado | Refresh y reintentar 1 vez |
| 403 | `forbidden` | Falta scope o cuenta sin reputación | Avisar a Leo |
| 404 | `not_found` | Item ya cerrado/borrado | Marcar publicación como `closed` |
| 429 | `too_many_requests` | Rate limit | Backoff exponencial (tenacity) |
| 500-503 | `server_error` | ML caído | Reintentar con backoff hasta 3 veces |

## Implementación recomendada

```python
# app/services/ml_publisher.py
class MLPublisher:
    def __init__(self, settings: Settings, http: httpx.AsyncClient) -> None:
        self.settings = settings
        self.http = http
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        retry=retry_if_exception_type(MLTransientError),
    )
    async def create_listing(self, payload: dict[str, Any]) -> dict[str, Any]:
        await self._ensure_token()
        response = await self.http.post(
            "https://api.mercadolibre.com/items",
            json=payload,
            headers={"Authorization": f"Bearer {self._access_token}"},
            timeout=30,
        )
        if response.status_code == 401:
            self._access_token = None
            raise MLTokenExpiredError()
        if response.status_code == 429:
            raise MLTransientError("rate_limited")
        if response.status_code >= 500:
            raise MLTransientError(f"server_error_{response.status_code}")
        if response.status_code >= 400:
            raise MLPermanentError(response.json())
        return response.json()
```

## Testing

- Usar `pytest_httpx` o `respx` para mockear endpoints.
- Tener fixtures con respuestas reales en `tests/fixtures/ml_responses/`.
- **NUNCA** llamar al API real desde tests.

## Recursos

- [Auth & Tokens](https://developers.mercadolibre.com.mx/es_ar/autenticacion-y-autorizacion)
- [Publish Items](https://developers.mercadolibre.com.mx/es_ar/publica-productos)
- [Listing Types](https://developers.mercadolibre.com.mx/es_ar/listing-types)
- [Category Predictor](https://developers.mercadolibre.com.mx/es_ar/predicador-de-categoria)
- [Sandbox / Test Users](https://developers.mercadolibre.com.mx/es_ar/usuarios-test)
