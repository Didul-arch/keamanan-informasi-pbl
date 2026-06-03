from contextlib import asynccontextmanager
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
import time
from pathlib import Path

# Import Infrastruktur (Database & Session)
from digital_signature.auth_router import router as auth_router
from backend.app.api.v1.routers.claim_router import router as claim_router
from backend.app.api.v1.routers.notification_router import router as notification_router
from backend.app.api.v1.routers.item_router import router as item_router
from backend.app.api.v1.routers.user_router import router as user_router
from backend.app.infrastructure.config.settings import settings

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    Path("storage").mkdir(parents=True, exist_ok=True)
    Path(settings.CLAIM_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.IDENTITY_DOCUMENT_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Lost & Found IPB", lifespan=lifespan)
app.mount("/storage", StaticFiles(directory="storage"), name="storage")


def _parse_cors_origins(raw_origins: str) -> list[str]:
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

# Enable CORS for cross-origin API calls from the React frontend port
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(claim_router)
app.include_router(notification_router)
app.include_router(item_router)
app.include_router(user_router)

@app.middleware("http")
async def add_process_time_header(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
def read_root():
    return {"message": "API is running!"}
