# ADR-017: Despliegue continuo en Render con Docker unificado, PostgreSQL administrado y resolución dinámica de roles

## Estado

Aceptado

## Contexto

El MVP de After Look requería una infraestructura de producción escalable, segura y completamente automatizada para alojar tanto el frontend compilado (Astro) como el backend API (FastAPI con SQLAlchemy asyncpg) y la base de datos relacional (PostgreSQL).

Durante el proceso de despliegue en la nube mediante **Render**, surgieron los siguientes requerimientos y desafíos arquitecturales:
1. **Contenedor unificado liviano:** Evitar tener múltiples servicios separados o instancias independientes para Astro y FastAPI. El contenedor de producción debía compilar los activos estáticos de Astro y servirlos eficientemente a través de FastAPI/Starlette en un único proceso.
2. **Normalización transparente de la URL de base de datos:** Render expone URLs con esquemas `postgres://` o `postgresql://`, mientras que SQLAlchemy con soporte asíncrono estricto requiere el dialecto `postgresql+asyncpg://`.
3. **Ciclo de vida de migraciones y seed automático en contenedor:** El contenedor debe ejecutar de forma confiable `alembic upgrade head` y el seed de inicialización de datos de negocio (`scripts.seed_initial_data`) antes de que `uvicorn` empiece a escuchar peticiones HTTP en el puerto dinámico `$PORT`.
4. **Privacidad estricta de credenciales e identidades:** Las direcciones de correo electrónico personales del personal, IDs de cliente y secretos de Google OAuth nunca deben quedar expuestos ni registrados en el historial de commits de Git ni en repositorios públicos.
5. **Resolución dinámica de roles y saneamiento de clientes provisionales:** Cuando un profesional o administrador ingresa por primera vez mediante Google OAuth, el sistema debe resolverlo como `staff` con su rol correspondiente (`PELUQUERO` o `ADMIN`). Si el usuario intentó ingresar antes de que se configure el seed y quedó transitoriamente en la tabla `clientes`, el sistema debe convertirlo de forma transparente y segura al rol de personal, eliminando el registro de cliente huérfano sin turnos asociados.

## Decisión

1. **Estrategia Docker Multi-Stage (`Dockerfile`):**
   - **Stage 1 (`frontend-builder`):** Basado en `node:22-alpine`. Instala dependencias (`npm ci`) y compila el frontend de Astro hacia `/app/frontend/dist/`.
   - **Stage 2 (`runner`):** Basado en `python:3.12-slim`. Instala dependencias de Python desde `requirements.txt`, copia el código de la aplicación, migraciones y scripts, e incorpora el directorio compilado `/app/frontend/dist/`.
   - **Comando de inicio (`CMD`):** Encadena en un script de shell atómico:
     ```sh
     alembic upgrade head && python -m scripts.seed_initial_data && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'
     ```
     Con `PYTHONPATH=/app` garantizado para la resolución limpia de módulos y flags `--proxy-headers --forwarded-allow-ips='*'` para procesar adecuadamente los encabezados HTTPS del proxy inverso de Render.

2. **Normalización Automática de `DATABASE_URL`:**
   - En `app/config/settings.py`, se implementó un validador Pydantic (`@field_validator("database_url")`) que reemplaza automáticamente prefijos `postgres://` o `postgresql://` por `postgresql+asyncpg://`, permitiendo copiar directamente la URL interna o externa provista por Render PostgreSQL sin intervención manual.

3. **Arquitectura Segura de Variables de Entorno en Producción:**
   - Toda credencial sensible se administra exclusivamente en la sección **Environment Variables** de Render:
     - `DATABASE_URL`: Enlace interno de conexión a la base de datos `after-look-db`.
     - `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET`: Credenciales OAuth emitidas por Google Cloud.
     - `GOOGLE_REDIRECT_URI`: Endpoint absoluto de callback (`https://after-look-app.onrender.com/auth/google/callback`).
     - `SEED_HAIRDRESSER_3_EMAIL` y `SEED_HAIRDRESSER_3_NAME`: Identidad real del profesional sin exponer su email en el código ni en Git.

4. **Saneamiento Idempotente y Conversión de Clientes a Personal en Seed:**
   - En `scripts/seed_initial_data.py`:
     - Se verifica si un email configurado para el staff ya existía en la tabla `clientes` (por intentos previos de login). Si existe y no cuenta con reservas asociadas, se elimina el registro de cliente y se da de alta como `User` en la tabla `usuarios` con rol `PELUQUERO`.
     - Se vinculan automáticamente todas las capacidades de servicios y horarios semanales base.
     - Los usuarios placeholder de prueba (`@afterlook.com`) que no formen parte del plan de identidades activo se desactivan (`activo = False`).

## Consecuencias

* **Positivas:**
  * **Cero Downtime y Despliegue Automatizado:** Cada `git push` a `main` desencadena la compilación de Astro, ejecución de migraciones en PostgreSQL, sincronización del catálogo y puesta en marcha de Uvicorn.
  * **Seguridad y Privacidad Garantizadas:** Cero fugas de credenciales o correos personales en repositorios de código.
  * **Experiencia de Usuario Fluida:** Los peluqueros son redirigidos directamente a su agenda (`/peluquero/turnos`) al autenticarse con su cuenta de Google, mientras que los clientes son dirigidos a completar perfil o reservar.
* **Negativas / Mitigaciones:**
  * Las instancias en planes gratuitos o de baja demanda pueden experimentar cold starts; mitigado con endpoints de `/healthz` y dimensionamiento adecuado de recursos.

## Evidencia relacionada

* `Dockerfile`
* `.dockerignore`
* `app/config/settings.py`
* `scripts/seed_initial_data.py`
* `app/modules/identity/router.py`
* `app/modules/identity/service.py`
