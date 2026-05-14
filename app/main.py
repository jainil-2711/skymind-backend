from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="SkyMind API",
    description="AI-powered flight intelligence platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allows the React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return {
        "success": True,
        "data": {"status": "healthy"},
        "meta": {},
    }