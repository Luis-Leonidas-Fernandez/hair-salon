import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.config.settings import get_settings
from app.modules.booking.router import router as booking_router
from app.modules.calendar.router import router as calendar_router
from app.modules.identity.router import router as identity_router
from app.shared.errors.application_error import ApplicationError
from app.shared.errors.handlers import (
    application_error_handler,
    unexpected_error_handler,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
http_logger = logging.getLogger("afterlook.http")

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Log incoming HTTP requests and responses with latency for observability."""
    start_time = time.perf_counter()
    path = request.url.path
    if request.url.query:
        path = f"{path}?{request.url.query}"
    http_logger.info("--> %s %s", request.method, path)
    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        http_logger.info(
            "<-- %s %s [%s] (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000
        http_logger.exception(
            "<-- %s %s [EXCEPTION: %s] (%.1fms)",
            request.method,
            request.url.path,
            exc,
            duration_ms,
        )
        raise


app.add_exception_handler(ApplicationError, application_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)

app.include_router(identity_router)
app.include_router(booking_router)
app.include_router(calendar_router)


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
