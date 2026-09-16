# Reglas de negocio

## Sistema de reservas Peluquería Sergio

Este documento define las reglas de negocio validadas para el MVP del sistema de reservas. Su objetivo es evitar ambigüedades antes de implementar pantallas, base de datos, servicios de backend e integraciones.

## 1. Alcance de estas reglas

Estas reglas aplican al flujo de reserva, modificación, cancelación, disponibilidad, estados, recordatorios y sincronización con Google Calendar.

No incluyen pagos, señas ni facturación automática. Aunque el negocio mencionó seña para peluquería, por decisión del proyecto queda fuera del alcance actual.

## 2. Actores

| Actor | Descripción | Acciones principales |
| --- | --- | --- |
| Cliente | Persona que reserva un turno usando Google OAuth. | Reservar, modificar y cancelar turnos permitidos. |
| Peluquero | Usuario interno que atiende servicios asignados. | Ver su agenda, cambiar estados y cancelar si corresponde. |
| Administrador | Usuario interno con permisos operativos. | Configurar servicios, horarios, bloqueos y cargar reservas manuales. |

## 3. Servicios

| Regla | Definición |
| --- | --- |
| Servicios iniciales | Barbería y peluquería. |
| Duración base | Cada atención dura 60 minutos. |
| Precio visible | El precio no se muestra al cliente en el MVP. |
| Servicios combinados | Se permiten como servicios configurables, por ejemplo corte y barba. |
| Servicio exclusivo | No se validó que un servicio sea exclusivo de un único peluquero. |

## 4. Horarios y disponibilidad

| Regla | Definición |
| --- | --- |
| Horario general | Lunes a sábado, de 9:30 a 22:00. |
| Bloques de agenda | La agenda se organiza en bloques de 30 minutos. |
| Duración de turno | Aunque los bloques sean de 30 minutos, una reserva ocupa 60 minutos. |
| Atención paralela | Los dos profesionales pueden atender en paralelo, cada uno en su puesto. |
| Bloqueo excepcional | Si un peluquero no trabaja un día puntual, se bloquea su disponibilidad. |
| Descansos | No se automatizan todavía; se manejan como bloqueos manuales si hace falta. |

## 5. Reservas

| Regla | Definición |
| --- | --- |
| Login obligatorio | El cliente debe iniciar sesión con Google. |
| Datos del cliente | Nombre, email de Google, teléfono, WhatsApp y fecha de nacimiento. |
| Selección de peluquero | El cliente puede elegir peluquero. |
| Reserva para el mismo día | Está permitida. |
| Anticipación máxima | Se puede reservar hasta un mes antes. |
| Reserva manual | El administrador puede cargar reservas tomadas por teléfono. |
| Canal de reserva | Debe registrarse si la reserva entra por web, admin o teléfono. |

## 6. Prevención de solapamientos

Una reserva no puede solaparse con otra reserva vigente para el mismo peluquero en el mismo rango horario.

La validación debe considerar:

- peluquero elegido;
- fecha y hora de inicio;
- duración de la reserva;
- estado de la reserva;
- bloqueos excepcionales de disponibilidad.

La prevención de solapamientos no debe depender solo del frontend. Debe protegerse también en backend y persistencia.

## 7. Modificación de turnos

| Regla | Definición |
| --- | --- |
| Modificación por cliente | El cliente puede modificar el turno. |
| Efecto de modificación | Cambiar fecha, horario, peluquero o servicio debe volver a validar disponibilidad. |
| Historial | Toda modificación relevante debe registrarse en historial de reserva. |
| Notificaciones | Una modificación puede generar nuevas notificaciones o actualización de calendario. |

## 8. Cancelaciones

| Regla | Definición |
| --- | --- |
| Cancelación por cliente | Permitida hasta una hora antes del turno. |
| Cancelación por administrador | Permitida para gestión operativa. |
| Cancelación por peluquero | Permitida si corresponde por operación interna. |
| Motivo obligatorio | No se registra motivo obligatorio de cancelación. |
| Historial | La cancelación conserva fecha, actor y estado anterior. |

## 9. Estados de reserva

Los estados deben ser controlados, no texto libre. El catálogo técnico propuesto es:

| Estado | Significado operativo | Ocupa agenda |
| --- | --- | --- |
| PENDIENTE | Reserva iniciada o pendiente de confirmación operativa. | Sí, si ya tiene horario asignado. |
| EN_ESPERA | Cliente o turno en espera de disponibilidad o confirmación. | No, salvo que se asigne horario explícito. |
| AGENDADA | Turno cargado en agenda. | Sí. |
| RESERVADA | Turno reservado por cliente o administrador. | Sí. |
| CONFIRMADA | Turno confirmado. | Sí. |
| ASISTIO | El cliente asistió al turno. | No afecta disponibilidad futura. |
| NO_ASISTIO | El cliente no asistió. | No afecta disponibilidad futura. |
| CANCELADA | Turno cancelado. | No. |

Antes de implementar, conviene revisar si `AGENDADA`, `RESERVADA` y `CONFIRMADA` representan pasos realmente distintos o si alguno debe unificarse. Por ahora se conservan porque surgieron en la validación.

## 10. Recordatorios

| Regla | Definición |
| --- | --- |
| Recordatorio automático | Se contempla para el MVP. |
| Canal mínimo | Email. |
| WhatsApp | Deseado por el negocio, pero pendiente de proveedor, costo y factibilidad. |
| Momentos de envío | Entre 24 y 48 horas antes, y nuevamente el mismo día. |
| Falla de envío | La reserva sigue siendo válida aunque falle una notificación. |

## 11. Google Calendar

| Regla | Definición |
| --- | --- |
| Inclusión en MVP | Google Calendar entra en el MVP. |
| Fuente de verdad | PostgreSQL conserva la fuente oficial de la reserva. |
| Rol de Calendar | Calendar es una integración derivada, no el registro maestro. |
| Falla de sincronización | Una falla de Calendar no cancela ni invalida la reserva. |
| Reintento | Debe registrarse estado de sincronización para permitir reintentos. |

## 12. Permisos operativos

| Acción | Cliente | Peluquero | Administrador |
| --- | --- | --- | --- |
| Reservar turno propio | Sí | No aplica | Sí, manualmente |
| Elegir peluquero | Sí | No aplica | Sí |
| Modificar turno | Sí, si cumple reglas | Sí, según operación | Sí |
| Cancelar turno | Sí, hasta una hora antes | Sí | Sí |
| Ver agenda propia | No aplica | Sí | Sí |
| Ver toda la agenda | No | No, salvo permiso futuro | Sí |
| Configurar servicios | No | No | Sí |
| Configurar horarios y bloqueos | No | No o limitado | Sí |

## 13. Reglas fuera de alcance actual

- Pagos online.
- Señas.
- Facturación automática.
- Marketplace o múltiples peluquerías.
- Aplicación móvil nativa.
- Automatización avanzada por chatbot.

## 14. Pendientes de definición

| Tema | Pendiente | Impacto |
| --- | --- | --- |
| WhatsApp | Definir proveedor, costo y factibilidad. | Determina si entra como canal obligatorio o posterior. |
| Descansos | Confirmar si se cargan manualmente o se automatizan. | Afecta disponibilidad. |
| Estados similares | Confirmar diferencia real entre agendada, reservada y confirmada. | Afecta lógica de flujo y reportes. |

## 15. Criterio de aceptación general

El sistema cumple estas reglas cuando permite reservar, modificar y cancelar turnos sin solapamientos, conserva historial de cambios, respeta disponibilidad por peluquero, registra el canal de origen y mantiene la reserva válida aunque fallen notificaciones o sincronización con Google Calendar.
