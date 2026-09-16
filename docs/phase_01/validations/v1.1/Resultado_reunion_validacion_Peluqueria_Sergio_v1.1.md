# Resultado de reunión de validación

**Versión:** 1.1  
**Estado:** Actualizado post-validación de negocio  
**Fecha:** septiembre de 2026  
**Responsable:** Proyecto Peluquería Sergio  
**Fuente:** Reunión de validación, reglas de negocio, alcance MVP y ADRs aceptados


## Sistema de reservas Peluquería Sergio

Este documento consolida las respuestas recibidas y las evalúa contra la documentación existente. No todas las respuestas se incorporan automáticamente como decisiones técnicas: algunas se normalizan, otras quedan pendientes y pagos queda fuera del alcance actual.

## Decisiones aceptadas

| Tema | Decisión validada | Impacto documental |
| --- | --- | --- |
| Servicios | Barbería y peluquería | Actualizar requisitos y servicios iniciales. |
| Duración | Una hora por cliente | Mantener `duracion_minutos`, con valor inicial 60. |
| Agenda | Bloques de 30 minutos | Agregar granularidad de agenda. |
| Horario | Lunes a sábado, 9:30 a 22:00 | Configurar disponibilidad base. |
| Profesionales | Atienden en paralelo | Mantener reserva asociada a peluquero. |
| Elección | Cliente elige peluquero | El flujo de reserva debe incluir selección de peluquero. |
| Bloqueos | Se bloquea disponibilidad si un peluquero no trabaja | Mantener `disponibilidades` y bloqueos excepcionales. |
| Anticipación | Mismo día hasta un mes | Agregar regla de ventana de reserva. |
| Login | Google obligatorio | Mantener Google OAuth como decisión vigente. |
| Datos cliente | Nombre, teléfono, WhatsApp y fecha de nacimiento | Ampliar datos protegidos del cliente. |
| Reserva manual | Admin puede cargar turnos telefónicos | Mantener canal de reserva y actor responsable. |
| Cancelación | Cliente, admin o peluquero; hasta una hora antes para cliente | Actualizar reglas de cancelación. |
| Modificación | Cliente puede modificar turno | Agregar transición de modificación con historial. |
| Notificaciones | Email y WhatsApp deseados; falla no invalida reserva | Email entra como mínimo; WhatsApp pendiente de definición. |
| Google Calendar | Necesario desde MVP | Incorporar como integración derivada, no fuente de verdad. |

## Decisiones normalizadas

### Estados de reserva

El negocio mencionó: `agendado`, `reservado`, `confirmado`, `asiste`, `no asistió`, `pendiente` y `en espera`.

Para evitar estados duplicados o ambiguos, el modelo técnico debe usar un catálogo controlado. Propuesta inicial:

- `PENDIENTE`
- `EN_ESPERA`
- `AGENDADA`
- `RESERVADA`
- `CONFIRMADA`
- `ASISTIO`
- `NO_ASISTIO`
- `CANCELADA`

`CANCELADA` se mantiene aunque no haya sido listada en la respuesta de estados, porque la validación confirmó cancelaciones.

## Pendientes

- Definir si WhatsApp será integración obligatoria o posterior.
- Definir proveedor/costo de WhatsApp si se incorpora.
- Precisar si los descansos se cargan manualmente como bloqueos o si se calculan automáticamente.

## Fuera de alcance actual

- Pagos online.
- Señas.
- Facturación automática.

## Cambios recomendados

- Actualizar requisitos no funcionales con reglas de disponibilidad, datos personales, Google Calendar y recordatorios.
- Pasar ADRs ya validados a estado `Aceptado`.
- Reemplazar el ADR de integraciones externas, porque Google Calendar ya no queda postergado.
- Actualizar el ADR de estados explícitos para reflejar el catálogo normalizado.
- Mantener pagos fuera del modelo por ahora para no sobredimensionar el MVP.
