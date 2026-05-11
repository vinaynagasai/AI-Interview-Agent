import os
from pathlib import Path
from dotenv import load_dotenv
# Load .env BEFORE any other imports that read env vars
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import DATABASE_URL, init_db, close_db
from app.routes.auth import router as auth_router
from app.routes.resume import router as resume_router
from app.routes.jobs import router as jobs_router
from app.routes.interview import router as interview_router
from app.services.groq_client import close_client as close_groq, _get_model


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    print(f"[InterviewAI] API key set: {bool(GROQ_API_KEY)}")
    print(f"[InterviewAI] Using model: {_get_model()}")
    print("[InterviewAI] Connecting to database...")
    await init_db()
    print("[InterviewAI] Database ready")
    yield
    await close_groq()
    await close_db()
    print("[InterviewAI] Shutdown complete")


app = FastAPI(
    title="InterviewAI - Intelligent Mock Interview Agent",
    description="Agentic AI-powered mock interview platform with multimodal analysis",
    version="1.0.0",
    lifespan=lifespan,
)

BACKEND_URL = os.getenv("BACKEND_URL", "")
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
if BACKEND_URL:
    CORS_ORIGINS.append(BACKEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(interview_router, prefix="/api")


@app.get("/api/health")
async def health() -> dict:
    is_sqlite = DATABASE_URL.startswith("sqlite")
    return {
        "status": "ok",
        "service": "InterviewAI Backend",
        "groq_enabled": bool(os.getenv("GROQ_API_KEY")),
        "database": "local_sqlite" if is_sqlite else "postgresql",
    }

# ── Serve Frontend Build (Production) ──
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR_EXISTS = STATIC_DIR.is_dir()


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        return JSONResponse({"detail": "Not found"}, status_code=404)
    if not STATIC_DIR_EXISTS:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    file_path = STATIC_DIR / full_path
    if file_path.is_file():
        return FileResponse(str(file_path))
    index_path = STATIC_DIR / "index.html"
    if index_path.is_file():
        return FileResponse(str(index_path))
    return JSONResponse({"detail": "Not found"}, status_code=404)
