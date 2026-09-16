# CR-000 WhatsApp obligatorio como ejemplo

Este archivo es un ejemplo explicado. No representa una decisión real del proyecto.

## Metadata

| Campo | Valor |
| --- | --- |
| ID | CR-000 |
| Estado | Ejemplo |
| Fecha | 2026-09-15 |
| Solicitante | Ejemplo de cliente |
| Responsable de análisis | Proyecto Peluquería Sergio |
| Prioridad | Media |
| Versión objetivo | Futuro |

## 1. Solicitud original

> “Queremos que WhatsApp sea obligatorio para confirmar reservas”.

## 2. Problema o necesidad

El negocio quiere reducir ausencias y mejorar la comunicación con clientes. La hipótesis es que WhatsApp tiene mayor tasa de lectura que email.

## 3. Evaluación de impacto

| Área | Impacta | Detalle |
| --- | --- | --- |
| Alcance MVP | Sí | WhatsApp hoy está pendiente, no obligatorio. |
| Reglas de negocio | Sí | Cambia la regla de recordatorios y confirmación. |
| Requisitos funcionales | Sí | RF-021 pasaría de pendiente a obligatorio. |
| Requisitos no funcionales | Sí | Agrega dependencia externa y manejo de fallas. |
| Casos de uso | Sí | CU-013 debería incluir envío WhatsApp. |
| Modelos de datos | Quizás | `notificaciones.canal` ya lo soporta, pero podrían requerirse campos de proveedor. |
| ADRs | Sí | ADR-008 debería revisarse o reemplazarse. |
| Matriz de trazabilidad | Sí | Cambia estado de pendiente a cubierto u obligatorio. |
| Implementación | Sí | Requiere proveedor, credenciales, costos, límites y reintentos. |

## 4. Riesgos

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| No tener proveedor definido | Bloquea implementación real. | Evaluar proveedores antes de aprobar. |
| Costo por mensaje | Puede afectar operación mensual. | Estimar volumen de turnos y mensajes. |
| Falla de envío | Puede confundir si la reserva depende del mensaje. | Mantener PostgreSQL como fuente de verdad. |
| Privacidad | Manejo de teléfono y mensajes. | Documentar consentimiento y uso del dato. |

## 5. Decisión

Diferido. Antes de aprobarlo se necesita definir proveedor, costo, política de consentimiento y comportamiento ante fallas.

## 6. Documentos afectados si se aprobara

| Documento | Acción | Nueva versión |
| --- | --- | --- |
| Alcance MVP | Actualizar WhatsApp de pendiente a incluido | v1.2 |
| Reglas de negocio | Actualizar recordatorios | v1.2 |
| Requisitos funcionales | Cambiar RF-021 | v1.2 |
| Requisitos no funcionales | Agregar dependencia externa y manejo de fallas | v1.2 |
| Casos de uso | Actualizar CU-013 | v1.2 |
| ADRs | Crear nuevo ADR o reemplazar ADR-008 | ADR-009 |
| Matriz de trazabilidad | Actualizar estado y relaciones | v1.2 |

## 7. Criterio de cierre

El cambio quedaría cerrado cuando se confirme proveedor de WhatsApp, costo, alcance funcional, documentos afectados y decisión arquitectónica.

## 8. Nota importante

Este ejemplo muestra por qué no se debe modificar toda la documentación de una vez. Primero se evalúa impacto; después se actualizan solo los documentos afectados.
