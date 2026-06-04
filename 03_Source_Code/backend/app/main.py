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


from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from backend.app.infrastructure.config.limiter import limiter

app = FastAPI(title="Lost & Found IPB", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

@app.middleware("http")
async def audit_log_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    # Skip logging for static files, docs, and root
    if request.url.path.startswith(("/docs", "/openapi.json", "/storage", "/redoc")) or request.url.path == "/":
        return await call_next(request)

    response = await call_next(request)

    # Only log mutating actions and login/token requests, or admin reads if desired. 
    # Based on user's request: "semua event semua kegiatan dicatat", let's log everything that isn't skipped above.
    
    user_id = getattr(request.state, "user_id", None)
    action = f"{request.method} {request.url.path}"
    
    # Run DB insert synchronously or in background if possible, but we'll do it safely asynchronously
    # using a new session
    from database.session import SessionLocal
    from database.models.audit_log_model import AuditLogModel
    
    try:
        async with SessionLocal() as db:
            log = AuditLogModel(
                user_id=user_id,
                action=action,
                endpoint=request.url.path,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                status_code=response.status_code
            )
            db.add(log)
            await db.commit()
    except Exception as e:
        print(f"Failed to write audit log: {e}")
        
    return response

@app.get("/")
def read_root():
    return {"message": "API is running!"}
