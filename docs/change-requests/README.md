# Change Requests

Esta carpeta registra solicitudes de cambio del cliente o del negocio antes de modificar la documentación formal del proyecto.

El objetivo es evitar cambios impulsivos. Cada pedido nuevo debe pasar por una evaluación mínima de impacto para decidir qué documentos se modifican y qué versión nueva corresponde generar.

## Flujo recomendado

1. Registrar la solicitud en un archivo `CR-XXX-nombre-corto.md`.
2. Describir quién pidió el cambio y qué problema intenta resolver.
3. Evaluar impacto en alcance, reglas, requisitos, casos de uso, modelos, ADRs y trazabilidad.
4. Decidir si el cambio entra ahora, queda pendiente o se rechaza.
5. Actualizar solo los documentos afectados.
6. Registrar qué versiones se generaron.

## Convención de nombres

```txt
CR-001-whatsapp-obligatorio.md
CR-002-pagos-online.md
CR-003-cambio-politica-cancelacion.md
```

## Estados posibles

| Estado | Significado |
| --- | --- |
| Propuesto | El cambio fue registrado pero todavía no evaluado. |
| En análisis | Se está evaluando impacto y decisión. |
| Aprobado | El cambio se acepta y debe implementarse en documentación o producto. |
| Rechazado | El cambio no se incorpora. |
| Diferido | El cambio queda para una fase futura. |
| Implementado en documentación | Los documentos afectados ya fueron actualizados. |

## Regla importante

No se modifica toda la carpeta `docs` por cada cambio. Se modifican solo los documentos afectados por la solicitud.

La matriz de trazabilidad ayuda a detectar qué documentos toca cada cambio.
