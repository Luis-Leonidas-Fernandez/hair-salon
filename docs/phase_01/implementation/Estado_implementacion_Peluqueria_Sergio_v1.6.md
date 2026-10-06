# Estado de implementación — After Look v1.6

Este documento conecta el diseño aprobado con lo que ya está implementado, desplegado y verificado en el proyecto. La versión **v1.6** consolida el **despliegue exitoso en producción en Render**, la **arquitectura de contenedor Docker multi-stage**, la **integración productiva con Google Cloud OAuth 2.0**, y la **resolución dinámica de roles del personal y clientes** ([ADR-017](../adr/ADR-017-despliegue-continuo-en-render-con-docker-unificado-y-resolucion-dinamica-de-roles.md)).

## Camino rápido

1. Activar el entorno virtual local: `source .venv/bin/activate`.
2. Ejecutar linter y formateador: `ruff check .` y `ruff format .`.
3. Ejecutar suite de pruebas: `pytest -v` (56 pruebas automatizadas pasando).
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

---

## Módulos y Arquitectura en Producción (v1.6)

### 1. Infraestructura de Producción (Render Cloud)
* **Web Service:** `after-look-app` ejecutándose sobre contenedor Linux optimizado (`python:3.12-slim` + Node.js 22 alpine en build multi-stage).
* **Managed Database:** PostgreSQL 18 en región Virginia (US East) (`after-look-db`).
* **Normalización Automática de Driver:** `Settings.normalize_database_url` convierte en caliente `postgres://` o `postgresql://` en `postgresql+asyncpg://`, permitiendo compatibilidad nativa sin reconfiguraciones manuales.
* **Ciclo de Inicio Atómico:**
  ```sh
  alembic upgrade head && python -m scripts.seed_initial_data && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
  ```

### 2. Autenticación Google OAuth 2.0 en Producción (CU-001)
* **Entorno Seguro:** Credenciales inyectadas mediante variables de entorno en Render (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`).
* **Seguridad de Repositorio:** Cero correos personales o secretos almacenados en código o historial de Git.
* **Enrutamiento por Rol:**
  - **Peluquero:** Redirigido automáticamente a la agenda privada en `/peluquero/turnos/`.
  - **Cliente con perfil incompleto:** Redirigido a `/completar-perfil` (CU-002).
  - **Cliente con perfil completo:** Redirigido a la reserva interactiva de turnos en `/reservas/` (CU-003).

### 3. Resolución Dinámica de Personal y Limpieza en Seed
* Si un miembro del staff intenta iniciar sesión antes de que sus variables estén activas, el seed detecta el correo en la tabla `clientes`, lo sanea automáticamente si no posee turnos huérfanos, y lo registra como `User` en la tabla `usuarios` con rol `PELUQUERO`.
* Asignación automática de todas las capacidades de servicio del catálogo inicial y generación de la disponibilidad base semanal (lunes a sábados de 9:30 a 22:00 hs).
* Inactivación preventiva de usuarios de prueba genéricos (`@afterlook.com`).

---

## Verificación y Tests Automatizados

La suite completa consta de **56 tests automatizados pasando al 100%** (`pytest`) con **0 errores de linting** (`ruff`):

```text
tests/test_booking.py ......                                             [ 10%]
tests/test_database_integrity.py ..                                      [ 14%]
tests/test_domain_types.py ..                                            [ 17%]
tests/test_hairdresser_turnos.py .....                                   [ 26%]
tests/test_health.py .                                                   [ 28%]
tests/test_identity_flow.py ....                                         [ 35%]
tests/test_identity_router.py .............                              [ 58%]
tests/test_identity_service.py ........                                  [ 73%]
tests/test_identity_session.py ...                                       [ 78%]
tests/test_models.py .                                                   [ 80%]
tests/test_seed_validations.py .........                                 [ 96%]
tests/test_settings.py ..                                                [100%]

======================== 56 passed, 2 warnings in 0.38s ========================
```
