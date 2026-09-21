from fastapi import FastAPI

from app.config.settings import get_settings
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


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": f"{settings.app_name} API",
        "status": "running",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
