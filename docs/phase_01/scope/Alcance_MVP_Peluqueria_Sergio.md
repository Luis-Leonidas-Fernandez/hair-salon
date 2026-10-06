# Alcance MVP

## Sistema de reservas Peluquería Sergio

Este documento define el perímetro completo del MVP. Su objetivo es dejar claro qué se construye en la primera versión, qué queda fuera, qué depende de una definición pendiente y qué puede pasar a una fase futura.

El alcance se basa en la validación de negocio, las reglas de negocio, los requisitos funcionales, los requisitos no funcionales, los modelos de datos v1.1 y los ADR aceptados.

## 1. Objetivo del MVP

El MVP debe permitir que Peluquería Sergio gestione reservas de turnos de forma digital, evitando solapamientos, manteniendo historial operativo y permitiendo que clientes y usuarios internos trabajen con una agenda consistente.

La primera versión debe resolver el flujo principal de reserva antes de incorporar pagos, automatizaciones avanzadas o integraciones no confirmadas.

## 2. Principios de alcance

| Principio | Definición |
| --- | --- |
| Resolver el flujo central | El MVP prioriza reservar, modificar, cancelar y gestionar turnos. |
| Evitar solapamientos | La disponibilidad debe ser confiable por peluquero, fecha y horario. |
| Registrar trazabilidad | Cambios relevantes deben conservar actor, fecha y estado. |
| Separar núcleo e integraciones | La reserva vive en PostgreSQL; Calendar y notificaciones son efectos derivados. |
| No sobredimensionar | Pagos, señas y automatizaciones complejas no entran todavía. |

## 3. Entra en el MVP

| Área | Incluido | Detalle |
| --- | --- | --- |
| Autenticación cliente | Sí | Login y registro mediante Google OAuth. |
| Datos del cliente | Sí | Nombre, email Google, teléfono, WhatsApp y fecha de nacimiento. |
| Servicios | Sí | Barbería, peluquería y servicios combinados configurables. |
| Duración de turno | Sí | Atención base de 60 minutos. |
| Bloques de agenda | Sí | Disponibilidad organizada en bloques de 30 minutos. |
| Horario de atención | Sí | Lunes a sábado, de 9:30 a 22:00. |
| Profesionales | Sí | Hasta tres peluqueros/profesionales atendiendo en paralelo (actualizado según seed plan). |
| Elección de peluquero | Sí | El cliente puede elegir peluquero. |
| Consulta de disponibilidad | Sí | Por servicio, peluquero y fecha. |
| Reserva web | Sí | Cliente reserva desde el sistema. |
| Reserva manual | Sí | Administrador carga reservas tomadas por teléfono. |
| Modificación de turno | Sí | Cliente puede modificar bajo reglas de disponibilidad. |
| Cancelación cliente | Sí | Hasta una hora antes del turno. |
| Cancelación interna | Sí | Administrador o peluquero pueden cancelar según operación. |
| Estados de reserva | Sí | Catálogo controlado, no texto libre. |
| Historial | Sí | Cambios de estado y modificaciones relevantes. |
| Agenda peluquero | Sí | Cada peluquero ve su propia agenda. |
| Agenda administrativa | Sí | Administrador ve agenda general. |
| Bloqueos excepcionales | Sí | Bloquear disponibilidad por peluquero, día u horario. |
| Recordatorios email | Sí | Recordatorios antes del turno. |
| Google Calendar | Sí | Integración derivada desde la reserva. |
| Auditoría básica | Sí | Acciones críticas atribuibles a un usuario interno. |

## 4. No entra en el MVP

| Área | Motivo |
| --- | --- |
| Pagos online | Cambia alcance operativo, técnico y comercial. |
| Señas | Aunque se mencionó para peluquería, queda fuera por decisión actual. |
| Facturación automática | No es necesaria para validar el flujo central de reservas. |
| Aplicación móvil nativa | El MVP será web/responsive. |
| Marketplace o multiempresa | El sistema está pensado para Peluquería Sergio. |
| Múltiples sucursales | No fue validado como necesidad actual. |
| Chatbot inteligente | No es necesario para probar el flujo central. |
| Programa de fidelización | Puede evaluarse en una etapa posterior. |
| Cupones o promociones complejas | No forman parte del problema principal. |
| Analítica avanzada | El MVP puede registrar datos, pero no requiere módulo avanzado de BI. |

## 5. Queda pendiente de definición

| Tema | Pendiente | Decisión necesaria |
| --- | --- | --- |
| WhatsApp | Falta proveedor, costo y factibilidad. | Definir si será canal obligatorio, deseable o futuro. |
| Estados similares | Falta confirmar diferencia real entre agendada, reservada y confirmada. | Mantener todos o simplificar catálogo antes de implementar. |
| Descansos | La validación indicó que dependen de la cantidad de clientes. | Confirmar si serán bloqueos manuales o regla automática. |
| Política de no asistencia | Se registra no asistencia, pero no hay sanción definida. | Definir si en el futuro afecta al cliente. |
| Reintentos de Calendar | Se registra falla, pero falta definir política exacta. | Definir cantidad de reintentos y criterio de alerta. |

## 6. Integraciones del MVP

| Integración | Estado en MVP | Regla |
| --- | --- | --- |
| Google OAuth | Incluida | Es el mecanismo obligatorio de identificación de clientes. |
| Google Calendar | Incluida | Es integración derivada; no reemplaza la base de datos. |
| Email | Incluido | Canal mínimo para recordatorios. |
| WhatsApp | Pendiente | Deseado, pero no obligatorio hasta resolver proveedor y costo. |
| Pagos | Excluido | No se modela ni se implementa en esta fase. |

## 7. Supuestos del MVP

- Hay dos profesionales iniciales.
- Ambos pueden trabajar en paralelo.
- El horario base es lunes a sábado de 9:30 a 22:00.
- Una atención dura 60 minutos.
- La agenda se organiza en bloques de 30 minutos.
- El cliente puede elegir peluquero.
- La base de datos es la fuente oficial de verdad.
- Google Calendar es una sincronización derivada.
- La falla de una notificación o de Calendar no invalida una reserva confirmada.
- No hay pagos ni señas en la primera versión.

## 8. Estados incluidos en el alcance

| Estado | En MVP | Observación |
| --- | --- | --- |
| PENDIENTE | Sí | Estado inicial o pendiente de confirmación operativa. |
| EN_ESPERA | Sí | Se conserva por validación de negocio. |
| AGENDADA | Sí | Requiere confirmar diferencia con reservada. |
| RESERVADA | Sí | Requiere confirmar diferencia con agendada. |
| CONFIRMADA | Sí | Requiere confirmar transición exacta. |
| ASISTIO | Sí | Estado final operativo. |
| NO_ASISTIO | Sí | Estado final operativo. |
| CANCELADA | Sí | Necesario porque existe cancelación. |

## 9. Criterios de cierre del MVP

| Criterio | Condición de cierre |
| --- | --- |
| Reserva cliente | Un cliente puede reservar con Google, servicio, peluquero, fecha y horario. |
| Disponibilidad | El sistema no ofrece turnos bloqueados, ocupados o fuera de horario. |
| Solapamientos | No se pueden confirmar dos reservas vigentes para el mismo peluquero y rango horario. |
| Modificación | Un cliente puede modificar una reserva y se revalida disponibilidad. |
| Cancelación | Un cliente puede cancelar hasta una hora antes. |
| Operación interna | Admin puede cargar reservas manuales y gestionar agenda básica. |
| Agenda peluquero | Cada peluquero puede ver su agenda. |
| Historial | Cambios relevantes quedan registrados. |
| Recordatorios | Se pueden programar recordatorios por email. |
| Calendar | Las reservas pueden sincronizarse con Google Calendar sin ser dependientes de él. |
| Fuera de alcance | Pagos, señas y WhatsApp obligatorio no bloquean el MVP. |

## 10. Riesgos de alcance

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| WhatsApp se vuelve obligatorio tarde | Puede agregar complejidad de proveedor y costos. | Mantenerlo como adaptador futuro hasta decidir. |
| Estados duplicados | Puede complicar reportes y lógica de flujo. | Confirmar significado antes de implementar transiciones. |
| Calendar se interpreta como fuente oficial | Puede romper consistencia si falla sincronización. | Documentar que PostgreSQL manda y Calendar deriva. |
| Pagos entran sin planificación | Cambia seguridad, operación y alcance legal/comercial. | Mantener pagos fuera de MVP y crear fase específica si se aprueba. |
| Descansos no definidos | Puede generar disponibilidad poco realista. | Iniciar con bloqueos manuales y medir necesidad real. |

## 11. Referencias internas

| Documento | Uso |
| --- | --- |
| Requisitos funcionales | Define qué debe hacer el sistema. |
| Requisitos no funcionales | Define cualidades técnicas y restricciones operativas. |
| Reglas de negocio | Define reglas operativas validadas. |
| Modelos de datos v1.1 | Define estructura conceptual, lógica y física. |
| ADRs | Explican por qué se tomaron decisiones técnicas. |
| Resultado de validación | Fuente de decisiones aceptadas, pendientes y fuera de alcance. |

## 12. Decisión de alcance

El MVP queda enfocado en resolver reservas confiables, operación interna básica, trazabilidad e integración mínima necesaria. No se incorporan pagos ni señas. WhatsApp queda pendiente. Google Calendar entra como integración derivada, sin desplazar a PostgreSQL como fuente oficial.
