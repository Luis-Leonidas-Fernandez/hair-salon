"""Unit tests for identity domain service (CU-001, CU-002, ADR-002)."""

import pytest

from app.modules.identity.google_adapter import GoogleOAuthError
from app.modules.identity.google_port import IdentityProvider, VerifiedIdentity
from app.modules.identity.service import authenticate_and_resolve_actor
from app.modules.services.shared.domain_types import ClientAccountStatus
from app.modules.services.shared.models import Client, Role, User


class FakeIdentityProvider(IdentityProvider):
    """Test double for IdentityProvider protocol."""

    def __init__(self, identity: VerifiedIdentity) -> None:
        self._identity = identity

    def build_authorization_url(self, *, state: str, nonce: str, verifier: str) -> str:
        return f"https://accounts.google.com/test?state={state}"

    async def exchange_code(
        self, *, code: str, expected_nonce: str, code_verifier: str
    ) -> VerifiedIdentity:
        return self._identity


class FakeDatabaseSession:
    """In-memory AsyncSession mock for identity resolution tests."""

    def __init__(
        self,
        users: list[User] | None = None,
        clients: list[Client] | None = None,
    ) -> None:
        self.users = users or []
        self.clients = clients or []
        self.added: list[object] = []

    async def scalar(self, statement: object) -> object | None:
        # Check against users first
        sql = str(statement)
        if "usuarios" in sql:
            for u in self.users:
                return u
            return None
        if "clientes" in sql:
            for c in self.clients:
                return c
            return None
        return None

    def add(self, entity: object) -> None:
        self.added.append(entity)
        if isinstance(entity, Client):
            entity.id = 99
            self.clients.append(entity)

    async def commit(self) -> None:
        pass

    async def refresh(self, entity: object) -> None:
        pass


@pytest.mark.asyncio
async def test_authenticate_staff_active() -> None:
    """Active staff user is identified with their role and profile complete."""
    admin_role = Role(id=1, nombre="ADMIN", activo=True)
    staff_user = User(
        id=10,
        nombre_completo="Admin Hairdresser",
        email_google="admin@afterlook.com",
        google_sub=None,
        rol_id=1,
        activo=True,
    )
    staff_user.rol = admin_role

    session = FakeDatabaseSession(users=[staff_user])
    provider = FakeIdentityProvider(
        VerifiedIdentity(
            subject="google-sub-admin-123",
            email="admin@afterlook.com",
            name="Admin Hairdresser",
        )
    )

    actor = await authenticate_and_resolve_actor(
        session,  # type: ignore[arg-type]
        provider,
        code="auth-code-123",
        expected_nonce="nonce-123",
        code_verifier="verifier-123",
    )

    assert actor.actor_id == 10
    assert actor.actor_type == "staff"
    assert actor.role == "ADMIN"
    assert actor.email == "admin@afterlook.com"
    assert actor.nombre == "Admin Hairdresser"
    assert actor.profile_complete is True
    assert staff_user.google_sub == "google-sub-admin-123"


@pytest.mark.asyncio
async def test_authenticate_staff_inactive_raises_error() -> None:
    """Inactive staff user is rejected with STAFF_ACCOUNT_INACTIVE."""
    hairdresser_user = User(
        id=20,
        nombre_completo="Inactive Stylist",
        email_google="stylist@afterlook.com",
        google_sub=None,
        rol_id=2,
        activo=False,
    )

    session = FakeDatabaseSession(users=[hairdresser_user])
    provider = FakeIdentityProvider(
        VerifiedIdentity(
            subject="google-sub-stylist",
            email="stylist@afterlook.com",
            name="Inactive Stylist",
        )
    )

    with pytest.raises(GoogleOAuthError) as exc_info:
        await authenticate_and_resolve_actor(
            session,  # type: ignore[arg-type]
            provider,
            code="code-123",
            expected_nonce="nonce-123",
            code_verifier="verifier-123",
        )

    assert exc_info.value.code == "STAFF_ACCOUNT_INACTIVE"


@pytest.mark.asyncio
async def test_authenticate_new_client_registers_under_cu001() -> None:
    """New identity registers a client with incomplete profile (CU-001/CU-002)."""
    session = FakeDatabaseSession(users=[], clients=[])
    provider = FakeIdentityProvider(
        VerifiedIdentity(
            subject="google-sub-new-client",
            email="newclient@example.com",
            name="Martina Gómez",
        )
    )

    actor = await authenticate_and_resolve_actor(
        session,  # type: ignore[arg-type]
        provider,
        code="code-123",
        expected_nonce="nonce-123",
        code_verifier="verifier-123",
    )

    assert actor.actor_id == 99
    assert actor.actor_type == "cliente"
    assert actor.role == "CLIENTE"
    assert actor.email == "newclient@example.com"
    assert actor.nombre == "Martina Gómez"
    assert actor.profile_complete is False  # Missing phone/whatsapp initially

    # Verify registered client attributes
    created_client = session.added[0]
    assert isinstance(created_client, Client)
    assert created_client.nombre == "Martina Gómez"
    assert created_client.email_google == "newclient@example.com"
    assert created_client.google_sub == "google-sub-new-client"
    assert created_client.estado_cuenta == ClientAccountStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_authenticate_existing_client_complete_profile() -> None:
    """Existing client with phone number has profile_complete=True."""
    existing_client = Client(
        id=55,
        nombre="Carlos Cliente",
        email_google="carlos@example.com",
        google_sub="google-sub-carlos",
        telefono="+5491112345678",
        whatsapp=None,
        estado_cuenta=ClientAccountStatus.ACTIVE.value,
    )

    session = FakeDatabaseSession(users=[], clients=[existing_client])
    provider = FakeIdentityProvider(
        VerifiedIdentity(
            subject="google-sub-carlos",
            email="carlos@example.com",
            name="Carlos Cliente",
        )
    )

    actor = await authenticate_and_resolve_actor(
        session,  # type: ignore[arg-type]
        provider,
        code="code-123",
        expected_nonce="nonce-123",
        code_verifier="verifier-123",
    )

    assert actor.actor_id == 55
    assert actor.actor_type == "cliente"
    assert actor.profile_complete is True


@pytest.mark.asyncio
async def test_authenticate_suspended_client_raises_error() -> None:
    """Suspended client is rejected with CLIENT_ACCOUNT_SUSPENDED."""
    suspended_client = Client(
        id=77,
        nombre="Suspended User",
        email_google="suspended@example.com",
        google_sub="google-sub-suspended",
        estado_cuenta=ClientAccountStatus.SUSPENDED.value,
    )

    session = FakeDatabaseSession(users=[], clients=[suspended_client])
    provider = FakeIdentityProvider(
        VerifiedIdentity(
            subject="google-sub-suspended",
            email="suspended@example.com",
            name="Suspended User",
        )
    )

    with pytest.raises(GoogleOAuthError) as exc_info:
        await authenticate_and_resolve_actor(
            session,  # type: ignore[arg-type]
            provider,
            code="code-123",
            expected_nonce="nonce-123",
            code_verifier="verifier-123",
        )

    assert exc_info.value.code == "CLIENT_ACCOUNT_SUSPENDED"
