# ADR-008: Incorporar Google Calendar y postergar WhatsApp y pagos

## Estado

Aceptado

## Contexto

La primera definición proponía postergar integraciones externas para proteger el MVP. Después de la validación de negocio, la peluquería confirmó que Google Calendar es necesario desde el MVP.

También se indicó interés en recordatorios por email y WhatsApp, pero WhatsApp quedó pendiente de averiguación. Pagos y señas fueron mencionados, pero por decisión del proyecto no se incorporan todavía.

## Decisión

Incorporar Google Calendar en el MVP como integración derivada de las reservas.

Mantener fuera del alcance actual:

- WhatsApp como canal obligatorio hasta definir proveedor, costo y factibilidad.
- Pagos online.
- Señas.
- Facturación automática.

La base de datos seguirá siendo la fuente oficial de verdad. Google Calendar y futuras notificaciones serán proyecciones o efectos secundarios de la reserva, no el registro maestro.

## Consecuencias

- La reserva debe confirmarse en PostgreSQL antes de sincronizar con Calendar.
- Una falla de Calendar no debe borrar ni invalidar una reserva confirmada.
- Se necesita registrar estado de sincronización o error para reintentos.
- WhatsApp puede agregarse luego como adaptador sin cambiar el núcleo de reservas.
- Pagos no condicionan todavía el ciclo de vida de una reserva.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla ahora |
| --- | --- |
| Postergar todas las integraciones | Ya no refleja la validación: Google Calendar fue solicitado para el MVP. |
| Incorporar WhatsApp desde el MVP | Falta confirmar proveedor, costo y condiciones operativas. |
| Incorporar pagos o señas | Cambia alcance, reglas comerciales y complejidad operativa; el usuario decidió no incluirlo todavía. |

## Evidencia relacionada

- `docs/phase_01/validations/v1.1/Resultado_reunion_validacion_Peluqueria_Sergio_v1.1.md`
- `docs/phase_01/requirements/v1.1/Requisitos_no_funcionales_Peluqueria_Sergio_v1.1.md`
