"""
routers/health.py — Health Check Endpoint
Returns API + DB status for Railway health probes.
"""
import logging
from fastapi import APIRouter
from datetime import datetime
from schemas import HealthResponse
from database import check_db_health

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse, summary="Health Check")
async def health_check():
    """
    Health check endpoint.
    - Returns 200 if API is running
    - Reports database connectivity status
    - Used by Railway for health probes
    """
    db_healthy = check_db_health()
    logger.debug(f"Health check: db={'ok' if db_healthy else 'error'}")

    return HealthResponse(
        status="healthy" if db_healthy else "degraded",
        database="connected" if db_healthy else "disconnected",
        version="1.0.0",
        timestamp=datetime.utcnow(),
    )
