# Estado de implementación — After Look v1.7

Este documento conecta el diseño aprobado con lo que ya está implementado, verificado y listo en el proyecto. La versión **v1.7** consolida la **integración completa con Google Calendar (CU-012)** mediante la arquitectura de doble vía definida en [ADR-018](../adr/ADR-018-estrategia-integracion-google-calendar-clientes-y-staff.md).

## Camino rápido

1. Activar el entorno virtual local: `source .venv/bin/activate`.
2. Ejecutar linter y formateador: `ruff check .` y `ruff format .`.
3. Ejecutar suite de pruebas: `pytest -v` (68 pruebas automatizadas pasando al 100%).
4. Verificar la revisión de Alembic: `alembic current`.
5. Compilar frontend y levantar aplicación unificada local: `make run`.
6. En producción: despliegue automatizado continuo en Render mediante push a `main`.

## Etapas completadas

| Etapa | Resultado | Evidencia |
| :--- | :--- | :--- |
| 1 | Seed inicial idempotente y validado | `scripts/seed_initial_data.py`, `tests/test_seed_validations.py` |
| 2 | Configuración centralizada desde `.env` y variables de entorno | `app/config/settings.py`, `tests/test_settings.py` |
| 3 | Enums para vocabularios del dominio | `app/modules/services/shared/domain_types.py`, `tests/test_domain_types.py` |
| 4 | Integridad de reservas en PostgreSQL | `migrations/versions/20260920_01_reservation_integrity.py` |
| 5 | Autenticación con Google OpenID Connect (CU-001) | `app/modules/identity/`, `migrations/versions/20261005_02_google_oauth_sub.py` |
| 6 | Servidor unificado Frontend + Backend | `frontend/dist/` servido en `app/main.py`, target `make run` |
| 7 | Onboarding y completitud de perfil (CU-002) | `frontend/src/pages/completar-perfil.astro`, `POST /auth/complete-profile` |
| 8 | Extensión de capacidad a 3 Peluqueros | `seed_plan.py`, `settings.py`, `.env`, peluquero 3 enlazado en BD |
| 9 | Módulo de Reservas y Disponibilidad (CU-003) | `app/modules/booking/`, `frontend/src/pages/reservas.astro`, `reservas.css` |
| 10 | Optimización de red y observabilidad en tiempo real | Pool de conexiones en `google_adapter.py`, middleware de latencia en `main.py` |
| 11 | Agenda e historial de turnos para el peluquero (CU-010, CU-011) | `frontend/src/pages/peluquero/turnos.astro`, `GET /api/booking/hairdresser/my`, `PATCH /status` |
| 12 | Home de registro directo, archivo de landing y refinamiento de UX | `frontend/src/pages/index.astro`, `_servicios-landing-disabled.astro`, [ADR-016](../adr/ADR-016-home-de-registro-y-refinamiento-de-experiencia-de-usuario.md) |
| 13 | Despliegue en producción en Render con Docker y resolución de roles | `Dockerfile`, `settings.py`, [ADR-017](../adr/ADR-017-despliegue-continuo-en-render-con-docker-unificado-y-resolucion-dinamica-de-roles.md) |
| 14 | Integración con Google Calendar para Clientes y Staff (CU-012) | `app/modules/calendar/`, `frontend/src/pages/reservas.astro`, `frontend/src/pages/peluquero/turnos.astro`, `tests/test_calendar_feed.py`, [ADR-018](../adr/ADR-018-estrategia-integracion-google-calendar-clientes-y-staff.md) |

---

## Módulos y Arquitectura en Producción (v1.7)

### 1. Integración con Google Calendar (CU-012 & ADR-018)
* **Vía 1: Clientes (Zero-auth Action Template):**
  - Botón dinámico `📅 Guardar en Google Calendar` en el modal de confirmación de `/reservas`.
  - Construcción de URL interactiva de Google Calendar con título, timestamps UTC ISO compactos (`YYYYMMDDTHHMMSSZ`), notas, costo y dirección del salón.
  - Cero fricción de scopes sensibles en OAuth de clientes.
* **Vía 2: Staff / Peluqueros (Feed iCalendar RFC 5545 desatendido):**
  - Módulo backend `app/modules/calendar/` con generador RFC 5545 (`ics_builder.py`), escape estricto y folding de líneas a 75 bytes.
  - Acceso seguro mediante token HMAC-SHA256 en tiempo constante (`security.py`).
  - Endpoints: `GET /api/calendar/hairdresser/my-feed-url` (staff autenticado) y `GET /api/calendar/hairdresser/{id}/feed.ics?token=...` (feed público seguro con cache control).
  - Modal interactivo en `/peluquero/turnos` con botón de copiado de URL y enlace directo para suscripción en 1 clic en Google Calendar.

### 2. Infraestructura y Despliegue (Render Cloud)
* **Web Service:** `after-look-app` ejecutándose sobre contenedor Linux optimizado (`python:3.12-slim` + Node.js 22 alpine en build multi-stage).
* **Managed Database:** PostgreSQL 18 en región Virginia (US East) (`after-look-db`).
* **Normalización Automática de Driver:** `Settings.normalize_database_url` convierte en caliente `postgres://` o `postgresql://` en `postgresql+asyncpg://`.

---

## Verificación y Tests Automatizados

La suite completa consta de **67 tests automatizados pasando al 100%** (`pytest`) con **0 errores de linting** (`ruff`):

```text
tests/test_booking.py ......                                             [  8%]
tests/test_calendar_feed.py ..........                                   [ 23%]
tests/test_database_integrity.py ..                                      [ 26%]
tests/test_domain_types.py ..                                            [ 29%]
tests/test_hairdresser_turnos.py .....                                   [ 37%]
tests/test_health.py .                                                   [ 38%]
tests/test_identity_flow.py ....                                         [ 44%]
tests/test_identity_router.py .............                              [ 64%]
tests/test_identity_service.py ........                                  [ 76%]
tests/test_identity_session.py ...                                       [ 80%]
tests/test_models.py .                                                   [ 82%]
tests/test_seed_validations.py .........                                 [ 95%]
tests/test_settings.py ...                                               [100%]

======================== 67 passed, 2 warnings in 0.39s ========================
```
