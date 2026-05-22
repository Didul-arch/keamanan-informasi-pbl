import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api.v1.routers.claim_router import router as claim_router
from backend.app.api.v1.routers.item_router import router as item_router
from backend.app.api.v1.routers.user_router import router as user_router
from backend.app.infrastructure.config.settings import settings
from database.session import Base, engine
from digital_signature.auth_router import router as auth_router

app = FastAPI(title="Lost & Found IPB")
app.mount("/storage", StaticFiles(directory="backend/storage"), name="storage")

# Enable CORS for cross-origin API calls from the React frontend port
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(claim_router)
app.include_router(item_router)
app.include_router(user_router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.on_event("startup")
async def startup():
    Path(settings.CLAIM_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables Synced!")

@app.get("/")
def read_root():
    return {"message": "API is running!"}
