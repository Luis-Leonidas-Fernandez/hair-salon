# Requisitos funcionales

**Versión:** 1.1  
**Estado:** Actualizado post-validación de negocio  
**Fecha:** septiembre de 2026  
**Responsable:** Proyecto Peluquería Sergio  
**Fuente:** Validación de negocio, reglas de negocio, modelos v1.1 y ADRs aceptados


## Sistema de reservas Peluquería Sergio

Este documento define las funcionalidades que debe cubrir el MVP del sistema de reservas. Se basa en la validación de negocio, las reglas de negocio, los modelos de datos v1.1 y los ADR aceptados.

## 1. Alcance funcional del MVP

El MVP debe permitir que un cliente reserve, modifique o cancele turnos con Google OAuth, eligiendo servicio, peluquero, fecha y horario disponible. También debe permitir operación interna para administrar servicios, horarios, bloqueos, agenda, estados, reservas manuales, recordatorios y sincronización con Google Calendar.

Quedan fuera del alcance funcional actual los pagos online, señas, facturación automática, aplicación móvil nativa y automatizaciones avanzadas.

## 2. Actores funcionales

| Actor | Descripción funcional |
| --- | --- |
| Cliente | Persona que ingresa con Google y gestiona sus propios turnos. |
| Peluquero | Usuario interno que consulta su agenda y actualiza estados operativos. |
| Administrador | Usuario interno que configura servicios, horarios, bloqueos y reservas manuales. |

## 3. Requisitos funcionales

| ID | Funcionalidad | Prioridad | Descripción | Criterio de aceptación |
| --- | --- | --- | --- | --- |
| RF-001 | Login con Google | Obligatorio | El cliente debe ingresar mediante Google OAuth. | El sistema identifica al cliente por email de Google y no solicita contraseña propia. |
| RF-002 | Completar datos de cliente | Obligatorio | El cliente debe registrar nombre, teléfono, WhatsApp y fecha de nacimiento. | No se confirma una reserva si faltan datos obligatorios. |
| RF-003 | Consultar servicios | Obligatorio | El cliente puede ver servicios activos disponibles para reservar. | Se muestran barbería, peluquería y servicios combinados activos si existen. |
| RF-004 | Seleccionar peluquero | Obligatorio | El cliente puede elegir peluquero para el turno. | La disponibilidad se calcula según el peluquero elegido. |
| RF-005 | Consultar disponibilidad | Obligatorio | El cliente puede consultar horarios disponibles por servicio, peluquero y fecha. | No se muestran horarios bloqueados, ocupados o fuera del horario de atención. |
| RF-006 | Reservar turno | Obligatorio | El cliente puede confirmar una reserva con servicio, peluquero, fecha y horario. | La reserva queda registrada sin solaparse con otro turno vigente. |
| RF-007 | Reservar para el mismo día | Obligatorio | El sistema permite reservar turnos para el mismo día si hay disponibilidad. | El horario elegido cumple las reglas de disponibilidad y no está vencido. |
| RF-008 | Limitar anticipación | Obligatorio | El sistema permite reservar hasta un mes de anticipación. | No se permite seleccionar fechas posteriores a la ventana permitida. |
| RF-009 | Modificar turno | Obligatorio | El cliente puede modificar un turno existente. | Al modificar fecha, horario, servicio o peluquero, se vuelve a validar disponibilidad. |
| RF-010 | Cancelar turno cliente | Obligatorio | El cliente puede cancelar hasta una hora antes del turno. | Si falta menos de una hora, el sistema impide la cancelación del cliente. |
| RF-011 | Cancelar turno interno | Obligatorio | Administrador o peluquero pueden cancelar turnos por operación interna. | La cancelación registra actor, fecha y estado anterior. |
| RF-012 | Reserva manual | Obligatorio | El administrador puede cargar reservas tomadas por teléfono. | La reserva manual registra canal y actor responsable. |
| RF-013 | Gestión de servicios | Obligatorio | El administrador puede crear, editar, activar o desactivar servicios. | Los cambios impactan en la reserva sin modificar código. |
| RF-014 | Gestión de horarios | Obligatorio | El administrador puede configurar horario de atención y disponibilidad por peluquero. | La disponibilidad se refleja en la consulta de turnos. |
| RF-015 | Bloqueos excepcionales | Obligatorio | El administrador puede bloquear disponibilidad de un peluquero en días u horarios puntuales. | Los horarios bloqueados no aparecen como disponibles. |
| RF-016 | Agenda de peluquero | Obligatorio | El peluquero puede ver su propia agenda. | No visualiza agenda completa salvo permiso futuro o administrador. |
| RF-017 | Agenda administrativa | Obligatorio | El administrador puede ver agenda general por fecha, peluquero y estado. | Puede filtrar y revisar reservas próximas. |
| RF-018 | Cambiar estado de reserva | Obligatorio | Usuarios internos autorizados pueden cambiar el estado operativo de una reserva. | El cambio queda registrado en historial. |
| RF-019 | Historial de reserva | Obligatorio | El sistema conserva cambios relevantes de una reserva. | Se puede reconstruir quién cambió qué, cuándo y desde qué estado. |
| RF-020 | Recordatorios por email | Obligatorio | El sistema contempla envío de recordatorios por email. | Se programa recordatorio entre 24 y 48 horas antes y el mismo día. |
| RF-021 | WhatsApp pendiente | Pendiente | El sistema deja preparada la posibilidad de WhatsApp, pero no lo vuelve obligatorio. | No se bloquea el MVP por falta de proveedor de WhatsApp. |
| RF-022 | Sincronizar Google Calendar | Obligatorio | La reserva debe sincronizarse con Google Calendar como integración derivada. | Si falla Calendar, la reserva sigue válida y queda registrada la falla. |
| RF-023 | Reintentar sincronización Calendar | Deseable | El sistema debe permitir detectar y reintentar sincronizaciones fallidas. | Existe estado de sincronización y error registrado. |
| RF-024 | Auditoría de acciones críticas | Obligatorio | El sistema registra acciones relevantes de usuarios internos. | Cambios de servicios, horarios, bloqueos y reservas quedan atribuibles. |
| RF-025 | Prevención de solapamientos | Obligatorio | El sistema evita reservas superpuestas para el mismo peluquero. | Dos reservas vigentes no pueden ocupar el mismo rango horario para el mismo peluquero. |

## 4. Flujo funcional principal de reserva

1. El cliente inicia sesión con Google.
2. Completa datos obligatorios si es la primera vez.
3. Selecciona servicio.
4. Selecciona peluquero.
5. Selecciona fecha dentro de la ventana permitida.
6. El sistema muestra horarios disponibles.
7. El cliente confirma la reserva.
8. El sistema valida solapamientos y disponibilidad.
9. El sistema registra la reserva e historial inicial.
10. El sistema programa recordatorios.
11. El sistema intenta sincronizar Google Calendar.
12. El cliente ve confirmación del turno.

## 5. Flujo funcional de modificación

1. El cliente selecciona una reserva existente.
2. El sistema verifica si la reserva puede modificarse.
3. El cliente cambia fecha, horario, servicio o peluquero.
4. El sistema vuelve a validar disponibilidad.
5. Si el cambio es válido, se actualiza la reserva.
6. Se registra historial.
7. Se actualizan recordatorios y sincronización con Calendar si corresponde.

## 6. Flujo funcional de cancelación

1. El cliente, peluquero o administrador solicita cancelar una reserva.
2. El sistema valida permisos y reglas de tiempo.
3. El sistema cambia el estado a `CANCELADA`.
4. El sistema registra actor, fecha y estado anterior.
5. El horario vuelve a quedar disponible si las reglas de agenda lo permiten.
6. Se actualiza o cancela la sincronización derivada con Google Calendar si corresponde.

## 7. Estados funcionales de reserva

| Estado | Uso funcional |
| --- | --- |
| PENDIENTE | Reserva iniciada o pendiente de confirmación operativa. |
| EN_ESPERA | Turno o cliente en espera de disponibilidad o confirmación. |
| AGENDADA | Turno cargado en agenda. |
| RESERVADA | Turno reservado por cliente o administrador. |
| CONFIRMADA | Turno confirmado. |
| ASISTIO | Cliente asistió. |
| NO_ASISTIO | Cliente no asistió. |
| CANCELADA | Turno cancelado. |

## 8. Reglas funcionales transversales

- La base de datos es la fuente oficial de la reserva.
- Google Calendar es una integración derivada, no el registro maestro.
- Una falla de notificación o Calendar no invalida una reserva confirmada.
- El sistema no debe permitir solapamientos para un mismo peluquero.
- Las acciones críticas deben conservar historial o auditoría.
- Pagos y señas no forman parte del MVP actual.

## 9. Pendientes funcionales

| Tema | Definición pendiente | Impacto |
| --- | --- | --- |
| WhatsApp | Falta definir proveedor, costo y factibilidad. | Puede convertirse en canal obligatorio futuro. |
| Estados similares | Falta confirmar si agendada, reservada y confirmada son pasos distintos. | Puede simplificar flujo antes de programar. |
| Descansos | Falta definir si serán bloqueos manuales o regla automática. | Afecta disponibilidad. |

## 10. Criterio de aceptación del MVP funcional

El MVP funcional queda completo cuando un cliente puede ingresar con Google, registrar sus datos, reservar un turno disponible eligiendo peluquero, modificarlo o cancelarlo bajo las reglas definidas; y cuando el administrador puede operar servicios, horarios, bloqueos, reservas manuales, agenda, estados, historial, recordatorios y sincronización derivada con Google Calendar sin incorporar pagos ni señas.
