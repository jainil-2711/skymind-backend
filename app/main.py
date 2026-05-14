from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.api.v1 import api_router

settings = get_settings()

app = FastAPI(
    title="SkyMind API",
    description="AI-powered flight intelligence platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all v1 routes under /api/v1
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