# TASK DEMO 01 Frontend de reservas

## Resultado esperado

Planificar un frontend responsive de reservas para escritorio y móvil, generado como **salida estática de Astro con Node** y servido después por el **FastAPI existente bajo `/demo`**, en el mismo origen que la API. Permitirá consultar servicios, elegir profesional y horario, y solicitar una reserva. Esta es una **task de documentación para una demo local o privada**, no una implementación terminada ni una autorización para publicar reservas sin autenticación.

La demo no incluye pagos, inicio de sesión, Google Calendar ni datos personales reales. No se diseña aquí una interfaz visual: composición, colores y detalles de pantalla quedan pendientes de diseños posteriores de Open Design; esta task no lo invoca.

## Camino rápido

1. Cerrar los contratos pendientes de catálogo, profesionales, disponibilidad y reserva con las TASK-03 y TASK-04.
2. Acordar un mecanismo de identidad de prueba **solo local** para la reserva; el navegador nunca envía un `cliente_id` arbitrario. No exponer el flujo al público sin autenticación.
3. Generar el sitio estático, montarlo en FastAPI bajo `/demo`, probar con API simulada y después recorrer el flujo contra el backend real desde un solo servidor.

## Estado real y dependencias

Hoy `app/main.py` registra únicamente `GET /` y `GET /health`. No hay montaje `/demo` ni routers de servicios, disponibilidad o reservas conectados. La migración `20260920_01` ya define `reservas.fecha_fin` y la exclusión `ex_reservas_peluquero_horario_activo`; la creación de reservas y su traducción a HTTP siguen pendientes.

- **TASK-03:** entregar servicios activos y slots calculados, con duración y zona horaria correctas. La selección de profesionales elegibles necesita un contrato público acordado.
- **TASK-04:** crear la reserva y responder conflictos; su contrato de cliente presupone autenticación. Para esta demo sin login hay que acordar antes una identidad ficticia resuelta **en el servidor y restringida al entorno local/privado**, o mantener la reserva como simulación hasta tenerla. Nunca reutilizar esa excepción en producción.
- **TASK-05:** cubrir API, persistencia y concurrencia; el frontend no sustituye la garantía de PostgreSQL.

Los precios requieren aprobación comercial. Ni el frontend ni los datos simulados deben inventar o fijar importes como si fueran vigentes.

## Elección técnica y estructura propuesta

La elección es **Astro con `output: 'static'`**. Node se utiliza para crear el proyecto, instalar dependencias y ejecutar el build; el resultado terminado (`dist/` por defecto) es HTML, CSS y JavaScript estáticos. **FastAPI es el único servidor de la demo terminada y del recorrido local equivalente a producción**: monta esos archivos bajo `/demo` y conserva la API en el mismo origen. No se seleccionan SSR de Astro, un servidor Node de runtime ni plantillas Jinja para renderizar estas páginas.

Configurar `base: '/demo'` para que Astro genere páginas y assets bajo ese subpath; usar `import.meta.env.BASE_URL` cuando se construyan enlaces internos o referencias a recursos, sin confundirlo con la ruta de la API. La disponibilidad cambia después del build: el frontmatter de Astro se ejecuta al construir la salida estática, **no** en cada solicitud de reserva. Por eso las consultas de horarios y la confirmación se ejecutan en módulos JavaScript del navegador, sobre HTML semántico de componentes `.astro`. No hace falta introducir un framework de componentes cliente.

Configuración propuesta, pendiente de implementar:

```js
import { defineConfig } from "astro/config";

export default defineConfig({ output: "static", base: "/demo" });
```

Comandos de scaffold propuestos para cuando se apruebe la implementación, desde la raíz del repositorio:

```bash
npm create astro@latest
# Choose frontend/ as the project directory in the wizard.
cd frontend
npm run build
```

Instalar dependencias si el asistente no lo hizo y comprobar la versión de Node exigida por la guía vigente de Astro. Esta task **no ejecuta** el scaffold ni modifica el backend. `npm run dev` puede usarse aparte para HMR durante la edición; no sirve la demo terminada. `astro preview` tampoco es el servidor de producción.

```text
frontend/
  astro.config.mjs                    # Static output and /demo base
  src/
    pages/index.astro                 # Semantic page generated at build time
    components/BookingForm.astro      # Accessible booking controls
    components/SlotList.astro         # Slot list and empty state
    styles/demo.css                   # Responsive layout rules
    domain/booking.js                 # Service, Professional, Slot, BookingRequest
    client/bookingAction.js           # Per-action pending and duplicate guard
    client/submitBooking.js           # Client use case and feedback flow
    api/reservationsApi.js            # Same-origin fetch and HTTP error mapping
    tests/bookingFlow.test.js         # Browser interaction with a mock API
```

El árbol es una guía inicial, no una exigencia de cantidad de archivos. Los componentes `.astro` presentan estructura; CSS resuelve adaptación; módulos cliente coordinan eventos; el adaptador HTTP conoce rutas y respuestas; el módulo de dominio describe los datos del flujo. Separar solo cuando cambien por motivos distintos o se dificulte la prueba.

## Mapa REST propuesto todavía no implementado

El frontend consume contratos acordados, no asume que los endpoints existen. Antes de integrar, fijar rutas definitivas, parámetros, estados HTTP y ejemplos en OpenAPI. La tabla distingue el hecho actual de cada propuesta.

| Interacción | Contrato propuesto para acordar | Estado y tratamiento |
|---|---|---|
| Comprobar conexión | `GET /health` → `{"status":"ok"}` | **Disponible hoy**; solo prueba conectividad. |
| Mostrar servicios | `GET /services` → lista con `id`, `nombre`, `descripcion`, `tipo_servicio`, `duracion_minutos`; sin precio | **Pendiente TASK-03**; ruta sugerida allí. |
| Elegir profesional | `GET /professionals?service_id=…` → profesionales habilitados para ese servicio | **Propuesta pendiente**; no hay router ni esquema acordado. |
| Ver horarios | `GET /availability?service_id=…&professional_id=…&date=…` → slots con `peluquero_id`, `fecha_inicio`, `fecha_fin` | **Propuesta pendiente TASK-03**; nombres de ruta y parámetros por confirmar. Mostrar horas con zona `America/Argentina/Buenos_Aires`. |
| Solicitar reserva | `POST /bookings` con `servicio_id`, `peluquero_id`, `fecha_inicio`; respuesta con identificador y estado | **Propuesta pendiente TASK-04** y decisión de identidad de demo. No enviar `cliente_id` desde el navegador. |
| Resolver conflicto | HTTP `409`, cuerpo `error.code`, `error.message`, `error.details` | La forma de error existe en el manejador actual; el caso de reserva aún debe mapear la restricción a `ConflictError`. Refrescar slots y explicar que el horario dejó de estar disponible. |

`fecha_inicio` y `fecha_fin` deben ser instantes con zona horaria; la representación exacta se acuerda en el contrato. La disponibilidad orienta al usuario, pero no garantiza la reserva: la validación transaccional y la exclusión de PostgreSQL son la última defensa frente a dos clientes concurrentes.

## Publicación y seguridad de la demo

- El build de Astro debe quedar disponible para FastAPI en una ruta de archivos conocida y montarse con `StaticFiles` bajo `/demo`. Verificar `/demo/`, recarga directa, HTML, CSS, JavaScript y rutas de API sin que el montaje estático las intercepte. Es una integración **pendiente**, no un endpoint actual.
- En el flujo terminado, llamar a la API con rutas del mismo origen que comiencen en la raíz, por ejemplo `fetch('/health')` y, cuando exista, `fetch('/bookings')`. `/demo` es la base de páginas y assets, **no** un prefijo de API. No se necesita `PUBLIC_API_BASE_URL` ni CORS para este recorrido de un solo origen.
- Las variables `PUBLIC_*` de Astro son visibles en el código cliente: nunca incluir claves, tokens o credenciales. Node es necesario para instalar y construir; **no** para servir el build ya generado con FastAPI.
- Si se usa el servidor de desarrollo de Astro para HMR, ese modo opcional puede tener otro origen: acordar un proxy de desarrollo o CORS restringido solo para desarrollo. No trasladar esa configuración al recorrido normal de la demo ni usar CORS como sustituto de autenticación.
- Usar datos ficticios y un entorno local/privado. No cargar cuentas, correos, teléfonos ni PII reales en fixtures, capturas, logs o Git. Mostrar duración y disponibilidad desde el backend; no fijar precios mientras siga pendiente la aprobación comercial.

## Acciones asíncronas sin duplicados

Cada acción independiente (cargar slots, confirmar reserva) conserva su propio estado de espera y error. Durante la solicitud, deshabilitar **solo** su control dependiente, mostrar carga visible y volver a habilitarlo tras éxito o fallo. El bloqueo debe establecerse sincrónicamente al recibir el evento, antes de que llegue un segundo clic. Los componentes `.astro` aportan el botón y regiones con `role="status"` y `role="alert"`; el módulo cliente actualiza esos nodos.

Marcado semántico mínimo del botón y sus mensajes, sin definir diseño visual:

```html
<button id="booking-submit" type="button">Confirmar reserva</button>
<p id="booking-status" role="status"></p>
<p id="booking-error" role="alert"></p>
```

Ejemplo breve de una acción de reserva en JavaScript del navegador. `request` representa al adaptador HTTP que llama a la ruta relativa a la raíz acordada. `fetch` **no rechaza** la promesa por un HTTP `409`: hay que examinar `response.ok` y `response.status`. El adaptador definitivo puede extraer esa traducción sin cambiar el guard de UI.

```js
/** Binds one booking action and prevents duplicate client requests. */
export function bindBookingAction({ button, status, error, request }) {
  let pending = false;
  button.addEventListener("click", async () => {
    if (pending) return;
    pending = true;
    button.disabled = true;
    status.textContent = "Procesando reserva…";
    error.textContent = "";
    try {
      const response = await request();
      if (!response.ok) {
        status.textContent = "";
        error.textContent = response.status === 409
          ? "El horario ya no está disponible. Seleccione otro."
          : "No se pudo completar la reserva. Vuelva a intentarlo.";
        return;
      }
      status.textContent = "Reserva registrada.";
    } catch {
      status.textContent = "";
      error.textContent = "No se pudo conectar. Vuelva a intentarlo.";
    } finally {
      pending = false;
      button.disabled = false;
    }
  });
}
```

Cada instancia de `bindBookingAction` protege solo su acción; otra pestaña o cliente todavía puede competir por el mismo horario. Después de un `409`, refrescar slots y ofrecer otra elección. La prevalidación y la exclusión de PostgreSQL en el backend siguen siendo la garantía final contra solapamientos.

## Criterios de aceptación de experiencia

- El flujo permite seleccionar servicio, profesional elegible, fecha y slot disponible, y confirmar una sola solicitud; estados vacío, carga, error y éxito son comprensibles sin depender solo del color.
- Navegación completa por teclado, foco visible, controles con nombre accesible, orden lógico y mensajes anunciados con `role="status"` o `role="alert"` cuando corresponda.
- En móvil y escritorio no hay desplazamiento horizontal ni controles cortados; el formulario y los horarios siguen siendo utilizables con zoom y tamaños de pantalla estrechos.
- Al cargar o reservar, el control correspondiente queda deshabilitado mientras `pending` es verdadero y se recupera tanto tras éxito como tras error; doble clic inmediato no genera dos llamadas de reserva.
- Un conflicto `409` no muestra éxito: explica la pérdida del slot, actualiza disponibilidad y deja elegir otro. Ningún texto promete que un horario está confirmado antes de la respuesta del backend.
- No se muestran precios sin aprobación, datos reales ni funciones excluidas.

## Pruebas y ejecución de la demo

**Con API simulada:** probar carga, vacío, fallo de red, respuesta HTTP `409` que resuelve `fetch`, doble clic sin segunda llamada, restauración del botón en `finally`, navegación por teclado y disposición móvil/escritorio. El doble usa solo datos ficticios y no se presenta como backend funcional.

**Con backend real, después de TASK-03 y TASK-04:**

1. Preparar PostgreSQL local de prueba y migraciones; confirmar la restricción de solapamiento. Acordar y habilitar únicamente para esta demo el actor ficticio resuelto del lado servidor; si no existe, detener la prueba de creación real.
2. Cerrar las rutas y los esquemas en OpenAPI. Con Node, instalar dependencias si corresponde y ejecutar `npm run build` en `frontend/`; comprobar que `dist/` contiene HTML, CSS y JavaScript con la base `/demo`.
3. Montar el build terminado en el FastAPI existente bajo `/demo` y levantar **solo FastAPI**. Verificar `/health`, `/demo/`, assets y recarga directa desde el mismo origen. No levantar Astro dev ni preview como servidor de la demo.
4. Desde `/demo/`, consultar servicios y slots reales mediante rutas de API que comiencen en `/`; confirmar una reserva ficticia y verificar respuesta y persistencia. Intentar el mismo profesional y horario desde otra solicitud: la segunda debe recibir `409`, y la UI debe recuperar el control y ofrecer otro slot.
5. Detener la demo sin publicar el entorno ni conservar PII. Registrar qué contratos quedaron pendientes o difirieron de los propuestos. El mismo patrón de build estático más un servidor FastAPI se conserva para el despliegue autorizado.

**Desarrollo opcional con HMR:** `npm run dev` en `frontend/` puede acelerar cambios de código antes del build. Ese servidor separado no representa la ruta de ejecución de la demo; si usa otro origen para llamar a FastAPI, configurar solo para desarrollo un proxy o CORS acotado y volver a verificar después el build servido por FastAPI.

## Checklist de entrega futura

- [ ] TASK-03 entrega servicios, profesionales elegibles y disponibilidad con contratos acordados.
- [ ] TASK-04 entrega reserva transaccional, `409` de solapamiento e identidad ficticia local controlada, o se declara explícitamente que la confirmación sigue simulada.
- [ ] Astro genera salida `static` con `base: '/demo'`; el build se sirve por FastAPI bajo `/demo` y la API conserva sus rutas en la raíz del mismo origen.
- [ ] Node se utiliza para crear e instalar el proyecto y construirlo, pero no se ejecuta un servidor Node, Astro dev ni Astro preview para la demo terminada. No se requiere CORS ni `PUBLIC_API_BASE_URL` en el recorrido normal.
- [ ] Componentes `.astro`, CSS, módulos cliente, caso de uso, adaptador HTTP y dominio conservan responsabilidades claras sin capas innecesarias.
- [ ] Cada acción muestra carga/error, se rehabilita en éxito y fallo, y bloquea invocaciones repetidas; el backend mantiene la garantía final.
- [ ] Pruebas con API simulada y recorrido real documentado, incluyendo assets bajo `/demo`, `409`, móvil, escritorio y accesibilidad.
- [ ] No hay pagos, login, Calendar, precios no aprobados, PII real ni despliegue público sin autenticación.

## Referencias oficiales

- [Astro Configuration Reference](https://docs.astro.build/en/reference/configuration-reference/): `output: 'static'`, `base` e `import.meta.env.BASE_URL`.
- [Astro Install](https://docs.astro.build/en/install-and-setup/): creación del proyecto con Node.
- [Astro CLI Commands](https://docs.astro.build/en/reference/cli-reference/): `astro build`, directorio `dist/` y alcance de `astro preview`.
- [Astro Client-Side Scripts](https://docs.astro.build/en/guides/client-side-scripts/): interacciones del navegador sin servidor Astro de runtime.
- [Astro Tutorial Send a Script to the Browser](https://docs.astro.build/en/tutorial/3-components/4/): frontmatter en build y scripts de interacción en el navegador.
- [Astro Environment Variables](https://docs.astro.build/en/guides/environment-variables/): `PUBLIC_*` queda disponible en el cliente.
- [FastAPI Static Files](https://fastapi.tiangolo.com/tutorial/static-files/): montaje de archivos estáticos; [FastAPI Templates](https://fastapi.tiangolo.com/advanced/templates/) describe una alternativa no elegida.
- [MDN Using Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch): verificar `response.ok` y `response.status` ante errores HTTP.
