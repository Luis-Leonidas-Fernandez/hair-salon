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
| [ADR-009](ADR-009-seed-idempotente-y-validado.md) | Usar un seed idempotente y validado | Aceptado |
| [ADR-010](ADR-010-configuracion-tipada-desde-entorno.md) | Centralizar la configuración tipada desde el entorno | Aceptado |
| [ADR-011](ADR-011-centralizar-vocabularios-del-dominio.md) | Centralizar vocabularios del dominio mediante enums | Aceptado |
| [ADR-012](ADR-012-proteger-solapamientos-en-postgresql.md) | Proteger los solapamientos de reservas en PostgreSQL | Aceptado |
| [ADR-013](ADR-013-versionar-el-estado-de-implementacion.md) | Versionar y sincronizar el estado de implementación | Aceptado |
| [ADR-014](ADR-014-autenticacion-google-openid-connect-y-servidor-unificado.md) | Autenticación con Google OpenID Connect y servidor unificado | Aceptado |
| [ADR-015](ADR-015-modulo-de-reservas-y-optimizacion-de-disponibilidad.md) | Módulo de reservas, cálculo de disponibilidad y optimización del callback | Aceptado |
| [ADR-016](ADR-016-home-de-registro-y-refinamiento-de-experiencia-de-usuario.md) | Home de registro, inhabilitación no destructiva de servicios y refinamiento de UX | Aceptado |
