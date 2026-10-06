# ADR-018: Estrategia de integración de Google Calendar para clientes y peluqueros

## Estado

Aceptado

## Contexto

En [ADR-008](ADR-008-incorporar-google-calendar-y-postergar-whatsapp-pagos.md) se determinó incorporar Google Calendar como integración oficial del MVP, estableciendo que la base de datos PostgreSQL permanece como la fuente de verdad y el calendario actúa como una proyección derivada de las reservas confirmadas.

Al abordar la arquitectura técnica y de experiencia de usuario (UX) para llevar esta integración a producción, surgieron los siguientes condicionantes:
1. **Fricción de permisos y pantallas de advertencia de Google:** Solicitar scopes de escritura directa (`https://www.googleapis.com/auth/calendar.events`) en el login de los clientes activa advertencias de "permisos sensibles" en Google Cloud, incrementa la desconfianza del usuario al registrarse y exige procesos prolongados de verificación de marca.
2. **Facilidad de guardado para el cliente:** El cliente requiere poder agendar el turno en su Google Calendar personal (web o app móvil de Android/iOS) con un solo toque inmediatamente después de confirmar la reserva, sin configuraciones previas.
3. **Visibilidad en tiempo real para el peluquero:** El profesional necesita que los turnos asignados aparezcan automáticamente en su Google Calendar personal/laboral en su teléfono celular, sin depender de cargar manualmente cada cita ni de autorizar accesos invasivos en su cuenta privada.

## Decisión

Se adopta una **estrategia combinada y desacoplada de doble vía**:

1. **Para Clientes — Enlace Dinámico Interactivo (Google Calendar Action Template):**
   - En la pantalla de confirmación exitosa de reserva (en `/reservas`), se presenta el botón interactivo **`📅 Guardar en Google Calendar`**.
   - El enlace se construye de forma determinista y dinámica utilizando la URL oficial de plantillas de eventos de Google:
     ```text
     https://calendar.google.com/calendar/render?action=TEMPLATE&text={titulo}&dates={inicio_utc}/{fin_utc}&details={detalles}&location={ubicacion}
     ```
   - Al hacer clic, se abre Google Calendar (o la aplicación nativa en dispositivos móviles) con los datos precargados:
     - **Título:** *{Servicio} con {Peluquero} - After Look*
     - **Horario:** Fechas y horas de inicio y fin exactas calculadas en formato ISO UTC (`YYYYMMDDTHHMMSSZ`).
     - **Detalle:** ID de reserva, precio estimado, notas y recordatorio del salón.
     - **Ubicación:** Dirección física de la peluquería.
   - **Cero fricción:** No requiere pedir scopes de calendario en el OAuth inicial, garantizando una tasa de registro limpia y transparente.

2. **Para Peluqueros — Suscripción Automática por Feed iCalendar (`.ics`):**
   - El backend expondrá un endpoint privado de calendario bajo el estándar RFC 5545 (`text/calendar`):
     ```text
     GET /api/calendar/hairdresser/{hairdresser_id}/feed.ics?token={security_token}
     ```
   - En el panel del peluquero (`/peluquero/turnos`), se provee la opción de suscripción **"Sincronizar con Google Calendar"** con su enlace seguro.
   - El peluquero vincula la URL una sola vez en su Google Calendar mediante la opción *"Agregar calendario desde URL"*.
   - Google Calendar consulta periódicamente el feed y refleja de forma desatendida todos los turnos confirmados y actualizados del profesional en su calendario móvil.

## Consecuencias

* **Positivas:**
  * **Experiencia de usuario instantánea y segura:** Cero barreras de permisos invasivos para los clientes.
  * **Sincronización desatendida para el staff:** El peluquero recibe todos sus turnos en su celular sin requerir cuentas de servicio complejas ni almacenamiento de refresh tokens adicionales.
  * **Resiliencia arquitectural:** La falla eventual de conectividad con Google Calendar no interrumpe ni degrada el flujo transaccional de reservas en PostgreSQL.
  * **Compatibilidad universal:** El estándar iCalendar funciona tanto en Google Calendar como en Apple Calendar y Microsoft Outlook.
* **Negativas / Mitigaciones:**
  * Google Calendar sincroniza calendarios externos por URL con un intervalo que suele variar entre pocas horas según la política interna de Google; mitigado porque el peluquero cuenta con su panel web en tiempo real (`/peluquero/turnos`) como fuente operativa inmediata.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla |
| :--- | :--- |
| Scope OAuth `calendar.events` para todos los clientes | Fricción elevada: exige permisos de edición sobre todo el calendario del usuario y revisión estricta de Google Cloud. |
| Creación de eventos vía Service Account central con invitado | Requiere que el dominio del correo del cliente acepte invitaciones externas y puede terminar en la bandeja de spam de invitaciones. |

## Evidencia relacionada

* `docs/phase_01/adr/ADR-008-incorporar-google-calendar-y-postergar-whatsapp-pagos.md`
* `app/modules/services/shared/models.py` (`CalendarEvent`)
* `frontend/src/pages/reservas.astro`
* `frontend/src/pages/peluquero/turnos.astro`
