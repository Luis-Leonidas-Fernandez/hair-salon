# ADR-009: Usar un seed idempotente y validado

## Estado

Aceptado

## Contexto

El entorno necesita datos iniciales para operar: roles internos, administrador, dos peluqueros, servicios, capacidades y disponibilidades. Ejecutar el seed más de una vez no debe duplicar registros ni reactivar silenciosamente datos que alguien desactivó.

## Decisión

Implementar el seed como un caso de uso idempotente, con catálogo separado, configuración externa y validaciones previas a la mutación.

El seed debe:

- leer identidades desde `Settings` y no desde literales sensibles;
- utilizar catálogos tipados para roles y servicios;
- rechazar roles, usuarios, servicios, relaciones o disponibilidades existentes que estén inactivos o sean incompatibles;
- confirmar todos los cambios en una única transacción;
- dejar la lógica de validación separada de la orquestación.

## Consecuencias

- El seed puede ejecutarse de forma segura en desarrollo.
- Una configuración inconsistente falla antes de dejar datos parcialmente cargados.
- Los cambios de negocio se realizan en catálogos y validadores pequeños, respetando SRP.
- El seed no debe usarse para corregir manualmente datos operativos existentes.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla |
| --- | --- |
| Insertar datos manualmente | No es repetible ni auditable. |
| Ignorar conflictos existentes | Oculta configuraciones incorrectas y puede producir reservas inválidas. |
| Reactivar todo automáticamente | Puede sobrescribir una decisión operativa legítima. |

## Evidencia relacionada

- `scripts/seed_initial_data.py`
- `app/modules/services/shared/seed_plan.py`
- `app/modules/services/shared/seed_validations.py`
- `tests/test_seed_validations.py`
