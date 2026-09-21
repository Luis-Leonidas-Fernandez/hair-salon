# ADR-010: Centralizar la configuración tipada desde el entorno

## Estado

Aceptado

## Contexto

La aplicación necesita configuración para la base de datos, comportamiento del motor, versión de la API y datos del seed. Leer `.env` directamente desde varios módulos genera acoplamiento, dificulta las pruebas y favorece valores hardcodeados.

## Decisión

Usar `pydantic-settings` en `app/config/settings.py` como único punto de entrada de configuración.

Los módulos consumidores deben recibir `get_settings()` y no leer variables de entorno por su cuenta. Los secretos permanecen en `.env`; `.env.example` solo documenta la forma esperada.

## Consecuencias

- La configuración se valida al iniciar la aplicación.
- Los campos obligatorios faltantes provocan un error temprano.
- Los tests pueden construir `Settings` con valores controlados.
- `@lru_cache` garantiza una única configuración por proceso.
- Los cambios en `.env` requieren reiniciar la aplicación.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla |
| --- | --- |
| Leer `os.getenv` en cada módulo | Repite lógica y evita validación centralizada. |
| Hardcodear credenciales o identidades | Expone secretos y obliga a modificar código por entorno. |
| Archivo de configuración propio sin validación | Permite errores de tipo y fallos tardíos. |

## Evidencia relacionada

- `app/config/settings.py`
- `.env.example`
- `app/main.py`
- `app/infrastructure/database/session.py`
