# Architecture Decision Records

Esta carpeta registra decisiones técnicas importantes del proyecto Peluquería Sergio.

Los ADR no reemplazan requisitos ni diagramas. Sirven para conservar el porqué de una decisión para que el equipo pueda revisarla, aceptarla o reemplazarla más adelante.

## Convención

- Cada decisión tiene un ID estable: `ADR-001`, `ADR-002`, etc.
- El nombre del archivo usa el ID y un resumen corto en kebab case.
- Los ADR empiezan en estado `Propuesto` hasta validar reglas de negocio con la peluquería.
- Cuando una decisión se confirme, el estado pasa a `Aceptado`.
- Si una decisión cambia, se crea un nuevo ADR y el anterior queda como `Reemplazado`.

## Índice

| ID | Decisión | Estado |
| --- | --- | --- |
| [ADR-001](ADR-001-usar-postgresql-como-base-principal.md) | Usar PostgreSQL como base principal | Aceptado |
| [ADR-002](ADR-002-separar-clientes-y-usuarios-internos.md) | Separar clientes y usuarios internos | Aceptado |
| [ADR-003](ADR-003-modelar-reserva-como-entidad-central.md) | Modelar reserva como entidad central | Aceptado |
| [ADR-004](ADR-004-estrategia-combinada-orm-query-builder-sql.md) | Usar estrategia combinada ORM Query Builder y SQL directo | Aceptado |
| [ADR-005](ADR-005-usar-estados-explicitos-de-reserva.md) | Usar estados explícitos de reserva | Aceptado |
| [ADR-006](ADR-006-postergar-integraciones-externas-del-mvp.md) | Definir integraciones externas del MVP | Reemplazado por ADR-008 |
| [ADR-007](ADR-007-validar-reglas-de-negocio-antes-de-implementar.md) | Validar reglas de negocio antes de implementar | Aceptado |
| [ADR-008](ADR-008-incorporar-google-calendar-y-postergar-whatsapp-pagos.md) | Incorporar Google Calendar y postergar WhatsApp y pagos | Aceptado |
