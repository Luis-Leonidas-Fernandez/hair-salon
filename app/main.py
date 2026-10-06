from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config.settings import get_settings
from app.modules.identity.router import router as identity_router
from app.shared.errors.application_error import ApplicationError
from app.shared.errors.handlers import (
    application_error_handler,
    unexpected_error_handler,
)

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_exception_handler(ApplicationError, application_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)

app.include_router(identity_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api")
async def api_info() -> dict[str, str]:
    return {
        "message": f"{settings.app_name} API",
        "status": "running",
    }


# Montar frontend compilado de Astro si existe el directorio dist
frontend_dist_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist_dir.is_dir():
    app.mount(
        "/", StaticFiles(directory=str(frontend_dist_dir), html=True), name="frontend"
    )
