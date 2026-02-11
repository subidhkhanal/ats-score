from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import analyze, optimize

app = FastAPI(
    title="ATS Score API",
    description="AI-Powered ATS Score Analyzer",
    version="1.0.0",
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api/v1", tags=["analyze"])
app.include_router(optimize.router, prefix="/api/v1", tags=["optimize"])


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "service": "ATS Score API"}
