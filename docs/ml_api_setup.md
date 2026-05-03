# Configuración de App en Mercado Libre Developers

Guía paso a paso para que Leo cree su aplicación en ML antes del Sprint 9.

## Prerrequisitos

1. **Cuenta de vendedor en ML México.**
   - No basta cuenta de comprador.
   - Realizar al menos 5-10 ventas como vendedor regular antes de pedir API.
   - Esto construye reputación y ML otorga permisos de API más fácilmente.

2. **Datos fiscales completos.**
   - Registrar RFC en perfil de ML.
   - Esto evita retención adicional del 1% ISR.

## Paso 1: Crear app en DevCenter

1. Ir a https://developers.mercadolibre.com.mx/devcenter
2. Iniciar sesión con la misma cuenta de vendedor.
3. **Crear aplicación** → llenar:
   - **Nombre:** `Arbitraje Libros - Leo`
   - **Descripción corta:** "Sistema personal de gestión de inventario y publicaciones de libros."
   - **URL del sitio:** `https://arbitraje-libros.up.railway.app` (o la que asigne Railway)
   - **URL de Redirect:** `https://arbitraje-libros.up.railway.app/auth/ml/callback`
   - **Scopes:** `read offline_access write`
   - **Tópicos de notificaciones:** `orders`, `items` (para webhooks futuros)

## Paso 2: Guardar credenciales

ML te dará:
- `App ID` → guardar como `ML_CLIENT_ID` en `.env`
- `Secret Key` → guardar como `ML_CLIENT_SECRET`

⚠️ **Nunca commitear estas credenciales.** Solo en variables de Railway.

## Paso 3: Pasar OAuth flow una vez

Para obtener el primer `refresh_token`:

1. Construir URL:
   ```
   https://auth.mercadolibre.com.mx/authorization?
     response_type=code
     &client_id={TU_CLIENT_ID}
     &redirect_uri=https://arbitraje-libros.up.railway.app/auth/ml/callback
   ```

2. Abrir en navegador, autorizar la app.

3. ML redirige a tu callback con `?code=XXX`.

4. La app intercambia ese code por tokens (este paso lo hace el endpoint `/auth/ml/callback` en el Sprint 9).

5. Guardar el `refresh_token` resultante en variable `ML_REFRESH_TOKEN` de Railway.

## Tiempos esperados

- **Crear app:** instantáneo.
- **Aprobación de scopes write:** automática para uso personal, pero ML monitorea.
- **Si la app empieza a hacer mucho volumen:** ML puede pedir verificación adicional.

## Sandbox

Si quieres probar sin afectar tu cuenta real:

1. Crear **usuarios de prueba** en https://developers.mercadolibre.com.mx/es_ar/usuarios-test
2. ML te da credenciales de un comprador y un vendedor de prueba.
3. Las publicaciones de prueba no son visibles públicamente.
4. Útil durante desarrollo del Sprint 9.

## Webhooks (futuro)

Cuando configures notificaciones:
- ML envía POST a tu endpoint cuando algo cambia (venta, mensaje, etc.).
- URL del webhook: `https://arbitraje-libros.up.railway.app/webhooks/ml`
- Validar firma `x-signature` de la request.

## Troubleshooting común

### Error "invalid_client" en token exchange
- Verificar que `client_id` y `client_secret` estén bien copiados (sin espacios).
- Verificar que `redirect_uri` sea **exactamente** la registrada en DevCenter.

### Error "forbidden" al publicar
- Tu cuenta puede no tener permiso para esa categoría.
- Verifica reputación de vendedor.

### Token expira muy rápido
- `access_token` dura 6 horas. Es normal.
- Implementar refresh automático con cache.

### "missing_scope"
- Re-autorizar con scopes correctos: `offline_access read write`.

## Costos

- **API de ML:** gratis para vendedores con cuenta activa.
- **Sin límites de publicaciones** en cuenta gratuita.
- **Comisiones** se aplican normalmente sobre ventas (ver skill `ml-commissions`).
