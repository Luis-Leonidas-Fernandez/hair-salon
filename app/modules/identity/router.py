"""HTTP routing controller for Google OAuth and session lifecycle.

Responsible only for HTTP protocol orchestration: query parameters, cookies,
redirects, and delegating business logic to the identity service and provider.
"""

import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.infrastructure.database.session import get_db_session
from app.modules.identity.google_adapter import GoogleOAuthError, GoogleOIDCAdapter
from app.modules.identity.google_flow import (
    GOOGLE_FLOW_COOKIE_NAME,
    create_google_flow,
    decode_flow_state,
    encode_flow_state,
)
from app.modules.identity.google_port import IdentityProvider
from app.modules.identity.observability import log_identity_event
from app.modules.identity.schemas import CompleteProfileRequest, CurrentUserResponse
from app.modules.identity.service import (
    authenticate_and_resolve_actor,
    complete_client_profile,
)
from app.modules.identity.session import (
    clear_session_cookie,
    extract_session,
    issue_session_cookie,
)
from app.modules.services.shared.models import Client, User

router = APIRouter(prefix="/auth", tags=["Identity"])


def get_identity_provider(
    settings: Settings = Depends(get_settings),
) -> IdentityProvider:
    """Dependency provider yielding the configured IdentityProvider implementation."""
    return GoogleOIDCAdapter(
        client_id=settings.google_client_id or "",
        client_secret=settings.google_client_secret or "",
        redirect_uri=settings.google_redirect_uri or "",
    )


@router.get("/google/start")
async def google_auth_start(
    source: str = Query("web"),
    settings: Settings = Depends(get_settings),
    provider: IdentityProvider = Depends(get_identity_provider),
) -> RedirectResponse:
    """Initiate Google OAuth Authorization Code flow with PKCE and state."""
    if not settings.google_oauth_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GOOGLE_NOT_CONFIGURED",
        )

    flow = create_google_flow(source=source)
    auth_url = provider.build_authorization_url(
        state=flow.state,
        nonce=flow.nonce,
        verifier=flow.verifier,
    )

    response = RedirectResponse(url=auth_url, status_code=status.HTTP_303_SEE_OTHER)
    is_production = settings.environment.lower() == "production"

    response.set_cookie(
        key=GOOGLE_FLOW_COOKIE_NAME,
        value=encode_flow_state(flow, settings.secret_key),
        max_age=300,
        httponly=True,
        samesite="lax",
        secure=is_production,
        path="/auth/google",
    )
    return response


@router.get("/google/callback")
async def google_auth_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    settings: Settings = Depends(get_settings),
    provider: IdentityProvider = Depends(get_identity_provider),
    db: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    """Consume the Google OAuth callback, authenticate identity, and issue session."""
    frontend_login_url = "/registro/"
    is_production = settings.environment.lower() == "production"

    # 1. Handle user cancellation or denial in Google consent screen
    if error:
        log_identity_event(
            "google_callback",
            attempt_id="unknown",
            success=False,
            reason="access_denied",
        )
        res = RedirectResponse(
            f"{frontend_login_url}?auth_error=GOOGLE_ACCESS_DENIED",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        res.delete_cookie(GOOGLE_FLOW_COOKIE_NAME, path="/auth/google")
        return res

    # 2. Extract and validate ephemeral flow cookie
    flow_cookie = request.cookies.get(GOOGLE_FLOW_COOKIE_NAME)
    if not flow_cookie or not code or not state:
        log_identity_event(
            "google_callback",
            attempt_id="unknown",
            success=False,
            reason="missing_flow_parameters",
        )
        res = RedirectResponse(
            f"{frontend_login_url}?auth_error=GOOGLE_SESSION_EXPIRED",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        res.delete_cookie(GOOGLE_FLOW_COOKIE_NAME, path="/auth/google")
        return res

    try:
        flow = decode_flow_state(flow_cookie, settings.secret_key)
    except Exception:
        log_identity_event(
            "google_callback",
            attempt_id="unknown",
            success=False,
            reason="invalid_flow_cookie",
        )
        res = RedirectResponse(
            f"{frontend_login_url}?auth_error=GOOGLE_SESSION_EXPIRED",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        res.delete_cookie(GOOGLE_FLOW_COOKIE_NAME, path="/auth/google")
        return res

    if not secrets.compare_digest(flow.state, state):
        log_identity_event(
            "google_callback",
            attempt_id=flow.attempt_id,
            success=False,
            reason="state_mismatch",
        )
        res = RedirectResponse(
            f"{frontend_login_url}?auth_error=GOOGLE_SESSION_EXPIRED",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        res.delete_cookie(GOOGLE_FLOW_COOKIE_NAME, path="/auth/google")
        return res

    # 3. Authenticate and resolve local identity
    try:
        actor = await authenticate_and_resolve_actor(
            db,
            provider,
            code=code,
            expected_nonce=flow.nonce,
            code_verifier=flow.verifier,
        )
    except GoogleOAuthError as err:
        log_identity_event(
            "google_callback",
            attempt_id=flow.attempt_id,
            success=False,
            reason=err.code,
        )
        res = RedirectResponse(
            f"{frontend_login_url}?auth_error={err.code}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        res.delete_cookie(GOOGLE_FLOW_COOKIE_NAME, path="/auth/google")
        return res
    except Exception:
        log_identity_event(
            "google_callback",
            attempt_id=flow.attempt_id,
            success=False,
            reason="unexpected_auth_error",
        )
        res = RedirectResponse(
            f"{frontend_login_url}?auth_error=GOOGLE_AUTH_FAILED",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        res.delete_cookie(GOOGLE_FLOW_COOKIE_NAME, path="/auth/google")
        return res

    # 4. Contextual redirection target based on actor type and role
    # (CU-002, CU-003, CU-010)
    if actor.actor_type == "staff":
        if actor.role == "PELUQUERO":
            target_url = "/peluquero/turnos/"
        else:
            target_url = "/admin"
    elif not actor.profile_complete:
        target_url = "/completar-perfil"  # CU-002
    else:
        target_url = "/reservas/"  # CU-003

    log_identity_event(
        "google_callback",
        attempt_id=flow.attempt_id,
        success=True,
        actor_type=actor.actor_type,
    )

    response = RedirectResponse(url=target_url, status_code=status.HTTP_303_SEE_OTHER)
    issue_session_cookie(
        response,
        actor_id=actor.actor_id,
        actor_type=actor.actor_type,
        role=actor.role,
        email=actor.email,
        nombre=actor.nombre,
        profile_complete=actor.profile_complete,
        secret_key=settings.secret_key,
        cookie_name=settings.session_cookie_name,
        ttl_minutes=settings.session_ttl_minutes,
        secure=is_production,
    )
    response.delete_cookie(GOOGLE_FLOW_COOKIE_NAME, path="/auth/google")
    return response


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    request: Request,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db_session),
) -> CurrentUserResponse:
    """Return the profile claims of the currently authenticated session."""
    session = extract_session(
        request,
        settings.secret_key,
        settings.session_cookie_name,
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NOT_AUTHENTICATED",
        )

    display_name = session.nombre
    if session.actor_type == "staff":
        u = await db.get(User, session.sub)
        if u and u.nombre_completo:
            display_name = u.nombre_completo
    elif session.actor_type == "cliente":
        c = await db.get(Client, session.sub)
        if c and c.nombre:
            display_name = c.nombre

    return CurrentUserResponse(
        id=session.sub,
        actor_type=session.actor_type,
        role=session.role,
        email=session.email,
        nombre=display_name,
        profile_complete=session.profile_complete,
    )


@router.post("/logout")
async def logout(
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Clear session cookie and log out."""
    response = JSONResponse(content={"status": "logged_out"})
    clear_session_cookie(response, settings.session_cookie_name)
    return response


@router.post("/complete-profile", response_model=CurrentUserResponse)
async def complete_profile(
    body: CompleteProfileRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> CurrentUserResponse:
    """Update contact data for the currently authenticated client (CU-002)."""
    session = extract_session(
        request,
        settings.secret_key,
        settings.session_cookie_name,
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NOT_AUTHENTICATED",
        )

    if session.actor_type != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FORBIDDEN_STAFF_ACTOR",
        )

    try:
        actor = await complete_client_profile(
            db,
            client_id=session.sub,
            telefono=body.telefono,
            whatsapp=body.whatsapp,
            fecha_nacimiento=body.fecha_nacimiento,
        )
    except GoogleOAuthError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.code,
        )

    is_production = settings.environment.lower() == "production"
    issue_session_cookie(
        response,
        actor_id=actor.actor_id,
        actor_type=actor.actor_type,
        role=actor.role,
        email=actor.email,
        nombre=actor.nombre,
        profile_complete=actor.profile_complete,
        secret_key=settings.secret_key,
        cookie_name=settings.session_cookie_name,
        ttl_minutes=settings.session_ttl_minutes,
        secure=is_production,
    )

    return CurrentUserResponse(
        id=actor.actor_id,
        actor_type=actor.actor_type,
        role=actor.role,
        email=actor.email,
        nombre=actor.nombre,
        profile_complete=actor.profile_complete,
    )
