# TASK-02 — Identidad segura con Google OpenID Connect

## Resultado esperado

El backend usa Authorization Code Flow para verificar la identidad Google, crea o recupera un `Client` y emite su propia sesión de aplicación. Nunca acepta un email enviado por el navegador como prueba de identidad.

## Decisión de seguridad

- Scopes mínimos: `openid email profile`.
- Validar `state` para CSRF y `nonce` para replay.
- Usar PKCE cuando participe un cliente público, como una SPA.
- Intercambiar el authorization code en el backend.
- Validar issuer, audience, firma y expiración del ID token.
- Usar cookies `HttpOnly`, `Secure` y `SameSite=Lax` en producción.
- No solicitar scope de Calendar durante el login básico; se obtiene mediante consentimiento separado.

## Archivos

```text
app/modules/identity/router.py
app/modules/identity/schemas.py
app/modules/identity/service.py
app/modules/identity/google_port.py
app/modules/identity/google_adapter.py
app/config/settings.py
app/main.py
```

## Puerto de identidad — DIP e ISP

En `app/modules/identity/google_port.py`:

```python
"""Provider-independent contracts for verified external identities."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class VerifiedIdentity:
    """Identity claims accepted after cryptographic provider verification."""

    subject: str
    email: str
    name: str


class IdentityProvider(Protocol):
    """Exchange an authorization code for one verified identity."""

    async def exchange_code(
        self, *, code: str, expected_nonce: str, code_verifier: str | None
    ) -> VerifiedIdentity:
        """Validate the provider response and return trusted claims."""
        ...
```

El caso de uso depende de `IdentityProvider`, no del SDK de Google. Esa es la inversión de dependencias; el adaptador concreto queda en `google_adapter.py`.

## Caso de uso

En `app/modules/identity/service.py`:

```python
"""Use cases for mapping trusted external identities to local clients."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.google_port import IdentityProvider
from app.modules.services.shared.models import Client


async def authenticate_client(
    session: AsyncSession,
    provider: IdentityProvider,
    *,
    code: str,
    expected_nonce: str,
    code_verifier: str | None,
) -> Client:
    """Verify Google identity and return the corresponding active client."""
    identity = await provider.exchange_code(
        code=code,
        expected_nonce=expected_nonce,
        code_verifier=code_verifier,
    )
    client = await session.scalar(
        select(Client).where(Client.email_google == identity.email)
    )
    if client is None:
        client = Client(
            nombre=identity.name,
            email_google=identity.email,
            estado_cuenta="ACTIVA",
        )
        session.add(client)
        await session.flush()
    return client
```

## Configuración

Agregar a `Settings` y `.env.example` cuando se implemente:

```python
google_client_id: str
google_client_secret: str
google_redirect_uri: str = "http://127.0.0.1:8000/auth/google/callback"
```

```env
GOOGLE_CLIENT_ID=replace-me
GOOGLE_CLIENT_SECRET=replace-me
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/auth/google/callback
```

## Errores que deben rechazarse

- `state` ausente o distinto.
- `nonce` inválido.
- Redirect URI no registrada exactamente.
- Token expirado, issuer incorrecto o audience distinta.
- Email no verificado.
- Cuenta local `SUSPENDIDA` o `INACTIVA`.

## Checklist

- [ ] El router solo coordina HTTP, cookies y redirecciones.
- [ ] El servicio no importa FastAPI ni SDKs de Google.
- [ ] Un adaptador falso reemplaza Google en tests.
- [ ] No se guardan tokens si el MVP no los necesita.
- [ ] Ningún secreto se devuelve al frontend o entra en Git.
- [ ] Login y consentimiento de Calendar son flujos separados.
