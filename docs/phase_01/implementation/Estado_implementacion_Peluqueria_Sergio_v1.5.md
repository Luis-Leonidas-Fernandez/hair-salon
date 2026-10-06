# Estado de implementación — After Look v1.5

Este documento conecta el diseño aprobado con lo que ya está implementado y verificado en el proyecto. La versión v1.5 consolida la **reestructuración de la Home oficial de acceso directo**, la **inhabilitación no destructiva de la landing informativa de servicios**, el **refinamiento del flujo de autenticación con Google**, y las **mejoras ergonómicas y de diseño en la experiencia de cliente y peluquero** ([ADR-016](../adr/ADR-016-home-de-registro-y-refinamiento-de-experiencia-de-usuario.md)).

## Camino rápido

1. Activar el entorno virtual: `source .venv/bin/activate`.
2. Ejecutar linter y formateador: `ruff check .` y `ruff format .`.
3. Ejecutar suite de pruebas: `pytest -v`.
4. Verificar la revisión de Alembic: `alembic current`.
5. Compilar frontend y levantar aplicación unificada: `make run`.

## Etapas completadas

| Etapa | Resultado | Evidencia |
| :--- | :--- | :--- |
| 1 | Seed inicial idempotente y validado | `scripts/seed_initial_data.py`, `tests/test_seed_validations.py` |
| 2 | Configuración centralizada desde `.env` | `app/config/settings.py`, `tests/test_settings.py` |
| 3 | Enums para vocabularios del dominio | `app/modules/services/shared/domain_types.py`, `tests/test_domain_types.py` |
| 4 | Integridad de reservas en PostgreSQL | `migrations/versions/20260920_01_reservation_integrity.py` |
| 5 | Autenticación con Google OpenID Connect (CU-001) | `app/modules/identity/`, `migrations/versions/20261005_02_google_oauth_sub.py` |
| 6 | Servidor unificado Frontend + Backend | `frontend/dist/` servido en `app/main.py`, target `make run` |
| 7 | Onboarding y completitud de perfil (CU-002) | `frontend/src/pages/completar-perfil.astro`, `POST /auth/complete-profile` |
| 8 | Extensión de capacidad a 3 Peluqueros | `seed_plan.py`, `settings.py`, `.env`, peluquero 3 enlazado en BD |
| 9 | Módulo de Reservas y Disponibilidad (CU-003) | `app/modules/booking/`, `frontend/src/pages/reservas.astro`, `reservas.css` |
| 10 | Optimización de red y observabilidad en tiempo real | Pool de conexiones en `google_adapter.py`, middleware de latencia en `main.py` |
| 11 | Agenda e historial de turnos para el peluquero (CU-010, CU-011) | `frontend/src/pages/peluquero/turnos.astro`, `GET /api/booking/hairdresser/my`, `PATCH /status` |
| 12 | Home de registro directo, archivo de landing y refinamiento de UX | `frontend/src/pages/index.astro`, `_servicios-landing-disabled.astro`, [ADR-016](../adr/ADR-016-home-de-registro-y-refinamiento-de-experiencia-de-usuario.md) |

---

## Módulos y Flujos de Usuario Actualizados

### 1. Puerta de Entrada y Autenticación Directa (CU-001) — *Home*
* **Home Oficial (`/`):** Implementada en `frontend/src/pages/index.astro`. Actúa directamente como la pantalla de acceso y bienvenida exclusiva con Google OAuth, suprimiendo la fricción de una landing estática previa.
* **Preservación No Destructiva:** El catálogo visual previo y estructura de servicios fue resguardado en `frontend/src/pages/_servicios-landing-disabled.astro`. Al comenzar con guion bajo (`_`), Astro la excluye de la compilación y enrutamiento público, manteniendo el código disponible para reactivación.
* **Estilizado de CTA y Copy Comercial:**
  - Reducción uniforme de 5px en altura para `.google-register-button` (`min-height: 53px` en mobile, proporción clamp en desktop).
  - Acabado satinado premium con borde dorado (`rgba(248, 197, 107, 0.4)`), elevación hover y microinteracciones.
  - Reemplazo de leyendas de prueba por copy persuasivo listo para producción.
  - Eliminación del botón "Volver al inicio" para un flujo de foco único.

### 2. Flujo de Reserva y Perfil del Cliente (CU-002, CU-003)
* **Topbar Limpio en `/reservas`:**
  - Eliminación del botón "← Inicio".
  - Incorporación de avatar reactivo (`.client-avatar-badge`) con iniciales dinámicas (`getInitials`) y degradado dorado.
  - Color del nombre del cliente estandarizado a gris pizarra elegante (`#cbd5e1`) con protección contra desbordamiento (`ellipsis`), eliminando el tono turquesa anterior.

### 3. Agenda del Peluquero (CU-010, CU-011)
* **Alineación y Espaciado (`/peluquero/turnos`):**
  - Ajuste de padding lateral en `+5px` en `.turnos-shell` para todas las resoluciones móviles y de escritorio, eliminando la compresión contra los bordes de la pantalla.
  - Sincronización del nombre real del profesional desde la sesión activa de Google y eliminación de etiquetas redundantes.

---

## Verificación y Tests Automatizados

La suite completa consta de **55 tests pasando en verde** (`pytest`):

```text
tests/test_booking.py ......                                             [ 10%]
tests/test_database_integrity.py ..                                      [ 14%]
tests/test_domain_types.py ..                                            [ 18%]
tests/test_hairdresser_turnos.py .....                                    [ 27%]
tests/test_health.py .                                                   [ 29%]
tests/test_identity_flow.py ....                                         [ 36%]
tests/test_identity_router.py .............                              [ 60%]
tests/test_identity_service.py ........                                  [ 74%]
tests/test_identity_session.py ...                                       [ 80%]
tests/test_models.py .                                                   [ 81%]
tests/test_seed_validations.py .........                                 [ 98%]
tests/test_settings.py .                                                 [100%]
============================== 55 passed in 0.40s ==============================
```

Compilación estática de Astro (`npm run build`): **5 páginas generadas sin errores**.

---

## ADRs relacionados

- [ADR-001 — Usar PostgreSQL como base principal](../adr/ADR-001-usar-postgresql-como-base-principal.md)
- [ADR-002 — Separar clientes y usuarios internos](../adr/ADR-002-separar-clientes-y-usuarios-internos.md)
- [ADR-003 — Modelar reserva como entidad central](../adr/ADR-003-modelar-reserva-como-entidad-central.md)
- [ADR-005 — Usar estados explícitos de reserva](../adr/ADR-005-usar-estados-explicitos-de-reserva.md)
- [ADR-009 — Seed idempotente y validado](../adr/ADR-009-seed-idempotente-y-validado.md)
- [ADR-010 — Configuración tipada desde el entorno](../adr/ADR-010-configuracion-tipada-desde-entorno.md)
- [ADR-011 — Vocabularios del dominio mediante enums](../adr/ADR-011-centralizar-vocabularios-del-dominio.md)
- [ADR-012 — Protección de solapamientos en PostgreSQL](../adr/ADR-012-proteger-solapamientos-en-postgresql.md)
- [ADR-013 — Estado de implementación versionado](../adr/ADR-013-versionar-el-estado-de-implementacion.md)
- [ADR-014 — Autenticación Google OpenID Connect y servidor unificado](../adr/ADR-014-autenticacion-google-openid-connect-y-servidor-unificado.md)
- [ADR-015 — Módulo de reservas, cálculo de disponibilidad y optimización del callback](../adr/ADR-015-modulo-de-reservas-y-optimizacion-de-disponibilidad.md)
- [ADR-016 — Home de registro, inhabilitación no destructiva de servicios y refinamiento de UX](../adr/ADR-016-home-de-registro-y-refinamiento-de-experiencia-de-usuario.md)

---

## Próxima etapa

Implementar la vista del cliente para consultar y autogestionar la cancelación de sus turnos vigentes ([CU-005](../use-cases/Casos_de_uso_Peluqueria_Sergio.md) — *Cancelar turno*) y la vista general de agenda administrativa para el dueño/administrador ([CU-014](../use-cases/Casos_de_uso_Peluqueria_Sergio.md) — *Consultar agenda administrativa*).
