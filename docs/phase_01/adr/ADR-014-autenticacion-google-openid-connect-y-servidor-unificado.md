# ADR-014: Autenticación con Google OpenID Connect y servidor unificado

## Estado

Aceptado

## Contexto

El sistema requiere identificar a clientes externos para permitirles reservar turnos (CU-001, CU-002) y al personal interno (administrador y peluqueros) para gestionar agendas y servicios, cumpliendo con:
* RNF-SEG-01: Prohibición de almacenar contraseñas locales de clientes si la identidad se resuelve mediante Google.
* ADR-002: Separación estricta entre `clientes` y `usuarios` internos.
* Prevención de suplantación de identidad (Account Takeover), ataques CSRF, y repetición de tokens (replay attacks).
* Operación simplificada para despliegue y desarrollo local sin problemas de CORS ni requerir múltiples servidores web.

## Decisión

1. **Flujo Authorization Code en Servidor con PKCE (S256), State y Nonce:**
   * El cliente web no intercambia tokens ni maneja secretos. El navegador es redirigido a `/auth/google/start`, el backend genera los desafíos criptográficos y redirige a Google.
   * Al regresar a `/auth/google/callback`, el backend valida el `id_token` firmado por Google (RS256), comprueba `aud`, `iss`, `exp`, `email_verified=true` y coincidencia estricta de `nonce`.
2. **Estado Efímero sin Redis ni Base de Datos (`afterlook_google_flow`):**
   * El estado del handshake (`state`, `nonce`, `code_verifier`, `attempt_id`) se almacena en una cookie firmada con JWT (HS256) con TTL de 5 minutos, `HttpOnly`, `SameSite=Lax`, y path restringido a `/auth/google`. Se invalida de inmediato al consumir el callback.
3. **Identificador Estable Inmutable (`google_sub`):**
   * Se agrega la columna única `google_sub` a las tablas `clientes` y `usuarios` mediante la migración `20261005_02`. La identidad se asocia al Subject Identifier inmutable de Google para proteger al sistema si el usuario cambia de email.
4. **Resolución de Identidad Dual (ADR-002):**
   * Si la identidad coincide con un registro preconfigurado en `usuarios`, se emite sesión de personal interno (`actor_type="staff"`, rol `ADMIN` o `PELUQUERO`) validando `activo=True`.
   * Si no pertenece al staff, se resuelve contra `clientes`: si no existe, se auto-registra (CU-001) en estado `ACTIVA`. Si le faltan datos de contacto (`telefono`/`whatsapp`), se detecta `profile_complete=False` (CU-002).
5. **Sesión Canónica Local (`afterlook_session`):**
   * Tras validar la identidad con Google, el backend emite su propia cookie de sesión JWT (`afterlook_session`, 8 horas, `HttpOnly`, `SameSite=Lax`, `Path=/`). Nunca expone tokens de acceso o ID tokens de Google al navegador.
6. **Arquitectura Hexagonal (DIP / ISP):**
   * El caso de uso (`service.py`) depende del contrato abstracto `IdentityProvider` (`google_port.py`), desacoplándolo de librerías externas de Google. La implementación concreta reside en `GoogleOIDCAdapter` (`google_adapter.py`).
7. **Hosting Unificado de Frontend y Backend:**
   * El frontend compilado de Astro (`frontend/dist/`) se sirve directamente mediante `StaticFiles` en FastAPI en el puerto 8000. Se elimina CORS y se centraliza la ejecución en un solo comando: `make run`.

## Consecuencias

* **Positivas:**
  * Máxima seguridad contra CSRF, fijación de sesión y replay attacks.
  * Cero almacenamiento ni exposición de contraseñas de clientes o tokens de Google.
  * Cero problemas de CORS al compartir el mismo origen `http://127.0.0.1:8000`.
  * Cobertura de pruebas unitarias al 100% sin depender de conexión a internet mediante `FakeIdentityProvider`.
* **Negativas / Compensaciones:**
  * Requiere compilar el frontend (`npm run build`) antes de levantar el servidor unificado con Uvicorn (automatizado en el target `make run`).

## Evidencia relacionada

* `app/modules/identity/google_port.py`
* `app/modules/identity/google_adapter.py`
* `app/modules/identity/google_flow.py`
* `app/modules/identity/service.py`
* `app/modules/identity/session.py`
* `app/modules/identity/router.py`
* `app/modules/identity/observability.py`
* `migrations/versions/20261005_02_google_oauth_sub.py`
* `tests/test_identity_flow.py`
* `tests/test_identity_session.py`
* `tests/test_identity_service.py`
* `tests/test_identity_router.py`
