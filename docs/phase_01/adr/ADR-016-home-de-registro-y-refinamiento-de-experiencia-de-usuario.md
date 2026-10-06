# ADR-016: Home de registro, inhabilitación no destructiva de servicios y refinamiento de experiencia de usuario

## Estado

Aceptado

## Contexto

El sistema contaba con una página inicial (`index.astro`) de carácter informativo donde se exhibía el catálogo estático de servicios, beneficios y un botón de reserva que derivaba a la página de registro (`/registro/`). En las pruebas de producto y validación de negocio se identificó:
1. **Fricción innecesaria en el embudo:** Los clientes recurrentes y nuevos deben ingresar directamente al acceso con Google para verificar su identidad y proceder inmediatamente a la reserva de turnos, sin pasos intermedios informativos redundantes.
2. **Preservación del trabajo previo:** La página original de servicios no debía eliminarse, sino quedar inhabilitada temporalmente de forma limpia para una posible reactivación o evolución futura.
3. **Copy comercial para producción:** La pantalla de autenticación presentaba leyendas de "vista previa visual" que debían reemplazarse por textos persuasivos, orientados a la exclusividad y listos para producción.
4. **Ergonomía visual y alineación responsiva:**
   - El botón CTA de Google requería mayor estilizado y una reducción de 5px en altura para equilibrar las proporciones en todos los dispositivos.
   - En la página de reserva del cliente (`/reservas`), el botón "← Inicio" generaba ruido de navegación una vez autenticado, siendo más adecuado mostrar un avatar reactivo con las iniciales del usuario y su nombre en una tonalidad gris armoniosa con el diseño oscuro y dorado.
   - En la agenda del peluquero (`/peluquero/turnos`), el contenido quedaba excesivamente pegado a los laterales de la pantalla en dispositivos móviles y tablets.

## Decisión

1. **Inhabilitación No Destructiva de la Landing de Servicios:**
   - Se renombró el archivo original a `frontend/src/pages/_servicios-landing-disabled.astro`.
   - Se adopta la convención nativa del router de Astro: los archivos prefijados con guion bajo (`_`) quedan automáticamente excluidos de la generación de rutas estáticas, preservando el 100% del marcado, estilos y lógica sin exponerlos al usuario final.

2. **La Página de Registro como Nueva Home (`/`):**
   - El archivo `frontend/src/pages/index.astro` adopta el flujo de registro con Google, convirtiendo la raíz del sitio en la puerta de entrada principal.
   - Se mantiene activa en paralelo la ruta `/registro/` para garantizar retrocompatibilidad total con los callbacks de Google OAuth y redirecciones de sesión.

3. **Refinamiento de Copy y Estilo en el Acceso:**
   - Se reemplazaron las advertencias de "vista previa" por copy publicitario de salón exclusivo.
   - Se removió el enlace "Volver al inicio" (`.registro-back`).
   - El botón `.google-register-button` se estilizó con acabado satinado marfil/oro (`linear-gradient(180deg, #fffcf4 0%, #f7e8c8 100%)`), borde dorado fino (`rgba(248, 197, 107, 0.4)`), elevación con microinteracción en hover y reducción uniforme de 5px de altura (`min-height: 53px` en móvil, `min-height: clamp(51px, calc(7.1dvh - 5px), 59px)` en desktop).

4. **Identidad del Cliente en la Barra de Reservas (`/reservas`):**
   - Se eliminó el botón "← Inicio".
   - Se introdujo el componente `.client-avatar-badge`, que computa dinámicamente las iniciales del cliente autenticado (`getInitials`) con un fondo en degradado radial dorado.
   - El nombre completo (`.client-name-display`) migró del tono turquesa (`#38bdf8`) a un gris pizarra elegante (`#cbd5e1`), con `text-overflow: ellipsis` y protección contra desbordes.

5. **Alineación y Padding en la Agenda del Peluquero (`/peluquero/turnos`):**
   - Se incrementó en `+5px` el padding lateral de `.turnos-shell` en todas las resoluciones (mínimo base de 21px a 41px, móvil ≤ 640px con `max(21px, env(...) + 5px)` y móvil ≤ 380px con `max(17px, env(...) + 5px)`), asegurando que el contenido conserve su centrado con una separación lateral confortable.

## Consecuencias

* **Positivas:**
  * Embudo de conversión directo: menor abandono de usuarios al acceder de inmediato al flujo de turnos.
  * Preservación del patrimonio de código: el catálogo de servicios sigue disponible en el repositorio para cuando se requiera reactivar como sección independiente.
  * Consistencia estética premium: coherencia completa en paleta cromática (dorado, pizarra y negro carbón) en todas las pantallas.
* **Negativas / Mitigaciones:**
  * Al no haber una landing de bienvenida tradicional, los nuevos usuarios ven directamente la pantalla de ingreso con Google; se mitiga con un lede claro de valor de marca ("Conectate en segundos para reservar tu próximo turno...").

## Evidencia relacionada

* `frontend/src/pages/index.astro`
* `frontend/src/pages/_servicios-landing-disabled.astro`
* `frontend/src/pages/registro.astro`
* `frontend/src/styles/registro.css`
* `frontend/src/pages/reservas.astro`
* `frontend/src/styles/reservas.css`
* `frontend/src/styles/peluquero-turnos.css`
