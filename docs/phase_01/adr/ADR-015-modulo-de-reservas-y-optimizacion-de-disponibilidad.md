# ADR-015: Módulo de reservas, cálculo de disponibilidad y optimización del callback

## Estado

Aceptado

## Contexto

El sistema completó la autenticación con Google OIDC (ADR-014), el onboarding de datos de contacto (CU-002) y requería implementar el núcleo del negocio: la reserva de turnos (CU-003), garantizando:
* **Separación de responsabilidades (SRP):** Módulo desacoplado de reservas (`app/modules/booking/`) con schemas, service y router independientes de identidad.
* **Cálculo dinámico de disponibilidad:** Generación de bloques de 30 minutos a partir de los horarios semanales del peluquero (09:30 a 21:00) deduciendo las reservas activas concurrentes para evitar solapamientos.
* **Integridad transaccional y auditoría:** Creación atómica de la reserva en estado `CONFIRMADA` junto a su entrada inicial en `historial_reservas`, con captura y tratamiento de la restricción de exclusión GiST de PostgreSQL (`exclusion_active_booking_overlap`).
* **Optimización y resiliencia de la red en autenticación:** Eliminación de los cuellos de botella en la descarga de certificados JWK de Google y prevención de reinicios continuos de Uvicorn durante la compilación del frontend.

## Decisión

1. **Módulo de Reservas Autónomo (`app/modules/booking/`):**
   * **`schemas.py`:** Define DTOs para `ServiceResponse`, `HairdresserResponse`, `TimeSlot`, `AvailabilityResponse`, `CreateBookingRequest` y `BookingResponse`.
   * **`service.py`:** Expone lógica de negocio pura:
     - `get_active_services`: Lista servicios vigentes.
     - `get_active_hairdressers`: Lista profesionales con rol `PELUQUERO` y `activo=True` (expandido de 2 a 3 peluqueros).
     - `get_hairdresser_availability`: Determina la disponibilidad diaria consultando `disponibilidades`, generando franjas candidatas de 30 min y excluyendo rangos ocupados por reservas que no estén canceladas ni finalizadas.
     - `create_booking`: Valida que el cliente tenga perfil completo (CU-002), valida el rango de fechas (máximo 31 días a futuro, excluyendo domingos), verifica ausencia de conflictos, inserta `Booking` y su primer `BookingHistory` en la misma transacción.
   * **`router.py`:** Controladores HTTP con prefijo `/api/booking` y verificación de sesión cliente mediante `afterlook_session`.
2. **Onboarding Dedicado para Contacto de Cliente (CU-002):**
   * Vista `/completar-perfil` con formulario para teléfono obligatorio, WhatsApp sincronizable y fecha de nacimiento opcional. Endpoint `POST /auth/complete-profile` que actualiza `clientes` y reemite el JWT con `profile_complete=True`.
3. **Escalabilidad del Seed a 3 Peluqueros:**
   * Actualización de la cuota en `seed_plan.py` (`InternalRole.PELUQUERO: 3`), variables en `.env` y soporte para profesionales adicionales.
4. **Optimización de Rendimiento en Handshake OAuth:**
   * Pool de conexiones persistente con `requests.Session()` en `GoogleOIDCAdapter` para reutilizar conexiones HTTPS en la descarga de claves públicas de Google (`googleapis.com/oauth2/v3/certs`), bajando el tiempo de respuesta de 50+ segundos a menos de 50 ms.
   * Middleware HTTP en `app/main.py` para medir y loguear latencias en milisegundos (`--> METHOD PATH`, `<-- METHOD PATH [STATUS] (ms)`).
   * Restricción de auto-reload de Uvicorn con `--reload-dir app` para evitar reinicios por artefactos de Astro (`dist/`).

## Consecuencias

* **Positivas:**
  * Cumplimiento estricto de CU-001, CU-002 y CU-003 con pruebas automatizadas (48 tests pasando).
  * Flujo fluido de reserva de extremo a extremo sin demoras ni pantallas congeladas.
  * Trazabilidad completa de cada reserva desde su creación en `historial_reservas`.
* **Negativas / Compensaciones:**
  * La generación de slots en memoria por intervalos de 30 min es óptima para 3-10 peluqueros y ventanas de 14 días; para salones masivos requerirá caché en memoria (e.g. Redis o memoización).

## Evidencia relacionada

* `app/modules/booking/schemas.py`
* `app/modules/booking/service.py`
* `app/modules/booking/router.py`
* `app/modules/identity/schemas.py`
* `app/modules/identity/service.py`
* `app/modules/identity/router.py`
* `frontend/src/pages/completar-perfil.astro`
* `frontend/src/pages/reservas.astro`
* `tests/test_booking.py`
* `tests/test_identity_router.py`
* `tests/test_identity_service.py`
