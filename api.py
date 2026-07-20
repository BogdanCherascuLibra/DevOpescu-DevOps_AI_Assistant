from contextlib import asynccontextmanager
from fastapi import FastAPI
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routers.conversations import router as conversations_router
from routers.health import router as health_router
from routers.transfer import router as transfer_router
from database import initialize_database

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield

app = FastAPI(
    title="DevOpescu API",
    version="1.0.0",
    lifespan=lifespan
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

app.include_router(health_router)
app.include_router(conversations_router)
app.include_router(transfer_router)

@app.get("/", include_in_schema=False)
def web_interface():
    return FileResponse(
        STATIC_DIR / "index.html"
    )