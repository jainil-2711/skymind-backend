from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1 import api_router
from app.tasks import price_checker

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────
    price_checker.start()
    yield
    # ── Shutdown ──────────────────────────────────────────────────────────
    price_checker.stop()


app = FastAPI(
    title="SkyMind API",
    description="AI-powered flight intelligence platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "success": True,
        "data": {
            "name": "SkyMind API",
            "version": "1.0.0",
            "status": "online",
            "environment": settings.APP_ENV,
        },
        "meta": {},
    }


@app.get("/health")
def health():
    return {"success": True, "data": {"status": "healthy"}, "meta": {}}