# Desajuste objeto-relacional

## Aplicación al sistema de reservas Peluquería Sergio

**Versión:** 1.1  
**Estado:** Actualizado post-validación de negocio  
**Fecha:** septiembre de 2026  
**Responsable:** Proyecto Peluquería Sergio  
**Fuente:** Modelos de datos v1.1, requisitos versionados v1.1, reglas de negocio, alcance MVP, casos de uso, matriz de trazabilidad y ADRs aceptados

> **Idea central:** el backend trabaja con objetos de dominio como `ReservaDetalle`, `Cliente`, `Servicio`, `Peluquero`, `Notificacion` y `EventoCalendario`, mientras PostgreSQL persiste esos datos en tablas normalizadas. La traducción entre ambos mundos genera desajuste objeto-relacional y debe diseñarse de forma consciente.

## 1. Qué significa el desajuste objeto-relacional

Muchas aplicaciones modelan el negocio con objetos o estructuras anidadas. En Peluquería Sergio, una reserva completa no es solo una fila: incluye cliente, servicio, peluquero elegido, estado normalizado, historial de cambios, notificaciones y sincronización derivada con Google Calendar.

PostgreSQL, en cambio, organiza esa información en tablas, claves primarias, claves foráneas, índices, restricciones y transacciones. El desajuste aparece porque el código necesita operar con estructuras cómodas para el dominio, mientras la base necesita una forma normalizada, consistente y consultable.

La solución no es esconder la base de datos detrás de un ORM sin criterio. La solución es definir una frontera clara entre dominio y persistencia.

## 2. Modelo de dominio actualizado

En el backend, una pantalla de detalle de reserva podría necesitar un objeto como este:

```ts
const reserva = {
  id: 42,
  estado: "CONFIRMADA",
  canalReserva: "WEB",
  fechaInicio: "2026-09-18T15:00:00-03:00",
  duracionMinutos: 60,
  cliente: {
    id: 7,
    nombre: "Juan Perez",
    emailGoogle: "juan@gmail.com",
    telefono: "1122334455",
    whatsapp: "1122334455",
    fechaNacimiento: "1990-05-20"
  },
  servicio: {
    id: 3,
    nombre: "Corte y barba",
    tipoServicio: "BARBERIA",
    duracionMinutos: 60,
    precioInterno: 12000
  },
  peluquero: {
    id: 2,
    nombreCompleto: "Sergio",
    rol: "PELUQUERO"
  },
  notificaciones: [
    { canal: "EMAIL", estadoEnvio: "PENDIENTE" }
  ],
  eventoCalendario: {
    proveedor: "GOOGLE_CALENDAR",
    eventoExternoId: "abc123",
    estadoSync: "SINCRONIZADO"
  },
  historial: [
    { estadoAnterior: "RESERVADA", estadoNuevo: "CONFIRMADA" }
  ]
};
```

En PostgreSQL, esa información queda distribuida entre varias tablas:

- `clientes`
- `usuarios`
- `roles`
- `servicios`
- `usuarios_servicios`
- `disponibilidades`
- `reservas`
- `historial_reservas`
- `notificaciones`
- `eventos_calendario`
- `auditoria_cambios`

Por lo tanto, el backend debe reconstruir la respuesta final mediante JOIN, consultas explícitas, proyecciones de lectura o un ORM/query builder usado con criterio.

## 3. Desajustes concretos del proyecto

| Desajuste | Ejemplo en dominio | Representación relacional | Riesgo si se ignora |
| --- | --- | --- | --- |
| Objeto anidado | `ReservaDetalle.cliente.nombre` | `reservas.cliente_id` más JOIN con `clientes` | Consultas N+1 o respuestas incompletas. |
| Estado controlado | `reserva.estado = CONFIRMADA` | `reservas.estado` con catálogo o `CHECK` | Texto libre, estados duplicados y reportes rotos. |
| Disponibilidad calculada | `horariosDisponibles()` | `disponibilidades`, bloqueos y reservas vigentes | Turnos solapados o disponibilidad falsa. |
| Historial | `reserva.historial[]` | `historial_reservas` | Pérdida de trazabilidad. |
| Calendar derivado | `reserva.eventoCalendario` | `eventos_calendario` | Confundir Calendar con fuente de verdad. |
| Notificaciones | `reserva.notificaciones[]` | `notificaciones` | Bloquear reserva por falla de envío. |
| Auditoría | `accion.realizadaPor` | `auditoria_cambios` | Cambios críticos sin responsable. |

## 4. Estados normalizados

La validación de negocio mencionó estados como agendado, reservado, confirmado, asiste, no asistió, pendiente y en espera. En código conviene trabajar con un catálogo controlado:

| Estado técnico | Uso |
| --- | --- |
| PENDIENTE | Reserva iniciada o pendiente de confirmación operativa. |
| EN_ESPERA | Turno o cliente en espera de disponibilidad o confirmación. |
| AGENDADA | Turno cargado en agenda. |
| RESERVADA | Turno reservado por cliente o administrador. |
| CONFIRMADA | Turno confirmado. |
| ASISTIO | Cliente asistió. |
| NO_ASISTIO | Cliente no asistió. |
| CANCELADA | Turno cancelado. |

`CANCELADA` se mantiene aunque no haya aparecido en la lista espontánea de estados, porque la validación confirmó cancelaciones. Antes de implementar, queda pendiente confirmar si `AGENDADA`, `RESERVADA` y `CONFIRMADA` son pasos realmente distintos o si deben simplificarse.

## 5. Prevención de solapamientos

La regla crítica del sistema es que no pueden existir dos reservas vigentes para el mismo peluquero en el mismo rango horario.

El dominio puede expresar esto como una regla de negocio:

```ts
puedeReservar({ peluqueroId, fechaInicio, duracionMinutos, estado })
```

Pero la persistencia debe protegerlo también con consultas, transacciones e índices adecuados. No alcanza con validar solo en frontend.

La verificación debe considerar:

- `peluquero_id`
- `fecha_inicio`
- `duracion_minutos`
- estados que ocupan agenda
- bloqueos excepcionales en `disponibilidades`

## 6. Problema N+1

Un riesgo típico de ORM es el problema N+1. Ocurre cuando se consulta una lista de reservas y luego el ORM ejecuta consultas adicionales por cada reserva para traer cliente, servicio, peluquero, notificaciones o evento de Calendar.

| Operación | Cantidad de consultas |
| --- | --- |
| Consulta inicial de reservas del día | 1 |
| Consulta de cliente por reserva | N |
| Consulta de servicio por reserva | N |
| Consulta de peluquero por reserva | N |
| Consulta de Calendar por reserva | N |
| Consulta de notificaciones por reserva | N |
| Total para 40 reservas | 201 consultas potenciales |

Una consulta explícita con JOIN o una proyección de lectura resuelve el caso en una operación controlada:

```sql
SELECT
  r.id,
  r.fecha_inicio,
  r.duracion_minutos,
  r.estado,
  c.nombre AS cliente,
  c.telefono,
  s.nombre AS servicio,
  u.nombre_completo AS peluquero,
  ec.estado_sync AS calendar_estado
FROM reservas AS r
JOIN clientes AS c ON c.id = r.cliente_id
JOIN servicios AS s ON s.id = r.servicio_id
JOIN usuarios AS u ON u.id = r.peluquero_id
LEFT JOIN eventos_calendario AS ec ON ec.reserva_id = r.id
WHERE r.fecha_inicio::date = CURRENT_DATE
ORDER BY r.fecha_inicio;
```

## 7. Decisión para el proyecto

> **Decisión:** usar una estrategia combinada: ORM o query builder para operaciones comunes, y SQL directo o query builder explícito para consultas críticas de agenda, disponibilidad, solapamientos, reportes y sincronizaciones derivadas.

Esta decisión se mantiene en v1.1 porque:

- El CRUD de clientes, servicios y reservas puede ser más rápido con ORM/query builder.
- La agenda diaria necesita consultas controladas y eficientes.
- La prevención de solapamientos debe apoyarse en transacciones y restricciones.
- Google Calendar y notificaciones son efectos derivados, no el núcleo de consistencia.
- Pagos y señas quedan fuera del MVP; no deben contaminar el modelo actual.

## 8. Distribución propuesta de responsabilidades

| Necesidad | Enfoque preferente | Motivo |
| --- | --- | --- |
| Crear o actualizar cliente | ORM o query builder | Operación común y repetitiva. |
| Crear reserva | Transacción con ORM/query builder explícito | Agrupa reserva, historial inicial, disponibilidad y efectos derivados. |
| Consultar agenda diaria | SQL directo o query builder explícito | Evita N+1 y aprovecha índices por peluquero y fecha. |
| Validar solapamientos | SQL transaccional | Regla crítica de integridad. |
| Cambiar estado | Transacción | Reserva e historial deben cambiar juntos. |
| Programar recordatorios | Query builder | Filtros por estado, fecha y canal. |
| Sincronizar Calendar | Adaptador externo + tabla `eventos_calendario` | Calendar es derivado y puede fallar sin invalidar reserva. |
| Auditoría administrativa | Inserción explícita en auditoría | Acciones críticas deben tener responsable. |
| Reportes | SQL directo | Mayor claridad y control del plan de consulta. |

## 9. Frontera entre dominio y persistencia

El resto de la aplicación no debería recibir filas crudas de PostgreSQL ni depender directamente del ORM. Conviene definir repositorios o servicios de aplicación que traduzcan la persistencia a contratos estables.

```ts
interface ReservaDetalle {
  id: number;
  estado: 'PENDIENTE' | 'EN_ESPERA' | 'AGENDADA' | 'RESERVADA' | 'CONFIRMADA' | 'ASISTIO' | 'NO_ASISTIO' | 'CANCELADA';
  fechaInicio: string;
  duracionMinutos: number;
  cliente: { id: number; nombre: string; emailGoogle: string; telefono: string; whatsapp: string };
  servicio: { id: number; nombre: string; tipoServicio: string; duracionMinutos: number };
  peluquero: { id: number; nombreCompleto: string };
  notificaciones: Array<{ canal: string; estadoEnvio: string }>;
  eventoCalendario?: { estadoSync: string; eventoExternoId?: string };
}
```

Así, si en el futuro se cambia de ORM, query builder o estrategia de consulta, la mayor parte del backend no debería necesitar cambios. Cambia la infraestructura, no el contrato del dominio.

## 10. Reglas de implementación derivadas

- No permitir que el ORM diseñe automáticamente el dominio sin revisar el esquema resultante.
- Revisar el SQL generado en consultas críticas de agenda y disponibilidad.
- Evitar cargas perezosas que produzcan N+1.
- Usar JOIN, eager loading o proyecciones específicas para pantallas de agenda.
- Mantener `reservas` como entidad central.
- Mantener PostgreSQL como fuente oficial de verdad.
- Tratar Google Calendar como integración derivada.
- Registrar fallas de Calendar sin invalidar la reserva.
- Mantener WhatsApp como pendiente hasta definir proveedor y costo.
- No agregar tablas de pagos o señas en esta versión.
- Escribir pruebas para solapamientos de turnos.
- Documentar consultas SQL directas y por qué existen.

## 11. Relación con documentos versionados

| Documento | Ruta versionada |
| --- | --- |
| Requisitos funcionales v1.1 | `docs/phase_01/requirements/v1.1/Requisitos_funcionales_Peluqueria_Sergio_v1.1.md` |
| Requisitos no funcionales v1.1 | `docs/phase_01/requirements/v1.1/Requisitos_no_funcionales_Peluqueria_Sergio_v1.1.md` |
| Modelo conceptual v1.1 | `docs/phase_01/data-modeling/modelado/modelo-conceptual.png` |
| Modelo lógico v1.1 | `docs/phase_01/data-modeling/modelado/modelo-logico.png` |
| Modelo físico v1.1 | `docs/phase_01/data-modeling/modelado/modelo-fisico.png` |
| ADR-004 | `docs/phase_01/adr/ADR-004-estrategia-combinada-orm-query-builder-sql.md` |
| ADR-008 | `docs/phase_01/adr/ADR-008-incorporar-google-calendar-y-postergar-whatsapp-pagos.md` |

## 12. Conclusión

El desajuste objeto-relacional no es un error del proyecto. Es una consecuencia normal de usar objetos en el código y relaciones en PostgreSQL. En Peluquería Sergio v1.1, el punto sensible es mantener la reserva como núcleo, proteger disponibilidad y solapamientos en persistencia, y tratar notificaciones y Google Calendar como efectos derivados.

La estrategia combinada ORM/query builder/SQL directo sigue siendo la más sana para el MVP: permite avanzar rápido sin perder control sobre las consultas críticas de agenda.

## 13. Fuente conceptual

Kleppmann, Martin; Riccomini, Chris. *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems*. 2.ª edición. O’Reilly Media, 2026. Capítulo 3, sección “The Object-Relational Mismatch”, especialmente la discusión sobre ORM y el problema N+1.

Nota metodológica: las definiciones generales sobre el desajuste objeto-relacional se toman como base conceptual. Los ejemplos de tablas, consultas y decisiones específicas son una aplicación al proyecto Peluquería Sergio v1.1.
