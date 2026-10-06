"""Domain service for identity authentication and resolution.

Follows DIP by depending on the IdentityProvider protocol rather than
concrete Google SDKs. Orchestrates CU-001 (Google Login / auto-registration)
and CU-002 (contact completeness evaluation) while respecting ADR-002.
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.identity.google_adapter import GoogleOAuthError
from app.modules.identity.google_port import IdentityProvider
from app.modules.services.shared.domain_types import ClientAccountStatus
from app.modules.services.shared.models import Client, User


@dataclass(frozen=True, slots=True)
class AuthenticatedActor:
    """Canonical authenticated identity within After Look."""

    actor_id: int
    actor_type: str  # "staff" | "cliente"
    role: str  # "ADMIN" | "PELUQUERO" | "CLIENTE"
    email: str
    nombre: str
    profile_complete: bool


async def authenticate_and_resolve_actor(
    session: AsyncSession,
    provider: IdentityProvider,
    *,
    code: str,
    expected_nonce: str,
    code_verifier: str,
) -> AuthenticatedActor:
    """Exchange OIDC code and resolve or create local identity.

    1. Uses the provider port to obtain cryptographic claims (sub, email, name).
    2. Checks if the identity belongs to an internal staff member (usuarios).
    3. If not, checks or creates a client (clientes) under CU-001.
    4. Evaluates if contact information (phone/WhatsApp) is completed (CU-002).
    """
    identity = await provider.exchange_code(
        code=code,
        expected_nonce=expected_nonce,
        code_verifier=code_verifier,
    )

    # 1. Check if identity matches an internal staff user (User: Admin or Peluquero)
    user_stmt = (
        select(User)
        .options(selectinload(User.rol))
        .where(
            (User.google_sub == identity.subject)
            | (User.email_google == identity.email)
        )
    )
    user = await session.scalar(user_stmt)
    if user is not None:
        if not user.activo:
            raise GoogleOAuthError("STAFF_ACCOUNT_INACTIVE")

        changed = False
        # Link google_sub if this is the first login
        if user.google_sub is None:
            user.google_sub = identity.subject
            changed = True

        # Keep staff display name in sync with Google profile name when provided
        if identity.name and identity.name.strip():
            google_name = identity.name.strip()
            if user.nombre_completo != google_name:
                user.nombre_completo = google_name
                changed = True

        if changed:
            await session.commit()

        role_name = user.rol.nombre if user.rol else "PELUQUERO"
        return AuthenticatedActor(
            actor_id=user.id,
            actor_type="staff",
            role=role_name,
            email=user.email_google,
            nombre=user.nombre_completo,
            profile_complete=True,
        )

    # 2. Identity belongs to an external client (Client)
    client_stmt = select(Client).where(
        (Client.google_sub == identity.subject)
        | (Client.email_google == identity.email)
    )
    client = await session.scalar(client_stmt)

    if client is not None:
        if client.estado_cuenta != ClientAccountStatus.ACTIVE.value:
            raise GoogleOAuthError("CLIENT_ACCOUNT_SUSPENDED")

        # Link immutable google_sub if not yet associated
        if client.google_sub is None:
            client.google_sub = identity.subject
            await session.commit()
    else:
        # CU-001: Register new client
        display_name = identity.name.strip() if identity.name else "Cliente After Look"
        client = Client(
            nombre=display_name,
            email_google=identity.email,
            google_sub=identity.subject,
            estado_cuenta=ClientAccountStatus.ACTIVE.value,
        )
        session.add(client)
        await session.commit()
        await session.refresh(client)

    # CU-002: Evaluate profile completeness
    has_contact = bool(client.telefono or client.whatsapp)

    return AuthenticatedActor(
        actor_id=client.id,
        actor_type="cliente",
        role="CLIENTE",
        email=client.email_google,
        nombre=client.nombre,
        profile_complete=has_contact,
    )


async def complete_client_profile(
    session: AsyncSession,
    client_id: int,
    telefono: str,
    whatsapp: str | None = None,
    fecha_nacimiento: date | None = None,
) -> AuthenticatedActor:
    """Update contact information for an authenticated client under CU-002."""
    stmt = select(Client).where(Client.id == client_id)
    client = await session.scalar(stmt)

    if client is None:
        raise GoogleOAuthError("CLIENT_NOT_FOUND")

    if client.estado_cuenta != ClientAccountStatus.ACTIVE.value:
        raise GoogleOAuthError("CLIENT_ACCOUNT_SUSPENDED")

    client.telefono = telefono
    client.whatsapp = whatsapp
    client.fecha_nacimiento = fecha_nacimiento

    await session.commit()
    await session.refresh(client)

    return AuthenticatedActor(
        actor_id=client.id,
        actor_type="cliente",
        role="CLIENTE",
        email=client.email_google,
        nombre=client.nombre,
        profile_complete=True,
    )
