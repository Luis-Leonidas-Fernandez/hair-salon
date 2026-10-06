# Actualización de modelos post validación

## Sistema de reservas Peluquería Sergio

Este documento registra los ajustes que deben aplicarse al modelo conceptual, lógico y físico después de contrastar la reunión de validación con la documentación existente. No reemplaza los PNG existentes; funciona como control de cambios para la próxima versión visual de los modelos.

## Cambios aceptados

| Área | Cambio | Impacto en modelo |
| --- | --- | --- |
| Servicios | Barbería y peluquería como servicios iniciales | `servicios.nombre` debe permitir ambos valores como configuración inicial, no como hardcode. |
| Duración | Una hora por cliente | `servicios.duracion_minutos` y `reservas.duracion_minutos` deben iniciar con 60. |
| Bloques | Agenda en bloques de 30 minutos | Agregar regla de granularidad de agenda. Puede resolverse por configuración o restricción. |
| Horario | Lunes a sábado, 9:30 a 22:00 | Cargar disponibilidad base para ambos peluqueros. |
| Peluquero | Cliente elige peluquero | `reservas.peluquero_id` sigue siendo obligatorio en la reserva confirmada. |
| Bloqueos | Si un peluquero no trabaja, se bloquea disponibilidad | `disponibilidades` debe soportar bloqueo excepcional por usuario. |
| Cliente | Se piden nombre, teléfono, WhatsApp y fecha de nacimiento | `clientes` debe contemplar `whatsapp` y `fecha_nacimiento`. |
| Reserva manual | Admin puede cargar reservas telefónicas | `reservas.canal_reserva` debe incluir `TELEFONO` o `ADMIN`. |
| Cancelación | Cliente, admin o peluquero pueden cancelar | Historial debe registrar actor y fecha. Motivo queda opcional. |
| Google Calendar | Entra en MVP como integración derivada | Agregar estado/campo de sincronización o tabla futura de integraciones/eventos externos. |

## Estados de reserva normalizados

La validación mencionó estados del negocio, pero no conviene trasladarlos como texto libre. El catálogo técnico propuesto queda:

- `PENDIENTE`
- `EN_ESPERA`
- `AGENDADA`
- `RESERVADA`
- `CONFIRMADA`
- `ASISTIO`
- `NO_ASISTIO`
- `CANCELADA`

`CANCELADA` se conserva porque la validación confirmó cancelaciones, aunque no haya aparecido en la lista espontánea de estados.

## Pendientes que no deben modelarse todavía como definitivos

- WhatsApp obligatorio: falta proveedor, costo y factibilidad.
- Descansos automáticos: la respuesta indica que dependen de la cantidad de clientes, por lo tanto conviene modelarlos como bloqueos manuales al inicio.
- Pagos y señas: fuera de alcance actual. No agregar tablas de pago todavía.

## Cambios técnicos implementados después de la validación

| Cambio | Implementación | Estado |
| --- | --- | --- |
| Vocabularios controlados | Enums en `app/modules/services/shared/domain_types.py` y módulos existentes | Implementado |
| Solapamientos | `reservas.fecha_fin` generada y exclusión GiST por peluquero | Implementado |
| Migración física | `20260920_01_reservation_integrity` aplicada en PostgreSQL | Implementado |
| Identificador Google OIDC | `google_sub` único e indexado en `clientes` y `usuarios` (`20261005_02_google_oauth_sub`) | Implementado |
| Precios | Se mantienen como dato interno; no se muestran al cliente | Vigente |
| Pagos y señas | No se agregan tablas ni flujo | Fuera de alcance |

## Próxima acción recomendada

Actualizar las imágenes de modelo lógico y físico cuando se realice la siguiente revisión visual. La fuente técnica vigente para la restricción contra solapamientos es `docs/phase_01/implementation/Estado_implementacion_Peluqueria_Sergio_v1.2.md` y la migración aplicada.
