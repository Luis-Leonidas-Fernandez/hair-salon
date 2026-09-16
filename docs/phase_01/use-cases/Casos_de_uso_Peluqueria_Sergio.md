# Casos de uso

## Sistema de reservas Peluquería Sergio

Este documento describe cómo interactúan los actores con el sistema durante el MVP. Los casos de uso conectan reglas de negocio, requisitos funcionales, alcance MVP y modelos de datos.

## 1. Actores

| Actor | Descripción |
| --- | --- |
| Cliente | Persona que usa Google OAuth para reservar, modificar o cancelar sus turnos. |
| Peluquero | Usuario interno que consulta su agenda y actualiza estados operativos de reservas. |
| Administrador | Usuario interno que configura servicios, disponibilidad, bloqueos y reservas manuales. |
| Sistema | Componentes internos que validan disponibilidad, envían recordatorios y sincronizan Calendar. |

## 2. Resumen de casos de uso

| ID | Caso de uso | Actor principal | Prioridad |
| --- | --- | --- | --- |
| CU-001 | Login con Google | Cliente | Obligatoria |
| CU-002 | Completar datos del cliente | Cliente | Obligatoria |
| CU-003 | Reservar turno | Cliente | Obligatoria |
| CU-004 | Modificar turno | Cliente | Obligatoria |
| CU-005 | Cancelar turno | Cliente | Obligatoria |
| CU-006 | Cargar reserva manual | Administrador | Obligatoria |
| CU-007 | Configurar servicios | Administrador | Obligatoria |
| CU-008 | Configurar disponibilidad | Administrador | Obligatoria |
| CU-009 | Bloquear disponibilidad | Administrador | Obligatoria |
| CU-010 | Consultar agenda del peluquero | Peluquero | Obligatoria |
| CU-011 | Cambiar estado de reserva | Peluquero / Administrador | Obligatoria |
| CU-012 | Sincronizar Google Calendar | Sistema | Obligatoria |
| CU-013 | Programar recordatorios | Sistema | Obligatoria |
| CU-014 | Consultar agenda administrativa | Administrador | Obligatoria |

## CU-001 Login con Google

| Campo | Detalle |
| --- | --- |
| Actor principal | Cliente |
| Objetivo | Identificar al cliente mediante Google OAuth. |
| Precondición | El cliente tiene una cuenta de Google válida. |
| Disparador | El cliente inicia el flujo de reserva o entra a su cuenta. |
| Resultado esperado | El sistema identifica al cliente por email de Google. |

### Flujo principal

1. El cliente selecciona ingresar con Google.
2. El sistema redirige al proveedor de autenticación.
3. Google valida la identidad.
4. El sistema recibe la identidad validada.
5. El sistema busca o crea el cliente por email de Google.
6. El sistema permite continuar el flujo.

### Alternativas y excepciones

- Si Google rechaza la autenticación, el sistema no permite continuar.
- Si falta información obligatoria del cliente, continúa CU-002.

## CU-002 Completar datos del cliente

| Campo | Detalle |
| --- | --- |
| Actor principal | Cliente |
| Objetivo | Registrar datos mínimos para operar reservas. |
| Precondición | El cliente ingresó con Google. |
| Resultado esperado | El cliente queda con datos completos. |

### Flujo principal

1. El sistema detecta datos incompletos.
2. El cliente completa nombre, teléfono, WhatsApp y fecha de nacimiento.
3. El sistema valida campos obligatorios.
4. El sistema guarda los datos.
5. El cliente puede continuar con la reserva.

### Alternativas y excepciones

- Si falta un dato obligatorio, el sistema informa el campo faltante.
- Si el teléfono o WhatsApp tiene formato inválido, el sistema solicita corrección.

## CU-003 Reservar turno

| Campo | Detalle |
| --- | --- |
| Actor principal | Cliente |
| Objetivo | Crear una reserva válida sin solapamientos. |
| Precondición | Cliente autenticado y con datos completos. |
| Resultado esperado | Reserva registrada, historial inicial creado y sincronización derivada programada. |

### Flujo principal

1. El cliente selecciona servicio.
2. El cliente selecciona peluquero.
3. El cliente selecciona fecha dentro de la ventana permitida.
4. El sistema consulta disponibilidad.
5. El cliente selecciona horario.
6. El sistema valida disponibilidad, duración y solapamientos.
7. El sistema registra la reserva.
8. El sistema crea historial inicial.
9. El sistema programa recordatorios.
10. El sistema intenta sincronizar Google Calendar.
11. El sistema muestra confirmación.

### Alternativas y excepciones

- Si el horario ya no está disponible, el sistema solicita elegir otro.
- Si la fecha supera un mes de anticipación, el sistema impide confirmar.
- Si falla Calendar, la reserva queda válida y se registra falla de sincronización.
- Si falla una notificación, la reserva queda válida.

## CU-004 Modificar turno

| Campo | Detalle |
| --- | --- |
| Actor principal | Cliente |
| Objetivo | Cambiar datos de una reserva existente. |
| Precondición | La reserva existe y pertenece al cliente. |
| Resultado esperado | La reserva se actualiza y queda historial del cambio. |

### Flujo principal

1. El cliente selecciona una reserva propia.
2. El sistema verifica que la reserva pueda modificarse.
3. El cliente cambia fecha, horario, servicio o peluquero.
4. El sistema recalcula disponibilidad.
5. El sistema valida solapamientos.
6. El sistema actualiza la reserva.
7. El sistema registra historial.
8. El sistema actualiza recordatorios y Calendar si corresponde.

### Alternativas y excepciones

- Si el nuevo horario no está disponible, no se aplica el cambio.
- Si la reserva ya está cancelada o finalizada, el sistema impide modificar.

## CU-005 Cancelar turno

| Campo | Detalle |
| --- | --- |
| Actor principal | Cliente |
| Objetivo | Cancelar un turno dentro de la regla permitida. |
| Precondición | La reserva pertenece al cliente y no está finalizada. |
| Resultado esperado | La reserva queda en estado CANCELADA y conserva historial. |

### Flujo principal

1. El cliente selecciona cancelar reserva.
2. El sistema valida que falte al menos una hora para el turno.
3. El sistema cambia el estado a CANCELADA.
4. El sistema registra actor, fecha y estado anterior.
5. El sistema libera disponibilidad según reglas de agenda.
6. El sistema actualiza Calendar si corresponde.

### Alternativas y excepciones

- Si falta menos de una hora, el sistema impide cancelación por cliente.
- Si Calendar falla al actualizar, la cancelación sigue siendo válida en el sistema.

## CU-006 Cargar reserva manual

| Campo | Detalle |
| --- | --- |
| Actor principal | Administrador |
| Objetivo | Registrar una reserva tomada fuera del canal web. |
| Precondición | El administrador está autenticado. |
| Resultado esperado | Reserva creada con canal ADMIN o TELEFONO. |

### Flujo principal

1. El administrador ingresa al panel de reservas.
2. Busca o crea el cliente.
3. Selecciona servicio, peluquero, fecha y horario.
4. El sistema valida disponibilidad.
5. El administrador confirma la reserva.
6. El sistema registra canal y actor responsable.
7. El sistema crea historial inicial.

### Alternativas y excepciones

- Si el horario está ocupado, el sistema impide guardar.
- Si faltan datos mínimos del cliente, el sistema solicita completarlos.

## CU-007 Configurar servicios

| Campo | Detalle |
| --- | --- |
| Actor principal | Administrador |
| Objetivo | Mantener servicios disponibles sin cambiar código. |
| Precondición | El administrador está autenticado. |
| Resultado esperado | Servicios actualizados para el flujo de reserva. |

### Flujo principal

1. El administrador accede a configuración de servicios.
2. Crea o edita nombre, tipo, duración, precio interno y estado activo.
3. El sistema valida datos obligatorios.
4. El sistema guarda los cambios.
5. Los servicios activos quedan disponibles para reservas.

### Alternativas y excepciones

- Si un servicio se desactiva, no debe aparecer para nuevas reservas.
- Las reservas existentes conservan su referencia histórica.

## CU-008 Configurar disponibilidad

| Campo | Detalle |
| --- | --- |
| Actor principal | Administrador |
| Objetivo | Definir horarios disponibles por peluquero. |
| Precondición | Existen usuarios internos con rol peluquero. |
| Resultado esperado | La consulta de turnos usa la disponibilidad configurada. |

### Flujo principal

1. El administrador selecciona un peluquero.
2. Define día de semana, hora desde, hora hasta y bloque de 30 minutos.
3. El sistema valida que el rango horario sea válido.
4. El sistema guarda disponibilidad.
5. El sistema usa esa regla para mostrar horarios disponibles.

### Alternativas y excepciones

- Si el rango horario es inválido, el sistema no guarda.
- Si hay superposición de reglas, el sistema debe advertir o consolidar según diseño técnico.

## CU-009 Bloquear disponibilidad

| Campo | Detalle |
| --- | --- |
| Actor principal | Administrador |
| Objetivo | Impedir reservas en días u horarios puntuales. |
| Precondición | Existe disponibilidad base para el peluquero. |
| Resultado esperado | El horario bloqueado no aparece disponible. |

### Flujo principal

1. El administrador selecciona peluquero y rango de bloqueo.
2. Indica si corresponde un motivo opcional.
3. El sistema registra el bloqueo excepcional.
4. El sistema excluye ese rango de la disponibilidad.

### Alternativas y excepciones

- Si ya existen reservas en el rango, el sistema debe advertir antes de bloquear.
- El bloqueo no elimina reservas existentes automáticamente.

## CU-010 Consultar agenda del peluquero

| Campo | Detalle |
| --- | --- |
| Actor principal | Peluquero |
| Objetivo | Ver los turnos propios. |
| Precondición | El peluquero está autenticado. |
| Resultado esperado | El peluquero ve su agenda por fecha y estado. |

### Flujo principal

1. El peluquero ingresa a su agenda.
2. El sistema lista reservas asociadas a ese peluquero.
3. El peluquero filtra por fecha o estado.
4. El sistema muestra datos relevantes del turno.

### Alternativas y excepciones

- El peluquero no ve la agenda completa salvo permiso futuro.
- Si no hay reservas, el sistema muestra agenda vacía.

## CU-011 Cambiar estado de reserva

| Campo | Detalle |
| --- | --- |
| Actor principal | Peluquero o Administrador |
| Objetivo | Reflejar el estado operativo real del turno. |
| Precondición | La reserva existe. |
| Resultado esperado | Estado actualizado e historial registrado. |

### Flujo principal

1. El usuario interno selecciona una reserva.
2. Elige nuevo estado permitido.
3. El sistema valida transición básica.
4. El sistema actualiza estado.
5. El sistema registra historial con actor y fecha.

### Alternativas y excepciones

- Si el estado no pertenece al catálogo permitido, el sistema rechaza el cambio.
- Si la transición no está permitida, el sistema informa el motivo.

## CU-012 Sincronizar Google Calendar

| Campo | Detalle |
| --- | --- |
| Actor principal | Sistema |
| Objetivo | Reflejar reservas en Google Calendar como integración derivada. |
| Precondición | Existe una reserva creada o modificada. |
| Resultado esperado | Calendar queda sincronizado o se registra falla. |

### Flujo principal

1. El sistema detecta una reserva creada, modificada o cancelada.
2. El sistema genera o actualiza el evento de Calendar.
3. Calendar responde exitosamente.
4. El sistema registra identificador externo y estado sincronizado.

### Alternativas y excepciones

- Si Calendar falla, la reserva sigue válida.
- El sistema registra estado fallido y último error.
- El sistema puede reintentar según política definida.

## CU-013 Programar recordatorios

| Campo | Detalle |
| --- | --- |
| Actor principal | Sistema |
| Objetivo | Programar avisos previos al turno. |
| Precondición | Existe una reserva vigente. |
| Resultado esperado | Recordatorios programados por email. |

### Flujo principal

1. El sistema identifica una reserva vigente.
2. Calcula recordatorio entre 24 y 48 horas antes.
3. Calcula recordatorio para el mismo día.
4. Registra notificaciones pendientes.
5. Envía o deja listas las notificaciones según el mecanismo implementado.

### Alternativas y excepciones

- Si falla el envío, la reserva sigue válida.
- WhatsApp queda pendiente hasta definir proveedor y costo.

## CU-014 Consultar agenda administrativa

| Campo | Detalle |
| --- | --- |
| Actor principal | Administrador |
| Objetivo | Ver y operar la agenda general. |
| Precondición | El administrador está autenticado. |
| Resultado esperado | El administrador puede revisar reservas por fecha, peluquero y estado. |

### Flujo principal

1. El administrador ingresa a la agenda general.
2. Selecciona fecha, peluquero o estado.
3. El sistema lista reservas coincidentes.
4. El administrador puede abrir detalle, modificar, cancelar o cambiar estado según permisos.

### Alternativas y excepciones

- Si no hay reservas para los filtros seleccionados, el sistema muestra resultado vacío.
- Las acciones realizadas desde la agenda deben quedar registradas.

## 3. Reglas transversales de los casos de uso

- Ningún caso de uso debe confirmar una reserva solapada para el mismo peluquero.
- La base de datos es la fuente oficial de reservas.
- Google Calendar no reemplaza la reserva interna.
- Una falla de notificación o Calendar no invalida la reserva.
- Pagos y señas no forman parte de estos casos de uso.
- WhatsApp queda como extensión futura o pendiente.

## 4. Criterio de aceptación general

Los casos de uso quedan cubiertos cuando cliente, peluquero, administrador y sistema pueden ejecutar sus flujos principales sin romper reglas de disponibilidad, trazabilidad, permisos ni alcance MVP.
