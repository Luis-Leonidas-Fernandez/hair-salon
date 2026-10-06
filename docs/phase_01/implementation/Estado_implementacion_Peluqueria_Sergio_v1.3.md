# Estado de implementación — After Look v1.3

Este documento conecta el diseño aprobado con lo que ya está implementado en el proyecto. La versión v1.3 incorpora la arquitectura completa de autenticación con **Google OAuth 2.0 / OpenID Connect**, el identificador inmutable `google_sub`, la resolución dual de actores (staff vs clientes), el servidor unificado y la suite de pruebas unitarias/integración.

## Camino rápido

1. Activar el entorno virtual: `source .venv/bin/activate`.
2. Ejecutar linter y formateador: `ruff check app tests migrations`.
3. Ejecutar suite de pruebas: `pytest -v`.
4. Verificar la revisión de Alembic: `alembic current`.
5. Compilar y levantar la aplicación unificada: `make run`.

## Etapas completadas

| Etapa | Resultado | Evidencia |
| :--- | :--- | :--- |
| 1 | Seed inicial idempotente y validado | `scripts/seed_initial_data.py`, `tests/test_seed_validations.py` |
| 2 | Configuración centralizada desde `.env` | `app/config/settings.py`, `tests/test_settings.py` |
| 3 | Enums para vocabularios del dominio | `app/modules/services/shared/domain_types.py`, `tests/test_domain_types.py` |
| 4 | Integridad de reservas en PostgreSQL | `migrations/versions/20260920_01_reservation_integrity.py` |
| 5 | Autenticación con Google OpenID Connect | `app/modules/identity/`, `migrations/versions/20261005_02_google_oauth_sub.py` |
| 6 | Servidor unificado Frontend + Backend | `frontend/dist/` servido en `app/main.py`, target `make run` |

---

## Módulo de Identidad implementado (`app/modules/identity/`)

Siguiendo el Principio de Responsabilidad Única (SRP) y Arquitectura Hexagonal (DIP/ISP):

1. **`google_port.py`:** Contrato abstracto `IdentityProvider` y dataclass inmutable `VerifiedIdentity`.
2. **`google_adapter.py`:** Implementación concreta OIDC con Google (`httpx` + `id_token.verify_oauth2_token`).
3. **`google_flow.py`:** Generación y validación del estado efímero PKCE (S256), `state`, `nonce` mediante cookie firmada `afterlook_google_flow` (5 min TTL).
4. **`session.py`:** Emisión y validación de la sesión canónica de aplicación `afterlook_session` (JWT con `sub`, `actor_type`, `role`, `profile_complete`).
5. **`service.py`:** Lógica de dominio:
   * **Personal Interno (`usuarios`):** Reconoce cuentas pre-sembradas (`ADMIN`, `PELUQUERO`), valida `activo=True` y enlaza `google_sub`.
   * **Clientes (`clientes`):** Auto-registro seguro en estado `ACTIVA` (CU-001) y detección de completitud de datos de contacto (CU-002).
6. **`observability.py`:** Registro estructurado JSON con `attempt_id` y **Zero PII** (sin nombres, emails ni tokens en logs).
7. **`schemas.py`:** DTOs Pydantic de sesión y respuesta para `/auth/me`.
8. **`router.py`:** Endpoints HTTP `/auth/google/start`, `/auth/google/callback`, `/auth/me`, `/auth/logout`.

---

## Modelo de Datos y Migración Aplicada

* **Migración Alembic:** `20261005_02_google_oauth_sub` aplicada en PostgreSQL `afterlook`.
* **Columnas agregadas:**
  * `clientes.google_sub`: `VARCHAR(255) NULL UNIQUE`, con índice `ix_clientes_google_sub`.
  * `usuarios.google_sub`: `VARCHAR(255) NULL UNIQUE`, con índice `ix_usuarios_google_sub`.

---

## Servidor Unificado (Frontend + Backend)

* **Hosting estático integrado:** `frontend/dist/` (generado por Astro) es servido directamente por FastAPI en `app/main.py` mediante `StaticFiles(..., html=True)`.
* **Cero CORS:** El frontend y el backend comparten el origen `http://127.0.0.1:8000`.
* **Vistas disponibles:**
  * `http://127.0.0.1:8000/` → Landing Page del salón.
  * `http://127.0.0.1:8000/registro/` → Pantalla de acceso con botón de Google OAuth.
  * `http://127.0.0.1:8000/reservas/` → Pantalla de selección de servicios y turnos con reconocimiento de usuario autenticado (`¡Hola, Luis Fernandez!`).
  * `http://127.0.0.1:8000/docs` → Documentación Swagger de la API.

---

## Verificación y Tests Automatizados

La suite completa consta de **36 tests pasando en verde** (`pytest`):

```text
tests/test_database_integrity.py ..                                      [  5%]
tests/test_domain_types.py ..                                            [ 11%]
tests/test_health.py .                                                   [ 13%]
tests/test_identity_flow.py ....                                         [ 25%]
tests/test_identity_router.py ........                                   [ 47%]
tests/test_identity_service.py .....                                     [ 61%]
tests/test_identity_session.py ...                                       [ 69%]
tests/test_models.py .                                                   [ 72%]
tests/test_seed_validations.py .........                                 [ 97%]
tests/test_settings.py .                                                 [100%]
============================== 36 passed in 0.31s ==============================
```

* **Flujo seguro probado:** `tests/test_identity_flow.py` verifica generación PKCE, expiración y rechazo por firmas inválidas.
* **Sesión probada:** `tests/test_identity_session.py` verifica claims JWT según RFC 7519, expiración y limpieza.
* **Casos de negocio probados:** `tests/test_identity_service.py` valida staff activo/inactivo, clientes nuevos (CU-001), clientes existentes y clientes suspendidos sin llamadas reales de red.
* **Endpoints HTTP probados:** `tests/test_identity_router.py` valida `/auth/google/start`, `/auth/google/callback`, cancelaciones de usuario, `/auth/me` (401 vs 200) y `/auth/logout`.

---

## ADRs relacionados

- [ADR-002 — Separar clientes y usuarios internos](../adr/ADR-002-separar-clientes-y-usuarios-internos.md)
- [ADR-009 — Seed idempotente y validado](../adr/ADR-009-seed-idempotente-y-validado.md)
- [ADR-010 — Configuración tipada desde el entorno](../adr/ADR-010-configuracion-tipada-desde-entorno.md)
- [ADR-011 — Vocabularios del dominio mediante enums](../adr/ADR-011-centralizar-vocabularios-del-dominio.md)
- [ADR-012 — Protección de solapamientos en PostgreSQL](../adr/ADR-012-proteger-solapamientos-en-postgresql.md)
- [ADR-013 — Estado de implementación versionado](../adr/ADR-013-versionar-el-estado-de-implementacion.md)
- [ADR-014 — Autenticación Google OpenID Connect y servidor unificado](../adr/ADR-014-autenticacion-google-openid-connect-y-servidor-unificado.md)

---

## Próxima etapa

Implementar el formulario interactivo para completar teléfono/WhatsApp en reservas ([CU-002](file:///Users/luis/desktop/PROYECTOS/peluqueria/docs/phase_01/use-cases/Casos_de_uso_Peluqueria_Sergio.md)) y la creación de reservas con persistencia en PostgreSQL ([CU-003](file:///Users/luis/desktop/PROYECTOS/peluqueria/docs/phase_01/use-cases/Casos_de_uso_Peluqueria_Sergio.md)).
