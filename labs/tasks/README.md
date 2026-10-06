# Laboratorio de implementación — After Look

Estas son únicamente las tareas que todavía faltan implementar para completar el MVP. Las tareas terminadas se conservan en `labs/tasks/completed/` como historial.

## Camino rápido

1. Leer `docs/phase_01/adr/` y respetar las convenciones ya aceptadas.
2. Implementar una task por vez.
3. Ejecutar lint y tests antes de avanzar.
4. Crear un commit revisable por task.

## Orden recomendado

| Orden | Archivo | Resultado |
|---:|---|---|
| 02 | `TASK-02-identidad-google-oauth.md` | Autenticación segura y asociación de clientes. |
| 03 | `TASK-03-servicios-y-disponibilidad.md` | Catálogo y cálculo de turnos disponibles. |
| 04 | `TASK-04-reservas-y-reglas.md` | Reservas transaccionales sin solapamientos. |
| 05 | `TASK-05-pruebas-del-mvp.md` | Pruebas unitarias, integración y concurrencia. |
| 06 | `TASK-06-google-calendar.md` | Sincronización desacoplada e idempotente. |

## Carril demo separado

- [TASK DEMO 01 Frontend de reservas](demo/TASK-DEMO-01-frontend-reservas.md) — plan responsive de Astro estático construido con Node y servido por FastAPI bajo `/demo` en una demo local/privada. **Pendiente**: depende de los contratos de TASK-03 y TASK-04; no forma parte del orden de finalización del MVP ni indica implementación completada.

## Infraestructura ya disponible

- Configuración tipada desde `.env`.
- Vocabularios del dominio centralizados mediante enums.
- Migración `20260920_01` aplicada en PostgreSQL.
- Protección contra solapamientos mediante exclusión GiST.

## Regla de avance

No avanzar si la task anterior no cumple su checklist. Un ejemplo que compila no reemplaza una prueba; una validación en frontend no reemplaza una restricción de base de datos.

## Flujo común

```bash
source .venv/bin/activate
ruff check .
python -m pytest -q
```

En Windows:

```powershell
.venv\Scripts\Activate.ps1
ruff check .
python -m pytest -q
```

## Definition of Done

- [ ] Código con docstrings en fronteras y casos de uso.
- [ ] Sin secretos ni datos personales en Git.
- [ ] Pruebas del comportamiento nuevo.
- [ ] Migración revisada cuando cambia el esquema.
- [ ] Documentación y nombres alineados con After Look.

## Historial

- `completed/TASK-00-principios-arquitectura.md` — convenciones base definidas.
- `completed/TASK-01-seed-datos-iniciales.md` — seed idempotente y validado implementado.
