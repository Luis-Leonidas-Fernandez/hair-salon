# ADR-011: Centralizar vocabularios del dominio mediante enums

## Estado

Aceptado

## Contexto

Roles, estados, canales y proveedores se repetían como cadenas en modelos, seed, validaciones y documentación. Esa duplicación permite variantes incompatibles, por ejemplo `confirmada`, `CONFIRMADA` o `confirmado`.

## Decisión

Representar los vocabularios estables mediante `StrEnum` y conservar como `.value` los literales ya utilizados por PostgreSQL.

Se centralizan estados de clientes, reservas, notificaciones y Calendar en `domain_types.py`. Roles y tipos de servicio mantienen sus módulos especializados. Las restricciones SQLAlchemy se construyen a partir de esos enums.

## Consecuencias

- El código usa nombres semánticos y la base conserva valores compatibles.
- Se reducen errores por escritura y cambios parciales.
- Agregar un valor requiere revisar enum, modelo, migración, tests y documentación.
- Los enums no reemplazan las reglas de transición de estados.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla |
| --- | --- |
| Cadenas libres | No garantiza consistencia. |
| Constantes dispersas | Mantiene duplicación entre módulos. |
| Enums nativos PostgreSQL | Agrega acoplamiento y migraciones más complejas para un MVP. |

## Evidencia relacionada

- `app/modules/services/shared/domain_types.py`
- `app/modules/services/shared/role_types.py`
- `app/modules/services/shared/service_types.py`
- `tests/test_domain_types.py`
