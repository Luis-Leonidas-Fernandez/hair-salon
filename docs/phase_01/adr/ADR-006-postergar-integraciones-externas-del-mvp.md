# ADR-006: Definir integraciones externas del MVP

## Estado

Reemplazado por ADR-008

## Contexto

El sistema podría integrarse con WhatsApp, Google Calendar, pagos online o señas. Todas esas integraciones agregan valor, pero también agregan complejidad, proveedores externos, manejo de fallas y reglas comerciales.

El MVP debe probar primero el flujo central de reserva.

## Decisión

Postergar integraciones externas del MVP salvo validación explícita con la peluquería.

Quedan como adaptadores futuros:

- WhatsApp
- Google Calendar
- pagos online
- señas
- chatbot o automatización avanzada

## Consecuencias

- El núcleo de reservas queda más simple y estable.
- La arquitectura debe dejar puntos de extensión para integraciones futuras.
- Si la reunión confirma que WhatsApp o pagos son obligatorios desde el día uno, este ADR debe revisarse.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla ahora |
| --- | --- |
| Integrar WhatsApp desde el MVP | Puede ser útil, pero requiere validar canal, costo, proveedor y política de envío. |
| Integrar pagos desde el MVP | Cambia alcance funcional, legal y operativo. |
| Integrar Google Calendar desde el MVP | Conviene validar si la peluquería ya lo usa realmente. |

## Evidencia relacionada

- `docs/phase_01/requirements/v1.1/Requisitos_no_funcionales_Peluqueria_Sergio_v1.1.md`
- `docs/phase_01/validations/v1.1/Objetivos_reunion_validacion_Peluqueria_Sergio_v1.1.md`


## Revisión posterior

La validación de negocio confirmó Google Calendar como necesidad de MVP. Por eso este ADR queda reemplazado por `ADR-008-incorporar-google-calendar-y-postergar-whatsapp-pagos.md`.
