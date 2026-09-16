# PROPUESTA TÉCNICA

**Versión:** 1.1  
**Estado:** Actualizado post-validación de negocio  
**Fecha:** septiembre de 2026  
**Responsable:** Proyecto Peluquería Sergio  
**Fuente:** Validación de negocio, reglas de negocio, modelos v1.1 y ADRs aceptados


## Requisitos no funcionales

Sistema web de reservas y gestión de servicios para Peluquería Sergio

Documento actualizado con validación de negocio para análisis y planificación del MVP

Fecha: septiembre de 2026

> Objetivo del documento

> Definir las cualidades técnicas y operativas que deberá cumplir el sistema, priorizando una experiencia simple de reserva, autenticación segura con Google, disponibilidad de turnos, trazabilidad de cambios y facilidad de mantenimiento.

## 1. Propósito y alcance

Este documento adapta criterios de rendimiento, confiabilidad, seguridad, escalabilidad y mantenibilidad a la primera versión del sistema de reservas para Peluquería Sergio.

El sistema deberá permitir que los clientes ingresen con una cuenta de Google, consulten servicios disponibles, seleccionen fecha y horario, elijan peluquero cuando corresponda, confirmen una reserva y reciban información clara sobre el estado del turno. También deberá permitir que el negocio administre servicios, disponibilidad horaria, cancelaciones, modificaciones, reservas manuales y reservas registradas.

## 2. Criterios de prioridad

| Prioridad | Interpretación | Aplicación en el MVP |
| --- | --- | --- |
| Obligatorio | Debe existir para considerar utilizable y seguro el sistema. | Se implementa antes de la primera puesta en producción. |
| Deseable | Aporta calidad operativa, pero puede incorporarse durante la estabilización. | Se incluye si el tiempo y presupuesto del MVP lo permiten. |
| Futuro | Se reserva para una fase posterior, cuando exista uso real y métricas. | No debe complicar la arquitectura inicial. |

## 3. Rendimiento

| ID | Prioridad | Tema | Requisito | Criterio de aceptación |
| --- | --- | --- | --- | --- |
| RNF-REN-01 | Obligatorio | Consulta de turnos | La consulta de disponibilidad por día, servicio y profesional deberá responder en un tiempo percibido como inmediato bajo la carga prevista del MVP. | Medir tiempos p50 y p95 con horarios y reservas representativas. |
| RNF-REN-02 | Obligatorio | Confirmación de reserva | El usuario deberá recibir confirmación clara luego de reservar, cancelar o modificar un turno. | No mostrar éxito hasta confirmar la transacción principal. |
| RNF-REN-03 | Obligatorio | Carga inicial | La pantalla principal de reserva deberá cargar los servicios y próximas disponibilidades sin esperar recursos secundarios. | Diferir imágenes, datos auxiliares o paneles administrativos. |
| RNF-REN-04 | Deseable | Medición operativa | El backend deberá registrar duración, ruta, método y código de respuesta de operaciones relevantes. | Los registros permitirán detectar errores y consultas lentas. |
| RNF-REN-05 | Futuro | Picos de demanda | El sistema podrá incorporar cola o protección adicional ante campañas, promociones o alta demanda puntual. | Aplicar cuando las métricas reales lo justifiquen. |

## 4. Confiabilidad e integridad de datos

| ID | Prioridad | Tema | Requisito | Criterio de aceptación |
| --- | --- | --- | --- | --- |
| RNF-CON-01 | Obligatorio | Fuente oficial | La base de datos será la fuente oficial de usuarios, servicios, horarios y reservas. | Notificaciones, calendarios o reportes serán datos derivados. |
| RNF-CON-02 | Obligatorio | Atomicidad | La reserva deberá guardarse de manera transaccional, evitando cupos duplicados para el mismo horario y recurso. | Dos usuarios no podrán confirmar simultáneamente el mismo turno. |
| RNF-CON-03 | Obligatorio | Estados de turno | Las reservas deberán manejar estados explícitos normalizados a partir del lenguaje real del negocio: pendiente, en espera, agendada, reservada, confirmada, asistió, no asistió y cancelada. | Cada cambio de estado conservará fecha, actor responsable y canal. El motivo será opcional porque la reunión confirmó que no se registra motivo de cancelación. |
| RNF-CON-04 | Obligatorio | Cancelaciones | Cancelar un turno no deberá borrar su historial operativo. | La cancelación conservará quién la realizó, cuándo y desde qué canal. |
| RNF-CON-05 | Obligatorio | Disponibilidad consistente | Los horarios disponibles deberán calcularse desde reglas administrables de agenda, reservas vigentes y bloqueos excepcionales por peluquero. | No depender de edición manual dispersa o datos duplicados. Un peluquero bloqueado en un día puntual no deberá aparecer como seleccionable. |
| RNF-CON-06 | Obligatorio | Respaldos | Se realizarán respaldos automáticos periódicos de la base de datos. | Definir frecuencia, retención y procedimiento de restauración. |
| RNF-CON-07 | Deseable | Recuperación | La restauración de respaldo deberá probarse periódicamente. | Documentar resultado de cada prueba. |
| RNF-CON-08 | Deseable | Reintentos | Una falla temporal al enviar notificación no deberá perder la reserva confirmada. | Registrar la reserva y marcar notificación pendiente o fallida. |

## 5. Seguridad, permisos y privacidad

| ID | Prioridad | Tema | Requisito | Criterio de aceptación |
| --- | --- | --- | --- | --- |
| RNF-SEG-01 | Obligatorio | Autenticación Google | El registro e inicio de sesión de clientes deberá realizarse mediante Google OAuth o un proveedor equivalente configurado de forma segura. | No almacenar contraseñas de clientes si el acceso se resuelve con Google. |
| RNF-SEG-02 | Obligatorio | Cuentas individuales | Toda acción administrativa deberá ser atribuible a una cuenta individual. | No usar cuentas compartidas para operar reservas o configuración. |
| RNF-SEG-03 | Obligatorio | Roles | Los permisos deberán separarse por función. | Como mínimo: cliente, administrador y operador o peluquero. |
| RNF-SEG-04 | Obligatorio | Datos personales | El sistema deberá proteger nombre, email de Google, teléfono, WhatsApp, fecha de nacimiento y datos de reservas del cliente. | Aplicar control de acceso y evitar exposición pública de agendas personales. |
| RNF-SEG-05 | Obligatorio | Secretos | Las credenciales de Google, claves y secretos no deberán quedar en código fuente. | Usar variables de entorno o gestor de secretos. |
| RNF-SEG-06 | Deseable | Sesiones | Las sesiones administrativas deberán expirar y poder revocarse. | Definir duración y política de cierre de sesión. |

## 6. Escalabilidad y capacidad

| ID | Prioridad | Tema | Requisito | Criterio de aceptación |
| --- | --- | --- | --- | --- |
| RNF-ESC-01 | Obligatorio | Volumen inicial | El MVP deberá soportar el volumen esperado de una peluquería local sin requerir arquitectura distribuida. | Validar con cantidad estimada de clientes, servicios y turnos por mes. |
| RNF-ESC-02 | Obligatorio | Servicios configurables | Agregar o modificar servicios no deberá requerir cambios de código. | Nombre, duración, precio interno y disponibilidad deberán ser administrables. El precio no se muestra al cliente en el MVP. |
| RNF-ESC-03 | Obligatorio | Dos profesionales iniciales | El modelo deberá soportar dos profesionales que atienden en paralelo y pueden compartir horario general. | La disponibilidad deberá asociarse a cada peluquero y permitir bloqueos excepcionales individuales. |
| RNF-ESC-04 | Futuro | Sucursales | El sistema podrá evolucionar para varias sucursales si el negocio lo necesita. | No implementar en el MVP salvo confirmación de necesidad real. |

## 7. Mantenibilidad y operabilidad

| ID | Prioridad | Tema | Requisito | Criterio de aceptación |
| --- | --- | --- | --- | --- |
| RNF-MAN-01 | Obligatorio | Configuración simple | Horarios de atención, feriados, servicios, duración, bloques de agenda y bloqueos de peluquero deberán poder mantenerse desde una interfaz administrativa. | El administrador no dependerá del desarrollador para cambios operativos comunes. |
| RNF-MAN-02 | Obligatorio | Errores comprensibles | Los mensajes de error deberán explicar el problema sin exponer detalles técnicos. | El usuario entenderá si el turno dejó de estar disponible, faltan datos o hubo falla temporal. |
| RNF-MAN-03 | Obligatorio | Registro de eventos | El sistema deberá registrar errores relevantes y acciones críticas. | Los logs permitirán investigar reservas fallidas y cambios administrativos. |
| RNF-MAN-04 | Deseable | Panel básico | El administrador podrá ver turnos del día, próximos turnos y cancelaciones recientes. | El panel usará datos actuales sin exportaciones manuales. |
| RNF-MAN-05 | Obligatorio | Google Calendar | El MVP deberá contemplar integración con Google Calendar como sincronización derivada de la reserva. | La reserva en PostgreSQL seguirá siendo la fuente de verdad; si Calendar falla, no deberá romper la reserva. |

## 8. Usabilidad y prevención de errores humanos

| ID | Prioridad | Tema | Requisito | Criterio de aceptación |
| --- | --- | --- | --- | --- |
| RNF-USA-01 | Obligatorio | Flujo de reserva | El flujo de reserva deberá pedir solo los datos necesarios para confirmar el turno. | Servicio, fecha, horario, peluquero elegido y datos de contacto mínimos quedan visibles antes de confirmar. |
| RNF-USA-02 | Obligatorio | Prevención de doble reserva | Si un horario se ocupa mientras el cliente está reservando, el sistema deberá informarlo y ofrecer elegir otro. | No fallar silenciosamente ni confirmar un turno inexistente. |
| RNF-USA-03 | Obligatorio | Responsive | La experiencia deberá funcionar correctamente en teléfono móvil. | La reserva completa debe poder hacerse desde pantalla chica. |
| RNF-USA-04 | Obligatorio | Recordatorios | El sistema deberá contemplar recordatorios antes del turno. | Como mínimo email; WhatsApp queda condicionado a definición de proveedor/costo. Los disparos deseados son entre 24 y 48 horas antes y nuevamente el mismo día. |
| RNF-USA-05 | Deseable | Accesibilidad básica | Los formularios deberán tener etiquetas claras, contraste suficiente y navegación usable con teclado. | Validar al menos flujo de login, selección de servicio y confirmación. |

## 9. Requisitos excluidos del MVP

- Aplicación móvil nativa independiente.

- Pagos online, señas o facturación automática. La validación mencionó seña para peluquería, pero se deja fuera del alcance actual por decisión del proyecto.

- Marketplace de peluquerías o gestión multiempresa.

- Microservicios, Kubernetes, colas distribuidas o arquitectura multi-región.

- Chatbot inteligente o atención automática avanzada.

- Programa de fidelización complejo, cupones dinámicos o analítica avanzada.

## 10. Decisión arquitectónica inicial

Para el MVP conviene priorizar una arquitectura monolítica modular o aplicación web integrada con una base de datos relacional. La reserva de turnos debe quedar protegida por restricciones y transacciones en la capa de persistencia, no solo por validaciones visuales en la interfaz.

Las integraciones externas como Google OAuth, recordatorios, Google Calendar o WhatsApp deberán tratarse como adaptadores reemplazables. Google Calendar pasa a ser integración prevista para el MVP, pero siempre como dato derivado: PostgreSQL conserva la fuente oficial de la reserva. WhatsApp queda pendiente de definición operativa y pagos queda fuera del alcance actual.

## 11. Validación con Peluquería Sergio

Antes de cerrar estos requisitos, deberán validarse con el dueño o responsable operativo y con una persona que use la agenda diaria. La validación deberá confirmar:

- servicios ofrecidos, duración real y precio visible o no visible;

- horarios de atención, días no laborables y tolerancia ante llegadas tarde;

- cantidad de profesionales o recursos que atienden en paralelo;

- política de cancelación, modificación y no asistencia;

- datos mínimos que se pedirán al cliente además del login con Google;

- canales de notificación esperados, como email, WhatsApp o ambos;

- quiénes podrán administrar servicios, horarios y reservas;

- necesidad real de integración con Google Calendar o herramientas existentes.




## 12. Actualización posterior a validación de negocio

La reunión de validación confirmó reglas que corrigen y precisan el alcance inicial:

- Los servicios iniciales son barbería y peluquería.
- Cada atención se estima en una hora por cliente, con agenda organizada en bloques de 30 minutos.
- El horario general validado es de lunes a sábado, de 9:30 a 22:00.
- Los dos profesionales atienden en paralelo, cada uno en su puesto.
- El cliente puede elegir peluquero.
- Se permite reservar para el mismo día y hasta un mes de anticipación.
- El cliente debe ingresar con Google y además se solicitan nombre, teléfono, WhatsApp y fecha de nacimiento.
- El administrador puede cargar reservas manuales tomadas por teléfono.
- La cancelación puede hacerla cliente, administrador o peluquero hasta una hora antes del turno.
- No se registra motivo obligatorio de cancelación.
- Los estados de negocio registrados deben normalizarse antes de implementación para evitar duplicados semánticos.
- Google Calendar se considera dentro del MVP como integración derivada.
- WhatsApp queda pendiente de averiguación.
- Pagos y señas no se incorporan todavía al alcance técnico.
