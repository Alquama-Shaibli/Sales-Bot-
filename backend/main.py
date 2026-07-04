"""
main.py — FastAPI Application Entry Point
Initializes app, registers routers, middleware, startup/shutdown events.
"""
import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime

from config import settings
from database import create_tables, check_db_health

# ── Logging Setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup/shutdown) ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──
    logger.info("🚀 EnterpriseLead AI starting up...")
    try:
        create_tables()
        logger.info("✅ Database ready")
    except Exception as e:
        logger.error(f"❌ Database startup failed: {e}")
    logger.info(f"🌍 Environment: {settings.environment}")
    logger.info(f"🤖 LLM Model: {settings.claude_model}")
    yield
    # ── SHUTDOWN ──
    logger.info("👋 EnterpriseLead AI shutting down...")


# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="EnterpriseLead AI",
    description="Autonomous B2B SaaS Lead Qualification Agent — FlowZint Hackathon 2026",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",       # React dev server
        "http://localhost:5173",       # Vite dev server
        "https://*.railway.app",       # Railway deployments
        "https://*.vercel.app",        # Vercel deployments (frontend)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "Something went wrong",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────
from routers.health import router as health_router
from routers.chat import router as chat_router
from routers.leads import router as leads_router

app.include_router(health_router, tags=["Health"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(leads_router, prefix="/api", tags=["Leads"])


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "EnterpriseLead AI",
        "tagline": "From Website Visitor to Qualified Lead in 3 Minutes",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "hackathon": "FlowZint AI Hackathon 2026",
    }


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
