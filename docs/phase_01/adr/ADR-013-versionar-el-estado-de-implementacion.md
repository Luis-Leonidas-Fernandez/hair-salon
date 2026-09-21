# ADR-013: Versionar y sincronizar el estado de implementación

## Estado

Aceptado

## Contexto

El proyecto tiene requisitos, modelos, reglas, ADRs y TASKS que evolucionan en momentos diferentes. Sin un documento de estado, una persona puede leer una decisión correcta pero desactualizada respecto del código o de la base aplicada.

## Decisión

Mantener un documento versionado de estado de implementación y actualizar la trazabilidad y las TASK cuando una etapa técnica se complete.

La versión v1.2 registra las etapas 1 a 4 implementadas, la migración aplicada y las decisiones que siguen fuera del MVP. Los modelos visuales se actualizan en una revisión gráfica separada para no confundir documentación textual con artefactos de diseño.

## Consecuencias

- El equipo tiene una fuente rápida para conocer qué está implementado.
- Las TASK distinguen infraestructura disponible de trabajo futuro.
- Los cambios quedan vinculados con modelos, migraciones y pruebas.
- Cada nueva decisión arquitectónica o de datos debe agregar o actualizar un ADR.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla |
| --- | --- |
| Actualizar solo el código | El conocimiento se pierde y la trazabilidad queda incompleta. |
| Editar todos los documentos sin control de versión | Aumenta contradicciones y dificulta revisar el motivo del cambio. |
| Usar únicamente comentarios en el código | No cubre decisiones de alcance, datos ni proceso. |

## Evidencia relacionada

- `docs/phase_01/implementation/Estado_implementacion_Peluqueria_Sergio_v1.2.md`
- `docs/phase_01/traceability/Matriz_trazabilidad_Peluqueria_Sergio.md`
- `labs/tasks/README.md`
