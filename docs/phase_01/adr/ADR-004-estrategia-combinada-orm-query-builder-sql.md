# ADR-004: Usar estrategia combinada ORM Query Builder y SQL directo

## Estado

Aceptado

## Contexto

El documento de desajuste objeto-relacional identifica que el backend trabajará con objetos anidados, mientras PostgreSQL guarda información normalizada en tablas.

Un ORM o query builder reduce código repetitivo, pero no elimina la necesidad de entender SQL, relaciones, índices, transacciones y consultas críticas.

## Decisión

Usar una estrategia combinada:

- ORM o query builder para operaciones comunes de CRUD.
- SQL directo o query builder explícito para agenda diaria, reportes, validación de solapamientos, operaciones masivas y consultas donde importe controlar el plan de consulta.

## Consecuencias

- Se evita depender ciegamente de abstracciones que puedan generar N+1.
- El equipo conserva control sobre consultas críticas.
- El código debe separar dominio y persistencia mediante repositorios o servicios.
- Cada consulta SQL directa debe documentar por qué existe.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla ahora |
| --- | --- |
| ORM para todo | Puede ocultar consultas ineficientes y complicar optimizaciones de agenda. |
| SQL directo para todo | Aumenta código repetitivo y reduce velocidad para CRUD simple. |

## Evidencia relacionada

- `docs/phase_01/data-modeling/desajuste-objeto-realcional/v1.1/Desajuste_objeto_relacional_Peluqueria_Sergio_v1.1.md`
