"""
FastAPI application entry point.

This module initializes the database, configures the HTTP application,
registers API routers, serves static frontend files, and exposes the
main web interface.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import initialize_database
from routers.conversations import router as conversations_router
from routers.health import router as health_router
from routers.transfer import router as transfer_router


BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize application resources when the API starts."""
    initialize_database()
    yield


app = FastAPI(
    title="DevOpescu API",
    version="1.0.0",
    lifespan=lifespan,
)

# Serve the HTML, CSS, and JavaScript files used by the web interface.
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

# Register the application API routes.
app.include_router(health_router)
app.include_router(conversations_router)
app.include_router(transfer_router)


@app.get("/", include_in_schema=False)
def web_interface():
    """Return the main web interface."""
    return FileResponse(
        STATIC_DIR / "index.html"
    )