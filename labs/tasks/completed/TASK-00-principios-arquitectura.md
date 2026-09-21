# TASK-00 — Convenciones de arquitectura y calidad

## Resultado esperado

Antes de implementar funcionalidades, el equipo debe acordar estas fronteras. El objetivo no es agregar capas por moda, sino evitar que FastAPI, SQLAlchemy o Google definan el negocio.

## Camino rápido

1. Usar módulos verticales: `identity`, `services`, `bookings` e `integrations`.
2. Mantener routers delgados: validan HTTP y delegan casos de uso.
3. Mantener reglas del negocio fuera de routers y adaptadores externos.
4. Inyectar `AsyncSession` y puertos externos; no usar estado global mutable.
5. Proteger invariantes críticas también en PostgreSQL.

## Aplicación de SOLID

| Principio | Aplicación en After Look |
|---|---|
| SRP | Router HTTP, caso de uso, consulta SQL y adaptador Google tienen responsabilidades distintas. |
| OCP | Nuevos canales de notificación o calendarios se agregan implementando un puerto, sin modificar reservas. |
| LSP | Un adaptador falso para tests debe poder reemplazar al adaptador Google sin cambiar el caso de uso. |
| ISP | Definir puertos pequeños, por ejemplo `CalendarPort`, en lugar de un cliente externo gigante. |
| DIP | Los casos de uso dependen de protocolos y contratos; FastAPI y Google son detalles externos. |

## Convenciones técnicas

- Python 3.14 y anotaciones modernas (`X | None`, `list[X]`).
- SQLAlchemy 2 con `select()` y una `AsyncSession` por request o tarea.
- Nunca compartir una misma `AsyncSession` entre tareas concurrentes.
- Pydantic para contratos HTTP; modelos ORM solo en persistencia.
- Datetimes conscientes de zona horaria; negocio en `America/Argentina/Buenos_Aires` y persistencia `TIMESTAMPTZ`.
- Excepciones de aplicación (`NotFoundError`, `ConflictError`, `BusinessRuleError`), no `ValueError` genérico.
- Migraciones versionadas; nunca modificar una migración ya aplicada en ambientes compartidos.
- No realizar llamadas a Google dentro de la transacción que crea una reserva.

## Estructura objetivo

```text
app/modules/
├── identity/
│   ├── router.py
│   ├── schemas.py
│   └── service.py
├── services/
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   └── shared/models.py
├── bookings/
│   ├── router.py
│   ├── schemas.py
│   └── service.py
└── integrations/
    └── google_calendar/
        ├── adapter.py
        ├── port.py
        └── worker.py
```

## Fuera de alcance

- Microservicios.
- Event sourcing.
- Pagos y señas.
- WhatsApp hasta definir proveedor, costo y requisitos.
- Repositorios genéricos que solo oculten SQLAlchemy sin aportar una frontera real.

## Referencias oficiales

- [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [PostgreSQL range constraints](https://www.postgresql.org/docs/18/rangetypes.html)
- [Google OAuth for web server applications](https://developers.google.com/identity/protocols/oauth2/web-server)

## Checklist

- [ ] Cada módulo tiene una responsabilidad reconocible.
- [ ] Los routers no contienen SQL ni reglas de negocio.
- [ ] Los servicios no dependen de objetos HTTP.
- [ ] Las integraciones externas se acceden mediante puertos pequeños.
- [ ] Las invariantes críticas tienen respaldo en PostgreSQL.
