# Matriz de trazabilidad

## Sistema de reservas Peluquería Sergio

Este documento relaciona reglas de negocio, requisitos funcionales, requisitos no funcionales, casos de uso, modelos de datos y ADRs. Su objetivo es verificar que cada funcionalidad importante tenga respaldo documental y que las decisiones técnicas estén alineadas con la validación del negocio.

## 1. Documentos fuente

| Código | Documento | Ruta |
| --- | --- | --- |
| BR | Reglas de negocio | `docs/phase_01/business-rules/Reglas_de_negocio_Peluqueria_Sergio.md` |
| RF | Requisitos funcionales | `docs/phase_01/requirements/v1.1/Requisitos_funcionales_Peluqueria_Sergio_v1.1.md` |
| RNF | Requisitos no funcionales | `docs/phase_01/requirements/v1.1/Requisitos_no_funcionales_Peluqueria_Sergio_v1.1.md` |
| CU | Casos de uso | `docs/phase_01/use-cases/Casos_de_uso_Peluqueria_Sergio.md` |
| MVP | Alcance MVP | `docs/phase_01/scope/Alcance_MVP_Peluqueria_Sergio.md` |
| VAL | Resultado de validación | `docs/phase_01/validations/v1.1/Resultado_reunion_validacion_Peluqueria_Sergio_v1.1.md` |
| MC | Modelo conceptual | `docs/phase_01/data-modeling/modelado/modelo-conceptual.png` |
| ML | Modelo lógico | `docs/phase_01/data-modeling/modelado/modelo-logico.png` |
| MF | Modelo físico | `docs/phase_01/data-modeling/modelado/modelo-fisico.png` |
| ADR | Architecture Decision Records | `docs/phase_01/adr/` |

## 2. Matriz principal

| Tema | Regla / decisión fuente | RF | RNF | CU | Modelo | ADR | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Login con Google | BR-Reservas, MVP-Integraciones, VAL-Login | RF-001 | RNF-SEG-01 | CU-001 | clientes.email_google, clientes.google_sub | ADR-002, ADR-014 | Implementado con tests |
| Datos del cliente | BR-Reservas, VAL-Datos cliente | RF-002 | RNF-SEG-04 | CU-002 | clientes | ADR-002, ADR-014 | Implementado con tests |
| Servicios iniciales | BR-Servicios, VAL-Servicios | RF-003, RF-013 | RNF-ESC-02 | CU-003, CU-007 | servicios | ADR-003 | Cubierto |
| Selección de peluquero | BR-Reservas, VAL-Elección | RF-004 | RNF-USA-01 | CU-003 | reservas.peluquero_id | ADR-003 | Cubierto |
| Consulta de disponibilidad | BR-Horarios, BR-Prevención | RF-005 | RNF-CON-05 | CU-003, CU-008 | disponibilidades | ADR-001, ADR-003 | Cubierto |
| Reserva de turno | BR-Reservas, MVP-Entra | RF-006, RF-007, RF-008 | RNF-CON-02 | CU-003 | reservas | ADR-001, ADR-003 | Cubierto |
| Ventana de reserva | BR-Reservas, MVP-Supuestos | RF-007, RF-008 | RNF-USA-01 | CU-003 | reservas.fecha_inicio | ADR-003 | Cubierto |
| Prevención de solapamientos | BR-Prevención, MVP-Cierre | RF-025 | RNF-CON-02, RNF-USA-02 | CU-003 | reservas.fecha_fin, exclusión GiST | ADR-001, ADR-003 | Cubierto en PostgreSQL |
| Modificación de turno | BR-Modificación | RF-009 | RNF-CON-03, RNF-CON-04 | CU-004 | reservas, historial_reservas | ADR-003, ADR-005 | Cubierto |
| Cancelación cliente | BR-Cancelaciones | RF-010 | RNF-CON-04 | CU-005 | reservas.estado, historial_reservas | ADR-005 | Cubierto |
| Cancelación interna | BR-Cancelaciones | RF-011 | RNF-CON-04 | CU-005, CU-011 | reservas, historial_reservas | ADR-005 | Cubierto |
| Reserva manual | BR-Reservas | RF-012 | RNF-SEG-02 | CU-006 | reservas.canal_reserva | ADR-003 | Cubierto |
| Gestión de servicios | BR-Servicios | RF-013 | RNF-MAN-01 | CU-007 | servicios | ADR-004 | Cubierto |
| Gestión de horarios | BR-Horarios | RF-014 | RNF-MAN-01 | CU-008 | disponibilidades | ADR-004 | Cubierto |
| Bloqueos excepcionales | BR-Horarios | RF-015 | RNF-CON-05 | CU-009 | disponibilidades.bloqueo_excepcional | ADR-003 | Cubierto |
| Agenda del peluquero | BR-Permisos, MVP-Entra | RF-016 | RNF-SEG-03 | CU-010 | reservas, usuarios | ADR-002, ADR-003 | Cubierto |
| Agenda administrativa | BR-Permisos, MVP-Entra | RF-017 | RNF-MAN-04 | CU-014 | reservas, usuarios | ADR-002 | Cubierto |
| Estados de reserva | BR-Estados, VAL-Estados | RF-018 | RNF-CON-03 | CU-011 | reservas.estado | ADR-005 | Cubierto con pendiente |
| Historial de reserva | BR-Modificación, BR-Cancelación | RF-019 | RNF-CON-04, RNF-MAN-03 | CU-004, CU-005, CU-011 | historial_reservas | ADR-003, ADR-005 | Cubierto |
| Recordatorios email | BR-Recordatorios | RF-020 | RNF-USA-04, RNF-CON-08 | CU-013 | notificaciones | ADR-008 | Cubierto |
| WhatsApp | BR-Recordatorios, MVP-Pendientes | RF-021 | RNF-MAN-05 | CU-013 | notificaciones.canal | ADR-008 | Pendiente |
| Google Calendar | BR-Calendar, MVP-Integraciones | RF-022, RF-023 | RNF-MAN-05 | CU-012 | eventos_calendario | ADR-008 | Cubierto |
| Auditoría | BR-Permisos, MVP-Cierre | RF-024 | RNF-MAN-03 | CU-006, CU-014 | auditoria_cambios | ADR-001, ADR-004 | Cubierto |
| Pagos y señas | MVP-No entra, BR-Fuera de alcance | No aplica | RNF-Excluidos | No aplica | No modelado | ADR-008 | Excluido |

## 3. Trazabilidad por ADR

| ADR | Decisión | Elementos respaldados |
| --- | --- | --- |
| ADR-001 | Usar PostgreSQL como base principal | Reservas, disponibilidad, prevención de solapamientos, auditoría e integridad. |
| ADR-002 | Separar clientes y usuarios internos | Login cliente, permisos internos, agenda del peluquero y administración. |
| ADR-003 | Modelar reserva como entidad central | Reserva, modificación, cancelación, historial, notificaciones y Calendar derivado. |
| ADR-004 | Usar estrategia combinada ORM Query Builder y SQL directo | Consultas de agenda, disponibilidad, reportes y prevención de N+1. |
| ADR-005 | Usar estados explícitos de reserva | Estados controlados, historial, reportes y cambios de estado. |
| ADR-006 | Definir integraciones externas del MVP | Reemplazado por ADR-008. |
| ADR-007 | Validar reglas de negocio antes de implementar | Validación del negocio y actualización documental. |
| ADR-008 | Incorporar Google Calendar y postergar WhatsApp y pagos | Google Calendar en MVP, WhatsApp pendiente, pagos y señas fuera. |
| ADR-009 | Usar un seed idempotente y validado | Datos iniciales, validaciones previas y transacción atómica. |
| ADR-010 | Centralizar la configuración tipada desde el entorno | `.env`, settings, conexión de base y seed. |
| ADR-011 | Centralizar vocabularios del dominio mediante enums | Estados, canales, roles y restricciones compatibles con PostgreSQL. |
| ADR-012 | Proteger los solapamientos de reservas en PostgreSQL | `fecha_fin`, `btree_gist` y exclusión GiST. |
| ADR-013 | Versionar y sincronizar el estado de implementación | Estado v1.2 y v1.3, trazabilidad y TASKS alineadas. |
| ADR-014 | Autenticación con Google OpenID Connect y servidor unificado | Identidad OIDC, inmutabilidad `google_sub`, sesión JWT y hosting unificado. |

## 4. Cobertura por modelo de datos

| Modelo / tabla | Requisitos cubiertos | Observación |
| --- | --- | --- |
| clientes | RF-001, RF-002 | Identidad de cliente con Google y datos de contacto. |
| usuarios | RF-016, RF-017, RF-024 | Usuarios internos, peluqueros y administrador. |
| roles | RF-016, RF-017, RF-024 | Control de permisos internos. |
| servicios | RF-003, RF-013 | Servicios configurables, duración y precio interno. |
| usuarios_servicios | RF-004, RF-013 | Relación entre peluqueros y servicios ofrecidos. |
| disponibilidades | RF-005, RF-014, RF-015 | Horarios, bloques y bloqueos excepcionales. |
| reservas | RF-006 a RF-012, RF-018, RF-025 | Entidad central del sistema. |
| historial_reservas | RF-009, RF-010, RF-011, RF-019 | Trazabilidad del ciclo de vida de la reserva. |
| notificaciones | RF-020, RF-021 | Recordatorios por email y canal WhatsApp pendiente. |
| eventos_calendario | RF-022, RF-023 | Sincronización derivada con Google Calendar. |
| auditoria_cambios | RF-024 | Acciones críticas administrativas. |

## 5. Pendientes trazables

| Pendiente | Documentos afectados | Acción recomendada |
| --- | --- | --- |
| Definir WhatsApp | RF-021, CU-013, ADR-008, MVP | Resolver proveedor, costo y obligatoriedad. |
| Diferenciar AGENDADA, RESERVADA y CONFIRMADA | BR, RF-018, CU-011, ADR-005, modelos | Confirmar si son estados distintos o se simplifican. |
| Definir descansos | BR, RF-014, RF-015, CU-008, CU-009 | Mantener bloqueos manuales hasta validar automatización. |
| Política de reintentos Calendar | RF-023, CU-012, ADR-008 | Definir cantidad de reintentos y criterio de alerta. |
| Actualizar desajuste objeto-relacional | ADR-004, modelos, RF | Alinear el documento con estados, Calendar y modelos v1.1. |

## 6. Verificación de consistencia

| Pregunta de control | Resultado |
| --- | --- |
| ¿Cada funcionalidad crítica tiene caso de uso? | Sí. |
| ¿Cada integración incluida está respaldada por ADR? | Sí: Google OAuth y Calendar quedan cubiertos; WhatsApp pendiente. |
| ¿Pagos y señas aparecen como funcionalidad del MVP? | No. Quedan excluidos. |
| ¿Los modelos reflejan los requisitos principales? | Sí, con la integridad física de reservas implementada en v1.2. |
| ¿Hay pendientes visibles antes de implementar? | Sí: WhatsApp, estados similares, descansos y reintentos Calendar. |

## 7. Conclusión

La trazabilidad muestra que el MVP tiene cobertura documental suficiente para continuar con la implementación. La prevención de solapamientos ya está respaldada por una restricción PostgreSQL aplicada, además de las validaciones previstas en backend. Las brechas restantes son decisiones pendientes explícitas: WhatsApp, estados similares, descansos y reintentos de Calendar.
