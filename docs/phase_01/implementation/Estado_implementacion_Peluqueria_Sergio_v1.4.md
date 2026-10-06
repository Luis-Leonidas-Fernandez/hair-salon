# Estado de implementación — After Look v1.4

Este documento conecta el diseño aprobado con lo que ya está implementado y verificado en el proyecto. La versión v1.4 consolida el flujo central completo del cliente: **Onboarding de datos de contacto (CU-002)**, **Reserva de turnos con cálculo dinámico de disponibilidad (CU-003)**, **expansión de capacidad a 3 peluqueros**, **optimización de rendimiento y observabilidad en OAuth** y la suite de pruebas extendida a **48 tests pasando**.

## Camino rápido

1. Activar el entorno virtual: `source .venv/bin/activate`.
2. Ejecutar linter y formateador: `ruff check .` y `ruff format .`.
3. Ejecutar suite de pruebas: `pytest -v`.
4. Verificar la revisión de Alembic: `alembic current`.
5. Compilar frontend y levantar aplicación unificada: `make run`.

## Etapas completadas

| Etapa | Resultado | Evidencia |
| :--- | :--- | :--- |
| 1 | Seed inicial idempotente y validado | `scripts/seed_initial_data.py`, `tests/test_seed_validations.py` |
| 2 | Configuración centralizada desde `.env` | `app/config/settings.py`, `tests/test_settings.py` |
| 3 | Enums para vocabularios del dominio | `app/modules/services/shared/domain_types.py`, `tests/test_domain_types.py` |
| 4 | Integridad de reservas en PostgreSQL | `migrations/versions/20260920_01_reservation_integrity.py` |
| 5 | Autenticación con Google OpenID Connect (CU-001) | `app/modules/identity/`, `migrations/versions/20261005_02_google_oauth_sub.py` |
| 6 | Servidor unificado Frontend + Backend | `frontend/dist/` servido en `app/main.py`, target `make run` |
| 7 | Onboarding y completitud de perfil (CU-002) | `frontend/src/pages/completar-perfil.astro`, `POST /auth/complete-profile` |
| 8 | Extensión de capacidad a 3 Peluqueros | `seed_plan.py`, `settings.py`, `.env`, peluquero 3 enlazado en BD |
| 9 | Módulo de Reservas y Disponibilidad (CU-003) | `app/modules/booking/`, `frontend/src/pages/reservas.astro`, `reservas.css` |
| 10 | Optimización de red y observabilidad en tiempo real | Pool de conexiones en `google_adapter.py`, middleware de latencia en `main.py` |
| 11 | Agenda e historial de turnos para el peluquero (CU-010, CU-011) | `frontend/src/pages/peluquero/turnos.astro`, `GET /api/booking/hairdresser/my`, `PATCH /status` |

---

## Módulos Implementados

### 1. Módulo de Identidad (`app/modules/identity/`) — CU-001 & CU-002
* **`google_port.py` / `google_adapter.py`:** Autenticación Google OIDC con PKCE y validación de `id_token`. Optimizado con pool de conexiones `requests.Session()` para certificados JWK (< 50 ms).
* **`google_flow.py`:** Cookie efímera firmada `afterlook_google_flow` con state y nonce (5 min TTL).
* **`session.py`:** Sesión JWT canónica `afterlook_session` con `sub`, `actor_type`, `role`, `profile_complete`.
* **`service.py`:** Resolución dual de actores: staff (`usuarios`) vs clientes (`clientes`), auto-registro y función `complete_client_profile`.
* **`router.py`:** Endpoints `/auth/google/start`, `/auth/google/callback`, `/auth/me`, `/auth/logout` y `/auth/complete-profile`. Redirección inteligente de peluqueros directamente a `/peluquero/turnos/`.
* **Frontend Onboarding:** `/completar-perfil` con validación de teléfono argentino/internacional, sincronización de WhatsApp y redirección automática hacia `/reservas/`.

### 2. Módulo de Reservas (`app/modules/booking/`) — CU-003
* **`schemas.py`:** DTOs Pydantic estrictos para servicios, peluqueros, slots horarios, disponibilidad y reservas.
* **`service.py`:**
  - `get_active_services`: Servicios vigentes con precio y duración.
  - `get_active_hairdressers`: Peluqueros activos disponibles para asignación.
  - `get_hairdresser_availability`: Generación de franjas de 30 minutos a partir de los horarios semanales del peluquero (09:30 a 21:00) descontando turnos ocupados y excluyendo domingos y horas pasadas.
  - `create_booking`: Creación atómica de `Booking` en estado `CONFIRMADA` con canal `WEB`, precio estimado base y creación de su primer `BookingHistory`. Captura de violaciones de exclusión GiST de PostgreSQL con retorno de conflicto amigable.
* **`router.py`:** Endpoints `/api/booking/services`, `/api/booking/hairdressers`, `/api/booking/availability`, `/api/booking/reserve` y `/api/booking/my`.
* **Frontend Interactivo:** `/reservas/` en Astro con selector de servicios en tarjetas, selección de peluquero, carrusel de 14 días laborales, píldoras de horario en tiempo real, resumen de turno, notas opcionales y modal de confirmación con identificador de reserva persistido en PostgreSQL.

### 3. Agenda e Historial del Peluquero (`app/modules/booking/`) — CU-010 & CU-011
* **`schemas.py`:** DTOs `HairdresserBookingResponse`, `HairdresserBookingClient` y `UpdateBookingStatusRequest`.
* **`service.py`:**
  - `get_hairdresser_bookings`: Filtra turnos exclusivos del peluquero autenticado con carga ansiosa (`joinedload`) de datos de contacto del cliente y servicio contratado, ordenados cronológicamente con soporte de filtros por fecha y estado.
  - `update_booking_status_by_hairdresser`: Permite al peluquero cambiar el estado operativo del turno (`ASISTIO`, `NO_ASISTIO`, `CANCELADA`) garantizando propiedad del turno y registrando trazabilidad inmutable en `historial_reservas`.
* **`router.py`:** Endpoints protegidos para staff `GET /api/booking/hairdresser/my` y `PATCH /api/booking/hairdresser/bookings/{id}/status`.
* **Frontend:** `/peluquero/turnos/` con panel de control, tarjetas de reservas, acceso directo a WhatsApp y teléfono del cliente, y botones de acción rápida.

---

## Verificación y Tests Automatizados

La suite completa consta de **55 tests pasando en verde** (`pytest`):

```text
tests/test_booking.py ......                                             [ 10%]
tests/test_database_integrity.py ..                                      [ 14%]
tests/test_domain_types.py ..                                            [ 18%]
tests/test_hairdresser_turnos.py .....                                    [ 27%]
tests/test_health.py .                                                   [ 29%]
tests/test_identity_flow.py ....                                         [ 36%]
tests/test_identity_router.py .............                              [ 60%]
tests/test_identity_service.py ........                                  [ 74%]
tests/test_identity_session.py ...                                       [ 80%]
tests/test_models.py .                                                   [ 81%]
tests/test_seed_validations.py .........                                 [ 98%]
tests/test_settings.py .                                                 [100%]
============================== 55 passed in 0.40s ==============================
```

---

## ADRs relacionados

- [ADR-001 — Usar PostgreSQL como base principal](../adr/ADR-001-usar-postgresql-como-base-principal.md)
- [ADR-002 — Separar clientes y usuarios internos](../adr/ADR-002-separar-clientes-y-usuarios-internos.md)
- [ADR-003 — Modelar reserva como entidad central](../adr/ADR-003-modelar-reserva-como-entidad-central.md)
- [ADR-005 — Usar estados explícitos de reserva](../adr/ADR-005-usar-estados-explicitos-de-reserva.md)
- [ADR-009 — Seed idempotente y validado](../adr/ADR-009-seed-idempotente-y-validado.md)
- [ADR-010 — Configuración tipada desde el entorno](../adr/ADR-010-configuracion-tipada-desde-entorno.md)
- [ADR-011 — Vocabularios del dominio mediante enums](../adr/ADR-011-centralizar-vocabularios-del-dominio.md)
- [ADR-012 — Protección de solapamientos en PostgreSQL](../adr/ADR-012-proteger-solapamientos-en-postgresql.md)
- [ADR-013 — Estado de implementación versionado](../adr/ADR-013-versionar-el-estado-de-implementacion.md)
- [ADR-014 — Autenticación Google OpenID Connect y servidor unificado](../adr/ADR-014-autenticacion-google-openid-connect-y-servidor-unificado.md)
- [ADR-015 — Módulo de reservas, cálculo de disponibilidad y optimización del callback](../adr/ADR-015-modulo-de-reservas-y-optimizacion-de-disponibilidad.md)

---

## Próxima etapa

Implementar la vista del cliente para consultar y autogestionar la cancelación de sus turnos vigentes ([CU-005](file:///Users/luis/desktop/PROYECTOS/peluqueria/docs/phase_01/use-cases/Casos_de_uso_Peluqueria_Sergio.md) — *Cancelar turno*) y la vista general de agenda administrativa para el dueño/administrador ([CU-014](file:///Users/luis/desktop/PROYECTOS/peluqueria/docs/phase_01/use-cases/Casos_de_uso_Peluqueria_Sergio.md) — *Consultar agenda administrativa*).
